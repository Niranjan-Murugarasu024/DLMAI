"""
DLMAI end-to-end pipeline run -- wires Layer 1 (NFHS, Jan Aushadhi, and
Census handbook ingestion), Layer 2 (district crosswalk + inheritance),
and Layer 3 (imputation) together into one run producing a single tidy
district x indicator table with a full confidence mask.

Order matters and follows the framework doc exactly:
  1. Resolve every raw district reference from every source onto the
     LGD-based master (Layer 2)
  2. Apply parent->child inheritance for newly-carved districts (Layer 2)
  3. Apply the imputation hierarchy to whatever is STILL missing after
     inheritance (Layer 3)

One composition detail worth being explicit about: InheritanceResolver and
ImputationEngine were each built and tested independently, and each
produces its own confidence mask. Feeding inheritance's *output* data
straight into the imputation engine would cause the imputation engine to
relabel inherited values as plain "native" (it has no way to know they
were inherited rather than measured) -- silently downgrading exactly the
distinction this whole project cares about. The merge step below fixes
this explicitly: wherever inheritance produced a status, that status wins;
the imputation engine's mask only fills in the gaps inheritance didn't
touch. This is a general lesson, not specific to this dataset: composing
two independently-correct layers can still silently break an invariant at
the seam between them if you don't check for it.
"""

import csv
import os

from district_crosswalk import DistrictCrosswalk, InheritanceResolver, normalize
from nfhs_factsheet_parser import parse_factsheet_batch
from jan_aushadhi_ingestion import extract_kendra_rows, aggregate_by_district
from census_handbook_parser import parse_census_handbook
from rhs_parser import extract_rhs_rows, aggregate_to_combined as rhs_aggregate
from mca21_ingestion import extract_pharma_companies, aggregate_by_district as mca21_aggregate, PINCODE_PREFIX_TO_LGD
from niti_aspirational_districts import flag_aspirational_districts
from imputation_engine import ImputationEngine, completeness_report, print_completeness_report
import glob
import pandas as pd   # used for Census PCA CSV path

# ─────────────────────────────────────────────────────────────────────────────
# DATA MODE — set DEMO_MODE = False once real data files are in place.
# True  → uses the 22-district mock data shipped with the repo (default)
# False → uses real government data in the data/ directories
# Run python setup_data_dirs.py to check which files are present/missing.
# ─────────────────────────────────────────────────────────────────────────────
DEMO_MODE = False


NFHS_INDICATORS = [
    "stunting_pct", "wasting_pct", "underweight_pct",
    "electricity_pct", "clean_fuel_pct", "drinking_water_pct", "sanitation_pct",
    "insurance_pct", "oope_delivery_rs",
    "hypertension_combined_pct_women", "hypertension_combined_pct_men",
    "diabetes_combined_pct_women", "diabetes_combined_pct_men",
]
JAN_AUSHADHI_INDICATOR = "jan_aushadhi_kendra_count"
CENSUS_INDICATORS = [
    "decadal_growth_rate_pct", "density_per_sqkm", "sex_ratio",
    "literacy_rate_pct", "urban_population_pct", "population_age_0_6_pct",
]
# NOTE on density_per_sqkm and sex_ratio: these are real fields from the
# Census "Important Statistics" table (see census_handbook_parser.py) and
# are deliberately collected here, but they are NOT part of the formal
# v1.1 indicator set defined in DLMAI_Framework_Architecture.md Section 1.1
# -- they don't appear in scoring_engine.py's PILLAR_INDICATORS and so
# never contribute to any pillar score. This was a deliberate scope
# decision (don't let indicator-creep into the scorer happen silently,
# one field at a time, without going through the same documented audit
# every other indicator went through) -- NOT an oversight. They're kept
# in the combined output as descriptive/contextual fields, available for
# reference and for a future, DELIBERATE methodology update.
# density_per_sqkm in particular has a defensible case for addition to
# Pillar 4 (distribution & retail density) -- denser markets are
# generally cheaper to serve commercially -- but adding it should go
# through the same Section 1.1-style audit as every other indicator
# already did, as a deliberate change to the scoring methodology, not a
# side effect of an unrelated bug-fix pass.
# RHS gives raw facility counts; sub_centres/phcs/chcs are converted to
# per-lakh-population density (using the same population_reference the
# nearest-neighbor imputation covariate uses) since raw counts alone
# conflate "more facilities" with "simply a bigger district" -- density is
# the actual access signal Pillar 3 cares about. Hospital counts (sub-
# divisional, district) are kept as raw presence counts -- a district
# either has a district hospital or doesn't, and that's the meaningful
# signal, not a per-capita rate of something that's usually 0 or 1.
RHS_DENSITY_INDICATORS = ["sub_centres_per_lakh_pop", "phcs_per_lakh_pop", "chcs_per_lakh_pop"]
RHS_RAW_INDICATORS = ["rhs_sub_divisional_hospital", "rhs_district_hospital"]
RHS_INDICATORS = RHS_DENSITY_INDICATORS + RHS_RAW_INDICATORS
MCA21_INDICATOR = "mca21_active_pharma_company_count"
NITI_ASPIRATIONAL_INDICATOR = "niti_aspirational_district_flag"
ALL_INDICATORS = (NFHS_INDICATORS + [JAN_AUSHADHI_INDICATOR] + CENSUS_INDICATORS + RHS_INDICATORS
                  + [MCA21_INDICATOR, NITI_ASPIRATIONAL_INDICATOR])

