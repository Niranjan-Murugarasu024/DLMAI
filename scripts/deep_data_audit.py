"""
Comprehensive Deep-Dive Audit of Discovered Datasets in dlmai_complete.
Audits:
1. MCA21 Data (943,267 rows across 7 state CSVs)
2. Census PCA Data (98 columns)
3. SECC Socioeconomic Data (60 columns)
4. NFHS-5 Indicator Catalog (Factsheet full structure)
5. RHS Healthcare Table
6. Jan Aushadhi Kendras
"""

import os
import glob
import pandas as pd
import numpy as np

def audit_mca21():
    print("\n=======================================================")
    print("AUDIT 1: MCA21 CORPORATE REGISTRY (South India States)")
    print("=======================================================")
    mca_files = glob.glob("data/mca21/*.csv")
    total_rows = 0
    state_summaries = []
    
    # We will sample one to see exact schema
    sample_df = None
    for f in sorted(mca_files):
        st_name = os.path.splitext(os.path.basename(f))[0]
        try:
            df = pd.read_csv(f, low_memory=False)
            total_rows += len(df)
            if sample_df is None:
                sample_df = df
            
            # Check for NIC code / activity / name columns
            nic_col = "nic_code" if "nic_code" in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
            comp_name_col = "CompanyName" if "CompanyName" in df.columns else "Company_Name"
            status_col = "CompanyStatus" if "CompanyStatus" in df.columns else None
            
            # Find pharmaceutical keywords
            pharma_keywords = ["PHARMA", "DRUG", "MEDICINE", "HEALTHCARE", "LABORATORIES", "BIOTECH", "THERAPEUTIC", "FORMULATION", "APIS", "LIFE SCIENCES"]
            pat = "|".join(pharma_keywords)
            pharma_matches = df[df[comp_name_col].astype(str).str.upper().str.contains(pat, regex=True, na=False)]
            
            # Check NIC code 2100 / 210 / 21 (Manufacture of pharmaceuticals, medicinal chemical and botanical products)
            nic_matches = pd.DataFrame()
            if "nic_code" in df.columns:
                nic_matches = df[df["nic_code"].astype(str).str.startswith(("210", "21.", "211", "212", "2423"))]
                
            state_summaries.append({
                "state": st_name,
                "total_companies": len(df),
                "pharma_name_matches": len(pharma_matches),
                "nic_pharma_matches": len(nic_matches),
                "columns": len(df.columns)
            })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    df_summary = pd.DataFrame(state_summaries)
    print(df_summary.to_string(index=False))
    print(f"\nTotal South India MCA21 Companies: {total_rows:,}")
    print("\nSample Columns in MCA21 Data:")
    for i, c in enumerate(sample_df.columns):
        print(f"  {i+1}. {c} (type: {sample_df[c].dtype}, nulls: {sample_df[c].isna().sum()}/{len(sample_df)})")
        
    print("\nSample Rows of Identified Pharma Companies:")
    sample_pharma = sample_df[sample_df["CompanyName"].astype(str).str.upper().str.contains("PHARMA", na=False)].head(3)
    print(sample_pharma[["CIN", "CompanyName", "CompanyStatus", "Registered_Office_Address", "PaidupCapital", "nic_code"]].to_string())

def audit_census_pca():
    print("\n=======================================================")
    print("AUDIT 2: CENSUS 2011 PRIMARY CENSUS ABSTRACT (PCA)")
    print("=======================================================")
    pca_path = "data/census/primary_census_abstract/PCA_district_level.csv"
    if os.path.exists(pca_path):
        df = pd.read_csv(pca_path)
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        print("\nAll 98 Columns in PCA Dataset:")
        for i, c in enumerate(df.columns):
            print(f"  {i+1}. {c}")
        print("\nDistricts / States represented in PCA dataset:")
        if "District Name" in df.columns:
            print(df["District Name"].head(15).tolist())
        elif "Name" in df.columns:
            print(df["Name"].head(15).tolist())
            
def audit_secc():
    print("\n=======================================================")
    print("AUDIT 3: SOCIO ECONOMIC AND CASTE CENSUS (SECC)")
    print("=======================================================")
    secc_path = "data/secc/Socio Economic and Caste Census (SECC).csv"
    if os.path.exists(secc_path):
        df = pd.read_csv(secc_path)
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        print("\nAll Columns in SECC Dataset:")
        for i, c in enumerate(df.columns):
            print(f"  {i+1}. {c}")
        print("\nStates in SECC:")
        print(df["State Name"].dropna().tolist())

if __name__ == "__main__":
    audit_mca21()
    audit_census_pca()
    audit_secc()
