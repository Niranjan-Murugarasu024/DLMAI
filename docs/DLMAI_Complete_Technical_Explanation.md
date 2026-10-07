# DLMAI — Complete Technical Explanation
## What has been built, what you're seeing, what it actually means for Sun Pharma

---

## PART 1: THE HONEST STARTING POINT

The model is real, working, and architecturally complete. But the numbers
you are looking at in the dashboard right now are NOT the numbers Sun
Pharma would ever use to make a business decision. Here is why:

  The model is currently running on 22 hand-picked illustrative districts,
  NOT the real 780+ districts across India. Of those 22 districts, only
  17.8% of the data cells contain genuinely measured, real-world numbers.
  The other 82.2% are filled by the model's own imputation engine
  (nearest-neighbor: 52.7%, state-mean: 23.2%, inheritance: 6.2%).

That is the root cause of everything that looks "static" or "off" in
the dashboard. It is not a flaw in the methodology — it is the natural,
expected behaviour of a statistically correct model running on a 22-row
illustrative dataset instead of a real 780-row one. The purpose of this
build was to prove the architecture works correctly so that when you feed
it real data, the output is trustworthy.

---

## PART 2: WHAT THE MODEL ACTUALLY IS

Think of DLMAI as a RECIPE, not a cake. Right now you have a fully
tested, professionally verified recipe, and a small batch of sample
ingredients to show it works. The actual cake — the district scores Sun
Pharma would publish — requires buying the real ingredients (downloading
real government data).

More precisely: DLMAI is a five-stage data pipeline that takes raw
government PDFs and CSVs, processes them through a statistical engine,
and produces one number (0-100) per district, called the "composite
score," representing how attractive that district is as a pharmaceutical
market. That number is built from seven pillars:

  P1  Demand & disease burden       — 33.98% of the final score weight
  P3  Healthcare infrastructure     — 24.71%
  P2  Economic access               — 15.61%
  P4  Distribution & retail density — 10.37%
  P6  Regulatory & scheme env.      —  6.23%
  P7  Growth momentum               —  6.06%
  P5  Industry presence             —  3.04%
                                     -------
                                     100.00%

---

## PART 3: WHY THE NUMBERS LOOK "100" AND "0" AND "STATIC"

This is the critical thing to understand. Let me walk through exactly
what produces those numbers with real evidence.

---------------------------------------------------------------------
REASON A: Min-Max Normalization on a tiny dataset
---------------------------------------------------------------------

Every indicator is scaled from 0 to 100 using this formula:

  score = (raw_value - min_across_all_districts)
        / (max_across_all_districts - min_across_all_districts)
        × 100

The min and max are computed from whichever districts are IN THE CURRENT
RUN. With only 22 districts, the spacing between those extremes is very
compressed. The district with the MOST Jan Aushadhi Kendras in our 22-
district sample gets P4 = 100. The district with ZERO Kendras gets P4 = 0.
These are not "real" absolute scores — they are RELATIVE rankings within
this small pool.

When you run this on all 780 real districts, Bengaluru Urban (which gets
P4 = 100 now because it has the most Kendras in our sample) will almost
certainly not get P4 = 100 anymore — there will be districts with far
more Kendra density. Its score will correctly drop to reflect its true
national standing.

Current P4 distribution (22 districts):
  Bengaluru Urban  → P4 = 100 (has 4 Kendras in mock data — the max)
  Bengaluru Rural  → P4 =   0 (has 0 confirmed Kendras in covered states)
  Coimbatore       → P4 =  75 (has 3 Kendras)
  Pune             → P4 =  50 (has 2 Kendras)
  Prayagraj        → P4 =  42 (interpolated — nearest-neighbor imputed)

At real scale with 780 districts, every one of these numbers will change.

---------------------------------------------------------------------
REASON B: Pillar 6 (Regulatory & Scheme) is almost entirely zeros
---------------------------------------------------------------------

P6 currently has ONLY ONE indicator: the NITI Aayog Aspirational District
flag (a binary 1 or 0 for each district). Of our 22 sample districts,
only ONE — YSR Kadapa — is on the Aspirational Districts list. So P6
scores like this:

  YSR Kadapa: P6 = 100 (only aspirational district in the sample)
  Everyone else: P6 = 0

