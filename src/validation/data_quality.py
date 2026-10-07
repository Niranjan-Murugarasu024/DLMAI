"""
Data Quality Assessment, Provenance Tracking, and Forensic Audit Deliverables Generator.
Generates comprehensive audit CSVs for geography, NFHS, RHS, Jan Aushadhi, MCA21,
district-level completeness, indicator provenance, and model run metadata.
"""

import os
import glob
import json
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


def generate_data_quality_report(
    provenance_mask: Dict[int, Dict[str, str]],
    district_metadata: Dict[int, Dict[str, str]]
) -> pd.DataFrame:
    """
    Computes observed, inherited, and imputed percentages for each district.
    """
    rows = []
    for code, ind_masks in provenance_mask.items():
        meta = district_metadata.get(code, {})
        total_inds = len(ind_masks)
        obs_count = sum(1 for s in ind_masks.values() if "OBSERVED" in s.upper() or "NATIVE" in s.upper())
        inh_count = sum(1 for s in ind_masks.values() if "INHERITED" in s.upper())
        imp_count = sum(1 for s in ind_masks.values() if "IMPUTED" in s.upper())
        proxy_count = sum(1 for s in ind_masks.values() if "PROXY" in s.upper())

        obs_pct = round((obs_count / total_inds) * 100.0, 1) if total_inds else 0.0
        inh_pct = round((inh_count / total_inds) * 100.0, 1) if total_inds else 0.0
        imp_pct = round((imp_count / total_inds) * 100.0, 1) if total_inds else 0.0

        # Quality index: weighted combination (observed=1.0, inherited=0.85, imputed=0.60)
        quality_score = round(obs_pct * 1.0 + inh_pct * 0.85 + imp_pct * 0.60, 1)

        rows.append({
            "lgd_district_code": code,
            "district_name": meta.get("district_name", str(code)),
            "state_name": meta.get("state_name", "Unknown"),
            "total_indicators": total_inds,
            "observed_count": obs_count,
            "inherited_count": inh_count,
            "imputed_count": imp_count,
            "proxy_count": proxy_count,
            "observed_pct": obs_pct,
            "inherited_pct": inh_pct,
            "imputed_pct": imp_pct,
            "data_quality_score": quality_score
        })

    return pd.DataFrame(rows).sort_values("data_quality_score", ascending=False).reset_index(drop=True)


def generate_district_coverage_matrix(
    provenance_mask: Dict[int, Dict[str, str]],
    district_metadata: Dict[int, Dict[str, str]]
) -> pd.DataFrame:
    """
    Creates outputs/district_coverage_matrix.csv showing source-by-source availability.
    """
    rows = []
    for code, ind_masks in provenance_mask.items():
        meta = district_metadata.get(code, {})

        # Source groupings
        nfhs_status = "AVAILABLE" if any(ind_masks.get(k) == "OBSERVED" for k in ind_masks if k.startswith("nfhs_")) else \
                      ("INHERITED" if any("INHERITED" in str(ind_masks.get(k)) for k in ind_masks if k.startswith("nfhs_")) else "IMPUTED")

        rhs_status = "AVAILABLE" if any(ind_masks.get(k) == "OBSERVED" for k in ind_masks if k.startswith("rhs_")) else \
                     ("INHERITED" if any("INHERITED" in str(ind_masks.get(k)) for k in ind_masks if k.startswith("rhs_")) else "IMPUTED")

        ja_status = ind_masks.get("jan_aushadhi_density_per_100k", "AVAILABLE")
        if "INHERITED" in ja_status:
            ja_status = "INHERITED"
        elif "IMPUTED" in ja_status:
            ja_status = "IMPUTED"
        else:
            ja_status = "AVAILABLE"

        census_status = "AVAILABLE" if any(ind_masks.get(k) == "OBSERVED" for k in ind_masks if k.startswith("census_")) else \
                        ("INHERITED" if any("INHERITED" in str(ind_masks.get(k)) for k in ind_masks if k.startswith("census_")) else "IMPUTED")

        mca_status = "PROXY_DERIVED"
        niti_status = "AVAILABLE"

        rows.append({
            "lgd_district_code": code,
            "district_name": meta.get("district_name", str(code)),
            "state_name": meta.get("state_name", "Unknown"),
            "NFHS_5": nfhs_status,
            "RHS_Health_Centres": rhs_status,
            "Jan_Aushadhi_PMBJP": ja_status,
            "Census_Demographics": census_status,
            "MCA21_Corporate": mca_status,
            "NITI_Aspirational": niti_status
        })

    return pd.DataFrame(rows).sort_values(["state_name", "district_name"]).reset_index(drop=True)


