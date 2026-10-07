# DLMAI v2.0 — Immutable Architecture Snapshot & Baseline Record

**Document ID:** DLMAI-SNAP-v2-FROZEN  
**Snapshot Timestamp:** August 2026  
**Status:** **FROZEN & IMMUTABLE BASELINE**  
**Geographic Universe:** South India (7 States/UTs, 148 Canonical LGD Districts)  

---

## 1. Executive Summary & Purpose

This document constitutes an immutable, archival record of the production **DLMAI v2.0 model architecture**, capturing its exact mathematical formulations, indicator catalog, weighting matrices, imputation hierarchy, normalization rules, and validation metrics prior to the empirical construction of DLMAI v3.0.

---

## 2. DLMAI v2.0 Indicator Catalog & Pillar Bindings

DLMAI v2.0 utilizes **20 analytical indicators** partitioned across **7 theoretical pillars**:

| Pillar Code & Name | Indicator Identifier | Direction | Source Dataset | Measurement Unit |
|---|---|---|---|---|
| **P1: Chronic Disease & Need** | `nfhs_hypertension_combined_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_diabetes_combined_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_stunting_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_wasting_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_underweight_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| **P2: Demographic Potential** | `census_total_population` | POSITIVE | Census 2011 PCA | Persons |
| | `census_urban_population_pct` | POSITIVE | Census 2011 PCA | Percentage ($\%$) |
| | `census_population_age_0_6_pct` | POSITIVE | Census 2011 PCA | Percentage ($\%$) |
| **P3: Healthcare Access** | `rhs_phc_density_per_100k` | POSITIVE | MoHFW RHS Table | Count per 100k pop |
| | `rhs_chc_density_per_100k` | POSITIVE | MoHFW RHS Table | Count per 100k pop |
| | `rhs_subcentre_density_per_100k` | POSITIVE | MoHFW RHS Table | Count per 100k pop |
| | `rhs_hospital_presence` | POSITIVE | MoHFW RHS Table | Binary $[0, 1]$ |
| **P4: Economic Affordability** | `nfhs_insurance_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_oope_delivery_rs` | POSITIVE | NFHS-5 Factsheet | INR ($\text{Rs.}$) |
| | `nfhs_clean_fuel_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| | `nfhs_sanitation_pct` | POSITIVE | NFHS-5 Factsheet | Percentage ($\%$) |
| **P5: Corporate Saturation Proxy** | `mca21_pharma_density_per_100k` | NEGATIVE (Cost) | Calibrated Proxy | Count per 100k pop |
| **P6: Medicine Availability** | `jan_aushadhi_density_per_100k` | POSITIVE | PMBJP State PDFs | Count per 100k pop |
| **P7: Growth & Policy Momentum** | `niti_aspirational_district_flag` | POSITIVE | NITI Aayog Registry | Binary $[0, 1]$ |
| | `census_decadal_growth_pct` | POSITIVE | Census 2011 PCA | Percentage ($\%$) |

---

## 3. DLMAI v2.0 Mathematical Formulation

### 1. Normalization (Direction-Aware Min-Max):
$$\tilde{x}_{ij} = \begin{cases}
\dfrac{x_{ij} - \min(x_j)}{\max(x_j) - \min(x_j)} \times 100, & \text{Positive (Benefit)} \\[8pt]
\dfrac{\max(x_j) - x_{ij}}{\max(x_j) - \min(x_j)} \times 100, & \text{Negative (Cost)}
\end{cases}$$

### 2. Intra-Pillar Shannon Entropy Weights:
$$p_{ij} = \frac{\tilde{x}_{ij} + \epsilon}{\sum_{k=1}^N (\tilde{x}_{kj} + \epsilon)}, \quad e_j = -\frac{1}{\ln(N)} \sum_{i=1}^N p_{ij} \ln(p_{ij}), \quad w_j = \frac{1 - e_j}{\sum_k (1 - e_k)}$$

### 3. Inter-Pillar Saaty AHP Weights:
The $7 \times 7$ pairwise comparison matrix yielded principal eigenvalue $\lambda_{\max} = 7.121565$ and Consistency Ratio $\text{CR} = 0.015349 < 0.10$.
Re-normalized positive value driver weights (excluding P5):
$$\mathbf{W}_{\text{driver}} = \{\text{P1}: 0.3664, \text{P3}: 0.2468, \text{P2}: 0.1618, \text{P4}: 0.1039, \text{P6}: 0.0606, \text{P7}: 0.0606\}$$

### 4. Composite DLMAI Score:
$$V_i = \sum_{p \ne \text{P5}} W_p P_{ip}, \quad C_i = \lambda \cdot P_{i,\text{P5}} \quad (\lambda = 0.15)$$
$$\text{DLMAI}_i = V_i - C_i$$

---

## 4. Frozen v2.0 Baseline Performance & Validation Metrics

- **Total Districts Scored:** 148
- **Mean DLMAI Score:** 47.45 (Median: 47.88, Min: 24.46, Max: 56.17)
- **Top Scoring District:** Hyderabad, Telangana (56.17, Rank 1)
- **Lowest Scoring District:** Adilabad, Telangana (24.46, Rank 148)
- **Monte Carlo Rank Stability ($N=1,000$):** Mean Spearman $\rho = 0.9922$
- **Enterprise Quality Gates:** 15 / 15 Passed
- **Automated Tests:** 39 / 39 Pytest Assertions Passed (100%)
