# DLMAI — Scaling Guide: From the 22-District Demo to ~780-800 Real Districts

Everything built so far — `district_crosswalk.py`, the six ingestion modules, `imputation_engine.py`, `scoring_engine.py`, `sensitivity_analysis.py` — is architecturally complete and runs correctly. Going to real scale is not a rebuild; it's a specific, bounded set of substitutions and a few things that genuinely behave differently at 800 rows than at 22. This document is organized around what changes and what doesn't, district by district, source by source.

---

## 0. What does NOT change

This is worth saying explicitly because it's most of the codebase: `district_crosswalk.py`'s matching logic, `imputation_engine.py`'s hierarchy, `scoring_engine.py`'s normalization/weighting/aggregation math, and `sensitivity_analysis.py`'s Monte Carlo engine are all already written generically — none of them hardcode anything about the 22 sample districts. Pointing them at real data is a matter of swapping inputs, not rewriting logic.

What changes is entirely in the **data layer**: the master table, the manual alias list, and the actual files each ingestion module reads.

---

## 1. Phase 1 (do this first, alone): harden the district master

This is the one piece of advice that matters most. Don't start pulling real NFHS/Census/RHS data until this phase has a clean exit criterion. Trying to debug crosswalk mismatches *while also* debugging six ingestion parsers at once is how this kind of project stalls.

**Step 1.1 — Replace the seed file.** Download the real district list from lgdirectory.gov.in ("View/Download Entities → Districts") or the mirrored `data.gov.in/resource/local-government-directory-lgd-districts` dataset. Reshape it to `sample_lgd_seed.csv`'s exact column schema: `lgd_code, state_lgd_code, state_name, current_name, historical_names, parent_lgd_code, effective_from`.

**Step 1.2 — `historical_names` and `parent_lgd_code` won't come pre-filled.** The LGD download gives you the *current* district list with current names — it doesn't ship a "renamed from" or "carved from" field. This has to be hand-compiled, and there's no shortcut:
- **Historical names:** compile from known renames (Allahabad→Prayagraj, Faizabad→Ayodhya, Bombay→Mumbai, Calcutta→Kolkata, Madras→Chennai, Bangalore→Bengaluru, and others by state). This list will never be "complete" on day one — treat it the way `manual_aliases.csv` is already treated: a living file you add to every time the crosswalk reports an unmatched district that turns out to be an old name.
- **Parent-child relationships:** compile from state reorganization notifications — Andhra Pradesh's 2022 split (13→26 districts, already partially represented in the sample), Telangana's 2016 and subsequent splits, Assam's 2022 reorganization, Chhattisgarh's 2022 new districts, and others. This is genuinely the most labor-intensive one-time task in the whole scale-up. There is no single authoritative "what got carved from what" dataset; state government gazette notifications are the ground truth, and a web search per state ("[state] district reorganization [year] notification") is the realistic path.

**Step 1.3 — Run a crosswalk-only pass before anything else.** Take the real district/state-name columns from every source you intend to use (NFHS factsheet headers, RHS table, Jan Aushadhi exports, etc. — just the names, not the full ingestion) and run them through `DistrictCrosswalk.resolve()`. Collect every `ambiguous` and `unmatched` result into one consolidated review list, resolve them (mostly by adding entries to `manual_aliases.csv`), and re-run. **Exit criterion for Phase 1: zero unmatched/ambiguous results across every source's district names.** Only then move to Phase 2. This front-loads the hardest engineering work into one clearly-bounded phase instead of discovering it piecemeal while debugging six parsers simultaneously.

---

## 2. Phase 2: source-by-source — what's the same, what's different, what to watch for

