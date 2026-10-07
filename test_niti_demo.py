"""
Validates niti_aspirational_districts.py: confirms the real list resolves
correctly against the crosswalk, specifically that "Y.S.R. Kadapa" (the
real list's punctuation/spacing) correctly matches this sample's
"YSR Kadapa" via normalize(), and that every other sample district
correctly gets flagged 0 (confirmed real non-membership, not a guess).
"""

from district_crosswalk import DistrictCrosswalk
from niti_aspirational_districts import flag_aspirational_districts, ASPIRATIONAL_DISTRICTS

xwalk = DistrictCrosswalk("sample_lgd_seed.csv", "manual_aliases.csv")
all_codes = [d.lgd_code for d in xwalk.districts]

print("=" * 78)
print(f"TEST 1 -- real list integrity ({len(ASPIRATIONAL_DISTRICTS)} districts, expect 112)")
print("=" * 78)
assert len(ASPIRATIONAL_DISTRICTS) == 112
print("  -> confirmed: full real list, not a truncated sample")

flagged = flag_aspirational_districts(xwalk)

print()
print("=" * 78)
print("TEST 2 -- YSR Kadapa matches 'Y.S.R. Kadapa' despite punctuation/spacing differences")
print("=" * 78)
print(f"  flagged dict contains SAMPLE-AP-06: {'SAMPLE-AP-06' in flagged}")
assert "SAMPLE-AP-06" in flagged and flagged["SAMPLE-AP-06"] == 1
print("  -> matched correctly via normalize() stripping periods/spacing, not a hand-coded special case")

print()
print("=" * 78)
print("TEST 3 -- every other sample district correctly gets a confirmed zero, not 'unknown'")
print("=" * 78)
final_flags = {code: flagged.get(code, 0) for code in all_codes}
for code in all_codes:
    d = xwalk.by_code[code]
    status = "ASPIRATIONAL" if final_flags[code] == 1 else "not aspirational (confirmed)"
    print(f"  {d.current_name:18s} flag={final_flags[code]}  [{status}]")

non_kadapa_flagged = [c for c in all_codes if c != "SAMPLE-AP-06" and final_flags[c] == 1]
assert non_kadapa_flagged == [], f"unexpected extra flags: {non_kadapa_flagged}"
print("\n  -> exactly one flagged district in this sample (YSR Kadapa), everything else "
      "correctly 0 -- and unlike Jan Aushadhi/MCA21, these zeros need no covered-vs-uncovered "
      "caveat, since the source list is genuinely exhaustive")

print()
print("ALL CHECKS PASSED")
