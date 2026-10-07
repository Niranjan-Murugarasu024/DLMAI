# DLMAI — Publishing & Deployment Guide

This is the step-by-step path from "working code validated on a 22-district sample" to "open-source repo on GitHub, scored on real data, refreshed on a schedule, feeding an always-on dashboard." It assumes you've read `DLMAI_Scaling_Guide.md` — that document covers *what real data to get and how*; this one covers *how to wire it into a published, automated system*.

Five new files now exist alongside the rest of the package specifically for this:
- `build_index.py` — the clean production entrypoint (no test assertions, basic sanity guardrails, writes a refresh-metadata file)
- `dashboard_app.py` — a working Streamlit dashboard, verified against the real output schema
- `.github/workflows/ci.yml` — runs every test on every push/PR
- `.github/workflows/scheduled_refresh.yml` — quarterly cron job that re-runs the pipeline and commits updated scores
- `requirements.txt`, `.gitignore`, `LICENSE` — repo hygiene

---

## Phase A — Make the repo itself publish-ready

1. **Pick a real LICENSE.** An MIT license is already in the package as a reasonable permissive default — edit the copyright line, or swap to Apache-2.0 if you want explicit patent-grant language. Either way, **do not skip the data-licensing note inside `LICENSE`**: your code license does not cover the government datasets you're redistributing or republishing scores derived from. Check each source's actual terms before publishing:
   - Most Census/data.gov.in datasets are published under India's National Data Sharing and Accessibility Policy (NDSAP) terms, generally allowing reuse with attribution — verify on the specific dataset page, don't assume.
   - NFHS data usage is governed by IIPS/DHS Program terms — check before redistributing raw factsheet content (republishing your *derived, normalized scores* is a very different thing from republishing their raw tables verbatim).
   - Credit every source explicitly in your README (a "Data Sources" section) regardless of the exact license terms.
2. **Initialize the repo:**
   ```bash
   cd dlmai_complete
   git init
   git add .
   git commit -m "Initial commit: DLMAI pipeline, validated on 22-district sample"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo-name>.git
   git push -u origin main
   ```
