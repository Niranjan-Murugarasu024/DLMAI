# DLMAI v3.0 — MCA21 Bulk Corporate Registry Forensic Analysis & Pharmaceutical Classification Report

**Document ID:** DLMAI-DOC-v3-MCA21  
**Classification:** Corporate Registry Data Engineering & Algorithmic Classification  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Executive Summary

This forensic report documents the complete processing of **943,267 company records** across the 7 South Indian state/UT CSV files in `data/mca21/`. By implementing a 5-tier classification hierarchy combining **National Industrial Classification (NIC 2100)** codes, normalized corporate names, active status checks, and deterministic postal PIN/address spatial resolution, the pipeline identified **28,909 verified pharmaceutical entities** and mapped them across all 148 canonical LGD districts.

---

## 2. Classification Hierarchy & Filtering Rules

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MCA21 PHARMACEUTICAL CLASSIFICATION TREE                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: DIRECT_NIC_PHARMA_MANUFACTURER (11,170 Records)                                │
│   - NIC Code starts with '2100', '210', '211', '212', '2423'                           │
│   - Activity: Manufacture of pharmaceuticals, medicinal chemicals & botanical products │
│                                                                                        │
│ TIER 2: PHARMA_RELATED_MANUFACTURER (4,312 Records)                                    │
│   - NIC Code starts with '20' (Chemicals), '266' (Electro-medical), '325' (Medical)   │
│   - AND Corporate name contains verified pharmaceutical / drug keywords                │
│                                                                                        │
│ TIER 3: PHARMA_CORPORATE_ENTITY (8,825 Records)                                        │
│   - Corporate Name contains 'PHARMACEUTICAL', 'PHARMA', 'DRUG', 'MEDICINE', 'BIOTECH', │
│     'FORMULATION', 'LABORATORIES', 'APIS', 'THERAPEUTIC', 'LIFE SCIENCES'              │
│                                                                                        │
│ TIER 4: NAME_BASED_MATCH (4,602 Records)                                               │
│   - Name contains 'HEALTHCARE', 'AYURVED', 'HERBAL', 'DIAGNOSTIC'                      │
│                                                                                        │
│ EXCLUDED (914,358 Records)                                                             │
│   - Non-pharmaceutical entities (IT, construction, agriculture, finance, textiles, etc)│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. State-by-State Forensic Extraction Summary

| State / Territory | Total Companies Scanned | Active Companies | Direct NIC Pharma Manufacturers | Total Pharma Entities | Pharma Paid-up Capital (INR Cr) |
|---|---|---|---|---|---|
| **Telangana** | 219,893 | 184,210 | 4,465 | 9,842 | 48,210.5 |
| **Karnataka** | 258,323 | 218,940 | 1,840 | 7,120 | 32,450.8 |
| **Tamil Nadu** | 251,291 | 209,115 | 2,601 | 6,584 | 29,810.2 |
| **Kerala** | 127,433 | 104,820 | 1,081 | 3,115 | 8,420.5 |
| **Andhra Pradesh** | 65,662 | 54,310 | 907 | 1,820 | 6,110.0 |
| **Goa** | 15,684 | 12,980 | 148 | 254 | 1,850.4 |
| **Puducherry** | 4,981 | 4,112 | 128 | 174 | 640.2 |
| **TOTAL** | **943,267** | **788,487** | **11,170** | **28,909** | **127,492.6** |

---

## 4. Top Pharmaceutical Manufacturing Clusters in South India

Based on empirical MCA21 direct manufacturing density (`direct_pharma_manufacturers` per 100k):
1. **Hyderabad & Medchal-Malkajgiri (Telangana):** Primary national API and formulation hub (over 4,200 active pharma units).
2. **Bengaluru Urban (Karnataka):** Major biotechnology, biopharma, and corporate R&D cluster (over 2,100 active units).
3. **Chennai, Kancheepuram & Tiruvallur (Tamil Nadu):** Major formulation and medical devices hub (over 1,800 active units).
4. **Visakhapatnam (Andhra Pradesh):** Major coastal API and bulk drug manufacturing zone (over 450 active units).
5. **Ernakulam & Thrissur (Kerala):** Ayurvedic, herbal, and formulation manufacturing cluster (over 650 active units).
6. **North Goa & South Goa (Goa):** Export formulation manufacturing hub (over 180 active units).

---

## 5. Output Artifacts

- Sample Classification Table: [`outputs/v3/mca21_company_classification.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/mca21_company_classification.csv)
- District Aggregated Features: [`outputs/v3/mca21_district_features.csv`](file:///e:/DMLIA-Sun%20pharma/dlmai_complete/outputs/v3/mca21_district_features.csv)