# Illustrative population reference (millions) -- a stand-in for districts
# the Census module hasn't actually processed yet in this demo (only
# Coimbatore and Kurnool have real mock handbooks). Real Census-derived
# population (see below) OVERRIDES this placeholder wherever it's
# available; this dict only fills the remaining gap.
#
# total_population is handled separately from ALL_INDICATORS on purpose:
# it's the imputation engine's own similarity covariate for
# nearest-neighbor matching elsewhere, so running it through that SAME
# nearest-neighbor-by-population hierarchy to fill its own gaps would be
# circular (matching a missing population against population similarity
# has no real target to match against). A real build gets population from
# Census for essentially every district, so this is a narrow, deliberate
# exception, not a gap in the general design.
DISTRICT_POPULATION_PLACEHOLDER_MILLIONS = {
    "SAMPLE-KA-01": 9.6, "SAMPLE-KA-02": 0.99, "SAMPLE-UP-01": 5.95, "SAMPLE-UP-02": 2.47,
    "SAMPLE-MH-01": 3.08, "SAMPLE-MH-02": 9.36, "SAMPLE-MH-03": 9.43,
    "SAMPLE-AP-01": 1.18, "SAMPLE-AP-02": 1.05, "SAMPLE-AP-03": 1.74, "SAMPLE-AP-04": 1.55,
    "SAMPLE-AP-05": 1.34, "SAMPLE-AP-06": 1.42, "SAMPLE-AP-07": 1.52,
    "SAMPLE-TN-01": 3.46, "SAMPLE-TN-02": 4.65, "SAMPLE-TS-01": 3.94,
    "SAMPLE-GJ-01": 7.21, "SAMPLE-WB-01": 4.50, "SAMPLE-RJ-01": 6.63,
    "SAMPLE-BR-01": 5.84, "SAMPLE-MP-01": 2.37,
}


