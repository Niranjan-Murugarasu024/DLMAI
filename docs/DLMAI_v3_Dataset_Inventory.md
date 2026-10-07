# DLMAI v3.0 — Complete Dataset Inventory & Technical Schema Catalog

**Document ID:** DLMAI-DOC-v3-02  
**Classification:** Technical Data Catalog  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Inventory Summary

This catalog documents all 10 discovered datasets in the repository, including physical storage paths, formats, schemas, source organizations, and production usability classifications.

---

## 2. Comprehensive Dataset Catalog

### 1. Local Government Directory (LGD) Master South India
- **Dataset ID:** `DS_01_LGD_MASTER`
- **File Path:** [`data/master/lgd_south_india.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/data/master/lgd_south_india.csv)
- **Format / Size:** CSV | 10.5 KB | 148 rows | 5 columns
- **Source Authority:** Ministry of Panchayati Raj (MoPR), Government of India
- **Schema:**
  - `lgd_district_code` (int): Unique LGD primary key (501 to 755).
  - `district_name` (str): Official administrative name.
  - `state_lgd_code` (int): State code (28, 29, 30, 32, 33, 34, 36).
  - `state_name` (str): State name.
  - `census_2011_code` (int): Matching Census 2011 district code.
- **Role in Model:** **Universal Geographic Reference (Single Source of Truth)**

---

### 2. South India District Crosswalk & Lineage Registry
- **Dataset ID:** `DS_02_CROSSWALK`
- **File Path:** [`data/master/district_crosswalk_south.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/data/master/district_crosswalk_south.csv)
- **Format / Size:** CSV | 16.4 KB | 186 rows | 9 columns
- **Source Authority:** Internal Harmonization Engine / Survey Alignment Master
- **Schema:**
  - `source_district_name` (str): Raw district alias / historical spelling.
  - `source_state` (str): State hint.
  - `canonical_lgd_code` (int): Target LGD code.
  - `canonical_district_name` (str): Official standard name.
  - `mapping_type` (str): `EXACT`, `ALIAS`, `SPLIT_CHILD`.
  - `parent_district_name` (str): Parent district name if split.
  - `parent_lgd_code` (float/int): Parent LGD code.
  - `confidence` (str): `HIGH`, `VERIFIED`.
- **Role in Model:** **Harmonization & Fixed-Point Lineage Inheritance Engine**

---

### 3. National Family Health Survey (NFHS-5) District Factsheets
- **Dataset ID:** `DS_03_NFHS5_DISTRICT`
- **File Path:** `data/nfhs/district/*/*.pdf`
- **Format / Size:** 124 PDF Files | 74.5 MB Total | 104 Standard Indicators per PDF
- **Source Authority:** Ministry of Health and Family Welfare (MoHFW) / IIPS Mumbai
- **Schema & Indicators Extracted:**
  - `hypertension_combined_pct`: Blood pressure $\ge 140/90\text{ mmHg}$ or taking anti-hypertensive medication.
  - `diabetes_combined_pct`: Blood glucose $>140\text{ mg/dl}$ or taking diabetes medication.
  - `stunting_pct`: Children under 5 years whose height-for-age is below $-2\text{ SD}$.
  - `wasting_pct`: Children under 5 years whose weight-for-height is below $-2\text{ SD}$.
  - `underweight_pct`: Children under 5 years whose weight-for-age is below $-2\text{ SD}$.
  - `clean_fuel_pct`: Households using clean fuel for cooking.
  - `sanitation_pct`: Households using improved sanitation facility.
  - `insurance_pct`: Households with at least one member covered under health insurance/scheme.
  - `oope_delivery_rs`: Average out-of-pocket expenditure per delivery in public health facility (INR).
- **Role in Model:** **P1 Healthcare Need & P5 Economic Affordability Core**

---

### 4. NFHS-5 State & Union Territory Factsheets
- **Dataset ID:** `DS_04_NFHS5_STATE`
- **File Path:** `data/nfhs/state/*.pdf`
- **Format / Size:** 7 PDF Files | 5.5 MB Total
- **Source Authority:** MoHFW / IIPS Mumbai
- **Role in Model:** **Hierarchical Layer-2 Imputation Anchor & State Macro Baselines**

---

