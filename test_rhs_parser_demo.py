"""
Validates rhs_parser.py: checks that real district rows extract exactly
right, that blank-district-name state-total rows are correctly skipped
(not counted as phantom districts), and that Mumbai's real absence
doesn't produce any spurious entry.
"""

from district_crosswalk import DistrictCrosswalk
from rhs_parser import extract_rhs_rows, aggregate_to_combined

xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")

rows = extract_rhs_rows("mock_rhs_district_table.pdf")
print("=" * 78)
print(f"TEST 1 -- raw extraction (expect exactly 6 real district rows, 0 total rows)")
print("=" * 78)
for r in rows:
    print(f"  {r}")
assert len(rows) == 6, f"expected 6 district rows (state-total rows must be skipped), got {len(rows)}"
print("  -> all 3 state-total rows (blank district name) correctly excluded")

combined = {d.lgd_code: {} for d in xwalk.districts}
unmatched = []
aggregate_to_combined(rows, xwalk, combined, unmatched)

print()
print("=" * 78)
print("TEST 2 -- values match the real source exactly")
print("=" * 78)
expected = {
    "SAMPLE-AP-03": {"rhs_sub_centres": 689.0, "rhs_phcs": 74.0, "rhs_chcs": 16.0,
                      "rhs_sub_divisional_hospital": 2.0, "rhs_district_hospital": 1.0},   # Guntur
    "SAMPLE-TS-01": {"rhs_sub_centres": 53.0, "rhs_phcs": 10.0, "rhs_chcs": 0.0,
                      "rhs_sub_divisional_hospital": 4.0, "rhs_district_hospital": 1.0},   # Hyderabad
    "SAMPLE-AP-01": {"rhs_sub_centres": 576.0, "rhs_phcs": 88.0, "rhs_chcs": 18.0,
                      "rhs_sub_divisional_hospital": 1.0, "rhs_district_hospital": 1.0},   # Kurnool
    "SAMPLE-KA-01": {"rhs_sub_centres": 195.0, "rhs_phcs": 75.0, "rhs_chcs": 3.0,
                      "rhs_sub_divisional_hospital": 3.0, "rhs_district_hospital": 3.0},   # Bangalore Urban
    "SAMPLE-KA-02": {"rhs_sub_centres": 167.0, "rhs_phcs": 47.0, "rhs_chcs": 1.0,
                      "rhs_sub_divisional_hospital": 4.0, "rhs_district_hospital": 0.0},   # Bangalore Rural
    "SAMPLE-MH-03": {"rhs_sub_centres": 539.0, "rhs_phcs": 96.0, "rhs_chcs": 21.0,
                      "rhs_sub_divisional_hospital": 3.0, "rhs_district_hospital": 1.0},   # Pune
}
all_ok = True
for code, exp_fields in expected.items():
    d = xwalk.by_code[code]
    for field, exp_val in exp_fields.items():
        got = combined[code].get(field)
        ok = (got == exp_val)
        all_ok &= ok
        if not ok:
            print(f"  MISMATCH: {d.current_name} {field} expected={exp_val} got={got}")
    print(f"  {d.current_name:18s} {combined[code]}")
assert all_ok, "value mismatch detected"

print()
print("=" * 78)
print("TEST 3 -- Mumbai's real absence: no entry at all, not a zero, not an error")
print("=" * 78)
for code in ["SAMPLE-MH-01", "SAMPLE-MH-02"]:
    d = xwalk.by_code[code]
    print(f"  {d.current_name:18s} combined dict = {combined[code]}  (expect empty -- {{}})")
    assert combined[code] == {}, "Mumbai should have NO rhs_ fields at all, not zeros"
print("  -> correctly empty, matching the real document's actual gap, not silently zero-filled")

print()
print("ALL CHECKS PASSED")
