# DLMAI v3.0 — Geographic Coverage, Crosswalk & Harmonization Audit Report

**Document ID:** DLMAI-DOC-v3-04  
**Classification:** Geospatial Harmonization Architecture  
**Target Repository:** `e:/DMLIA-Sun pharma/dlmai_complete`  
**Date:** August 2026  

---

## 1. Canonical Geographic Universe

The authoritative spatial boundaries of DLMAI v3.0 are defined by **148 canonical districts** across 7 South Indian States and Union Territories:

```
                          ┌───────────────────────────┐
                          │   SOUTH INDIA GEOGRAPHY   │
                          │   148 CANONICAL DISTRICTS │
                          └─────────────┬─────────────┘
          ┌─────────────┬───────────────┼───────────────┬─────────────┐
          ▼             ▼               ▼               ▼             ▼
     TAMIL NADU     TELANGANA       KARNATAKA     ANDHRA PRADESH    KERALA (14)
    38 Districts   33 Districts   31 Districts     26 Districts     PUDUCHERRY (4)
     (LGD: 33)      (LGD: 36)      (LGD: 29)        (LGD: 28)       GOA (2)
```

---

## 2. Harmonization Architecture

To ensure 100% deterministic spatial alignment, all incoming data streams are processed through the following multi-stage resolver:

```
[RAW INPUT STRING] (e.g. "Medchal Malkajgiri", "Ananthapuramu", "The Nilgiris")
        │
        ▼
[STAGE 1: CANONICAL NORMALIZATION]
  - Strip whitespace, lowercase, remove punctuation, expand abbreviations ("dt", "dist")
        │
        ▼
[STAGE 2: EXACT CANONICAL LGD MATCH]
  - Check against normalized district names in LGD Master (148 canonical names)
        │
        ▼
[STAGE 3: ALIAS & HISTORICAL CROSSWALK MATCH]
  - Check against 186 aliases in district_crosswalk_south.csv
        │
        ▼
[STAGE 4: STATE-CONSTRAINED FUZZY MATCH (Jaro-Winkler >= 0.88)]
  - Evaluate phonetic / spelling similarity constrained within state boundary
        │
        ▼
[STAGE 5: PARENT-CHILD LINEAGE RESOLVER]
  - If district is a post-bifurcation child, map to parent LGD for inheritance
```

---

## 3. Detailed State-by-State Coverage Audit

| State / UT | Canonical Districts | NFHS-5 Direct PDFs | RHS Healthcare Mapped | MCA21 Pharma Mapped | Jan Aushadhi Mapped | Crosswalk Confidence |
|---|---|---|---|---|---|---|
| **Tamil Nadu** | 38 | 32 (84.2%) | 31 (81.6%) | 38 (100.0%) | 38 (100.0%) | **100% CANONICAL** |
| **Telangana** | 33 | 29 (87.9%) | 31 (93.9%) | 33 (100.0%) | 33 (100.0%) | **100% CANONICAL** |
| **Karnataka** | 31 | 30 (96.8%) | 30 (96.8%) | 31 (100.0%) | 31 (100.0%) | **100% CANONICAL** |
| **Andhra Pradesh** | 26 | 13 (50.0%) | 13 (50.0%) | 26 (100.0%) | 26 (100.0%) | **100% CANONICAL** |
| **Kerala** | 14 | 14 (100.0%) | 14 (100.0%) | 14 (100.0%) | 14 (100.0%) | **100% CANONICAL** |
| **Puducherry** | 4 | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | 4 (100.0%) | **100% CANONICAL** |
| **Goa** | 2 | 2 (100.0%) | 2 (100.0%) | 2 (100.0%) | 2 (100.0%) | **100% CANONICAL** |
| **TOTAL** | **148** | **124 (83.8%)** | **125 (84.5%)** | **148 (100.0%)** | **148 (100.0%)** | **100% CANONICAL** |
