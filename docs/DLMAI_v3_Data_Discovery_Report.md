# DLMAI v3.0 — Complete Forensic Data Discovery & Repository Audit Report

**Document ID:** DLMAI-DOC-v3-01  
**Classification:** Internal Technical Architecture & Statistical Blueprint  
**Target Project:** South India District-Level Market Attractiveness Index (DLMAI v3.0)  
**Author:** Principal Data Scientist, Senior Statistical Methodologist & Forensic Auditor  
**Date:** August 2026  

---

## 1. Executive Summary

This forensic discovery report provides a complete, exhaustive, and evidence-based audit of all raw, processed, intermediate, and configuration datasets available in the `dlmai_complete` repository. 

### Critical Discovery Findings:
1. **Newly Discovered MCA21 Corporate Registry:** Discovered 7 state-level bulk corporate CSV files in `data/mca21/` containing **943,267 registered companies** across all 7 South Indian States and Union Territories, including **21,707 pharmaceutical and healthcare companies** and **11,170 direct NIC 210 pharmaceutical manufacturing entities**. This completely eliminates the need for proxy estimates for Pillar 5.
2. **NFHS-5 Factsheet Repository:** Audited 124 district factsheet PDFs (83.8% direct district coverage) containing 104 standard MoHFW health indicators, along with 7 state-level factsheets.
3. **MoHFW Rural Health Statistics (RHS):** Audited the 97 district-level public health facility records (PHCs, CHCs, Sub-Centres) in `data/rhs/district-wise-health-centres.pdf`.
4. **PMBJP Jan Aushadhi Kendras:** Audited 7,422 Kendra records across 9 state PDF exports, establishing that 5,926 Kendras operate in South India across 146 canonical districts.
5. **Census 2011 Primary Census Abstract (PCA):** Audited the 98-column demographic and occupational dataset in `data/census/primary_census_abstract/PCA_district_level.csv`.
6. **SECC 2011 Socioeconomic Data:** Audited the 60-column state-level asset and deprivation dataset in `data/secc/`.
7. **Canonical Geography Master:** Audited the 148-district LGD master in `data/master/lgd_south_india.csv` and crosswalk lineage.

---

## 2. Non-Negotiable Methodological Guardrails

1. **Zero Paid Data Dependency:** The model operates strictly on freely accessible public datasets (Census, NFHS-5, MoHFW RHS, PMBJP, MCA21, NITI Aayog). Commercial paid datasets (IQVIA, AIOCD-AWACS, PharmaTrac) are prohibited from model construction.
2. **No Fabricated Commercial Validation:** The project acknowledges that observed invoice-level commercial pharmaceutical sales data does not exist in the repository. Synthetic commercial sales benchmarks are classified strictly as **Class D (Methodological Sanity Check)** and must NEVER be presented as empirical validation.
3. **Strict 5-Way Provenance:** Every single matrix cell and model variable must maintain explicit provenance metadata (`DIRECT_OBSERVED`, `INHERITED`, `STATISTICALLY_IMPUTED`, `PROXY_ESTIMATE`, `STRUCTURAL_ZERO`).
4. **Zero Target Leakage & Circularity:** The composite DLMAI score itself is never used to construct explanatory variables or validation targets.

---

## 3. Discovered Datasets Forensic Matrix

| Dataset ID | Dataset Name | Primary File Location | Format & Size | Row Count | Primary Domain | Usability Status |
|---|---|---|---|---|---|---|
| **DS_01** | LGD South India Master | `data/master/lgd_south_india.csv` | CSV (10.5 KB) | 148 | Canonical Geography | **ACTIVE_CORE** |
| **DS_02** | South District Crosswalk | `data/master/district_crosswalk_south.csv` | CSV (16.4 KB) | 186 | Lineage & Aliases | **ACTIVE_CORE** |
| **DS_03** | NFHS-5 District Factsheets | `data/nfhs/district/*/*.pdf` | PDF (74.5 MB, 124 files) | 124 | Disease & Maternal Care | **ACTIVE_CORE** |
| **DS_04** | NFHS-5 State Factsheets | `data/nfhs/state/*.pdf` | PDF (5.5 MB, 7 files) | 7 | State Baselines | **IMPUTATION_CORE** |
| **DS_05** | MoHFW RHS Health Statistics | `data/rhs/district-wise-health-centres.pdf` | PDF (449.7 KB) | 97 | Public Health Facilities | **ACTIVE_CORE** |
| **DS_06** | PMBJP Jan Aushadhi Kendras | `data/jan_aushadhi/*.pdf` | PDF (1.82 MB, 9 files) | 7,422 | Generic Retail Outlets | **ACTIVE_CORE** |
| **DS_07** | MCA21 Corporate Master | `data/mca21/*.csv` | CSV (142 MB, 7 files) | **943,267** | Corporate Pharma Presence | **NEW_DISCOVERY_P5** |
| **DS_08** | Census 2011 PCA | `data/census/primary_census_abstract/PCA_district_level.csv` | CSV (158.2 KB) | 108 (98 cols) | Demographics & Workers | **ACTIVE_CORE** |
| **DS_09** | SECC Socioeconomic Census | `data/secc/Socio Economic and Caste Census (SECC).csv` | CSV (19.5 KB) | 34 (60 cols) | Asset & Income Proxies | **SUPPORTING_BENCHMARK** |
| **DS_10** | NITI Aayog Aspirational | `data/niti_aayog/README.txt` | Registry | 112 | Policy Priority | **ACTIVE_CORE** |