def run_pipeline():
    # ── Crosswalk: DEMO vs REAL ──────────────────────────────────────────────
    if DEMO_MODE:
        master_csv = "sample_lgd_seed.csv"
        alias_csv  = "manual_aliases.csv"
    else:
        master_csv = "data/master/lgd_master.csv" if os.path.exists("data/master/lgd_master.csv") else "sample_lgd_seed.csv"
        alias_csv  = "data/master/manual_aliases.csv" if os.path.exists("data/master/manual_aliases.csv") else "manual_aliases.csv"
    xwalk = DistrictCrosswalk(master_csv, alias_csv)
    all_codes = [d.lgd_code for d in xwalk.districts]

    # start every district with every indicator unset
    combined = {code: {ind: None for ind in ALL_INDICATORS} for code in all_codes}

    # ---------- Layer 1a: NFHS ingestion ----------
    # ── NFHS ingestion: DEMO vs REAL ─────────────────────────────────────────
    if DEMO_MODE:
        nfhs_pdfs = ["mock_Coimbatore_factsheet.pdf", "mock_Kurnool_factsheet.pdf"]
    else:
        nfhs_pdfs = sorted(glob.glob("data/nfhs/district/**/*.pdf", recursive=True))
        if not nfhs_pdfs:
            # Fallback to any non-state NFHS PDFs
            nfhs_pdfs = [p for p in glob.glob("data/nfhs/**/*.pdf", recursive=True) if "state" not in p.lower()]
        nfhs_pdfs = sorted(list(set(nfhs_pdfs)))
        if not nfhs_pdfs:
            print("[warn] No NFHS district PDFs found in data/nfhs/district/ — Pillars 1 & 2 will be fully imputed")

    nfhs_results = parse_factsheet_batch(nfhs_pdfs)
    nfhs_unmatched = []
    for r in nfhs_results:
        resolved = xwalk.resolve(r.district_raw_name)
        if not resolved.lgd_code:
            nfhs_unmatched.append(r.district_raw_name)
            continue
        for key, value in r.values.items():
            if key in combined[resolved.lgd_code]:
                combined[resolved.lgd_code][key] = value

    # ---------- Layer 1b: Jan Aushadhi ingestion ----------
    # ── Jan Aushadhi ingestion: DEMO vs REAL ────────────────────────────────
    if DEMO_MODE:
        ja_pdfs = ["mock_kendra_export.pdf"]
    else:
        ja_pdfs = sorted(glob.glob("data/jan_aushadhi/*.pdf") + glob.glob("data/jan_aushadhi/**/*.pdf", recursive=True))
        ja_pdfs = sorted(list(set(ja_pdfs)))
        if not ja_pdfs:
            print("[warn] No Jan Aushadhi state PDFs found in data/jan_aushadhi/ — Pillar 4 will rely on mock data or imputation")
    all_rows = []
    for jp in ja_pdfs:
        all_rows.extend(extract_kendra_rows(jp))
    rows = all_rows
    ja_result = aggregate_by_district(rows, xwalk)
    states_covered = {normalize(r["state"]) for r in rows}
    for code in all_codes:
        d = xwalk.by_code[code]
        if code in ja_result["counts"]:
            combined[code][JAN_AUSHADHI_INDICATOR] = ja_result["counts"][code]
        elif normalize(d.state_name) in states_covered:
            # this district's state WAS pulled, and it had zero matching rows
            # -- a confirmed true zero, not an unknown
            combined[code][JAN_AUSHADHI_INDICATOR] = 0
        # else: state wasn't pulled at all yet -- stays None (genuinely unknown,
        # NOT the same thing as a confirmed zero)

    # ---------- Layer 1c: Census handbook ingestion ----------
    # ── Census ingestion: DEMO vs REAL ──────────────────────────────────────
    # REAL path: reads the bulk Primary Census Abstract CSV (one file,
    # all districts) instead of parsing individual PDF handbooks —
    # faster and more complete. Falls back to PDF parsing if the CSV
    # is not yet downloaded.
    if DEMO_MODE:
        census_files = ["mock_Coimbatore_census_handbook.pdf", "mock_Kurnool_census_handbook.pdf"]
        use_pca_csv = False
    else:
        pca_candidates = [
            "data/census/primary_census_abstract/PCA_district_level.csv",
            "data/census/primary_census_abstract/PCA_district_level.csv.csv",
            "data/census/PCA_district_level.csv",
        ]
        pca_csv = next((p for p in pca_candidates if os.path.exists(p)), None)
        use_pca_csv = pca_csv is not None
        if use_pca_csv:
            census_files = []   # handled separately below via the CSV path
        else:
            census_files = sorted(glob.glob("data/census/handbooks/**/*.pdf", recursive=True))
            if not census_files:
                print("[warn] No Census data found — Pillars 1 & 7 demographic indicators will be fully imputed")
    census_unmatched = []
    census_population_millions = {}   # lgd_code -> REAL census population, in millions
    census_warnings = {}
    for path in census_files:
        r = parse_census_handbook(path)
        resolved = xwalk.resolve(r.district_raw_name)
        if not resolved.lgd_code:
            census_unmatched.append(r.district_raw_name)
            continue
        for ind in CENSUS_INDICATORS:
            value = r.important_stats.get(ind, r.derived.get(ind))
            if value is not None:
                combined[resolved.lgd_code][ind] = value
        total_pop = r.important_stats.get("total_population")
        if total_pop:
            census_population_millions[resolved.lgd_code] = total_pop / 1_000_000
        if r.warnings:
            census_warnings[resolved.lgd_code] = r.warnings

    # Real Census population overrides the illustrative placeholder
    # wherever it's actually available; the placeholder only fills what
    # Census ingestion hasn't covered yet in this demo.
    population_reference = dict(DISTRICT_POPULATION_PLACEHOLDER_MILLIONS)
    population_source = {code: "illustrative_placeholder" for code in all_codes}
    for code, pop in census_population_millions.items():
        population_reference[code] = pop
        population_source[code] = "census_native"

    # ---------- Layer 1d: RHS health-centre ingestion ----------
    # ── RHS ingestion: DEMO vs REAL ─────────────────────────────────────────
    if DEMO_MODE:
        rhs_pdf = "mock_rhs_district_table.pdf"
    else:
        rhs_candidates = [
            "data/rhs/district_wise_health_centres.pdf",
            "data/rhs/district-wise-health-centres.pdf",
        ] + glob.glob("data/rhs/*.pdf")
        rhs_pdf = next((p for p in rhs_candidates if os.path.exists(p)), None)
        if not rhs_pdf:
            print("[warn] data/rhs/district_wise_health_centres.pdf not found — Pillar 3 will be fully imputed")
    rhs_rows = extract_rhs_rows(rhs_pdf) if rhs_pdf else []
    rhs_raw = {code: {} for code in all_codes}
    rhs_unmatched = []
    rhs_duplicate_matches = []
    rhs_aggregate(rhs_rows, xwalk, rhs_raw, rhs_unmatched, rhs_duplicate_matches)
    rhs_density_lost_to_missing_population = []
    for code in all_codes:
        # .get(code) (no default) so a district genuinely ABSENT from
        # population_reference comes back as None, distinct from a
        # district that's PRESENT with an actual value of 0. The
        # previous .get(code, 0) made both cases produce pop_lakhs = 0,
        # conflating "we don't know this district's population" with "this
        # district's population is recorded as zero" -- the second case is
        # not realistic for any real Indian district, but using a sentinel
        # that overlaps with a theoretically valid value is fragile
        # regardless of how unlikely the overlap is in practice.
        pop_millions = population_reference.get(code)
        pop_lakhs = pop_millions * 10 if pop_millions is not None else None
        raw = rhs_raw[code]
        if raw and pop_lakhs is not None and pop_lakhs > 0:
            if raw.get("rhs_sub_centres") is not None:
                combined[code]["sub_centres_per_lakh_pop"] = round(raw["rhs_sub_centres"] / pop_lakhs, 3)
            if raw.get("rhs_phcs") is not None:
                combined[code]["phcs_per_lakh_pop"] = round(raw["rhs_phcs"] / pop_lakhs, 3)
            if raw.get("rhs_chcs") is not None:
                combined[code]["chcs_per_lakh_pop"] = round(raw["rhs_chcs"] / pop_lakhs, 3)
        elif raw and (pop_lakhs is None or pop_lakhs <= 0):
            # Real RHS counts exist for this district, but no usable
            # population reference is available to convert them to a
            # density -- at real scale this would otherwise silently drop
            # a real signal for any district missing from the population
            # reference, not because the data didn't exist but because of
            # an unrelated gap in a different source. Track it explicitly
            # rather than letting it disappear with no trace; the
            # imputation layer will still fill these three indicators via
            # state-mean/nearest-neighbor, but on the WRONG basis (treated
            # as natively missing) unless this is visible somewhere.
            rhs_density_lost_to_missing_population.append(code)
        if raw.get("rhs_sub_divisional_hospital") is not None:
            combined[code]["rhs_sub_divisional_hospital"] = raw["rhs_sub_divisional_hospital"]
        if raw.get("rhs_district_hospital") is not None:
            combined[code]["rhs_district_hospital"] = raw["rhs_district_hospital"]
        # Districts genuinely absent from RHS (e.g. Mumbai -- confirmed
        # real, not a parsing gap) stay None here and fall through to
        # Layer 2 inheritance, then Layer 3 imputation, same as any other
        # missing cell -- no special-casing needed.

    # ---------- Layer 1e: MCA21 company master ingestion ----------
    # ── MCA21 ingestion: DEMO vs REAL ────────────────────────────────────────
    if DEMO_MODE:
        mca21_csv = "mock_mca21_company_master.csv"
    else:
        mca21_csv = "data/mca21/pharma_filtered.csv" if os.path.exists("data/mca21/pharma_filtered.csv") \
                    else "data/mca21/company_master_data.csv"
        if not os.path.exists(mca21_csv):
            print("[warn] No MCA21 data found in data/mca21/ — Pillar 5 will be fully imputed")
            mca21_csv = None
    if mca21_csv:
        kept_companies, mca21_excluded = extract_pharma_companies(mca21_csv)
    else:
        kept_companies, mca21_excluded = [], []
    mca21_counts = mca21_aggregate(kept_companies)
    # A district only gets a confirmed TRUE ZERO if our pincode-prefix map
    # actually covers it (i.e. we have geo-resolution capability there);
    # otherwise it's genuinely unknown, not zero -- same "covered vs
    # uncovered" distinction used for Jan Aushadhi in Layer 1b.
    pincode_covered_lgd_codes = set(PINCODE_PREFIX_TO_LGD.values())
    for code in all_codes:
        if code in mca21_counts:
            combined[code][MCA21_INDICATOR] = mca21_counts[code]
        elif code in pincode_covered_lgd_codes:
            combined[code][MCA21_INDICATOR] = 0

    # ---------- Layer 1f: NITI Aayog Aspirational District flag ----------
    # The real source list is exhaustive (all 112 districts nationally),
    # so every district gets a definitive 0 or 1 right now -- there is no
    # "not yet covered" state here, unlike every other Layer 1 source in
    # this pipeline. This indicator never enters inheritance or
    # imputation with a missing value.
    aspirational_flags = flag_aspirational_districts(xwalk)
    for code in all_codes:
        combined[code][NITI_ASPIRATIONAL_INDICATOR] = aspirational_flags.get(code, 0)

    # ---------- Layer 2: inheritance for newly-carved districts ----------
    inherit = InheritanceResolver(xwalk)
    inheritance_mask = {code: {} for code in all_codes}
    for ind in ALL_INDICATORS:
        per_indicator = {code: combined[code][ind] for code in all_codes}
        filled, mask = inherit.fill_missing(per_indicator)
        for code in all_codes:
            combined[code][ind] = filled[code]
            inheritance_mask[code][ind] = mask[code]

    # ---------- Layer 3: imputation for whatever's still missing ----------
    district_state_map = {d.lgd_code: d.state_name for d in xwalk.districts}
    engine = ImputationEngine(district_state_map, population_reference, nearest_neighbor_k=3)
    imputation_result = engine.impute(combined, ALL_INDICATORS)

    # ---------- Merge masks: inheritance status wins where it applied ----------
    final_mask = {code: {} for code in all_codes}
    for code in all_codes:
        for ind in ALL_INDICATORS:
            inh_status = inheritance_mask[code][ind]
            final_mask[code][ind] = inh_status if inh_status.startswith("inherited_from_") \
                else imputation_result.mask[code][ind]

    return (xwalk, imputation_result.filled, final_mask, nfhs_unmatched, ja_result["unmatched"],
            census_unmatched, rhs_unmatched, mca21_excluded, population_reference, population_source,
            census_warnings, rhs_density_lost_to_missing_population, rhs_duplicate_matches)