### NFHS-5 district factsheets
- **Same:** `nfhs_factsheet_parser.py`'s indicator patterns are built from the *real, verified* NFHS-5 indicator text (pulled from the actual published indicator list, not guessed) — these should hold up against real factsheets.
- **Different, and the one real risk:** the parser has only been tested against a PDF *I generated* to mimic the real layout — never against an actual downloaded factsheet. The indicator-text matching is solid; what's unverified is how `pdfplumber` extracts text from the *real* PDF's actual column layout, which I couldn't confirm (multi-column layouts sometimes interleave text in extraction in ways a single-column mock can't reveal).
- **What to do:** download 5-10 real factsheets spanning different states before committing to all 715. Run them through the parser and read the `missing` / `unparsed_lines` warnings closely — that's exactly what they're there for. Expect to adjust a regex or two; don't expect to rewrite the matching approach.
- **Scale note:** 715 separate PDF downloads, one per district. This is a real, bounded manual/scripted task, not a blocker — but budget for it as actual time, not an afterthought.

### Census District Handbooks
- **Same:** the two-table approach (Important Statistics + District PCA) is built from a verified real table-of-contents structure.
- **Different:** real handbooks are much longer documents (the two tables this module targets are a small fraction of the full handbook, which also has village/town directories and amenity tables this module doesn't touch). `census_handbook_parser.py` scans every page for matching tables, so it will still find the right tables in a longer document — it'll just take longer per file.
- **Scale note:** ~780 documents, each potentially 100+ pages. If runtime becomes a real concern, the fix is parallelizing the per-file parsing (each file is independent), not changing the parsing logic itself.

### Rural Health Statistics (district health centres)
- **Best case for scaling.** This is already one national bulk file, not one-per-district — `rhs_parser.py` already handles the real confirmed column structure and the real confirmed quirks (blank-row state totals, fully-urban districts being absent). Swapping the mock PDF for the real one from nhm.gov.in should need little to no parser adjustment. Verify the page count and total-row count once against the live file, but this is the lowest-risk source in the whole pipeline.

### Jan Aushadhi Kendra locator
- **Confirmed, not assumed:** there's no bulk "export everything" button on the live portal — the realistic path is ~36 state-level pulls (state selected, district blank, then the page's own PDF export), not a single download or a per-district crawl.
- **Scale note:** 36 manual exports is a bounded one-time task. `jan_aushadhi_ingestion.py`'s table extraction and the "states actually covered get a confirmed zero, uncovered states stay unknown" logic already handles partial rollout correctly — just keep running it as each state's PDF comes in, rather than waiting for all 36 before the first real run.

### MCA21 Company Master Data
- **Same:** the real NIC codes (21001/21002/21009 manufacturing, 46497 wholesale, 4772 retail) and the Active-status filter are verified and correct.
- **Different, and significant:** the real bulk file has on the order of a million-plus company rows nationally, not 11. The simple `csv.DictReader` loop in `mca21_ingestion.py` will still produce correct results, but reading a multi-gigabyte CSV row-by-row in plain Python will be slow. Pre-filter with a command-line tool (`grep`/`awk` on the Principal Business Activity column) before handing rows to Python, or switch to chunked reading with pandas, before running this against the real file.
- **Different, the other thing to budget for:** the pincode-prefix map (`PINCODE_PREFIX_TO_LGD`) currently covers 9 illustrative prefixes. The real version needs the actual LGD "Local Bodies with PIN Codes" dataset, which is a genuine many-thousand-row mapping — this is a real download-and-join task, not a hand-typed dict, at real scale.

### NITI Aayog Aspirational Districts
- **Nothing changes.** This module already contains the real, complete, verified 112-district list. It's done. Copy it as-is into the real run.

### PMJAY (confirmed non-viable)
- **Nothing changes here either, in the sense that the conclusion doesn't change with scale:** the live dashboard is robots-disallowed for automated access regardless of how many districts you're asking about, and the only bulk dataset is state-level. This stays a documented gap unless a manual, human-driven collection effort is invested — it doesn't get easier or harder by going from 22 to 780 districts; it's just as not-free either way.

---

## 3. Performance notes at real scale

None of these are blockers — they're things to be aware of, not things that need fixing today.

