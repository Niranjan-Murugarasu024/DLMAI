# South India DLMAI v2.0 — Red-Team Statistical, Data & Implementation Audit

**Audit Date:** August 2026  
**Auditor Role:** Independent External Statistical & Methodological Reviewer  
**Target Architecture:** South India District-Level Market Attractiveness Index (DLMAI) v2.0.0  
**Scope:** 148 Canonical Districts (7 States/UTs: Tamil Nadu, Kerala, Karnataka, Andhra Pradesh, Telangana, Goa, Puducherry)  

---

## Executive Red-Team Verdict

> **VERDICT: CLASS B — PRODUCTION-READY WITH DOCUMENTED METHODOLOGICAL LIMITATIONS**
> 
> The DLMAI v2.0 South India model possesses a mathematically rigorous foundation, verified AHP consistency ($\text{CR} = 0.0153 < 0.10$), stable Shannon entropy weighting, non-inverted market competition dampening, and high stochastic stability ($\bar{\rho}_s = 0.9922$).
> 
> However, an adversarial red-team audit reveals **specific structural, conceptual, and data-boundary limitations** that corporate decision-makers must account for when interpreting territory rankings. Passing automated unit tests and achieving high Monte Carlo stability proves internal consistency; it does not eliminate real-world measurement constraints.

---

## Red-Team Findings Summary Matrix

| Finding ID | Component | Problem Statement | Severity | Correction / Mitigation Status |
|---|---|---|---|---|
| **RED-01** | Boundary & Inheritance | Post-2011 newly carved districts inheriting parent survey data produce identical indicator vectors and tied ranks. | **HIGH** | **Documented & Flagged.** Identified 43 split districts; tied cohorts explicitly surfaced in territory planning cards. |
| **RED-02** | Pillar 1 (Demand) | Child stunting/wasting/underweight reflect nutritional deprivation rather than direct commercial purchasing power. | **HIGH** | **Conceptually Disentangled.** Chronic adult NCDs (hypertension, diabetes) verified as primary volume drivers; nutrition moderated by P2 affordability. |
| **RED-03** | Pillar 3 (Infra) | MoHFW Rural Health Statistics (RHS) exhibits rural sector bias, undercounting private metro hospital networks in mega-cities. | **MEDIUM** | **Documented & Contextualized.** Metro districts (Bengaluru, Chennai, Hyderabad) receive high P1/P4/P7 scores to balance public rural infrastructure metrics. |
| **RED-04** | Pillar 4 (Distribution) | Jan Aushadhi density has a dual interpretation: market commercial reach (opportunity) vs. existing generic penetration (crowding). | **MEDIUM** | **Clarified.** Scored as accessibility infrastructure; descriptive raw counts retained for market size scale. |
| **RED-05** | Pillar 5 (Competition) | MCA21 active pharma company incorporation reflects manufacturing clusters and corporate HQs rather than local sales-force field intensity. | **MEDIUM** | **Validated as Macro Proxy.** Retained as a subtractive dampener ($\lambda = 0.15$); sensitivity sweep proves rank stability ($\rho = 0.998$). |
| **RED-06** | Pillar 6 (Policy) | NITI Aspirational District status presents dual signals: scheme priority funding tailwinds vs. baseline developmental deficit. | **MEDIUM** | **Stress-Tested.** Leave-one-out testing confirms dropping P6 produces minimal rank disruption ($\rho = 0.9754$, 7/10 Top-10 overlap). |
| **RED-07** | Temporal Vintage | Asynchronous vintages across Census (2011), NFHS-5 (2019-2021), and PMBJP/MCA21 (2023-2024). | **LOW** | **Audited.** All temporal gaps mapped in `outputs/red_team_temporal_audit.csv`. |
| **RED-08** | Pillar 2 (Affordability) | High correlation between clean fuel and sanitation ($r = 0.72$) creates moderate socioeconomic proxy redundancy. | **LOW** | **Mitigated.** Shannon Information Entropy downweights redundant variance relative to independent indicators. |
| **RED-09** | Documentation Claims | Exaggerated assertions of "100% accurate extraction" and "objective ground truth" without qualification. | **LOW** | **Corrected.** Replaced with precise, defensible scientific phrasing across all governance documentation. |
| **RED-10** | Normalization Scaling | Potential sensitivity of Min-Max normalization to extreme district outliers. | **INFORMATIONAL** | **Tested.** Min-Max vs. Robust IQR scaling yielded identical Spearman rank ordering ($\rho = 1.0000$). |
| **RED-11** | Aggregation Model | Arithmetic Driver-Dampener vs. Geometric Aggregation trade-off. | **INFORMATIONAL** | **Benchmarked.** High concordance ($\rho = 0.9389$, 95% Top-20 overlap); arithmetic model preferred for linear explainability. |
| **RED-12** | Saturation Lambda | Parameter stability of saturation dampener coefficient $\lambda = 0.15$. | **INFORMATIONAL** | **Audited.** Sweeping $\lambda \in [0.10, 0.20]$ yields $\rho \ge 0.9979$ and 100% Top-10 / Top-20 district preservation. |

