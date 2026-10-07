# DLMAI South India Refactor: Comprehensive Architecture & Data Audit Report

**Document Version:** 1.0.0  
**Target Geography:** South India (Tamil Nadu, Kerala, Karnataka, Andhra Pradesh, Telangana, Goa, Puducherry)  
**Total Canonical Districts in Scope:** **148 Districts** across 7 States/UTs  
**Authoritative Reference:** Local Government Directory (LGD), Ministry of Panchayati Raj, Government of India  

---

## Executive Summary

This audit report establishes the architectural, empirical, and statistical foundation for refactoring the **District-Level Market Attractiveness Index (DLMAI)** from a pan-India prototype to a dedicated **South India Pharmaceutical Market Intelligence Model**.

Rather than filtering a national 785-district output, this refactor redesigns the entire pipeline from ground up. South India becomes the primary geographic and analytical scope, accounting for unique regional healthcare dynamics, distinct state healthcare schemes, dense private/public provider ecosystems, and recent administrative boundary reorganizations (e.g., 2014 Telangana bifurcation, 2022 Andhra Pradesh district restructuring).

---

## A. Existing Architecture Analysis

The existing codebase implements a 5-layer pipeline:

| Module | Architectural Layer | Primary Responsibility | Audit Evaluation & Status |
|---|---|---|---|
| `district_crosswalk.py` | Layer 2 — Harmonization | Maps incoming text/alias variations to canonical LGD codes. Implements `InheritanceResolver` for parent-child lineage. | **High Quality Core:** Regex normalization, fuzzy matching with state-hints, ambiguity detection, and fixed-point inheritance are mathematically sound. Needs configuration-driven South India LGD master. |
| `nfhs_factsheet_parser.py` | Layer 1 — Ingestion (P1, P2) | Extracts 13 health, nutrition, and amenity indicators from NFHS-5 factsheet PDFs. | **Critical Bug Identified:** `_extract_trailing_number` extracted footnotes (`clean_fuel_pct=3.0`, `drinking_water_pct=1.0`) and NFHS-4 historical numbers instead of NFHS-5 values. Must be rewritten with unit-anchor regex `r'\(\s*%\s*\)\s*([0-9,.]+)'`. |
| `rhs_parser.py` | Layer 1 — Ingestion (P3) | Extracts Sub Centres, PHCs, CHCs, Sub-Divisional Hospitals, and District Hospitals from MoHFW RHS table PDF. | **Critical Bug Identified:** Parser assumed 6 columns where `raw_row[0]` was State and `raw_row[1]` was District. Real PDF has 8 columns (Col 0=S.No, Col 1=State, Col 2=District). Parsed only 34 rows nationally instead of 620 rows. Fixed layout yields all 148 South Indian districts. |
| `jan_aushadhi_ingestion.py` | Layer 1 — Ingestion (P4) | Parses Pradhan Mantri Jan Aushadhi Kendra export tables. | **Sound Structure:** Needs deduplication by Kendra Code, address-to-district normalization, and per-100k population density normalization. |
| `mca21_ingestion.py` | Layer 1 — Ingestion (P5) | Filters active pharma corporations by NIC-2008 codes (21001, 21002, 21009) and maps via PIN-to-district lookup. | **Sound Structure:** Requires real South Indian pincode-to-LGD mapping table and saturation dampening parameter. |
| `niti_aspirational_districts.py` | Layer 1 — Ingestion (P6) | Exhaustive 112 Aspirational Districts list from NITI Aayog. | **Fully Functional:** Verified exact official list. Binary indicator scored as policy tailwind. |
| `census_handbook_parser.py` | Layer 1 — Ingestion (P1, P7) | Extracts population growth, literacy, urbanization, age demographics from Census tables. | **Sound Structure:** Needs clear temporal separation between 2011 Census baseline and 2019-21 NFHS-5. |
| `imputation_engine.py` | Layer 3 — Imputation | Implements 4-tier fallback: Trend $\to$ State Mean $\to$ kNN Covariate $\to$ Unresolved null. | **Sound Structure:** Produces confidence mask (`native`, `state_mean`, `nearest_neighbor`, `still_missing`). Needs South-India-specific peer covariate matching. |
| `ahp_pillar_weights.py` | Layer 4 — Weighting | Computes pillar weights via Saaty AHP pairwise comparison matrix. Checks Consistency Ratio ($CR < 0.10$). | **Sound Structure:** Verified consistency ($CR = 0.023 < 0.10$). Explicit starting template for pharma BD / market access panels. |
| `scoring_engine.py` | Layer 4 — Scoring | Direction-aware Min-Max scaling, intra-pillar Entropy weighting, inter-pillar AHP weighting, geometric aggregation, and Pillar 5 saturation dampening. | **Sound Structure:** Needs configuration externalization into `config/weights.yaml` and quantile/natural breaks tiering. |
| `sensitivity_analysis.py` | Layer 5 — Validation | Monte Carlo weight perturbation ($\pm 20\%$) with Spearman rank correlation and confidence intervals. | **Sound Structure:** Rigorous validation of ranking stability and identification of volatile districts. |
| `run_pipeline.py` & `build_index.py` | Orchestration | Wires Layers 1 to 5 into unified execution and generates outputs. | **Requires Refactoring:** Needs configuration decoupling, structured logging, and automated execution for South India. |
| `dashboard_app.py` | Presentation | Interactive Streamlit UI dashboard for exploring scores, breakdowns, and rankings. | **Requires Refactoring:** Update to focus on South India regional analysis, state-by-state comparison, explainability cards, and choropleth maps. |

