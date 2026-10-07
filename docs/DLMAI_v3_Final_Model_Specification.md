# DLMAI v3.0 — Final Statistical Model Specification & Implementation Blueprint

**Document ID:** DLMAI-SPEC-v3-FINAL  
**Classification:** Enterprise Model Architecture Specification  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  
**Status:** **STATISTICAL REDESIGN & PRODUCTION CANDIDATE BLUEPRINT**  

---

## 1. Specification Overview

DLMAI v3.0 is a multi-criteria, provenance-aware, 8-pillar district-level market attractiveness model designed for pharmaceutical commercial strategy across the **148 canonical districts of South India**.

---

## 2. Complete Model Equations

### 1. Direction-Aware Min-Max Normalization:
$$\tilde{x}_{ij} = \begin{cases}
\dfrac{x_{ij} - \min(x_j)}{\max(x_j) - \min(x_j)} \times 100, & \text{for Positive Benefit Indicators} \\[10pt]
\dfrac{\max(x_j) - x_{ij}}{\max(x_j) - \min(x_j)} \times 100, & \text{for Negative Cost Indicators}
\end{cases}$$

### 2. Intra-Pillar Shannon Information Entropy Weights:
$$p_{ij} = \frac{\tilde{x}_{ij} + 10^{-6}}{\sum_{k=1}^{148} (\tilde{x}_{kj} + 10^{-6})}, \quad e_j = -\frac{1}{\ln(148)} \sum_{i=1}^{148} p_{ij} \ln(p_{ij})$$
$$w_j = \frac{1 - e_j}{\sum_{k \in J_p} (1 - e_k)}$$

### 3. Pillar Sub-Scores:
$$P_{ip} = \sum_{j \in J_p} w_j \tilde{x}_{ij}, \quad \forall p \in \{\text{P1, P2, P3, P4, P5, P6, P7, P8}\}$$

### 4. Core Market Attractiveness Index ($\text{DLMAI}_{\text{Core}}$):
$$\text{DLMAI}_{\text{Core}, i} = \sum_{p \in \{\text{P1, P2, P3, P4, P5, P6, P8}\}} W_p P_{ip}$$
Where the Saaty AHP priority weights $\mathbf{W}$ are:
- $\text{P1 (Healthcare Need)}: W_1 = 0.3200$
- $\text{P3 (Healthcare Access)}: W_3 = 0.2200$
- $\text{P2 (Demographic Potential)}: W_2 = 0.1600$
- $\text{P5 (Economic Affordability)}: W_5 = 0.1200$
- $\text{P4 (Healthcare Utilization)}: W_4 = 0.0800$
- $\text{P6 (Medicine Availability)}: W_6 = 0.0500$
- $\text{P8 (Growth & Policy Priority)}: W_8 = 0.0500$
- *($\sum W_p = 1.0000$, Saaty Consistency Ratio $\text{CR} = 0.0153 < 0.05$)*

### 5. Corporate Concentration Index ($\text{DLMAI}_{\text{Saturation}}$):
$$\text{DLMAI}_{\text{Saturation}, i} = P_{i, \text{P7}}$$
Derived from empirical active pharmaceutical corporate density per 100k and paid-up capital intensity from the 943k MCA21 registry.

---

## 3. Decision Matrix & 4-Quadrant Strategic Categorization

$$\text{Strategic Category}_i = \begin{cases}
\text{Quadrant 1: Battleground Core}, & \text{DLMAI}_{\text{Core}, i} \ge 50.0 \text{ and } \text{DLMAI}_{\text{Saturation}, i} \ge 50.0 \\
\text{Quadrant 2: Prime Expansion}, & \text{DLMAI}_{\text{Core}, i} \ge 50.0 \text{ and } \text{DLMAI}_{\text{Saturation}, i} < 50.0 \\
\text{Quadrant 3: Headquarters Hub}, & \text{DLMAI}_{\text{Core}, i} < 50.0 \text{ and } \text{DLMAI}_{\text{Saturation}, i} \ge 50.0 \\
\text{Quadrant 4: Emerging Watch}, & \text{DLMAI}_{\text{Core}, i} < 50.0 \text{ and } \text{DLMAI}_{\text{Saturation}, i} < 50.0
\end{cases}$$

---

## 4. Legitimate vs Prohibited Claims

- **Permitted Claim:** *"DLMAI v3.0 is an 8-pillar composite index evaluating district-level pharmaceutical patient demand, healthcare infrastructure, and corporate manufacturing saturation using authentic government data across 148 South Indian districts."*
- **Forbidden Claim:** *"DLMAI v3.0 predicts commercial secondary sales volume in rupees."* (Commercial sales data remains unobserved).
