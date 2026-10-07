# DLMAI v2.0 — District-Level Market Attractiveness Index
## South Indian Pharmaceutical Market Analytics
### A Complete Learning System, Technical Reference, and Forensic Audit Document

> **This document is a forensically verified source-of-truth learning system.**
> **Every claim is traceable to a specific file, function, line of code, or output artifact in the repository.**
> **Claims that cannot be verified are explicitly labeled `[NOT VERIFIED FROM CODE]`.**

---

## Current Project Status

| Property | Verified Value |
|---|---|
| Model Version | DLMAI v2.0.0 |
| Geographic Scope | South India — 7 States/UTs |
| Canonical Districts | **148** |
| Scored Indicators | **20** |
| Pillars | **7** (6 Value Drivers + 1 Value Dampener) |
| Automated Pytest Tests | **24 / 24 Passing** |
| Validation Classification | **Class B — Statistically Defensible Internal Index** |
| External Commercial Validation | **NOT ACHIEVED (Class D — Synthetic Benchmark)** |
| AHP Consistency Ratio | **CR = 0.015349 < 0.10 (Strictly Consistent)** |
| Monte Carlo Mean Spearman rho (N=1,000) | **0.9922 (Highly Stable)** |
| Highest-Ranked District | Palakkad (score: 55.953) |
| Lowest-Ranked District | Bengaluru Urban (score: 24.3506) |

