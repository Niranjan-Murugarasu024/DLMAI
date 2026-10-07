# South India District-Level Market Attractiveness Index (DLMAI)
## Comprehensive Indicator Data Dictionary (Version 2.0.0)

**Document Version:** 2.0.0 (Post-Audit Reconciled)  
**Scope:** South India (Tamil Nadu, Kerala, Karnataka, Andhra Pradesh, Telangana, Goa, Puducherry)  
**Total Canonical Districts:** 148 Districts  
**Total Scored Core Indicators:** **20 Indicators** across 7 Framework Pillars  
**Auxiliary Market Scale Variables:** 5 Non-Scored Descriptive Variables  

---

## 1. Pillar Overview & Composition Matrix

| Pillar Code | Pillar Name | Primary Focus | Scored Indicators | AHP Priority Weight ($w_p$) | Re-normalized Driver Weight ($w'_p$) | Role in Model |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **P1** | Healthcare Demand & Disease Burden | Epidemiology, chronic non-communicable diseases (hypertension, diabetes), child nutrition, demographic base | 7 | 35.41% | 36.64% | **Value Driver** (+) |
| **P2** | Economic Access & Affordability | Health insurance coverage, household living standards, out-of-pocket delivery costs | 4 | 15.63% | 16.18% | **Value Driver** (+) |
| **P3** | Healthcare Infrastructure | Primary Health Centres, Community Health Centres, Sub-Divisional & District Hospitals | 4 | 23.86% | 24.68% | **Value Driver** (+) |
| **P4** | Pharmaceutical Distribution Accessibility | Jan Aushadhi generic pharmacy density per 100k population | 1 | 10.04% | 10.39% | **Value Driver** (+) |
| **P5** | Market Competition & Saturation | Active pharmaceutical manufacturing & corporate enterprise density per 100k population | 1 | 3.35% | — | **Value Dampener** (−) |
| **P6** | Policy & Healthcare Development Environment | NITI Aayog Aspirational District priority development status | 1 | 5.85% | 6.06% | **Value Driver** (+) |
| **P7** | Demographic & Market Growth | Population decadal growth rate, district literacy rate | 2 | 5.85% | 6.06% | **Value Driver** (+) |
| **TOTAL** | — | — | **20** | **100.00%** | **100.00%** | — |

---

## 2. Core Scored Indicators (20 Core Indicators)

### PILLAR 1: Healthcare Demand & Disease Burden (7 Indicators)

#### 1. `nfhs_hypertension_combined_pct`
- **Name:** Adult Hypertension Prevalence Rate (%)
- **Definition:** Percentage of women and men (age 15+ years) with elevated blood pressure (Systolic $\ge 140$ mmHg and/or Diastolic $\ge 90$ mmHg) or currently taking medication to control blood pressure.
- **Source:** NFHS-5 (2019–2021), District Factsheets, Table "Hypertension among Adults".
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Derived Formula:** $\frac{\text{Hypertension}_{\text{women}} + \text{Hypertension}_{\text{men}}}{2}$
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** Same-district trend (NFHS-4) $\to$ State Mean $\to$ kNN Covariate.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Core volume driver for chronic cardiovascular therapy portfolios (ARBs, CCBs, Beta-blockers, Statins).

#### 2. `nfhs_diabetes_combined_pct`
- **Name:** Adult Diabetes Prevalence Rate (%)
- **Definition:** Percentage of women and men (age 15+ years) with blood sugar level high/very high ($> 140$ mg/dl) or currently taking medication to control blood sugar.
- **Source:** NFHS-5 (2019–2021), District Factsheets, Table "Blood Sugar Level among Adults".
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Derived Formula:** $\frac{\text{Diabetes}_{\text{women}} + \text{Diabetes}_{\text{men}}}{2}$
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** Same-district trend (NFHS-4) $\to$ State Mean $\to$ kNN Covariate.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** South India has the highest adult diabetes prevalence in India. Direct driver of oral hypoglycemics (Metformin, DPP4i, SGLT2i) and insulin.

#### 3. `nfhs_stunting_pct`
- **Name:** Child Stunting Rate (Height-for-Age) (%)
- **Definition:** Percentage of children under 5 years who are stunted (height-for-age below $-2$ SD from WHO child growth standards median).
- **Source:** NFHS-5 (2019–2021), Line 73.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE (Pediatric Need)**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** State Mean $\to$ kNN Covariate.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Pediatric nutritional therapies, micronutrients, growth supplements.

#### 4. `nfhs_wasting_pct`
- **Name:** Child Wasting Rate (Weight-for-Height) (%)
- **Definition:** Percentage of children under 5 years who are wasted (weight-for-height below $-2$ SD).
- **Source:** NFHS-5 (2019–2021), Line 74.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** State Mean $\to$ kNN.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 5. `nfhs_underweight_pct`
- **Name:** Child Underweight Rate (Weight-for-Age) (%)
- **Definition:** Percentage of children under 5 years who are underweight (weight-for-age below $-2$ SD).
- **Source:** NFHS-5 (2019–2021), Line 76.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** State Mean $\to$ kNN.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 6. `census_urban_population_pct`
- **Name:** Urban Population Share (%)
- **Definition:** Percentage of district population residing in urban statutory towns/corporations.
- **Source:** Census of India (District PCA).
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Urbanization correlates with lifestyle diseases and higher willingness-to-pay for premium branded formulations.

#### 7. `census_population_age_0_6_pct`
- **Name:** Pediatric Population Share (Age 0–6) (%)
- **Definition:** Percentage of total population in the 0–6 age cohort.
- **Source:** Census of India.
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P1 (Demand & Disease Burden)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

---

### PILLAR 2: Economic Access & Affordability (4 Indicators)

#### 8. `nfhs_insurance_pct`
- **Name:** Health Insurance / Financing Scheme Coverage (%)
- **Definition:** Percentage of households with at least one member covered under health insurance or public health scheme (e.g. CMCHIS, Aarogyasri, PMJAY).
- **Source:** NFHS-5 (2019–2021), Line 12.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P2 (Economic Access & Affordability)
- **Missingness Strategy:** State Mean $\to$ kNN.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Increases inpatient admissions and hospital-dispensed drug therapy compliance.

#### 9. `nfhs_clean_fuel_pct`
- **Name:** Household Clean Fuel for Cooking (%)
- **Definition:** Percentage of households using clean cooking fuel (LPG, electricity, biogas).
- **Source:** NFHS-5 (2019–2021), Line 10.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P2 (Economic Access & Affordability)
- **Missingness Strategy:** State Mean $\to$ kNN.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Robust proxy for household disposable income and economic wellbeing.

#### 10. `nfhs_sanitation_pct`
- **Name:** Improved Sanitation Facility Usage (%)
- **Definition:** Percentage of population living in households using improved sanitation.
- **Source:** NFHS-5 (2019–2021), Line 9.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P2 (Economic Access & Affordability)
- **Missingness Strategy:** State Mean $\to$ kNN.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 11. `nfhs_oope_delivery_rs`
- **Name:** Out-of-Pocket Expenditure per Delivery (INR)
- **Definition:** Average out-of-pocket expenditure (Rs.) incurred per institutional delivery in a public healthcare facility.
- **Source:** NFHS-5 (2019–2021), Line 39.
- **Vintage / Level:** 2019–2021 | District
- **Unit:** Indian Rupees (INR)
- **Direction:** **NEGATIVE**
- **Pillar:** P2 (Economic Access & Affordability)
- **Missingness Strategy:** Trend (NFHS-4) $\to$ State Mean.
- **Normalization:** Inverted Min-Max: $\frac{\max(X) - X}{\max(X) - \min(X)} \times 100$.
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** High out-of-pocket expenditure indicates medical financial distress and lower commercial liquidity.

---

### PILLAR 3: Healthcare Infrastructure (4 Indicators)

#### 12. `rhs_phc_density_per_100k`
- **Name:** Primary Health Centres (PHCs) per 100,000 Population
- **Definition:** Total operational PHCs divided by district population (in 100k).
- **Source:** MoHFW Rural Health Statistics (RHS).
- **Vintage / Level:** 2011 Baseline / RHS Current | District
- **Unit:** Number per 100k population
- **Direction:** **POSITIVE**
- **Pillar:** P3 (Healthcare Infrastructure)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean $\to$ Urban peer proxy.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 13. `rhs_chc_density_per_100k`
- **Name:** Community Health Centres (CHCs) per 100,000 Population
- **Definition:** Total 30-bed secondary CHCs divided by district population (in 100k).
- **Source:** MoHFW RHS.
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Number per 100k population
- **Direction:** **POSITIVE**
- **Pillar:** P3 (Healthcare Infrastructure)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 14. `rhs_subcentre_density_per_100k`
- **Name:** Health Sub-Centres per 100,000 Population
- **Definition:** Grassroots health sub-centres per 100,000 population.
- **Source:** MoHFW RHS.
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Number per 100k population
- **Direction:** **POSITIVE**
- **Pillar:** P3 (Healthcare Infrastructure)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

#### 15. `rhs_hospital_presence`
- **Name:** Secondary & Tertiary Public Hospital Presence (Count)
- **Definition:** Count of Sub-Divisional Hospitals plus District Hospitals in the district.
- **Source:** MoHFW RHS.
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Count (Integer)
- **Direction:** **POSITIVE**
- **Pillar:** P3 (Healthcare Infrastructure)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.

---

### PILLAR 4: Pharmaceutical Distribution Accessibility (1 Indicator)

#### 16. `jan_aushadhi_density_per_100k`
- **Name:** Jan Aushadhi Kendras per 100,000 Population
- **Definition:** Deduplicated active Pradhan Mantri Jan Aushadhi generic retail pharmacies per 100k population.
- **Source:** PMBI Registry (`janaushadhi.gov.in`).
- **Vintage / Level:** 2023–2024 | District (via LGD Crosswalk)
- **Unit:** Outlets per 100k population
- **Direction:** **POSITIVE**
- **Pillar:** P4 (Pharmaceutical Distribution Accessibility)
- **Missingness Strategy:** Verified deduplication $\to$ 0 for confirmed absence.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Single indicator in pillar ($w = 1.0$).
- **Business Rationale:** Evaluates formal retail pharmacy network penetration and consumer generic acceptance.

---

### PILLAR 5: Market Competition & Saturation (1 Value Dampener Indicator)

#### 17. `mca21_pharma_density_per_100k`
- **Name:** Active Pharmaceutical Enterprises per 100,000 Population
- **Definition:** Active corporate entities registered under NIC-2008 pharma manufacture codes (21001, 21002, 21009) per 100k population.
- **Source:** Ministry of Corporate Affairs (MCA21 Master Database).
- **Vintage / Level:** 2021–2024 | District (via Pincode mapping)
- **Unit:** Enterprises per 100k population
- **Direction:** **SATURATION_DAMPENER**
- **Pillar:** P5 (Market Competition & Saturation)
- **Role in Model:** **Value Dampener** ($\lambda = 0.15$). High local pharma corporate concentration represents intense field competition, generic discounting, and crowded prescriber channels. Subtracted from positive value drivers.
- **Missingness Strategy:** Pincode mapping $\to$ State Mean for unmapped rural.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Inter-pillar Dampener Coefficient ($\lambda = 0.15$).

---

### PILLAR 6: Policy & Healthcare Development Environment (1 Indicator)

#### 18. `niti_aspirational_district_flag`
- **Name:** NITI Aayog Aspirational District Priority Status (0 / 1)
- **Definition:** Binary indicator where 1 denotes selection under Government of India's Aspirational Districts Programme (ADP).
- **Source:** NITI Aayog Official Registry.
- **Vintage / Level:** Current | District
- **Unit:** Binary $\{0, 1\}$
- **Direction:** **POSITIVE**
- **Pillar:** P6 (Policy & Healthcare Development Environment)
- **Missingness Strategy:** Exhaustive national list (absence is a confirmed 0).
- **Normalization:** Binary $\{0 \to 0.0, 1 \to 100.0\}$.
- **Weighting:** Single indicator in pillar ($w = 1.0$).
- **Business Rationale:** Prioritized for state health budgets, CSR fund allocations, PMJAY hospital empanelment, and accelerated medical procurement.

---

### PILLAR 7: Demographic & Market Growth (2 Indicators)

#### 19. `census_decadal_growth_pct`
- **Name:** Population Decadal Growth Rate (%)
- **Definition:** Percentage intercensal population growth over 2001–2011.
- **Source:** Census of India.
- **Vintage / Level:** 2001–2011 Baseline | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P7 (Demographic & Market Growth)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Demographic expansion drives long-term pharmaceutical volume baseline.

#### 20. `census_literacy_rate_pct`
- **Name:** District Literacy Rate (%)
- **Definition:** Percentage of population age 7+ who can read and write.
- **Source:** Census of India.
- **Vintage / Level:** 2011 Baseline | District
- **Unit:** Percentage (%)
- **Direction:** **POSITIVE**
- **Pillar:** P7 (Demographic & Market Growth)
- **Missingness Strategy:** Parent inheritance $\to$ State Mean.
- **Normalization:** Min-Max ($[0, 100]$).
- **Weighting:** Intra-pillar Shannon Entropy Weight.
- **Business Rationale:** Patient health awareness, doctor prescription adherence, self-care medication literacy.

---

## 3. Auxiliary Market Scale Variables (Non-Scored)

1. `census_total_population`: Absolute district population (millions). Essential denominator covariate for nearest-neighbor matching and territory sizing.
2. `jan_aushadhi_raw_count`: Total count of Kendras. Descriptive commercial retail footprint.
3. `mca21_raw_company_count`: Total registered pharma enterprises. Descriptive corporate presence.
4. `census_density_per_sqkm`: Population density per square kilometer. Retail distribution route efficiency proxy.
5. `census_sex_ratio`: Females per 1,000 males. Demographic profiling covariate.

---
*Data Dictionary Complete. Documented in `docs/South_India_DLMAI_Data_Dictionary.md`.*