This is technically correct: in the model's design, P6 was meant to have
PMJAY scheme penetration data as a second indicator, but that source turned
out to be unautomatable (the live dashboard blocks automated access and
only publishes bulk data at the state level, not district level). With a
single binary indicator, every non-aspirational district scores 0.

At real scale, this pillar is the weakest of the seven. Its 6.23% AHP
weight means it has limited influence on the final score, but it still
produces a "P6 = 0 for almost everywhere" pattern that makes the model
look more uniform than it should be in that dimension. This is a known,
documented limitation.

---------------------------------------------------------------------
REASON C: Pillars 1 and 2 have only 3 unique values each
---------------------------------------------------------------------

P1 scores: only 3 distinct values — 84.26, 38.58, 15.74
P2 scores: only 3 distinct values — 95.54, 34.82, 4.46

Why? Because ALL NFHS data in the demo comes from just TWO real factsheet
PDFs (Coimbatore and Kurnool). Every other district's Pillar 1 and 2
data is imputed:

  - Coimbatore: native NFHS data (stunting 18.7%, electricity 99.4%, etc.)
  - Kurnool: native NFHS data (stunting 29.4%, electricity 98.2%, etc.)
  - All Andhra Pradesh districts: inherit or average from Kurnool
  - All other 14 districts: get nearest-neighbor imputed values
    (weighted average of the closest-population districts that DO have
    native data — which is Coimbatore and Kurnool)

So most of the 22 districts are split between "looks like Coimbatore"
and "looks like Kurnool" for Pillars 1 and 2. That is why the pillar
scores cluster into just 3 groups. With real NFHS factsheets for all
715 districts, every district gets its own unique measured values, and
these pillars produce a rich, continuous distribution.

---------------------------------------------------------------------
REASON D: Six Andhra Pradesh districts have identical scores
---------------------------------------------------------------------

Kurnool and Nandyal both score 6.60. Guntur, Palnadu, and Bapatla all
score 6.10. This is 100% correct behaviour:

  Nandyal was carved from Kurnool in the 2022 AP district reorganization.
  It has no pre-existing Census/NFHS/RHS data under its own name. The
  inheritance engine correctly gives Nandyal the same values as Kurnool.
  So their score is identical — because the system is being honest that
  it doesn't have independent data for the child district yet.

  Palnadu and Bapatla were carved from Guntur. Same logic.

At real scale, if Nandyal ever gets its own NFHS factsheet or RHS entry
(which it will once the 2023-24 NFHS district tables are released), its
score will separate from Kurnool's. Until then, the equal scores are
correct.

---

## PART 4: THE COMPLETE FIVE-LAYER TECHNICAL ARCHITECTURE

Here is what has actually been built, layer by layer:

=======================================================================
LAYER 1 — Six data ingestion parsers (what data goes in)
=======================================================================

Six separate Python modules, each built against the verified real
structure of its government source:

Module              Pillars fed    Source                       Status
-------------------------------------------------------------------
nfhs_factsheet      P1, P2        NFHS-5 district PDFs         Real structure, mock PDFs
census_handbook     P1, P7        Census District Handbooks    Real structure, mock PDFs
rhs_parser          P3            Rural Health Statistics      Real numbers, real format
jan_aushadhi        P4            PMBJP Kendra export PDFs     Real structure, mock data
mca21_ingestion     P5            MCA21 company master CSV     Real NIC codes, mock CSV
niti_aspirational   P6            NITI Aayog published list    REAL DATA, all 112 districts

Every module:
  - Was built after actually checking the real government portal
  - Handles the specific structural quirks of that source
    (e.g., blank-name state-total rows in RHS, the dual Women/Men
    occurrence of blood pressure indicators in NFHS, the word-boundary
    NIC code matching in MCA21)
  - Reports everything it couldn't match as a warning, never silently drops data
  - Has its own test file with hand-verified expected values

=======================================================================
LAYER 2 — District crosswalk + inheritance (name resolution)
=======================================================================

This is the most critical engineering component. "District" is not a
stable concept in India:
  - India had ~640 districts at Census 2011, ~780-800 now
  - Names change: Allahabad → Prayagraj, Calcutta → Kolkata
  - Districts split: Kurnool → Kurnool + Nandyal (2022)
  - Sources use different spellings: "Bangalore Urban" vs "Bengaluru Urban"

