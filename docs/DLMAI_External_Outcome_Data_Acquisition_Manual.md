# DLMAI v3.2 — Independent Pharmaceutical Outcome Data Acquisition Manual

**Document ID:** DLMAI-MANUAL-OUTCOMES-v3.2  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Purpose:** Standard Operating Procedure (SOP) for downloading, cataloging, and installing Layer-3 Independent Pharmaceutical Outcome Datasets (Zero Paid-Data Constraint).  
**Target Schema:** `outputs/external_outcomes/DLMAI_EXTERNAL_OUTCOME_MASTER.csv`  

---

## 1. Target Directory Architecture

Create the following folder hierarchy inside `data/external_outcomes/`:

```
data/external_outcomes/
├── cppp/                           # Central Public Procurement Portal (Tenders & Awards)
├── state_corporations/             # State Medical Services Corporations
│   ├── tnmsc_tamil_nadu/           # Tamil Nadu Medical Services Corp
│   ├── kmscl_kerala/               # Kerala Medical Services Corp Ltd
│   ├── apmsidc_andhra/             # Andhra Pradesh Med Services & Infra Dev Corp
│   ├── tsmsidc_telangana/          # Telangana State Med Services & Infra Dev Corp
│   ├── ksmscl_karnataka/           # Karnataka State Medical Supplies Corp Ltd
│   ├── goa_dhs/                    # Directorate of Health Services, Goa
│   └── puducherry_dhfws/           # Directorate of Health & Family Welfare Puducherry
├── dpdmis_dvdms/                   # Drug Distribution Management & Stock MIS
├── ogd_data_gov/                   # Open Government Data (PMBI sales, medicine catalogue)
├── gem_procurement/                # Government e-Marketplace medicine purchase orders
├── nppa_pmru/                      # NPPA Price Monitoring & Resource Units
├── gst_medicines/                  # State-wise GST on medicines & medical devices
└── dop_annual_reports/             # Department of Pharmaceuticals Therapeutic Sales
```

---

## 2. Step-by-Step Dataset Download & Installation Procedures

---

### 🥇 P0 Priority 1: Central Public Procurement Portal (CPPP) — Medicine Tenders & Awarded Contracts