### 5. Rural Health Statistics (RHS) Table 2021-22
- **Dataset ID:** `DS_05_RHS_HEALTHCARE`
- **File Path:** [`data/rhs/district-wise-health-centres.pdf`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/data/rhs/district-wise-health-centres.pdf)
- **Format / Size:** PDF Table | 449.7 KB | 97 Mapped Districts | 5 Columns
- **Source Authority:** Ministry of Health and Family Welfare (MoHFW)
- **Schema:**
  - `sub_centres` (int): Operational health sub-centres.
  - `phcs` (int): Primary Health Centres.
  - `chcs` (int): Community Health Centres.
  - `hospital_presence` (int): Sub-district & district hospital counts.
- **Role in Model:** **P3 Healthcare Access & Inpatient Capacity Core**

---

### 6. PMBJP Jan Aushadhi Kendra Registry
- **Dataset ID:** `DS_06_JAN_AUSHADHI`
- **File Path:** `data/jan_aushadhi/*.pdf`
- **Format / Size:** 9 PDF Files | 1.82 MB | 7,422 Records (5,926 South India)
- **Source Authority:** Pharmaceuticals & Medical Devices Bureau of India (PMBI)
- **Schema:**
  - `kendra_code` (str): Unique PMBJP outlet identifier.
  - `kendra_name` (str): Name of the retail shop.
  - `state` (str): State location.
  - `district` (str): District location.
  - `address` (str): Street address.
  - `pincode` (str): 6-digit postal code.
- **Role in Model:** **P6 Medicine Availability & Generic Retail Access Point Core**

---

### 7. Ministry of Corporate Affairs (MCA21) Company Master Registry
- **Dataset ID:** `DS_07_MCA21_CORPORATE`
- **File Path:** `data/mca21/*.csv` (7 Files)
- **Format / Size:** CSV | 142.1 MB | **943,267 Records** | 16 Columns
- **Source Authority:** Ministry of Corporate Affairs (MCA), Government of India
- **Schema:**
  - `CIN`: Corporate Identification Number.
  - `CompanyName`: Registered legal company name.
  - `CompanyROCcode`: ROC jurisdiction.
  - `CompanyCategory` / `CompanyClass`: Classification.
  - `AuthorizedCapital` / `PaidupCapital`: Financial equity scale.
  - `Registered_Office_Address`: Full street address, city, district, state, PIN code.
  - `CompanyStatus`: Active, Strike Off, Liquidation.
  - `nic_code`: National Industrial Classification (NIC 2100 = Manufacture of pharmaceuticals).
- **Role in Model:** **P7 Pharmaceutical Corporate & Manufacturing Concentration Core**

---

### 8. Census 2011 Primary Census Abstract (PCA)
- **Dataset ID:** `DS_08_CENSUS_PCA`
- **File Path:** [`data/census/primary_census_abstract/PCA_district_level.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/data/census/primary_census_abstract/PCA_district_level.csv)
- **Format / Size:** CSV | 158.2 KB | 108 Rows | 98 Columns
- **Source Authority:** Office of the Registrar General & Census Commissioner (RGI)
- **Schema Highlights:**
  - `Total Population Person` / `Male` / `Female`
  - `Population in the age group 0-6 Person`
  - `Literates Population Person`
  - `Total Worker Population Person`
  - `Main Working Population Person`
  - `Non Working Population Person`
- **Role in Model:** **P2 Demographic Market Potential & Population Denominators**

---

### 9. Socio Economic and Caste Census (SECC 2011)
- **Dataset ID:** `DS_09_SECC_SOCIOECONOMIC`
- **File Path:** [`data/secc/Socio Economic and Caste Census (SECC).csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/data/secc/Socio%20Economic%20and%20Caste%20Census%20(SECC).csv)
- **Format / Size:** CSV | 19.5 KB | 34 Rows | 60 Columns
- **Source Authority:** Ministry of Rural Development (MoRD)
- **Role in Model:** **Macro State Socioeconomic Benchmarking & Living Standard Validation**

---

### 10. NITI Aayog Aspirational Districts Programme
- **Dataset ID:** `DS_10_NITI_ASPIRATIONAL`
- **File Path:** `data/niti_aayog/README.txt`
- **Format / Size:** Registry / Text | 112 National Districts (13 South India)
- **Source Authority:** NITI Aayog, Government of India
- **Role in Model:** **P8 Market Expansion & Policy Priority Driver**
