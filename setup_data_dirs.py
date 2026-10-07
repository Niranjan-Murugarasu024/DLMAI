"""
setup_data_dirs.py — run this to set up folders and verify downloaded data.

Creates every data/ subfolder the pipeline expects and prints a
comprehensive checklist of what data files are present and what to
download next. Safe to re-run anytime.

Usage: python setup_data_dirs.py
"""

import os
import sys
import glob
import re
from pathlib import Path

# Ensure UTF-8 output on Windows consoles without crashing
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

DIRS = [
    DATA / "master",
    DATA / "nfhs" / "district",
    DATA / "nfhs" / "state",
    DATA / "census" / "primary_census_abstract",
    DATA / "census" / "handbooks",
    DATA / "rhs",
    DATA / "jan_aushadhi",
    DATA / "mca21",
    DATA / "niti_aayog",
    DATA / "shapefiles",
    DATA / "secc",
]

NFHS_PRIORITY_STATES = [
    "Tamil_Nadu", "Karnataka", "Maharashtra", "Gujarat", "Telangana",
    "Andhra_Pradesh", "Uttar_Pradesh", "Rajasthan", "West_Bengal",
    "Madhya_Pradesh", "Bihar", "Punjab", "Haryana", "Kerala", "Odisha",
]

JAN_AUSHADHI_STATES = [
    "Maharashtra", "Karnataka", "Tamil_Nadu", "Gujarat", "Telangana",
    "Andhra_Pradesh", "Uttar_Pradesh", "Rajasthan", "West_Bengal",
    "Madhya_Pradesh", "Bihar", "Punjab", "Haryana", "Kerala", "Odisha",
    "Chhattisgarh", "Jharkhand", "Uttarakhand", "Himachal_Pradesh",
    "Jammu_and_Kashmir", "Assam", "Meghalaya", "Manipur", "Nagaland",
    "Mizoram", "Tripura", "Arunachal_Pradesh", "Sikkim", "Goa",
    "Delhi", "Chandigarh", "Puducherry", "Andaman_and_Nicobar",
    "Dadra_and_Nagar_Haveli", "Daman_and_Diu", "Lakshadweep",
]


def normalize_name(s: str) -> str:
    """Normalizes string for fuzzy comparison (e.g. 'Tamil Nadu' -> 'tamilnadu')."""
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()


def find_first_matching(patterns: list, base_dir: Path):
    """Searches for any existing file matching one of several candidate filenames/globs."""
    if not base_dir.exists():
        return None
    for pat in patterns:
        if isinstance(pat, str):
            if "*" in pat or "?" in pat:
                matches = list(base_dir.glob(pat))
                if matches:
                    return matches[0]
            else:
                p = base_dir / pat
                if p.exists():
                    return p
        elif isinstance(pat, Path) and pat.exists():
            return pat
    return None


def inspect_lgd_master():
    candidates = [
        "lgd_master.csv",
        "lgd_districts.csv",
        "lgd_districts.csv.csv",
        "sample_lgd_seed.csv",
    ]
    found = find_first_matching(candidates, DATA / "master")
    if found:
        return found, f"[OK] PRESENT ({found.name})"
    return DATA / "master" / "lgd_districts.csv", "[--] MISSING"


def inspect_lgd_pincodes():
    candidates = [
        "lgd_pincodes.csv",
        "lgd_pincodes.csv.csv",
        "lgd_pincodes.pdf",
        "lgd_pincodes.xlsx",
        "lgd_pincodes.xls",
        "*pincode*.csv",
        "*pincode*.pdf",
        "*pincode*.xlsx",
    ]
    found = find_first_matching(candidates, DATA / "master")
    if found:
        return found, f"[OK] PRESENT ({found.name})"
    return DATA / "master" / "lgd_pincodes.csv", "[--] MISSING"


def inspect_rhs():
    candidates = [
        "district_wise_health_centres.pdf",
        "district-wise-health-centres.pdf",
        "*health*centre*.pdf",
        "*rhs*.pdf",
    ]
    found = find_first_matching(candidates, DATA / "rhs")
    if found:
        return found, f"[OK] PRESENT ({found.name})"
    return DATA / "rhs" / "district_wise_health_centres.pdf", "[--] MISSING"


