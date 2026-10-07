# DLMAI South India Refactor: Methodological Decision Log

**Document Version:** 1.0.0  
**Target Geography:** South India (148 Districts across 7 States/UTs)  

---

## Overview

This document records the strategic, mathematical, and data-engineering decisions made during the refactoring of the **District-Level Market Attractiveness Index (DLMAI)** for South India. Each entry documents the problem context, alternatives evaluated, empirical evidence, chosen methodology, and expected impact.

---

### Decision 1: Geographic Scope & Baseline Entity Definition
- **Context:** The original prototype operated on an illustrative 22-district seed table. We needed an authoritative definition of South India.
- **Alternatives Considered:**
  1. *National 785-district run with downstream regional filtering.*
  2. *Regional model bounded strictly to South India's 7 States/UTs from the start.*
- **Evidence:** Normalization (Min-Max) and Shannon Entropy are distribution-dependent. Evaluating South India relative to national extremes distorts regional variance (e.g. Kerala's high diabetes prevalence would be compressed against national outliers).
- **Chosen Method:** Dedicated regional model targeting the 7 South Indian States/UTs: Tamil Nadu, Kerala, Karnataka, Andhra Pradesh, Telangana, Goa, and Puducherry (**148 canonical districts** in LGD).
- **Impact:** Reflects true intra-regional competitive dynamics and regional purchasing power.

---

### Decision 2: Indicator Count Reconciliation & Pillar 4 Redundancy Elimination
- **Context:** Legacy documentation stated "22 core indicators", but listed 21 items, including both `jan_aushadhi_density_per_100k` and `jan_aushadhi_raw_count` in Pillar 4.
- **Alternatives Considered:**
  1. *Score both count and density in Pillar 4.*
  2. *Score density only; retain count as descriptive metadata.*
- **Evidence:** $\text{Density} = \frac{\text{Count}}{\text{Population}} \times 100{,}000$. Scoring both creates structural multicollinearity ($r = 0.88$), distorting entropy weights and double-counting urban scale.
- **Chosen Method:** Score `jan_aushadhi_density_per_100k` as the single core P4 indicator. Retain `jan_aushadhi_raw_count` as non-scored descriptive scale context. Total scored core indicators = **20**.
- **Impact:** Eliminates collinear bias, ensures mathematical independence within Pillar 4.

---

### Decision 3: Saaty AHP Weight Recalculation & Matrix Governance
- **Context:** The legacy code contained hardcoded pillar weights that differed slightly (0.5%–1.5%) from the true principal eigenvector of the $7 \times 7$ Saaty pairwise comparison matrix.
- **Alternatives Considered:**
  1. *Retain legacy hardcoded dictionary.*
  2. *Derive weights dynamically from the pairwise comparison matrix via eigenvector decomposition.*
- **Evidence:** The $7 \times 7$ pairwise comparison matrix yields $\lambda_{\max} = 7.121566$, $\text{CI} = 0.020261$, $\text{CR} = 0.015349 < 0.10$ ($1.53\%$, strictly consistent).
- **Chosen Method:** Derive exact weights dynamically from the matrix: P1=35.41%, P2=15.63%, P3=23.86%, P4=10.04%, P5=3.35%, P6=5.85%, P7=5.85%. Decoupled into `config/weights.yaml`.
- **Impact:** Strict mathematical reproducibility; guarantees $CR < 0.10$.

---

### Decision 4: Pillar 5 Market Saturation Formulation (Value Dampener)
- **Context:** Legacy scoring inverted P5 via negative min-max and then subtracted it, creating a contradictory double-inversion.
- **Alternatives Considered:**
  1. *Positive interpretation (pharma hub = attractive ecosystem).*
  2. *Negative indicator inside composite.*
  3. *Separate Value Dampener ($\text{Score} = \text{ValueDrivers} - \text{Penalty}$).*
- **Evidence:** In commercial pharma strategy, high existing pharma company density indicates intense generic price competition and crowded field forces.
- **Chosen Method:** Non-inverted Saturation Intensity $S^{\text{sat}}_i \in [0, 100]$ penalized via $C_i = \lambda S^{\text{sat}}_i$ ($\lambda = 0.15$), yielding $\text{DLMAI}_i = V_i - C_i$.
- **Impact:** Transparent dampening effect; allows identification of attractive "white-space" markets with high healthcare demand and low competitor crowding.

---

### Decision 5: Disease Burden vs. Socioeconomic Deprivation Nuance
- **Context:** High child malnutrition (stunting, wasting, underweight) can correlate with extreme poverty, where commercial purchasing power is zero.
- **Alternatives Considered:**
  1. *Invert malnutrition indicators (treat well-nourished as more attractive).*
  2. *Remove malnutrition entirely.*
  3. *Retain as positive demand indicators, moderated by Pillar 2 (Affordability) and Pillar 3 (Infrastructure).*
- **Evidence:** Pediatric malnutrition creates legitimate therapeutic demand (antibiotics, vitamins, minerals, rehydration). However, commercial realization requires purchasing power (P2) and clinical access (P3).
- **Chosen Method:** Retain malnutrition in P1 under explicit "Pediatric Therapeutic Need" framing. The compensatory structure ensures a poor district with no insurance and no hospitals does not rank high.
- **Impact:** Balanced epidemiological representation without perverse incentive distortions.

---

### Decision 6: Exclusion of SECC from District Composite Scoring
- **Context:** The available Socio Economic and Caste Census (SECC) dataset exists only at the **State Level** (35 rows).
- **Alternatives Considered:**
  1. *Broadcast state SECC values into all constituent districts.*
  2. *Exclude SECC from district composite; use for macro state analysis.*
- **Evidence:** Broadcasting state numbers to districts creates artificial intra-state homogeneity and disguises state-level aggregates as micro observations.
- **Chosen Method:** Exclude SECC from district composite scoring. Utilize NFHS-5 household amenities (`clean_fuel_pct`, `sanitation_pct`, `insurance_pct`) for true district-level economic profiling.
- **Impact:** Preserves strict geographic granularity integrity.

---

### Decision 7: Missing Data & Zero Policy
- **Context:** Unmatched pincodes or missing survey entries were occasionally treated as zero in legacy mocks.
- **Alternatives Considered:**
  1. *Impute zeros for missing cells.*
  2. *Strict 4-tier fallback (Trend $\to$ State Mean $\to$ kNN Covariate $\to$ Unresolved null) with provenance tracking.*
- **Evidence:** Treating missing hospital or enterprise records as zero introduces severe false-negative bias for rural/new districts.
- **Chosen Method:** Enforce Missing $\ne 0$. Track every cell status as `OBSERVED`, `INHERITED`, `IMPUTED`, or `DERIVED`. Unmatched pincodes are flagged as unmapped.
- **Impact:** 100% auditability and honest reporting of data quality.

---

### Decision 8: Standardized Quantile-Based Tiering
- **Context:** Legacy documentation referenced "Quantile-Based Natural Boundaries", mixing two distinct classification methods.
- **Alternatives Considered:**
  1. *Jenks Natural Breaks.*
  2. *Fixed score thresholds (e.g. >75 = Tier 1).*
  3. *Quantile Percentile Cutoffs (80th, 50th, 20th percentiles).*
- **Evidence:** Relative ranking across 148 districts is most actionable for territory planning when divided into consistent demographic cohorts.
- **Chosen Method:** Quantile-Based Tiering:
  - **Tier 1 (High Priority):** $\ge 80\text{th}$ percentile (~Top 30 districts)
  - **Tier 2 (Growth Markets):** $50\text{th}\text{--}80\text{th}$ percentile (~44 districts)
  - **Tier 3 (Moderate Opportunity):** $20\text{th}\text{--}50\text{th}$ percentile (~44 districts)
  - **Tier 4 (Nascent / Rural):** $< 20\text{th}$ percentile (~30 districts)
- **Impact:** Clear territory prioritization for sales force deployment.

---

### Decision 9: Adversarial 7-Test Statistical Validation & Governance Certification
- **Context:** Need for independent adversarial verification across scaling, weighting, data completeness bias, competition proxy construct, and Monte Carlo convergence.
- **Alternatives Considered:**
  1. *Rely solely on internal unit test pass rates.*
  2. *Execute an exhaustive 7-test independent statistical red-team validation protocol.*
- **Evidence:**
  - *Test 1:* 100% exact mathematical recomputation from scratch ($\text{error} \le 1 \times 10^{-4}$, 0 rank mismatches).
  - *Test 2:* Normalization decomposition confirms Min-Max and Robust IQR scaling produce identical rank order ($\rho = 1.0000$).
  - *Test 3:* Identified 59 invariant robust districts and 61 specification-sensitive districts across 10 distinct variants.
  - *Test 4:* OLS regression confirms no positive data completeness bias ($r = -0.0820, p = 0.3220$).
  - *Test 5:* P5 saturation ablation confirms stability under competition dampening ($\rho = 0.9804$).
  - *Test 6:* Decomposed composite into Need ($r=0.63$), Access ($r=0.65$), Growth ($r=0.41$), and Competition ($r=-0.21$).
  - *Test 7:* Monte Carlo 1k and 5k simulations confirm stochastic convergence ($\bar{\rho}_s = 0.9922, \bar{\tau} = 0.9367$).
- **Chosen Method:** Formal certification of South India DLMAI v2.0 as **Class B Production-Ready** under documented governance controls:
  - Cluster newly carved child districts sharing parent survey vectors as single territory planning units.
  - Complement rural public infrastructure scores with private bed registries for Tier 1 mega-metros.
  - Interpret composite DLMAI alongside the 4 strategic sub-scores (Need, Access, Growth, Competition).
- **Impact:** Complete statistical defensibility and clear operational guidance for corporate leadership.

---

### Decision 10: External Commercial Predictive Validation & Out-of-Sample Gate
- **Context:** To evaluate whether DLMAI predicts pharmaceutical commercial market outcomes and to conduct a forensic provenance audit of external benchmarks.
- **Alternatives Considered:**
  1. *Stop at internal Monte Carlo and mathematical sensitivity validation.*
  2. *Execute external predictive validation against top-down calibrated IPM benchmarks and perform a strict forensic provenance audit.*
- **Forensic Audit Findings:**
  - Macro South India benchmark of INR 66,400 Cr is an estimated/calibrated top-down allocation from state aggregates.
  - Zero out of 148 districts possess directly ingested, invoice-level secondary sales audit records (AIOCD-AWACS/IQVIA).
  - Four DLMAI indicators (population, urbanization, hospitals, Jan Aushadhi) were used in benchmark construction, creating high covariate circularity.
  - Population scale models outperform DLMAI on gross absolute volume prediction ($R^2 = 0.88$ vs $R^2 = 0.005$), while DLMAI is a statistically significant predictor of per-capita healthcare demand ($p < 0.0001$).
- **Classification & Chosen Policy:** Formal classification as **CLASS D: CALIBRATED / SYNTHETIC BENCHMARK — NOT TRUE EXTERNAL VALIDATION**.
- **Impact:** Test 8 proves methodological feasibility and benchmark sensitivity, but the project must NOT claim to be "empirically validated" until real proprietary district sales audit data is ingested in Phase 2.

---
*Decision Log Complete. Documented in `docs/DLMAI_Model_Decision_Log.md`.*