---

## B. Current Data Flow vs. Target Refactored Flow

### Current Architecture
```
[Raw PDFs / CSVs] ──► [Parsers (Hardcoded)] ──► [sample_lgd_seed.csv (22 districts)] ──► [Imputation] ──► [Scoring] ──► [National Output]
```

### Target South India Architecture
```
┌────────────────────────────────────────────────────────┐
│                   config/geography.yaml                │
│    (Target States, LGD Codes, Aliases, Lineages)       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             data/master/lgd_south_india.csv            │
│  (Authoritative 148 Districts across 7 States/UTs)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│            Layer 1: Robust Source Ingestion            │
│  - NFHS-5 District Facts (124 real PDFs parsed)        │
│  - RHS Health Infrastructure (620 districts parsed)    │
│  - Jan Aushadhi Kendra Density                         │
│  - MCA21 Active Pharma Enterprises                     │
│  - NITI Aayog Aspirational Districts (112 list)        │
│  - Census Demographic Baselines                        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│        Layer 2: Canonical District Harmonization       │
│  - LGD Code Resolution (Exact, Alias, Historical)      │
│  - Multi-generation Parent-Child Lineage Inheritance   │
│  - Audit Matrix: outputs/district_coverage_matrix.csv  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│        Layer 3: Auditable Imputation Hierarchy         │
│  - Trend -> South India State Mean -> kNN Matching     │
│  - Traceable Confidence Mask (outputs/imputation_audit)│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Layer 4: Mathematical Scoring              │
│  - Directional Min-Max Normalization                   │
│  - Intra-Pillar Entropy Weights                        │
│  - Inter-Pillar AHP Weights (Validated CR < 0.10)      │
│  - Value Driver Aggregation - Saturation Dampener      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│        Layer 5: Monte Carlo Sensitivity Analysis       │
│  - ±20% Log-Normal Pillar Weight Perturbation          │
│  - Spearman Rank Stability & Rank Volatility Bounds    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Outputs & Interactive Dashboard            │
│  - outputs/dlmai_south_india_scores.csv                │
│  - outputs/district_coverage_matrix.csv                │
│  - outputs/data_quality_report.csv                     │
│  - dashboard/dashboard_app.py (Streamlit UI)           │
└────────────────────────────────────────────────────────┘
```

---

## C. Reusable Components

The following components possess strong mathematical and architectural foundations and are retained with appropriate modularization:
1. **LGD Crosswalk Matcher (`district_crosswalk.py`)**: String normalization, fuzzy scoring with SequenceMatcher, ambiguity bounds, and state-hint filtering.
2. **Fixed-Point Inheritance Engine (`InheritanceResolver`)**: Multi-generation resolution of newly carved districts from parent districts.
3. **Saaty AHP Engine (`ahp_pillar_weights.py`)**: Normalized pairwise comparison matrix, principal eigenvector computation, and Consistency Ratio validation against Saaty Random Index ($RI$).
4. **Intra-Pillar Shannon Entropy Weighting (`scoring_engine.py`)**: Objective weighting based on information dispersion.
5. **Monte Carlo Sensitivity Engine (`sensitivity_analysis.py`)**: Perturbation sampling, Spearman $\rho$ correlation, and empirical confidence intervals.

---

## D. Components Requiring Modification & Bug Rectification

