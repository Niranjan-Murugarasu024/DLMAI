# DLMAI v3.0 — Temporal Coverage & Multi-Period Structure Report

**Document ID:** DLMAI-DOC-v3-05  
**Classification:** Econometric & Temporal Data Architecture  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Temporal Classification of DLMAI v3.0

DLMAI v3.0 is fundamentally structured as a **Multi-Source Cross-Sectional Index (Static Macro Composite)** benchmarked to the modern post-pandemic operational period (**2021–2024**).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TEMPORAL ANCHORS OF INPUT DATA STREAMS                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Census 2011 PCA              : 2011 Baseline (Adjusted to 2024 via decadal growth)  │
│ 2. SECC Socioeconomic Census   : 2011-2012 State Poverty & Living Standard Baseline   │
│ 3. NITI Aspirational Baseline   : 2018-2024 Continuous Policy Priority Status          │
│ 4. NFHS-5 Survey               : 2019-2021 Epidemiological & Maternal-Child Baseline  │
│ 5. MoHFW RHS Table             : 2021-2022 Healthcare Infrastructure Panel            │
│ 6. PMBJP Jan Aushadhi Registry : 2023-2024 Active Retail Kendra Network                │
│ 7. MCA21 Corporate Registry    : Cumulative to 2024 Active Corporate Enterprise Stock │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Temporal Compatibility & Harmonization Strategy

1. **Census 2011 Population Aging & Scaling:** Raw Census 2011 population totals are updated to 2024 projected district populations using state-specific decadal growth rates and urban agglomeration multipliers.
2. **NFHS-5 Relevance:** NFHS-5 represents the latest comprehensive district-level health survey conducted by the Government of India. Its epidemiological rates (hypertension, diabetes, malnutrition) reflect structural disease prevalence patterns with high multi-year stability.
3. **MCA21 Real-Time Alignment:** The MCA21 corporate registry provides a live, active stock of registered pharmaceutical companies as of 2024.
4. **PMBJP Dynamic Network:** Jan Aushadhi Kendra counts reflect active retail generic pharmacy distribution points operational in 2023–2024.

---

## 3. Implications for Econometric Modeling

- **Cross-Sectional Integrity:** DLMAI v3.0 evaluates relative spatial attractiveness across districts at a single unified modern epoch.
- **Pseudo-Panel Potential (Future Phase):** When NFHS-6 and Census 2026 become publicly available, DLMAI can be expanded into a true longitudinal panel to measure district-level market trajectory and structural transition dynamics over time.
