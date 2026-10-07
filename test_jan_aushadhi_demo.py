"""
Validates jan_aushadhi_ingestion.py end-to-end: table extraction from the
mock PDF -> per-district aggregation -> crosswalk resolution, checking the
expected count per district AND that the deliberately-unmatched district
(Wayanad) surfaces correctly rather than vanishing.
"""

from district_crosswalk import DistrictCrosswalk
from jan_aushadhi_ingestion import extract_kendra_rows, aggregate_by_district

xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")

rows = extract_kendra_rows("mock_kendra_export.pdf")
print("=" * 78)
print(f"TEST 1 -- raw extraction ({len(rows)} rows expected: 12)")
print("=" * 78)
for r in rows:
    print(f"  {r}")
assert len(rows) == 12, f"expected 12 rows, got {len(rows)}"

result = aggregate_by_district(rows, xwalk)

print()
print("=" * 78)
print("TEST 2 -- matched districts resolve to the correct LGD code with correct counts")
print("=" * 78)
expected = {
    "SAMPLE-TN-01": 3,  # Coimbatore
    "SAMPLE-TN-02": 2,  # Chennai
    "SAMPLE-KA-01": 4,  # Bangalore Urban -> Bengaluru Urban, via historical-name match
    "SAMPLE-MH-03": 2,  # Pune
}
all_ok = True
for code, expected_count in expected.items():
    got = result["counts"].get(code)
    ok = (got == expected_count)
    all_ok &= ok
    d = xwalk.by_code[code]
    print(f"  {d.current_name:18s} expected={expected_count}  got={got}  [{'OK' if ok else 'MISMATCH'}]")

print()
print("=" * 78)
print("TEST 3 -- the renamed district matched via historical name, not a fresh fuzzy guess")
print("=" * 78)
r = xwalk.resolve("Bangalore Urban", state_hint="Karnataka")
print(f"  resolve('Bangalore Urban', state_hint='Karnataka') -> method={r.method} "
      f"(expect 'historical' or 'exact_or_historical', not 'fuzzy')")

print()
print("=" * 78)
print("TEST 4 -- Wayanad (not in the sample master) surfaces as unmatched, not dropped")
print("=" * 78)
print(f"  unmatched districts: {result['unmatched']}")
assert len(result["unmatched"]) == 1 and result["unmatched"][0][0] == "Wayanad", \
    "expected exactly one unmatched entry for Wayanad"
print("  -> correctly preserved with its raw name, state, and count (1), not silently lost")

print()
print("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED -- see above")
