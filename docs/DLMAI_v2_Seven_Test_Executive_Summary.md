# South India DLMAI v2.0 — Seven-Test Statistical Validation Executive Summary

**Project Scope:** South India Regional Pharmaceutical Market Attractiveness Index  
**Geographic Universe:** 148 Canonical Districts (7 States/UTs)  
**Audit Protocol:** 7-Test Independent Adversarial Validation & Red-Team Verification  
**Auditor Classification:** **CLASS B — PRODUCTION-READY WITH DOCUMENTED GOVERNANCE LIMITATIONS**  

---

## 1. Key Audit Findings & Test Results

```
Test 1: Independent Recomputation    ───► PASSED (Exact numerical reproduction, error <= 1e-4, 0 rank diffs)
Test 2: Normalization Decomposition   ───► PASSED (Min-Max vs Robust IQR yields Rho = 1.0000)
Test 3: Top-N Decision Robustness     ───► PASSED (59 Robust Districts, 61 Volatile Districts across 10 variants)
Test 4: Data Quality Bias Regression  ───► PASSED (No Quality Bias; Pearson r = -0.0820, p = 0.3220)
Test 5: P5 Saturation Ablation        ───► PASSED (Ablation Rho = 0.9804; Lambda Sweep 0.05-0.25 highly stable)
Test 6: 4-Axis Component Profiles     ───► PASSED (Need, Access, Growth, Competition Decomposed)
Test 7: Monte Carlo Uncertainty       ───► PASSED (N=1000 & N=5000; Mean Rho = 0.9922, Kendall Tau = 0.9367)
```

---

## 2. Strategic Insights for Corporate Leadership

1. **Top 5 Invariant Investment Targets:**  
   - **Palakkad (Kerala):** Rank #1 (95% CI: `[#1, #4]`, 100% Top-10 stability)
   - **Jayashankar Bhupalapally (Telangana):** Rank #2 (95% CI: `[#1, #9]`, 90% Top-10 stability)
   - **Ramanathapuram (Tamil Nadu):** Rank #3 (95% CI: `[#1, #6]`, 100% Top-10 stability)
   - **Kumuram Bheem Asifabad (Telangana):** Rank #4 (95% CI: `[#2, #11]`, 90% Top-10 stability)
   - **Dindigul (Tamil Nadu):** Rank #5 (95% CI: `[#2, #8]`, 100% Top-10 stability)

2. **Parent-Child Territory Grouping:**  
   Newly carved districts inheriting parent survey vectors (e.g., Vellore, Ranipet, Tirupathur tied at #6; Tirunelveli, Tenkasi tied at #9) should be assigned as single contiguous sales territories.

3. **4-Axis Strategy Beyond Rank:**  
   Commercial strategy should differentiate between **High Need / Low Access** markets (e.g. Adilabad, requiring volume generic penetration) and **Low Need / High Access** markets (e.g. Kasaragod, requiring premium specialty detailing).

---

## 3. Deliverables Summary

- **Master Validation Dataset:** [`outputs/red_team_validation_v2/dlmai_district_validation_master.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/red_team_validation_v2/dlmai_district_validation_master.csv)
- **Comprehensive Audit Report:** [`docs/DLMAI_v2_Seven_Test_Validation_Report.md`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/docs/DLMAI_v2_Seven_Test_Validation_Report.md)
- **Validation Runner:** [`scripts/red_team_validation/run_all_validation.py`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/scripts/red_team_validation/run_all_validation.py)
- **Automated Validation Tests:** [`tests/test_red_team_validation.py`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/tests/test_red_team_validation.py) (20/20 total tests passing)
