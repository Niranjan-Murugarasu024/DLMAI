"""
DLMAI scoring engine — Layer 4 (normalization, weighting, aggregation).

Implements Section 5 of DLMAI_Framework_Architecture.md exactly:
  5.1 Min-max normalization (direction-aware: higher-is-better vs lower-is-better)
  5.2 Entropy weighting within each pillar, AHP weighting across pillars
       (using the actual validated weights from ahp_pillar_weights.py:
       P1=33.98%, P3=24.71%, P2=15.61%, P4=10.37%, P6=6.23%, P7=6.06%, P5=3.04%)
  5.3 Arithmetic mean within pillar, geometric mean across pillars

HONEST HANDLING OF MISSING PILLARS -- this is the part that matters most
right now: only Pillars 1, 2, 4, and 7 have any real ingested data so far
(P3 Healthcare Infrastructure, P5 Industry Presence, and P6 Regulatory &
Scheme have no built ingestion source yet). Those three pillars alone
carry 24.71 + 3.04 + 6.23 = 33.98% of the FULL AHP weight -- over a third.
Silently dropping them and renormalizing across the rest is the only
honest way to produce a usable score today, but it would be dishonest to
present that renormalized score as if it carries the same meaning as a
full 7-pillar score. So this module always reports `pillar_coverage_pct`
(the share of the FULL AHP weight that's actually backed by data) right
alongside every score, and the composite is explicitly a "partial DLMAI
score" until Pillars 3, 5, and 6 exist.
"""

import math

# --- Direction: does a HIGHER value make a district MORE pharma-attractive? ---
DIRECTION = {
    # Pillar 1 -- demand & disease burden (lower disease burden isn't more
    # attractive in the literal sense, but higher prevalence/worse outcomes
    # DOES mean higher therapy demand -- so these are scored "higher", on
    # purpose, as a DEMAND signal, not a wellbeing signal. Worth flagging
    # explicitly: this index measures market size, not population health,
    # and the two point in opposite directions for these particular fields.
    "stunting_pct": "higher", "wasting_pct": "higher", "underweight_pct": "higher",
    "hypertension_combined_pct_women": "higher", "hypertension_combined_pct_men": "higher",
    "diabetes_combined_pct_women": "higher", "diabetes_combined_pct_men": "higher",
    "population_age_0_6_pct": "higher", "urban_population_pct": "higher",
    # Pillar 2 -- economic access & affordability
    "electricity_pct": "higher", "clean_fuel_pct": "higher",
    "drinking_water_pct": "higher", "sanitation_pct": "higher", "insurance_pct": "higher",
    "oope_delivery_rs": "lower",   # higher out-of-pocket cost = worse affordability
    # Pillar 4 -- distribution & retail density
    "jan_aushadhi_kendra_count": "higher",
    # Pillar 7 -- growth momentum
    "decadal_growth_rate_pct": "higher", "literacy_rate_pct": "higher",
    # Pillar 3 -- healthcare infrastructure (public-sector skew, see
    # Section 1.1 of the framework doc -- RHS only, no private-sector data)
    "sub_centres_per_lakh_pop": "higher", "phcs_per_lakh_pop": "higher",
    "chcs_per_lakh_pop": "higher", "rhs_sub_divisional_hospital": "higher",
    "rhs_district_hospital": "higher",
    # Pillar 5 -- industry presence (MCA21 active pharma company registrations)
    "mca21_active_pharma_company_count": "higher",
    # Pillar 6 -- regulatory & scheme environment. DELIBERATE, CONTESTABLE
    # JUDGMENT CALL (same category as Pillar 5's sign-convention decision
    # in the framework doc's Section 1): Aspirational District status is
    # scored "higher" here on the theory that it signals intensified
    # government scheme rollout and policy attention (more PMJAY/Jan
    # Aushadhi push, lower regulatory friction) -- a tailwind for market
    # entry. The equally defensible OPPOSITE reading is that Aspirational
    # status mainly signals weak purchasing power and distribution
    # infrastructure, which should count against attractiveness. This
    # module picks the tailwind reading and documents it; it does not
    # claim that reading is objectively correct. Flip DIRECTION's entry
    # for this indicator to "lower" if your panel disagrees -- that's a
    # one-line change, by design.
    "niti_aspirational_district_flag": "higher",
}

