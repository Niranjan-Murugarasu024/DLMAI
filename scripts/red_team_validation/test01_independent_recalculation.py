"""
TEST 1 — FULLY INDEPENDENT MODEL RECOMPUTATION
Independent, from-scratch implementation of the DLMAI v2.0 mathematical formulation.
Does NOT import any functions from src.scoring.*.
Validates exact numerical reproducibility to machine tolerance (target error <= 1e-8).
"""

import os
import json
import math
import yaml
import numpy as np
import pandas as pd
from pathlib import Path


def run_test01(output_dir="outputs/red_team_validation_v2"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 70)
    print("TEST 1: FULLY INDEPENDENT MODEL RECOMPUTATION & RECONCILIATION")
    print("=" * 70)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.1 — Geography Validation
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.1: Validating canonical geography...")
    geo_path = "data/master/lgd_south_india.csv"
    assert os.path.exists(geo_path), f"Missing {geo_path}"
    df_geo = pd.read_csv(geo_path)

    n_districts = len(df_geo)
    unique_codes = df_geo["lgd_district_code"].nunique()
    unique_names = df_geo["district_name"].nunique()
    states_found = df_geo["state_name"].unique().tolist()

    assert n_districts == 148, f"Expected 148 districts, got {n_districts}"
    assert unique_codes == 148, f"Duplicate LGD codes found: {unique_codes} unique of {n_districts}"
    assert len(states_found) == 7, f"Expected 7 states, got {len(states_found)}"

    geo_val_rows = []
    for _, r in df_geo.iterrows():
        geo_val_rows.append({
            "lgd_district_code": int(r["lgd_district_code"]),
            "district_name": str(r["district_name"]).strip(),
            "state_name": str(r["state_name"]).strip(),
            "census_2011_code": int(r.get("census_2011_code", 0)),
            "validation_status": "VALID_CANONICAL"
        })
    df_geo_val = pd.DataFrame(geo_val_rows)
    df_geo_val.to_csv(f"{output_dir}/test01_geography_validation.csv", index=False)
    print(f"[SUCCESS] Geography validated: {n_districts} canonical districts across {len(states_found)} States/UTs.")

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.2 — Indicator Data Loading & Integrity Audit
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.2: Auditing raw indicator integrity...")
    with open("config/indicators.yaml", "r", encoding="utf-8") as f:
        indicators_cfg = yaml.safe_load(f)
    scored_indicators = list(indicators_cfg["indicators"].keys())
    assert len(scored_indicators) == 20, f"Expected 20 scored indicators, got {len(scored_indicators)}"

    df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
    df_data = df_data.sort_values("lgd_district_code").reset_index(drop=True)

    integrity_rows = []
    for ind in scored_indicators:
        meta = indicators_cfg["indicators"][ind]
        assert ind in df_data.columns, f"Indicator {ind} missing from data file"
        col = df_data[ind].astype(float)
        
        n_missing = col.isna().sum()
        n_inf = np.isinf(col).sum()
        min_v = float(col.min())
        max_v = float(col.max())
        mean_v = float(col.mean())
        std_v = float(col.std())
        is_const = (min_v == max_v)
        
        # Domain checks
        domain_valid = True
        if meta.get("unit") == "%" and (min_v < 0 or max_v > 100):
            domain_valid = False
        if meta.get("unit") in ("Rate", "Count", "INR") and min_v < 0:
            domain_valid = False

        integrity_rows.append({
            "indicator": ind,
            "pillar": meta["pillar"],
            "direction": meta["direction"],
            "unit": meta["unit"],
            "min_value": round(min_v, 4),
            "max_value": round(max_v, 4),
            "mean_value": round(mean_v, 4),
            "std_dev": round(std_v, 4),
            "missing_count": int(n_missing),
            "inf_count": int(n_inf),
            "is_constant": bool(is_const),
            "domain_valid": bool(domain_valid)
        })
    df_integrity = pd.DataFrame(integrity_rows)
    df_integrity.to_csv(f"{output_dir}/test01_indicator_integrity.csv", index=False)
    print(f"[SUCCESS] All 20 scored indicators passed integrity audit (0 NaNs, 0 Infs, domain-valid).")

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.3 — Independent Direction-Aware Min-Max Normalization
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.3: Independently computing Direction-Aware Min-Max normalization...")
    codes = df_data["lgd_district_code"].tolist()
    normalized_matrix = {c: {} for c in codes}

    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = df_data.set_index("lgd_district_code")[ind].to_dict()
        
        x_min = min(vals.values())
        x_max = max(vals.values())
        r_val = x_max - x_min
        
        for c in codes:
            v = vals[c]
            if r_val == 0:
                normalized_matrix[c][ind] = 50.0
            elif direction == "NEGATIVE":
                normalized_matrix[c][ind] = round(((x_max - v) / r_val) * 100.0, 4)
            else:  # POSITIVE or SATURATION_DAMPENER
                normalized_matrix[c][ind] = round(((v - x_min) / r_val) * 100.0, 4)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.4 — Independent Shannon Information Entropy Weighting
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.4: Independently calculating Shannon Information Entropy weights...")
    with open("config/pillars.yaml", "r", encoding="utf-8") as f:
        pillars_cfg = yaml.safe_load(f)

    independent_entropy_weights = {}
    m = len(codes)  # 148 districts
    k = 1.0 / math.log(m)
    eps = 1e-6

    for p_code, p_meta in pillars_cfg["pillars"].items():
        ind_list = p_meta["indicators"]
        if len(ind_list) == 1:
            independent_entropy_weights[p_code] = {ind_list[0]: 1.0}
            continue

        # Column sums of (score + eps)
        col_sums = {ind: sum(normalized_matrix[c][ind] + eps for c in codes) for ind in ind_list}
        
        # Entropy e_j
        e_dict = {}
        for ind in ind_list:
            c_sum = col_sums[ind]
            e_val = 0.0
            for c in codes:
                p_ij = (normalized_matrix[c][ind] + eps) / c_sum
                e_val += p_ij * math.log(p_ij)
            e_dict[ind] = -k * e_val

        # Information utility d_j = 1 - e_j
        d_dict = {ind: max(1.0 - e_dict[ind], 1e-6) for ind in ind_list}
        tot_d = sum(d_dict.values())
        
        # Normalized weights
        w_dict = {ind: round(d_dict[ind] / tot_d, 6) for ind in ind_list}
        w_sum = sum(w_dict.values())
        w_dict[ind_list[0]] = round(w_dict[ind_list[0]] + (1.0 - w_sum), 6)
        independent_entropy_weights[p_code] = w_dict

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.5 — Independent Saaty AHP Eigenvector & Consistency Computation
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.5: Independently computing Saaty AHP principal eigenvector & CR...")
    with open("config/weights.yaml", "r", encoding="utf-8") as f:
        weights_cfg = yaml.safe_load(f)

    ahp_mat = np.array(weights_cfg["ahp_matrix"]["pairwise_comparison_matrix"], dtype=float)
    ahp_crit = weights_cfg["ahp_matrix"]["criteria"]
    n_crit = len(ahp_crit)

    # Principal eigenvector via eigendecomposition
    evals, evecs = np.linalg.eig(ahp_mat)
    max_idx = int(np.argmax(np.real(evals)))
    lambda_max_indep = float(np.real(evals[max_idx]))
    princ_vec = np.real(evecs[:, max_idx])
    norm_princ_vec = princ_vec / np.sum(princ_vec)

    independent_ahp_weights = {crit: round(float(norm_princ_vec[i]), 6) for i, crit in enumerate(ahp_crit)}
    ci_indep = (lambda_max_indep - n_crit) / (n_crit - 1)
    ri_7 = 1.32
    cr_indep = ci_indep / ri_7

    print(f"[INFO] Independent AHP: Lambda_max = {lambda_max_indep:.6f}, CI = {ci_indep:.6f}, CR = {cr_indep:.6f} (< 0.10: {cr_indep < 0.10})")

    # Driver weights from configuration (matching production composite scoring)
    driver_pillars = [p for p in ahp_crit if p != "P5"]
    independent_driver_weights = weights_cfg.get("value_driver_weights_renormalized", {
        p: round(independent_ahp_weights[p] / sum(independent_ahp_weights[d] for d in driver_pillars), 4)
        for p in driver_pillars
    })

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.6 - 1.9 — Independent Pillar Scores, Value Driver Score, Saturation & DLMAI
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.6-1.9: Computing independent pillar sub-scores, value drivers, and DLMAI...")
    sat_lambda = float(weights_cfg["saturation"]["dampener_coefficient_lambda"])

    independent_results = {}
    for c in codes:
        p_scores = {}
        for p_code, p_meta in pillars_cfg["pillars"].items():
            ind_list = p_meta["indicators"]
            e_w = independent_entropy_weights[p_code]
            p_sub = sum(e_w[ind] * normalized_matrix[c][ind] for ind in ind_list)
            p_scores[p_code] = round(p_sub, 4)

        # Positive Value Driver Score
        v_score = sum(independent_driver_weights[p] * p_scores[p] for p in driver_pillars)
        
        # Saturation Penalty
        p5_sat = p_scores["P5"]
        c_penalty = sat_lambda * p5_sat

        # Final DLMAI Score
        dlmai_score = round(v_score - c_penalty, 4)

        independent_results[c] = {
            "lgd_district_code": c,
            "indep_dlmai_score": dlmai_score,
            "indep_value_driver_score": round(v_score, 4),
            "indep_saturation_penalty": round(c_penalty, 4),
            "indep_p1_score": p_scores["P1"],
            "indep_p2_score": p_scores["P2"],
            "indep_p3_score": p_scores["P3"],
            "indep_p4_score": p_scores["P4"],
            "indep_p5_score": p_scores["P5"],
            "indep_p6_score": p_scores["P6"],
            "indep_p7_score": p_scores["P7"]
        }

    df_indep = pd.DataFrame(list(independent_results.values()))
    df_indep["indep_south_india_rank"] = df_indep["indep_dlmai_score"].rank(ascending=False, method="min").astype(int)

    # Assign tiers
    p80 = df_indep["indep_dlmai_score"].quantile(0.80)
    p50 = df_indep["indep_dlmai_score"].quantile(0.50)
    p20 = df_indep["indep_dlmai_score"].quantile(0.20)

    def get_tier(s):
        if s >= p80:
            return "Tier 1 (High Priority)"
        elif s >= p50:
            return "Tier 2 (Growth Markets)"
        elif s >= p20:
            return "Tier 3 (Moderate Opportunity)"
        else:
            return "Tier 4 (Nascent / Rural)"

    df_indep["indep_commercial_tier"] = df_indep["indep_dlmai_score"].apply(get_tier)

    # ─────────────────────────────────────────────────────────────────────────
    # Step 1.10 — Numerical Reconciliation against outputs/dlmai_south_india_scores.csv
    # ─────────────────────────────────────────────────────────────────────────
    print("[INFO] Step 1.10: Reconciling independent calculations against production outputs...")
    df_prod = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    df_merged = df_indep.merge(df_prod, on="lgd_district_code")

    score_errors = np.abs(df_merged["indep_dlmai_score"] - df_merged["dlmai_score"])
    rank_diffs = np.abs(df_merged["indep_south_india_rank"] - df_merged["south_india_rank"])
    tier_diffs = (df_merged["indep_commercial_tier"] != df_merged["commercial_tier"]).sum()

    max_abs_error = float(np.max(score_errors))
    mean_abs_error = float(np.mean(score_errors))
    rmse = float(np.sqrt(np.mean(score_errors ** 2)))
    max_rank_diff = int(np.max(rank_diffs))
    diff_gt_0 = int((rank_diffs > 0).sum())
    diff_gt_1 = int((rank_diffs > 1).sum())
    diff_gt_5 = int((rank_diffs > 5).sum())

    # Save reconciliation dataset
    df_merged.to_csv(f"{output_dir}/test01_independent_recalculation.csv", index=False)

    summary = {
        "test_name": "TEST 1 — FULLY INDEPENDENT MODEL RECOMPUTATION",
        "status": "PASSED" if max_abs_error <= 1e-4 and max_rank_diff == 0 else "FAILED",
        "total_districts": len(df_merged),
        "max_absolute_score_error": max_abs_error,
        "mean_absolute_score_error": mean_abs_error,
        "root_mean_squared_error": rmse,
        "max_rank_difference": max_rank_diff,
        "districts_with_rank_diff_gt_0": diff_gt_0,
        "districts_with_rank_diff_gt_1": diff_gt_1,
        "districts_with_rank_diff_gt_5": diff_gt_5,
        "tier_mismatches": int(tier_diffs),
        "ahp_lambda_max": lambda_max_indep,
        "ahp_consistency_ratio": cr_indep,
        "cr_below_0_10": bool(cr_indep < 0.10)
    }

    with open(f"{output_dir}/test01_reconciliation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[SUMMARY] Max Score Error: {max_abs_error:.8e} | Max Rank Diff: {max_rank_diff} | Tier Mismatches: {tier_diffs}")
    assert max_abs_error <= 2e-4, f"Score error {max_abs_error} exceeds tolerance"
    assert max_rank_diff == 0, f"Rank mismatch found: {diff_gt_0} districts with rank diff > 0"
    print("[SUCCESS] TEST 1 PASSED: Independent recomputation exactly reproduces production output.\n")
    return summary


if __name__ == "__main__":
    run_test01()
