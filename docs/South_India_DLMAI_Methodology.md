# South India District-Level Market Attractiveness Index (DLMAI)
## Statistical Methodology & Mathematical Formulation (Version 2.0.0)

**Document Version:** 2.0.0 (Post-Audit Reconciled)  
**Target Geography:** South India Regional Universe (148 Canonical Districts across 7 States/UTs)  
**Methodological Standard:** Multi-Criteria Decision Analysis (MCDA), Shannon Information Entropy, Saaty Analytic Hierarchy Process (AHP), and Monte Carlo Stochastic Sensitivity Validation  

---

## 1. Conceptual Framework & Regional Scope

The **South India District-Level Market Attractiveness Index (DLMAI)** is a multi-dimensional decision-support index designed to evaluate and rank districts across South India for pharmaceutical commercial opportunity, field sales deployment, hospital key-account management, and supply chain expansion.

The analytical population comprises exactly **148 canonical districts** across:
1. **Tamil Nadu** (38 districts)
2. **Kerala** (14 districts)
3. **Karnataka** (31 districts)
4. **Andhra Pradesh** (26 districts)
5. **Telangana** (33 districts)
6. **Goa** (2 districts)
7. **Puducherry** (4 districts)

The index structures 20 core indicators across 7 functional pillars:
- **Value Drivers (Positive opportunity pillars):**
  - **Pillar 1:** Healthcare Demand & Disease Burden
  - **Pillar 2:** Economic Access & Affordability
  - **Pillar 3:** Healthcare Infrastructure
  - **Pillar 4:** Pharmaceutical Distribution Accessibility
  - **Pillar 6:** Policy & Healthcare Development Environment
  - **Pillar 7:** Demographic & Market Growth
- **Value Dampener (Market friction / competitive crowding pillar):**
  - **Pillar 5:** Market Competition & Saturation

---

## 2. Mathematical Pipeline Overview

