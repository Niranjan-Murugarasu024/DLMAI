# DLMAI — Complete Procedure: Test → Improve → Deploy

Current model state (August 2026):
  22-district demo · 13/13 tests passing · image formula implemented
  Score range 14.58–67.98 · W5 dampener = 0.15
  All code correct, all data mock — deployment gate is real data collection

---

## PHASE 1: TEST (Start here — takes 1 day on mock data)

### 1.1 Local environment setup

Prerequisites: Python 3.11+, pip, git

```bash
# Clone / unzip the project
cd dlmai_complete

# Install pinned dependencies (use lock file, not requirements.txt)
pip install -r requirements-lock.txt

# Verify environment
python -c "import pdfplumber, reportlab, pandas, numpy, streamlit; print('All dependencies OK')"

# Create the data directory structure
python setup_data_dirs.py
```

Expected output: "All data directories created" with a checklist
showing every required file as MISSING — that is correct for now.

---

### 1.2 Run the full test suite (13 tests, all should pass)

```bash
# Run all 13 tests individually
for f in test_crosswalk_demo.py \
          test_parser_validation.py \
          test_jan_aushadhi_demo.py \
          test_census_parser_demo.py \
          test_imputation_demo.py \
          test_rhs_parser_demo.py \
          test_mca21_demo.py \
          test_niti_demo.py \
          test_scoring_demo.py \
          test_sensitivity_demo.py \
          test_scoring_missing_data_demo.py \
          test_entropy_and_montecarlo_missing_data_demo.py \
          test_multilevel_inheritance_demo.py; do
    echo -n "Running $f ... "
    python "$f" > /tmp/test_$f.log 2>&1 && echo "PASS" || echo "FAIL (see /tmp/test_$f.log)"
done
```

All 13 must print PASS before you proceed to anything else.
If any FAIL, read the log — most failures are environment issues
(missing dependency, wrong Python version) not code bugs.

---

### 1.3 Run the production entrypoint end-to-end

```bash
python build_index.py
```

Expected output:
  [timestamp] Starting DLMAI build...
  Build complete. Global coverage: 100.0%, minimum per-district 
  coverage: 97.0%. Wrote outputs/dlmai_scores.csv, ...

Check the outputs:
```bash
# Scores file — 22 rows, one per district
python -c "import pandas as pd; df=pd.read_csv('outputs/dlmai_scores.csv'); print(df[['district_name','composite_score','dampener_applied','tier']].to_string())"

# Metadata — confirms formula config is captured
python -c "import json; print(json.dumps(json.load(open('outputs/refresh_metadata.json')), indent=2))"
```

---

### 1.4 Run the dashboard locally

```bash
streamlit run dashboard_app.py
```

Open http://localhost:8501 in your browser.

What to verify visually:
  ✓ "Global pillar coverage" metric shows 100.0%
  ✓ "Lowest district coverage" metric shows 97.0%
  ✓ Formula caption shows: "DMAI = (Σ driver-pillar scores) − (0.15 × Competitive Intensity)"
  ✓ Ranking table shows "dampener_applied" column
  ✓ Hyderabad appears near the bottom (highest P5 penalty)
  ✓ State filter works — deselecting all states shows a warning, not a crash
  ✓ District detail shows P5 with negative weight (−0.1500) in the breakdown

---

### 1.5 Test the formula at different dampener levels

The W5_DAMPENER constant in scoring_engine.py is the single number
that controls how aggressively competitive saturation is penalised.
Test three values before settling on one:

```bash
# Test dampener = 0.10 (mild — competitive markets still score well)
python -c "
import scoring_engine
scoring_engine.W5_DAMPENER = 0.10
from run_pipeline import run_pipeline
from scoring_engine import score_districts
xwalk, filled, mask, *_ = run_pipeline()
codes = [d.lgd_code for d in xwalk.districts]
results = score_districts(filled, codes)
ranked = sorted(results.items(), key=lambda kv: -(kv[1]['composite_score'] or -1))
for code, r in ranked[:5]:
    print(f'{xwalk.by_code[code].current_name:<20} score={r[\"composite_score\"]:>6} dampener={r[\"dampener_applied\"]}')
"

# Test dampener = 0.20 (strong — saturated markets heavily penalised)
# (change 0.10 to 0.20 in the command above)
```

