# DLMAI v3.0 — Model Governance, Decision Log & Audit Policy Plan

**Document ID:** DLMAI-DOC-v3-10  
**Classification:** Enterprise Model Risk Management & Governance Policy  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Enterprise Model Governance Framework

DLMAI v3.0 complies with international model risk management standards (SR 11-7 / OCC 2011-12) adapted for pharmaceutical commercial strategy.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                MODEL GOVERNANCE LIFECYCLE                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. DATA GOVERNANCE    : Strict schema validation, LGD canonical checks, hash logging   │
│ 2. PIPELINE RUNNER    : Single authoritative entry point with 15 pre/post quality gates│
│ 3. PROVENANCE LOGGING : Full 5-way classification exported per cell in CSV/JSON       │
│ 4. RED-TEAM VALIDATION: 25-test adversarial battery required prior to deployment       │
│ 5. REPRODUCIBILITY    : Fixed random seeds, exact mathematical formulas, zero mock data│
│ 6. BOUNDARY CONTROL   : Explicit prohibition against claims of empirical sales predict.│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Model Decision Log (DLMAI v1.0 $\rightarrow$ v2.0 $\rightarrow$ v3.0)

| Decision ID | Model Component | Decision Implemented | Statistical Rationale | Business Rationale | Version |
|---|---|---|---|---|---|
| **DEC_01** | Geography Master | Standardized on 148 LGD districts | Eliminates mock prototype IDs and spatial fragmentation | Aligns with commercial field-force territories | v2.0 |
| **DEC_02** | Inheritance Engine | Fixed-point recursive parent-child propagation | Solves missing data in newly split districts without distortion | Preserves authentic local epidemiological profiles | v2.0 |
| **DEC_03** | Weighting Engine | Hybrid Saaty AHP + Shannon Entropy | Balances objective indicator variance with expert commercial priorities | Prevents mathematically arbitrary equal weighting | v2.0 |
| **DEC_04** | P5 Corporate Proxy | Declared as `DEGRADED_P5_PROXY` | Eliminates false claims of direct bulk MCA observation | Transparent governance and limitation disclosure | v2.0 |
| **DEC_05** | Quality Gates Engine | Integrated 15 automated validation gates | Halts execution immediately on geography or domain errors | Prevents silent data corruption | v2.0 |
| **DEC_06** | Test 8 Benchmark | Classified as Class D Synthetic Benchmark | Prevents circularity and false validation claims | Maintains high scientific integrity | v2.0 |
| **DEC_07** | MCA21 Integration | Incorporate 943k MCA21 corporate registry records into empirical P7 | Replaces proxy estimates with directly observed pharma units | Directly captures pharmaceutical industrial clustering | **v3.0** |
| **DEC_08** | Indicator Pruning | Remove `underweight_pct` due to $r=0.884$ collinearity with `stunting_pct` | Lowers multicollinearity and stabilizes variance | Focuses on height-for-age chronic stunting | **v3.0** |
| **DEC_09** | 8-Pillar Expansion | Expand to 8 distinct conceptual pillars | Separate Utilization from Access and Corporate Concentration | Granular commercial portfolio strategy | **v3.0** |

---

## 3. Legitimate Claims vs. Prohibited Claims

### Legitimate Claims Allowed:
- *"DLMAI v3.0 is a statistically defensible, multi-criteria composite index evaluating district-level pharmaceutical market attractiveness across 148 South Indian districts."*
- *"The model synthesizes observed government data across disease prevalence, demographics, healthcare infrastructure, purchasing power, generic pharmacy retail, and corporate pharmaceutical presence."*
- *"Model weights and rankings demonstrate high statistical stability ($\rho = 0.9945$) under 1,000 Monte Carlo stochastic perturbations."*

### Prohibited Claims Forbidden:
- ❌ *"DLMAI predicts actual pharmaceutical sales revenue in rupees."* (Requires paid IQVIA/AWACS sales invoices).
- ❌ *"DLMAI is empirically validated against commercial market sales data."* (Benchmark is synthetic Class D).
- ❌ *"Pillar 7 measures field-force medical representative competition density."* (Measures registered corporate headquarters and manufacturing facilities).
