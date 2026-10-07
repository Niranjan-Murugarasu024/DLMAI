"""
Regression test for a real bug caught in external code review: a district
reaching scoring with a genuine STATUS_STILL_MISSING (None) value used to
crash min_max_normalize() with a TypeError -- and because normalization
runs once across ALL districts per indicator, one district's missing
cell took down the entire scoring run, not just that district's score.

This is now fixed by having every layer (min_max_normalize,
entropy_weights, score_districts) explicitly handle None: excluded from
range/discrimination calculations, and renormalizing pillar/composite
weights for just the affected district among whatever it DOES have --
the same coverage-aware principle already used when an entire pillar is
missing, now applied per-district per-indicator too.

This test constructs the exact failure scenario directly (not relying on
the imputation engine to produce it organically, since the 22-district
sample never naturally hits this path) and checks both that nothing
crashes AND that the unaffected districts are completely unchanged by
one other district's missing value.
"""

from scoring_engine import score_districts


def _make_complete_district(seed: float) -> dict:
    return {
        "stunting_pct": 20.0 + seed, "wasting_pct": 10.0 + seed, "underweight_pct": 15.0 + seed,
        "hypertension_combined_pct_women": 18.0 + seed, "hypertension_combined_pct_men": 22.0 + seed,
        "diabetes_combined_pct_women": 12.0 + seed, "diabetes_combined_pct_men": 14.0 + seed,
        "population_age_0_6_pct": 12.0 + seed, "urban_population_pct": 50.0 + seed,
        "electricity_pct": 95.0, "clean_fuel_pct": 70.0 + seed, "drinking_water_pct": 90.0,
        "sanitation_pct": 80.0 + seed, "insurance_pct": 50.0 + seed, "oope_delivery_rs": 2000.0 + seed * 10,
        "jan_aushadhi_kendra_count": 2 + int(seed) % 5,
        "decadal_growth_rate_pct": 10.0 + seed, "literacy_rate_pct": 70.0 + seed,
        "sub_centres_per_lakh_pop": 5.0 + seed, "phcs_per_lakh_pop": 1.0 + seed * 0.1,
        "chcs_per_lakh_pop": 0.2 + seed * 0.02,
        "rhs_sub_divisional_hospital": 1, "rhs_district_hospital": 1,
        "mca21_active_pharma_company_count": 1 + int(seed) % 3,
        "niti_aspirational_district_flag": 1 if seed == 3 else 0,
    }


print("=" * 78)
print("TEST 1 -- a None value (STATUS_STILL_MISSING) no longer crashes scoring")
print("=" * 78)
filled_baseline = {f"d{i}": _make_complete_district(float(i)) for i in range(10)}
filled_with_gap = {k: dict(v) for k, v in filled_baseline.items()}
filled_with_gap["d5"]["jan_aushadhi_kendra_count"] = None   # the exact real failure case

all_codes = list(filled_with_gap.keys())
try:
    results_baseline = score_districts(filled_baseline, all_codes)
    results_with_gap = score_districts(filled_with_gap, all_codes)
    print("  No crash on either run -- OK")
except Exception as e:
    raise AssertionError(f"score_districts crashed: {type(e).__name__}: {e}")

print()
print("=" * 78)
print("TEST 2 -- the affected district's P4 score is None, not a fabricated number")
print("=" * 78)
assert results_with_gap["d5"]["pillar_scores"].get("P4") is None
print("  d5 P4 score:", results_with_gap["d5"]["pillar_scores"].get("P4"), "-- correctly absent")

print()
print("=" * 78)
print("TEST 3 -- d5's driver weights renormalize to exclude P4, dampener stored negative")
print("=" * 78)
from scoring_engine import VALUE_DAMPENER_PILLAR, W5_DAMPENER
d5_weights = results_with_gap["d5"]["pillar_weights_renormalized"]
print(f"  d5 weights: {d5_weights}")
# P4 excluded (missing data) -- correct
assert "P4" not in d5_weights, "P4 should be absent (missing data)"
# P5 present with its dampener coefficient stored NEGATIVE to signal penalty role
assert d5_weights.get(VALUE_DAMPENER_PILLAR) == -W5_DAMPENER,     f"P5 should be stored as -{W5_DAMPENER} (negative = dampener)"
# Driver weights (all positive entries) sum to 1
driver_weights = {p: w for p, w in d5_weights.items() if w >= 0}
driver_sum = sum(driver_weights.values())
print(f"  driver weights sum = {driver_sum:.10f}  (expect 1.0)")
print(f"  dampener weight = {d5_weights.get(VALUE_DAMPENER_PILLAR)}  (negative = subtracted)")
assert abs(driver_sum - 1.0) < 1e-9, f"Driver weights should sum to 1, got {driver_sum}"
print(f"  OK -- driver weights sum to 1; P5 stored as -W5_DAMPENER to signal subtraction")

print()
print("=" * 78)
print("TEST 4 -- every OTHER district is completely unaffected by d5's gap")
print("=" * 78)
all_unaffected = True
for code in all_codes:
    if code == "d5":
        continue
    same = results_baseline[code]["composite_score"] == results_with_gap[code]["composite_score"]
    all_unaffected &= same
    if not same:
        print(f"  MISMATCH on {code}: {results_baseline[code]['composite_score']} vs "
              f"{results_with_gap[code]['composite_score']}")
assert all_unaffected
print("  Confirmed: one district's missing cell does not change anyone else's score "
      "-- this is the actual bug from the original report; it used to crash the whole run.")

print()
print("=" * 78)
print("TEST 5 -- a PARTIAL gap in a multi-indicator pillar still produces a real pillar score")
print("=" * 78)
# The tests above only cover a single-indicator pillar (P4) going
# entirely missing. This explicitly covers the other case: P2 has SIX
# indicators -- knock out just ONE of them for one district and confirm
# the pillar score is still computed from the remaining five (correctly
# renormalized), not wrongly excluded as if the whole pillar were gone.
filled_partial_gap = {k: dict(v) for k, v in filled_baseline.items()}
filled_partial_gap["d3"]["insurance_pct"] = None   # one of P2's six indicators
results_partial = score_districts(filled_partial_gap, all_codes)

p2_score = results_partial["d3"]["pillar_scores"].get("P2")
print(f"  d3 P2 score with one of six indicators missing: {p2_score}")
assert p2_score is not None, "P2 should still produce a real score from the remaining 5 indicators"
assert "P2" in results_partial["d3"]["pillar_weights_renormalized"], "P2 must still count toward d3's composite"
print("  PASS -- pillar score computed from the remaining indicators, not wrongly treated as fully missing")

print()
print("ALL CHECKS PASSED")