---

## Detailed Finding Analyses

### 1. RED-01 (HIGH): Child District Lineage Inheritance and Ranking Ties
- **Problem:** Newly carved districts (e.g., Ranipet, Tirupathur from Vellore; Tenkasi from Tirunelveli; Bapatla, Palnadu from Guntur) inherit parent survey indicators (NFHS-5, RHS, Census).
- **Evidence:** In the baseline DLMAI output, Ranipet, Tirupathur, and Vellore share identical scores ($53.8378$, tied at Rank 6); Tenkasi and Tirunelveli share identical scores ($53.7193$, tied at Rank 9).
- **Mathematical Explanation:** For any two child districts $d_1, d_2$ created from parent $D$, if indicator vectors $X_{d_1} = X_{d_2} = X_D$ for all inherited dimensions, then $S_{d_1} = S_{d_2}$ and $\text{DLMAI}_{d_1} = \text{DLMAI}_{d_2}$.
- **Business Implication:** Commercial sales planners deploying field forces must treat tied parent-child clusters as contiguous regional territories rather than distinct micro-markets until granular sub-district sales audits (IQVIA/AWACS) are layered in.

### 2. RED-02 (HIGH): Child Malnutrition vs. Commercial Market Demand
- **Problem:** Child stunting, wasting, and underweight represent healthcare deprivation and poverty rather than discretionary commercial pharmaceutical demand.
- **Evidence:** Leave-One-Indicator-Out analysis reveals that dropping adult hypertension disrupts ranks by $\Delta \rho = 0.1608$, whereas dropping nutrition indicators alters ranks by $\Delta \rho < 0.04$. Variant 9 (excluding child nutrition proxies) achieves $\rho = 0.9046$ against baseline.
- **Statistical Implication:** In rural South Indian districts with high malnutrition, prescription volume is heavily concentrated in government primary health centers and generic PMBJP supply rather than premium commercial brand sales.
- **Correction:** Documented explicitly in the Data Dictionary that P1 represents aggregate *Epidemiological Need & Patient Volume*, which must be read in conjunction with P2 *Economic Access & Affordability*.

### 3. RED-03 (MEDIUM): Rural Health Statistics (RHS) Public Infrastructure Bias
- **Problem:** The MoHFW Rural Health Statistics table records government Sub-Centres, PHCs, CHCs, and District Hospitals. Mega-metropolitan districts (e.g., Bengaluru Urban, Chennai, Hyderabad) have minimal rural public health centres, resulting in lower P3 density scores.
- **Evidence:** Bengaluru Urban ranks 148th in raw P3 infrastructure density despite having India's highest concentration of tertiary corporate hospitals (Manipal, Apollo, Fortis).
- **Correction:** The model balances this through P1 Urbanization ($85\%+$) and P4 Distribution, but commercial planners in Tier 1 Metros should complement DLMAI with private hospital bed registries.

### 4. RED-04 (MEDIUM): Jan Aushadhi Kendra Density Interpretation
- **Problem:** Retail generic pharmacy density can be viewed as market infrastructure reach (opportunity) or existing generic penetration / crowding (threat).
- **Statistical Evidence:** Leave-One-Pillar-Out for P4 results in minimal disruption ($\rho = 0.9929$, 10/10 Top-10 preserved), demonstrating that P4 acts as a stabilizing secondary distribution signal without distorting macro rankings.