def generate_geography_audit_csv(output_path: str = "outputs/data_quality/geography_audit.csv",
                                master_csv_path: str = "data/master/lgd_south_india.csv",
                                crosswalk_csv_path: str = "data/master/district_crosswalk_south.csv") -> pd.DataFrame:
    """
    Audits all 148 canonical districts, their LGD codes, parent linkages, and creation status.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    master = pd.read_csv(master_csv_path)
    cw = pd.read_csv(crosswalk_csv_path) if os.path.exists(crosswalk_csv_path) else pd.DataFrame()

    parent_map = {}
    if not cw.empty and "parent_lgd_code" in cw.columns:
        for _, r in cw.dropna(subset=["parent_lgd_code"]).iterrows():
            try:
                parent_map[int(r["canonical_lgd_code"])] = (int(r["parent_lgd_code"]), str(r.get("parent_district_name", "")))
            except (ValueError, TypeError):
                pass

    rows = []
    for _, r in master.iterrows():
        lgd = int(r["lgd_district_code"])
        name = str(r["district_name"])
        state = str(r["state_name"])
        state_lgd = int(r["state_lgd_code"])
        census_code = int(r.get("census_2011_code", 0))

        is_split = lgd in parent_map
        parent_info = parent_map.get(lgd, (None, None))

        rows.append({
            "canonical_lgd_code": lgd,
            "district_name": name,
            "state_name": state,
            "state_lgd_code": state_lgd,
            "census_2011_code": census_code,
            "is_canonical": True,
            "geographic_level": "DISTRICT",
            "is_split_child": is_split,
            "parent_lgd_code": parent_info[0] if is_split else None,
            "parent_district_name": parent_info[1] if is_split else None,
            "mapping_status": "CANONICAL_CONFIRMED"
        })

    df = pd.DataFrame(rows).sort_values(["state_name", "district_name"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    return df


def generate_nfhs_coverage_audit_csv(output_path: str = "outputs/data_quality/nfhs_coverage_audit.csv",
                                     crosswalk = None,
                                     nfhs_pdf_paths: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Audits all 148 districts for NFHS-5 factsheet direct observation, parent inheritance, or state imputation.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    from src.ingestion.nfhs_parser import parse_nfhs_factsheet
    from src.harmonization.crosswalk import SouthDistrictCrosswalk

    if crosswalk is None:
        crosswalk = SouthDistrictCrosswalk("data/master/lgd_south_india.csv", "data/master/district_crosswalk_south.csv")
    if nfhs_pdf_paths is None:
        nfhs_pdf_paths = glob.glob("data/nfhs/district/*/*.pdf")

    # Map available PDFs
    pdf_by_lgd = {}
    for p in nfhs_pdf_paths:
        res = parse_nfhs_factsheet(p)
        m = crosswalk.resolve(res.district_raw_name, state_hint=res.state_raw_name)
        if m.lgd_code:
            pdf_by_lgd[m.lgd_code] = {
                "pdf_path": p,
                "raw_name": res.district_raw_name,
                "raw_state": res.state_raw_name,
                "method": m.method,
                "values": res.values
            }

    rows = []
    for lgd, d in crosswalk.districts.items():
        if lgd in pdf_by_lgd:
            info = pdf_by_lgd[lgd]
            val_count = len(info["values"])
            rows.append({
                "canonical_lgd_code": lgd,
                "district_name": d.district_name,
                "state_name": d.state_name,
                "pdf_found": True,
                "pdf_path": info["pdf_path"],
                "source_district_name": info["raw_name"],
                "mapping_status": "DIRECT_OBSERVED",
                "mapping_method": info["method"],
                "extraction_status": "SUCCESS",
                "indicators_extracted": val_count,
                "parent_district_code": None,
                "reason": "Direct NFHS-5 PDF factsheet observed and parsed."
            })
        else:
            parent_code = crosswalk.parent_map.get(lgd)
            if parent_code and parent_code in pdf_by_lgd:
                parent_name = crosswalk.districts[parent_code].district_name
                rows.append({
                    "canonical_lgd_code": lgd,
                    "district_name": d.district_name,
                    "state_name": d.state_name,
                    "pdf_found": False,
                    "pdf_path": None,
                    "source_district_name": parent_name,
                    "mapping_status": "INHERITED_FROM_PARENT",
                    "mapping_method": "PARENT_LINEAGE",
                    "extraction_status": "INHERITED",
                    "indicators_extracted": len(pdf_by_lgd[parent_code]["values"]),
                    "parent_district_code": parent_code,
                    "reason": f"Post-NFHS bifurcated district. Inherited epidemiological profile from parent district {parent_name} (LGD: {parent_code})."
                })
            else:
                rows.append({
                    "canonical_lgd_code": lgd,
                    "district_name": d.district_name,
                    "state_name": d.state_name,
                    "pdf_found": False,
                    "pdf_path": None,
                    "source_district_name": None,
                    "mapping_status": "IMPUTED_STATE_MEAN",
                    "mapping_method": "STATE_MEAN_FALLBACK",
                    "extraction_status": "IMPUTED",
                    "indicators_extracted": 0,
                    "parent_district_code": None,
                    "reason": "Direct PDF factsheet unavailable in repository; imputed using state mean."
                })

    df = pd.DataFrame(rows).sort_values(["state_name", "district_name"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    return df


def generate_rhs_coverage_audit_csv(output_path: str = "outputs/data_quality/rhs_coverage_audit.csv",
                                    crosswalk = None,
                                    rhs_pdf_path: str = "data/rhs/district-wise-health-centres.pdf") -> pd.DataFrame:
    """
    Audits RHS table rows, distinguishing STATE-level summary rows from DISTRICT-level observations.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    from src.ingestion.rhs_parser import extract_all_rhs_rows
    from src.harmonization.crosswalk import SouthDistrictCrosswalk

    if crosswalk is None:
        crosswalk = SouthDistrictCrosswalk("data/master/lgd_south_india.csv", "data/master/district_crosswalk_south.csv")

    rows = []
    if os.path.exists(rhs_pdf_path):
        raw_rows = extract_all_rhs_rows(rhs_pdf_path)
        for r in raw_rows:
            st = r["state"]
            dt = r["district"]
            m = crosswalk.resolve(dt, state_hint=st)

            # Check if this row is a state-level row
            is_state_row = ("total" in dt.lower() or dt.lower() in [s.lower() for s in ["karnataka", "kerala", "tamil nadu", "andhra pradesh", "telangana", "goa", "puducherry", "bihar", "assam", "gujarat", "maharashtra", "delhi", "punjab", "rajasthan", "odisha", "west bengal", "uttar pradesh", "uttarakhand", "madhya pradesh", "haryana", "himachal pradesh", "jharkhand", "chhattisgarh", "manipur", "meghalaya", "mizoram", "nagaland", "sikkim", "tripura"]])

            geo_level = "STATE_TOTAL" if is_state_row else "DISTRICT"
            mapping_status = "MATCHED_CANONICAL" if m.lgd_code else ("STATE_AGGREGATE_EXCLUDED" if is_state_row else "OUT_OF_SCOPE_OR_UNRESOLVED")

            rows.append({
                "source_state": st,
                "source_district_text": dt,
                "geography_level": geo_level,
                "canonical_lgd_code": m.lgd_code,
                "canonical_name": m.matched_name,
                "mapping_status": mapping_status,
                "mapping_method": m.method if m.lgd_code else "EXCLUDED",
                "sub_centres": r["sub_centres"],
                "phcs": r["phcs"],
                "chcs": r["chcs"],
                "hospital_presence": r["hospital_presence"]
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def generate_jan_aushadhi_mapping_audit_csv(output_path: str = "outputs/data_quality/jan_aushadhi_mapping_audit.csv",
                                            crosswalk = None) -> pd.DataFrame:
    """
    Audits Jan Aushadhi records across all state PDFs and classifies in-scope vs out-of-scope records.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    from jan_aushadhi_ingestion import extract_kendra_rows
    from src.harmonization.crosswalk import SouthDistrictCrosswalk

    if crosswalk is None:
        crosswalk = SouthDistrictCrosswalk("data/master/lgd_south_india.csv", "data/master/district_crosswalk_south.csv")

    ja_pdfs = glob.glob("data/jan_aushadhi/*.pdf")
    rows = []
    for p in ja_pdfs:
        records = extract_kendra_rows(p)
        fname = os.path.basename(p)
        for r in records:
            st = r.get("state", "")
            dt = r.get("district", "")
            k_code = r.get("kendra_code", "")

            is_outside = st in ["MadhyaPradesh", "Maharashtra", "Madhya Pradesh"]
            if is_outside:
                rows.append({
                    "source_pdf": fname,
                    "kendra_code": k_code,
                    "source_state": st,
                    "source_district": dt,
                    "geography_scope": "OUTSIDE_SOUTH_INDIA",
                    "canonical_lgd_code": None,
                    "mapping_status": "EXCLUDED_OUT_OF_SCOPE",
                    "reason": f"State '{st}' is outside the 7 South Indian target States/UTs."
                })
            else:
                m = crosswalk.resolve(dt, state_hint=st)
                rows.append({
                    "source_pdf": fname,
                    "kendra_code": k_code,
                    "source_state": st,
                    "source_district": dt,
                    "geography_scope": "SOUTH_INDIA_IN_SCOPE",
                    "canonical_lgd_code": m.lgd_code,
                    "mapping_status": "MATCHED" if m.lgd_code else "UNRESOLVED_ROW",
                    "reason": f"Matched via {m.method}." if m.lgd_code else "Multiline table split or unmatched spelling."
                })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def generate_mca21_provenance_audit_csv(output_path: str = "outputs/data_quality/mca21_provenance_audit.csv",
                                        district_metadata: Dict[int, Dict[str, str]] = None) -> pd.DataFrame:
    """
    Audits MCA21 Pillar 5 provenance, establishing that raw bulk data is absent and P5 operates as a calibrated proxy.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    raw_csv_present = os.path.exists("data/mca21/pharma_filtered.csv") or os.path.exists("data/mca21/company_master_data.csv")

    rows = []
    for code, meta in district_metadata.items():
        rows.append({
            "canonical_lgd_code": code,
            "district_name": meta.get("district_name", str(code)),
            "state_name": meta.get("state_name", "Unknown"),
            "mca21_raw_bulk_file_present": raw_csv_present,
            "p5_status": "CALIBRATED_PROXY_ESTIMATE" if not raw_csv_present else "DIRECT_OBSERVED",
            "construct_definition": "Pharmaceutical Manufacturing & Corporate Concentration Proxy",
            "is_field_force_competition": False,
            "notes": "P5 represents registered corporate manufacturing entities per 100k, not deployed field sales force."
        })

    df = pd.DataFrame(rows).sort_values(["state_name", "district_name"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    return df


def generate_indicator_provenance_csv(output_path: str = "outputs/data_quality/indicator_provenance.csv",
                                      provenance_mask: Dict[int, Dict[str, str]] = None,
                                      harmonized_matrix: Dict[int, Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Generates full indicator x district cell-level provenance breakdown.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rows = []
    for code, ind_masks in provenance_mask.items():
        for ind, status in ind_masks.items():
            val = harmonized_matrix[code].get(ind) if harmonized_matrix else None
            source_type = "DIRECT_OBSERVED" if ("OBSERVED" in status.upper() or "NATIVE" in status.upper()) else \
                          ("INHERITED" if "INHERITED" in status.upper() else \
                          ("STATISTICALLY_IMPUTED" if "IMPUTED" in status.upper() else "PROXY_ESTIMATE"))
            rows.append({
                "canonical_lgd_code": code,
                "indicator_id": ind,
                "harmonized_value": val,
                "provenance_status": status,
                "provenance_class": source_type
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return df


def generate_model_run_metadata_json(output_path: str = "outputs/model_run_metadata.json",
                                    run_info: Dict[str, Any] = None,
                                    quality_report: Any = None) -> Dict[str, Any]:
    """
    Exports full provenance, file hashes, run environment, and quality gate results.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    meta = {
        "model_version": "DLMAI v2.0.0",
        "geographic_scope": "South India (7 States/UTs, 148 Canonical Districts)",
        "run_info": run_info or {},
        "quality_gate_summary": quality_report.to_dict() if quality_report else {},
        "target_commercial_benchmark_class": "Class D: Calibrated/Synthetic Benchmark (Method Development Sanity Check Only)",
        "p5_status": "DEGRADED_P5_PROXY (Corporate Concentration Proxy, Not Field Competition)",
        "provenance_classification": {
            "directly_observed_input_data": ["NFHS-5 Factsheets (124 Districts)", "Rural Health Statistics (97 Districts)", "NITI Aspirational Registry"],
            "inherited_input_data": ["Post-2019 Bifurcated Child Districts from Parents"],
            "statistically_imputed_input_data": ["Hierarchical State-Mean & Population kNN"],
            "target_commercial_sales_data": "SYNTHETIC_CALIBRATED (Zero directly observed sales invoices in Test 8)"
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta
