# DLMAI v3.0 — Comprehensive Statistical Validation Strategy & Adversarial Test Battery

**Document ID:** DLMAI-DOC-v3-09  
**Classification:** Statistical Model Validation & Stress-Testing Protocol  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Validation Philosophy & Non-Negotiables

Before promoting any model specification to production, DLMAI v3.0 requires execution of a **25-Test Adversarial Validation Suite**:
1. **Zero Point Estimate Reliance:** Every district must have empirical rank confidence intervals via Monte Carlo and bootstrap simulations.
2. **Zero Direct Score Leakage:** The composite DLMAI score is never used in explanatory features or validation targets.
3. **Transparent Benchmark Classification:** Target commercial sales benchmarks must be labeled **Class D: Synthetic/Calibrated Benchmark** (internal scenario check only).

---

## 2. The 25-Test Adversarial Validation Battery

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE 25-TEST ADVERSARIAL VALIDATION SUITE                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ T01: Fully Independent Model Recomputation & Zero-Tolerance Reconciliation             │
│ T02: Canonical Geography Integrity (148 LGD District Universe Assertion)               │
│ T03: Zero Sample / Prototype Identifier Contamination Assertion                        │
│ T04: Indicator Domain & Unit Range Integrity Assertion                                 │
│ T05: Linear Identity Exactness & Non-NaN Assertion                                     │
│ T06: Normalization Sensitivity & Decomposition (Min-Max vs IQR vs Percentile)          │
│ T07: Weighting Sensitivity & Effect Decomposition (Entropy vs Equal vs AHP)            │
│ T08: Pillar Removal & Sensitivity Decomposition                                        │
│ T09: Decision-Oriented Top-N Inclusion Probabilities (N=10, 20, 30)                    │
│ T10: Rank Invariance & Volatility Classification                                       │
│ T11: Multicollinearity & Variance Inflation Factor (VIF) Audit                         │
│ T12: Pairwise Indicator Redundancy Audit                                               │
│ T13: Pillar 7 Corporate Saturation Ablation ($\lambda = 0.0$ vs $\lambda = 0.15$)      │
│ T14: MCA21 Company Classification Sensitivity (NIC vs Name Matches)                    │
│ T15: Imputation Sensitivity & Missing Data Mechanism Audit (MCAR / MAR)                │
│ T16: Monte Carlo Stochastic Weight Perturbation ($\sigma^2 = 0.04$, $N=1,000$)         │
│ T17: Non-Parametric Bootstrap Uncertainty Estimation ($B=1,000$)                       │
│ T18: Spatial Leave-One-State-Out (LOSO) Cross-Validation (7 States)                   │
│ T19: Temporal Robustness & Decadal Sensitivity Analysis                                │
│ T20: Naive Baseline Comparison (Population, Urbanization, Income)                      │
│ T21: Data-Quality Bias Regression Audit (DLMAI $\sim$ Completeness)                    │
│ T22: Target Leakage & Covariate Circularity Detection Matrix                           │
│ T23: Structural Boundary Break Sensitivity (Pre/Post-Bifurcation Districts)            │
│ T24: Spatial Autocorrelation & Moran's I Geographic Clustering                         │
│ T25: 15-Gate Enterprise Quality Assertion Pipeline                                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Key Statistical Acceptance Thresholds

- **AHP Consistency Ratio:** $\text{CR} < 0.05$ (Saaty threshold $\text{CR} < 0.10$).
- **Monte Carlo Rank Stability:** Mean Spearman $\rho \ge 0.980$ across 1,000 iterations.
- **Top-10 Rank Preservation:** $\ge 80\%$ under $\pm 20\%$ weight perturbation.
- **Data Quality Bias:** Pearson correlation $|r| < 0.15$ between completeness and final score.
- **Max Recomputation Numerical Error:** Absolute error $\le 10^{-6}$.
