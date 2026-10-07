"""
Regression tests for two bugs caught in a second round of external review:

BUG-001: entropy_weights() computed its normalizing constant k=1/ln(n)
from the FIRST indicator's non-None count and reused it for every other
indicator, even when those indicators had a different number of missing
districts. Confirmed empirically: two EQUALLY uninformative (perfectly
constant) indicators with different non-None counts landed at weights
0.0 and 1.0 instead of both correctly getting 0 -- a real, silent
mis-weighting, not just a theoretical concern. The fix also needed a
numerical-tolerance check (not exact-zero equality) on the final
normalization step, since floating-point rounding rarely lands two
independently-computed near-zero diversification values on exactly the
same sign.

BUG-013: sensitivity_analysis.py's composite_from_weights() assumed every
district had every pillar key present -- but scoring_engine.py's
score_districts() (fixed in the previous round) omits a pillar's key
entirely for a district with a total data desert in that one pillar.
This would have crashed an entire multi-thousand-iteration Monte Carlo
run over a single district's single missing pillar.
"""

from scoring_engine import entropy_weights
from sensitivity_analysis import composite_from_weights, run_monte_carlo
from scoring_engine import AHP_PILLAR_WEIGHTS

print("=" * 78)
print("TEST 1 -- BUG-001: two equally-uninformative indicators get equal weight")
print("=" * 78)
ind_a = {f"d{i}": 50.0 for i in range(20)}      # constant, 20 non-None values
ind_b = {f"d{i}": 50.0 for i in range(18)}      # constant, only 18 non-None values
ind_b["d18"], ind_b["d19"] = None, None
weights = entropy_weights({"A": ind_a, "B": ind_b})
print(f"  weights = {weights}")
assert abs(weights["A"] - 0.5) < 1e-9 and abs(weights["B"] - 0.5) < 1e-9, \
    "two equally-constant indicators with different non-None counts must get equal weight"
print("  PASS -- both correctly treated as equally uninformative")

print()
print("=" * 78)
print("TEST 2 -- BUG-001: a genuinely varying indicator still dominates a constant one")
print("=" * 78)
ind_varying = {f"d{i}": float(i * 10) for i in range(10)}
ind_constant = {f"d{i}": 42.0 for i in range(10)}
w2 = entropy_weights({"constant_ind": ind_constant, "varying_ind": ind_varying})
print(f"  weights = {w2}")
assert w2["varying_ind"] > 0.99, "the fix must not have broken the original, correct behavior"
print("  PASS -- fix didn't disturb the legitimate case from the previous round")

print()
print("=" * 78)
print("TEST 3 -- BUG-013: composite_from_weights no longer crashes on a per-district missing pillar")
print("=" * 78)
pillar_scores = {
    "d0": {"P1": 50, "P2": 50, "P3": 50, "P4": 50, "P5": 50, "P6": 50, "P7": 50},
    "d1": {"P1": 50, "P2": 50, "P3": 50, "P4": 50, "P5": 50, "P6": 50},   # P7 missing
}
result = composite_from_weights(pillar_scores, AHP_PILLAR_WEIGHTS, ["d0", "d1"])
print(f"  d0={result['d0']:.2f}  d1={result['d1']:.2f}  (no crash)")
assert result["d0"] is not None and result["d1"] is not None

print()
print("=" * 78)
print("TEST 4 -- BUG-013: a TOTAL data desert district is excluded, not crashing the whole run")
print("=" * 78)
pillar_scores["d2"] = {}   # zero usable pillars at all
mc = run_monte_carlo(pillar_scores, AHP_PILLAR_WEIGHTS, ["d0", "d1", "d2"], n_iterations=200)
print(f"  excluded_no_data = {mc['excluded_no_data']}")
assert mc["excluded_no_data"] == ["d2"]
assert "d2" not in mc["rank_stats"]
print("  PASS -- d2 explicitly excluded and reported, d0/d1 analyzed normally, no crash")

print()
print("ALL CHECKS PASSED")