PILLAR_INDICATORS = {
    # NOTE: run_pipeline.py's CENSUS_INDICATORS also collects
    # density_per_sqkm and sex_ratio -- deliberately NOT included in any
    # pillar below. See the note next to that list for why; this isn't
    # an omission, but it IS a real, intentional scope boundary worth
    # knowing about if you're looking for them here and not finding them.
    "P1": ["stunting_pct", "wasting_pct", "underweight_pct",
           "hypertension_combined_pct_women", "hypertension_combined_pct_men",
           "diabetes_combined_pct_women", "diabetes_combined_pct_men",
           "population_age_0_6_pct", "urban_population_pct"],
    "P2": ["electricity_pct", "clean_fuel_pct", "drinking_water_pct",
           "sanitation_pct", "insurance_pct", "oope_delivery_rs"],
    "P3": ["sub_centres_per_lakh_pop", "phcs_per_lakh_pop", "chcs_per_lakh_pop",
           "rhs_sub_divisional_hospital", "rhs_district_hospital"],   # Healthcare infrastructure -- now built (RHS ingestion)
    "P4": ["jan_aushadhi_kendra_count"],
    "P5": ["mca21_active_pharma_company_count"],   # Industry presence -- now built (MCA21 ingestion)
    "P6": ["niti_aspirational_district_flag"],   # Regulatory & scheme -- now built (NITI Aayog); PMJAY excluded, confirmed non-viable (see niti_aspirational_districts.py docstring)
    "P7": ["decadal_growth_rate_pct", "literacy_rate_pct"],
}

# From ahp_pillar_weights.py's validated output (CR = 0.023, consistent)
AHP_PILLAR_WEIGHTS = {
    "P1": 0.3398, "P3": 0.2471, "P2": 0.1561, "P4": 0.1037,
    "P6": 0.0623, "P7": 0.0606, "P5": 0.0304,
}

PILLAR_NAMES = {
    "P1": "Demand & disease burden", "P2": "Economic access & affordability",
    "P3": "Healthcare infrastructure", "P4": "Distribution & retail density",
    "P5": "Industry presence & supply depth", "P6": "Regulatory & scheme environment",
    "P7": "Growth momentum",
}

# ─────────────────────────────────────────────────────────────────────────────
# FORMULA CONFIGURATION (image formula, Section 5.3)
#
# DMAI_i = ( Σ_{p∈{1,2,3,4,6,7}} w_p · S_{i,p} ) − ( W5_DAMPENER · S_{i,5} )
#
# Pillars 1,2,3,4,6,7 are VALUE DRIVERS: higher score = more attractive.
# Pillar 5 is a VALUE DAMPENER: higher competitive intensity subtracts from
# the composite score. This makes the model agnostic to company strategy —
# any pharma company (not just Sun Pharma) can use this to find white-space
# markets where demand is high but competition has not yet arrived.
#
# W5_DAMPENER: the penalty coefficient applied to the Pillar 5 score.
#   Range:  0.10 (mild penalty) to 0.20 (strong penalty)
#   Default: 0.15 (midpoint of the range specified in the formula image)
#   To change: edit this one number. It lives here deliberately — in the
#   config, not buried inside a function.
#
# NOTE ON DIRECTION: mca21_active_pharma_company_count stays direction=
# "higher" in the DIRECTION dict. That means a district with MORE
# registered pharma companies gets a HIGHER S_{i,5} normalized score,
# which then gets SUBTRACTED from the composite — correctly penalising
# saturated markets more than sparse ones.
# ─────────────────────────────────────────────────────────────────────────────
W5_DAMPENER = 0.15          # configurable: 0.10 (mild) to 0.20 (strong)
VALUE_DRIVER_PILLARS = ["P1", "P2", "P3", "P4", "P6", "P7"]
VALUE_DAMPENER_PILLAR = "P5"