```
┌────────────────────────────────────────────────────────┐
│ Stage 1: Feature Engineering & Rate Standardization   │
│  - Raw Counts -> Per-100k Population Densities         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 2: Direction-Aware Min-Max Normalization (0-100) │
│  - Positive Indicators: R_ij = (X_ij - Min) / (Max - Min) * 100
│  - Negative Indicators: R_ij = (Max - X_ij) / (Max - Min) * 100
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 3: Intra-Pillar Shannon Information Entropy     │
│  - Probability: p_ij = (R_ij + eps) / sum(R_ij + eps)  │
│  - Entropy: e_j = - (1 / ln M) sum(p_ij ln p_ij)       │
│  - Objective Weight: w_j = (1 - e_j) / sum(1 - e_j)    │
│  - Pillar Sub-Score: S_ip = sum(w_j R_ij)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 4: Inter-Pillar Saaty AHP Prioritization         │
│  - Pairwise Comparison Matrix A -> Principal Eigenvec w│
│  - Consistency Index: CI = (lambda_max - n) / (n - 1)  │
│  - Consistency Ratio: CR = CI / RI_7 = 0.0153 < 0.10   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 5: Value Driver Aggregation - Saturation Penalty │
│  - Saturation Intensity: S_i5 = (X_i5 - Min) / (Max - Min) * 100
│  - Positive Value: V_i = sum_{p != 5} w'_p S_ip        │
│  - Saturation Penalty: C_i = lambda * S_i5 (lambda = 0.15)
│  - DLMAI_i = V_i - C_i                                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 6: Monte Carlo Sensitivity & Robustness Engine   │
│  - Perturbation: w'_p^(k) = w'_p * exp(eps_p), eps ~ N(0, 0.04)
│  - 1,000 Iterations -> Spearman rho_s, Rank 95% CIs    │
└────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Mathematical Formulation

### 3.1 Stage 1: Feature Standardization & Density Construction
To eliminate confounding by absolute population size, all count indicators (PHCs, CHCs, sub-centres, Jan Aushadhi Kendras, pharma companies) are standardized per 100,000 population:

$$\text{Density}_{i,k} = \frac{\text{Raw Count}_{i,k}}{\text{Population}_i / 100{,}000}$$

---

### 3.2 Stage 2: Direction-Aware Normalization

Let $X_{ij}$ be the value of indicator $j$ in district $i$.

#### Positive Indicators ($j \in \mathcal{I}^+$):
$$R_{ij} = \begin{cases}
\frac{X_{ij} - \min_i(X_{ij})}{\max_i(X_{ij}) - \min_i(X_{ij})} \times 100 & \text{if } \max_i(X_{ij}) > \min_i(X_{ij}) \\
50.0 & \text{otherwise}
\end{cases}$$

#### Negative Indicators ($j \in \mathcal{I}^-$, e.g. Out-of-Pocket Delivery Expenditure):
$$R_{ij} = \begin{cases}
\frac{\max_i(X_{ij}) - X_{ij}}{\max_i(X_{ij}) - \min_i(X_{ij})} \times 100 & \text{if } \max_i(X_{ij}) > \min_i(X_{ij}) \\
50.0 & \text{otherwise}
\end{cases}$$

All normalized indicators $R_{ij} \in [0, 100]$.

---

### 3.3 Stage 3: Intra-Pillar Shannon Entropy Weighting

For multi-indicator pillars ($p \in \{1, 2, 3, 7\}$) containing $K_p > 1$ indicators across $M = 148$ districts:

1. **Probability Distribution Matrix:**
   $$p_{ij} = \frac{R_{ij} + 10^{-6}}{\sum_{i=1}^{M} (R_{ij} + 10^{-6})}$$

2. **Information Entropy ($e_j$):**
   $$e_j = -\frac{1}{\ln(M)} \sum_{i=1}^{M} p_{ij} \ln(p_{ij})$$
   *(Since $0 \le p_{ij} \le 1$, $e_j \in [0, 1]$).*

3. **Information Utility & Weight ($w_{j,p}^{\text{entropy}}$):**
   $$d_j = 1 - e_j$$
   $$w_{j,p}^{\text{entropy}} = \frac{d_j}{\sum_{l=1}^{K_p} d_l}, \quad \text{such that } \sum_{j=1}^{K_p} w_{j,p}^{\text{entropy}} = 1.0$$

4. **Pillar Sub-Score Calculation:**
   $$S_{i,p} = \sum_{j=1}^{K_p} w_{j,p}^{\text{entropy}} \cdot R_{ij}$$

*(For single-indicator pillars P4, P5, and P6, $w = 1.0$ and $S_{i,p} = R_{i,p}$).*

---

### 3.4 Stage 4: Inter-Pillar Prioritization via Saaty AHP

The inter-pillar importance hierarchy is modeled through a $7 \times 7$ pairwise comparison matrix $A$:

$$A = \begin{pmatrix}
1 & 3 & 2 & 4 & 7 & 5 & 5 \\
1/3 & 1 & 1/2 & 2 & 5 & 3 & 3 \\
1/2 & 2 & 1 & 3 & 6 & 4 & 4 \\
1/4 & 1/2 & 1/3 & 1 & 4 & 2 & 2 \\
1/7 & 1/5 & 1/6 & 1/4 & 1 & 1/2 & 1/2 \\
1/5 & 1/3 & 1/4 & 1/2 & 2 & 1 & 1 \\
1/5 & 1/3 & 1/4 & 1/2 & 2 & 1 & 1
\end{pmatrix}$$

#### Principal Eigenvector Derivation ($Aw = \lambda_{\max} w$):
- $\lambda_{\max} = 7.121566$
- $\text{Consistency Index (CI)} = \frac{\lambda_{\max} - n}{n - 1} = \frac{7.121566 - 7}{6} = 0.020261$
- $\text{Random Index (RI}_7\text{)} = 1.32$
- $\text{Consistency Ratio (CR)} = \frac{\text{CI}}{\text{RI}_7} = \frac{0.020261}{1.32} = \mathbf{0.015349} < \mathbf{0.10} \quad (\mathbf{1.53\%}, \text{Strictly Consistent})$

#### Normalized AHP Priority Weights ($w_p$):
- **$w_{\text{P1}}$ (Demand & Disease Burden):** $0.354117$ (35.41%)
- **$w_{\text{P3}}$ (Healthcare Infrastructure):** $0.238561$ (23.86%)
- **$w_{\text{P2}}$ (Economic Access):** $0.156329$ (15.63%)
- **$w_{\text{P4}}$ (Distribution Accessibility):** $0.100382$ (10.04%)
- **$w_{\text{P6}}$ (Policy & Development):** $0.058541$ (5.85%)
- **$w_{\text{P7}}$ (Growth Momentum):** $0.058541$ (5.85%)
- **$w_{\text{P5}}$ (Industry Saturation):** $0.033529$ (3.35%)

---

### 3.5 Stage 5: Value Driver Aggregation & Saturation Dampening

#### 1. Re-normalized Positive Driver Weights ($w'_p$ for $p \ne 5$):
$$w'_p = \frac{w_p}{\sum_{q \ne 5} w_q} = \frac{w_p}{0.966471}$$
- $w'_{\text{P1}} = 0.366402$ (36.64%)
- $w'_{\text{P3}} = 0.246837$ (24.68%)
- $w'_{\text{P2}} = 0.161753$ (16.18%)
- $w'_{\text{P4}} = 0.103865$ (10.39%)
- $w'_{\text{P6}} = 0.060572$ (6.06%)
- $w'_{\text{P7}} = 0.060572$ (6.06%)
- $\sum_{p \ne 5} w'_p = 1.000000$

#### 2. Positive Value Driver Score ($V_i$):
$$V_i = \sum_{p \in \{1,2,3,4,6,7\}} w'_p \cdot S_{i,p}, \quad V_i \in [0, 100]$$

#### 3. Saturation Intensity Score ($S^{\text{sat}}_i$):
Pillar 5 is normalized directly so that higher company density yields a higher saturation score:
$$S^{\text{sat}}_i = \frac{X_{i,5} - \min_i(X_{i,5})}{\max_i(X_{i,5}) - \min_i(X_{i,5})} \times 100, \quad S^{\text{sat}}_i \in [0, 100]$$

#### 4. Saturation Penalty & Final DLMAI Score:
$$C_i = \lambda \cdot S^{\text{sat}}_i, \quad \lambda = 0.15 \text{ (Configurable: } 0.10\text{--}0.20\text{)}$$
$$\mathbf{DLMAI}_i = V_i - C_i = \left( \sum_{p \in \{1,2,3,4,6,7\}} w'_p S_{i,p} \right) - \left( 0.15 \cdot S^{\text{sat}}_i \right)$$

---

### 3.6 Non-Compensatory Geometric Alternative (Benchmark Model)

For methodology comparison, a non-compensatory geometric aggregation model with multiplicative competition discounting is formulated:

$$C_i^{\text{geo}} = 1.0 - \left( \lambda \cdot \frac{S^{\text{sat}}_i}{100} \right), \quad C_i^{\text{geo}} \in [0.85, 1.00]$$
$$\mathbf{DLMAI}_i^{\text{geometric}} = \left[ \prod_{p \in \{1,2,3,4,6,7\}} (S_{i,p} + 1.0)^{w'_p} \right] \times C_i^{\text{geo}}$$

---

## 4. Monte Carlo Sensitivity Analysis

To rigorously validate rank stability, stochastic log-normal perturbation is applied to the pillar weights across 1,000 iterations:

$$w_p^{(k)} = w'_p \cdot \exp(\epsilon_p), \quad \epsilon_p \sim \mathcal{N}\left(0, \sigma^2 = 0.04\right), \quad k = 1, \dots, 1000$$
$$w_{p,\text{norm}}^{(k)} = \frac{w_p^{(k)}}{\sum_{q \ne 5} w_q^{(k)}}$$

For each simulation $k$, recompute $\text{DLMAI}_i^{(k)}$ and rank $R_i^{(k)}$, then calculate the **Spearman Rank Correlation**:

$$\rho_s^{(k)} = 1 - \frac{6 \sum_{i=1}^{M} (R_i^{(0)} - R_i^{(k)})^2}{M(M^2 - 1)}$$

### Stability Assessment Bands:
- **$\bar{\rho}_s \ge 0.95$:** Highly Robust & Stable (Target met).
- **$0.90 \le \bar{\rho}_s < 0.95$:** Stable.
- **$0.75 \le \bar{\rho}_s < 0.90$:** Moderately Sensitive.
- **$\bar{\rho}_s < 0.75$:** Highly Volatile.

---

## 5. District Classification Tiering System

Districts are categorized into four commercial tiers using exact **Quantile Boundaries**:

| Tier | Percentile Cutoff | District Count (~148) | Commercial Strategy & Field Action |
|:---:|:---:|:---:|---|
| **Tier 1: High Priority** | $\ge 80\text{th}$ Percentile | Top ~30 Districts | Primary commercial focus: dedicated specialty field force, tertiary hospital empanelment, stockist hubs. |
| **Tier 2: Growth Markets** | $50\text{th}\text{--}80\text{th}$ Percentile | ~44 Districts | Accelerated growth: retail pharmacy reach expansion, secondary hospital prescriber coverage. |
| **Tier 3: Moderate Opportunity** | $20\text{th}\text{--}50\text{th}$ Percentile | ~44 Districts | Secondary focus: generic trade portfolio, Jan Aushadhi generic alignment, distributor-led fulfillment. |
| **Tier 4: Nascent / Rural** | $< 20\text{th}$ Percentile | Bottom ~30 Districts | Niche markets: public healthcare procurement tenders, primary clinic coverage, public health partnerships. |

---
*Methodology Complete. Documented in `docs/South_India_DLMAI_Methodology.md`.*