* **Primary Portal Link:** [CPPP Advanced Tender Search](https://eprocure.gov.in/eprocure/app?page=FrontEndAdvancedSearch&service=page)
* **Alternative e-Publishing Link:** [CPPP e-Publish Tenders](https://eprocure.gov.in/epublish/app)
* **Target Output Directory:** `data/external_outcomes/cppp/`

#### Step-by-Step Retrieval Procedure:
1. Navigate to [CPPP Advanced Search](https://eprocure.gov.in/eprocure/app?page=FrontEndAdvancedSearch&service=page).
2. Set **Tender Category**: `Goods`.
3. Set **Product Category**: `Medicines` / `Drugs and Pharmaceutical Products` / `Medical Equipments/Waste`.
4. In **Tender Title / Description**, query each keyword sequentially:
   - `Procurement of Medicines`
   - `Supply of Essential Drugs`
   - `Tablets / Capsules / Injections / Syrups`
   - `Anti-hypertensive / Anti-diabetic / Antibiotics`
5. Select Target States: `Tamil Nadu`, `Karnataka`, `Kerala`, `Telangana`, `Andhra Pradesh`, `Goa`, `Puducherry`.
6. Click **Search** $\rightarrow$ Click on **Tender Awards / Financial Bid Results**.
7. Export table or download XML/HTML/PDF tender notices containing:
   - Tender ID, Organisation, Item Name, Quantity, Estimated Cost, Awarded Value (INR), Pincode, District, Awardee.
8. Save raw downloads as: `data/external_outcomes/cppp/cppp_tenders_south_india_<YEAR>.csv` or `.pdf`.

---

### 🥇 P0 Priority 2: State Medical Services Corporations (South India 7 States/UTs)

#### 1. Tamil Nadu Medical Services Corporation (TNMSC)
* **Official Portal:** [https://www.tnmsc.tn.gov.in](https://www.tnmsc.tn.gov.in)
* **Tender & Purchase Orders Section:** [TNMSC Tenders & Rate Contracts](https://www.tnmsc.tn.gov.in/tnmsc/html/tenders.php)
* **Target Directory:** `data/external_outcomes/state_corporations/tnmsc_tamil_nadu/`
* **Download Steps:**
  1. Open the portal $\rightarrow$ Navigate to **Tenders / Rate Contracts / Drug Price Lists**.
  2. Download the latest **Approved Drug List with Unit Rate & Annual Requirement Estimates** (PDF/Excel).
  3. Navigate to **District Drug Warehouses** (DDW) to extract district-level allotment quantities.
  4. Save as: `tnmsc_drug_procurement_annual_<YEAR>.pdf` and `tnmsc_district_warehouse_allocations.csv`.

#### 2. Kerala Medical Services Corporation Ltd (KMSCL)
* **Official Portal:** [https://kmscl.kerala.gov.in](https://kmscl.kerala.gov.in)
* **Tender & Rate Contracts:** [KMSCL Tenders & Drug Price Lists](https://kmscl.kerala.gov.in/tenders/)
* **Target Directory:** `data/external_outcomes/state_corporations/kmscl_kerala/`
* **Download Steps:**
  1. Go to **Procurement $\rightarrow$ Drug Rate Contracts $\rightarrow$ Awarded Tenders**.
  2. Download the master **Essential Drug List (EDL) with Approved Supplier Rates & Annual Order Indents**.
  3. Extract district hospital supply allocations across the 14 districts of Kerala.
  4. Save as: `kmscl_rate_contract_drugs_<YEAR>.pdf`.

#### 3. Andhra Pradesh Medical Services & Infrastructure Development Corporation (APMSIDC)
* **Official Portal:** [https://apmsidc.ap.nic.in](https://apmsidc.ap.nic.in)
* **e-Aushadhi / e-Upkaran Portal:** [AP e-Aushadhi Drug Supply System](https://apmsidc.ap.nic.in/eAushadhi/)
* **Target Directory:** `data/external_outcomes/state_corporations/apmsidc_andhra/`
* **Download Steps:**
  1. Open APMSIDC Tenders / e-Aushadhi dashboard.
  2. Access **District Drug Warehouse (DDW) Issue Registers & Hospital Stock Statements**.
  3. Export district-wise distributed medicine quantities.

#### 4. Telangana State Medical Services & Infrastructure Development Corporation (TSMSIDC)
* **Official Portal:** [https://tsmsidc.telangana.gov.in](https://tsmsidc.telangana.gov.in)
* **Target Directory:** `data/external_outcomes/state_corporations/tsmsidc_telangana/`
* **Download Steps:**
  1. Access **Procurement $\rightarrow$ Accepted Drug Tenders & Central Drug Stores (CDS) Indents**.
  2. Download drug allotment schedules across 33 Telangana districts.

#### 5. Karnataka State Medical Supplies Corporation Ltd (KSMSCL)
* **Official Portal:** [https://ksmscl.karnataka.gov.in](https://ksmscl.karnataka.gov.in)
* **Target Directory:** `data/external_outcomes/state_corporations/ksmscl_karnataka/`
* **Download Steps:**
  1. Access **Tenders Awarded $\rightarrow$ Aushada Drug Distribution Management System**.
  2. Export district-wise drug consumption and warehouse issue quantities.

#### 6. Goa Directorate of Health Services & Puducherry DHFWS
* **Goa DHS Portal:** [https://dhsgoa.gov.in](https://dhsgoa.gov.in)
* **Puducherry DHFWS Portal:** [https://health.py.gov.in](https://health.py.gov.in)
* **Target Directory:** `data/external_outcomes/state_corporations/goa_dhs/` and `puducherry_dhfws/`

---

### 🥇 P0 Priority 3: Drug Procurement & Distribution Management MIS (DVDMS / DPDMIS / e-Aushadhi)

* **Reference DPDMIS Portal:** [https://dpdmis.in/DPDMISStock/Public_HomeDrug.aspx](https://dpdmis.in/DPDMISStock/Public_HomeDrug.aspx)
* **MoHFW DVDMS (Drugs and Vaccines Distribution Management System - CDAC):** [https://dvdms.gov.in](https://dvdms.gov.in)
* **Target Directory:** `data/external_outcomes/dpdmis_dvdms/`

#### Step-by-Step Retrieval Procedure:
1. Access the public stock/issue dashboards (such as DPDMIS / DVDMS state portals).
2. Filter by:
   - **State / District**
   - **Facility Type:** District Hospital (DH), Sub-Divisional Hospital (SDH), Community Health Centre (CHC), Primary Health Centre (PHC)
   - **Essential Drug Categories:** Anti-Hypertensive (Amlodipine, Telmisartan), Anti-Diabetic (Metformin, Glimepiride), Antibiotics, Analgesics.
3. Export **Quantity Received, Quantity Issued to Patients, Stock on Hand, Issue Date**.
4. Save as: `dvdms_facility_issue_south_<YEAR>.csv`.

---

### 🥈 P1 Priority 4: Open Government Data (data.gov.in) — PMBI Sales & Medicine Datasets

* **Data.gov.in Medicine Catalog:** [https://www.data.gov.in/keywords/Medicine](https://www.data.gov.in/keywords/Medicine)
* **Year-Wise PMBJP Sales Resource:** [data.gov.in Jan Aushadhi Kendra Sales Details](https://www.data.gov.in/resource/year-wise-details-sales-through-jan-aushadhi-kendras-jaks-and-overall-turnover-pharma)
* **State-Wise PMBI Medicine Sales 2024-25:** [data.gov.in State PMBI Sales Catalog](https://www.data.gov.in/catalog/stateut-wise-sales-medicines-made-pmbi-distributors-and-jan-aushadhi-kendras-during-2024-25)
* **Target Directory:** `data/external_outcomes/ogd_data_gov/`

#### Step-by-Step Download Procedure:
1. Open [data.gov.in/keywords/Medicine](https://www.data.gov.in/keywords/Medicine).
2. Log in with your free data.gov.in account or click direct download on the CSV/XLS resources.
3. Download:
   - `State/UT-wise sales of medicines made by PMBI to distributors and Jan Aushadhi Kendras during 2024-25.csv`
   - `Year-wise details of Sales through Jan Aushadhi Kendras (JAKs) and overall Turnover of Pharma & Medical Bureau of India (PMBI) from 2021-22 to 2023-24.csv`
4. Place files in `data/external_outcomes/ogd_data_gov/`.

---

### 🥈 P1 Priority 5: Government e-Marketplace (GeM) Medicine Procurement Contracts

* **Primary Portal Link:** [https://gem.gov.in](https://gem.gov.in)
* **GeM Public Bid & Contract Search:** [https://bidplus.gem.gov.in/all-bids](https://bidplus.gem.gov.in/all-bids)
* **Target Directory:** `data/external_outcomes/gem_procurement/`

#### Step-by-Step Retrieval Procedure:
1. Navigate to [GeM All Bids / Contracts](https://bidplus.gem.gov.in/all-bids).
2. Filter **Category**: `Pharmaceutical Formulations` / `Drugs` / `Medical Consumables`.
3. Set **Consignee State**: `Tamil Nadu`, `Karnataka`, `Kerala`, `Telangana`, `Andhra Pradesh`, `Goa`, `Puducherry`.
4. Export contract details including: **Contract Number, Buyer Department, Consignee District & Pincode, Item Name, Quantity, Total Contract Value (INR), Award Date**.
5. Save as: `gem_medicine_contracts_south_<YEAR>.csv`.

---

### 🥈 P1 Priority 6: NPPA / PMRU (Price Monitoring & Resource Units)

* **NPPA Official Portal:** [https://nppa.gov.in](https://nppa.gov.in)
* **PMRU Information & Guidelines:** [https://nppa.gov.in/en/pmru](https://nppa.gov.in/en/pmru)
* **Target Directory:** `data/external_outcomes/nppa_pmru/`

#### Step-by-Step Download Procedure:
1. Go to NPPA $\rightarrow$ **PMRU State Reports / Monitoring Studies**.
2. Download published market availability, capped ceiling price adherence, and district price monitoring surveys for South Indian state PMRU cells (e.g. Kerala PMRU, Tamil Nadu PMRU, Karnataka PMRU).
3. Save as: `pmru_state_market_monitoring_<STATE>_<YEAR>.pdf`.

---

### 🥉 P2 Priority 7: State/UT-Wise GST Collected on Medicines

* **Data.gov.in GST Medicine Catalog:** [https://www.data.gov.in/catalog/stateut-wise-gst-collected-medicines-and-medical-goods-2019-20-2023-24](https://www.data.gov.in/catalog/stateut-wise-gst-collected-medicines-and-medical-goods-2019-20-2023-24)
* **Target Directory:** `data/external_outcomes/gst_medicines/`

#### Step-by-Step Download Procedure:
1. Access the dataset on data.gov.in.
2. Download `State/UT-wise GST collected from medicines and medical goods from 2019-20 to 2023-24 (in Rs. Crore).csv`.
3. Save in `data/external_outcomes/gst_medicines/gst_medicines_statewise_2019_2024.csv`.

---

### 🥉 P2 Priority 8: Department of Pharmaceuticals (DoP) Annual Reports & Segment Trends

* **Official Portal:** [https://pharmaceuticals.gov.in](https://pharmaceuticals.gov.in)
* **Annual Reports Section:** [DoP Annual Report 2023-24 (PDF)](https://pharmaceuticals.gov.in/sites/default/files/English%20version%20of%20Annual%20Report%202023-24.pdf)
* **Target Directory:** `data/external_outcomes/dop_annual_reports/`

#### Step-by-Step Download Procedure:
1. Download the latest Annual Report PDF.
2. Extract Chapter 2 & 3: **National Therapeutic Segment Market Shares (Cardiac, Anti-diabetic, Anti-infective, Gastrointestinal, Respiratory, Pain)**.
3. Save as `dop_annual_report_2023_24.pdf`.