1. **`nfhs_factsheet_parser.py` (Critical Bug Fix)**:
   - *Problem:* Footnotes like `cooking3 (%)` and trailing historical NFHS-4 column numbers corrupted `clean_fuel_pct`, `drinking_water_pct`, and `hypertension_pct`.
   - *Resolution:* Implemented unit-anchored regex matching `r'\(\s*(?:%|Rs\.|females[^\)]*)\s*\)\s*([0-9,.]+|\*|na)'` that isolates the NFHS-5 column cleanly.
2. **`rhs_parser.py` (Critical Bug Fix)**:
   - *Problem:* Previous implementation assumed 6 columns with state in column 0. The true MoHFW PDF has 8 columns: S.No (Col 0), State (Col 1), District (Col 2), Sub Centres (Col 3), PHCs (Col 4), CHCs (Col 5), SDH (Col 6), DH (Col 7).
   - *Resolution:* Updated column offset extractor, prefix stripper (e.g. `'b 36' -> 36.0`), and state-continuation tracker.
3. **`mca21_ingestion.py`**:
   - *Improvement:* Enhanced postal code prefix resolution to map South Indian PIN ranges (PIN 50xxxx-69xxxx) to canonical LGD codes.
4. **`scoring_engine.py`**:
   - *Improvement:* Decoupled weights and dampener into YAML configuration, added population-normalized feature calculations, and enabled dual arithmetic/geometric aggregation comparison.

---

## E. Data Source Audit Profile

| Data Source | Format & Files Found | Pages / Rows | Geographic Level | Reference Period | Quality & Integrity Assessment |
|---|---|---|---|---|---|
| **NFHS-5 District Factsheets** | 124 PDFs across 6 State folders | 4–6 pages per PDF | District | 2019–2021 | **High Quality:** Real IIPS survey data. Covers 124 South Indian districts natively. High statistical validity. |
| **NFHS-5 State Factsheets** | 7 PDFs (AP, GA, KA, KL, PY, TN, TS) | 6–8 pages per PDF | State | 2019–2021 | **High Quality:** Authoritative state benchmarks used for state-mean reference and audit. |
| **Rural Health Statistics (RHS)** | 1 PDF (`district-wise-health-centres.pdf`) | 13 Pages | District (Rural) | March 2011 | **Comprehensive:** 620 districts nationally. Covers all South Indian districts under pre-split boundaries. Inherited for new districts. |
| **Jan Aushadhi Kendras** | Tabular export / registry records | Multi-record | Kendra / District | 2023–2024 | **High Relevance:** Real retail accessibility metric. Requires deduplication by Kendra Code and population density scaling. |
| **MCA21 Corporate Master** | Corporate registry CSV | Multi-record | Pincode / District | 2021–2024 | **Moderate Quality:** Direct proxy of corporate presence. Saturation dampener applied to prevent penalty of white-space opportunities. |
| **NITI Aayog Aspirational** | Published reference list | 112 National Districts | District | Current | **Exhaustive:** 100% complete national list. Unambiguous binary indicator. |
| **SECC Socioeconomic Census** | 1 CSV (`Socio Economic and Caste Census.csv`) | 35 Rows | **STATE Level Only** | 2011–2012 | **Methodological Constraint:** Dataset is state-level. Must NOT be falsely presented as district-level observations; tracked as `granularity=STATE`. |

---

## F. South India Geographic Coverage & Canonical LGD Master

Querying the authoritative national LGD master (`data/master/lgd_master.csv`) for the 7 target South Indian states yields exactly **148 Districts**:

| State / Union Territory | State LGD Code | Total Canonical Districts | NFHS-5 District PDFs Available | RHS 2011 Coverage | Aspirational Districts |
|---|:---:|:---:|:---:|:---:|:---:|
| **Tamil Nadu** | 33 | 38 | 32 (Pre-2019 splits) | 30 (Pre-2011 splits) | 1 (Ramanathapuram) |
| **Kerala** | 32 | 14 | 14 (100% native) | 14 (100% native) | 1 (Wayanad) |
| **Karnataka** | 29 | 31 | 30 (Pre-Vijayanagara) | 30 (Pre-Vijayanagara) | 2 (Raichur, Yadgir) |
| **Andhra Pradesh** | 28 | 26 | 13 (Pre-2022 26-district split) | 13 (Pre-2014/2022 split) | 3 (YSR Kadapa, Visakhapatnam, Vizianagaram) |
| **Telangana** | 36 | 33 | 31 (Post-2016 31-district split) | 10 (Pre-2014 10-district split) | 3 (Asifabad, Bhupalpally, Bhadradri) |
| **Goa** | 30 | 2 | 2 (North & South Goa) | 2 (100% native) | 0 |
| **Puducherry (UT)** | 34 | 4 | 4 (Puducherry, Karaikal, Mahe, Yanam) | 4 (100% native) | 0 |
| **TOTAL SOUTH INDIA** | — | **148** | **126 Native Files** | **103 Pre-split Baselines** | **10 Districts** |

