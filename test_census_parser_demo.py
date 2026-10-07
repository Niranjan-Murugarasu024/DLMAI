"""
Validates census_handbook_parser.py against the mock handbooks: checks the
Important Statistics extraction, the PCA table extraction (a genuine ruled
table this time, not narrative lines), and the derived percentages
(urban %, age-0-6 %, literacy cross-check) against hand-computed expected
values.
"""

from census_handbook_parser import parse_census_handbook
from generate_mock_census_handbook import DISTRICTS

for district_name, data in DISTRICTS.items():
    print("=" * 78)
    print(f"{district_name}")
    print("=" * 78)
    result = parse_census_handbook(f"mock_{district_name}_census_handbook.pdf")

    print(f"  district_raw_name = {result.district_raw_name!r}")

    print("\n  Important Statistics extracted:")
    for k, v in result.important_stats.items():
        expected = data["important_stats"][k]
        flag = "OK" if v == expected else "MISMATCH"
        print(f"    {k:28s} expected={expected:<12} got={v!s:<12} [{flag}]")

    print("\n  PCA table extracted:")
    for residence in ["Total", "Rural", "Urban"]:
        got = result.pca_table.get(residence, {})
        expected = data["pca"][residence]
        print(f"    {residence:8s} expected={expected}")
        print(f"    {'':8s} got     ={got}")
        assert got == expected, f"PCA mismatch for {district_name} / {residence}"

    print("\n  Derived indicators:")
    total = data["pca"]["Total"]
    urban = data["pca"]["Urban"]
    expected_urban_pct = round(100 * urban["population"] / total["population"], 2)
    expected_0_6_pct = round(100 * total["population_0_6"] / total["population"], 2)
    expected_lit_pct = round(100 * total["literates"] / total["population"], 2)

    checks = {
        "urban_population_pct": expected_urban_pct,
        "population_age_0_6_pct": expected_0_6_pct,
        "literacy_rate_pct_from_pca": expected_lit_pct,
    }
    for k, expected_v in checks.items():
        got_v = result.derived.get(k)
        flag = "OK" if got_v == expected_v else "MISMATCH"
        print(f"    {k:28s} expected={expected_v:<8} got={got_v!s:<8} [{flag}]")
        assert got_v == expected_v, f"derived mismatch: {k}"

    print(f"\n  Cross-check warnings (expect none, since mock data is internally consistent): {result.warnings}")
    assert not result.warnings, "unexpected warning -- mock data should be fully consistent"
    print()

print("=" * 78)
print("Deliberately breaking consistency to confirm the cross-check warning actually fires")
print("=" * 78)
import census_handbook_parser as parser
real_total = DISTRICTS["Coimbatore"]["important_stats"]["total_population"]
DISTRICTS["Coimbatore"]["important_stats"]["total_population"] = real_total + 50000  # introduce a mismatch
from generate_mock_census_handbook import build_mock_handbook
build_mock_handbook("mock_Coimbatore_broken.pdf", "Coimbatore", DISTRICTS["Coimbatore"])
broken_result = parser.parse_census_handbook("mock_Coimbatore_broken.pdf")
print(f"  warnings: {broken_result.warnings}")
assert broken_result.warnings, "expected the mismatch to be caught"
print("  -> mismatch correctly caught, not silently ignored")

print()
print("ALL CHECKS PASSED")