The crosswalk engine resolves every district name from every source onto
one canonical LGD (Local Government Directory) coded master table using:
  1. Exact match against current name
  2. Historical name lookup (e.g., "Bangalore Urban" found as a historical
     variant of "Bengaluru Urban")
  3. Manual alias table (for renames too different for fuzzy matching,
     e.g., "Bombay" → "Mumbai City")
  4. Fuzzy string matching with explicit ambiguity detection
     (if two districts are equally close, it flags rather than guesses)
  5. Confirmed unmatched (never silently discards — surfaces for review)

The inheritance resolver uses a fixpoint loop (verified to be order-
independent) to fill child districts from their parents for any
pre-bifurcation source data.

=======================================================================
LAYER 3 — Imputation engine (filling gaps)
=======================================================================

For any indicator value that a district is genuinely missing after the
crosswalk and inheritance steps, the imputation hierarchy applies:

  Step 1: Trend interpolation (if 2+ time points exist for that district)
  Step 2: State-mean substitution (average from other districts in
           the same state that DO have native data)
  Step 3: Nearest-neighbor matching (average from k=3 districts with
           the most similar population, nationally)
  Step 4: Still missing — tagged as such, never fabricated

CRITICAL DESIGN: every single imputed cell carries a "status" tag.
When you read 'nearest_neighbor' in the data, it means: "this number
was computed, not measured." The model never hides that. This is what
produces the __status columns in dlmai_combined_output.csv.

The current 22-district run status breakdown:
  native (actually measured)     = 17.8%  — only Coimbatore, Kurnool,
                                            NITI Aayog, some RHS values
  nearest_neighbor (computed)    = 52.7%  — most of the "data"
  state_mean (computed)          = 23.2%
  inherited (passed from parent) =  6.2%

At real scale with all 780 districts and real NFHS/Census/RHS data:
  native should be >70-75% of all cells
  The remaining 25-30% would be genuinely missing districts
  (newly-carved, urban-only exclusions from RHS, etc.)

=======================================================================
LAYER 4 — Scoring engine (producing the index number)
=======================================================================

Step A — Min-max normalize every indicator to 0-100, direction-aware
  (higher stunting = higher score because it signals therapy demand,
   higher out-of-pocket cost = LOWER score because it signals poor access)

Step B — Entropy weighting within each pillar
  Indicators that vary more across districts get more weight, because
  they carry more discriminating power. This is computed per-indicator
  using each indicator's own non-None count (a bug in an earlier version
  used a shared n — fixed in the second round of external review).

Step C — AHP (Analytic Hierarchy Process) weighting across pillars
  A pairwise comparison matrix was used to assign weights to each pillar.
  The consistency ratio (CR = 0.023, well below the 0.10 threshold) was
  verified, confirming the weights are internally coherent. These weights
  currently reflect a single person's domain judgement — the workflow
  to aggregate 3-5 expert opinions via geometric mean is built and ready,
  but no real panel has filled the matrix yet.

Step D — Geometric mean aggregation across pillars
  Using geometric mean instead of arithmetic mean means a district
  cannot "hide" a very weak pillar by being very strong elsewhere.
  A district with no healthcare infrastructure at all (P3 = 0) gets
  a zero composite regardless of how strong its other pillars are.
  This is the right behavior for a market-attractiveness index.

=======================================================================
LAYER 5 — Sensitivity / validation (Monte Carlo)
=======================================================================

3,000 iterations of random pillar-weight perturbation (log-normal,
sigma=0.15 — roughly ±15% relative change per pillar per draw).

For each draw: recomputes all scores → ranks districts → compares to
the base ranking using Spearman correlation.

Current 22-district result:
  Mean Spearman correlation: 0.97 (very stable)
  Coimbatore's #1 position: held in 100% of draws
  Most volatile: Mumbai City (rank swings ±7 positions)

At real scale this is where the model earns its business credibility —
instead of "Coimbatore scores 41.54", you say "Coimbatore is robustly
in the top 5% under any reasonable weighting scheme."

---

## PART 5: WHAT THE MODEL DOES NOT CONTAIN (HONEST GAPS)

Gap                       Why                           Business impact
---------------------------------------------------------------------
Private hospital data     No free district-level        P3 only measures
                          source exists                 public health infra

PMJAY scheme penetration  Dashboard is robot-blocked;   P6 is weaker than
                          only state-level bulk data    intended

