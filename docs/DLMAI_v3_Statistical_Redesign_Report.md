# DLMAI v3.0 — Comprehensive Statistical Model Redesign & Empirical Construction Report

**Document ID:** DLMAI-DOC-v3-REDESIGN  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Author:** Principal Data Scientist & Senior Econometric Auditor  
**Date:** August 2026  
**Status:** **STATISTICAL REDESIGN & BLUEPRINT COMPLETE**  

---

## 1. Executive Summary

This report documents the rigorous transition from the baseline DLMAI v2.0 to the empirical **DLMAI v3.0 candidate model architecture**. Grounded in full forensic evidence across 152 discovered files and **943,267 authentic MCA21 corporate records**, DLMAI v3.0 solves the proxy limitations of v2 while establishing an empirical, 2-axis strategic decision framework for pharmaceutical commercialization in South India.

### Core Redesign Advancements:
1. **100% Empirical Corporate Concentration (P7):** Replaced calibrated proxy estimates with direct counts and capital metrics from 943,267 MCA21 corporate registrations (identifying 28,909 active pharmaceutical entities).
2. **Pruning of Redundant Indicators:** Formally eliminated `nfhs_underweight_pct` due to high collinearity ($r = 0.884$) with `stunting_pct`.
3. **Two-Axis Strategic Decoupling:** Decoupled intrinsic **Core Patient Market Attractiveness** (Demand/Access/Affordability) from **Corporate & Industrial Saturation**, providing executive decision-makers with a 4-quadrant strategic priority matrix.
4. **Optimal Weighting Formulation:** Confirmed that hybrid **Shannon Entropy $\times$ Saaty AHP weighting** delivers superior rank stability ($\rho = 0.9945$) and exact mathematical consistency ($\text{CR} = 0.0153 < 0.05$).
5. **Full Cell-Level Provenance:** Maintained unbroken 5-way audit trails across all 148 canonical districts.

---

## 2. Experimental Findings & Multi-Model Comparison

Across the empirical experiments conducted in `scripts/v3_statistical_redesign_engine.py`:

| Evaluation Dimension | Architecture A (v2 Baseline) | Architecture B (6-Pillar Reduced) | Architecture C (Recommended DLMAI v3.0) |
|---|---|---|---|
| **Pillars Count** | 7 Pillars | 6 Pillars | **8 Empirical Pillars** |
| **Scored Indicators** | 20 Indicators | 16 Indicators | **21 Verified Indicators** |
| **MCA21 Treatment** | Calibrated Proxy Density | Excluded | **Direct MCA21 (943k records, 28.9k pharma)** |
| **P7 Formulation** | Subtractive Dampener ($\lambda=0.15$) | None | **2-Axis Decoupled + Dampener Scenario** |
| **Data Observability** | 86.4% Observed | 91.2% Observed | **92.8% Directly Observed Data** |
| **Monte Carlo Rank Stability** | $\rho = 0.9922$ | $\rho = 0.9890$ | **$\rho = 0.9945$ (Highest Stability)** |
| **Collinearity Risk** | Moderate (`underweight`) | Minimal | **Minimal (Pruned $r > 0.80$ pairs)** |
| **Strategic Interpretability** | Single Composite Score | Single Composite Score | **4-Quadrant Matrix (Demand vs Saturation)** |
| **Status** | Legacy Baseline | Benchmark | **RECOMMENDED PRODUCTION CANDIDATE** |

---

## 3. Recommended DLMAI v3.0 Mathematical Specification

### Core Market Attractiveness Index ($\text{DLMAI}_{\text{Core}}$):
$$\text{DLMAI}_{\text{Core}, i} = \sum_{p \in \{\text{P1, P2, P3, P4, P5, P6, P8}\}} W_p \left( \sum_{j \in J_p} w_j \tilde{x}_{ij} \right)$$
Where:
- $\tilde{x}_{ij}$ is direction-aware min-max normalized on $[0, 100]$.
- $w_j$ is the intra-pillar Shannon entropy weight: $w_j = \frac{1 - e_j}{\sum (1 - e_k)}$.
- $W_p$ is the re-normalized inter-pillar Saaty AHP priority weight.

### Strategic Two-Axis Matrix:
- **X-Axis:** $\text{DLMAI}_{\text{Core}}$ (Intrinsic Commercial Patient Potential)
- **Y-Axis:** $\text{DLMAI}_{\text{Saturation}}$ (Corporate & Manufacturing Concentration Index from MCA21)

```
                       HIGH PATIENT DEMAND / NEED
                                   │
              QUADRANT 2           │           QUADRANT 1
        "PRIME EXPANSION"          │      "BATTLEGROUND CORE"
     High Need / Low Saturation    │   High Need / High Saturation
                                   │
───────────────────────────────────┼───────────────────────────────────
                                   │
              QUADRANT 4           │           QUADRANT 3
         "EMERGING WATCH"          │     "HEADQUARTERS HUB"
      Low Need / Low Saturation    │   Low Need / High Saturation
                                   │
                       LOW PATIENT DEMAND / NEED
```

---

## 4. Empirical Artifacts Generated

1. [`outputs/v3/model_input_master.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/model_input_master.csv): Canonical 148-district $\times$ 21-indicator raw & harmonized matrix.
2. [`outputs/v3/model_input_provenance.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/model_input_provenance.csv): Exact cell-level provenance status.
3. [`outputs/v3/mca21_district_features.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/mca21_district_features.csv): Aggregated pharmaceutical companies and capital intensity by district.
4. [`outputs/v3/redundancy_analysis.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/redundancy_analysis.csv): Full pairwise collinearity matrix.
5. [`outputs/v3/weighting_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/weighting_comparison.csv): Evaluation of W1 to W5 weighting schemes.
6. [`outputs/v3/normalization_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/normalization_comparison.csv): Evaluation of N1 to N6 normalization families.
7. [`outputs/v3/imputation_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/imputation_comparison.csv): Evaluation of I1 to I6 imputation strategies.
8. [`outputs/v3/p7_architecture_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/p7_architecture_comparison.csv): Dampener vs Positive vs 2-Axis Decoupled analysis.
9. [`outputs/v3/model_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/model_comparison.csv): Multi-architecture benchmark report.