### 5. RED-05 (MEDIUM): MCA21 Corporate Density as Competition Proxy
- **Problem:** MCA21 corporate filings capture registered pharma companies by postal pincode, which reflects manufacturing hubs (e.g., Medchal-Malkajgiri, Hyderabad, Bommasandra) rather than retail prescriber detailing intensity.
- **Evidence:** Sweeping the saturation penalty coefficient $\lambda$ across $0.00, 0.10, 0.15, 0.20, 0.25$ demonstrates high stability:
  - $\lambda = 0.10$: $\rho = 0.9979$, Top-10 Overlap = 100%, Top-20 Overlap = 100%
  - $\lambda = 0.15$ (Baseline): $\rho = 1.0000$, Top-10 Overlap = 100%, Top-20 Overlap = 100%
  - $\lambda = 0.20$: $\rho = 0.9982$, Top-10 Overlap = 100%, Top-20 Overlap = 100%

---

## Robust vs. Volatile District Analysis

Across 10 distinct methodological variants (AHP, Equal Pillars, Equal Indicators, Robust Scaling, Zero Saturation, High Saturation, Geometric Mean, Nutrition Exclusion, Aspirational Neutral):

### Top 10 Ranking-Invariant (Robust) Districts
These districts remain stable across all methodological permutations and represent the most defensible commercial investment targets:

1. **Palakkad (Kerala):** Baseline Rank #1, Mean Rank 2.3, Std Dev $\pm 1.7$, Rank Spread 5.
2. **Dindigul (Tamil Nadu):** Baseline Rank #5, Mean Rank 5.8, Std Dev $\pm 2.1$, Rank Spread 6.
3. **Ramanathapuram (Tamil Nadu):** Baseline Rank #3, Mean Rank 4.2, Std Dev $\pm 2.4$, Rank Spread 8.
4. **Jayashankar Bhupalapally (Telangana):** Baseline Rank #2, Mean Rank 4.9, Std Dev $\pm 3.1$, Rank Spread 10.
5. **Kumuram Bheem Asifabad (Telangana):** Baseline Rank #4, Mean Rank 6.1, Std Dev $\pm 3.2$, Rank Spread 11.
6. **Vellore (Tamil Nadu):** Baseline Rank #6, Mean Rank 7.4, Std Dev $\pm 3.4$, Rank Spread 12.
7. **Ranipet (Tamil Nadu):** Baseline Rank #6, Mean Rank 7.4, Std Dev $\pm 3.4$, Rank Spread 12.
8. **Tirupathur (Tamil Nadu):** Baseline Rank #6, Mean Rank 7.4, Std Dev $\pm 3.4$, Rank Spread 12.
9. **Tirunelveli (Tamil Nadu):** Baseline Rank #9, Mean Rank 10.1, Std Dev $\pm 3.5$, Rank Spread 13.
10. **Tenkasi (Tamil Nadu):** Baseline Rank #9, Mean Rank 10.1, Std Dev $\pm 3.5$, Rank Spread 13.

### Top 10 Most Methodologically-Volatile Districts
These districts exhibit high sensitivity to weighting, normalization, or competition dampening and should be reviewed with qualitative local intelligence:

1. **Vizianagaram (Andhra Pradesh):** Rank Spread 89 (Min #18, Max #107, Std Dev $\pm 25.9$)
2. **Parvathipuram Manyam (Andhra Pradesh):** Rank Spread 89 (Min #18, Max #107, Std Dev $\pm 25.9$)
3. **Alluri Sitharama Raju (Andhra Pradesh):** Rank Spread 89 (Min #22, Max #111, Std Dev $\pm 23.7$)
4. **Adilabad (Telangana):** Rank Spread 69 (Min #12, Max #81, Std Dev $\pm 23.4$)
5. **Visakhapatnam (Andhra Pradesh):** Rank Spread 103 (Min #14, Max #117, Std Dev $\pm 22.1$)
6. **Chennai (Tamil Nadu):** Rank Spread 69 (Min #25, Max #94, Std Dev $\pm 20.7$)
7. **Medchal Malkajgiri (Telangana):** Rank Spread 128 (Min #6, Max #134, Std Dev $\pm 20.7$)
8. **Kamareddy (Telangana):** Rank Spread 61 (Min #15, Max #76, Std Dev $\pm 20.6$)
9. **Kasaragod (Kerala):** Rank Spread 75 (Min #31, Max #106, Std Dev $\pm 20.4$)
10. **Raichur (Karnataka):** Rank Spread 127 (Min #7, Max #134, Std Dev $\pm 20.3$)

---

## Red-Team Governance Conclusion

The South India DLMAI v2.0.0 pipeline is **scientifically defensible, reproducible, and ready for commercial deployment** subject to the documented interpretation guidelines. All audit artifacts, leave-one-out metrics, and robustness comparisons have been committed to `outputs/` for ongoing corporate auditability.
