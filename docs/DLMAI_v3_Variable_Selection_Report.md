# DLMAI v3.0 — Variable Selection, Statistical Redundancy & Catalog Report

**Document ID:** DLMAI-DOC-v3-07  
**Classification:** Statistical Feature Engineering & Redundancy Audit  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Variable Selection Methodology

Candidate variables were evaluated across six statistical and conceptual criteria:
1. **Conceptual Alignment:** Direct relevance to pharmaceutical market attractiveness.
2. **Observational Authenticity:** High proportion of directly observed or legitimate lineage-inherited data ($>80\%$).
3. **Information Entropy / Variance:** Sufficient non-zero spatial variation across districts (low information degeneracy).
4. **Multicollinearity & Redundancy:** Pairwise Pearson correlation $r < 0.85$ and Variance Inflation Factor (VIF) $< 5.0$.
5. **Domain Validity:** Stable numerical boundaries with verified positive or cost directionality.
6. **Zero Leakage:** Complete independence from target sales benchmarks and composite score formulas.

---

## 2. Redundancy & Collinearity Audit

| Candidate Variable Pair | Pearson $r$ | Spearman $\rho$ | Collinearity Risk | Selection Decision & Justification |
|---|---|---|---|---|
| `stunting_pct` vs `underweight_pct` | **0.884** | **0.862** | **HIGH** | **DROP `underweight_pct`**: Stunting is a cleaner, height-for-age chronic indicator that does not fluctuate with temporary hydration. |
| `wasting_pct` vs `underweight_pct` | 0.792 | 0.771 | **MODERATE** | **DROP `underweight_pct`**: Eliminates composite collinearity between acute and chronic malnutrition metrics. |
| `clean_fuel_pct` vs `sanitation_pct` | 0.765 | 0.781 | **MODERATE** | **RETAIN BOTH**: Measure distinct socioeconomic dimensions (indoor air pollution vs. water/sanitation hygiene). |
| `total_population` vs `urban_population_pct` | 0.412 | 0.435 | **LOW** | **RETAIN BOTH**: Capture distinct volume scale vs. spatial density dimensions. |
| `phc_density` vs `subcentre_density` | 0.684 | 0.651 | **LOW_MODERATE** | **RETAIN BOTH**: Primary care clinics (with medical officers) vs. grassroots sub-centres (with ANMs/ASHAs). |

---

## 3. Final Scored Variable Catalog (20 Verified Indicators)

```
[PILLAR 1: HEALTHCARE NEED & DISEASE BURDEN] (Entropy Weighted)
  1. nfhs_hypertension_combined_pct  (Positive, NFHS-5) -> Chronic adult cardiovascular burden
  2. nfhs_diabetes_combined_pct      (Positive, NFHS-5) -> Chronic adult metabolic burden
  3. nfhs_stunting_pct               (Positive, NFHS-5) -> Chronic pediatric nutritional deficit
  4. nfhs_wasting_pct                (Positive, NFHS-5) -> Acute pediatric nutritional deficit

[PILLAR 2: DEMOGRAPHIC MARKET POTENTIAL] (Entropy Weighted)
  5. census_total_population         (Positive, Census/PCA) -> Total addressable patient pool
  6. census_urban_population_pct     (Positive, Census/PCA) -> Urban clinic & pharmacy concentration
  7. census_population_age_0_6_pct   (Positive, Census/PCA) -> Pediatric demographic segment

[PILLAR 3: HEALTHCARE ACCESS & CLINICAL CAPACITY] (Entropy Weighted)
  8. rhs_phc_density_per_100k        (Positive, RHS) -> Primary medical consultation density
  9. rhs_chc_density_per_100k        (Positive, RHS) -> Secondary specialist inpatient facility density
 10. rhs_subcentre_density_per_100k  (Positive, RHS) -> Grassroots primary care delivery density
 11. rhs_hospital_presence           (Positive, RHS) -> District / Sub-district hospital flag

[PILLAR 4: HEALTHCARE UTILIZATION] (Entropy Weighted)
 12. nfhs_institutional_births_pct   (Positive, NFHS-5) -> Formal medical facility delivery adherence
 13. nfhs_antenatal_care_4_visits_pct(Positive, NFHS-5) -> Preventive clinical consultation adherence

[PILLAR 5: ECONOMIC AFFORDABILITY & PURCHASING POWER] (Entropy Weighted)
 14. nfhs_insurance_pct              (Positive, NFHS-5) -> Household health insurance risk pooling
 15. nfhs_oope_delivery_rs           (Positive, NFHS-5) -> Private out-of-pocket spending capacity
 16. nfhs_clean_fuel_pct             (Positive, NFHS-5) -> Household disposable living standard proxy
 17. nfhs_sanitation_pct             (Positive, NFHS-5) -> Household structural living standard proxy

[PILLAR 6: MEDICINE AVAILABILITY & RETAIL CHANNELS] (Entropy Weighted)
 18. jan_aushadhi_density_per_100k   (Positive, PMBJP) -> Active generic retail pharmacy density

[PILLAR 7: PHARMACEUTICAL CORPORATE CONCENTRATION] (Entropy Weighted)
 19. mca21_pharma_density_per_100k   (Positive/Sat, MCA21) -> Active pharma corporate & manufacturing units

[PILLAR 8: MARKET EXPANSION & POLICY MOMENTUM] (Entropy Weighted)
 20. niti_aspirational_district_flag (Positive, NITI) -> High-priority government development focus
```
