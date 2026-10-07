# DLMAI — Complete Data Download Procedure & Folder Structure
## Step-by-step guide to collect every real dataset and organize it so the model recognizes it

---

## PART 0: READ THIS FIRST — TWO IMPORTANT UPDATES (August 2026)

### NFHS-6 District Factsheets: Available NOW (released May 29, 2026)
NFHS-6 (2023-24) was released on May 29, 2026. However as of the time
of writing, only the national-level and state/UT-level factsheets are
published. District-level factsheets have NOT been released yet.

  For district-level data, STILL USE NFHS-5 (2019-21) factsheets.
  When NFHS-6 district factsheets eventually appear on nfhsiips.in,
  the parser (nfhs_factsheet_parser.py) will work on them with only
  minor regex adjustments — the indicator wording changes minimally
  across NFHS rounds for comparability.

### Rural Health Statistics renamed:
The annual bulletin formerly known as "Rural Health Statistics" has been
renamed to "Health Dynamics of India (Infrastructure and Human Resources)"
as of the 2022-23 edition. Same data, new title. The district-wise health
centres table (the specific file the model uses) remains at nhm.gov.in
and has not changed its format.

---

## PART 1: THE FOLDER STRUCTURE

Create this entire structure BEFORE downloading anything. Every file in
every folder must be placed exactly as shown — the pipeline's ingestion
modules look for files at these exact relative paths.

```
dlmai_complete/
├── data/
│   ├── master/                        ← district crosswalk files (DO FIRST)
│   │   ├── lgd_districts.csv          ← from lgdirectory.gov.in
│   │   ├── lgd_pincodes.csv           ← pincode-to-district crosswalk
│   │   └── manual_aliases.csv         ← already shipped with the model
│   │
│   ├── nfhs/                          ← NFHS factsheet PDFs (BIGGEST TASK)
│   │   ├── district/                  ← one PDF per district
│   │   │   ├── Andhra_Pradesh/
│   │   │   │   ├── Guntur.pdf
│   │   │   │   ├── Kurnool.pdf
│   │   │   │   └── ...
│   │   │   ├── Tamil_Nadu/
│   │   │   │   ├── Coimbatore.pdf
│   │   │   │   └── ...
│   │   │   └── [one subfolder per state, one PDF per district]
│   │   └── state/                     ← state-level factsheets (backup reference)
│   │       ├── NFHS5_Tamil_Nadu.pdf
│   │       └── ...
│   │
│   ├── census/                        ← Census 2011 handbooks
│   │   ├── primary_census_abstract/   ← THE EFFICIENT PATH (one CSV, all districts)
│   │   │   └── PCA_district_level.csv ← from data.gov.in (see Step 3 below)
│   │   └── handbooks/                 ← ALTERNATIVE: individual PDFs by state
│   │       ├── Tamil_Nadu/
│   │       │   ├── Coimbatore_DCHB.pdf
│   │       │   └── ...
│   │       └── ...
│   │
│   ├── rhs/                           ← Rural Health Statistics / Health Dynamics
│   │   ├── district_wise_health_centres.pdf   ← the specific district table
│   │   └── health_dynamics_2022_23.pdf        ← full annual bulletin (optional)
│   │
│   ├── jan_aushadhi/                  ← Jan Aushadhi Kendra state exports
│   │   ├── Andhra_Pradesh_kendras.pdf
│   │   ├── Tamil_Nadu_kendras.pdf
│   │   ├── Maharashtra_kendras.pdf
│   │   └── [one PDF per state/UT — ~36 files total]
│   │
│   ├── mca21/                         ← Company Master Data
│   │   └── company_master_data.csv    ← full bulk download (~1GB+)
│   │
│   └── niti_aayog/                    ← NITI Aayog (already in the code)
│       └── aspirational_districts_112.pdf  ← keep for reference/audit trail
│
├── outputs/                           ← model writes here (do not touch)
├── docs/
├── [all .py files remain in the root]
└── requirements-lock.txt
```

---

## PART 2: STEP-BY-STEP DOWNLOAD PROCEDURE

