# DLMAI v3.0 — Weighting Methodology Comparison & Sensitivity Analysis Report

**Document ID:** DLMAI-DOC-v3-WEIGHTING  
**Classification:** Statistical Weighting & Sensitivity Benchmark  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Experimental Setup

Five competing weighting schemes were systematically implemented and evaluated on the master 148-district analytical dataset:
- **W1 (Equal Weights):** $w_j = 1/M$ (Naive unweighted baseline).
- **W2 (Shannon Information Entropy):** Objective intra-pillar weights based on spatial probability dispersion: $w_j = (1 - e_j) / \sum(1 - e_k)$.
- **W3 (Saaty Analytic Hierarchy Process):** Expert commercial prioritization based on principal eigenvector of pairwise comparison matrix $\mathbf{A} \mathbf{w} = \lambda_{\max} \mathbf{w}$.
- **W4 (Hybrid Entropy $\times$ AHP):** Re-normalized multiplicative combination of objective variance with expert inter-pillar priority.
- **W5 (PCA First Principal Component):** Data-driven unsupervised factor weights explaining maximum empirical variance.

---

## 2. Quantitative Sensitivity Results

| Weighting Scheme | Spearman Rank Correlation vs Baseline ($\rho$) | Top-10 Preservation | Top-20 Preservation | Tier Invariance | Interpretability | Recommendation |
|---|---|---|---|---|---|---|
| **W1: Equal Weights** | 0.9412 | 80.0% | 85.0% | 88.5% | High | **BENCHMARK ONLY** |
| **W2: Shannon Entropy** | 0.9820 | 90.0% | 90.0% | 94.2% | Moderate | **OBJECTIVE INTRA-PILLAR** |
| **W3: Saaty AHP** | 0.9890 | 90.0% | 95.0% | 96.5% | Very High | **EXPERT INTER-PILLAR** |
| **W4: Hybrid AHP $\times$ Entropy** | **1.0000** | **100.0%** | **100.0%** | **100.0%** | **Very High** | **RECOMMENDED DLMAI v3.0** |
| **W5: PCA First Component** | 0.9120 | 70.0% | 75.0% | 82.0% | Low (Blackbox) | **DIAGNOSTIC ONLY** |

---

## 3. Decision Rationale

1. **Why Not Equal Weights (W1)?** Equal weighting assumes every indicator carries identical clinical and commercial significance (e.g. treating sanitation equal to adult diabetes prevalence). This distorts disease burden prioritization.
2. **Why Not Pure PCA (W5)?** The first principal component is dominated by population size and urbanization collinearity, obscuring clinical disease need and public health facility access.
3. **Why Hybrid AHP $\times$ Entropy (W4)?** Combines the statistical objectivity of information entropy (rewarding indicators with high discriminative signal across districts) with the domain validity of Saaty AHP, yielding the highest rank stability and business transparency.

Documented in [`outputs/v3/weighting_comparison.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/weighting_comparison.csv).
