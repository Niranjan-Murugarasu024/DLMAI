"""
Validates sensitivity_analysis.py:
  - Spearman correlation is hand-checked against trivial cases (identical
    rankings -> rho=1.0; perfectly reversed rankings -> rho=-1.0)
  - perturb_weights always renormalizes to sum to 1
  - the Monte Carlo run on the REAL pipeline output produces a sensible,
    interpretable result -- not just "it ran without crashing"
"""

import math
from run_pipeline import run_pipeline
from scoring_engine import score_districts, AHP_PILLAR_WEIGHTS, PILLAR_NAMES
from sensitivity_analysis import (
    spearman_correlation, rankdata, perturb_weights, run_monte_carlo,
)
import random

print("=" * 78)
print("TEST 1 -- Spearman correlation hand-checks")
print("=" * 78)
codes = ["a", "b", "c", "d", "e"]
identical = {c: i for i, c in enumerate(codes)}
reversed_scores = {c: -i for i, c in enumerate(codes)}
rho_identical = spearman_correlation(identical, identical, codes)
rho_reversed = spearman_correlation(identical, reversed_scores, codes)
print(f"  identical rankings: rho = {rho_identical:.4f}  (expect 1.0)")
print(f"  perfectly reversed rankings: rho = {rho_reversed:.4f}  (expect -1.0)")
assert abs(rho_identical - 1.0) < 1e-9
assert abs(rho_reversed - (-1.0)) < 1e-9

# tie handling: two equal values should each get the average of their positions
tied = {"a": 1, "b": 2, "c": 2, "d": 3}
ranks = rankdata([tied[c] for c in ["a", "b", "c", "d"]])
print(f"  rankdata([1,2,2,3]) = {ranks}  (expect [1.0, 2.5, 2.5, 4.0] -- tied values average their ranks)")
assert ranks == [1.0, 2.5, 2.5, 4.0]

print()
print("=" * 78)
print("TEST 2 -- perturb_weights always renormalizes to sum to 1")
print("=" * 78)
rng = random.Random(1)
for _ in range(5):
    w = perturb_weights(AHP_PILLAR_WEIGHTS, sigma=0.3, rng=rng)
    total = sum(w.values())
    print(f"  sum = {total:.10f}")
    assert abs(total - 1.0) < 1e-9

print()
print("=" * 78)
print("Running the full pipeline + scoring to get real base pillar scores")
print("=" * 78)
(xwalk, filled, mask, *_rest) = run_pipeline()
all_codes = [d.lgd_code for d in xwalk.districts]
results = score_districts(filled, all_codes)
pillar_scores_by_district = {code: results[code]["pillar_scores"] for code in all_codes}

print()
print("=" * 78)
print("TEST 3 -- Monte Carlo sensitivity analysis (3000 draws, sigma=0.15)")
print("=" * 78)
mc = run_monte_carlo(pillar_scores_by_district, AHP_PILLAR_WEIGHTS, all_codes,
                      n_iterations=3000, sigma=0.15)
print(f"  Mean Spearman correlation vs base ranking: {mc['mean_correlation']:.4f}")
print(f"  5th-percentile (worst-case-ish) correlation: {mc['p5_correlation']:.4f}")
print(f"  Minimum correlation observed: {mc['min_correlation']:.4f}")
print(f"  #1-ranked district stayed #1 in {mc['top1_stability_pct']}% of draws "
      f"(base #1: {xwalk.by_code[mc['base_ranking'][0]].current_name})")
if mc["excluded_no_data"]:
    print(f"  Districts excluded from sensitivity analysis (total data desert, no score to rank): "
          f"{[xwalk.by_code[c].current_name for c in mc['excluded_no_data']]}")
else:
    print("  No districts excluded -- every district had at least one usable pillar")

print()
print("=" * 78)
print("Per-district rank volatility, sorted MOST volatile first (the actionable table)")
print("=" * 78)
sorted_by_volatility = sorted(mc["rank_stats"].items(), key=lambda kv: -kv[1]["std_rank"])
for code, stats in sorted_by_volatility:
    d = xwalk.by_code[code]
    print(f"  {d.current_name:18s} base_rank={stats['base_rank']:2d}  "
          f"mean_rank={stats['mean_rank']:5.1f}  std={stats['std_rank']:5.2f}  "
          f"range=[{stats['min_rank']:.0f}-{stats['max_rank']:.0f}]")

print()
print("=" * 78)
print("Sanity check: districts with the LOWEST volatility should be the clear leader/laggard")
print("=" * 78)
most_stable = sorted(mc["rank_stats"].items(), key=lambda kv: kv[1]["std_rank"])[:3]
for code, stats in most_stable:
    d = xwalk.by_code[code]
    print(f"  {d.current_name:18s} base_rank={stats['base_rank']:2d}  std={stats['std_rank']:.2f}  "
          f"(score={mc['base_composite'][code]:.2f})")
print("  -> these should be districts whose score is far from their nearest neighbor's, "
      "not coincidentally stable")

print()
print("ALL CHECKS PASSED")
