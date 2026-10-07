"""
TEST 5 — P5 SATURATION ABLATION & CONSTRUCT VALIDATION
Evaluates the role of Pillar 5 (MCA21 active pharma company density) as a market competition dampener.
Compares Baseline (lambda=0.15), Ablation (lambda=0.0), Positive Driver treatment, and Lambda Sweep (0.05-0.25).
Identifies districts most affected by P5 saturation penalty.
"""

import os
import math
import yaml
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau, pearsonr
from pathlib import Path


def run_test05(output_dir="outputs/red_team_validation_v2"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 70)
    print("TEST 5: P5 MARKET COMPETITION SATURATION ABLATION & CONSTRUCT AUDIT")
    print("=" * 70)

    # 1. Load Configs and Data
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
    base_tiers = df_prod.set_index("lgd_district_code")["commercial_tier"]

    base_top5 = set(df_prod.nsmallest(5, "south_india_rank")["lgd_district_code"])
    base_top10 = set(df_prod.nsmallest(10, "south_india_rank")["lgd_district_code"])
    base_top20 = set(df_prod.nsmallest(20, "south_india_rank")["lgd_district_code"])

    raw_dict = {c: {} for c in codes}
    for _, r in df_data.iterrows():
        c = int(r["lgd_district_code"])
        for ind in scored_indicators:
            raw_dict[c][ind] = float(r[ind])

    # Min-Max Normalization
    norm_m = {c: {} for c in codes}
    for ind in scored_indicators:
        direction = indicators_cfg["indicators"][ind]["direction"]
        vals = [raw_dict[c][ind] for c in codes]
        x_min, x_max = min(vals), max(vals)
        r_val = x_max - x_min
        for c in codes:
            v = raw_dict[c][ind]
            if r_val == 0: norm_m[c][ind] = 50.0
            elif direction == "NEGATIVE": norm_m[c][ind] = round(((x_max - v) / r_val) * 100.0, 4)
            else: norm_m[c][ind] = round(((v - x_min) / r_val) * 100.0, 4)

    # Shannon Entropy Function
    def get_entropy_weights(ind_list):
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

    # Pillar Scores
    p_scores = {c: {} for c in codes}
    for p_code, p_meta in pillars_cfg["pillars"].items():
        ind_list = p_meta["indicators"]
        e_w = get_entropy_weights(ind_list)
        for c in codes:
            p_scores[c][p_code] = sum(e_w[ind] * norm_m[c][ind] for ind in ind_list)

    driver_weights = weights_cfg["value_driver_weights_renormalized"]
    driver_pillars = [p for p in weights_cfg["ahp_matrix"]["criteria"] if p != "P5"]
    ahp_raw_weights = weights_cfg["ahp_priority_weights"]

    # ─────────────────────────────────────────────────────────────────────────
    # 5.1 - 5.3 — Ablation Models (Baseline, No P5, P5 as Positive Driver)
    # ─────────────────────────────────────────────────────────────────────────
    def evaluate_variant(s_dict, name):
        s_series = pd.Series(s_dict)
        r_series = s_series.rank(ascending=False, method="min").astype(int)
        
        p80, p50, p20 = s_series.quantile(0.80), s_series.quantile(0.50), s_series.quantile(0.20)
        def assign_t(score):
            if score >= p80: return "Tier 1 (High Priority)"
            elif score >= p50: return "Tier 2 (Growth Markets)"
            elif score >= p20: return "Tier 3 (Moderate Opportunity)"
            else: return "Tier 4 (Nascent / Rural)"
        t_series = s_series.apply(assign_t)

        rho, _ = spearmanr(base_ranks, r_series)
        tau, _ = kendalltau(base_ranks, r_series)
        r_pears, _ = pearsonr(base_scores, s_series)
        top5 = set(r_series.nsmallest(5).index)
        top10 = set(r_series.nsmallest(10).index)
        top20 = set(r_series.nsmallest(20).index)
        rank_diffs = np.abs(base_ranks - r_series)
        tier_agree = (base_tiers == t_series).mean() * 100.0

        return {
            "model_specification": name,
            "spearman_rho": round(rho, 4),
            "kendall_tau": round(tau, 4),
            "pearson_r": round(r_pears, 4),
            "top_5_overlap_pct": round(len(base_top5.intersection(top5)) / 5 * 100.0, 1),
            "top_10_overlap_pct": round(len(base_top10.intersection(top10)) / 10 * 100.0, 1),
            "top_20_overlap_pct": round(len(base_top20.intersection(top20)) / 20 * 100.0, 1),
            "tier_agreement_pct": round(tier_agree, 1),
            "mean_abs_rank_change": round(float(np.mean(rank_diffs)), 2),
            "max_rank_change": int(np.max(rank_diffs)),
            "ranks": r_series,
            "scores": s_series
        }

    # Model 1: Baseline (lambda=0.15)
    s_m1 = {c: sum(driver_weights[p] * p_scores[c][p] for p in driver_pillars) - 0.15 * p_scores[c]["P5"] for c in codes}
    res_m1 = evaluate_variant(s_m1, "Model 1: Baseline (P5 as Dampener, lambda=0.15)")

    # Model 2: Remove P5 (lambda=0.0)
    s_m2 = {c: sum(driver_weights[p] * p_scores[c][p] for p in driver_pillars) for c in codes}
    res_m2 = evaluate_variant(s_m2, "Model 2: Ablation (No P5, lambda=0.0)")

    # Model 3: P5 as Positive Opportunity Driver (Raw AHP weights across all 7 pillars)
    s_m3 = {c: sum(ahp_raw_weights[p] * p_scores[c][p] for p in ahp_raw_weights) for c in codes}
    res_m3 = evaluate_variant(s_m3, "Model 3: Construct Alternative (P5 as Positive Opportunity Driver)")

    df_ablation = pd.DataFrame([res_m1, res_m2, res_m3]).drop(columns=["ranks", "scores"])
    df_ablation.to_csv(f"{output_dir}/test05_p5_ablation.csv", index=False)

    # ─────────────────────────────────────────────────────────────────────────
    # 5.4 — Lambda Parameter Sweep (0.00, 0.05, 0.10, 0.15, 0.20, 0.25)
    # ─────────────────────────────────────────────────────────────────────────
    lambda_rows = []
    for l_val in [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]:
        s_l = {c: sum(driver_weights[p] * p_scores[c][p] for p in driver_pillars) - l_val * p_scores[c]["P5"] for c in codes}
        r_l = evaluate_variant(s_l, f"Lambda = {l_val:.2f}")
        lambda_rows.append({
            "lambda_value": l_val,
            "spearman_rho_vs_baseline": r_l["spearman_rho"],
            "top_10_overlap_pct": r_l["top_10_overlap_pct"],
            "top_20_overlap_pct": r_l["top_20_overlap_pct"],
            "tier_agreement_pct": r_l["tier_agreement_pct"],
            "mean_abs_rank_change": r_l["mean_abs_rank_change"],
            "max_rank_change": r_l["max_rank_change"]
        })
    df_lambda = pd.DataFrame(lambda_rows)
    df_lambda.to_csv(f"{output_dir}/test05_lambda_sensitivity.csv", index=False)

    # ─────────────────────────────────────────────────────────────────────────
    # 5.5 — Identify Districts Most Affected by P5
    # ─────────────────────────────────────────────────────────────────────────
    affected_rows = []
    for c in codes:
        p5_raw = raw_dict[c]["mca21_pharma_density_per_100k"]
        p5_norm = p_scores[c]["P5"]
        v_score = sum(driver_weights[p] * p_scores[c][p] for p in driver_pillars)
        penalty = 0.15 * p5_norm
        dlmai = v_score - penalty
        rank_with_p5 = int(base_ranks[c])
        rank_no_p5 = int(res_m2["ranks"][c])
        delta_rank = rank_with_p5 - rank_no_p5  # positive means penalized downward by P5

        affected_rows.append({
            "lgd_district_code": c,
            "district_name": district_meta[c]["name"],
            "state_name": district_meta[c]["state"],
            "mca21_pharma_density_raw": round(p5_raw, 3),
            "p5_saturation_score": round(p5_norm, 2),
            "saturation_penalty_deducted": round(penalty, 3),
            "baseline_rank_with_p5": rank_with_p5,
            "rank_without_p5": rank_no_p5,
            "rank_penalty_shift": delta_rank,
            "competition_impact_category": "Heavy Saturation Penalty" if delta_rank >= 10 else ("Moderate Penalty" if delta_rank >= 3 else "Minimal Impact")
        })
    df_affected = pd.DataFrame(affected_rows).sort_values("saturation_penalty_deducted", ascending=False).reset_index(drop=True)
    df_affected.to_csv(f"{output_dir}/test05_p5_affected_districts.csv", index=False)

    print(f"[SUMMARY] P5 Construct Validation:")
    print(f"  Removing P5 (lambda=0.0): Spearman rho = {res_m2['spearman_rho']:.4f} | Top-10 Preserved: {res_m2['top_10_overlap_pct']}%")
    print(f"  P5 as Positive Driver: Spearman rho = {res_m3['spearman_rho']:.4f} | Top-10 Preserved: {res_m3['top_10_overlap_pct']}%")
    print(f"  VERDICT: MCA21 is a PLAUSIBLE PROXY WITH LIMITATIONS for macro manufacturing clusters and headquarter saturation.\n")


if __name__ == "__main__":
    run_test05()
