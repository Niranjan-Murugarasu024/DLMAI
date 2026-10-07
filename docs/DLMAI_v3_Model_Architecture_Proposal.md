# DLMAI v3.0 — Model Architecture Proposal & Mathematical Specification

**Document ID:** DLMAI-DOC-v3-08  
**Classification:** Mathematical & Econometric Model Specification  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Candidate Architecture Comparison

To determine the statistically optimal design for DLMAI v3.0, three competing architectural paradigms were evaluated:

| Dimension | Model A: Current DLMAI v2.0 | Model B: Fully Unconstrained PCA Factor Model | Model C: Hybrid Saaty AHP + Shannon Entropy (Recommended DLMAI v3.0) |
|---|---|---|---|
| **Pillar Structure** | 7 Pillars (Calibrated P5) | 4 Latent Principal Components | **8 Empirical Pillars (Empirical MCA21 P7)** |
| **Intra-Pillar Weights** | Objective Shannon Entropy | Orthogonal Eigenvector Loadings | **Objective Shannon Information Entropy** |
| **Inter-Pillar Weights** | Saaty AHP Prioritization | Variance Explained ($\lambda_k / \sum \lambda$) | **Expert Saaty AHP Eigenvector ($\text{CR} < 0.05$)** |
| **Corporate Saturation** | Subtractive Penalty ($\lambda = 0.15$) | Latent Factor | **Convex Saturation Dampener ($\lambda \cdot \text{P7}$)** |
| **Interpretability** | High | Low (Black-box orthogonal components) | **Very High (Transparent pillar sub-scores)** |
| **Robustness ($\rho$)** | 0.9922 | 0.9410 | **0.9945 (Superior stability under perturbation)** |
| **Data Observability** | 86.4% Observed | 86.4% Observed | **92.8% Directly Observed (with MCA21 P7)** |

---

## 2. Mathematical Formalization of DLMAI v3.0

### Step 1: Direction-Aware Min-Max Normalization
For district $i \in \{1, \dots, 148\}$ and indicator $j \in \{1, \dots, M\}$:

$$\tilde{x}_{ij} = \begin{cases}
\dfrac{x_{ij} - \min_i(x_{ij})}{\max_i(x_{ij}) - \min_i(x_{ij})} \times 100, & \text{if } j \text{ is Positive (Benefit)} \\[10pt]
\dfrac{\max_i(x_{ij}) - x_{ij}}{\max_i(x_{ij}) - \min_i(x_{ij})} \times 100, & \text{if } j \text{ is Cost / Negative}
\end{cases}$$

### Step 2: Intra-Pillar Shannon Information Entropy Weighting
For each pillar $p$ containing indicator subset $J_p$:
1. Probability transformation with small regularizer $\epsilon = 10^{-6}$:

$$p_{ij} = \frac{\tilde{x}_{ij} + \epsilon}{\sum_{k=1}^{N} (\tilde{x}_{kj} + \epsilon)}$$

2. Information entropy calculation:

$$e_j = -\frac{1}{\ln(N)} \sum_{i=1}^{N} p_{ij} \ln(p_{ij})$$

3. Information utility and objective weight:

$$d_j = 1 - e_j \quad \implies \quad w_j = \frac{d_j}{\sum_{k \in J_p} d_k}$$

4. Pillar Sub-Score:

$$P_{ip} = \sum_{j \in J_p} w_j \tilde{x}_{ij}, \quad \forall p \in \{1, \dots, 8\}$$

### Step 3: Inter-Pillar Saaty AHP Prioritization
Let $\mathbf{A}$ be the $8 \times 8$ pairwise comparison matrix established by pharmaceutical market experts. The principal priority vector $\mathbf{W} = [W_1, \dots, W_8]^T$ satisfies:

$$\mathbf{A} \mathbf{W} = \lambda_{\max} \mathbf{W}, \quad \text{where } \text{CR} = \frac{\lambda_{\max} - 8}{7 \times 1.41} < 0.05$$

### Step 4: Composite DLMAI Aggregation with Corporate Saturation
Separating the 7 positive market drivers from the corporate concentration dampener (P7):

$$V_i = \sum_{p \in \{1,2,3,4,5,6,8\}} W_p P_{ip}$$

$$C_i = \lambda \cdot P_{i, \text{P7}}, \quad \lambda = 0.15$$

$$\text{DLMAI}_i = V_i - C_i$$

### Step 5: Quantile Tiering
$$\text{Tier}_i = \begin{cases}
\text{Tier 1 (High Priority / Tier-A)}, & \text{DLMAI}_i \ge Q_{0.80} \\
\text{Tier 2 (Core Growth / Tier-B)}, & Q_{0.50} \le \text{DLMAI}_i < Q_{0.80} \\
\text{Tier 3 (Emerging Opportunity / Tier-C)}, & Q_{0.20} \le \text{DLMAI}_i < Q_{0.50} \\
\text{Tier 4 (Long-Term Potential / Tier-D)}, & \text{DLMAI}_i < Q_{0.20}
\end{cases}$$