Work in this exact sequence. Each step builds on the one before.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — LGD District Master (DO THIS FIRST, EVERYTHING DEPENDS ON IT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Ministry of Panchayati Raj via data.gov.in
UPDATED: 1st of every month (last updated 30 May 2026)

Download 1: LGD District Codes
  URL:  https://www.data.gov.in/resource/local-government-directory-lgd-districts
  What to do:
    1. Click the URL above
    2. Click the blue "Download" button (CSV format)
    3. Rename the downloaded file to: lgd_districts.csv
    4. Save to: data/master/lgd_districts.csv

Download 2: LGD Pincode-to-District Mapping
  URL:  https://lgdirectory.gov.in/
  What to do:
    1. Go to lgdirectory.gov.in
    2. Click "View/Download Entities" in the left menu
    3. Select "Local Bodies with PIN Codes" from the dropdown
    4. Click "Download" — choose CSV
    5. Rename to: lgd_pincodes.csv
    6. Save to: data/master/lgd_pincodes.csv

ALTERNATIVELY (both files, pre-cleaned, community-maintained):
  URL:  https://ramseraph.github.io/opendata/lgd/
  This GitHub project maintains monthly LGD archive exports in clean
  CSV format. Faster and more reliable than navigating the live portal.

AFTER DOWNLOADING:
  Open lgd_districts.csv and verify it has these columns:
  District LGD Code, District Name (In English), State LGD Code,
  State Name (In English), District Census 2011 Code (if present)
  
  The model's district_crosswalk.py needs this reshaped to:
  lgd_code, state_lgd_code, state_name, current_name
  (historical_names and parent_lgd_code you fill manually over time
  as you encounter mismatches — start with the column empty)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — NFHS-5 District Factsheets (BIGGEST DOWNLOAD TASK)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: IIPS (International Institute for Population Sciences)
SURVEY: NFHS-5 (2019-21) — use this until NFHS-6 district PDFs release
TOTAL: ~640 district factsheet PDFs

Main portal:
  URL:  https://www.nfhsiips.in/nfhsuser/nfhs5.php
  What to do:
    1. Go to the URL above
    2. Click "Documents" → "Publications" in the top menu
    3. Under "State Fact Sheets" and "District Fact Sheets" you'll find
       PDFs organized by state
    4. Download every district-level PDF you can find
    5. Organize into subfolders by state inside data/nfhs/district/

NAMING CONVENTION (the parser reads the PDF header, not the filename,
but consistent naming will help you track coverage):
  data/nfhs/district/Tamil_Nadu/Coimbatore.pdf
  data/nfhs/district/Tamil_Nadu/Chennai.pdf
  data/nfhs/district/Karnataka/Bengaluru_Urban.pdf
  etc.

REALISTIC PLAN: This is 640+ PDFs. Do it in batches by state:
  Week 1: Tamil Nadu, Karnataka, Maharashtra, Gujarat (high-priority states)
  Week 2: Andhra Pradesh, Telangana, Rajasthan, UP, Bihar, MP
  Week 3: Remaining states

The pipeline will work correctly on whatever subset you've completed —
missing districts fall through to the imputation engine, which is the
correct, documented behaviour.

NFHS-6 STATE FACTSHEETS (for reference, not scoring):
  URL:  https://www.nfhsiips.in/nfhsuser/assets/National%20Family%20Health%20Survey%20(NFHS-6)%202023-2024%20Fact%20Sheets.pdf
  Download this as a reference document. Do NOT feed it to the parser
  yet — it only covers national/state level. District tables pending.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — Census 2011 (TWO OPTIONS — Option A is MUCH FASTER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Census of India, Registrar General of India
NOTE: Census 2021 does not exist yet. Next census is scheduled for 2027.
      2011 is the only district-level census data available.

OPTION A — Primary Census Abstract bulk CSV (RECOMMENDED — one download)
  URL:  https://www.data.gov.in/catalog/primary-census-abstract-2011-india-and-states-0
  What to do:
    1. Click the URL above
    2. Click "Download" — select CSV format
    3. This gives you population, age 0-6, literates, workers for
       ALL districts in ONE file (no PDF parsing needed)
    4. Save to: data/census/primary_census_abstract/PCA_district_level.csv
  
  IMPORTANT: The census_handbook_parser.py was built to parse PDFs,
  but this CSV path is FASTER and BETTER for most indicators (population,
  literacy, age 0-6). Update run_pipeline.py to read this CSV directly
  for Census Pillar 1 and 7 indicators — simpler than parsing 640 PDFs.
  (A CSV-reading version of the census ingestion is the recommended
  upgrade — one pandas read_csv() replaces the entire PDF parsing loop.)

OPTION B — District Census Handbooks as individual PDFs
  URL:  https://censusindia.gov.in/nada/index.php/catalog
  What to do:
    1. Search "District Census Handbook 2011"
    2. Filter by state
    3. Download Part XII-A (Important Statistics) for each district
    4. Organize into: data/census/handbooks/[State_Name]/[District].pdf
  
  Use Option B ONLY if you need the village directory or town amenities
  data that is NOT in the bulk CSV.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — Health Dynamics of India / Rural Health Statistics (ONE FILE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: National Health Mission (NHM), Ministry of Health
RENAMED: "Rural Health Statistics" is now "Health Dynamics of India"

Download 1: The district-wise health centres table (what the model uses)
  URL:  https://www.nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-centres.pdf
  What to do:
    1. Download directly from the URL above
    2. Save to: data/rhs/district_wise_health_centres.pdf
  NOTE: The model's rhs_parser.py was built and tested against this
  exact file. This is the most plug-and-play download in the project.

Download 2: Full annual bulletin (for workforce data)
  URL:  https://hmis.mohfw.gov.in/downloadfile?filepath=publications%2FRural-Health-Statistics%2FRHS+2021-22.pdf
  What to do:
    1. For the latest edition, go to: https://mohfw.gov.in
    2. Search "Health Dynamics of India" in the publications section
    3. Download the most recent available PDF
    4. Save to: data/rhs/health_dynamics_latest.pdf
  NOTE: The full bulletin is 270+ pages and contains workforce vacancy
  data (doctors, nurses) by district. This is a bonus indicator —
  the model works fine with just the district-wise table from Download 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5 — Jan Aushadhi Kendra (~36 state-level PDF exports)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)
PORTAL: https://janaushadhi.gov.in/near-by-kendra
TOTAL: ~36 separate exports (one per state/UT)
COUNT: 15,000+ Kendras nationally as of March 2025

How to download (repeat for each state):
  1. Go to: https://janaushadhi.gov.in/near-by-kendra
  2. In the "Select State" dropdown, choose a state
  3. Leave "Select District" empty (returns all districts in the state)
  4. Click Search
  5. On the results page, click "DOWNLOAD PDF"
  6. Rename the file: [StateName]_kendras.pdf
  7. Save to: data/jan_aushadhi/[StateName]_kendras.pdf

STATE PRIORITY ORDER (do high-pharma-activity states first):
  Tier 1 (do immediately):
    Maharashtra, Karnataka, Tamil Nadu, Gujarat, Telangana,
    Andhra Pradesh, Uttar Pradesh, Rajasthan, West Bengal
  Tier 2:
    Madhya Pradesh, Bihar, Punjab, Haryana, Kerala, Odisha
  Tier 3 (complete as time permits):
    All remaining states and UTs

NAMING EXAMPLES:
  data/jan_aushadhi/Maharashtra_kendras.pdf
  data/jan_aushadhi/Tamil_Nadu_kendras.pdf
  data/jan_aushadhi/Andhra_Pradesh_kendras.pdf
  (use underscores, match state names exactly to help the crosswalk)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6 — MCA21 Company Master Data (LARGE FILE — do last)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Ministry of Corporate Affairs (MCA), data.gov.in
SIZE: ~1GB+ CSV (28 lakh+ company records)
WHAT THE MODEL USES: Only pharmaceutical-classified active companies
  (NIC codes 21001, 21002, 21009, 46497, 4772) — roughly 5,000-8,000
  rows after filtering from the full dataset.

  URL:  https://www.data.gov.in/catalog/company-master-data
  What to do:
    1. Go to the URL above
    2. Sign in / register on data.gov.in (free, requires email)
    3. Click "Download" on the Company Master Data resource
    4. Select CSV format
    5. Save to: data/mca21/company_master_data.csv

IMPORTANT — handle the large file size:
  Do NOT open this in Excel (it will crash or truncate).
  The model reads it with Python's csv.DictReader in chunks.
  For faster processing, pre-filter with this shell command:
    grep -i "pharmaceutical\|21001\|21002\|21009\|46497\|4772" \
      data/mca21/company_master_data.csv > data/mca21/pharma_filtered.csv
  Then point the ingestion module at the filtered file instead.
  This reduces the file from 1GB+ to roughly 20-50MB.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 7 — NITI Aayog Aspirational Districts (ALREADY IN THE CODE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS: The complete 112-district list is ALREADY embedded in
  niti_aspirational_districts.py — hardcoded from the real verified
  NITI Aayog published PDF. You do NOT need to download anything for
  this indicator to work.

Keep as reference (for audit trail):
  URL:  https://www.niti.gov.in/sites/default/files/2023-07/List-of-112-Aspirational-Districts%20(1).pdf
  Save to: data/niti_aayog/aspirational_districts_112.pdf

For NITI Aayog's monthly delta rankings (not currently scored,
useful for future enhancement):
  URL:  https://www.niti.gov.in/node/248
  (scroll down to find monthly PDFs)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 8 — National Health Profile / CBHI (OPTIONAL — bonus Pillar 3 data)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Central Bureau of Health Intelligence (CBHI) / NCDC
  URL:  https://cbhidghs.mohfw.gov.in/index4.php?lang=1&level=0&linkid=418&lid=3655
  Save to: data/rhs/national_health_profile_latest.pdf

NOTE: The NHP has inconsistent district-level granularity across states —
  useful for cross-checking hospital bed counts, but not a primary input.
  Only worth downloading once Steps 1-7 are complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 9 — SECC (Socio-Economic Caste Census) — OPTIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE: Ministry of Rural Development
  URL:  https://secc.gov.in/statewiseReportStatus.htm
  Save to: data/secc/secc_state_reports/

NOTE: SECC data is from 2011 (same vintage as Census). Useful as
  an affordability proxy (BPL household markers, asset ownership)
  but adds complexity without dramatically changing Pillar 2 scores
  if NFHS data is already present. Treat as a Phase 2 enhancement.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 10 — District Boundary Shapefiles (for the map view only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOTE: The choropleth map on the dashboard is NOT YET BUILT — it's the
  one remaining output-layer piece. You'll need shapefiles when that
  feature is added, but they're not needed for scoring at all.

When you're ready:
  URL:  https://onlinemaps.surveyofindia.gov.in/
  (Survey of India digital vector data — district level, listed at ₹0)
  OR community-maintained open alternative:
  URL:  https://github.com/datameet/maps/tree/master/Districts
  Save to: data/shapefiles/india_districts.shp (and companion files)

---

## PART 3: HOW TO WIRE REAL DATA INTO THE MODEL

After downloading, three changes are needed in run_pipeline.py:

CHANGE 1: Point NFHS parser at the real directory
  Replace this line:
    nfhs_results = parse_factsheet_batch(["mock_Coimbatore_factsheet.pdf", ...])
  With:
    import glob
    nfhs_files = glob.glob("data/nfhs/district/**/*.pdf", recursive=True)
    nfhs_results = parse_factsheet_batch(nfhs_files)

CHANGE 2: Point Census ingestion at real data (CSV path — fastest)
  Replace the census_handbook_parser.py calls with a direct CSV read:
    import pandas as pd
    pca = pd.read_csv("data/census/primary_census_abstract/PCA_district_level.csv")
  Then extract the columns you need (population, literates, age_0_6_pop)
  and feed them into combined[] the same way the PDF parser did.
  This change eliminates PDF parsing for Census entirely.

CHANGE 3: Point Jan Aushadhi parser at the real directory
  Replace this line:
    rows = extract_kendra_rows("mock_kendra_export.pdf")
  With:
    import glob
    all_rows = []
    for pdf_path in glob.glob("data/jan_aushadhi/*.pdf"):
        all_rows.extend(extract_kendra_rows(pdf_path))
    rows = all_rows

CHANGE 4: Point RHS parser at the real file
  Replace:
    rhs_rows = extract_rhs_rows("mock_rhs_district_table.pdf")
  With:
    rhs_rows = extract_rhs_rows("data/rhs/district_wise_health_centres.pdf")

CHANGE 5: Point MCA21 at real file (filtered version)
  Replace:
    kept_companies, mca21_excluded = extract_pharma_companies("mock_mca21_company_master.csv")
  With:
    kept_companies, mca21_excluded = extract_pharma_companies("data/mca21/pharma_filtered.csv")

CHANGE 6: Load real LGD master instead of the 22-row sample
  In district_crosswalk.py, the master CSV path is passed at construction:
    xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")
  Replace with:
    xwalk = DistrictCrosswalk("data/master/lgd_districts.csv", "data/master/manual_aliases.csv")
  Then reshape lgd_districts.csv to match the sample_lgd_seed.csv columns.
  See sample_lgd_seed.csv for the exact required schema.

---

## PART 4: DOWNLOAD PRIORITY MATRIX

| Step | Dataset              | Time to Download | Pillars Fed | Impact on Model |
|------|---------------------|-----------------|-------------|-----------------|
| 1    | LGD Master          | 15 minutes      | All         | ⭐⭐⭐⭐⭐ DO FIRST |
| 4    | RHS/Health Dynamics | 5 minutes       | P3          | ⭐⭐⭐⭐⭐ One file |
| 7    | NITI Aayog          | Already done    | P6          | ⭐⭐⭐⭐⭐ Done    |
| 3A   | Census PCA CSV      | 10 minutes      | P1, P7      | ⭐⭐⭐⭐⭐ One file |
| 5    | Jan Aushadhi        | 3-4 hours total | P4          | ⭐⭐⭐⭐ 36 exports|
| 2    | NFHS-5 PDFs         | 3-5 days total  | P1, P2      | ⭐⭐⭐⭐ 640 files |
| 6    | MCA21 CSV           | 1-2 hours       | P5          | ⭐⭐⭐ Large file |
| 8    | NHP                 | 30 minutes      | P3 bonus    | ⭐⭐ Optional    |
| 9    | SECC                | 2-3 hours       | P2 bonus    | ⭐⭐ Optional    |
| 10   | Shapefiles          | 30 minutes      | Map only    | ⭐ Not yet needed|

FASTEST PATH TO A USABLE REAL-DATA MODEL (2-3 days):
  Day 1: Steps 1, 3A, 4, 7 (LGD + Census CSV + RHS + NITI)
          → 4 of 7 pillars working on real data, ~450 districts covered
  Day 2: Step 5 Tier 1 states (9 major states' Jan Aushadhi)
          → P4 real data for ~60% of pharma-relevant geography
  Day 3: Step 2 Tier 1 states (NFHS for major states)
          → P1 and P2 real data replacing 82% imputed cells

---

## PART 5: DATASETS NOT IN SCOPE (and why)

PMJAY / Ayushman Bharat:
  Confirmed dead end for automated download. The NHA public dashboard
  (dashboard.pmjay.gov.in) is robots-disallowed. The only bulk dataset
  on data.gov.in is at State/UT level, not district. Pillar 6 will
  remain a single-indicator pillar (NITI flag only) until this changes.

State Drug Controller license registers:
  Listed in the original framework doc but excluded from the current
  pipeline after the feasibility audit confirmed these are fragmented
  across 36 state websites, most without bulk district-level exports.
  Maharashtra FDA and Gujarat FDA are the most accessible — worth a
  manual pull for those two states if you have the bandwidth.

AIOCD / IQVIA secondary sales data:
  Paid service. Not available for free download. If Sun Pharma has an
  existing IQVIA subscription, use those files to VALIDATE the model's
  rankings (compare DLMAI Tier 1 districts against actual sales
  performance) rather than as a scoring input.

State Directorates of Economics & Statistics (district GDP):
  Only about 12-15 states publish district-level GDP or GDC estimates.
  Maharashtra, Karnataka, Tamil Nadu, and Gujarat are the most reliable.
  Worth collecting opportunistically for those states; not a blocker.
