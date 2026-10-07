# District-Level Market Attractiveness Index (DLMAI)
## Indian Pharmaceutical Industry — Statistical Framework & System Architecture

---

## 0. What this document is

A blueprint for building a composite index that scores 700+ Indian districts on pharmaceutical market attractiveness, using only offline / bulk-downloadable data — no live APIs. This is a feature, not a constraint: an index meant to guide territory planning, market entry, or investment prioritization should refresh on a quarterly/annual cycle anyway, not in real time. The deliverable is a **batch analytical pipeline**, not a live service.

This document covers architecture and methodology only. No code yet — that's the deliberate next phase, once the framework below is locked.

**Version note (v1.1):** Section 1.1 below re-audits every indicator against a strict free/public-sources-only constraint (no AIOCD/IQVIA or other paid data). Several indicators were dropped or replaced as a result — see Section 1.1 for the full audit and rationale.

---

## 1. Conceptual framework — what "attractiveness" means here

A Market Attractiveness Index is a Multi-Criteria Decision Analysis (MCDA) problem: combine many indicators that individually matter, into one number that summarizes "how good is this district as a pharma market." The standard failure mode is picking indicators ad hoc. Instead, structure them under **pillars**, each representing a distinct economic driver of pharma demand or supply.

| Pillar | What it captures | Why it matters for pharma | Example indicators |
|---|---|---|---|
| **1. Demand & disease burden** | Population size, age structure, epidemiological profile | More people + more NCDs (diabetes, cardiovascular, oncology) = larger chronic-therapy market; younger/high-fertility districts skew toward pediatric, maternal, anti-infective demand | Population, % population age 0-6 (the age bracket Census actually publishes at district level — see Section 1.1), NCD prevalence, communicable vs non-communicable disease split |
| **2. Economic access & affordability** | Income, insurance penetration, out-of-pocket burden | Determines whether demand converts into purchases — and whether that purchase is branded or generic | Per-capita income proxy, % households with health insurance/PMJAY cards, out-of-pocket health expenditure share |
| **3. Healthcare infrastructure** | Supply-side capacity to diagnose and prescribe | No doctors/beds = no prescriptions, regardless of demand | Hospital beds per 1,000, PHC/CHC density, doctors & pharmacists per capita, diagnostic lab presence |
| **4. Pharma distribution & retail density** | Physical reach of the supply chain | A market can't be served without chemists, stockists, and cold-chain reach | Retail chemist density, wholesale stockist count, Jan Aushadhi Kendra count, distance to nearest distribution hub |
| **5. Competitive intensity** | How crowded the market already is | High attractiveness ≠ high opportunity if already saturated; this pillar usually *subtracts* from raw attractiveness | Registered manufacturing units, active drug licenses, estimated MR (medical representative) density, brand fragmentation proxy |
| **6. Regulatory & scheme environment** | Policy tailwinds/friction | Faster license processing and higher scheme penetration lower friction for market entry | PMJAY/Ayushman Bharat enrollment rate, drug license processing efficiency, presence in NITI Aayog Aspirational Districts list |
| **7. Growth momentum** | Trajectory, not just current state | A mid-tier district growing fast can outrank a stagnant Tier-1 city on a 3-5 year horizon | Population growth rate, urbanization rate, road/infrastructure project pipeline, digital health/e-pharmacy adoption |

**Design decision to make explicitly, in writing, before collecting data:** is Pillar 5 (competitive intensity) scored so that *more* competition *lowers* the attractiveness score (a "white space" index) or do you treat existing competitor presence as a *validation signal* that the market is real (a "proven demand" index)? Both are legitimate strategies — pharma companies use both depending on whether they're targeting underserved white space or following category leaders into validated markets. This single decision changes the sign of one entire pillar, so it has to be a conscious choice, documented in the config, not an accident of how the data fell out.

---

## 1.1 Feasibility audit — free-source-only refinement (v1.1)

No paid data (AIOCD/IQVIA) is in scope. Every indicator from Section 1 is re-checked here against what's actually downloadable for free at, or aggregable to, district level. This is the single biggest filter to run before any data collection starts: a pillar that looks clean in theory but has no real free district-level source is worse than useless — it invites you to either leave a large share of districts blank or quietly fabricate a comfortable interpolation.