*Note on Lineage Inheritance:* Newly created districts (e.g. 13 new AP districts created in April 2022, Vijayanagara in Karnataka created in 2021, and Mayiladuthurai / Chengalpattu in Tamil Nadu) are cleanly resolved to their parent districts via `district_crosswalk_south.csv` and flagged with `inherited_from_<parent_code>`.

---

## G. Proposed Indicator Framework

| Pillar | Indicator ID | Indicator Name | Source | Unit | Direction | Pharmacological & Market Rationale |
|---|---|---|---|:---:|:---:|---|
| **P1: Demand & Disease Burden** | `nfhs_hypertension_combined` | Adult Hypertension Prevalence | NFHS-5 | % | **POSITIVE** | High prevalence driving chronic CV therapy demand (ACEi, ARBs, Statins). |
| | `nfhs_diabetes_combined` | Adult Diabetes Prevalence | NFHS-5 | % | **POSITIVE** | Direct proxy for antidiabetic prescription volume (Metformin, SGLT2i, Insulin). |
| | `nfhs_stunting_pct` | Child Stunting Rate | NFHS-5 | % | **POSITIVE** | Pediatric therapy demand, nutritional deficiency, and antibiotic market need. |
| | `nfhs_underweight_pct` | Child Underweight Rate | NFHS-5 | % | **POSITIVE** | Baseline malnutrition and infectious disease vulnerability indicator. |
| | `census_urban_pop_pct` | Urbanization Rate | Census | % | **POSITIVE** | Correlates with lifestyle disease prevalence and organized retail pharmacy reach. |
| **P2: Economic Access** | `nfhs_insurance_pct` | Health Insurance Coverage | NFHS-5 | % | **POSITIVE** | Reduces out-of-pocket barrier to acute/specialty therapies; higher scheme claims. |
| | `nfhs_clean_fuel_pct` | Household Clean Fuel Usage | NFHS-5 | % | **POSITIVE** | Robust proxy for household disposable income and economic tier. |
| | `nfhs_sanitation_pct` | Improved Sanitation Facility | NFHS-5 | % | **POSITIVE** | Household living standard and basic infrastructure indicator. |
| | `nfhs_oope_delivery_rs` | Out-of-Pocket Delivery Cost | NFHS-5 | INR | **NEGATIVE** | High catastrophic healthcare expenditure indicates household financial distress. |
| **P3: Healthcare Infrastructure** | `rhs_phc_density_per_100k` | PHCs per 100k Population | RHS | Rate | **POSITIVE** | Primary care touchpoints and primary prescription distribution capacity. |
| | `rhs_chc_density_per_100k` | CHCs per 100k Population | RHS | Rate | **POSITIVE** | Secondary referral centres with in-patient pharmacy dispensaries. |
| | `rhs_hospital_presence` | Sub-Div & District Hospitals | RHS | Count | **POSITIVE** | Tertiary care and specialist physician concentration for high-value therapies. |
| **P4: Distribution & Retail** | `jan_aushadhi_density_per_100k` | Jan Aushadhi Kendras / 100k | PMBJP | Rate | **POSITIVE** | Penetration of formal retail pharmacy access points across the district. |
| **P5: Industry Presence (Dampener)** | `mca21_pharma_density_per_100k` | Active Pharma Enterprises / 100k | MCA21 | Rate | **NEGATIVE** | High local manufacturing/marketing density creates competition & price erosion. |
| **P6: Regulatory & Schemes** | `niti_aspirational_flag` | Aspirational District Status | NITI | 0 / 1 | **POSITIVE** | Priority government health grants, PMJAY empanelment drives, and CSR funding. |
| **P7: Growth Momentum** | `census_decadal_growth` | Population Decadal Growth | Census | % | **POSITIVE** | Expanding demographic base and long-term pharmaceutical volume expansion. |
| | `census_literacy_rate` | District Literacy Rate | Census | % | **POSITIVE** | Health literacy, compliance with treatment regimens, and self-care adoption. |

---

## H. Methodological Risk Matrix & Mitigation

