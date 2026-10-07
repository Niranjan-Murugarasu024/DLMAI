# DLMAI v3.0 — Comprehensive Data Provenance & Lineage Architecture Report

**Document ID:** DLMAI-DOC-v3-03  
**Classification:** Enterprise Data Governance & Lineage Architecture  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Provenance Architecture Overview

To eliminate silent data fabrication, unacknowledged imputations, and pseudo-observations, DLMAI v3.0 establishes a strict **5-Tier Data Provenance Taxonomy** applied at both the dataset level and individual matrix cell level across all 148 canonical districts $\times$ model variables.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              5-TIER PROVENANCE TAXONOMY                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. DIRECT_OBSERVED   : Value is directly extracted from an authentic source document   │
│ 2. INHERITED         : Value is inherited from parent district via documented lineage  │
│ 3. STATISTICALLY_IMP : Value is imputed via hierarchical state-mean or kNN regression │
│ 4. PROXY_ESTIMATE    : Value is estimated via an indirect proxy construct              │
│ 5. STRUCTURAL_ZERO   : Zero represents a genuine absence (e.g. 0 companies in district)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Enterprise Data Lineage

Every single indicator flowing into the DLMAI composite score follows an unbroken, deterministic, and auditable pipeline:

```
[RAW SOURCE DATASETS]
  ├── NFHS-5 Factsheets (124 District PDFs, 7 State PDFs)
  ├── MoHFW RHS Table (97 Health Facility Records)
  ├── MCA21 Corporate Master (943,267 Company Records)
  ├── PMBJP Registry (5,926 South India Kendras)
  └── Census 2011 PCA (Demographics & Urban Shares)
               │
               ▼
[STEP 1: INGESTION & HARMONIZATION]
  ├── PDF / Table / CSV parsing
  ├── Extraction of raw counts and prevalence rates
  └── Resolution to Canonical LGD Code via SouthDistrictCrosswalk
               │
               ▼
[STEP 2: FIXED-POINT LINEAGE INHERITANCE]
  ├── Newly bifurcated child districts identify parent LGD code
  └── Parent epidemiological profile propagated to child districts
               │
               ▼
[STEP 3: HIERARCHICAL STATISTICAL IMPUTATION]
  ├── Remaining missing cells imputed via State-Mean or Population kNN
  └── Provenance status stamped as IMPUTED_STATE_MEAN / IMPUTED_KNN
               │
               ▼
[STEP 4: DIRECTION-AWARE NORMALIZATION]
  ├── Positive indicators: (x - min) / (max - min) * 100
  └── Negative/Cost indicators: (max - x) / (max - min) * 100
               │
               ▼
[STEP 5: INTRA-PILLAR SHANNON ENTROPY WEIGHTING]
  ├── Probability distribution: p_ij = (x_ij + eps) / sum(x_ij + eps)
  ├── Entropy: e_j = -k * sum(p_ij * ln(p_ij))
  └── Objective weights: w_j = (1 - e_j) / sum(1 - e_j)
               │
               ▼
[STEP 6: INTER-PILLAR SAATY AHP PRIORITIZATION]
  ├── Pairwise comparison matrix A (validated consistency CR < 0.10)
  └── Principal eigenvector: A * w = lambda_max * w
               │
               ▼
[STEP 7: COMPOSITE SCORING & MONTE CARLO UNCERTAINTY]
  ├── Value Drivers aggregation: V_i = sum(W_p * Pillar_p)
  ├── Saturation penalty: C_i = lambda * Pillar_Corporate
  ├── Final DLMAI = V_i - C_i
  └── 1,000 Monte Carlo stochastic weight perturbations
```

---

## 3. Cell-Level Provenance Breakdown Across Matrix

| Indicator | Direct Observed Cells | Inherited Cells | Imputed Cells | Provenance Confidence |
|---|---|---|---|---|
| `nfhs_hypertension_combined_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_diabetes_combined_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_stunting_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_wasting_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_clean_fuel_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_sanitation_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_insurance_pct` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **VERY_HIGH** |
| `nfhs_oope_delivery_rs` | 124 (83.8%) | 23 (15.5%) | 1 (0.7%) | **HIGH** |
| `rhs_phc_density_per_100k` | 97 (65.5%) | 25 (16.9%) | 26 (17.6%) | **HIGH** |
| `rhs_chc_density_per_100k` | 97 (65.5%) | 25 (16.9%) | 26 (17.6%) | **HIGH** |
| `rhs_subcentre_density_per_100k` | 97 (65.5%) | 25 (16.9%) | 26 (17.6%) | **HIGH** |
| `jan_aushadhi_density_per_100k` | 146 (98.6%) | 0 (0.0%) | 2 (1.4%) | **VERY_HIGH** |
| `mca21_pharma_density_per_100k` | **148 (100.0%)** | 0 (0.0%) | 0 (0.0%) | **VERY_HIGH** |
| `census_total_population` | 108 (73.0%) | 25 (16.9%) | 15 (10.1%) | **HIGH** |
| `census_urban_population_pct` | 108 (73.0%) | 25 (16.9%) | 15 (10.1%) | **HIGH** |
| `niti_aspirational_district_flag` | 148 (100.0%) | 0 (0.0%) | 0 (0.0%) | **PERFECT** |
