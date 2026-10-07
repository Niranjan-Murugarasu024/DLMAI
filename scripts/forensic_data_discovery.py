"""
DLMAI v3.0 Forensic Discovery and Dataset Audit Script.
Scans every folder, inspects all files (CSVs, PDFs, JSONs, YAMLs, TXTs),
extracts schemas, row/col counts, headers, and builds the raw dataset inventory.
"""

import os
import sys
import glob
import json
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path

def get_file_info(file_path):
    p = Path(file_path)
    stat = p.stat()
    size = stat.st_size
    ext = p.suffix.lower()
    info = {
        "file_path": str(p).replace("\\", "/"),
        "file_name": p.name,
        "extension": ext,
        "size_bytes": size,
        "row_count": None,
        "col_count": None,
        "columns": [],
        "schema_summary": "",
        "category": "UNKNOWN",
        "is_safe_for_prod": True
    }
    
    # Categorize
    if "data/master" in info["file_path"]:
        info["category"] = "MASTER_GEOGRAPHY"
    elif "data/nfhs" in info["file_path"]:
        info["category"] = "RAW_SURVEY_NFHS"
    elif "data/rhs" in info["file_path"]:
        info["category"] = "RAW_HEALTHCARE_RHS"
    elif "data/jan_aushadhi" in info["file_path"]:
        info["category"] = "RAW_JAN_AUSHADHI"
    elif "data/census" in info["file_path"]:
        info["category"] = "RAW_CENSUS_DEMOGRAPHICS"
    elif "data/mca" in info["file_path"].lower() or "data/mca21" in info["file_path"].lower():
        info["category"] = "CORPORATE_MCA21"
    elif "data/secc" in info["file_path"]:
        info["category"] = "RAW_SECC_SOCIOECONOMIC"
    elif "data/niti_aayog" in info["file_path"]:
        info["category"] = "POLICY_NITI_AAYOG"
    elif "data/shapefiles" in info["file_path"]:
        info["category"] = "GEOSPATIAL_SHAPEFILE"
    elif "outputs/data_quality" in info["file_path"]:
        info["category"] = "DATA_QUALITY_AUDIT"
    elif "outputs/red_team" in info["file_path"]:
        info["category"] = "VALIDATION_ARTIFACT"
    elif "outputs" in info["file_path"]:
        info["category"] = "PRODUCTION_OUTPUT"
    elif "config" in info["file_path"]:
        info["category"] = "CONFIG_YAML"
    elif "src" in info["file_path"]:
        info["category"] = "PRODUCTION_CODE"
    elif "tests" in info["file_path"]:
        info["category"] = "TEST_FIXTURE"
    elif "docs" in info["file_path"]:
        info["category"] = "DOCUMENTATION"
    else:
        info["category"] = "PROJECT_MISC"
        
    # Detailed inspection for CSVs
    if ext == ".csv":
        try:
            df = pd.read_csv(file_path, nrows=5)
            # count total rows
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                row_cnt = sum(1 for _ in f) - 1
            info["row_count"] = max(0, row_cnt)
            info["col_count"] = len(df.columns)
            info["columns"] = list(df.columns)
            info["schema_summary"] = ", ".join(list(df.columns)[:10]) + ("..." if len(df.columns) > 10 else "")
        except Exception as e:
            info["schema_summary"] = f"Error reading CSV: {e}"
            
    # Detailed inspection for JSON
    elif ext == ".json":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                info["row_count"] = len(data)
                if len(data) > 0 and isinstance(data[0], dict):
                    info["col_count"] = len(data[0])
                    info["columns"] = list(data[0].keys())
            elif isinstance(data, dict):
                info["row_count"] = len(data)
                info["col_count"] = 1
                info["columns"] = list(data.keys())[:10]
            info["schema_summary"] = f"JSON object with {len(data) if hasattr(data, '__len__') else 1} top-level keys"
        except Exception as e:
            info["schema_summary"] = f"Error reading JSON: {e}"
            
    # Detailed inspection for YAML
    elif ext in [".yaml", ".yml"]:
        try:
            import yaml
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            info["schema_summary"] = f"YAML config with keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}"
        except Exception as e:
            info["schema_summary"] = f"Error reading YAML: {e}"
            
    return info

def run_discovery():
    root_dir = "."
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        if any(skip in root for skip in [".git", "__pycache__", ".pytest_cache", ".gemini"]):
            continue
        for f in files:
            full_p = os.path.join(root, f)
            all_files.append(get_file_info(full_p))
            
    df_all = pd.DataFrame(all_files)
    print(f"Total discovered files: {len(df_all)}")
    print("\nFile breakdown by category:")
    print(df_all["category"].value_counts())
    
    # Save raw audit inventory
    os.makedirs("outputs/data_discovery", exist_ok=True)
    df_all.to_csv("outputs/data_discovery/raw_file_scan.csv", index=False)
    print("\nSaved raw file scan to outputs/data_discovery/raw_file_scan.csv")
    
    # Print all data files specifically
    df_data = df_all[df_all["category"].str.startswith("RAW_") | df_all["category"].isin(["MASTER_GEOGRAPHY", "CORPORATE_MCA21", "POLICY_NITI_AAYOG", "GEOSPATIAL_SHAPEFILE"])]
    print("\n================ DATASET FILES SUMMARY ================")
    for _, r in df_data.iterrows():
        print(f"[{r['category']}] {r['file_path']} ({r['size_bytes']} bytes) - Rows: {r['row_count']}, Cols: {r['col_count']}")

if __name__ == "__main__":
    run_discovery()