| Risk Area | Risk Description | Methodological Mitigation |
|---|---|---|
| **1. Temporal Mismatch** | Census is 2011, NFHS-5 is 2019-21, RHS is 2011/current, MCA21 is 2024. | Maintain `temporal_metadata` layer. Calculate population projections where rates are computed; document compatibility bands (`HIGH`, `MEDIUM`, `LOW`). |
| **2. Boundary Reorganization** | AP created 13 new districts in 2022; Telangana created 21 new districts in 2016. | Fixed-point `InheritanceResolver` tracks exact parent LGD codes. No child district is left as a silent null; all inherited cells carry lineage provenance. |
| **3. Population Confounding** | Raw facility counts favor megacities over well-served smaller districts. | Compute per-100k population rates for infrastructure and distribution indicators, preserving raw counts as descriptive metadata. |
| **4. Public-Sector RHS Skew** | RHS covers rural government centres; metro districts (e.g. Chennai, Bangalore Urban) have low RHS counts. | Impute metro healthcare capacity using urban amenities, hospital counts, and nearest-neighbor urban peer matching. |
| **5. Market Saturation Ambiguity** | High company presence can mean either vibrant ecosystem or heavy competition. | Formalized Pillar 5 as a configurable Value Dampener ($W_5 = 0.15$) subtracted from positive value drivers. |
| **6. Rank Sensitivity** | AHP weights and normalization choices could alter district ranks. | Monte Carlo sensitivity engine perturbing weights by $\pm 20\%$ across 1,000 iterations to provide rank stability confidence bands. |

---

## I. Refactoring & File Placement Plan

```
dlmai_complete/
├── config/
│   ├── geography.yaml            # Target 7 States, LGD codes, state codes, alias tables
│   ├── indicators.yaml           # Metadata, directions, units, sources, formulas
│   ├── pillars.yaml              # 7-Pillar structure, descriptions, indicator bindings
│   └── weights.yaml              # Validated AHP weights, dampener coefficients, tier cutoffs
│
├── data/
│   ├── master/
│   │   ├── lgd_south_india.csv              # Exact 148 South Indian canonical districts
│   │   └── district_crosswalk_south.csv     # Historical lineage, aliases, and parent mapping
│   ├── raw/ (Immutable source archives)
│   ├── interim/ (Parsed intermediate extracts)
│   └── processed/ (Harmonized analytical matrix)
│
├── src/
│   ├── ingestion/
│   │   ├── nfhs_parser.py        # Corrected unit-anchored NFHS parser
│   │   ├── rhs_parser.py         # Corrected 8-column RHS parser
│   │   ├── jan_aushadhi.py       # Deduplicated Kendra aggregator
│   │   ├── mca21.py              # Pincode-mapped pharma enterprise density
│   │   └── niti_aayog.py         # Official Aspirational District flagger
│   ├── harmonization/
│   │   ├── crosswalk.py          # LGD crosswalk & multi-tier alias matcher
│   │   └── inheritance.py        # Recursive parent-child inheritance engine
│   ├── imputation/
│   │   └── engine.py             # Hierarchical imputation with audit masks
│   ├── scoring/
│   │   ├── normalizer.py         # Directional Min-Max & Robust scalers
│   │   ├── entropy.py            # Intra-pillar Shannon entropy weighting
│   │   ├── ahp.py                # Inter-pillar Saaty AHP consistency validator
│   │   └── composite.py          # Value Driver - Dampener aggregation & tiering
│   ├── sensitivity/
│   │   └── monte_carlo.py        # Weight perturbation & Spearman rank stability
│   └── utils/
│       └── logging.py            # Structured pipeline logging
│
├── docs/
│   ├── South_India_DLMAI_Data_Dictionary.md  # Deliverable 2
│   └── South_India_DLMAI_Methodology.md      # Deliverable 3
│
├── dashboard/
│   └── dashboard_app.py          # South India Streamlit intelligence portal
│
├── outputs/
│   ├── dlmai_south_india_scores.csv          # Final scores, rankings, tiers
│   ├── dlmai_south_india_combined_output.csv # Full indicator matrix + confidence mask
│   ├── district_coverage_matrix.csv          # Coverage matrix across all 148 districts
│   ├── data_quality_report.csv               # Data quality scores and completeness
│   ├── sensitivity_results.csv               # Monte Carlo rank stability metrics
│   └── refresh_metadata.json                 # Execution provenance & statistics
│
└── tests/
    └── test_south_india_pipeline.py          # End-to-end test suite
```

---
*Audit Report Complete. Deliverables 2 (`South_India_DLMAI_Data_Dictionary.md`) and 3 (`South_India_DLMAI_Methodology.md`) are documented in the `docs/` folder.*
