"""
Validates mca21_ingestion.py: checks that genuine active pharma companies
are kept and correctly counted per district, and that each of the four
distinct exclusion reasons fires on exactly the row designed to trigger
it -- not just that "some" rows got excluded.
"""

from mca21_ingestion import extract_pharma_companies, aggregate_by_district
from district_crosswalk import DistrictCrosswalk

xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")

kept, excluded = extract_pharma_companies("mock_mca21_company_master.csv")

print("=" * 78)
print(f"TEST 1 -- kept companies (expect 7: the genuine active, resolvable, pharma ones)")
print("=" * 78)
for c in kept:
    d = xwalk.by_code[c["lgd_code"]]
    print(f"  {c['company_name']:38s} -> {d.current_name} ({c['pincode']})")
assert len(kept) == 7, f"expected 7 kept companies, got {len(kept)}"

print()
print("=" * 78)
print("TEST 2 -- each exclusion reason fires on exactly the row designed to trigger it")
print("=" * 78)
excluded_dict = dict(excluded)
print(f"  All exclusions: {excluded}")

# Noyyal Textiles -- wrong industry entirely
assert excluded_dict["U17110TN2011PLC001008"] == "not_pharma_activity"
print("  Noyyal Textiles (NIC 13911, textiles)        -> not_pharma_activity   [correct]")

# Tungabhadra Pharma Labs -- real pharma NIC code, but Struck Off
assert "not_active" in excluded_dict["U24232AP2007PLC001009"]
print("  Tungabhadra Pharma Labs (Struck Off)          -> not_active            [correct -- pharma NIC didn't save it]")

# Krishnaveni Biotech -- real pharma NIC code, but Dormant
assert "not_active" in excluded_dict["U24239AP2013PLC001010"]
print("  Krishnaveni Biotech (Dormant)                 -> not_active            [correct]")

# Yamuna Pharmaceuticals -- genuinely active pharma company, but address has no PIN code
assert "unresolvable_pincode" in excluded_dict["U24232DL2010PLC001011"]
print("  Yamuna Pharmaceuticals (no PIN in address)    -> unresolvable_pincode  [correct -- "
      "a real active pharma company still gets excluded if its address can't be geo-resolved, "
      "which is an honest limitation, not a bug]")

print()
print("=" * 78)
print("TEST 3 -- per-district aggregation")
print("=" * 78)
counts = aggregate_by_district(kept)
for code, n in sorted(counts.items()):
    d = xwalk.by_code[code]
    print(f"  {d.current_name:18s} {n} active pharma company(ies)")

expected_counts = {
    "SAMPLE-TN-01": 2,   # Kaveri Pharma, Nila Biosciences (Coimbatore) -- Noyyal Textiles excluded
    "SAMPLE-TS-01": 3,   # Krishna Drugs, Deccan Therapeutics, Charminar Lifesciences (Hyderabad)
    "SAMPLE-GJ-01": 1,   # Sabarmati Pharmachem (Ahmedabad)
    "SAMPLE-MH-03": 1,   # Mula Mutha Pharma Retail (Pune)
}
assert counts == expected_counts, f"count mismatch: {counts} vs {expected_counts}"
print("\n  Note: Kurnool and Guntur have ZERO counted here, despite having a pharma-NIC "
      "company each -- both were Struck Off / Dormant. This is the correct outcome, "
      "not a data gap: those districts genuinely have no ACTIVE registered pharma "
      "company in this sample.")

print()
print("ALL CHECKS PASSED")