- **`DistrictCrosswalk.resolve()`'s fuzzy matching** is a linear scan with `difflib.SequenceMatcher` over the index. At ~800 districts (with multiple historical names each, so maybe 1,000-1,500 index entries), and called for every incoming row across every source, this is still a batch job measured in tens of seconds to low minutes, not hours — this is a one-time/periodic offline pipeline, not a live service, so this is comfortably fine. The `state_hint` parameter (already used throughout) narrows the candidate pool substantially whenever a source provides a state column, which most do.
- **`ImputationEngine`'s state-mean and nearest-neighbor steps** are O(districts) per indicator. At ~800 districts × ~20 indicators, that's roughly 16,000 operations — trivial.
- **`sensitivity_analysis.py`'s Monte Carlo loop** at 3,000 iterations × 800 districts is still comfortably fast in pure Python (seconds). If you want to push iteration count much higher (tens of thousands) at full scale, vectorizing the composite-score computation with numpy would be the natural next step — not necessary now, worth knowing about later.

---

## 4. Data-quality issues that only show up at real scale

The 22-district sample was, deliberately, mostly major cities and a few illustrative edge cases. Real districts include many small, remote, or newly-carved ones that the sample didn't stress-test:

- **Districts with zero native data across MULTIPLE sources at once.** Every sample district had at least some real data from somewhere. At real scale, expect districts — especially small or newly-created ones — with no native data from *any* source, relying entirely on state-mean/nearest-neighbor imputation for everything. The confidence mask already captures this per-cell; at real scale, it's worth adding a per-district summary statistic (e.g., "% of indicators that are native") and considering a visible low-confidence flag below some threshold (e.g., under 30% native), rather than only exposing this at the individual-cell level.
- **Extreme per-capita values from very small districts.** A district with a tiny population can produce wildly large per-lakh density figures from a single facility. Consider winsorizing (capping at a percentile) before normalization, or flagging districts below a population floor for manual review rather than letting one outlier stretch the whole min-max scale for everyone else.
- **Systematic state-level gaps, not just random district-level noise.** Some states/UTs simply have less digitized, less complete public data (this shows up as a *pattern* by state, not as scattered random gaps). Track completeness by state, not only by indicator, so a real gap doesn't get misread as 28 unrelated small problems instead of one structural one.

---

## 5. A concrete rollout sequence

1. Phase 1 above: real LGD master + hardened crosswalk, exit criterion = zero unmatched/ambiguous.
2. RHS first (lowest risk, already a national bulk file) — gives you a working Pillar 3 across all real districts fastest, and a good early signal on overall crosswalk health since it's one clean file to debug against.
3. NITI Aayog flag (already done, zero new work) — Pillar 6 instantly at full real coverage.
4. NFHS-5, after validating the parser against 5-10 real downloaded factsheets first.
5. Census handbooks.
6. Jan Aushadhi (36 manual state pulls — start this in parallel with the above, since it's a human task, not a blocking dependency).
7. MCA21, last — it's the highest one-time engineering effort (real pincode map, large-file handling) and isn't on the critical path for the other six.
8. Re-run `sensitivity_analysis.py` once all real data is in — the volatility patterns you've already seen in the 22-district demo (e.g., a district's rank depending heavily on one thin pillar) are exactly the kind of thing to re-check once real numbers replace the sample, not assume still hold.

---

## 6. Updated honest-limitations list for the real-scale build

Everything in Section 10 of `DLMAI_Framework_Architecture.md` still applies. Add to it:
- The crosswalk's historical-names and parent-district mappings are necessarily incomplete on day one and will be discovered incrementally — budget ongoing time for this, don't treat Phase 1 as a one-time cost.
- NFHS factsheet parsing carries some real, unverified risk until checked against actual downloaded PDFs (versus the verified indicator text, which carries much less risk).
- PMJAY remains excluded from Pillar 6 regardless of scale — this is a permanent gap in the free-sources-only build, not a temporary one.