def inspect_census_pca():
    candidates = [
        "PCA_district_level.csv",
        "PCA_district_level.csv.csv",
        "PCA_district_level.xls",
        "PCA_district_level.xlsx",
        "*PCA*.csv",
        "*PCA*.xls*",
    ]
    found = find_first_matching(candidates, DATA / "census" / "primary_census_abstract")
    if not found:
        found = find_first_matching(candidates, DATA / "census")
    if found:
        return found, f"[OK] PRESENT ({found.name})"
    return DATA / "census" / "primary_census_abstract" / "PCA_district_level.csv", "[--] MISSING"


def inspect_mca21():
    full_cands = ["company_master_data.csv", "company_master_data.csv.csv", "*company*master*.csv"]
    filt_cands = ["pharma_filtered.csv", "pharma_filtered.csv.csv", "*pharma*filtered*.csv"]
    full_found = find_first_matching(full_cands, DATA / "mca21")
    filt_found = find_first_matching(filt_cands, DATA / "mca21")
    return full_found, filt_found


def main():
    print("=" * 74)
    print(" DLMAI Data Directory Setup & Dataset Identification Report")
    print("=" * 74)

    # Create all directories
    created = 0
    for d in DIRS:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created += 1
    print(f"\n[+] Data directory structure checked ({created} new directories created)\n")

    # 1. CORE DATASETS CHECKLIST
    print("CORE REQUIRED FILES — IDENTIFICATION & STATUS:")
    print("-" * 74)

    # LGD Master
    lgd_path, lgd_status = inspect_lgd_master()
    print(f"\n1. Local Government Directory (LGD) Districts Master:")
    print(f"   Status:    {lgd_status}")
    print(f"   Location:  {lgd_path}")
    if (DATA / "master" / "lgd_master.csv").exists():
        print("   Note:      lgd_master.csv is reshaped and ready for the pipeline.")
    elif lgd_path and lgd_path.exists() and "lgd_districts" in lgd_path.name:
        print("   Action:    Raw file detected. Run: python reshape_lgd_master.py to produce lgd_master.csv")
    else:
        print("   Download:  https://www.data.gov.in/resource/local-government-directory-lgd-districts")

    # LGD PIN codes
    pin_path, pin_status = inspect_lgd_pincodes()
    print(f"\n2. LGD PIN Codes Mapping:")
    print(f"   Status:    {pin_status}")
    print(f"   Location:  {pin_path}")
    print("   Download:  https://lgdirectory.gov.in/ -> Local Bodies with PIN Codes")

    # Manual Aliases
    aliases_path = DATA / "master" / "manual_aliases.csv"
    if not aliases_path.exists() and (ROOT / "manual_aliases.csv").exists():
        # Auto-copy seed aliases if missing in data/master
        import shutil
        shutil.copy(ROOT / "manual_aliases.csv", aliases_path)
    aliases_status = "[OK] PRESENT" if aliases_path.exists() else "[--] MISSING"
    print(f"\n3. Manual Name Aliases CSV:")
    print(f"   Status:    {aliases_status}")
    print(f"   Location:  {aliases_path}")

    # RHS
    rhs_path, rhs_status = inspect_rhs()
    print(f"\n4. RHS District-wise Health Centres Table:")
    print(f"   Status:    {rhs_status}")
    print(f"   Location:  {rhs_path}")
    print("   Download:  https://www.nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-centres.pdf")

    # Census PCA
    pca_path, pca_status = inspect_census_pca()
    print(f"\n5. Census Primary Census Abstract (PCA):")
    print(f"   Status:    {pca_status}")
    print(f"   Location:  {pca_path}")
    if pca_path and pca_path.exists() and pca_path.suffix in [".xls", ".xlsx"]:
        print(f"   Note:      Detected Excel format ({pca_path.name}). Supported alongside CSV.")
    print("   Download:  https://www.data.gov.in/catalog/primary-census-abstract-2011-india-and-states-0")

    # MCA21
    mca_full, mca_filt = inspect_mca21()
    print(f"\n6. MCA21 Company Master:")
    print(f"   Full Master:     {f'[OK] PRESENT ({mca_full.name})' if mca_full else '[--] MISSING'}")
    print(f"   Pharma-Filtered: {f'[OK] PRESENT ({mca_filt.name})' if mca_filt else '[--] MISSING'}")
    if mca_full and not mca_filt:
        print("   Action:    Full MCA21 file found. Create filtered subset using:")
        print('              grep -i "pharmaceutical\\|21001\\|21002\\|21009\\|46497\\|4772" '
              f'{mca_full} > data/mca21/pharma_filtered.csv')

    # 2. NFHS COVERAGE
    print("\n" + "=" * 74)
    print("NFHS-5 DISTRICT FACTSHEETS — COVERAGE BY STATE:")
    print("-" * 74)
    nfhs_dir = DATA / "nfhs" / "district"
    all_nfhs_pdfs = list(DATA.glob("nfhs/**/*.pdf"))
    
    # State mapping dictionary
    state_pdf_counts = {}
    for st in NFHS_PRIORITY_STATES:
        norm_st = normalize_name(st)
        # Check subdirectories matching state
        count = 0
        for pdf in all_nfhs_pdfs:
            parts_norm = [normalize_name(p) for p in pdf.parts]
            if norm_st in parts_norm or norm_st in normalize_name(pdf.name):
                count += 1
        state_pdf_counts[st] = count
        indicator = "[OK]" if count > 0 else "[--]"
        print(f"  {indicator} {st:30s}  {count} district PDFs identified")
    
    total_nfhs = len(all_nfhs_pdfs)
    print(f"\n  Total NFHS district PDFs identified across all folders: {total_nfhs}")
    print("  Download from: https://www.nfhsiips.in/nfhsuser/nfhs5.php")

    # 3. JAN AUSHADHI COVERAGE
    print("\n" + "=" * 74)
    print("JAN AUSHADHI KENDRA EXPORTS — COVERAGE BY STATE:")
    print("-" * 74)
    ja_dir = DATA / "jan_aushadhi"
    all_ja_files = list(ja_dir.glob("*.*")) if ja_dir.exists() else []
    ja_total = 0
    for st in JAN_AUSHADHI_STATES:
        norm_st = normalize_name(st)
        matched_file = None
        for f in all_ja_files:
            if norm_st in normalize_name(f.stem):
                matched_file = f
                break
        if matched_file:
            ja_total += 1
            print(f"  [OK] {st:30s} ({matched_file.name})")
        else:
            print(f"  [--] {st}")
    
    print(f"\n  States covered: {ja_total} / {len(JAN_AUSHADHI_STATES)}")
    print("  Download from: https://janaushadhi.gov.in/near-by-kendra")

    # 4. SUMMARY & NEXT STEPS
    print("\n" + "=" * 74)
    print("RECOMMENDED NEXT ACTION:")
    print("-" * 74)
    
    if not (DATA / "master" / "lgd_master.csv").exists():
        if lgd_path and lgd_path.exists():
            print(f"  [!] Run reshape script to prepare district master:")
            print(f"      python reshape_lgd_master.py")
        else:
            print("  1. Download lgd_districts.csv from data.gov.in -> data/master/")
            print("     URL: https://www.data.gov.in/resource/local-government-directory-lgd-districts")
    elif not rhs_path or not rhs_path.exists():
        print("  2. Download the RHS district table (Step 4)")
        print("     URL: https://www.nhm.gov.in/images/pdf/monitoring/rhs/district-wise-health-centres.pdf")
    elif not pca_path or not pca_path.exists():
        print("  3. Download Census PCA dataset (Step 3A)")
        print("     URL: https://www.data.gov.in/catalog/primary-census-abstract-2011-india-and-states-0")
    elif total_nfhs == 0:
        print("  4. Begin NFHS-5 district factsheet downloads into data/nfhs/district/[State]/")
        print("     URL: https://www.nfhsiips.in/nfhsuser/nfhs5.php")
    else:
        print(f"  Ready for indexing! Total NFHS PDFs collected: {total_nfhs}")
        print("  Run pipeline: python run_pipeline.py (or python build_index.py)")
    print("=" * 74)


if __name__ == "__main__":
    main()