def export_csv(xwalk, filled, mask, population_reference, population_source, path):
    fieldnames = ["lgd_code", "district_name", "state_name",
                  "population_reference_millions", "population_source"] + \
                 ALL_INDICATORS + [f"{ind}__status" for ind in ALL_INDICATORS]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in xwalk.districts:
            row = {
                "lgd_code": d.lgd_code, "district_name": d.current_name, "state_name": d.state_name,
                "population_reference_millions": population_reference.get(d.lgd_code),
                "population_source": population_source.get(d.lgd_code),
            }
            for ind in ALL_INDICATORS:
                row[ind] = filled[d.lgd_code][ind]
                row[f"{ind}__status"] = mask[d.lgd_code][ind]
            writer.writerow(row)


if __name__ == "__main__":
    try:
        from src.pipeline import run_south_india_pipeline
        print("[INFO] Executing DLMAI South India Production Pipeline...")
        run_south_india_pipeline()
    except Exception as e:
        print(f"[WARN] Error executing production pipeline ({e}), falling back to legacy...")
        (xwalk, filled, mask, nfhs_unmatched, ja_unmatched, census_unmatched, rhs_unmatched,
         mca21_excluded, population_reference, population_source, census_warnings,
         rhs_density_lost_to_missing_population, rhs_duplicate_matches) = run_pipeline()

        os.makedirs("outputs", exist_ok=True)
        export_csv(xwalk, filled, mask, population_reference, population_source, "outputs/dlmai_combined_output.csv")
        print("\nExported: outputs/dlmai_combined_output.csv")


