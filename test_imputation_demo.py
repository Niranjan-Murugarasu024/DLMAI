"""
Demonstration / smoke test for imputation_engine.py.

Deliberately exercises every branch of the imputation hierarchy on the
same 21-district sample used in the crosswalk demo (district_state_map is
built directly from DistrictCrosswalk, not hand-rolled separately -- this
is the intended Layer 2 -> Layer 3 composition described in both modules'
docstrings):

  - native values left untouched
  - state-mean fill from a single same-state neighbor (Karnataka)
  - state-mean fill averaged across two same-state neighbors (Maharashtra)
  - nearest-neighbor fallback when an ENTIRE state has no data at all
    for an indicator (all 7 Andhra Pradesh sample districts)
  - the final still-missing fallback, when even the similarity covariate
    (population) is unavailable (Telangana's only sample district)
  - trend interpolation and extrapolation from two known time points
"""

from district_crosswalk import DistrictCrosswalk
from imputation_engine import (
    ImputationEngine, completeness_report, print_completeness_report,
    STATUS_NATIVE, STATUS_STATE_MEAN, STATUS_NEAREST_NEIGHBOR, STATUS_STILL_MISSING,
)

xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")

# Layer 2 -> Layer 3 composition: build the state map straight off the
# crosswalk's master table, never a second hand-maintained copy.
district_state_map = {d.lgd_code: d.state_name for d in xwalk.districts}

# Population reference (millions, illustrative) -- this is the similarity
# covariate for nearest-neighbor matching. Hyderabad's entry is left out on
# purpose, to force the still-missing fallback later in this test.
district_population = {
    "SAMPLE-KA-01": 9.6, "SAMPLE-KA-02": 0.99,
    "SAMPLE-UP-01": 5.95, "SAMPLE-UP-02": 2.47,
    "SAMPLE-MH-01": 3.08, "SAMPLE-MH-02": 9.36, "SAMPLE-MH-03": 9.43,
    "SAMPLE-AP-01": 1.18, "SAMPLE-AP-02": 1.05, "SAMPLE-AP-03": 1.74,
    "SAMPLE-AP-04": 1.55, "SAMPLE-AP-05": 1.34, "SAMPLE-AP-06": 1.42, "SAMPLE-AP-07": 1.52,
    "SAMPLE-TN-01": 3.46, "SAMPLE-TN-02": 4.65,
    # SAMPLE-TS-01 (Hyderabad) deliberately omitted
    "SAMPLE-GJ-01": 7.21, "SAMPLE-WB-01": 4.50, "SAMPLE-RJ-01": 6.63,
    "SAMPLE-BR-01": 5.84, "SAMPLE-MP-01": 2.37,
}

# Test indicator: "doctor_density_per_10k" -- native for most districts,
# missing for exactly the cases designed to exercise each fallback branch.
doctor_density = {
    "SAMPLE-KA-01": {"doctor_density_per_10k": 18.4},   # native
    "SAMPLE-KA-02": {"doctor_density_per_10k": None},   # -> state-mean from Bengaluru Urban alone
    "SAMPLE-MH-01": {"doctor_density_per_10k": None},   # -> state-mean averaged from Pune + Mumbai Suburban
    "SAMPLE-MH-02": {"doctor_density_per_10k": 14.7},   # native
    "SAMPLE-MH-03": {"doctor_density_per_10k": 16.9},   # native
    "SAMPLE-AP-01": {"doctor_density_per_10k": None},   # entire AP state missing -> nearest-neighbor by population
    "SAMPLE-AP-02": {"doctor_density_per_10k": None},
    "SAMPLE-AP-03": {"doctor_density_per_10k": None},
    "SAMPLE-AP-04": {"doctor_density_per_10k": None},
    "SAMPLE-AP-05": {"doctor_density_per_10k": None},
    "SAMPLE-AP-06": {"doctor_density_per_10k": None},
    "SAMPLE-AP-07": {"doctor_density_per_10k": None},
    "SAMPLE-TS-01": {"doctor_density_per_10k": None},   # Telangana's only sample district, no population either -> still missing
    "SAMPLE-TN-01": {"doctor_density_per_10k": 11.2},
    "SAMPLE-TN-02": {"doctor_density_per_10k": 22.8},
    "SAMPLE-GJ-01": {"doctor_density_per_10k": 13.5},
    "SAMPLE-WB-01": {"doctor_density_per_10k": 19.9},
    "SAMPLE-RJ-01": {"doctor_density_per_10k": 9.8},
    "SAMPLE-BR-01": {"doctor_density_per_10k": 6.4},
    "SAMPLE-MP-01": {"doctor_density_per_10k": 10.1},
    "SAMPLE-UP-01": {"doctor_density_per_10k": 8.7},
    "SAMPLE-UP-02": {"doctor_density_per_10k": 7.9},
}