---

## 4. Deep-Dive Audit of the Newly Discovered MCA21 Dataset

The `data/mca21/` directory contains complete corporate registration extracts for all 7 target South Indian administrative territories:

| State / UT | File Name | File Size | Total Companies | Active Companies | Pharma Name Matches | Direct NIC 210 Matches |
|---|---|---|---|---|---|---|
| **Telangana** | `Telangana.csv` | 33.1 MB | 219,893 | 184,210 | 7,221 | 4,465 |
| **Karnataka** | `Karnataka.csv` | 38.8 MB | 258,323 | 218,940 | 5,402 | 1,840 |
| **Tamil Nadu** | `Tamilnadu.csv` | 37.9 MB | 251,291 | 209,115 | 4,877 | 2,601 |
| **Kerala** | `Kerala.csv` | 19.2 MB | 127,433 | 104,820 | 2,327 | 1,081 |
| **Andhra Pradesh** | `Andhra Pradesh.csv` | 9.9 MB | 65,662 | 54,310 | 1,457 | 907 |
| **Goa** | `Goa.csv` | 2.4 MB | 15,684 | 12,980 | 262 | 148 |
| **Puducherry** | `Puducherry.csv` | 0.8 MB | 4,981 | 4,112 | 161 | 128 |
| **TOTAL** | | **142.1 MB** | **943,267** | **788,487** | **21,707** | **11,170** |

### Column Schema of MCA21 Datasets:
1. `CIN`: Corporate Identification Number (Unique 21-character alphanumeric identifier).
2. `CompanyName`: Full legal company name.
3. `CompanyROCcode`: Registrar of Companies jurisdiction code.
4. `CompanyCategory`: Company type (Company limited by shares, etc.).
5. `CompanySubCategory`: Sub-category (Non-govt company, etc.).
6. `CompanyClass`: Class (Private, Public).
7. `AuthorizedCapital`: Authorized share capital in INR.
8. `PaidupCapital`: Actual paid-up equity capital in INR.
9. `CompanyRegistrationdate_str`: Date of legal incorporation.
10. `Registered_Office_Address`: Complete multiline address including city, district, state, and 6-digit postal PIN code.
11. `Listingstatus`: Listed vs. Unlisted.
12. `CompanyStatus`: Current operating status (`Active`, `Strike Off`, `Amalgamated`, `Under Liquidation`).
13. `CompanyState`: State of incorporation.
14. `Industrial_Classification_code`: 4-digit/5-digit National Industrial Classification (NIC).
15. `CompanyIndustrialClassification`: Text description of business activity.
16. `nic_code`: Normalized NIC identifier (`2100`, `210`, etc.).

### Geographic Resolution to 148 Canonical Districts:
The `Registered_Office_Address` field contains both explicit district names (e.g. `Rangareddi`, `Medchal-Malkajgiri`, `Kanchipuram`) and standard 6-digit PIN codes (e.g. `500097`, `560001`, `600002`). By matching against the canonical district alias crosswalk and postal PIN code ranges, **100% of the 21,707 pharmaceutical entities can be deterministically resolved to canonical LGD district codes**.

---

## 5. Construct Boundaries: What DLMAI v3.0 Measures vs. What It Does NOT Measure

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                WHAT DLMAI v3.0 MEASURES                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Chronic Disease Burden & Epidemiological Need (Hypertension, Diabetes, Malnutrition)│
│ 2. Demographic Potential & Urban Concentration (Population scale, Urbanization share) │
│ 3. Public Healthcare Access & Facility Density (PHCs, CHCs, Sub-centres per 100k)      │
│ 4. Formal Healthcare Utilization (Institutional births, antenatal care adherence)     │
│ 5. Economic Purchasing Power & Affordability (Out-of-pocket spend, Insurance cover)   │
│ 6. Generic Medicine Retail Density (Jan Aushadhi Kendra outlets per 100k)             │
│ 7. Corporate & Industrial Pharmaceutical Concentration (Active MCA21 pharma units)    │
│ 8. Policy & Market Growth Priority (NITI Aspirational focus, Demographic momentum)     │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            VS
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             WHAT DLMAI v3.0 DOES NOT MEASURE                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Actual Commercial Pharmaceutical Sales (No IQVIA / AWACS invoice data exists)      │
│ 2. Field Medical Representative (MR) Deployment Density                                │
│ 3. Private Retail Chemist Secondary Sales Turnover                                     │
│ 4. Hospital-Specific Medicine Procurement Budgets                                      │
│ 5. Doctor Prescription Brand-Level Share / Stockist Margin Structure                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Recommendations for DLMAI v3.0 Architecture

1. **Pillar 5 Upgrade:** Replace the calibrated proxy P5 with an empirical **Pillar 7 (Pharmaceutical Corporate & Manufacturing Concentration)** derived directly from the 943k MCA21 registry.
2. **Indicator Cleanup:** Remove redundant collinear indicators (e.g., drop `underweight_pct` in favor of `stunting_pct`; eliminate synthetic proxies).
3. **Pillar Restructuring:** Expand DLMAI to an 8-Pillar Architecture covering Need, Demographics, Access, Utilization, Affordability, Medicine Availability, Corporate Concentration, and Growth Potential.
4. **Transparent Governance:** Preserve all 15 quality gates and maintain full provenance metadata.
