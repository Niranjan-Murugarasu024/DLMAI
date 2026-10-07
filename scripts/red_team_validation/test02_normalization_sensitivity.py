"""
TEST 2 — NORMALIZATION SENSITIVITY DECOMPOSITION
Decomposes the effects of normalization scaling from Shannon entropy weighting.
Evaluates Family A (Fixed Weights) vs Family B (Recomputed Entropy Weights)
across Min-Max, Robust IQR, Percentile Transformation, and Winsorized Min-Max (5-95%).
"""

import os
import math
import yaml
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau, pearsonr
from pathlib import Path


def run_test02(output_dir="outputs/red_team_validation_v2"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 70)
    print("TEST 2: NORMALIZATION SENSITIVITY & WEIGHTING EFFECT DECOMPOSITION")
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
    scored_indicators = list(indicators_cfg["indicators"].keys())
    base_ranks = df_prod.set_index("lgd_district_code")["south_india_rank"]
    base_scores = df_prod.set_index("lgd_district_code")["dlmai_score"]
    base_tiers = df_prod.set_index("lgd_district_code")["commercial_tier"]

    base_top5 = set(df_prod.nsmallest(5, "south_india_rank")["lgd_district_code"])
    base_top10 = set(df_prod.nsmallest(10, "south_india_rank")["lgd_district_code"])
    base_top20 = set(df_prod.nsmallest(20, "south_india_rank")["lgd_district_code"])
    base_top30 = set(df_prod.nsmallest(30, "south_india_rank")["lgd_district_code"])

    driver_weights = weights_cfg["value_driver_weights_renormalized"]
    sat_lambda = float(weights_cfg["saturation"]["dampener_coefficient_lambda"])
    driver_pillars = [p for p in weights_cfg["ahp_matrix"]["criteria"] if p != "P5"]

    raw_dict = {c: {} for c in codes}
    for _, r in df_data.iterrows():
        c = int(r["lgd_district_code"])
        for ind in scored_indicators:
            raw_dict[c][ind] = float(r[ind])

    # ─────────────────────────────────────────────────────────────────────────
    # Helper: Entropy Weight Calculator
    # ─────────────────────────────────────────────────────────────────────────
    def compute_entropy(norm_m, ind_list):
        if len(ind_list) == 1:
            return {ind_list[0]: 1.0}
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

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Build the 4 Normalization Matrices
    # ─────────────────────────────────────────────────────────────────────────
    norm_matrices = {}

    # Method 1: Min-Max (Baseline)
    n1 = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = [raw_dict[c][ind] for c in codes]
        x_min, x_max = min(vals), max(vals)
        r_val = x_max - x_min
        for c in codes:
            v = raw_dict[c][ind]
            if r_val == 0:
                n1[c][ind] = 50.0
            elif direction == "NEGATIVE":
                n1[c][ind] = round(((x_max - v) / r_val) * 100.0, 4)
            else:
                n1[c][ind] = round(((v - x_min) / r_val) * 100.0, 4)
    norm_matrices["1_MinMax_Baseline"] = n1

    # Baseline entropy weights
    baseline_entropy_weights = {}
    for p_code, p_meta in pillars_cfg["pillars"].items():
        baseline_entropy_weights[p_code] = compute_entropy(n1, p_meta["indicators"])

    # Method 2: Robust Scaling (Median / IQR mapped to 0-100)
    n2 = {c: {} for c in codes}
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
            if s_max == s_min:
                n2[c][ind] = 50.0
            elif direction == "NEGATIVE":
                n2[c][ind] = round(((s_max - v) / (s_max - s_min)) * 100.0, 4)
            else:
                n2[c][ind] = round(((v - s_min) / (s_max - s_min)) * 100.0, 4)
    norm_matrices["2_Robust_IQR"] = n2

    # Method 3: Percentile / Rank Transformation (0 to 100)
    n3 = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        s = pd.Series([raw_dict[c][ind] for c in codes], index=codes)
        pct = s.rank(pct=True, ascending=(direction != "NEGATIVE")) * 100.0
        for c in codes:
            n3[c][ind] = round(pct[c], 4)
    norm_matrices["3_Percentile_Rank"] = n3

    # Method 4: Winsorized Min-Max (5th to 95th percentiles)
    n4 = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = np.array([raw_dict[c][ind] for c in codes])
        p05, p95 = np.percentile(vals, 5), np.percentile(vals, 95)
        clipped = np.clip(vals, p05, p95)
        c_min, c_max = np.min(clipped), np.max(clipped)
        r_c = c_max - c_min
        for i, c in enumerate(codes):
            v = clipped[i]
            if r_c == 0:
                n4[c][ind] = 50.0
            elif direction == "NEGATIVE":
                n4[c][ind] = round(((c_max - v) / r_c) * 100.0, 4)
            else:
                n4[c][ind] = round(((v - c_min) / r_c) * 100.0, 4)
    norm_matrices["4_Winsorized_5_95"] = n4

    # ─────────────────────────────────────────────────────────────────────────
    # Helper: Evaluation Runner
    # ─────────────────────────────────────────────────────────────────────────
    def evaluate_model(norm_m, weights_by_pillar):
        # 1. Pillar scores
        p_scores = {c: {} for c in codes}
        for p_code, p_meta in pillars_cfg["pillars"].items():
            ind_list = p_meta["indicators"]
            w_dict = weights_by_pillar[p_code]
            for c in codes:
                p_scores[c][p_code] = sum(w_dict[ind] * norm_m[c][ind] for ind in ind_list)

        # 2. Composite
        dlmai_dict = {}
        for c in codes:
            v_score = sum(driver_weights[p] * p_scores[c][p] for p in driver_pillars)
            c_penalty = sat_lambda * p_scores[c]["P5"]
            dlmai_dict[c] = round(v_score - c_penalty, 4)

        s_series = pd.Series(dlmai_dict)
        r_series = s_series.rank(ascending=False, method="min").astype(int)

        p80, p50, p20 = s_series.quantile(0.80), s_series.quantile(0.50), s_series.quantile(0.20)
        def assign_t(score):
            if score >= p80: return "Tier 1 (High Priority)"
            elif score >= p50: return "Tier 2 (Growth Markets)"
            elif score >= p20: return "Tier 3 (Moderate Opportunity)"
            else: return "Tier 4 (Nascent / Rural)"
        t_series = s_series.apply(assign_t)

        # Metrics
        rho, _ = spearmanr(base_ranks, r_series)
        tau, _ = kendalltau(base_ranks, r_series)
        r_pears, _ = pearsonr(base_scores, s_series)

        top5 = set(r_series.nsmallest(5).index)
        top10 = set(r_series.nsmallest(10).index)
        top20 = set(r_series.nsmallest(20).index)
        top30 = set(r_series.nsmallest(30).index)

        rank_diffs = np.abs(base_ranks - r_series)
        tier_agree = (base_tiers == t_series).mean() * 100.0

        return {
            "spearman_rho": round(rho, 4),
            "kendall_tau": round(tau, 4),
            "pearson_r": round(r_pears, 4),
            "top_5_overlap_pct": round(len(base_top5.intersection(top5)) / 5 * 100.0, 1),
            "top_10_overlap_pct": round(len(base_top10.intersection(top10)) / 10 * 100.0, 1),
            "top_20_overlap_pct": round(len(base_top20.intersection(top20)) / 20 * 100.0, 1),
            "top_30_overlap_pct": round(len(base_top30.intersection(top30)) / 30 * 100.0, 1),
            "tier_agreement_pct": round(tier_agree, 1),
            "mean_abs_rank_change": round(float(np.mean(rank_diffs)), 2),
            "median_abs_rank_change": round(float(np.median(rank_diffs)), 2),
            "max_rank_change": int(np.max(rank_diffs)),
            "ranks": r_series,
            "tiers": t_series,
            "scores": s_series
        }

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Execute Family A (Fixed Weights) & Family B (Recomputed Weights)
    # ─────────────────────────────────────────────────────────────────────────
    family_a_rows = []
    family_b_rows = []
    decomposition_rows = []

    family_a_results = {}
    family_b_results = {}

    for name, m_dict in norm_matrices.items():
        # Family A: Fixed Baseline Weights
        res_a = evaluate_model(m_dict, baseline_entropy_weights)
        family_a_results[name] = res_a
        family_a_rows.append({
            "normalization_method": name,
            "experimental_condition": "Family A: Fixed Baseline Weights",
            "spearman_rho": res_a["spearman_rho"],
            "kendall_tau": res_a["kendall_tau"],
            "pearson_r": res_a["pearson_r"],
            "top_5_overlap_pct": res_a["top_5_overlap_pct"],
            "top_10_overlap_pct": res_a["top_10_overlap_pct"],
            "top_20_overlap_pct": res_a["top_20_overlap_pct"],
            "top_30_overlap_pct": res_a["top_30_overlap_pct"],
            "tier_agreement_pct": res_a["tier_agreement_pct"],
            "mean_abs_rank_change": res_a["mean_abs_rank_change"],
            "median_abs_rank_change": res_a["median_abs_rank_change"],
            "max_rank_change": res_a["max_rank_change"]
        })

        # Family B: Recomputed Entropy Weights
        weights_b = {}
        for p_code, p_meta in pillars_cfg["pillars"].items():
            weights_b[p_code] = compute_entropy(m_dict, p_meta["indicators"])
        res_b = evaluate_model(m_dict, weights_b)
        family_b_results[name] = res_b
        family_b_rows.append({
            "normalization_method": name,
            "experimental_condition": "Family B: Recomputed Entropy Weights",
            "spearman_rho": res_b["spearman_rho"],
            "kendall_tau": res_b["kendall_tau"],
            "pearson_r": res_b["pearson_r"],
            "top_5_overlap_pct": res_b["top_5_overlap_pct"],
            "top_10_overlap_pct": res_b["top_10_overlap_pct"],
            "top_20_overlap_pct": res_b["top_20_overlap_pct"],
            "top_30_overlap_pct": res_b["top_30_overlap_pct"],
            "tier_agreement_pct": res_b["tier_agreement_pct"],
            "mean_abs_rank_change": res_b["mean_abs_rank_change"],
            "median_abs_rank_change": res_b["median_abs_rank_change"],
            "max_rank_change": res_b["max_rank_change"]
        })

        # Decomposition: Comparison of Family A vs Family B
        diff_rho_ab, _ = spearmanr(res_a["ranks"], res_b["ranks"])
        decomposition_rows.append({
            "normalization_method": name,
            "fixed_weights_rho": res_a["spearman_rho"],
            "recomputed_weights_rho": res_b["spearman_rho"],
            "delta_rho_weighting_effect": round(res_b["spearman_rho"] - res_a["spearman_rho"], 4),
            "correlation_between_A_and_B": round(diff_rho_ab, 4),
            "fixed_top10_overlap": res_a["top_10_overlap_pct"],
            "recomputed_top10_overlap": res_b["top_10_overlap_pct"],
            "fixed_tier_agreement": res_a["tier_agreement_pct"],
            "recomputed_tier_agreement": res_b["tier_agreement_pct"]
        })

    # Save outputs
    df_fam_a = pd.DataFrame(family_a_rows)
    df_fam_b = pd.DataFrame(family_b_rows)
    df_decomp = pd.DataFrame(decomposition_rows)

    df_fam_a.to_csv(f"{output_dir}/test02_normalization_fixed_weights.csv", index=False)
    df_fam_b.to_csv(f"{output_dir}/test02_normalization_recomputed_weights.csv", index=False)
    df_decomp.to_csv(f"{output_dir}/test02_normalization_effect_decomposition.csv", index=False)

    print("[SUCCESS] Family A (Fixed Weights) and Family B (Recomputed Weights) evaluated.")
    for r in decomposition_rows:
        print(f"  {r['normalization_method']}: Fixed Rho={r['fixed_weights_rho']:.4f} | Recomputed Rho={r['recomputed_weights_rho']:.4f} | Delta Rho={r['delta_rho_weighting_effect']:.4f}")
    print("[SUCCESS] TEST 2 PASSED: Normalization sensitivity decomposed.\n")


if __name__ == "__main__":
    run_test02()
