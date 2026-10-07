# DLMAI v3.0 — Normalization Methodology Comparison & Transformation Report

**Document ID:** DLMAI-DOC-v3-NORMALIZATION  
**Classification:** Statistical Transformation Benchmark  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Experimental Setup

Six standard normalization methodologies were compared across all candidate indicators:
1. **Min-Max Baseline:** Direction-aware linear mapping onto $[0, 100]$.
2. **Robust Min-Max (IQR):** Interquartile range scaling ($Q_{0.75} - Q_{0.25}$) bounding extreme tails.
3. **Winsorized Min-Max (5th–95th Percentile):** Outlier-resistant linear transformation with tail clamping.
4. **Percentile Rank Transformation:** Non-parametric uniform rank mapping onto $[0, 100]$.
5. **Standard Z-Score:** Mean-zero, unit-variance standardization: $(x - \mu)/\sigma$.

---

## 2. Quantitative Transformation Results

| Normalization Method | Spearman $\rho$ vs Baseline | Top-10 Rank Preservation | Top-20 Rank Preservation | Bounded $[0, 100]$ | Outlier Sensitivity | Recommendation |
|---|---|---|---|---|---|---|
| **Min-Max Baseline** | **1.0000** | **100.0%** | **100.0%** | **Yes** | Moderate | **RECOMMENDED CORE** |
| **Robust Min-Max (IQR)** | 0.9985 | 100.0% | 95.0% | Yes | Low | **SENSITIVITY CHECK** |
| **Winsorized (5–95%)** | 0.9924 | 90.0% | 95.0% | Yes | Very Low | **ROBUST ALTERNATIVE** |
| **Percentile Rank** | 0.8574 | 70.0% | 75.0% | Yes | Zero | **REJECTED (Loses distance)** |
| **Standard Z-Score** | 0.9850 | 90.0% | 90.0% | No | High | **REJECTED (Unbounded)** |

---

## 3. Decision Rationale

- **Min-Max Baseline** preserves the true absolute interval distances between districts (e.g. distinguishing a district with 40% diabetes from one with 15%), whereas **Percentile Rank** completely destroys interval magnitude information.
- **Direction-Aware Min-Max** ensures natural score interpretability from 0 (lowest potential) to 100 (highest potential).

Documented in [`outputs/v3/normalization_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/normalization_comparison.csv).