def min_max_normalize(district_values: dict, direction: str) -> dict:
    """
    district_values: {lgd_code: value_or_None}. Returns {lgd_code: 0-100_or_None}.

    A None here means STATUS_STILL_MISSING survived all the way from the
    imputation layer -- genuinely no value exists for this district on
    this indicator (no native data, no same-state peers, no population
    reference to match against). This is rare in practice (it's exactly
    the failure mode the imputation hierarchy's three fallback steps
    exist to avoid), but it CAN happen at real scale for a sufficiently
    isolated district, and silently crashing the entire scoring run for
    EVERY district over one missing cell in one district is the wrong
    failure mode. Instead: None is excluded from the min/max range (so
    one missing district can't corrupt the scale for everyone else) and
    passed straight through as None in the output -- never fabricated
    into a number. Downstream (score_districts), a None here causes that
    one district to have its pillar weights renormalized among whatever
    indicators it DOES have, the same coverage-aware principle already
    used when an entire pillar is missing, just applied per-district.
    """
    known = {code: v for code, v in district_values.items() if v is not None}
    if not known:
        return {code: None for code in district_values}
    lo, hi = min(known.values()), max(known.values())
    out = {}
    for code, v in district_values.items():
        if v is None:
            out[code] = None
            continue
        if hi == lo:
            # no variance across districts with a real value -- nothing to
            # discriminate on, park everyone at the midpoint rather than
            # dividing by zero or arbitrarily picking a winner
            out[code] = 50.0
            continue
        frac = (v - lo) / (hi - lo)
        out[code] = 100 * frac if direction == "higher" else 100 * (1 - frac)
    return out


def entropy_weights(normalized_by_indicator: dict) -> dict:
    """
    normalized_by_indicator: {indicator_id: {lgd_code: normalized_value_or_None}}
    Returns {indicator_id: weight}, weights summing to 1. Indicators with
    more cross-district variance (more "discriminating power") get more
    weight -- see framework doc Section 5.2, Step B for the formula.
    None values (still-missing districts) are excluded from the
    discriminating-power calculation -- a handful of missing districts
    shouldn't be allowed to distort how informative an indicator is
    judged to be across everyone else.

    IMPORTANT: n (and therefore k = 1/ln(n)) is computed PER INDICATOR,
    from that indicator's own non-None count -- not borrowed from
    whichever indicator happens to be first in the dict. Different
    indicators in the same pillar can have different numbers of missing
    districts (Census might be missing for 3 districts, NFHS for a
    different 5), and k is the normalizing constant that makes a
    perfectly constant indicator come out to EXACTLY zero diversification
    regardless of how many districts it covers. Using a mismatched k from
    a different indicator's n breaks that guarantee -- two equally
    uninformative (constant-valued) indicators with different non-None
    counts would get arbitrarily different, nonzero weights instead of
    both correctly landing at zero. Caught by an external code review,
    confirmed empirically before fixing: a 20-district constant indicator
    and an 18-district constant indicator landed at weights 0.0 and 1.0
    respectively before this fix, despite both being equally
    uninformative.
    """
    indicator_ids = list(normalized_by_indicator.keys())
    if len(indicator_ids) == 1:
        return {indicator_ids[0]: 1.0}

    diversification = {}
    for ind in indicator_ids:
        values = [v for v in normalized_by_indicator[ind].values() if v is not None]
        n = len(values)
        if n < 2:
            diversification[ind] = 0.0
            continue
        k = 1 / math.log(n)
        total = sum(values)
        if total == 0:
            diversification[ind] = 0.0
            continue
        e = 0.0
        for v in values:
            if v > 0:
                p = v / total
                e -= p * math.log(p)
        diversification[ind] = 1 - k * e

    total_div = sum(diversification.values())
    # Use a tolerance, not exact equality: when every indicator is
    # effectively constant, floating-point rounding in the k*e
    # computation almost never lands exactly on 0.0 for every indicator
    # simultaneously (one might compute to 0.0, another to -2.22e-16) --
    # dividing by a total that's only "zero" up to floating-point noise
    # produces an arbitrary, noise-dominated ratio (confirmed empirically:
    # this produced a 0.0 / 1.0 split between two EQUALLY uninformative
    # indicators before this fix, rather than the correct equal-weight
    # fallback). A small absolute tolerance catches this reliably without
    # affecting any case with real, meaningful diversification.
    if abs(total_div) < 1e-9:
        return {ind: 1 / len(indicator_ids) for ind in indicator_ids}
    return {ind: diversification[ind] / total_div for ind in indicator_ids}