Source: `outputs/refresh_metadata.json`, `outputs/ahp_validation.json`,
`outputs/red_team_validation_v2/test_run_metadata.json`

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Problem Statement and Business Context](#2-problem-statement-and-business-context)
3. [What DLMAI Means — Word by Word](#3-what-dlmai-means--word-by-word)
4. [Geographic Coverage](#4-geographic-coverage)
5. [High-Level Architecture](#5-high-level-architecture)
6. [Repository Structure](#6-repository-structure)
7. [Complete Backend Workflow (16 Steps)](#7-complete-backend-workflow)
8. [Data Sources Explained](#8-data-sources-explained)
9. [Indicator Catalog (20 Indicators)](#9-indicator-catalog)
10. [Normalization](#10-normalization)
11. [Shannon Entropy Intra-Pillar Weighting](#11-shannon-entropy-intra-pillar-weighting)
12. [AHP Inter-Pillar Prioritization](#12-ahp-inter-pillar-prioritization)
13. [Pillar Architecture](#13-pillar-architecture)
14. [DLMAI Mathematical Formula](#14-dlmai-mathematical-formula)
15. [P5 / MCA21 Forensic Construct Analysis](#15-p5--mca21-forensic-construct-analysis)
16. [Ranking and Tiering](#16-ranking-and-tiering)
17. [Monte Carlo Uncertainty Analysis](#17-monte-carlo-uncertainty-analysis)
18. [Complete 8-Test Validation Framework](#18-complete-8-test-validation-framework)
19. [Test 8 — Forensic External Commercial Validation](#19-test-8--forensic-external-commercial-validation)
20. [Data Leakage and Circularity Audit](#20-data-leakage-and-circularity-audit)
21. [Automated Test Suite Architecture](#21-automated-test-suite-architecture)
22. [Output Files Reference](#22-output-files-reference)
23. [Complete Execution Guide](#23-complete-execution-guide)
24. [Troubleshooting and Failure Modes](#24-troubleshooting-and-failure-modes)
25. [Code Architecture and File-to-Function Map](#25-code-architecture-and-file-to-function-map)
26. [Documentation vs. Implementation Audit](#26-documentation-vs-implementation-audit)
27. [Project Maturity Assessment](#27-project-maturity-assessment)
28. [Valid vs. Invalid Claims](#28-valid-vs-invalid-claims)
29. [Model Governance Log Summary](#29-model-governance-log-summary)
30. [Industry Presentation Guide (5 Audiences)](#30-industry-presentation-guide)
31. [Interview Preparation (Beginner to Expert)](#31-interview-preparation)
32. [Glossary (40+ Terms)](#32-glossary)
33. [Complete Mathematical Reference (12 Formulas)](#33-complete-mathematical-reference)
34. [Learning Path (13 Levels)](#34-learning-path)
35. [Important Truths About DLMAI](#35-important-truths-about-dlmai)

---

## 1. Executive Overview

DLMAI (District-Level Market Attractiveness Index) is a quantitative, multi-criteria decision-support tool
designed to help pharmaceutical companies systematically identify and rank 148 South Indian districts
for commercial investment.

Rather than relying on sales-force intuition or population alone, DLMAI combines **20 government-sourced
indicators** from **6 data sources** into a single composite score per district, structured across 7 thematic pillars.

**What the score answers:**
> "Given the healthcare demand, economic access, infrastructure, distribution reach, policy environment,
> growth dynamics, and competitive crowding of this district — how commercially attractive is it
> relative to all other South Indian districts?"

**Validation status:** Class B — Statistically Defensible Internal Index. The model has been subjected
to an 8-test adversarial red-team validation suite. Its mathematics are exact, its structure is
robust, and its rankings are stable. However, it has **not been validated against independently observed
district-level pharmaceutical sales data**.

---

## 2. Problem Statement and Business Context

### The Business Problem

A pharmaceutical company deploying a South India field force must answer:
- Which 30 districts deserve Priority 1 specialty deployment?
- Where is therapeutic demand high but competition still low?
- Which districts have economic capacity to convert demand into actual purchases?
- Where will the next decade's growth come from?

These questions cannot be answered with a single metric. Dense urban districts may have high population
but saturated competition. Smaller districts may have disproportionate therapeutic need with minimal
current coverage. DLMAI provides systematic, data-driven answers.

### Why an Index?

An index converts heterogeneous measures (percentages, counts, rates, binary flags) into a single
comparable number, enabling apples-to-apples comparison across 148 districts measured on 20 different scales.

---

## 3. What DLMAI Means — Word by Word

| Letter | Word | Meaning |
|---|---|---|
| D | District | Administrative unit of India, sub-division of a State. South India: 148 canonical districts across 7 States/UTs. |
| L | Level | Analysis at district granularity — not national or state-level aggregates. |
| M | Market | The pharmaceutical commercial market: prescribers, dispensers, and patients. |
| A | Attractiveness | How commercially promising a district is — combining demand, access, infrastructure, growth, and low competition. |
| I | Index | A single composite number derived from many indicators on a normalized scale. |

---

## 4. Geographic Coverage

**Source:** `config/geography.yaml`, `data/master/lgd_south_india.csv`

| State / UT | LGD State Code | District Count |
|---|---|---|
| Tamil Nadu | 33 | 38 |
| Telangana | 36 | 33 |
| Karnataka | 29 | 31 |
| Andhra Pradesh | 28 | 26 |
| Kerala | 32 | 14 |
| Puducherry | 34 | 4 |
| Goa | 30 | 2 |
| **TOTAL** | | **148** |

**Newly created districts** (carved from parent districts post-Census 2011) are present in the LGD
canonical list and inherit parent-district data via the multi-generation lineage resolver.
Examples: Alluri Sitharama Raju (parent: Visakhapatnam), Ranipet and Tirupathur (parent: Vellore).

---

## 5. High-Level Architecture

```
GOVERNMENT DATA SOURCES
    NFHS-5 (2019-21)        -> Epidemiological indicators       -> P1, P2
    Census 2011             -> Demographics, urbanization        -> P1, P2, P7
    RHS / MoHFW             -> Healthcare facility counts        -> P3
    PMBJP Jan Aushadhi      -> Generic pharmacy network          -> P4
    MCA21 Corporate Reg.    -> Pharma enterprise concentration   -> P5
    NITI Aayog              -> Aspirational District status      -> P6
         |
         v
RAW DATA MATRIX  {lgd_code -> {indicator -> value or None}}
         |
    District Crosswalk & Name Standardization     (src/harmonization/crosswalk.py)
    Multi-generation Lineage Inheritance          (src/harmonization/inheritance.py)
    Hierarchical Imputation: State Mean -> kNN    (src/imputation/engine.py)
         |
HARMONIZED MATRIX with provenance_mask per cell
         |
    Direction-Aware Min-Max Normalization [0,100]  (src/scoring/normalizer.py)
         |
NORMALIZED MATRIX  {lgd_code -> {indicator -> score in [0,100]}}
         |
    Shannon Entropy Intra-Pillar Weighting         (src/scoring/entropy.py)
    Saaty AHP Inter-Pillar Prioritization          (src/scoring/ahp.py)
         |
PILLAR SCORES  {P1: 0-100, P2: 0-100, ..., P7: 0-100}
         |
    DLMAI_i = V_i - 0.15 * S_i5                   (src/scoring/composite.py)
         |
    South India Rank + State Rank
    Quantile Tiering (p80 / p50 / p20 cutoffs)
    Monte Carlo Uncertainty (N=1000, sigma=0.20)
         |
OUTPUT DELIVERABLES
    outputs/dlmai_south_india_scores.csv           <- PRIMARY OUTPUT
    outputs/dlmai_south_india_combined_output.csv
    outputs/ahp_validation.json
    outputs/sensitivity_results.csv
    outputs/robustness_comparison.csv
    outputs/data_quality_report.csv
    outputs/district_coverage_matrix.csv
    outputs/indicator_redundancy_report.csv
    outputs/refresh_metadata.json
    outputs/red_team_validation_v2/  (38 validation artifacts)
```

---

## 6. Repository Structure

```
dlmai_complete/
|
+-- config/                          <- YAML: source of truth for ALL model parameters
|   +-- geography.yaml               <- 7 states, 148 districts, LGD codes
|   +-- indicators.yaml              <- 20 scored indicators + 5 contextual variables
|   +-- pillars.yaml                 <- 7 pillars with indicator bindings
|   +-- weights.yaml                 <- 7x7 AHP matrix, CR=0.015349, driver weights
|   +-- scoring.yaml                 <- Normalization method, tier cutoffs (p80/p50/p20)
|   +-- sensitivity.yaml             <- Monte Carlo: N=1000, seed=42, sigma=0.20
|
+-- src/                             <- Core Python package (production logic)
|   +-- config.py                    <- Singleton ConfigManager (loads all 6 YAMLs)
|   +-- pipeline.py                  <- Main orchestrator (14 production steps)
|   +-- harmonization/
|   |   +-- crosswalk.py             <- District name -> LGD code resolver
|   |   +-- inheritance.py           <- Fixed-point multi-generation lineage inheritance
|   +-- ingestion/
|   |   +-- nfhs_parser.py           <- PDF parser for NFHS-5 district factsheets
|   |   +-- rhs_parser.py            <- PDF parser for MoHFW RHS health-centre tables
|   |   +-- niti_aayog.py            <- Hard-coded 112 Aspirational Districts list
|   |   +-- census_parser.py         <- Census demographic extractor
|   |   +-- jan_aushadhi.py          <- Jan Aushadhi Kendra ingestion
|   |   +-- mca21.py                 <- MCA21 corporate record ingestion
|   +-- imputation/
|   |   +-- engine.py                <- 3-tier hierarchical imputation with provenance mask
|   +-- scoring/
|   |   +-- normalizer.py            <- Direction-aware min-max normalization [0,100]
|   |   +-- entropy.py               <- Shannon Information Entropy intra-pillar weights
|   |   +-- ahp.py                   <- Saaty AHP eigenvector + CR validation
|   |   +-- composite.py             <- DLMAI = V - lambda*P5; ranking; quantile tiering
|   +-- sensitivity/
|   |   +-- monte_carlo.py           <- Log-normal weight perturbation, N=1000 iterations
|   +-- validation/
|       +-- data_quality.py          <- Completeness and provenance reports
|       +-- redundancy.py            <- Indicator correlation audit
|
+-- scripts/red_team_validation/
|   +-- run_all_validation.py        <- Master orchestrator (8 tests)
|   +-- test01_independent_recalculation.py      <- From-scratch recomputation
|   +-- test02_normalization_sensitivity.py      <- 4 normalization methods
|   +-- test03_topn_robustness.py                <- 10-variant Top-N stability
|   +-- test04_data_quality_bias.py              <- Completeness -> score bias
|   +-- test05_p5_ablation.py                    <- P5 construct sensitivity
|   +-- test06_component_decomposition.py        <- 4-axis strategic decomposition
|   +-- test07_monte_carlo_uncertainty.py        <- N=1000 and N=5000 MC
|   +-- test08_external_commercial_validation.py <- Forensic provenance audit
|
+-- tests/                           <- Automated pytest suite (24/24 passing)
|   +-- test_red_team_validation.py  <- 14 tests against validation artifacts
|   +-- test_south_india_methodology.py  <- 10 unit/integration tests
|
+-- data/master/
|   +-- lgd_south_india.csv          <- 148-district canonical LGD master
|   +-- district_crosswalk_south.csv <- Alias/historical name mappings
|
+-- outputs/
|   +-- dlmai_south_india_scores.csv           <- PRIMARY OUTPUT (148 rows)
|   +-- dlmai_south_india_combined_output.csv  <- Full analytical matrix
|   +-- ahp_validation.json                    <- AHP: CR=0.015349
|   +-- refresh_metadata.json                  <- Execution summary
|   +-- red_team_validation_v2/                <- 38 validation artifacts
|
+-- docs/
|   +-- South_India_DLMAI_Methodology.md       <- Full mathematical formulation
|   +-- South_India_DLMAI_Data_Dictionary.md   <- Indicator definitions
|   +-- DLMAI_Model_Decision_Log.md            <- 10 formal methodology decisions
|   +-- DLMAI_v2_Seven_Test_Validation_Report.md
|   +-- DLMAI_v2_Test08_Forensic_Commercial_Validation.md
|
+-- scoring_engine.py                <- LEGACY standalone engine (use src/scoring/* instead)
+-- ahp_pillar_weights.py            <- Standalone AHP computation tool
+-- dashboard_app.py                 <- Streamlit entry point
+-- requirements.txt                 <- pdfplumber, reportlab, streamlit, pandas, numpy
+-- README.md                        <- THIS FILE
```

---

## 7. Complete Backend Workflow

**Entry point:** `src/pipeline.py` -> `run_south_india_pipeline(output_dir="outputs")`

### Step 1: Configuration Loading
`src/config.py` -> `ConfigManager.__init__()`

Singleton loads all 6 YAML files into memory. All subsequent steps read from this object — no hard-coded parameters anywhere else.

### Step 2: Geographic Master Loading
`src/harmonization/crosswalk.py` -> `SouthDistrictCrosswalk.__init__()`

Reads `data/master/lgd_south_india.csv` (148 rows) and `data/master/district_crosswalk_south.csv`.
Builds: `districts = {lgd_code: CanonicalDistrict}`, `parent_map = {child_code: parent_code}`.

### Step 3: Population Anchoring
`src/pipeline.py` (inline)

Hard-coded `pop_anchors` dict provides calibrated population (millions) for named districts.
(e.g., Bengaluru Urban = 9.62M, Chennai = 4.65M). Unnamed districts default to 2.2M.

**NOTE:** These are calibrated estimates for per-100k density calculations, NOT authoritative
Census 2011 figures.

### Step 4: NFHS-5 Ingestion (PDF Parsing)
`src/ingestion/nfhs_parser.py` -> `parse_nfhs_factsheet()`

Scans `data/nfhs/district/*/*.pdf`. Extracts: hypertension %, diabetes %, stunting %, wasting %,
underweight %, insurance %, clean fuel %, sanitation %, OOPE delivery (INR).
Maps each record to LGD code via `crosswalk.resolve()`.

### Step 5: RHS Infrastructure Ingestion
`src/ingestion/rhs_parser.py` -> `extract_all_rhs_rows()`

Parses `data/rhs/district-wise-health-centres.pdf`.
Extracts PHC, CHC, sub-centre counts -> per-100k densities. Also: hospital presence count.

### Step 6: Jan Aushadhi and MCA21 Ingestion
`src/pipeline.py` (inline)

**Jan Aushadhi:** Named districts use calibrated anchor counts (e.g., Bengaluru Urban=142,
Chennai=115). Unnamed districts use formula: `max(int(pop_lakhs * 1.8), 6)`.

**MCA21:** Named districts use calibrated anchor counts (e.g., Hyderabad=420, Bengaluru Urban=350).
Unnamed districts use: `max(int(pop_lakhs * 0.4), 1)`.

**FORENSIC NOTE:** Jan Aushadhi and MCA21 values for unnamed districts are algorithmically derived
from population — NOT directly read from source databases. This is a documented limitation.

### Step 7: NITI Aayog and Census Baseline
`src/ingestion/niti_aayog.py` -> `is_aspirational_district()`

Aspirational district flag: looks up against a hard-coded list of 112 official Aspirational Districts.

Census demographics:
- `census_total_population` = pop_lakhs * 100,000
- `census_urban_population_pct` = 85% (known urban), 12% (known rural), else `25 + pop_lakhs * 0.8`
- `census_population_age_0_6_pct` = **10.2% constant across ALL districts** (NOT observed)
- `census_decadal_growth_pct` = **12.4% constant across ALL districts** (NOT observed)
- `census_literacy_rate_pct` = 94% (Kerala), 82% (Tamil Nadu), 76% (others)

**FORENSIC NOTE:** Three Census indicators are state-level constants, not district observations.

### Step 8: Multi-Generation Lineage Inheritance
`src/harmonization/inheritance.py` -> `SouthInheritanceResolver.fill_missing()`

Fixed-point loop: if child district has None and parent has a value -> child inherits parent value.
Provenance label: `INHERITED_FROM_{parent_code}`. Handles multi-generation chains.

### Step 9: Hierarchical Statistical Imputation
`src/imputation/engine.py` -> `SouthImputationEngine.impute_matrix()`

| Tier | Method | Label |
|---|---|---|
| 1 | State Mean (all observed/inherited in same state) | IMPUTED_STATE_MEAN |
| 2 | Population kNN (k=5 neighbors by population size) | IMPUTED_KNN |
| Unresolvable | Remains null -> 50.0 fallback at normalization | STILL_MISSING |

Zero is NEVER imputed. Missing != Zero. (Decision 7, `docs/DLMAI_Model_Decision_Log.md`)

### Step 10: Direction-Aware Normalization
`src/scoring/normalizer.py` -> `min_max_normalize(values, direction)`

```
POSITIVE:            normalized = (x - x_min) / (x_max - x_min) * 100
NEGATIVE (OOPE):     normalized = (x_max - x) / (x_max - x_min) * 100
SATURATION_DAMPENER: normalized = (x - x_min) / (x_max - x_min) * 100  (same as POSITIVE)
Zero variance:       normalized = 50.0
Missing value:       normalized = 50.0
```

### Step 11: Shannon Entropy Intra-Pillar Weighting
`src/scoring/entropy.py` -> `calculate_entropy_weights(normalized_matrix, indicator_list)`

```
eps = 1e-6
p_ij = (R_ij + eps) / sum_i(R_ij + eps)
e_j  = -(1/ln(M)) * sum_i(p_ij * ln(p_ij))    [M = 148]
d_j  = max(1 - e_j, 1e-6)
w_j  = d_j / sum_j(d_j)
S_ip = sum_j(w_j * R_ij)
```

Higher cross-district variance -> lower entropy -> higher weight.
Single-indicator pillars (P4, P5, P6): w=1.0, S_ip = R_ip directly.

### Step 12: AHP Inter-Pillar Weighting
`src/scoring/ahp.py` -> `calculate_ahp_weights(matrix, criteria)`

```python
eigenvalues, eigenvectors = np.linalg.eig(matrix)
max_idx = int(np.argmax(np.real(eigenvalues)))
lambda_max = float(np.real(eigenvalues[max_idx]))
weights = np.real(eigenvectors[:, max_idx])
weights = weights / np.sum(weights)
```

CI = (lambda_max - n)/(n-1) = (7.121565 - 7)/6 = 0.020261
CR = CI / RI_7 = 0.020261 / 1.32 = **0.015349 < 0.10** (Strictly Consistent)

Renormalized driver weights (P5 excluded from denominator):
- P1: 36.64%  |  P3: 24.68%  |  P2: 16.18%  |  P4: 10.39%  |  P6: 6.06%  |  P7: 6.06%

### Step 13: Composite DLMAI Calculation
`src/scoring/composite.py` -> `compute_composite_scores(pillar_scores, driver_weights, saturation_lambda=0.15)`

```
V_i     = 0.3664*P1 + 0.2468*P3 + 0.1618*P2 + 0.1039*P4 + 0.0606*P6 + 0.0606*P7
C_i     = 0.15 * P5_score
DLMAI_i = round(V_i - C_i, 4)
```

Geometric alternative also computed (stored as `geometric_score`).

### Step 14: Ranking and Tiering
`src/scoring/composite.py` -> `assign_ranks_and_tiers(results, district_metadata)`

- South India Rank: `df["dlmai_score"].rank(ascending=False, method="min")`
- State Rank: `df.groupby("state_name")["dlmai_score"].rank(ascending=False, method="min")`
- Tier 1 (High Priority): >= p80
- Tier 2 (Growth Markets): p50 to p80
- Tier 3 (Moderate Opportunity): p20 to p50
- Tier 4 (Nascent/Rural): < p20

### Step 15: Monte Carlo Sensitivity
`src/sensitivity/monte_carlo.py` -> `run_monte_carlo_sensitivity(..., iterations=1000, random_seed=42, noise_sigma=0.20)`

```
eps_p ~ N(0, sigma^2 = 0.04)
w_p^k = w_p * exp(eps_p)  then renormalized
rho_s^k = Spearman(baseline_ranks, iteration_k_ranks)
```

### Step 16: Output Generation
Writes 9 core CSVs + 2 JSONs + 38 validation artifacts.

---

## 8. Data Sources Explained

### Source 1: NFHS-5
**Full Name:** National Family Health Survey, Round 5
**Owner:** Ministry of Health & Family Welfare + International Institute for Population Sciences (IIPS)
**Period:** 2019-2021 | **Level:** District | **Format:** PDF factsheets (one per district)
**Indicators:** Hypertension %, Diabetes %, Stunting %, Wasting %, Underweight %, Insurance %,
Clean Fuel %, Sanitation %, OOPE Delivery (INR) | **Pillars:** P1, P2
**Status:** OBSERVED where PDF parsed; IMPUTED_STATE_MEAN or IMPUTED_KNN otherwise
**Known limitations:** Cross-sectional (single time-point); newly carved districts lack separate factsheets

### Source 2: Census 2011
**Owner:** Office of the Registrar General & Census Commissioner of India
**Period:** 2011 (Census 2021 not yet published as of model development)
**Indicators:** Total Population, Urban %, Age 0-6 %, Decadal Growth %, Literacy %
**Pillars:** P1, P7
**FORENSIC NOTE:** Age 0-6 % = constant 10.2%; Decadal Growth = constant 12.4%; Literacy = state constants.
Only urban % varies (for named districts), and population is calibrated anchor.

### Source 3: RHS (Rural Health Statistics)
**Owner:** Ministry of Health & Family Welfare
**Period:** 2011 | **Level:** District | **Format:** PDF table
**Indicators:** PHC density/100k, CHC density/100k, Sub-Centre density/100k, Hospital Presence
**Pillar:** P3
**CRITICAL LIMITATION:** Covers ONLY public-sector facilities. Private hospitals, nursing homes,
and clinics are NOT counted. Metro districts with large private sectors are systematically underscored.

### Source 4: PMBJP Jan Aushadhi
**Owner:** Bureau of Pharma PSUs of India (BPPI), Government of India
**Period:** 2023-2024 | **Indicators:** Jan Aushadhi Kendra count -> density per 100k | **Pillar:** P4
**LIMITATION:** Only government generic pharmacies. Private retail pharmacies not captured.
Named districts: calibrated anchor counts. Unnamed districts: population formula (not observed).

### Source 5: MCA21 Corporate Registry
**Owner:** Ministry of Corporate Affairs, Government of India
**Period:** 2021-2024
**What it measures:** Active pharma companies registered under pharmaceutical NIC codes at their
registered office/factory address in each district. | **Pillar:** P5
**CRITICAL FORENSIC NOTE:** MCA21 records REGISTERED OFFICE LOCATION, NOT field-force deployment
or sales activity. A company registered in Hyderabad may operate across all of South India.
This is a corporate concentration proxy, NOT a competition measurement.

### Source 6: NITI Aayog Aspirational Districts
**Owner:** NITI Aayog, Government of India | **Period:** Current (2018-present)
**What it measures:** Binary flag — whether district is in the official 112 Aspirational Districts list
**Pillar:** P6
**Implementation:** Hard-coded exhaustive list in `src/ingestion/niti_aayog.py`
**Design judgment (flagged in source):** Direction = POSITIVE (aspirational = government tailwind for
pharma development). Contestable: could equally represent low purchasing power.

---

## 9. Indicator Catalog

All 20 scored indicators verified from `config/indicators.yaml`:

| # | Indicator ID | Pillar | Direction | Source | Year | Unit |
|---|---|---|---|---|---|---|
| 1 | nfhs_hypertension_combined_pct | P1 | POSITIVE | NFHS-5 | 2019-21 | % |
| 2 | nfhs_diabetes_combined_pct | P1 | POSITIVE | NFHS-5 | 2019-21 | % |
| 3 | nfhs_stunting_pct | P1 | POSITIVE | NFHS-5 | 2019-21 | % |
| 4 | nfhs_wasting_pct | P1 | POSITIVE | NFHS-5 | 2019-21 | % |
| 5 | nfhs_underweight_pct | P1 | POSITIVE | NFHS-5 | 2019-21 | % |
| 6 | census_urban_population_pct | P1 | POSITIVE | Census | 2011 | % |
| 7 | census_population_age_0_6_pct | P1 | POSITIVE | Census | 2011 | % |
| 8 | nfhs_insurance_pct | P2 | POSITIVE | NFHS-5 | 2019-21 | % |
| 9 | nfhs_clean_fuel_pct | P2 | POSITIVE | NFHS-5 | 2019-21 | % |
| 10 | nfhs_sanitation_pct | P2 | POSITIVE | NFHS-5 | 2019-21 | % |
| 11 | nfhs_oope_delivery_rs | P2 | NEGATIVE | NFHS-5 | 2019-21 | INR |
| 12 | rhs_phc_density_per_100k | P3 | POSITIVE | RHS | 2011 | Rate |
| 13 | rhs_chc_density_per_100k | P3 | POSITIVE | RHS | 2011 | Rate |
| 14 | rhs_subcentre_density_per_100k | P3 | POSITIVE | RHS | 2011 | Rate |
| 15 | rhs_hospital_presence | P3 | POSITIVE | RHS | 2011 | Count |
| 16 | jan_aushadhi_density_per_100k | P4 | POSITIVE | PMBJP | 2023-24 | Rate |
| 17 | mca21_pharma_density_per_100k | P5 | SATURATION_DAMPENER | MCA21 | 2021-24 | Rate |
| 18 | niti_aspirational_district_flag | P6 | POSITIVE | NITI Aayog | Current | Binary |
| 19 | census_decadal_growth_pct | P7 | POSITIVE | Census | 2001-11 | % |
| 20 | census_literacy_rate_pct | P7 | POSITIVE | Census | 2011 | % |

**Why malnutrition indicators = POSITIVE direction:**
High stunting/wasting/underweight signals high therapeutic demand for pediatric nutrition,
vitamins, and antibiotics. DLMAI measures market opportunity. This is demand signal framing,
explicitly acknowledged as a commercial (not welfare) perspective.

**Why OOPE = NEGATIVE direction:**
Higher out-of-pocket delivery expenditure = weaker household healthcare affordability = lower
Rx drug uptake capacity = less commercially attractive.

**Non-scored contextual variables:** `census_total_population`, `jan_aushadhi_raw_count`,
`mca21_raw_company_count`, `census_density_per_sqkm`, `census_sex_ratio`

---

## 10. Normalization

### Why It Is Needed
Raw indicators cannot be directly combined:
- Population: 0 to 9,620,000 persons
- Hypertension: 0% to 100%
- PHC density: 0 to 10 per 100,000
- OOPE: INR 0 to 50,000

Without normalization, the largest-scale indicator dominates the composite.
Normalization maps all indicators to [0, 100].

### Formula (verified from `src/scoring/normalizer.py`)

```
POSITIVE:   R_ij = (X_ij - min_j) / (max_j - min_j) * 100
NEGATIVE:   R_ij = (max_j - X_ij) / (max_j - min_j) * 100
Zero range: R_ij = 50.0
Missing:    R_ij = 50.0
```

### Example
PHC density across 3 districts: [1.2, 3.8, 6.5]
- District A (1.2): (1.2-1.2)/(6.5-1.2)*100 = 0.0
- District B (3.8): (3.8-1.2)/(6.5-1.2)*100 = 49.06
- District C (6.5): (6.5-1.2)/(6.5-1.2)*100 = 100.0

---

## 11. Shannon Entropy Intra-Pillar Weighting

### Why Different Weights for Indicators?

Some indicators discriminate strongly across 148 districts (high variation = high information value).
Others are nearly constant (low variation = near-zero information value). Entropy weights reward
discriminating indicators and penalize constant ones.

### Formula (verified from `src/scoring/entropy.py`)

```
p_ij = (R_ij + 1e-6) / sum_i(R_ij + 1e-6)      [probability share of district i]
e_j  = -(1/ln(148)) * sum_i(p_ij * ln(p_ij))    [entropy of indicator j]
d_j  = max(1 - e_j, 1e-6)                         [information utility]
w_j  = d_j / sum_j(d_j)                           [normalized weight]
S_ip = sum_j(w_j * R_ij)                          [pillar sub-score]
```

e_j -> 1.0: nearly constant indicator (no discriminating power -> near-zero weight)
e_j -> 0.0: highly variable indicator (maximum discriminating power -> high weight)

Single-indicator pillars (P4, P5, P6): w=1.0, S_ip = R_ip directly.

---

## 12. AHP Inter-Pillar Prioritization

### Why AHP?
DLMAI has 7 pillars. Expert judgment is required to decide how much more important
healthcare demand (P1) is than policy environment (P6). AHP structures this judgment
mathematically using pairwise comparisons on Saaty's 1-9 scale.

### The 7x7 Pairwise Comparison Matrix
(verified from `config/weights.yaml`)

```
        P1    P2    P3    P4    P5    P6    P7
P1  [  1.00  3.00  2.00  4.00  7.00  5.00  5.00 ]
P2  [  0.33  1.00  0.50  2.00  5.00  3.00  3.00 ]
P3  [  0.50  2.00  1.00  3.00  6.00  4.00  4.00 ]
P4  [  0.25  0.50  0.33  1.00  4.00  2.00  2.00 ]
P5  [  0.14  0.20  0.17  0.25  1.00  0.50  0.50 ]
P6  [  0.20  0.33  0.25  0.50  2.00  1.00  1.00 ]
P7  [  0.20  0.33  0.25  0.50  2.00  1.00  1.00 ]
```

### AHP Weights (verified from `outputs/ahp_validation.json`)

| Pillar | Name | AHP Weight | Renorm. Driver Weight |
|---|---|---|---|
| P1 | Healthcare Demand & Disease Burden | 35.41% | **36.64%** |
| P3 | Healthcare Infrastructure | 23.86% | **24.68%** |
| P2 | Economic Access & Affordability | 15.63% | **16.18%** |
| P4 | Pharmaceutical Distribution | 10.04% | **10.39%** |
| P6 | Policy & Development Environment | 5.85% | **6.06%** |
| P7 | Demographic & Market Growth | 5.85% | **6.06%** |
| P5 | Market Saturation (Dampener) | 3.35% | (dampener, not driver) |

### Consistency Check
lambda_max = 7.121565
CI = (7.121565 - 7) / 6 = 0.020261
RI_7 = 1.32
CR = 0.020261 / 1.32 = **0.015349 < 0.10 -- STRICTLY CONSISTENT (1.53%)**

---

## 13. Pillar Architecture

### Two-Level Weight System
Final indicator contribution to DLMAI = entropy weight (within pillar) * AHP weight (pillar) * renorm driver weight.

### Pillar 1 -- Healthcare Demand & Disease Burden
**Role:** VALUE DRIVER | **AHP Weight:** 35.41% | **Driver Weight:** 36.64%
Indicators: nfhs_hypertension, nfhs_diabetes, nfhs_stunting, nfhs_wasting, nfhs_underweight,
            census_urban_population_pct, census_population_age_0_6_pct

### Pillar 2 -- Economic Access & Affordability
**Role:** VALUE DRIVER | **AHP Weight:** 15.63% | **Driver Weight:** 16.18%
Indicators: nfhs_insurance_pct, nfhs_clean_fuel_pct, nfhs_sanitation_pct, nfhs_oope_delivery_rs (NEGATIVE)

### Pillar 3 -- Healthcare Infrastructure
**Role:** VALUE DRIVER | **AHP Weight:** 23.86% | **Driver Weight:** 24.68%
Indicators: rhs_phc_density, rhs_chc_density, rhs_subcentre_density, rhs_hospital_presence
NOTE: PUBLIC SECTOR ONLY. Private sector systematically undercounted.

### Pillar 4 -- Pharmaceutical Distribution
**Role:** VALUE DRIVER | **AHP Weight:** 10.04% | **Driver Weight:** 10.39%
Indicators: jan_aushadhi_density_per_100k (single indicator; weight=1.0)

### Pillar 5 -- Market Competition & Saturation
**Role:** VALUE DAMPENER | **Saturation lambda:** 0.15 (configurable 0.10-0.20)
Indicators: mca21_pharma_density_per_100k (single indicator; weight=1.0)
Formula: C_i = 0.15 * S_i5 (subtracted from V_i)
At max saturation (P5=100): penalty = 15 points.

### Pillar 6 -- Policy & Healthcare Development Environment
**Role:** VALUE DRIVER | **AHP Weight:** 5.85% | **Driver Weight:** 6.06%
Indicators: niti_aspirational_district_flag (binary 0/1; weight=1.0)

### Pillar 7 -- Demographic & Market Growth
**Role:** VALUE DRIVER | **AHP Weight:** 5.85% | **Driver Weight:** 6.06%
Indicators: census_decadal_growth_pct, census_literacy_rate_pct

---

## 14. DLMAI Mathematical Formula

**Verified from** `src/scoring/composite.py`:

```
DLMAI_i = max(0, min(100, V_i - C_i))

V_i = w'_P1 * S_i,P1 + w'_P3 * S_i,P3 + w'_P2 * S_i,P2
    + w'_P4 * S_i,P4 + w'_P6 * S_i,P6 + w'_P7 * S_i,P7

    = 0.3664*S_P1 + 0.2468*S_P3 + 0.1618*S_P2
    + 0.1039*S_P4 + 0.0606*S_P6 + 0.0606*S_P7

C_i = 0.15 * S_i,P5

S_i,p = sum_j(w_j^entropy * R_ij)   [pillar sub-score]
R_ij  = direction-aware min-max normalized indicator value in [0, 100]
```

### Linear Identity (verified by pytest test_05)
`DLMAI_i = value_driver_score_i - saturation_penalty_i`
Max residual across all 148 districts: < 2e-4 (rounding artifact)

---

## 15. P5 / MCA21 Forensic Construct Analysis

### What P5 Formally Measures
Active pharmaceutical enterprises registered under pharmaceutical manufacturing NIC codes in MCA21,
per 100,000 district population.

### What MCA21 Actually Records
MCA21 (Ministry of Corporate Affairs 21st Century platform) maintains:
- Company name
- Registered office address / factory location -> district
- NIC code for industry type
- Active/dormant/struck-off status

A query for pharmaceutical NIC codes returns companies REGISTERED in a district -- not companies
OPERATING their field force there.

### Critical Distinction

```
WHAT P5 MEASURES:
  Registered pharma corporate offices / factories per 100k pop

WHAT P5 DOES NOT MEASURE:
  Field medical representatives (MRs) deployed per district
  Retail pharmacy visit intensity
  Brand competition at chemist/stockist level
  Prescriber relationship density
  Secondary sales agent coverage
```

A company registered in Hyderabad may deploy MRs across all 148 South Indian districts.

### Why P5 Still Has Value
Despite not measuring field-force competition directly, pharma company registrations indicate:
- Pharmaceutical manufacturing hub activity
- Corporate infrastructure and supply-chain presence
- Economic activity correlated with healthcare sophistication

### Ablation Results (verified from `test05_p5_ablation.csv`)
- Remove P5 entirely (lambda=0.0): Spearman rho = **0.9804** -- rankings very stable
- P5 as positive driver (wrong direction): rho = 0.9645
- Lambda sweep 0.05-0.25: all rho >= 0.9979

**P5 is a minor adjustment, not a primary driver.**

### Formal Classification
"Pharmaceutical Manufacturing & Corporate Concentration Proxy -- not a direct measurement of
active commercial field-force saturation" (Decision 4, `docs/DLMAI_Model_Decision_Log.md`)

---

## 16. Ranking and Tiering

**File:** `src/scoring/composite.py` -> `assign_ranks_and_tiers()`

### Rankings
- South India Rank: `pandas.rank(ascending=False, method="min")` across all 148 districts
- State Rank: grouped rank within each state
- Ties receive identical rank (no arbitrary tie-breaking)

### Quantile Tiering
| Tier | Percentile Cutoff | ~Districts | Commercial Strategy |
|---|---|---|---|
| Tier 1 (High Priority) | >= p80 | ~30 | Specialty field force, tertiary hospital KAM, stockist hubs |
| Tier 2 (Growth Markets) | p50 to p80 | ~44 | Retail expansion, secondary hospital coverage |
| Tier 3 (Moderate Opportunity) | p20 to p50 | ~44 | Generic portfolio, Jan Aushadhi alignment |
| Tier 4 (Nascent / Rural) | < p20 | ~30 | Government tenders, primary clinic coverage |

Why quantile-based: Ensures exactly 20% in Tier 1 regardless of score distribution, providing
consistent field force allocation planning.

---

## 17. Monte Carlo Uncertainty Analysis

**File:** `src/sensitivity/monte_carlo.py` -> `run_monte_carlo_sensitivity()`

### Method
```
eps_p ~ N(0, sigma^2 = 0.04)     [sigma = 0.20 = +-20% typical perturbation]
w_p^(k) = w_p * exp(eps_p)       [log-normal weight perturbation]
w_p^(k) renormalized so all driver weights sum to 1.0
Recompute all 148 DLMAI scores and rankings for iteration k
rho_s^(k) = Spearman(baseline_ranks, iteration_k_ranks)
```

### Results (verified from `test07_monte_carlo_global.csv`)
| Run | N | Mean Spearman rho | Mean Kendall tau |
|---|---|---|---|
| Primary | 1,000 | **0.9922** | **0.9367** |
| Validation | 5,000 | Consistent | Consistent |

Assessment: **HIGHLY STABLE** (threshold: rho >= 0.95)

### Per-District Output
Each district in `test07_monte_carlo_district.csv` has:
mean_sim_rank, rank_std_dev, rank_ci_lower_2_5, rank_ci_upper_97_5,
top_10_frequency_pct, top_20_frequency_pct

Random seed = 42 (config/sensitivity.yaml) -- guarantees exact reproducibility.

---

## 18. Complete 8-Test Validation Framework

All 8 tests run via `scripts/red_team_validation/run_all_validation.py`.
All results asserted by 24 automated pytest tests.

### Test 1 -- Fully Independent Model Recomputation

**Question:** Does an independent reimplementation reproduce exact production scores?
**Method:** Does NOT import from src/scoring/*. Reimplements all formulas in plain Python/NumPy.
**Results:**
- Max absolute score error: 1e-4 (output serialization rounding)
- Max rank difference: **0** (zero rank mismatches across all 148 districts)
- Tier mismatches: 0
- AHP CR (independent): 0.015349

**Verdict: PASSED**

### Test 2 -- Normalization Sensitivity

**Question:** How sensitive are rankings to normalization method choice?
**4 methods tested:** Min-Max, Robust IQR, Percentile Rank, Winsorized (5th-95th)

| Method | Fixed Weights rho | Recomputed Weights rho |
|---|---|---|
| Min-Max (baseline) | 1.0000 | 1.0000 |
| Robust IQR | **1.0000** | **1.0000** |
| Percentile Rank | 0.8546 | 0.7179 |
| Winsorized 5-95 | 0.9766 | 0.7309 |

Robust IQR produces identical rankings -> Min-Max not distorted by outliers.
**Verdict: PASSED**

### Test 3 -- Top-N Decision Robustness

**Question:** Which districts are robust vs. sensitive across model variants?
**Method:** 10 defensible model variants. Per-district Top-5/10/20 inclusion frequency.

| Category | Threshold | Count |
|---|---|---|
| Invariant | 100% inclusion | 1 (Palakkad) |
| High-Robustness | >=90% inclusion | 81 |
| Sensitive | <90% | 63 |
| Volatile | <50% | 0 |

**Verdict: PASSED**

### Test 4 -- Data Quality Bias Audit

**Question:** Do districts with more observed data score artificially higher?
**Result:**
- Pearson r(completeness, DLMAI) = **-0.0820** (p = 0.3220, R^2 = 0.007)
- Slightly negative (not positive) correlation
- No detectable positive quality bias

**Verdict: PASSED** (pytest asserts obs_corr <= 0.10)

### Test 5 -- P5 Saturation Ablation

**Question:** How much does P5 affect rankings? What if sign is reversed?
**Key results:**
- Remove P5 (lambda=0.0): rho = 0.9804
- Reverse P5 sign: rho = 0.9645
- Lambda sweep 0.05-0.25: all rho >= 0.9979
- P5 is minor adjustment, not primary driver.

**Verdict: PASSED**

### Test 6 -- 4-Axis Strategic Component Decomposition

| Component | Description | Pearson r with DLMAI |
|---|---|---|
| Need Score | Pillar 1 (Disease Burden) | 0.6277 |
| Access Score | Pillars 2+3 (Economic + Infrastructure) | 0.6539 |
| Growth Score | Pillar 7 (Growth Momentum) | 0.4115 |
| Competition Score | Pillar 5 (Saturation) | -0.2056 |

Need and Access are the primary drivers. Competition slightly negatively correlated (expected).
**Verdict: PASSED**

### Test 7 -- Monte Carlo Uncertainty

Mean Spearman rho = 0.9922 (N=1,000)
Mean Kendall tau = 0.9367
Assessment: HIGHLY_STABLE (Target Met)
**Verdict: PASSED**

### Test 8 -- External Commercial Validation

See Section 19 for complete forensic findings.
**Verdict: AUDITED -- CLASS D: CALIBRATED/SYNTHETIC BENCHMARK (NOT TRUE EXTERNAL VALIDATION)**

---

## 19. Test 8 -- Forensic External Commercial Validation

### What Test 8 Attempted
Test 8 (`scripts/red_team_validation/test08_external_commercial_validation.py`) attempted to
validate DLMAI against district-level pharmaceutical sales (INR Crores).

### What the Benchmark Data Actually Is

**From `test08_district_provenance_summary.json`:**
```
total_districts_evaluated: 148
number_with_directly_observed_district_sales: 0
number_with_derived_sales: 148
district_provenance_classification: "SYNTHETIC / CALIBRATED BENCHMARK -- ZERO DIRECTLY OBSERVED DISTRICT SALES"
```

**How the benchmark was constructed:**
1. State macro targets (INR Crores): TN=18200, KA=14500, AP=11200, TS=10800, KL=9600, GA=1250, PY=850
   Total: INR 66,400 Cr -- estimated South India market size (NOT invoice-observed)
2. District allocations = state_total * population_weight * urbanization_adjustment + lognormal_noise

This is top-down allocation, not bottom-up invoice observation.

### Commercial Variable Provenance

| Variable | Generation Method | Status |
|---|---|---|
| annual_pharma_sales_inr_cr | Calibrated state allocation via population & urbanization | SYNTHETIC_CALIBRATED |
| pharma_sales_usd_million | Currency conversion from above (/ 8.35) | DERIVED_FROM_SYNTHETIC |
| per_capita_consumption_inr | sales * 10M / population | DERIVED_FROM_SYNTHETIC |
| chronic_ncd_sales_inr_cr | Simulated therapy share formula (42% + 0.20*urban_pct) | SYNTHETIC_CALIBRATED |
| acute_therapy_sales_inr_cr | Residual: total - chronic | DERIVED_FROM_SYNTHETIC |
| monthly_rx_volume_index | Simulated per-capita index | SYNTHETIC_INDEX |

### Circularity Analysis (from `test08_circularity_matrix.csv`)

| Variable | Used in Benchmark | Circularity Risk |
|---|---|---|
| census_total_population | YES | VERY HIGH (r=0.94) |
| census_urban_population_pct | YES | HIGH (r=0.58) |
| rhs_hospital_presence | YES | MODERATE (r=0.42) |
| jan_aushadhi_raw_count | YES | MODERATE (r=0.39) |
| **dlmai_score** | **NO** | **NONE** |

Direct score leakage: ABSENT
Covariate circularity: PRESENT (4 shared input variables)

### Baseline Comparison (from `test08_baseline_comparison.csv`)

| Model | OOS 5-Fold R^2 |
|---|---|
| Baseline A: Population Only | **0.8821** |
| Baseline B: Population + Urbanization | **0.9380** |
| Model E: DLMAI Score Only | **-0.0733** |

Population dominates gross rupee volume because the benchmark was population-proportional.
DLMAI has negative OOS R^2 on gross volume because it is a per-capita INTENSITY index, not a volume predictor.
On per-capita healthcare intensity: DLMAI beta = +46.12, p < 0.0001 (statistically significant).

### LOSO Cross-Validation
Goa (n=2) and Puducherry (n=4) flagged: INSUFFICIENT_SAMPLE (verified by pytest test_14).

### Final Classification
> **CLASS D: CALIBRATED / SYNTHETIC BENCHMARK -- NOT TRUE EXTERNAL VALIDATION**

The project CANNOT claim "empirically validated pharmaceutical sales predictor."
The project CAN claim "Class B: Statistically Defensible Internal Market Attractiveness Index."

### What Real External Validation Requires (Phase 2)
- District-level secondary pharmaceutical sales invoices from AIOCD-AWACS or IQVIA TSA
- At least 3 years of historical district-level data
- Independent data with no overlap with DLMAI input indicators
- Out-of-sample or prospective validation

---

## 20. Data Leakage and Circularity Audit

### Simple Explanation
Data leakage occurs when the model "cheats" by using the answer as a feature.
Circularity occurs when the same variables appear in both the model and the outcome benchmark.

### DLMAI Circularity Findings

Direct target leakage (DLMAI composite score used in benchmark): **ABSENT**
Verified by `tests/test_red_team_validation.py::test_12_test08_no_direct_dlmai_leakage`

Covariate circularity: **PRESENT**
Population, urbanization, hospital count, and Jan Aushadhi count appear in both
DLMAI inputs AND benchmark generation formula.

This is why the simple population model achieves R^2=0.88 while DLMAI achieves R^2=0.005
on gross rupee volume -- the benchmark was largely population-proportional.

---

## 21. Automated Test Suite Architecture

### Two Layers
```
Layer 1: Statistical Red-Team Tests (scripts/red_team_validation/)
  8 tests, each generating CSV/JSON output artifacts

Layer 2: Pytest Regression Suite (tests/)
  test_red_team_validation.py  -- 14 tests assert on Layer 1 outputs
  test_south_india_methodology.py -- 10 unit/integration tests of src/ modules
```

### Run Command
```bash
python -m pytest tests/test_red_team_validation.py tests/test_south_india_methodology.py -v
```
Expected: **24 passed in ~3.5s**

### What Each Test Protects

| Test | Protects Against |
|---|---|
| test_01_independent_score_reconciliation | Silent formula bugs in production code |
| test_02_ahp_mathematical_consistency | Inconsistent weight structures (CR >= 0.10) |
| test_03_canonical_geography_integrity | Scope creep (not exactly 148/7 states) |
| test_04_indicator_catalog_and_domain_integrity | Missing indicators, NaN/Inf values |
| test_05_dlmai_linear_identity_exactness | V-C identity broken by rounding |
| test_06_normalization_decomposition_stability | Normalization method sensitivity |
| test_07_topn_inclusion_probabilities | Top-N probability out of [0,100] range |
| test_08_data_quality_bias_absence | Quality-score positive bias (r > 0.10) |
| test_09_monte_carlo_convergence | Stability degradation (rho < 0.95) |
| test_10_master_validation_dataset_completeness | Master CSV missing rows or columns |
| test_11_test08_provenance_transparency | Undisclosed synthetic data |
| test_12_test08_no_direct_dlmai_leakage | Score used in benchmark construction |
| test_13_test08_baseline_comparison_exists | Population baseline not computed |
| test_14_test08_small_sample_warning_flags | Goa/Puducherry LOSO not flagged |
| test_geographic_scope_and_district_count | 7 states not loaded correctly |
| test_indicator_count_and_pillar_reconciliation | 20 indicators not mapped to 7 pillars |
| test_ahp_mathematics_and_consistency | Reciprocity, hierarchy order, weight sum |
| test_direction_aware_normalization | Positive/negative direction logic error |
| test_intra_pillar_entropy_weights | High-variance indicator not weighted higher |
| test_saturation_dampener_mathematics | Penalty=15 at P5=100 assertion |
| test_multi_generation_inheritance | Child not inheriting parent value |
| test_quantile_tier_distribution | Tier 1 != 30 districts |
| test_monte_carlo_reproducibility | Different seeds giving same result |
| test_output_deliverables_integrity | Required output files missing or empty |

---

## 22. Output Files Reference

### Primary Outputs (`outputs/`)

| File | Rows | Key Columns |
|---|---|---|
| `dlmai_south_india_scores.csv` | 148 | lgd_district_code, district_name, state_name, dlmai_score, south_india_rank, state_rank, commercial_tier, value_driver_score, saturation_penalty, geometric_score, pillar_p1-p7_scores |
| `dlmai_south_india_combined_output.csv` | 148 | All 20 indicators + provenance per indicator |
| `ahp_validation.json` | JSON | weights, lambda_max:7.121565, consistency_ratio:0.015349 |
| `refresh_metadata.json` | JSON | model_version, highest_score, mean_dlmai_score, stability |
| `sensitivity_results.csv` | 148 | baseline_rank, mean_sim_rank, rank_std_dev, ci_lower/upper, top_10/20_pct |
| `robustness_comparison.csv` | 148 | baseline_rank, equal_pillar_rank, no_saturation_rank |
| `data_quality_report.csv` | 148 | observed_pct, inherited_pct, imputed_pct, data_quality_score |
| `district_coverage_matrix.csv` | 148 | Provenance label per indicator per district |
| `indicator_redundancy_report.csv` | 20x20 | Pairwise Pearson correlations |

### Validation Outputs (`outputs/red_team_validation_v2/`)

38 artifacts total. Key files:

| File | Description |
|---|---|
| `dlmai_district_validation_master.csv` | **Master cross-test dataset** -- 148 rows x 31 cols |
| `test01_independent_recalculation.csv` | Side-by-side: independent vs. production scores |
| `test01_reconciliation_summary.json` | Max error, rank diffs, AHP CR |
| `test03_topn_robustness.csv` | Top-5/10/20 inclusion probabilities per district |
| `test07_monte_carlo_district.csv` | Per-district rank statistics (N=1,000) |
| `test08_data_provenance_audit.csv` | Full provenance for all 7 commercial variables x 148 districts |
| `test08_district_provenance_summary.json` | 0 observed / 148 derived verdict |
| `test08_baseline_comparison.csv` | R^2: population vs. DLMAI vs. combined |
| `test_run_metadata.json` | File SHA-256 hashes, execution time, test results |

---

## 23. Complete Execution Guide

### Prerequisites
```bash
pip install pdfplumber>=0.10 reportlab>=4.0 streamlit>=1.30 pandas>=2.0 numpy>=1.24
pip install scipy scikit-learn pyyaml
```

### Step 1: Prepare Data
```
data/master/lgd_south_india.csv              (148-row LGD master)
data/master/district_crosswalk_south.csv     (alias mappings)
data/nfhs/district/<state>/<district>.pdf    (NFHS-5 factsheets)
data/rhs/district-wise-health-centres.pdf    (MoHFW RHS table)
```

LGD master format:
```csv
lgd_district_code,district_name,state_name,state_lgd_code,census_2011_code
560,Bengaluru Urban,Karnataka,29,602
```

### Step 2: Run Core Pipeline
```bash
python -c "from src.pipeline import run_south_india_pipeline; run_south_india_pipeline()"
```

### Step 3: Run Validation Suite
```bash
python scripts/red_team_validation/run_all_validation.py
```

### Step 4: Run Automated Tests
```bash
python -m pytest tests/test_red_team_validation.py tests/test_south_india_methodology.py -v
```
Expected: **24 passed**

### Step 5: Launch Dashboard
```bash
streamlit run dashboard_app.py
```

### Step 6: Verify Key Output
```bash
python -c "
import pandas as pd
df = pd.read_csv('outputs/dlmai_south_india_scores.csv')
print(df[['district_name', 'state_name', 'dlmai_score', 'south_india_rank', 'commercial_tier']].head(10))
"
```

---

## 24. Troubleshooting and Failure Modes

| Failure | Behavior | Risk | Fix |
|---|---|---|---|
| lgd_south_india.csv missing | FileNotFoundError at startup | Pipeline cannot run | Restore from data/master/ |
| NFHS-5 PDF missing for district | District gets STILL_MISSING -> state mean imputation | Minor | Add PDF to data/nfhs/district/ |
| District name unmatched | Ingestion silently skipped | Moderate | Add alias to district_crosswalk_south.csv |
| Duplicate LGD codes in master | test_03 fails | High | Deduplicate lgd_south_india.csv |
| AHP CR >= 0.10 | test_02 fails; pipeline continues | High | Revise config/weights.yaml AHP matrix |
| scipy/sklearn not installed | ImportError in MC/Test8 | Pipeline fails | pip install scipy scikit-learn |
| All indicator values zero-variance | Entropy fallback to equal weights | Low | Check normalization inputs |
| STILL_MISSING survives all imputation | 50.0 midpoint fallback used at normalization | Minor | Investigate why all 3 tiers failed |

---

## 25. Code Architecture and File-to-Function Map

| File | Function / Class | Purpose | Called By |
|---|---|---|---|
| `src/config.py` | ConfigManager.__init__() | Load all 6 YAMLs | src/pipeline.py |
| `src/config.py` | get_config() | Singleton accessor | All src modules |
| `src/harmonization/crosswalk.py` | normalize_name(name) | Standardize district names | crosswalk, tests |
| `src/harmonization/crosswalk.py` | SouthDistrictCrosswalk.__init__() | Build district lookup | pipeline, tests |
| `src/harmonization/crosswalk.py` | SouthDistrictCrosswalk.resolve() | Name -> LGD code | pipeline ingestion |
| `src/harmonization/inheritance.py` | SouthInheritanceResolver.fill_missing() | Parent-child inheritance | pipeline step 8 |
| `src/ingestion/nfhs_parser.py` | parse_nfhs_factsheet(pdf_path) | Extract NFHS indicators | pipeline step 4 |
| `src/ingestion/rhs_parser.py` | extract_all_rhs_rows(pdf_path) | Extract health centre counts | pipeline step 5 |
| `src/ingestion/niti_aayog.py` | is_aspirational_district(name) | Binary aspirational flag | pipeline step 7 |
| `src/imputation/engine.py` | SouthImputationEngine.impute_matrix() | 3-tier hierarchical imputation | pipeline step 9 |
| `src/scoring/normalizer.py` | min_max_normalize(values, direction) | [0,100] normalization | pipeline step 10 |
| `src/scoring/entropy.py` | calculate_entropy_weights(matrix, indicators) | Objective intra-pillar weights | pipeline step 11 |
| `src/scoring/ahp.py` | calculate_ahp_weights(matrix, criteria) | AHP eigenvector + CR | pipeline step 12 |
| `src/scoring/composite.py` | compute_composite_scores() | DLMAI = V - C | pipeline step 13 |
| `src/scoring/composite.py` | assign_ranks_and_tiers() | Rank + quantile tier | pipeline step 14 |
| `src/sensitivity/monte_carlo.py` | run_monte_carlo_sensitivity() | Log-normal MC, N=1000 | pipeline step 15 |
| `scoring_engine.py` (root) | score_districts() | LEGACY standalone engine | Legacy scripts only |

---

## 26. Documentation vs. Implementation Audit

| Claim | Documentation | Code Reality | Status |
|---|---|---|---|
| 148 canonical districts | States 148 | lgd_south_india.csv has 148 rows; enforced by Test 1 assert | IMPLEMENTED |
| 20 scored indicators | States 20 | indicators.yaml has 20 is_scored entries | IMPLEMENTED |
| 7 pillars | States 7 | pillars.yaml defines exactly 7 pillars | IMPLEMENTED |
| AHP CR = 0.015349 | States < 0.10 | ahp_validation.json confirms 0.015349 | IMPLEMENTED |
| Shannon entropy weighting | Described formally | src/scoring/entropy.py implements exactly | IMPLEMENTED |
| Monte Carlo N=1000, sigma=0.20, seed=42 | States these values | config/sensitivity.yaml specifies exactly | IMPLEMENTED |
| MCA21 = competition proxy | "P5 measures market saturation" | Source code notes: registered office, not field-force | PARTIAL -- construct limitation documented |
| DLMAI = V - C formula | States formula | composite.py: dlmai = round(v_score - c_penalty, 4) | IMPLEMENTED |
| Quantile tiering p80/p50/p20 | States cutoffs | composite.py uses df.quantile(0.80) etc. | IMPLEMENTED |
| Test 8 = external commercial validation | "External validation" | test08_district_provenance_summary.json: 0/148 observed | CONTRADICTED -- Class D only |
| Census indicators district-observed | Implied | age_0_6=10.2 constant; decadal_growth=12.4 constant | PARTIAL -- state constants |
| Jan Aushadhi directly observed | Implied PMBJP portal | Named: calibrated anchors; unnamed: population formula | PARTIAL |
| Zero imputation never applied | Decision 7 | engine.py: state mean -> kNN -> STILL_MISSING | IMPLEMENTED |

---

## 27. Project Maturity Assessment

| Dimension | Rating | Evidence |
|---|---|---|
| Statistical Methodology | GREEN | 8-test validation; AHP CR<0.10; MC rho=0.9922 |
| Mathematical Reproducibility | GREEN | Max error 1e-4, 0 rank mismatches |
| Model Robustness | GREEN | 81/148 High-Robustness; HIGHLY STABLE MC |
| Test Coverage | GREEN | 24/24 automated tests passing |
| Governance Documentation | GREEN | 10 formal decisions documented |
| Data Provenance Tracking | GREEN | Every cell has provenance label |
| Geographic Accuracy | YELLOW | LGD-correct 148 districts; newly carved inherit parent data |
| NFHS-5 Data Quality | YELLOW | Observed where PDFs available; imputed otherwise |
| Census Data Quality | YELLOW | Several indicators are state-level constants |
| Jan Aushadhi / MCA21 Data | YELLOW | Named districts calibrated; others population formula |
| P5 Construct Validity | ORANGE | Corporate concentration != field-force competition |
| External Validation | RED | Class D only -- no independently observed district sales |
| Production Infrastructure | YELLOW | No CI/CD, no Docker, no API layer |
| Private Infrastructure Data | RED | No private hospitals, clinics, or retail pharmacy data |

---

## 28. Valid vs. Invalid Claims

### VALID CLAIMS

- "DLMAI ranks 148 South Indian districts systematically across 20 government-sourced indicators."
- "The methodology is statistically reproducible (max error 1e-4, zero rank mismatches)."
- "AHP weights are internally consistent (CR = 0.015349 < 0.10)."
- "The model is robust to +-20% weight perturbation (MC rho = 0.9922)."
- "81/148 districts are High-Robustness across 90%+ of 10 defensible variants."
- "No positive data quality bias detected (Pearson r = -0.082, p = 0.322)."
- "Removing P5 produces 98.04% correlated ranking -- dampener is minor adjustment."
- "DLMAI is a statistically defensible Class B internal market attractiveness index."

### INVALID / PREMATURE CLAIMS

- "DLMAI is empirically validated against pharmaceutical sales data."
  REALITY: Test 8 uses synthetic/calibrated benchmark. 0/148 districts have directly observed sales.

- "DLMAI predicts actual pharmaceutical revenue."
  REALITY: On gross rupee volume, DLMAI OOS R^2 = -0.073. Population alone: R^2 = 0.88.

- "P5 measures field-force competition."
  REALITY: P5 measures registered pharma corporate offices per 100k, NOT deployed MRs.

- "DLMAI uses district-level Census 2011 data for all indicators."
  REALITY: age_0_6_pct and decadal_growth_pct are constants; literacy is state-level constant.

- "Palakkad is objectively the most attractive South Indian district."
  REALITY: Palakkad ranks #1 under THIS methodology. Different defensible assumptions can change the top-ranked district.

---

## 29. Model Governance Log Summary

10 formal decisions documented in `docs/DLMAI_Model_Decision_Log.md`:

| # | Decision | Outcome |
|---|---|---|
| 1 | Geographic Scope | Dedicated South India 148-district model vs. national 785-district |
| 2 | Indicator Count | 20 scored (eliminated jan_aushadhi_raw_count as collinear with density, r=0.88) |
| 3 | AHP Weight Derivation | Dynamic eigenvector (CR=0.015349) vs. legacy hardcoded values |
| 4 | P5 Formulation | Value Dampener (DLMAI = V - lambda*P5) vs. inverted negative indicator |
| 5 | Malnutrition Direction | POSITIVE (demand signal for pediatric therapeutics) |
| 6 | SECC Exclusion | State-level only; not suitable for district scoring |
| 7 | Missing Data | Zero never imputed; 3-tier fallback + full provenance tracking |
| 8 | Tiering Methodology | Quantile (p80/p50/p20) vs. fixed thresholds or natural breaks |
| 9 | 7-Test Statistical Validation | Formal Class B certification |
| 10 | External Commercial Validation | Test 8 classified as Class D; no empirical validation claim |

---

## 30. Industry Presentation Guide

### For Non-Technical Executives (2 minutes)

"We faced a territory prioritization problem: 148 South Indian districts, limited field force budget.
Which 30 districts deserve Priority 1 deployment?

DLMAI is our systematic answer. It evaluates every district on 20 factors across 7 dimensions:
disease burden, ability to pay, healthcare infrastructure, pharmacy reach, government policy focus,
population growth, and competitive crowding. Each district gets a score. Top 30 go to Tier 1.

It was stress-tested 1,000 times -- 99.2% of rankings held up regardless of assumption changes.
It's a tool to make territory allocation data-driven and defensible. Not a crystal ball."

---

### For Data Scientists (5 minutes)

"DLMAI is a MCDA composite index over 148 South Indian districts. Pipeline:
1. Ingest 20 indicators from 6 government sources (NFHS-5, Census, RHS, Jan Aushadhi, MCA21, NITI Aayog)
2. Missing data: parent-district lineage inheritance -> state mean -> population kNN
3. Direction-aware min-max normalization to [0,100]
4. Shannon entropy for intra-pillar objective indicator weighting
5. Saaty AHP for inter-pillar weighting (7x7, CR=0.015349)
6. DLMAI_i = V_i - 0.15*S_i5
7. 8-test adversarial validation (normalization sensitivity, Top-N robustness, MC N=1000, rho=0.9922)

Key limitation: Test 8 external benchmark is synthetic top-down allocation. Zero district invoice data.
Model is Class B internally valid, not empirically externally validated."

---

### For Statisticians (10 minutes)

"Linear composite: DLMAI_i = sum_p(w'_p * S_ip) - lambda*S_i,P5
Intra-pillar weights from Shannon entropy (d_j = 1-e_j, normalized).
Inter-pillar weights from Saaty AHP principal eigenvector (CR=0.015349).
Normalization: direction-aware min-max with midpoint=50.0 fallback for ties/missing.
Missing data: multi-generation lineage inheritance, state mean, population kNN.
MC uncertainty: log-normal sigma=0.20, N=1000, mean rho=0.9922, tau=0.9367.
Data quality bias: Pearson r(completeness, DLMAI) = -0.082, p=0.322, R^2=0.007.

External validation (Test 8): synthetic benchmark from state-level macro totals (INR 66,400 Cr)
allocated by population*urbanization + lognormal noise. Population baseline R^2=0.88 vs. DLMAI
R^2=0.005 on gross volume. Formal classification: Class D. Covariate circularity documented."

---

### For Pharmaceutical Commercial Leaders

"The business problem is territory prioritization. DLMAI tells you which South Indian districts
are most commercially attractive. It combines disease burden (demand), economic access and
insurance (ability to pay), healthcare infrastructure (prescriber density), pharmacy distribution,
government policy environment, and population growth -- penalized for competitive crowding.

Tier 1 districts (~30): specialty field force, tertiary hospital empanelment, stockist hubs.
Tier 4 districts (~30): government tenders, primary clinic coverage.

Built entirely from government data. Transparent, auditable, reproducible.
Stress-tested 1,000 times with different assumptions.

Important caveat: NOT validated against actual Rx or secondary sales data. It is a systematic
analytical input to territorial decisions, not a guarantee of commercial outcome."

---

### For ML/Data Engineering Interviewers

"Full-stack data science pipeline:
- Data Engineering: Multi-source PDF/CSV ingestion; LGD geographic standardization with fuzzy
  name matching (difflib, threshold 0.84); fixed-point parent-child inheritance for newly carved
  districts; 3-tier hierarchical imputation with cell-level provenance tracking.
- Statistical Modeling: Shannon entropy for objective intra-pillar weighting; Saaty AHP for
  inter-pillar prioritization with CR validation; linear composite with saturation dampener.
- Validation: 8-test adversarial suite including normalization sensitivity, Top-N decision
  robustness across 10 variants, data quality bias regression, P5 ablation, 4-axis decomposition,
  Monte Carlo (N=1,000, rho=0.9922), and forensic commercial provenance audit.
- Testing: 24 automated pytest assertions covering mathematical exactness, geography integrity,
  entropy properties, AHP reciprocity, Monte Carlo reproducibility, provenance transparency.

Key honest finding: External commercial validation (Test 8) failed Class A/B because benchmark
is synthetic top-down allocation, not independently observed invoice data. Model is Class B internally."

---

## 31. Interview Preparation

### Beginner Level

Q: What is DLMAI?
A: A composite score ranking South Indian districts by pharmaceutical market attractiveness using
   20 indicators from 6 government sources.
NOT: "A machine learning model that predicts sales."

Q: What are the 7 pillars?
A: P1-Demand, P2-Economic Access, P3-Infrastructure, P4-Distribution, P5-Competition(Dampener),
   P6-Policy, P7-Growth.

Q: Why is normalization needed?
A: Converts all indicators to [0,100] so incompatible units (%, counts, INR) can be combined.
   Without it, population (in millions) would dominate over hypertension (in %).
NOT: "It makes data Gaussian."

---

### Intermediate Level

Q: Explain Shannon entropy weighting.
A: Indicators with high cross-district variance receive high weights; near-constant indicators
   receive near-zero weights. Entropy measures information content -- higher variance = more
   discriminating = lower entropy = higher weight.

Q: What does CR = 0.015349 mean?
A: The AHP pairwise comparison matrix has CR = 1.53%, well below the 0.10 threshold.
   The expert's pillar judgments are internally consistent -- no contradictions.

Q: How is missing data handled?
A: 3-tier fallback: (1) parent district inheritance for newly carved districts, (2) state mean,
   (3) population-weighted kNN. Zero is NEVER imputed. Every cell has a provenance label.

---

### Advanced Level

Q: Why does Palakkad rank #1?
A: Palakkad has high P1 (strong NCD burden -- hypertension/diabetes in Kerala context), strong
   P3 (rural public health infrastructure), high P4 (Jan Aushadhi density), P6 (aspirational
   district), and low P5 (low MCA21 corporate saturation). High demand + good infrastructure
   + low competition = highest composite score.

Q: What is Test 8's forensic finding?
A: 0/148 districts have directly observed invoice-level sales data. All benchmarks are synthetically
   allocated from state-level macro totals using population and urbanization proxies. Four DLMAI
   input variables were used in benchmark construction (covariate circularity). The benchmark cannot
   constitute true external validation. Classification: Class D.

Q: Why does population baseline (R^2=0.88) outperform DLMAI (R^2=0.005)?
A: The commercial benchmark was constructed by allocating state totals proportionally to district
   population. Population-weighted allocation produces population-correlated outcomes by construction.
   DLMAI is a per-capita INTENSITY index (scale-free), not a gross volume predictor.

---

### Expert Level

Q: The entropy module uses global k=1/ln(M) where M=148. The legacy scoring_engine.py uses
   per-indicator n for k. Which is correct?

A: The production src/scoring/entropy.py correctly uses global k=1/ln(148) for all indicators in the
   same pillar, because all indicators are evaluated across the same 148 districts after full
   imputation ensures no missing values. The legacy scoring_engine.py uses per-indicator n (count
   of non-None values), which would give different k values for indicators with different missing
   counts -- producing arbitrarily unequal weights for equally uninformative constant indicators.
   The production path is methodologically correct.

Q: Why does P5 use direction=SATURATION_DAMPENER but get normalized identically to POSITIVE?

A: The normalization formula is identical to POSITIVE (higher raw value -> higher normalized score
   [0-100]). This is intentional: more pharma companies -> higher saturation score (P5_normalized).
   This score is then SUBTRACTED: C_i = 0.15 * S_i5. So POSITIVE normalization correctly
   maps "more companies = higher saturation = larger penalty subtracted from DLMAI."
   SATURATION_DAMPENER is a semantic direction label for downstream logic, not a formula modifier.

---

## 32. Glossary

| Term | Simple Meaning | Technical Meaning |
|---|---|---|
| AHP | Expert judgment structured mathematically | Saaty pairwise comparison -> principal eigenvector -> priority weights. CR < 0.10 validates. |
| Calibrated Data | Numbers calculated to match a total | Benchmark generated by allocating macro total to geographies using proxy variables. |
| Circularity | Same info on both sides of comparison | Shared inputs between model features and outcome benchmark construction formula. |
| Composite Index | Many measures combined into one | Linear/non-linear aggregation of standardized indicators with assigned weights. |
| CR | How consistent are the judgments? | Consistency Ratio = CI/RI. CI=(lambda_max-n)/(n-1). CR < 0.10 = consistent. |
| Data Leakage | Model cheats by using the answer | Target variable appears in training features. |
| Direction | Does more mean better? | POSITIVE: higher -> higher score. NEGATIVE: higher -> lower score. |
| Entropy | How spread out / variable is the data? | Shannon entropy: H = -sum(p_i * ln(p_i)). Higher entropy = more uniform = less information. |
| Imputation | Filling in missing values | Statistical estimation using available information. |
| Inheritance | New district borrows parent data | Child districts carved from parents receive parent's indicator values. |
| LGD Code | Unique ID for every Indian district | Local Government Directory integer code from Ministry of Panchayati Raj. |
| Min-Max Normalization | Stretch data to fit 0-100 | R = (x - x_min)/(x_max - x_min) * 100. |
| Monte Carlo | Run model thousands of times with noise | Stochastic simulation with perturbed parameters to assess sensitivity. |
| NFHS | India's household health survey | National Family Health Survey -- district PDF factsheets from IIPS/MOHFW. |
| OLS | Best straight line through data | Ordinary Least Squares regression -- minimizes sum of squared residuals. |
| OOPE | How much patients pay from pocket | Out-of-Pocket Expenditure -- household costs not covered by insurance. |
| P5 / MCA21 | Pharma companies registered in district | MCA21 count of active pharma companies at registered office per 100k population. |
| Pillar | Category of related indicators | Domain cluster of thematically related indicators aggregated into one sub-score. |
| Provenance | Where did this number come from? | Audit trail: OBSERVED / INHERITED / IMPUTED_STATE_MEAN / IMPUTED_KNN / STILL_MISSING. |
| R-squared | How much variation explained? | Coefficient of determination. 1=perfect. 0=no better than mean. Negative=worse than mean. |
| RHS | Government's health facility count | Rural Health Statistics -- Ministry of Health & Family Welfare. Public sector only. |
| Saturation Dampener | Subtract penalty for crowded markets | C_i = lambda * S_i,P5. Lambda=0.15. Reduces score for high pharma-concentration districts. |
| Spearman rho | How similar are two rankings? | Non-parametric rank correlation. 1=identical ranking. 0=no relationship. |
| Synthetic Data | Numbers created by formula, not measured | Data generated computationally rather than collected from the real world. |
| Tiering | Grouping districts into priority categories | Quantile-based. Tier 1 >= p80; Tier 4 < p20. 4 commercial tiers. |
| Validation | Checking the model is correct | Internal: mathematical consistency. External: independent outcome data. |
| Value Driver | Pillar that increases DLMAI | Positive contribution to composite. V_i = sum of w'_p * S_ip for p != P5. |
| AIOCD-AWACS | India's pharma sales audit | All India Organisation of Chemists & Druggists secondary sales tracking. Not yet ingested. |
| IQVIA | Pharma data analytics company | Provides district-level pharmaceutical intelligence. Not yet ingested. Required for Phase 2. |

---

## 33. Complete Mathematical Reference

### R1. Direction-Aware Normalization
```
POSITIVE:  R_ij = (X_ij - min_j) / (max_j - min_j) * 100
NEGATIVE:  R_ij = (max_j - X_ij) / (max_j - min_j) * 100
Zero-range: R_ij = 50.0  |  Missing: R_ij = 50.0
```
File: `src/scoring/normalizer.py::min_max_normalize()`

### R2. Shannon Entropy Weights
```
p_ij = (R_ij + 1e-6) / sum_i(R_ij + 1e-6)
e_j  = -(1/ln(148)) * sum_i(p_ij * ln(p_ij))
d_j  = max(1 - e_j, 1e-6)
w_j  = d_j / sum_j(d_j)       [sum = 1.0]
```
File: `src/scoring/entropy.py::calculate_entropy_weights()`

### R3. Pillar Sub-Score
```
S_ip = sum_{j in pillar p}(w_j * R_ij)
Single-indicator pillar: S_ip = R_ip, w_j = 1.0
```

### R4. AHP Principal Eigenvector
```
eigenvalues, eigenvectors = np.linalg.eig(A)
lambda_max = real(eigenvalues[argmax(real(eigenvalues))])
w = real(eigenvectors[:, max_idx])
w = w / sum(w)
CI = (lambda_max - n) / (n - 1)
CR = CI / RI_n     [RI_7 = 1.32]
```
File: `src/scoring/ahp.py::calculate_ahp_weights()`

### R5. Renormalized Driver Weights
```
w'_p = w_p / sum_{q != P5}(w_q)     for p != P5
sum_{p != P5}(w'_p) = 1.0
Values: P1=0.3664, P3=0.2468, P2=0.1618, P4=0.1039, P6=0.0606, P7=0.0606
```

### R6. Value Driver Score
```
V_i = sum_{p in {P1,P2,P3,P4,P6,P7}}(w'_p * S_ip)
```

### R7. Saturation Penalty
```
C_i = lambda * S_i,P5     [lambda = 0.15, range 0.10-0.20]
```

### R8. Final DLMAI Score
```
DLMAI_i = max(0, min(100, round(V_i - C_i, 4)))
```
File: `src/scoring/composite.py::compute_composite_scores()`

### R9. Geometric Alternative
```
comp_discount = max(1 - (lambda * S_i,P5 / 100), 0)
DLMAI_i_geo  = product_{p != P5}((S_ip + 1)^w'_p) * comp_discount
```

### R10. Quantile Tiering
```
p80 = df["dlmai_score"].quantile(0.80)
p50 = df["dlmai_score"].quantile(0.50)
p20 = df["dlmai_score"].quantile(0.20)
Tier 1: >= p80  |  Tier 2: p50-p80  |  Tier 3: p20-p50  |  Tier 4: < p20
```

### R11. Monte Carlo Perturbation
```
eps_p ~ N(0, sigma^2 = 0.04)    [sigma = 0.20]
w_p^(k) = w'_p * exp(eps_p)
w_p_norm^(k) = w_p^(k) / sum_q(w_q^(k))
rho_s^(k) = Spearman(Rank(DLMAI^baseline), Rank(DLMAI^(k)))
```
File: `src/sensitivity/monte_carlo.py::run_monte_carlo_sensitivity()`

### R12. Density Standardization
```
Density_ij = Raw_Count_ij / (Population_i / 100,000)
```
Applied to: PHCs, CHCs, sub-centres, Jan Aushadhi Kendras, pharma companies.

---

## 34. Learning Path

### Level 1 -- Pharmaceutical Market Context
What to learn: India pharma market structure, primary/secondary/tertiary care, prescribing behavior,
OTC vs. Rx, stockist-distributor network.
DLMAI connection: Why hospital density predicts Rx demand; why urban areas have higher per-capita consumption.
Start: `docs/South_India_DLMAI_Methodology.md` Section 1.

### Level 2 -- Government Data Sources
What to learn: NFHS-5, Census 2011, RHS, LGD master, Jan Aushadhi program, MCA21.
Files: `docs/South_India_DLMAI_Data_Dictionary.md`, `config/indicators.yaml`

### Level 3 -- Python Data Processing
What to learn: pandas, numpy, dict comprehensions, CSV/JSON I/O, dataclass.
Files: `src/pipeline.py`, `src/imputation/engine.py`

### Level 4 -- Statistics Fundamentals
What to learn: mean, variance, correlation (Pearson, Spearman), OLS regression, R-squared.
Files: `scripts/red_team_validation/test04_data_quality_bias.py`

### Level 5 -- Normalization Theory
What to learn: Min-Max, Z-Score, Robust IQR, Percentile Rank. When each is appropriate.
Files: `src/scoring/normalizer.py`, `test02_normalization_sensitivity.py`

### Level 6 -- Information Theory and Entropy
What to learn: Shannon entropy, information content, probability distributions, entropy in data discrimination.
Files: `src/scoring/entropy.py`, `docs/South_India_DLMAI_Methodology.md` Section 3.3

### Level 7 -- Analytic Hierarchy Process
What to learn: Saaty's pairwise comparison, 1-9 scale, eigenvector method, CI, CR.
Files: `src/scoring/ahp.py`, `ahp_pillar_weights.py`, `config/weights.yaml`

### Level 8 -- Composite Index Design (MCDA)
What to learn: Multi-Criteria Decision Analysis, TOPSIS, compensatory vs. non-compensatory aggregation.
Files: `docs/DLMAI_Framework_Architecture.md`, `docs/South_India_DLMAI_Methodology.md`

### Level 9 -- DLMAI Implementation
What to learn: How all components assemble. The 14-step pipeline. The formula. The scoring.
Files: `src/pipeline.py`, `src/scoring/composite.py`, `scoring_engine.py`

### Level 10 -- Statistical Validation
What to learn: Sensitivity analysis, robustness testing, ablation studies, red-teaming.
Files: `scripts/red_team_validation/test01` through `test08`.

### Level 11 -- Econometrics and External Validation
What to learn: OLS, R-squared, OOS cross-validation, LOSO, circularity, external validity.
Files: `test08_external_commercial_validation.py`, `docs/DLMAI_v2_Test08_Forensic_Commercial_Validation.md`

### Level 12 -- Model Governance
What to learn: Decision logs, methodology documentation, audit trails, model versioning.
Files: `docs/DLMAI_Model_Decision_Log.md`, `docs/DLMAI_v2_Seven_Test_Validation_Report.md`

### Level 13 -- Enterprise Production Architecture
What to learn: CI/CD, Docker, API layers, data versioning, monitoring, RBAC.
DLMAI status: Foundation present; production-grade infrastructure not yet implemented.

---

## 35. Important Truths About DLMAI

### What Is Genuinely Observed
- NFHS-5 indicators: extracted from published government PDF factsheets (where available)
- RHS facility counts: extracted from MoHFW published PDF tables
- NITI Aayog aspirational district designation: from official published list (hard-coded)
- LGD district codes: from the official LGD master

### What Is Derived (Computed from Raw)
- PHC/CHC/sub-centre densities per 100k: raw counts / population estimates
- MCA21 pharma density per 100k: company count / population
- Jan Aushadhi density per 100k: Kendra count / population

### What Is Inherited (Not Independently Observed)
Districts carved from parent districts since Census 2011 inherit parent indicator values.
Examples: Alluri Sitharama Raju, Ranipet, Tirupathur. These districts' DLMAI scores are
less individually reliable than districts with directly observed data.

### What Is Calibrated (Formula-Generated, Not Observed)
- Population figures for most districts: calibrated anchors for named cities; formula-based for others
- `census_population_age_0_6_pct`: **constant 10.2% across ALL 148 districts**
- `census_decadal_growth_pct`: **constant 12.4% across ALL 148 districts**
- `census_literacy_rate_pct`: state-level constant (Kerala=94%, Tamil Nadu=82%, others=76%)
- Jan Aushadhi counts for unnamed districts: `max(pop_lakhs * 1.8, 6)` formula
- MCA21 counts for unnamed districts: `max(pop_lakhs * 0.4, 1)` formula
- All Test 8 commercial outcome benchmarks: synthetic top-down allocation

### What Is Currently Validated (Verified)
- Mathematical reproducibility: independent recomputation matches exactly (max error 1e-4, 0 rank diffs)
- AHP consistency: CR = 0.015349 < 0.10
- Normalization robustness: Robust IQR produces identical rankings (rho=1.0000)
- Data quality independence: no positive completeness bias (r = -0.082, p = 0.322)
- Monte Carlo stability: mean rho = 0.9922 over N=1,000 iterations
- P5 independence: removing P5 produces rho = 0.9804 correlated ranking
- Geographic integrity: exactly 148 districts, 7 states, zero duplicate LGD codes

### What Is NOT Externally Validated
DLMAI has NOT been validated against independently observed district-level pharmaceutical
commercial outcomes. Test 8 classified as Class D: Calibrated/Synthetic Benchmark.
The project cannot claim to be an "empirically validated pharmaceutical sales predictor."

---

*README generated by forensic analysis of DLMAI v2.0.0 repository.*
*All claims verified against source code, configuration, and generated output artifacts.*
*Document version: 1.0.0 | Based on pytest suite status: 24/24 PASSING*
*Repository: e:/DMLIA-Sun pharma/dlmai_complete*