NFHS-6 district tables    Not published yet             Using 5-year-old
                          (state/national only)         NFHS-5 data

Census 2021               Postponed — doesn't exist     Using 2011 population
                          yet for districts             projections

Real AHP panel weights    No panel has filled the       Weights reflect one
                          matrix yet                    person's judgment

Real data from all        Only 2 real NFHS PDFs         82% of data is
715 districts             in the current run            imputed, not measured

---

## PART 6: WHAT RUNNING THE REAL MODEL ACTUALLY LOOKS LIKE

To go from the current illustrative demo to something Sun Pharma could
genuinely use, the steps are bounded and clear:

WEEK 1-2:
  Build the real LGD district master (~780-800 districts) from
  lgdirectory.gov.in — the single most important step; everything
  else depends on this being correct.

WEEK 2-4:
  Download 715 NFHS-5 district factsheet PDFs from nfhsiips.in.
  The nfhs_factsheet_parser.py module processes each one automatically.
  Download 36 Jan Aushadhi state-export PDFs (one per state from
  janaushadhi.gov.in). jan_aushadhi_ingestion.py handles each.
  Download the real RHS district health-centre table from nhm.gov.in
  (one file — rhs_parser.py already handles the real format).
  Download Census District Handbooks (census_handbook_parser.py ready).
  Download MCA21 bulk company master CSV from data.gov.in + the LGD
  pincode-to-district dataset to resolve registered-office addresses.

WEEK 4-5:
  Run python3 build_index.py (runs in minutes for 780 districts).
  Do expert face-validity review: show top 20 and bottom 20 districts
  to 3-5 pharma BD/market-access leaders without explaining the model —
  if the list passes their smell test, the model is publishing-ready.
  Run the AHP panel: 3-5 domain experts fill the pairwise comparison
  matrix, replacing the current single-person judgement weights.

WEEK 5-6:
  Deploy to Streamlit Community Cloud (one-time, one-click setup).
  The GitHub Actions quarterly refresh keeps it current automatically.

After this, Sun Pharma has a live, always-on district scoring dashboard
refreshed every quarter, built from publicly verifiable government data,
with full provenance on every number.

---

## PART 7: HOW SUN PHARMA ACTUALLY USES THIS

The model produces three outputs per district:

  1. composite_score (0-100): overall market attractiveness
  2. tier (1-4): action classification
     Tier 1 Established — direct sales force deployment justified
     Tier 2 Emerging    — field force with stockist appointment
     Tier 3 Nascent     — stockist-only with quarterly monitoring
     Tier 4 Frontier    — distributor + periodic review only
  3. Pillar breakdown: WHY a district scored the way it did

The pillar breakdown is the model's real competitive advantage. IQVIA
and AIOCD give you "this territory did ₹X crore" — the DLMAI gives you:
"this territory has HIGH disease burden (P1) but LOW distribution (P4),
meaning demand exists but the supply chain hasn't reached it yet."
That distinction — demand-supply gap vs. demand-supply alignment —
changes the go-to-market action. High-P1/low-P4 means invest in stockist
appointment, not more MRs. High-P1/high-P4/low-P5 means a market with
both demand and distribution but low competitor presence: white space.

The sensitivity analysis adds a third layer. Before presenting "Nashik
scores 68, so we should expand there," a national sales head can see:
"Nashik's rank is stable — it's in the top 20 in 97% of all weight
scenarios." That is the kind of statement that survives scrutiny in a
boardroom. "Our algorithm says so" does not.

---

## PART 8: WHAT WOULD MAKE THE DASHBOARD LOOK LESS "STATIC"

The current dashboard looks static because:
  - 22 districts produces very few unique normalized values
  - Most data is imputed from 2 real data points (Coimbatore, Kurnool)
  - P6 is a binary flag with one entry = one of two possible scores
  - P1 and P2 cluster into 3 groups because there are only 2 native
    data points and all others are interpolated toward them

With real data across 780 districts:
  - Every indicator will have a continuous distribution
  - The map will show meaningful geographic gradients
  - The tier distribution will spread realistically
    (not just Coimbatore anchoring the top and AP anchoring the bottom)
  - The sensitivity analysis will identify genuinely contested middle-
    tier districts where the ranking IS fragile — useful to know

The dashboard code is complete and correct. What it needs is real data.
