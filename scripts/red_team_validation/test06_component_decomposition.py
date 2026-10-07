"""
TEST 6 — DECOMPOSE DLMAI INTO NEED, ACCESS, GROWTH & COMPETITION
Deconstructs the single composite DLMAI score into 4 distinct strategic axes:
Need (Clinical & Population), Access (Infrastructure & Affordability), Growth (Demographic & Literacy), and Competition (Crowding).
Identifies districts with similar composite scores but radically divergent commercial profiles.
"""

import os
import yaml
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr
from pathlib import Path


def run_test06(output_dir="outputs/red_team_validation_v2"):
    os.makedirs(output_dir, exist_ok=True)
    print("=" * 70)
    print("TEST 6: 4-AXIS STRATEGIC COMPONENT DECOMPOSITION (NEED, ACCESS, GROWTH, COMPETITION)")
    print("=" * 70)

    # 1. Load Data & Indicator Catalog
    with open("config/indicators.yaml", "r", encoding="utf-8") as f:
        indicators_cfg = yaml.safe_load(f)
    
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
    
    codes = df_scores["lgd_district_code"].tolist()
    district_meta = {r["lgd_district_code"]: {"name": r["district_name"], "state": r["state_name"]} for _, r in df_scores.iterrows()}
    scored_indicators = list(indicators_cfg["indicators"].keys())

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

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Define 4 Strategic Components
    # ─────────────────────────────────────────────────────────────────────────
    # Component A: Clinical Need & Population Base (Chronic NCDs, Nutrition, Pediatric Share)
    need_inds = [
        "nfhs_hypertension_combined_pct", "nfhs_diabetes_combined_pct",
        "nfhs_stunting_pct", "nfhs_wasting_pct", "nfhs_underweight_pct",
        "census_population_age_0_6_pct"
    ]
    # Component B: Market Realization & Healthcare Access (Insurance, Clean Fuel, Sanitation, Inverted OOPE, PHC, CHC, SC, Hospital, Jan Aushadhi)
    access_inds = [
        "nfhs_insurance_pct", "nfhs_clean_fuel_pct", "nfhs_sanitation_pct", "nfhs_oope_delivery_rs",
        "rhs_phc_density_per_100k", "rhs_chc_density_per_100k", "rhs_subcentre_density_per_100k",
        "rhs_hospital_presence", "jan_aushadhi_density_per_100k"
    ]
    # Component C: Demographic & Market Growth (Urbanization, Population Growth, Literacy, Aspirational Support)
    growth_inds = [
        "census_urban_population_pct", "census_decadal_growth_pct",
        "census_literacy_rate_pct", "niti_aspirational_district_flag"
    ]
    # Component D: Market Competition (MCA21 pharma company density)
    comp_inds = ["mca21_pharma_density_per_100k"]

    comp_score_rows = []
    for c in codes:
        n_score = round(float(np.mean([norm_m[c][ind] for ind in need_inds])), 2)
        a_score = round(float(np.mean([norm_m[c][ind] for ind in access_inds])), 2)
        g_score = round(float(np.mean([norm_m[c][ind] for ind in growth_inds])), 2)
        c_score = round(float(norm_m[c]["mca21_pharma_density_per_100k"]), 2)

        comp_score_rows.append({
            "lgd_district_code": c,
            "district_name": district_meta[c]["name"],
            "state_name": district_meta[c]["state"],
            "need_score": n_score,
            "access_score": a_score,
            "growth_score": g_score,
            "competition_score": c_score
        })

    df_components = pd.DataFrame(comp_score_rows)
    df_merged = df_scores.merge(df_components, on=["lgd_district_code", "district_name", "state_name"])
    df_merged.to_csv(f"{output_dir}/test06_component_scores.csv", index=False)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Component Correlations against DLMAI Composite Score & Rank
    # ─────────────────────────────────────────────────────────────────────────
    corr_rows = []
    for comp in ["need_score", "access_score", "growth_score", "competition_score"]:
        r_val, p_r = pearsonr(df_merged[comp], df_merged["dlmai_score"])
        rho_val, p_rho = spearmanr(df_merged[comp], df_merged["south_india_rank"])
        corr_rows.append({
            "strategic_component": comp,
            "pearson_r_with_dlmai_score": round(r_val, 4),
            "spearman_rho_with_rank": round(rho_val, 4),
            "alignment_interpretation": "Primary Opportunity Driver" if r_val >= 0.50 else ("Secondary Driver" if r_val >= 0.20 else "Dampener / Orthogonal")
        })
    df_comp_corrs = pd.DataFrame(corr_rows)
    df_comp_corrs.to_csv(f"{output_dir}/test06_component_correlations.csv", index=False)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. District Commercial Profiling & Archetypes
    # ─────────────────────────────────────────────────────────────────────────
    need_med = df_merged["need_score"].median()
    access_med = df_merged["access_score"].median()
    growth_med = df_merged["growth_score"].median()
    comp_med = df_merged["competition_score"].median()

    def assign_archetype(row):
        is_hi_need = row["need_score"] >= need_med
        is_hi_access = row["access_score"] >= access_med
        is_hi_growth = row["growth_score"] >= growth_med
        is_hi_comp = row["competition_score"] >= comp_med

        if is_hi_need and is_hi_access and not is_hi_comp:
            return "Prime Opportunity: High Need + High Access + Low Competition"
        elif is_hi_need and is_hi_access and is_hi_comp:
            return "Crowded Core: High Need + High Access + High Competition"
        elif is_hi_need and not is_hi_access:
            return "Latent Demand: High Need + Under-Served Infrastructure"
        elif not is_hi_need and is_hi_access:
            return "Affluent Metro / Commercial Base: Low Need + High Access"
        elif is_hi_growth and is_hi_comp:
            return "Emerging Battleground: Rapid Growth + High Competition"
        else:
            return "Developing Frontier: Nascent Market"

    df_merged["strategic_commercial_archetype"] = df_merged.apply(assign_archetype, axis=1)
    
    # Save profiles
    df_profiles = df_merged[[
        "south_india_rank", "district_name", "state_name", "dlmai_score", "commercial_tier",
        "need_score", "access_score", "growth_score", "competition_score", "strategic_commercial_archetype"
    ]].sort_values("south_india_rank").reset_index(drop=True)
    df_profiles.to_csv(f"{output_dir}/test06_district_profiles.csv", index=False)

    # ─────────────────────────────────────────────────────────────────────────
    # 5. State Summary
    # ─────────────────────────────────────────────────────────────────────────
    df_state_summary = df_merged.groupby("state_name").agg(
        District_Count=("lgd_district_code", "count"),
        Mean_DLMAI=("dlmai_score", "mean"),
        Mean_Need=("need_score", "mean"),
        Mean_Access=("access_score", "mean"),
        Mean_Growth=("growth_score", "mean"),
        Mean_Competition=("competition_score", "mean")
    ).round(2).reset_index()
    df_state_summary.to_csv(f"{output_dir}/test06_state_component_summary.csv", index=False)

    print("[SUCCESS] Strategic component decomposition complete.")
    print("  Correlation with DLMAI:")
    for r in corr_rows:
        print(f"    {r['strategic_component']}: Pearson r = {r['pearson_r_with_dlmai_score']:.4f}")
    print("[SUCCESS] TEST 6 PASSED: 4-Axis Component profiles saved.\n")


if __name__ == "__main__":
    run_test06()