**Status key:** 🟢 Keep (solid free source exists) · 🟡 Keep with effort (fragmented/manual, doable) · 🔴 Drop or replace (no realistic free district-level source)

### Pillar 1 — Demand & disease burden (mostly intact, with corrections below)

**Verified correction (this build):** NFHS-6 (2023-24) district-level factsheets have **not been released as of mid-2026** — only national and state/UT tables are out so far; district tables historically follow later, as they did for NFHS-5. The current working district-level NFHS source is therefore **NFHS-5 (2019-21)**, with NFHS-6 to be swapped in once IIPS releases district tables. Pulling the real NFHS-5 indicator list also corrected two assumptions: **Total Fertility Rate is not published at district level** (state/national only — the district module doesn't carry a reliable district-level TFR estimate), so it's dropped from this pillar; and the NCD-prevalence row below was previously flagged as only partially available — the real indicator list confirms blood pressure and blood sugar measures **are** solidly present at district level.

| Indicator | Free source | Status |
|---|---|---|
| Population, urban %, % population age 0-6 | Census 2011 District Census Handbook — verified real structure: the standard Primary Census Abstract table publishes population age 0-6 only (a stable Census convention since 1991, used to compute the "effective literacy rate"), **not** a 0-14/60+ breakdown — correcting an earlier draft of this row. A fuller 0-14/60+ age structure exists only in a separate, less commonly bundled Census product (C-series single-year age tables) | 🟢 for population/urban%/age-0-6; 🟡 for fuller age brackets — extra source needed |
| ~~Total fertility rate~~ | Not published at district level in NFHS-5; state/national only | 🔴 dropped — % population age 0-6 (from Census, see above) is the working proxy for fertility/young-population-driven demand instead |
| Child stunting / wasting | NFHS-5 (2019-21) district factsheet — confirmed exact fields: "Children under 5 years who are stunted (height-for-age) (%)" and the equivalent wasting/underweight rows | 🟢 |
| Elevated blood pressure / on hypertension medication (%) | NFHS-5 district factsheet — confirmed real field, both a mild and a moderate-or-severe threshold reported | 🟢 |
| Blood sugar high/very high or on diabetes medication (%) | NFHS-5 district factsheet — confirmed real field | 🟢 |
| Communicable disease incidence (TB, malaria, dengue) | NVBDCP / NTEP district bulletins — NFHS does not cover this | 🟡 — published, but scattered across separate PDF dashboards; needs manual assembly |

### Pillar 2 — Economic access & affordability (corrected — rebuilt around verified real NFHS fields)

**Correction:** the previous version of this pillar claimed NFHS publishes a district-level wealth-index quintile and a BPL-card percentage. Pulling the real NFHS-5 indicator list shows **neither field actually exists** in the published district factsheet — that was an error in the earlier draft. What *is* real: the household-amenity indicators that wealth indices are normally built from in the first place (electricity, clean fuel, drinking water, sanitation), confirmed insurance coverage, and — reversing an earlier *over-correction* — a genuine district-level out-of-pocket expenditure figure, albeit narrower in scope than originally assumed (delivery costs specifically, not general health spending).

| Indicator | Free source | Status |
|---|---|---|
| Household amenities composite (% electricity, % clean cooking fuel, % improved drinking water, % improved sanitation) | NFHS-5 district factsheet — confirmed real fields, used here as a living-standards/affordability proxy in place of the unavailable wealth-quintile output | 🟢 |
| % households with any member covered under health insurance/financing scheme | NFHS-5 district factsheet — confirmed exact field | 🟢 |
| Average out-of-pocket expenditure per delivery in a public health facility (Rs.) | NFHS-5 district factsheet — confirmed real, district-level field | 🟢 — narrower than general OOPE (delivery-specific), but real and usable as a directional affordability signal |
| ~~Wealth index quintile distribution~~ | Not published at district level | 🔴 dropped — this was an error in the earlier draft |
| ~~% households with BPL card~~ | Not published at district level | 🔴 dropped — same error |
| ~~District domestic product / per-capita income~~ | State Directorates of Economics & Statistics | 🔴 dropped as a baseline requirement — published by some states, not most; add opportunistically where a state happens to publish it |

**Net effect:** this pillar still leans entirely on one internally-consistent survey, which remains the right call — it's just built from the amenity/insurance/OOPE fields that are *actually* in the factsheet rather than a wealth index that turned out not to exist at this granularity.

### Pillar 3 — Healthcare infrastructure (kept, with a disclosed skew)
| Indicator | Free source | Status |
|---|---|---|
| PHC / CHC / sub-centre counts and density | Rural Health Statistics (MoHFW) | 🟢 |
| District hospital count, public bed count | Rural Health Statistics / National Health Profile | 🟢 |
| Doctor / nurse / pharmacist sanctioned vs vacant posts | Rural Health Statistics | 🟢 |
| ~~Private hospital / bed count~~ | No standardized free district-level registry exists | 🔴 dropped |
| ~~Diagnostic lab presence~~ | No free district-level source found | 🔴 dropped |

**Disclosure to carry forward:** with private-sector beds and diagnostic labs dropped, this pillar measures *public health-system capacity* specifically, not total healthcare capacity. That's a real, defensible signal — most of India outside metro cores is served predominantly by public infrastructure — but it should be labeled as such in the final output, not presented as "total healthcare infrastructure."

### Pillar 4 — Pharma distribution & retail density (Jan Aushadhi becomes the backbone)
| Indicator | Free source | Status |
|---|---|---|
| Jan Aushadhi Kendra count per district | PMBJP store locator (19,000+ stores nationally, present in every district) | 🟢 |
| All-weather road connectivity | PMGSY dashboard / Ministry of Rural Development reports | 🟡 |
| Retail chemist license count | State FDA portals | 🟡 a handful of states (Maharashtra, Gujarat, Kerala among them) run searchable registries; most don't publish bulk district rollups — treat as a bonus indicator collected where feasible, not a required field, or it will create artificial gaps that look like real signal |

### Pillar 5 — restructured and renamed: "Industry presence & supply depth" (was "Competitive intensity")
This is the pillar that breaks without paid data, so it gets the biggest rework rather than a patch.

**Why the rename:** "competitive intensity" implies measuring market share or sales overlap, which genuinely requires AIOCD/IQVIA-grade data. Without it, what's measurable for free is industry **presence** — where companies are registered, not how much they're selling. Calling it what it actually is prevents the index from quietly overclaiming what it knows.

| Indicator | Free source | Status |
|---|---|---|
| Pharma-classified company count by registered-office district | **MCA21 Company Master Data** (data.gov.in bulk download — includes CIN, Principal Business Activity, Registered Office Address, Registered State) | 🟢 real and bulk-downloadable, but the registered-office address is free text, so mapping it to a district needs a pincode-to-district crosswalk step — a real but bounded data-engineering task, not a dead end |
| Manufacturing unit / drug license counts | CDSCO public licensing pages, state FDA portals | 🔴 fragmented the same way retail licenses are — drop as a required field, fold in opportunistically |
| ~~Sales-based market share~~ | AIOCD/IQVIA | 🔴 explicitly out of scope per the free-sources-only constraint |

**Net effect:** Pillar 5 becomes lower-confidence than the other six by design, and should enter the AHP weighting step with a visibly lower base weight (or a wider confidence band) until — or unless — paid validation data becomes available later.

### Pillar 6 — Regulatory & scheme environment (tightened)
| Indicator | Free source | Status |
|---|---|---|
| Ayushman Bharat/PMJAY cards issued, hospitals empanelled | NHA public dashboard (dashboard.pmjay.gov.in/publicdashboard) | 🔴 **confirmed dropped, not just downgraded:** the live dashboard returns a robots-disallowed response to automated access, and the only bulk dataset found on data.gov.in is State/UT-level, not district-level — a genuine dead end for a free, automatable district-level pull. Pillar 6 in this build runs on the NITI Aayog flag alone; PMJAY is a manual-collection candidate for a future pass, not a fabricated indicator |
| NITI Aayog Aspirational District flag | NITI Aayog published list | 🟢 |
| ~~Drug license processing time~~ | No systematic public data found | 🔴 dropped |
| *(New, validation-only)* SDG India Index district score | NITI Aayog | Use only to sense-check the final DLMAI ranking, never as a raw scoring input — it already blends similar indicators, so feeding it in as well would double-count |

### Pillar 7 — Growth momentum (trimmed to what Census actually supports)
| Indicator | Free source | Status |
|---|---|---|
| Decadal population growth rate | Census 2001 → 2011 | 🟢 dated, but the only systematic source until the next census round |
| Decadal urbanization change | Census 2001 → 2011 | 🟢 |
| Literacy rate and literacy growth | Census | 🟢 |
| ~~Digital/internet adoption~~ | Census 2011 "households with internet" (badly dated); TRAI publishes only at telecom-circle level, not district | 🔴 dropped — no current district-level source |
| ~~Infrastructure project pipeline~~ | No systematic free district-level source | 🔴 dropped |

### What this changes overall
- **~9 indicators dropped** across the original framework — mostly ones that quietly assumed a paid or fragmented source.
- **Pillars 2 and 6 get *more* internally consistent, not less** — leaning on fewer, single-survey sources (mostly NFHS-5) reduces cross-source noise.
- **Pillar 3 narrows its claim** to public-sector healthcare capacity specifically.
- **Pillar 5 is renamed and rebuilt** around company-registration data (MCA21) instead of sales data, entering the weighting step with a lower starting weight and a flagged lower confidence than the other six pillars.
- The **district master crosswalk from Section 2 gains one more job**: resolving a pincode → district mapping for MCA21 registered-office addresses, since that field is free text rather than a structured district code.

---

## 2. The core engineering challenge: the district master reference

This is the single most important architectural decision in the whole system, and the one most attempts at this kind of index get wrong.

**The problem:** "district" is not a stable key in India.
- District *count* is a moving target — roughly 780-800 as of early 2026, up from ~640 at Census 2011, and it keeps rising as states bifurcate districts for administrative convenience.
- District *names* change (Allahabad → Prayagraj, Faizabad → Ayodhha-area renaming) and are spelled inconsistently across sources (Bengaluru Urban vs Bangalore Urban vs Bangalore).
- Different sources use different *vintages*: Census 2011 districts, the districts NFHS-6 (2023-24) was *fielded* across (715 — though district-level factsheets haven't actually been *published* yet as of mid-2026, only national/state tables so far), and current administrative districts (~780-800) are three different partitions of the map.
- Newly created districts often have **no historical data at all** under their new identity — their predecessor district's old data has to be split or inherited.

**The fix: build one canonical district master table before touching any indicator data.**

- Use the **Local Government Directory (LGD) codes** published by the Ministry of Panchayati Raj (data.gov.in) as the canonical district identifier. LGD codes are the closest thing India has to a stable, government-maintained district key, and most recent administrative datasets can be mapped to them.
- This master table needs columns like: `lgd_district_code`, `district_name_current`, `district_name_historical[]`, `state_lgd_code`, `parent_district_if_newly_carved`, `census_2011_district_code`, `effective_from_date`.
- Every single incoming dataset gets a **crosswalk step** — mapped from its native key (Census code, NFHS district name, a state FDA's free-text district field) onto this master table — *before* it is allowed into the processing pipeline. No dataset joins another dataset directly; everything joins through the master.
- For districts created after a source's vintage, define an explicit inheritance rule (e.g., "inherit parent district's value, flagged as `inherited_proxy = true`") rather than silently leaving a null.

Treat this crosswalk table as a living artifact with its own version history — it will need correction passes as you encounter new mismatches, and every score you publish should be traceable to a specific crosswalk version.

---

## 3. Data architecture — offline-first source catalog

*For exact portal URLs, navigation paths, formats, and per-indicator effort ratings, see the companion document `DLMAI_Data_Source_Mapping.md`. The table below is the source-level overview; that document is the indicator-level working checklist for Phase 2 of the roadmap.*

Since no APIs are in scope, every source below is either a bulk download, a published report you parse, or (for the one paid category) a periodic file delivery.

| Source | Gives you | Native granularity | Access method | Cadence | Known limitation |
|---|---|---|---|---|---|
| **Census of India** | Population, age structure, literacy, urbanization, density | District | Bulk CSV/PDF from censusindia.gov.in | Decadal (2011 is the last full release; the next round is now scheduled for 2027, with houselisting operations underway in 2026) | Increasingly stale; needs population-growth-rate projection forward |
| **NFHS-5 (2019-21), current; NFHS-6 (2023-24) pending district release** | Disease prevalence, maternal/child health, insurance coverage, nutrition | District factsheets | IIPS (nfhsiips.in) PDF/dataset downloads | ~5-yearly | NFHS-6 was fielded across 715 districts but only national/state tables are published as of mid-2026 — use NFHS-5's district factsheets as the working source now, swap to NFHS-6 once its district tables are released |
| **Rural Health Statistics (MoHFW)** | PHC/CHC/sub-centre counts, health workforce vacancies | District | Annual bulletin (PDF) | Annual | Rural-skewed; weak on urban private healthcare capacity |
| **National Health Profile (CBHI/NCDC)** | Hospital beds, workforce, disease surveillance | State, partial district | Annual report download | Annual | Granularity inconsistent across states |
| **PMBJP / Jan Aushadhi Kendra locator** | Generic-medicine retail outlet locations (~19,000+ stores nationally, present in every district) | Store-level, aggregable to district | Downloadable store list / locator export | Continuous | A useful affordability/access proxy, not a substitute for the full retail chemist universe |
| **PMJAY / Ayushman Bharat dashboards** | Scheme enrollment, empanelled hospital counts | District (where published) | PIB / National Health Authority published reports | Periodic | District-level publication is inconsistent across states |
| **NITI Aayog SDG India Index / Aspirational Districts Programme** | Composite development indicators | District | Downloadable report/dataset | Periodic | Best used for *validation* of your index, not as a raw input — using it both ways double-counts |
| **State Drug Controller / CDSCO license registers** | Retail & wholesale drug license counts, manufacturing unit counts | District (format varies by state) | State FDA portals, RTI requests | Irregular | The single biggest data-engineering effort in this whole project — every state publishes differently, several don't publish district rollups at all |
| **State Directorates of Economics & Statistics** | District domestic product, employment | District (where published) | State government downloads | Annual/biennial | Not all states publish at district granularity; coverage gaps are themselves informative (often correlate with lower-data-maturity states) |
| **AIOCD AWACS / IQVIA secondary sales data** | Actual pharma sales value by town/district — closest thing to ground truth | Town/district | Paid periodic file delivery (not a live API) | Monthly | **Out of scope for v1.1 (free-sources-only build)**. Kept here for reference only — if paid access becomes available later, use it purely as a validation sample for the ~100-150 towns it covers, never as a full-coverage scoring input |
| **SECC (Socio-Economic Caste Census)** | Poverty markers, household assets | Village/district | Bulk download | One-time, dated | Useful for affordability proxy construction despite its age |
| **Survey of India / Bhuvan district boundary shapefiles** | GIS boundaries for mapping output | District | Bulk download | Updated periodically | Needed only for the output/visualization layer, not for scoring |

**Honest gap to flag up front:** Pillar 5 (competitive intensity) is the hardest pillar to source for free. Drug license registers are fragmented and AIOCD/IQVIA data is paid. Decide early whether to (a) budget for a sample of paid data purely for validation, (b) proxy competitive intensity from manufacturing unit registrations and Jan Aushadhi density, or (c) drop the pillar to a lower weight and disclose the limitation. All three are defensible; pretending the gap doesn't exist is not.

---

## 4. System architecture — the five-layer pipeline

Referencing the diagram above, each layer is a separable module with a defined input/output contract, so any layer can be rebuilt without touching the others.

**Layer 1 — Raw data sources**
Static files only (CSV, XLSX, PDF-extracted tables). Each file lands in `data/raw/<source>/<vintage>/` exactly as downloaded, untouched — this is your audit trail. Nothing here is ever edited in place.

**Layer 2 — District master crosswalk & harmonization** *(the amber layer)*
Every raw file gets mapped onto the LGD-based master table from Section 2. Output is a tidy long-format table: `lgd_district_code, indicator_id, source, vintage, value`. This is where 80% of the real engineering effort goes, and where almost all silent data-quality failures originate if rushed.

**Layer 3 — Data quality & imputation**
Before any statistics happen: completeness audit per indicator per district (what % of districts have real, non-imputed data), then a defined imputation hierarchy for gaps:
1. Same-district trend interpolation (if you have 2+ time points)
2. State-mean substitution
3. Nearest-neighbor imputation using population-matched similar districts
4. Flag as missing and exclude from that indicator's weight, if even that fails

Critically, maintain a **parallel confidence/imputation mask** — a same-shaped matrix recording *which* cells were imputed and by which method. This lets you later compute the index with and without imputed cells to see how much any single district's score depends on guesswork, and lets you report a confidence band, not just a score.

**Layer 4 — Normalization & weighting engine**
Covered in full in Section 5 below. Output: a normalized, weighted indicator table ready for aggregation.

**Layer 5 — Aggregation, validation & output**
Combines normalized/weighted indicators into pillar scores, pillar scores into the final DLMAI score, runs sensitivity analysis, and produces the scorecards/maps described in Section 6.

A cross-cutting principle for all five layers: **every weight, threshold, and imputation rule lives in a config file (YAML/JSON), never hardcoded.** The whole point of separating architecture from implementation is that a domain expert should be able to change "healthcare infrastructure should be 25% not 20% of the score" by editing a number in a config file, not by touching code.

---

## 5. Statistical methodology

This follows the same family of methods used in established composite indices (UNDP's Human Development Index, OECD/JRC's Handbook on Constructing Composite Indicators) — there's no need to invent new statistical machinery here, just apply established practice carefully.

### 5.1 Normalization
For an indicator *i* in district *d*, min-max scale to a common 0-100 range:

```
I(i,d) = (X(i,d) − min_d(X_i)) / (max_d(X_i) − min_d(X_i)) × 100
```

For "lower is better" indicators (infant mortality, poverty rate), invert the direction first:
```
I(i,d) = (max_d(X_i) − X(i,d)) / (max_d(X_i) − min_d(X_i)) × 100
```

Min-max is preferred over z-scores here because the output needs to be intuitively comparable on a fixed 0-100 scale across refresh cycles. Use z-scores only if you specifically want to compare a district's standing *relative to a given year's distribution* rather than on an absolute scale.

### 5.2 Weighting — a hybrid, not a single method
Pure equal-weighting is indefensible (it implicitly claims all 25+ indicators matter equally, which no domain expert believes). Pure expert-judgment weighting risks bias. The standard fix is a **hybrid of AHP and entropy weighting**.

**Step A — AHP at the pillar level (worked example, v1.1).** Domain experts fill a pairwise comparison matrix rating each pillar's importance relative to every other pillar, using Saaty's 1-9 scale (1 = equal importance, 3 = moderate, 5 = strong, 7 = very strong, 9 = extreme, with 2/4/6/8 as intermediate values). The matrix below is a **starting template** — built from the domain reasoning in Section 1.1, with Pillar 5 (Industry presence & supply depth) deliberately judged as consistently less important given its lower data confidence — not a final answer. It should be replaced with judgments from an actual 3-5 person pharma BD/market-access panel before being used for anything real (see the `ahp_pillar_weights.py` script for how to aggregate multiple experts' matrices via geometric mean).

| | P1 Demand | P3 Infra | P2 Econ. access | P4 Distribution | P6 Regulatory | P7 Growth | P5 Industry presence |
|---|---|---|---|---|---|---|---|
| **P1 Demand** | 1 | 2 | 3 | 3 | 5 | 5 | 7 |
| **P3 Healthcare infra** | 1/2 | 1 | 2 | 3 | 4 | 5 | 6 |
| **P2 Economic access** | 1/3 | 1/2 | 1 | 2 | 3 | 3 | 5 |
| **P4 Distribution** | 1/3 | 1/3 | 1/2 | 1 | 2 | 2 | 4 |
| **P6 Regulatory** | 1/5 | 1/4 | 1/3 | 1/2 | 1 | 1 | 3 |
| **P7 Growth momentum** | 1/5 | 1/5 | 1/3 | 1/2 | 1 | 1 | 3 |
| **P5 Industry presence** | 1/7 | 1/6 | 1/5 | 1/4 | 1/3 | 1/3 | 1 |

The principal eigenvector of this matrix gives the weights below. Crucially, the **Consistency Ratio (CR)** has to be checked before trusting any AHP output — it measures whether the judgments are internally coherent (e.g., if you say P1 > P3 and P3 > P2, you shouldn't then say P2 > P1). CR < 0.10 is the standard acceptance threshold:

| Pillar | AHP weight |
|---|---|
| P1 — Demand & disease burden | 33.98% |
| P3 — Healthcare infrastructure | 24.71% |
| P2 — Economic access & affordability | 15.61% |
| P4 — Distribution & retail density | 10.37% |
| P6 — Regulatory & scheme environment | 6.23% |
| P7 — Growth momentum | 6.06% |
| P5 — Industry presence & supply depth | 3.04% |

λ_max = 7.183, CI = 0.030, RI(n=7) = 1.32, **CR = 0.023 — consistent.** Pillar 5's low confidence is reflected as a small (~3%) but non-zero share of the composite score, arrived at by judging it honestly less decisive rather than capping its weight after the fact — that's the more defensible version of "low confidence gets a small say."

If your own panel's matrix comes back with CR ≥ 0.10, don't average your way past it — the `ahp_pillar_weights.py` script flags which pillar's comparisons deviate most from the rest, so you know exactly which judgment to send back to the panel for a second look.

**Step B — Entropy weighting at the indicator level (objective check).** Within each pillar, indicators that vary a lot across the 700+ districts carry more discriminating power than indicators that are nearly flat everywhere; entropy weighting rewards variance:
  ```
  P(i,d) = X(i,d) / Σ_d X(i,d)
  e_i = −k Σ_d P(i,d) ln(P(i,d)),  k = 1/ln(n)
  w_i = (1 − e_i) / Σ_i (1 − e_i)
  ```
  This can only be computed once real district data is loaded (Phase 3-4 of the roadmap), since it depends on the actual distribution of values — unlike AHP, which is a pure judgment exercise that can be done today.

**Step C — Blend.** Use AHP weights as the primary, business-informed structure at the pillar level. Use entropy weights as the primary method *within* each pillar (across its 2-5 indicators) — there's rarely a strong expert view on, say, whether BPL-card share should outweigh wealth-quintile share within the affordability pillar, so let the data's own variance decide that finer-grained split, while AHP decides the coarser, higher-stakes pillar-level split where domain judgment genuinely matters more than data variance.

### 5.3 Aggregation
Two choices, and they're not equivalent:
- **Arithmetic (weighted sum) aggregation** is fully compensatory — a district can offset a weak pillar entirely with a strong one. Reasonable *within* a pillar, where indicators are often genuine substitutes for each other (e.g., two different healthcare-access proxies).
- **Geometric mean aggregation** penalizes imbalance — a district that scores zero on any one pillar gets pulled sharply down overall, because you can't have a thriving pharma market with literally no healthcare infrastructure no matter how rich the population is. This is the same logic UNDP adopted for HDI in 2010, switching from arithmetic to geometric mean specifically to stop very poor performance on one dimension from being masked by strong performance on another.

**Recommendation:** arithmetic mean within each pillar (indicators are substitutable), geometric mean across pillars (pillars are not substitutable):
```
Pillar_p,d = Σ_i w_i × I(i,d)                [within-pillar, weights sum to 1]
DLMAI_d   = Π_p (Pillar_p,d) ^ W_p           [across pillars, weights sum to 1]
```

### 5.4 Validation & sensitivity analysis
A composite index has no ground truth to "test accuracy" against in the way a predictive model does, so validation has to come from a few different angles, used together:
- **Monte Carlo weight perturbation:** randomly jitter the pillar weights within a plausible range thousands of times, and check whether district rankings stay reasonably stable (using Spearman rank correlation between the base case and perturbed runs). A ranking that flips wildly under small weight changes means the index isn't actually decisive — it means the data isn't strong enough to support the precision you're claiming.
- **Partial ground-truth correlation:** for the ~100-150 towns where you do have AIOCD/IQVIA actual sales data, check whether your DLMAI score correlates sensibly with real market size. It won't (and shouldn't) be a perfect match — the index measures *attractiveness*, not *current sales* — but a strong negative or zero correlation is a red flag.
- **Face validity / expert review (Delphi-style):** show the top 20 and bottom 20 ranked districts to 3-5 domain experts without telling them the methodology, and ask if the list passes the smell test. This catches systemic errors no statistical check will surface (e.g., a data field that's accidentally in the wrong units for one state).

---

## 6. Output design

- **DLMAI score:** 0-100 composite, plus percentile rank among all scored districts.
- **Tiering:** translate the continuous score into decision-usable bands, e.g. Tier 1 "Established" (top decile), Tier 2 "Emerging", Tier 3 "Nascent", Tier 4 "Frontier" (bottom quartile) — labels should map to actual go-to-market actions (e.g., "Tier 1 = direct sales force," "Tier 4 = distributor-only / monitor").
- **District scorecard:** for any single district, show the composite score, the pillar-level breakdown (so a user can see *why* a district scored the way it did, not just the final number), and a confidence flag from the imputation mask in Layer 3.
- **Choropleth map:** requires a district boundary shapefile (Survey of India / Bhuvan, downloadable, not an API) joined on the same LGD master codes used everywhere else in the pipeline — this is exactly why the master table from Section 2 has to be airtight; a map is the fastest way to visually expose a bad join (a state that's suspiciously blank or a boundary that doesn't match).

---

## 7. Conceptual module structure (architecture only — no code yet)

```
project_root/
├── data/
│   ├── raw/<source>/<vintage>/          # untouched downloads, audit trail
│   ├── master/district_crosswalk.csv    # the LGD-based canonical table (Section 2)
│   └── processed/                        # post-harmonization, tidy long-format
├── config/
│   ├── pillars.yaml                      # pillar → indicator mapping, direction (higher/lower-better)
│   └── weights.yaml                      # AHP pairwise matrix + entropy blend ratio
├── src/
│   ├── ingestion/        # one module per source, normalizes raw files to a common schema
│   ├── harmonization/    # crosswalk logic against the district master
│   ├── imputation/       # missing-data hierarchy + confidence mask generation
│   ├── normalization/    # min-max scaling
│   ├── weighting/        # AHP + entropy computation
│   ├── aggregation/      # pillar scores → DLMAI
│   └── validation/       # Monte Carlo sensitivity, ground-truth correlation
└── outputs/
    ├── scorecards/        # per-district detail
    ├── maps/               # choropleth-ready exports
    └── reports/            # versioned full-run summaries
```

Each `src/` module takes a clearly defined input shape and produces a clearly defined output shape, independent of how any other module is implemented — this is what lets you swap, say, the imputation method later without touching the weighting engine.

---

## 8. Governance & refresh cycle

- Every full run is versioned and dated (`run_id`, crosswalk version, config version, source vintages used) — a score published in Q1 should be fully reproducible later, including which imputed values went into it.
- Align refresh cadence to your slowest meaningfully-updated input (NFHS rounds every ~5 years, Rural Health Statistics annually) — recompute the full index annually at minimum, but allow a lightweight "infrastructure-only" or "scheme-penetration-only" partial refresh quarterly if those specific layers update faster.
- Maintain a changelog specifically for weight revisions — if you change a pillar weight, you need to be able to show whether a district's apparent year-over-year rank change is due to real-world movement or a methodology change. Never let those two get mixed silently.

---

## 9. Implementation roadmap

| Phase | Focus | Key output |
|---|---|---|
| 0 | Framework lock-in | Final pillar/indicator list, signed off (this document) |
| 1 | District master construction | LGD-based crosswalk table covering all current districts + historical mappings |
| 2 | Data inventory & collection | Every indicator mapped to a real, accessed source file |
| 3 | Harmonization & imputation pipeline | All sources crosswalked into one tidy table, confidence mask in place |
| 4 | Statistical engine | Normalization, AHP + entropy weighting, aggregation — config-driven |
| 5 | Validation | Sensitivity analysis, partial ground-truth check, expert face-validity review |
| 6 | Output layer | Scorecards, tiering, choropleth maps, versioned reports |

---

## 10. Honest limitations to disclose alongside any published score

- Many indicators will not have true native district granularity for all 780-800 current districts — proxying and inheritance from parent districts is necessary for newly carved districts, and this should be visible, not hidden.
- **Industry presence & supply depth (Pillar 5, renamed from Competitive intensity in v1.1)** is built entirely from free company-registration data (MCA21), not sales data — its scores are directional presence signals, not market-share or competitive-saturation measures, and should carry a visibly lower confidence weight than the other six pillars until paid validation data is available.
- District boundary churn means comparing scores across years requires explicit handling of newly created districts — a naive year-over-year diff will misattribute boundary changes as market movement.
- This is a **relative ranking and prioritization tool**, not a sales forecast. It tells you where to look first, not how much revenue to expect.