def score_districts(filled: dict, all_codes: list) -> dict:
    """
    filled: {lgd_code: {indicator_id: value_or_None}} -- the Layer 3
        output. In the overwhelming majority of cases every value is
        non-None (that's the whole point of the imputation hierarchy),
        but a genuinely isolated district can still leave a None behind
        (STATUS_STILL_MISSING) -- handled explicitly below rather than
        assumed away.
    Returns a dict keyed by lgd_code, each containing:
        composite_score, pillar_coverage_pct (THIS district's actual AHP
        weight share, accounting for any per-district pillar gaps),
        global_pillar_coverage_pct (the dataset-wide figure -- which
        pillars have data ANYWHERE, same for every district), pillar_scores
        (dict), pillar_weights_renormalized (dict), tier
    """
    # --- normalize every indicator across all districts, once ---
    normalized = {}
    for pillar, indicators in PILLAR_INDICATORS.items():
        for ind in indicators:
            raw = {code: filled[code][ind] for code in all_codes}
            normalized[ind] = min_max_normalize(raw, DIRECTION[ind])

    # --- entropy weights (global, per pillar) + pillar scores (per district) ---
    pillar_scores = {}  # pillar_id -> {lgd_code: score_or_None}
    for pillar, indicators in PILLAR_INDICATORS.items():
        if not indicators:
            continue
        weights = entropy_weights({ind: normalized[ind] for ind in indicators})
        scores_this_pillar = {}
        for code in all_codes:
            # Use only the indicators THIS district actually has a value
            # for, renormalizing the entropy weights among just those --
            # the same coverage-aware principle used at the pillar level
            # below, applied per-district. If a district has none of this
            # pillar's indicators (vanishingly rare -- would mean total
            # data desert for this one pillar for this one district),
            # the pillar score is None for that district specifically,
            # not a fabricated number.
            available = [ind for ind in indicators if normalized[ind][code] is not None]
            if not available:
                scores_this_pillar[code] = None
                continue
            weight_sum = sum(weights[ind] for ind in available)
            scores_this_pillar[code] = sum(
                (weights[ind] / weight_sum) * normalized[ind][code] for ind in available
            )
        pillar_scores[pillar] = scores_this_pillar

    available_pillars = list(pillar_scores.keys())
    coverage_weight_sum = sum(AHP_PILLAR_WEIGHTS[p] for p in available_pillars)

    # --- composite: image formula (arithmetic weighted sum minus dampener) ---
    # DMAI_i = ( Σ_{p∈drivers} (w_p/Σw_drivers) · S_{i,p} ) - ( W5_DAMPENER · S_{i,5} )
    # Step 1: compute the renormalized positive-pillar weights (excluding P5
    #         from the denominator so the driver weights sum to 1 among themselves)
    # Step 2: subtract W5_DAMPENER * S_{i,5} as a penalty for competitive saturation
    # Step 3: clamp the final result to [0, 100] -- the penalty term can push
    #         a district below zero if competition is very high and demand is very
    #         low; clamping keeps scores on an interpretable scale without
    #         fabricating a meaningful negative number.
    all_composites = {}
    per_district_pillar_weights = {}
    for code in all_codes:
        usable_drivers = [p for p in VALUE_DRIVER_PILLARS
                          if p in pillar_scores and pillar_scores[p][code] is not None]
        has_dampener = (VALUE_DAMPENER_PILLAR in pillar_scores and
                        pillar_scores[VALUE_DAMPENER_PILLAR][code] is not None)

        if not usable_drivers:
            # No driver data at all for this district -- truly unscoreable
            all_composites[code] = None
            per_district_pillar_weights[code] = {}
            continue

        # Renormalize driver weights among the drivers this district actually has
        driver_w_sum = sum(AHP_PILLAR_WEIGHTS[p] for p in usable_drivers)
        district_weights = {p: AHP_PILLAR_WEIGHTS[p] / driver_w_sum for p in usable_drivers}

        # Arithmetic weighted sum of driver pillars
        driver_score = sum(district_weights[p] * pillar_scores[p][code] for p in usable_drivers)

        # Subtract the competitive-intensity dampener
        if has_dampener:
            dampener_score = W5_DAMPENER * pillar_scores[VALUE_DAMPENER_PILLAR][code]
            district_weights[VALUE_DAMPENER_PILLAR] = -W5_DAMPENER  # stored negative to signal dampener
        else:
            dampener_score = 0.0

        per_district_pillar_weights[code] = district_weights
        raw_composite = driver_score - dampener_score
        all_composites[code] = max(0.0, min(100.0, raw_composite))  # clamp to [0,100]

    # Rank once via enumerate over the sorted list (O(n log n) total) and
    # look ranks up from a dict, instead of calling list.index() inside
    # the per-district loop (O(n) per call -> O(n^2) overall, and at real
    # scale -- ~800 districts -- worth avoiding even though it wouldn't
    # have been a problem at 22). Ties are deliberately kept on the SAME
    # rank/tier here: two districts with an identical composite score
    # belong in the same tier -- there's no principled way to split them,
    # so this isn't "fixed" to break ties arbitrarily.
    valid_codes = [c for c in all_codes if all_composites[c] is not None]
    sorted_codes = sorted(valid_codes, key=lambda c: -all_composites[c])
    rank_of_score = {}
    for i, code in enumerate(sorted_codes):
        rank_of_score.setdefault(all_composites[code], i)
    n = len(sorted_codes)

    def tier_for(score):
        if score is None or n == 0:
            return "Unscored - insufficient data"
        pct = rank_of_score[score] / n
        if pct < 0.25:
            return "Tier 1 - Established"
        elif pct < 0.50:
            return "Tier 2 - Emerging"
        elif pct < 0.75:
            return "Tier 3 - Nascent"
        return "Tier 4 - Frontier"

    results = {}
    for code in all_codes:
        composite = all_composites[code]
        usable_pillars = list(per_district_pillar_weights[code].keys())
        # Coverage = share of AHP weight backed by real data for driver pillars only
        # (the dampener pillar is stored with a negative weight in per_district_pillar_weights
        # to flag it as a penalty, not a positive contributor -- exclude it from coverage %)
        usable_drivers_this = [p for p in usable_pillars if p != VALUE_DAMPENER_PILLAR]
        district_coverage_weight_sum = sum(AHP_PILLAR_WEIGHTS[p] for p in usable_drivers_this)
        results[code] = {
            "composite_score": round(composite, 2) if composite is not None else None,
            "pillar_coverage_pct": round(100 * district_coverage_weight_sum, 1),
            "global_pillar_coverage_pct": round(100 * coverage_weight_sum, 1),
            "pillar_scores": {p: round(pillar_scores[p][code], 2)
                               for p in usable_pillars if pillar_scores[p][code] is not None},
            "pillar_weights_renormalized": {p: round(w, 4)
                                              for p, w in per_district_pillar_weights[code].items()},
            "dampener_applied": round(W5_DAMPENER * pillar_scores[VALUE_DAMPENER_PILLAR][code], 2)
                                  if (VALUE_DAMPENER_PILLAR in pillar_scores and
                                      pillar_scores[VALUE_DAMPENER_PILLAR].get(code) is not None)
                                  else None,
            "tier": tier_for(composite),
        }
    return results


def export_scores_csv(xwalk, results, path):
    import csv
    all_pillars = sorted(AHP_PILLAR_WEIGHTS.keys())
    fieldnames = ["lgd_code", "district_name", "state_name", "composite_score",
                  "dampener_applied", "pillar_coverage_pct", "global_pillar_coverage_pct", "tier"] + \
                 [f"{p}_score" for p in all_pillars]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for d in xwalk.districts:
            r = results[d.lgd_code]
            row = {
                "lgd_code": d.lgd_code, "district_name": d.current_name, "state_name": d.state_name,
                "composite_score": r["composite_score"],
                "dampener_applied": r.get("dampener_applied"),
                "pillar_coverage_pct": r["pillar_coverage_pct"],
                "global_pillar_coverage_pct": r["global_pillar_coverage_pct"],
                "tier": r["tier"],
            }
            for p in all_pillars:
                row[f"{p}_score"] = r["pillar_scores"].get(p, "")  # blank for not-yet-built pillars
            writer.writerow(row)

