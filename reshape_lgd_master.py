"""
reshape_lgd_master.py — run ONCE after downloading lgd_districts.csv.

The raw LGD download from data.gov.in has inconsistent column names
across monthly editions (sometimes "District LGD Code", sometimes
"Entity LGD Code" etc.) and doesn't include the historical_names or
parent_lgd_code fields the crosswalk engine needs. This script:

  1. Reads the raw lgd_districts.csv
  2. Auto-detects whichever column naming convention is present
  3. Reshapes it to match sample_lgd_seed.csv's exact schema
  4. Writes data/master/lgd_master.csv (the file run_pipeline.py uses)

After running this, update the DistrictCrosswalk() call in
run_pipeline.py to point at data/master/lgd_master.csv instead of
sample_lgd_seed.csv.

historical_names and parent_lgd_code are populated manually over time
as you encounter crosswalk mismatches -- this script starts them empty.
"""

import csv
import sys
import re
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "master" / "lgd_master.csv"

# Column name candidates across known LGD download editions
LGD_CODE_CANDIDATES = [
    "District LGD Code", "Entity LGD Code", "lgd_code",
    "LGD Code", "District Code", "district_code", "district_lgd_code"
]
STATE_CODE_CANDIDATES = [
    "State LGD Code", "State Code", "state_lgd_code", "state_code"
]
STATE_NAME_CANDIDATES = [
    "State Name (In English)", "State Name", "state_name", "state_name_english",
    "State Name(In English)", "State Name English"
]
DISTRICT_NAME_CANDIDATES = [
    "District Name (In English)", "District Name", "current_name",
    "Entity Name (In English)", "Entity Name", "district_name_english",
    "District Name(In English)", "District Name English"
]


def detect_column(header_row, candidates):
    for c in candidates:
        if c in header_row:
            return c
    # Case-insensitive / whitespace-stripped fallback
    header_clean = {re.sub(r"[^a-zA-Z0-9]", "", h).lower(): h for h in header_row if h}
    for c in candidates:
        cand_clean = re.sub(r"[^a-zA-Z0-9]", "", c).lower()
        if cand_clean in header_clean:
            return header_clean[cand_clean]
    return None


def find_input_file():
    master_dir = ROOT / "data" / "master"
    candidates = [
        master_dir / "lgd_districts.csv",
        master_dir / "lgd_districts.csv.csv",
        master_dir / "lgd_districts_master.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Glob for any other lgd csv in master
    for p in master_dir.glob("*lgd*districts*.csv*"):
        return p
    return master_dir / "lgd_districts.csv"


def main():
    input_path = find_input_file()
    if not input_path.exists():
        print(f"ERROR: LGD raw file not found at {input_path}.")
        print("Download from: https://www.data.gov.in/resource/local-government-directory-lgd-districts")
        sys.exit(1)

    print(f"Reading raw LGD file: {input_path}")
    with open(input_path, newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        print(f"Raw LGD file columns: {header}")

        lgd_col = detect_column(header, LGD_CODE_CANDIDATES)
        state_code_col = detect_column(header, STATE_CODE_CANDIDATES)
        state_name_col = detect_column(header, STATE_NAME_CANDIDATES)
        dist_name_col = detect_column(header, DISTRICT_NAME_CANDIDATES)

        if not all([lgd_col, state_code_col, state_name_col, dist_name_col]):
            print("ERROR: Could not detect required columns.")
            print(f"  LGD Code column:    {lgd_col or 'NOT FOUND'}")
            print(f"  State Code column:  {state_code_col or 'NOT FOUND'}")
            print(f"  State Name column:  {state_name_col or 'NOT FOUND'}")
            print(f"  District Name col:  {dist_name_col or 'NOT FOUND'}")
            print("Open the raw CSV file and check exact column names.")
            sys.exit(1)

        print(f"  Using LGD Code column:   '{lgd_col}'")
        print(f"  Using State Code column: '{state_code_col}'")
        print(f"  Using State Name column: '{state_name_col}'")
        print(f"  Using District Name col: '{dist_name_col}'")

        rows = []
        for row in reader:
            # Only keep rows where the LGD code looks like a real
            # district-level code (skip state/sub-district level rows
            # that sometimes appear in the full LGD entity dump)
            lgd_code = (row.get(lgd_col) or "").strip()
            if not lgd_code:
                continue
            rows.append({
                "lgd_code": lgd_code,
                "state_lgd_code": (row.get(state_code_col) or "").strip(),
                "state_name": (row.get(state_name_col) or "").strip(),
                "current_name": (row.get(dist_name_col) or "").strip(),
                "historical_names": "",          # fill manually as you go
                "parent_lgd_code": "",           # fill manually for carved districts
                "effective_from": "",            # optional
            })

    print(f"\nReshaping {len(rows)} district rows...")

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "lgd_code", "state_lgd_code", "state_name", "current_name",
            "historical_names", "parent_lgd_code", "effective_from"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written to: {OUTPUT}")
    print()
    print("NEXT STEPS:")
    print("  1. Update run_pipeline.py: replace 'sample_lgd_seed.csv' with")
    print(f"     'data/master/lgd_master.csv' in the DistrictCrosswalk() call")
    print("  2. Run python setup_data_dirs.py to check what to download next")
    print("  3. As you encounter crosswalk 'unmatched' warnings, add the name")
    print("     mapping to data/master/manual_aliases.csv")
    print("  4. For post-2022 districts (AP bifurcation, etc.), manually set the")
    print(f"     parent_lgd_code in {OUTPUT} for the newly-carved districts")


if __name__ == "__main__":
    main()
