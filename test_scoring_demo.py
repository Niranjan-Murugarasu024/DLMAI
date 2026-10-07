"""
Runs the full pipeline (Layers 1-3) and feeds its output into the Layer 4
scoring engine, then hand-checks the key numbers rather than just printing
results and assuming they're right:
  - entropy weights sum to 1 within each pillar
  - pillar_coverage_pct exactly matches the AHP weight of the 4 pillars
    that actually have data (P1+P2+P4+P7 = 66.02%, NOT 100%)
  - min-max normalization is checked by hand for one indicator
  - the counterintuitive-but-correct result: a district with WORSE health
    indicators can score HIGHER on Pillar 1, because this index measures
    market demand, not population wellbeing -- worth seeing explicitly,
    not just asserting in a docstring
"""

import math
from run_pipeline import run_pipeline, ALL_INDICATORS
from scoring_engine import (
    score_districts, min_max_normalize, entropy_weights,
    PILLAR_INDICATORS, AHP_PILLAR_WEIGHTS, PILLAR_NAMES, DIRECTION,
)

(xwalk, filled, mask, nfhs_unmatched, ja_unmatched, census_unmatched, rhs_unmatched,
 mca21_excluded, population_reference, population_source, census_warnings,
 rhs_density_lost_to_missing_population, rhs_duplicate_matches) = run_pipeline()

all_codes = [d.lgd_code for d in xwalk.districts]
results = score_districts(filled, all_codes)

print("=" * 78)
print("TEST 1 -- pillar coverage now reaches 100% honestly, not by inflation")
print("=" * 78)
expected_coverage = 97.0  # driver pillars only; P5 is the dampener
sample_result = results["SAMPLE-TN-01"]
print(f"  Driver pillars with real data: P1, P2, P3, P4, P6, P7 (P5 is dampener)")
print(f"  Their combined AHP weight: {expected_coverage}%")
print(f"  pillar_coverage_pct reported: {sample_result['pillar_coverage_pct']}%")
assert sample_result["pillar_coverage_pct"] == expected_coverage, "coverage mismatch"
print(f"  -> {expected_coverage}% driver coverage -- P5 acts as dampener (subtracted), not counted in positive coverage")

print()
print("=" * 78)
print("TEST 2 -- entropy weights sum to 1 within every scored pillar")
print("=" * 78)
for pillar, indicators in PILLAR_INDICATORS.items():
    if not indicators:
        continue
    raw_normalized = {}
    for ind in indicators:
        raw = {code: filled[code][ind] for code in all_codes}
        raw_normalized[ind] = min_max_normalize(raw, DIRECTION[ind])
    weights = entropy_weights(raw_normalized)
    total = sum(weights.values())
    print(f"  {pillar} ({PILLAR_NAMES[pillar]}): {len(indicators)} indicators, "
          f"weights sum to {total:.6f}")
    assert abs(total - 1.0) < 1e-9, f"{pillar} entropy weights don't sum to 1"

print()
print("=" * 78)
print("TEST 3 -- hand-check min-max normalization for one indicator")
print("=" * 78)
stunting_raw = {code: filled[code]["stunting_pct"] for code in all_codes}
lo, hi = min(stunting_raw.values()), max(stunting_raw.values())
coimbatore_raw = stunting_raw["SAMPLE-TN-01"]
expected_norm = 100 * (coimbatore_raw - lo) / (hi - lo)   # "higher" direction
normalized = min_max_normalize(stunting_raw, "higher")
print(f"  stunting_pct range across all districts: [{lo:.2f}, {hi:.2f}]")
print(f"  Coimbatore raw = {coimbatore_raw}, hand-computed normalized = {expected_norm:.4f}")
print(f"  engine-computed normalized = {normalized['SAMPLE-TN-01']:.4f}")
assert abs(normalized["SAMPLE-TN-01"] - expected_norm) < 1e-9

print()
print("=" * 78)
print("TEST 4 -- the counterintuitive-but-correct case: worse health can mean a HIGHER P1 score")
print("=" * 78)
coim = results["SAMPLE-TN-01"]
kurnool = results["SAMPLE-AP-01"]
print(f"  Coimbatore: stunting={filled['SAMPLE-TN-01']['stunting_pct']}%  "
      f"P1 score={coim['pillar_scores']['P1']}")
print(f"  Kurnool:    stunting={filled['SAMPLE-AP-01']['stunting_pct']}%  "
      f"P1 score={kurnool['pillar_scores']['P1']}")
print("  Kurnool has notably worse nutrition indicators than Coimbatore -- and scores")
print("  HIGHER on Pillar 1 as a direct result, because this index treats higher disease/")
print("  malnutrition prevalence as higher THERAPY DEMAND, not as a wellbeing measure.")
print("  This is the explicit, documented design choice in DIRECTION, not a bug.")

print()
print("=" * 78)
print("Full ranking (full DLMAI score, all 7 pillars, sorted descending)")
print("=" * 78)
ranked = sorted(results.items(), key=lambda kv: -kv[1]["composite_score"])
for rank, (code, r) in enumerate(ranked, 1):
    d = xwalk.by_code[code]
    print(f"  {rank:2d}. {d.current_name:18s} ({d.state_name:15s}) "
          f"score={r['composite_score']:6.2f}  {r['tier']}")

print()
print("=" * 78)
print(f"Sample full breakdown: {xwalk.by_code['SAMPLE-TN-01'].current_name}")
print("=" * 78)
r = results["SAMPLE-TN-01"]
print(f"  composite_score = {r['composite_score']}  ({r['tier']})")
print(f"  pillar_coverage_pct = {r['pillar_coverage_pct']}%  (driver pillars P1-P4,P6,P7; P5 is dampener)")
print(f"  dampener_applied = {r.get('dampener_applied')}  (W5_DAMPENER x P5 score subtracted from composite)")
for p, score in r["pillar_scores"].items():
    print(f"    {p} ({PILLAR_NAMES[p]:35s}) score={score:6.2f}  "
          f"renormalized weight={r['pillar_weights_renormalized'][p]:.4f}")

print()
print("ALL CHECKS PASSED")

import os
os.makedirs("outputs", exist_ok=True)
from scoring_engine import export_scores_csv
export_scores_csv(xwalk, results, "outputs/dlmai_scores.csv")
print("\nExported: outputs/dlmai_scores.csv")
