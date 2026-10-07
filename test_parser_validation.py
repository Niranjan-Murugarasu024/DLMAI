"""
Validates nfhs_factsheet_parser.py against the mock factsheets, checking
not just that it runs, but that every extracted value matches what was
actually written into the mock PDF -- including the tricky cases:
noise lines that share keywords with real patterns (severely wasted vs
wasted, blood-sugar component lines vs the combined measure), and the
Women/Men dual-occurrence ordering for hypertension and diabetes.
"""

from nfhs_factsheet_parser import parse_factsheet_pdf, parse_factsheet_batch

# Re-declare expected values inline (mirrors generate_mock_factsheet.py) so
# this test doesn't silently pass if someone edits one file and not the other.
EXPECTED = {
    "mock_Coimbatore_factsheet.pdf": {
        "electricity_pct": 99.4, "drinking_water_pct": 97.8, "sanitation_pct": 88.3,
        "clean_fuel_pct": 78.1, "insurance_pct": 52.6, "oope_delivery_rs": 2840.0,
        "stunting_pct": 18.7, "wasting_pct": 11.2, "underweight_pct": 17.9,
        "diabetes_combined_pct_women": 13.8, "diabetes_combined_pct_men": 16.2,
        "hypertension_combined_pct_women": 19.4, "hypertension_combined_pct_men": 24.7,
    },
    "mock_Kurnool_factsheet.pdf": {
        "electricity_pct": 98.2, "drinking_water_pct": 92.4, "sanitation_pct": 71.6,
        "clean_fuel_pct": 61.0, "insurance_pct": 64.3, "oope_delivery_rs": 3510.0,
        "stunting_pct": 29.4, "wasting_pct": 17.8, "underweight_pct": 31.2,
        "diabetes_combined_pct_women": 10.5, "diabetes_combined_pct_men": 13.9,
        "hypertension_combined_pct_women": 16.1, "hypertension_combined_pct_men": 21.3,
    },
}

print("=" * 78)
print("Parsing both mock factsheets")
print("=" * 78)
results = parse_factsheet_batch(list(EXPECTED.keys()))

print()
print("=" * 78)
print("Checking every extracted value against what was actually written into the PDF")
print("=" * 78)
all_pass = True
for result, (pdf_path, expected) in zip(results, EXPECTED.items()):
    print(f"\n{pdf_path}  (district name read off the PDF header: {result.district_raw_name!r})")
    for key, expected_value in expected.items():
        got = result.values.get(key)
        ok = (got == expected_value)
        all_pass &= ok
        flag = "OK" if ok else "MISMATCH"
        print(f"  {key:32s} expected={expected_value:<8} got={got!s:<8} [{flag}]")

    # explicitly confirm the noise lines did NOT leak into our real keys
    noise_keys_present = [k for k in result.values if k.startswith("noise_")]
    print(f"  noise indicators captured (should be empty -- they're not in our pattern list): {noise_keys_present}")

print()
print("=" * 78)
print("ALL VALUES MATCHED EXPECTED" if all_pass else "SOME VALUES DID NOT MATCH -- inspect above")
print("=" * 78)