3. **Turn on GitHub Actions.** Nothing extra needed — `ci.yml` runs automatically on the push above. Check the Actions tab; it should go green within a couple of minutes (it's literally running the same test suite already verified in this package).
4. **Decide what NOT to commit.** The `.gitignore` already excludes a `data/raw/` directory for real downloaded source files — review whether the *real* (non-mock) PDFs/CSVs you'll download in Phase B should be committed at all. Government PDFs can be large in bulk (hundreds of NFHS/Census files); consider committing only the *processed* output (`outputs/dlmai_combined_output.csv`) and the small mock files used for tests, not the full raw corpus, to keep repo size sane. If you want raw files versioned too, look at Git LFS rather than committing large binaries directly.

---

## Phase B — Replace mock data with real data

This is `DLMAI_Scaling_Guide.md` in full — follow its Phase 1 (harden the district master) through Phase 2 (source-by-source real data) exactly as written there. The one thing to add here, specific to automation:

**Which sources can actually be automated in the scheduled refresh, and which can't:**

| Source | Automatable in CI? | What to actually do |
|---|---|---|
| RHS (Pillar 3) | Yes | One stable bulk file — script a download (check the URL is stable; government file paths do change) and drop it where `rhs_parser.py` expects it |
| MCA21 (Pillar 5) | Yes, with care | data.gov.in has a registered-user API with API keys — use that instead of scraping the catalog page; store the key as a GitHub Actions secret, never commit it |
| NITI Aayog flag (Pillar 6) | Already done | The real, complete list is already embedded in `niti_aspirational_districts.py`. Nothing to automate — it only needs updating if NITI Aayog revises the list |
| NFHS-5 (Pillars 1, 2) | No, not fully | 715 individual PDFs. Realistic approach: download once as a batch (manually or with a one-time script respecting the site's terms of use), commit the processed output, and only re-pull when NFHS-6's district tables are eventually released — not on the quarterly cadence |
| Census handbooks (Pillars 1, 7) | No | Same situation — ~780 PDFs, refreshed once per Census cycle (next one 2027), not quarterly |
| Jan Aushadhi (Pillar 4) | No | Confirmed no bulk export; ~36 manual state-level exports. Re-pull this one periodically by hand — it's the source most likely to have genuinely *new* numbers between Census/NFHS cycles, since stores open continuously |
| PMJAY | N/A | Confirmed non-viable for automation at any frequency — stays excluded |

**The honest implication:** your "quarterly scheduled refresh" will, for most quarters, be re-running the pipeline against the *same* underlying NFHS/Census/handbook files, picking up only genuinely new Jan Aushadhi exports (if you've manually added any) and a re-pulled RHS/MCA21 file. That's fine and correct — it's what "real-time" actually means for an index built on government data with multi-year refresh cycles. Don't let the cron schedule imply more freshness than the underlying data has.

---

## Phase C — Upgrade persistence (recommended before real-scale, not strictly required to launch)

CSV files are genuinely fine at this data volume (~800 districts × ~30 indicators × a handful of historical quarters is a few hundred thousand cells — trivial for SQLite, and SQLite needs zero infrastructure). The reason to upgrade anyway: versioned history. Right now, each refresh *overwrites* `outputs/dlmai_scores.csv` — you lose the ability to show "how has this district's score changed over the last 4 quarters" on the dashboard.

A minimal schema, added to a single `dlmai.db` SQLite file:
```sql
CREATE TABLE runs (
    run_id INTEGER PRIMARY KEY,
    run_timestamp_utc TEXT,
    pillar_coverage_pct REAL
);

CREATE TABLE district_scores (
    run_id INTEGER REFERENCES runs(run_id),
    lgd_code TEXT,
    composite_score REAL,
    tier TEXT,
    pillar_scores_json TEXT   -- store the per-pillar breakdown as JSON; no need to over-normalize this for a dataset this size
);

CREATE TABLE district_indicators (
    run_id INTEGER REFERENCES runs(run_id),
    lgd_code TEXT,
    indicator_id TEXT,
    value REAL,
    status TEXT
);
```
`build_index.py` is the one place to change: after `export_scores_csv(...)`, also insert a new `runs` row and the corresponding `district_scores`/`district_indicators` rows. The dashboard can then offer a "trend over time" view per district — genuinely the single highest-value upgrade once you have more than one quarter of real history to show.

---

## Phase D — The dashboard

`dashboard_app.py` is a working starting point, already verified against the real output schema (ranking table, state filter, top/bottom bar charts, per-district pillar breakdown, full indicator-level drill-down with confidence status). What it deliberately does NOT have yet: a choropleth map (needs district boundary shapefiles — see `DLMAI_Data_Source_Mapping.md` Section 0) and the time-series trend view (needs Phase C's versioned history).

**To deploy:**
1. Push the repo to GitHub (Phase A).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub account, point it at this repo and `dashboard_app.py`.
3. Done — Streamlit Community Cloud redeploys automatically on every push to `main`, including every commit the scheduled refresh workflow makes. There is no separate "deploy" step beyond this one-time connection.

**If you outgrow the free tier or want more control:** containerize with a standard `Dockerfile` (`FROM python:3.11-slim`, `COPY . .`, `RUN pip install -r requirements.txt`, `CMD ["streamlit", "run", "dashboard_app.py"]`) and deploy to Render, Railway, or Fly.io's free/cheap tiers — all support a Docker image plus a scheduled job for the refresh in roughly the same shape as the GitHub Actions setup above.

---

## Phase E — Pre-launch validation (do this before the first real publish, not after)

Don't publish real-data scores the first time they come out of the pipeline. Before making the dashboard public:

1. **Re-run `test_sensitivity_demo.py`'s Monte Carlo logic against the real-data run.** The volatility patterns observed on the 22-district sample (e.g., Mumbai City's high rank instability) were specific to that sample — re-check which real districts turn out to have fragile rankings, and treat those specifically as "directional, not decisive" in any write-up.
2. **Face-validity review.** Show the real top-20 and bottom-20 districts to 2-3 people who know Indian pharma markets, without telling them the methodology first. This catches systemic errors (e.g., a unit conversion bug, a misclassified state) that no statistical check will surface — this is explicitly called out in `DLMAI_Framework_Architecture.md` Section 5.4 and is still the right move now that it's real data, not a sample.
3. **Spot-check the crosswalk's `unmatched` and `ambiguous` lists are actually empty** (Phase 1 of the Scaling Guide) — `build_index.py`'s sanity check catches *coverage collapse*, but a handful of silently-misattributed districts wouldn't trip that guardrail. Check the lists explicitly.

---

## Phase F — Ongoing maintenance

- **Watch the CI badge**, not just the scheduled refresh. A source website changing its PDF URL or table layout will usually show up as a CI failure (if you've added the real-data path to a test) or a silently degraded `pillar_coverage_pct` in `refresh_metadata.json` — check that file after every scheduled run, at least until you've set up an actual alert (a simple option: have the scheduled workflow fail loudly, per `build_index.py`'s existing guardrails, and add a Slack/email notification step on failure using any of the standard GitHub Actions notification actions).
- **Keep `manual_aliases.csv` and the parent-district mappings as living files**, exactly as both `DLMAI_Framework_Architecture.md` and the Scaling Guide describe — every newly-discovered rename or boundary change is a one-line addition, not a rebuild.
- **Re-validate the AHP weights periodically.** They were built from this project's own domain reasoning, not a real expert panel (documented honestly in `ahp_pillar_weights.py`). If this becomes a real, used tool, getting an actual 3-5 person panel to fill the pairwise matrix and replacing the weights is worth doing once, properly — the script already supports aggregating multiple experts' matrices via geometric mean.
