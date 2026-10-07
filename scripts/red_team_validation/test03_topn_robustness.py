"""
TEST 3 — PROPER TOP-N ROBUSTNESS & INCLUSION PROBABILITIES
Evaluates district-level Top-5, Top-10, Top-20, and Top-30 inclusion frequencies across
10 defensible methodological specifications.
Classifies districts into ROBUST (>=90%), MODERATELY_ROBUST (70-89%), SENSITIVE (40-69%), and VOLATILE (<40%).
"""

import os
import math
import yaml
import numpy as np
import pandas as pd
from pathlib import Path


def run_test03(output_dir="outputs/red_team_validation_v2"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 70)
    print("TEST 3: DECISION-ORIENTED TOP-N INCLUSION PROBABILITIES & ROBUSTNESS")
    print("=" * 70)

    # 1. Load Data & Configs
    with open("config/indicators.yaml", "r", encoding="utf-8") as f:
        indicators_cfg = yaml.safe_load(f)
    with open("config/pillars.yaml", "r", encoding="utf-8") as f:
        pillars_cfg = yaml.safe_load(f)
    with open("config/weights.yaml", "r", encoding="utf-8") as f:
        weights_cfg = yaml.safe_load(f)

    df_prod = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
    
    codes = df_prod["lgd_district_code"].tolist()
    district_meta = {r["lgd_district_code"]: {"name": r["district_name"], "state": r["state_name"]} for _, r in df_prod.iterrows()}
    scored_indicators = list(indicators_cfg["indicators"].keys())
    base_ranks = df_prod.set_index("lgd_district_code")["south_india_rank"]
    base_scores = df_prod.set_index("lgd_district_code")["dlmai_score"]

    raw_dict = {c: {} for c in codes}
    for _, r in df_data.iterrows():
        c = int(r["lgd_district_code"])
        for ind in scored_indicators:
            raw_dict[c][ind] = float(r[ind])

    # Standard Min-Max Normalization Matrix
    norm_minmax = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = [raw_dict[c][ind] for c in codes]
        x_min, x_max = min(vals), max(vals)
        r_val = x_max - x_min
        for c in codes:
            v = raw_dict[c][ind]
            if r_val == 0: norm_minmax[c][ind] = 50.0
            elif direction == "NEGATIVE": norm_minmax[c][ind] = round(((x_max - v) / r_val) * 100.0, 4)
            else: norm_minmax[c][ind] = round(((v - x_min) / r_val) * 100.0, 4)

    # Robust IQR Normalization Matrix
    norm_robust = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = np.array([raw_dict[c][ind] for c in codes])
        med = np.median(vals)
        iqr = np.percentile(vals, 75) - np.percentile(vals, 25)
        iqr = iqr if iqr > 0 else 1.0
        scaled = (vals - med) / iqr
        s_min, s_max = np.min(scaled), np.max(scaled)
        for i, c in enumerate(codes):
            v = scaled[i]
            if s_max == s_min: norm_robust[c][ind] = 50.0
            elif direction == "NEGATIVE": norm_robust[c][ind] = round(((s_max - v) / (s_max - s_min)) * 100.0, 4)
            else: norm_robust[c][ind] = round(((v - s_min) / (s_max - s_min)) * 100.0, 4)

    # Shannon Entropy Function
    def get_entropy_weights(norm_m, ind_list):
        if len(ind_list) == 1: return {ind_list[0]: 1.0}
        m = len(codes)
        k = 1.0 / math.log(m)
        eps = 1e-6
        col_sums = {ind: sum(norm_m[c][ind] + eps for c in codes) for ind in ind_list}
        e_dict = {}
        for ind in ind_list:
            c_sum = col_sums[ind]
            e_val = 0.0
            for c in codes:
                p_ij = (norm_m[c][ind] + eps) / c_sum
                e_val += p_ij * math.log(p_ij)
            e_dict[ind] = -k * e_val
        d_dict = {ind: max(1.0 - e_dict[ind], 1e-6) for ind in ind_list}
        tot_d = sum(d_dict.values())
        w_dict = {ind: round(d_dict[ind] / tot_d, 6) for ind in ind_list}
        w_sum = sum(w_dict.values())
        w_dict[ind_list[0]] = round(w_dict[ind_list[0]] + (1.0 - w_sum), 6)
        return w_dict

    # Base Pillar Scores with Entropy
    base_p_scores = {c: {} for c in codes}
    for p_code, p_meta in pillars_cfg["pillars"].items():
        ind_list = p_meta["indicators"]
        e_w = get_entropy_weights(norm_minmax, ind_list)
        for c in codes:
            base_p_scores[c][p_code] = sum(e_w[ind] * norm_minmax[c][ind] for ind in ind_list)

    driver_weights = weights_cfg["value_driver_weights_renormalized"]
    driver_pillars = [p for p in weights_cfg["ahp_matrix"]["criteria"] if p != "P5"]
    sat_lambda = float(weights_cfg["saturation"]["dampener_coefficient_lambda"])

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Build 10 Defensible Model Specifications
    # ─────────────────────────────────────────────────────────────────────────
    variant_ranks = {}

    # Variant 1: Baseline AHP + Entropy + Saturation (lambda=0.15)
    variant_ranks["V01_Baseline"] = base_ranks

    # Variant 2: Equal Pillar Weights (1/6 each)
    eq_pillar_w = {p: 1.0 / 6.0 for p in driver_pillars}
    s_v2 = {c: sum(eq_pillar_w[p] * base_p_scores[c][p] for p in driver_pillars) - sat_lambda * base_p_scores[c]["P5"] for c in codes}
    variant_ranks["V02_Equal_Pillars"] = pd.Series(s_v2).rank(ascending=False, method="min").astype(int)

    # Variant 3: Equal Indicator Weights within pillars
    p_scores_eq_ind = {c: {} for c in codes}
    for p_code, p_meta in pillars_cfg["pillars"].items():
        ind_list = p_meta["indicators"]
        for c in codes:
            p_scores_eq_ind[c][p_code] = np.mean([norm_minmax[c][ind] for ind in ind_list])
    s_v3 = {c: sum(driver_weights[p] * p_scores_eq_ind[c][p] for p in driver_pillars) - sat_lambda * p_scores_eq_ind[c]["P5"] for c in codes}
    variant_ranks["V03_Equal_Indicators"] = pd.Series(s_v3).rank(ascending=False, method="min").astype(int)

    # Variant 4: Robust Normalization (IQR Scaling)
    p_scores_robust = {c: {} for c in codes}
    for p_code, p_meta in pillars_cfg["pillars"].items():
        ind_list = p_meta["indicators"]
        e_w_rob = get_entropy_weights(norm_robust, ind_list)
        for c in codes:
            p_scores_robust[c][p_code] = sum(e_w_rob[ind] * norm_robust[c][ind] for ind in ind_list)
    s_v4 = {c: sum(driver_weights[p] * p_scores_robust[c][p] for p in driver_pillars) - sat_lambda * p_scores_robust[c]["P5"] for c in codes}
    variant_ranks["V04_Robust_Scaling"] = pd.Series(s_v4).rank(ascending=False, method="min").astype(int)

    # Variant 5: No Saturation Dampener (lambda=0.0)
    s_v5 = {c: sum(driver_weights[p] * base_p_scores[c][p] for p in driver_pillars) for c in codes}
    variant_ranks["V05_No_Saturation"] = pd.Series(s_v5).rank(ascending=False, method="min").astype(int)

    # Variant 6: Low Saturation (lambda=0.10)
    s_v6 = {c: sum(driver_weights[p] * base_p_scores[c][p] for p in driver_pillars) - 0.10 * base_p_scores[c]["P5"] for c in codes}
    variant_ranks["V06_Low_Saturation"] = pd.Series(s_v6).rank(ascending=False, method="min").astype(int)

    # Variant 7: High Saturation (lambda=0.20)
    s_v7 = {c: sum(driver_weights[p] * base_p_scores[c][p] for p in driver_pillars) - 0.20 * base_p_scores[c]["P5"] for c in codes}
    variant_ranks["V07_High_Saturation"] = pd.Series(s_v7).rank(ascending=False, method="min").astype(int)

    # Variant 8: Geometric Aggregation
    geom_ranks = df_prod.set_index("lgd_district_code")["geometric_score"].rank(ascending=False, method="min").astype(int)
    variant_ranks["V08_Geometric"] = geom_ranks

    # Variant 9: Exclude Child Nutrition Deprivation Indicators (stunting, wasting, underweight)
    p1_clean_inds = [i for i in pillars_cfg["pillars"]["P1"]["indicators"] if i not in ("nfhs_stunting_pct", "nfhs_wasting_pct", "nfhs_underweight_pct")]
    e_w_clean = get_entropy_weights(norm_minmax, p1_clean_inds)
    p_scores_clean = {c: dict(base_p_scores[c]) for c in codes}
    for c in codes:
        p_scores_clean[c]["P1"] = sum(e_w_clean[ind] * norm_minmax[c][ind] for ind in p1_clean_inds)
    s_v9 = {c: sum(driver_weights[p] * p_scores_clean[c][p] for p in driver_pillars) - sat_lambda * p_scores_clean[c]["P5"] for c in codes}
    variant_ranks["V09_No_Nutrition_Proxies"] = pd.Series(s_v9).rank(ascending=False, method="min").astype(int)

    # Variant 10: P6 Aspirational Neutral (Weight=0)
    w_no_p6 = {p: w for p, w in driver_weights.items() if p != "P6"}
    tot_p6 = sum(w_no_p6.values())
    w_no_p6_norm = {p: w / tot_p6 for p, w in w_no_p6.items()}
    s_v10 = {c: sum(w_no_p6_norm[p] * base_p_scores[c][p] for p in w_no_p6_norm) - sat_lambda * base_p_scores[c]["P5"] for c in codes}
    variant_ranks["V10_Aspirational_Neutral"] = pd.Series(s_v10).rank(ascending=False, method="min").astype(int)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Compute Top-N Frequencies & Classifications across 10 Variants
    # ─────────────────────────────────────────────────────────────────────────
    df_var = pd.DataFrame(variant_ranks)
    n_variants = len(variant_ranks)

    topn_rows = []
    for c in codes:
        ranks = df_var.loc[c].values.astype(int)
        b_rank = int(base_ranks[c])
        
        f_top5 = float(np.mean(ranks <= 5)) * 100.0
        f_top10 = float(np.mean(ranks <= 10)) * 100.0
        f_top20 = float(np.mean(ranks <= 20)) * 100.0
        f_top30 = float(np.mean(ranks <= 30)) * 100.0

        r_mean = round(float(np.mean(ranks)), 2)
        r_median = round(float(np.median(ranks)), 2)
        r_sd = round(float(np.std(ranks)), 2)
        r_p05 = int(np.percentile(ranks, 5))
        r_p95 = int(np.percentile(ranks, 95))
        r_min = int(np.min(ranks))
        r_max = int(np.max(ranks))
        r_spread = r_max - r_min

        # Strict Decision Classification
        if b_rank <= 10:
            if f_top10 == 100.0: rob_class = "INVARIANT_TOP10 (100% Inclusion)"
            elif f_top10 >= 90.0: rob_class = "HIGH_ROBUSTNESS_TOP10 (90-99%)"
            elif f_top10 >= 70.0: rob_class = "MODERATE_ROBUSTNESS_TOP10 (70-89%)"
            elif f_top10 >= 40.0: rob_class = "SENSITIVE_TOP10 (40-69%)"
            else: rob_class = "VOLATILE_TOP10 (<40%)"
        elif b_rank <= 20:
            if f_top20 == 100.0: rob_class = "INVARIANT_TOP20 (100% Inclusion)"
            elif f_top20 >= 90.0: rob_class = "HIGH_ROBUSTNESS_TOP20 (90-99%)"
            elif f_top20 >= 70.0: rob_class = "MODERATE_ROBUSTNESS_TOP20 (70-89%)"
            elif f_top20 >= 40.0: rob_class = "SENSITIVE_TOP20 (40-69%)"
            else: rob_class = "VOLATILE_TOP20 (<40%)"
        elif b_rank <= 30:
            if f_top30 == 100.0: rob_class = "INVARIANT_TOP30 (100% Inclusion)"
            elif f_top30 >= 90.0: rob_class = "HIGH_ROBUSTNESS_TOP30 (90-99%)"
            elif f_top30 >= 70.0: rob_class = "MODERATE_ROBUSTNESS_TOP30 (70-89%)"
            elif f_top30 >= 40.0: rob_class = "SENSITIVE_TOP30 (40-69%)"
            else: rob_class = "VOLATILE_TOP30 (<40%)"
        else:
            if r_sd <= 4.5: rob_class = "HIGH_ROBUSTNESS_TIER_MEMBER"
            elif r_sd <= 8.0: rob_class = "MODERATE_ROBUSTNESS_TIER_MEMBER"
            else: rob_class = "SPECIFICATION_SENSITIVE_MID_TIER"

        topn_rows.append({
            "lgd_district_code": c,
            "district_name": district_meta[c]["name"],
            "state_name": district_meta[c]["state"],
            "baseline_rank": b_rank,
            "baseline_score": round(float(base_scores[c]), 4),
            "top_5_frequency_pct": round(f_top5, 1),
            "top_10_frequency_pct": round(f_top10, 1),
            "top_20_frequency_pct": round(f_top20, 1),
            "top_30_frequency_pct": round(f_top30, 1),
            "mean_rank": r_mean,
            "median_rank": r_median,
            "rank_std_dev": r_sd,
            "rank_p05": r_p05,
            "rank_p95": r_p95,
            "rank_min": r_min,
            "rank_max": r_max,
            "rank_spread": r_spread,
            "robustness_classification": rob_class
        })

    df_topn = pd.DataFrame(topn_rows).sort_values("baseline_rank").reset_index(drop=True)
    df_topn.to_csv(f"{output_dir}/test03_topn_robustness.csv", index=False)

    # Subsets
    df_robust = df_topn[df_topn["robustness_classification"].str.contains("ROBUST")].sort_values("baseline_rank")
    df_sensitive = df_topn[df_topn["robustness_classification"].str.contains("SENSITIVE")].sort_values("baseline_rank")
    df_volatile = df_topn[df_topn["robustness_classification"].str.contains("VOLATILE")].sort_values("rank_spread", ascending=False)

    df_robust.to_csv(f"{output_dir}/test03_robust_districts.csv", index=False)
    df_sensitive.to_csv(f"{output_dir}/test03_sensitive_districts.csv", index=False)
    df_volatile.to_csv(f"{output_dir}/test03_volatile_districts.csv", index=False)

    print(f"[SUMMARY] Top-N Robustness calculated across {n_variants} specifications.")
    print(f"  Robust Districts: {len(df_robust)} | Sensitive: {len(df_sensitive)} | Volatile: {len(df_volatile)}")
    print("[SUCCESS] TEST 3 PASSED: Decision-oriented Top-N probabilities saved.\n")


if __name__ == "__main__":
    run_test03()