engine = ImputationEngine(district_state_map, district_population, nearest_neighbor_k=3)
result = engine.impute(doctor_density, indicator_ids=["doctor_density_per_10k"])

print("=" * 78)
print("TEST 1 & 2 -- state-mean fill (single neighbor, then averaged across two)")
print("=" * 78)
for code, label in [("SAMPLE-KA-02", "Bengaluru Rural (KA, 1 in-state neighbor)"),
                     ("SAMPLE-MH-01", "Mumbai City (MH, 2 in-state neighbors)")]:
    v = result.filled[code]["doctor_density_per_10k"]
    status = result.mask[code]["doctor_density_per_10k"]
    print(f"  {label:48s} filled={v:.2f}  status={status}")
print(f"  (check: Bengaluru Urban alone = 18.40 -> Rural should match exactly)")
print(f"  (check: mean(Pune=16.90, Mumbai Suburban=14.70) = {(16.9+14.7)/2:.2f} -> Mumbai City should match)")

print()
print("=" * 78)
print("TEST 3 -- entire state missing the indicator -> nearest-neighbor by population")
print("=" * 78)
for code in ["SAMPLE-AP-01", "SAMPLE-AP-03", "SAMPLE-AP-06"]:
    d = xwalk.by_code[code]
    v = result.filled[code]["doctor_density_per_10k"]
    status = result.mask[code]["doctor_density_per_10k"]
    print(f"  {d.current_name:15s} (pop={district_population[code]}M) filled={v:.2f}  status={status}")
print("  (no Andhra Pradesh district had a native value, so state-mean had nothing to")
print("   work with for any of them -- this is exactly the case nearest-neighbor exists for)")

print()
print("=" * 78)
print("TEST 4 -- final fallback: indicator AND similarity covariate both missing")
print("=" * 78)
v = result.filled["SAMPLE-TS-01"]["doctor_density_per_10k"]
status = result.mask["SAMPLE-TS-01"]["doctor_density_per_10k"]
print(f"  Hyderabad -> filled={v}  status={status}")
print("  (Telangana has no other sample district for a state-mean, and population")
print("   wasn't provided either -- correctly left missing rather than guessed)")

print()
print("=" * 78)
print("TEST 5 -- trend interpolation / extrapolation")
print("=" * 78)
from imputation_engine import trend_interpolate
ts = {2011: 8.2, 2021: 9.6}   # e.g. a population-in-millions style time series
print(f"  known points: {ts}")
print(f"  interpolated 2016 (midpoint) = {trend_interpolate(ts, 2016):.3f}  (expect ~8.90)")
print(f"  extrapolated 2024 (forward)  = {trend_interpolate(ts, 2024):.3f}  (expect ~9.99)")
print(f"  single known point only -> {trend_interpolate({2011: 8.2}, 2016)}  (expect None -- can't interpolate from one point)")

print()
print("=" * 78)
print("Completeness report")
print("=" * 78)
report = completeness_report(result.mask, ["doctor_density_per_10k"])
print_completeness_report(report, total_districts=len(doctor_density))