Rule of thumb:
  0.10 → use when entering an established market (competitive signals = validation)
  0.15 → balanced (the default, the formula image's recommended midpoint)
  0.20 → use when specifically targeting white-space / underserved markets

---

## PHASE 2: IMPROVE (Takes 1–4 weeks depending on data availability)

### 2.1 Collect real data — the single highest-impact action

Follow docs/DLMAI_Data_Download_Procedure.md exactly.
Priority order (fastest path to a real-data model):

DAY 1 (2–3 hours):
  Step 1 → lgd_districts.csv from data.gov.in → data/master/
  Step 1 → lgd_pincodes.csv from lgdirectory.gov.in → data/master/
            python reshape_lgd_master.py  (run immediately after)
  Step 4 → district_wise_health_centres.pdf from nhm.gov.in → data/rhs/
  Step 3A → PCA_district_level.csv from data.gov.in → data/census/primary_census_abstract/

DAY 2 (3–4 hours):
  Step 5 → Jan Aushadhi exports for 9 priority states → data/jan_aushadhi/
            (Maharashtra, Karnataka, Tamil Nadu, Gujarat, Telangana,
             AP, UP, Rajasthan, West Bengal)

DAYS 3–10 (largest effort):
  Step 2 → NFHS-5 district PDFs → data/nfhs/district/[State]/[District].pdf
            Start with Tamil Nadu (38 districts), Karnataka (31), Maharashtra (36)

After Day 1 data is in place:
  1. Open run_pipeline.py
  2. Change:  DEMO_MODE = True
  3. To:      DEMO_MODE = False
  4. Run:     python build_index.py
  5. Check:   python setup_data_dirs.py   (shows coverage progress)

---

### 2.2 Validate the real-data run (do this before publishing anything)

After your first real-data build, run three validation checks:

VALIDATION A — Crosswalk unmatched rate
```bash
python build_index.py 2>&1 | grep "unmatched\|WARN\|warn"
```
Target: zero unmatched district names from RHS and Census.
NFHS and Jan Aushadhi may have some — add entries to
data/master/manual_aliases.csv for each one and re-run.

VALIDATION B — Completeness report
```bash
python -c "
from run_pipeline import run_pipeline, ALL_INDICATORS
from imputation_engine import completeness_report, print_completeness_report
xwalk, filled, mask, *_ = run_pipeline()
report = completeness_report(mask, ALL_INDICATORS)
print_completeness_report(report, total_districts=len(xwalk.districts))
"
```
Target: stunting_pct, electricity_pct, phcs_per_lakh_pop, and
literacy_rate_pct all >70% native after adding real data.

VALIDATION C — Face validity (most important, no code needed)
  1. Run build_index.py
  2. Open outputs/dlmai_scores.csv
  3. Show the top 20 and bottom 20 districts to 3–5 people who
     know Indian pharma markets WITHOUT explaining the methodology
  4. Ask: "Do these rankings make intuitive sense?"
  If yes → model is publishing-ready
  If no → identify which specific district looks wrong and trace
           which pillar is causing it (the pillar breakdown column
           in the CSV is exactly what you need for this)

---

### 2.3 Tune the AHP pillar weights with a real expert panel

The current weights are built from one person's domain reasoning.
To make them defensible to a board or a client:

Step 1: Give each of 3–5 domain experts (pharma BD / market access
        professionals) a blank 7×7 pairwise comparison matrix with
        the Saaty 1–9 scale instructions.

Step 2: Have each expert fill it INDEPENDENTLY (no group discussion).

Step 3: Run the aggregation:
```bash
python ahp_pillar_weights.py
# Edit ahp_pillar_weights.py to add each expert's matrix:
# combined = aggregate_expert_matrices([expert1_M, expert2_M, expert3_M])
# result = compute_ahp_weights(combined, labels)
```

Step 4: If CR >= 0.10, the function tells you which comparison to
        revisit. Go back to the panel for that specific pair only.

Step 5: Copy the resulting weights into scoring_engine.py:
        AHP_PILLAR_WEIGHTS = {P1: ..., P2: ..., ...}

Step 6: Re-run build_index.py and the sensitivity analysis.
        Check whether the ranking changes materially — if it does,
        that is information (the index was weight-sensitive); if it
        doesn't, that confirms robustness.

---

### 2.4 Tune the W5 dampener for your specific use case

If you are using this model for multiple clients / use cases,
consider making W5_DAMPENER a runtime argument rather than a
hardcoded constant:

```bash
# In build_index.py, accept it as a command-line argument:
import sys
dampener = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
import scoring_engine
scoring_engine.W5_DAMPENER = dampener

# Then call:
python build_index.py 0.10   # for established-market clients
python build_index.py 0.20   # for white-space-seeking clients
```

This makes the same model serve different strategic questions
by changing one command-line parameter, not the code.

---

### 2.5 Add the choropleth map (the most visible dashboard improvement)

The dashboard currently has no map — this is the highest-visibility
missing feature. Prerequisites: district boundary shapefiles.

```bash
# Download shapefiles (community-maintained, CC0 licensed)
# URL: https://github.com/datameet/maps/tree/master/Districts
# Save: data/shapefiles/india_districts.shp (+ .dbf, .shx, .prj)

# Install mapping library
pip install geopandas folium streamlit-folium

# Add to requirements-lock.txt:
# geopandas==0.14.x
# folium==0.16.x
# streamlit-folium==0.20.x

# Add to dashboard_app.py (after the ranking table):
import geopandas as gpd
from streamlit_folium import st_folium
import folium

@st.cache_data
def load_shapefile():
    return gpd.read_file("data/shapefiles/india_districts.shp")

gdf = load_shapefile()
# Join scores onto the shapefile by district name (via lgd_code crosswalk)
gdf_merged = gdf.merge(filtered, left_on="DISTRICT", right_on="district_name", how="left")

m = folium.Map(location=[20.5, 78.9], zoom_start=5)
folium.Choropleth(
    geo_data=gdf_merged.to_json(),
    data=filtered,
    columns=["district_name", "composite_score"],
    key_on="feature.properties.district_name",
    fill_color="RdYlGn",
    fill_opacity=0.7,
    legend_name="DLMAI Score"
).add_to(m)
st.subheader("District-Level Market Attractiveness Map")
st_folium(m, use_container_width=True, height=500)
```

---

## PHASE 3: DEPLOY (Takes 1 day after Phase 2 is complete)

### 3.1 Push to GitHub

```bash
cd dlmai_complete

# Initialize git
git init
git add .
git commit -m "Initial commit: DLMAI pipeline, image formula, all tests passing"

# Create a repo on github.com, then:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dlmai.git
git push -u origin main
```

After pushing, go to the GitHub Actions tab.
The CI workflow runs automatically — all 13 tests should go green
within 2–3 minutes. This is your first deployment gate: if CI
is red, fix before proceeding.

---

### 3.2 Deploy the dashboard on Streamlit Community Cloud (free)

Step 1: Go to share.streamlit.io
Step 2: Sign in with your GitHub account
Step 3: Click "New app"
Step 4: Select your repository
Step 5: Set Main file path: dashboard_app.py
Step 6: Click "Deploy"

That's it. The URL will be:
  https://YOUR_USERNAME-dlmai-dashboard-app-XXXXX.streamlit.app

The dashboard auto-redeploys every time you push to main —
including every commit the quarterly refresh workflow makes.

For a custom domain (e.g. dlmai.yourcompany.com):
  Go to app settings → Custom domain in the Streamlit Cloud dashboard.

---

### 3.3 Set up the quarterly automated refresh

The scheduled refresh is already configured in:
  .github/workflows/scheduled_refresh.yml

It runs on the 1st of January, April, July, October at 00:00 UTC.
When it runs, it:
  1. Installs dependencies from requirements-lock.txt
  2. Runs python build_index.py
  3. Commits the updated outputs/ files back to main
  4. Streamlit Cloud auto-redeploys from that commit

For the automated refresh to actually pick up NEW data (not just
re-run on the same files), you need to update the data files in the
repo before each refresh cycle. Options:

Option A — Manual update (simplest, recommended for v1):
  Every quarter, download the latest RHS PDF and Jan Aushadhi exports,
  commit them to the repo, push. The scheduled run picks them up.

Option B — Automate the RHS download (one source, stable URL):
  Add this step to scheduled_refresh.yml before the build step:
  ```yaml
  - name: Refresh RHS district table
    run: |
      curl -L "https://www.nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-centres.pdf" \
           -o data/rhs/district_wise_health_centres.pdf
  ```

Option C — Store secrets for authenticated sources (MCA21):
  Add MCA21 API key as a GitHub Actions secret:
  Settings → Secrets → New repository secret → MCA21_API_KEY
  Then in the workflow:
  ```yaml
  env:
    MCA21_API_KEY: ${{ secrets.MCA21_API_KEY }}
  ```

---

### 3.4 Set up failure alerts

Add to scheduled_refresh.yml after the build step so failures
send an email instead of silently failing:

```yaml
- name: Send failure notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.MAIL_USERNAME }}
    password: ${{ secrets.MAIL_PASSWORD }}
    subject: "DLMAI Refresh Failed — manual check required"
    body: "The scheduled DLMAI quarterly refresh failed. Check GitHub Actions for details."
    to: your@email.com
```

Alternative (simpler): Add the Slack GitHub Action for team notifications.

---

### 3.5 Post-deployment validation checklist

After the first real deployment:

□ Open the live Streamlit URL and confirm the dashboard loads
□ Check "Last refreshed" timestamp — must match today's date
□ Verify "Global pillar coverage" shows the correct percentage
  (100% if all 7 pillars have real data; lower if any are still mocked)
□ Verify W5 dampener value in the formula caption matches scoring_engine.py
□ Sort by composite_score descending — top 5 districts should be
  plausible high-value pharma markets (major cities, strong infrastructure)
□ Sort ascending — bottom 5 should be remote/low-data districts or
  heavily saturated markets with high dampener_applied
□ Click one district → verify the pillar breakdown shows P5 with
  a NEGATIVE weight (−0.15) and "dampener_applied" is nonzero
□ Deselect all states → should show a warning, not crash
□ Check GitHub Actions tab → scheduled_refresh.yml shows as active
□ Verify outputs/refresh_metadata.json is committed to the repo
  (not in .gitignore)

---

## QUICK REFERENCE: KEY COMMANDS

```bash
# Test (mock data)
python build_index.py                    # full pipeline run
python setup_data_dirs.py               # check data collection progress
python test_scoring_demo.py             # validate scoring formula

# Improve
python reshape_lgd_master.py            # after downloading lgd_districts.csv
# Edit DEMO_MODE = False in run_pipeline.py after real data is in place

# Tune
# Edit W5_DAMPENER in scoring_engine.py   (0.10 mild / 0.15 balanced / 0.20 strong)
# Edit AHP_PILLAR_WEIGHTS after panel session

# Dashboard
streamlit run dashboard_app.py          # local preview
# push to GitHub → auto-redeploys on Streamlit Cloud

# Key files
scoring_engine.py                       # W5_DAMPENER and AHP weights live here
run_pipeline.py                         # DEMO_MODE toggle lives here
data/master/manual_aliases.csv          # add historical district names here
data/master/lgd_master.csv              # the real district master (after reshape)
outputs/dlmai_scores.csv                # the final scored output
outputs/refresh_metadata.json           # build metadata including w5_dampener value
```

---

## TROUBLESHOOTING

| Symptom | Cause | Fix |
|---|---|---|
| Tests fail on import | Missing dependency | pip install -r requirements-lock.txt |
| "lgd_master.csv not found" | DEMO_MODE=False before reshape | Run reshape_lgd_master.py first |
| All districts have identical scores | DEMO_MODE=False but no data files | Check data/ dir with setup_data_dirs.py |
| Streamlit crash on empty filter | State filter deselected | Already fixed — update to latest zip |
| Dashboard shows stale data after refresh | Cache not expired | Wait 1 hour (TTL=3600) or restart app |
| CI goes red | Dependency version conflict | Pin exact versions in requirements-lock.txt |
| Crosswalk "unmatched" warnings | Historical district name | Add to data/master/manual_aliases.csv |
| P5 score not being subtracted | W5_DAMPENER is 0 | Check scoring_engine.py config block |
| Score goes negative | Very high P5, very low drivers | Expected — clamped to 0 by design |
