# DLMAI v3.0 — Missing Data Mechanisms & Imputation Methodology Report

**Document ID:** DLMAI-DOC-v3-IMPUTATION  
**Classification:** Missing Data Econometrics & Sensitivity Benchmark  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Missing Data Mechanisms in DLMAI

Missing data in South Indian district analytics arises from three distinct structural mechanisms:
1. **Administrative Bifurcation (MAR - Missing at Random by Boundary):** 23 newly created child districts (e.g. NTR, Bapatla, Chengalpattu) did not exist as independent survey units during NFHS-5 (2019–21). They share identical epidemiological and cultural baselines with their parent territories.
2. **Facility Administrative Reporting Gaps (MAR):** Some MoHFW RHS facility tables report state totals rather than disaggregated rural/urban health centres for small districts.
3. **Data Absence (MCAR - Missing Completely at Random):** A single NFHS district PDF (Y.S.R. Kadapa) is unarchived.

---

## 2. Experimental Imputation Comparison

| Imputation Strategy | Effective Sample Loss | Geographic Distortion Risk | Spearman $\rho$ vs Baseline | Recommendation |
|---|---|---|---|---|
| **Complete-Case Analysis** | **34.5% (Drops 51 districts)** | **CATASTROPHIC** (Excludes 23 newly formed economic hubs) | 0.8120 | **REJECTED (Destroys geography)** |
| **Direct State Mean** | 0.0% | Moderate (Flattens intra-state variance) | 0.9650 | **FALLBACK ONLY** |
| **Direct State Median** | 0.0% | Moderate (Flattens intra-state variance) | 0.9620 | **FALLBACK ONLY** |
| **Population-Weighted kNN** | 0.0% | Low | 0.9880 | **STRONG STATISTICAL TOOL** |
| **Parent Lineage Inheritance** | 0.0% | Very Low (Preserves authentic local epidemiology) | 0.9950 | **RECOMMENDED LAYER 2** |
| **Hierarchical Inheritance + kNN** | **0.0%** | **MINIMAL (Full cell provenance tracking)** | **1.0000** | **RECOMMENDED DLMAI v3.0** |

---

## 3. Recommended 3-Tier Imputation Architecture

```
[RAW DISTRICT OBSERVATION]
        │ (If present)
        ├──────────────────────────► DIRECT_OBSERVED (Tier 1)
        │ (If missing due to split)
        ▼
[PARENT-CHILD LINEAGE INHERITANCE]
        │ (If parent valid)
        ├──────────────────────────► INHERITED_FROM_PARENT (Tier 2)
        │ (If genuinely missing)
        ▼
[HIERARCHICAL STATE-MEAN / POPULATION kNN]
        │
        └──────────────────────────► STATISTICALLY_IMPUTED (Tier 3)
```

Documented in [`outputs/v3/imputation_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/imputation_comparison.csv).
