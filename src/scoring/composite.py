"""
Composite DLMAI Scoring & Tiering Module for South India.
Combines positive value drivers with market saturation penalty dampener.
Calculates regional and state ranks and assigns quantile-based commercial tiers.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd


def compute_composite_scores(
    pillar_scores: Dict[int, Dict[str, float]],
    driver_weights: Dict[str, float],
    saturation_lambda: float = 0.15
) -> Dict[int, Dict[str, Any]]:
    """
    pillar_scores: {lgd_code: {P1: score, P2: score, ..., P5: saturation_score, ...}}
    driver_weights: {P1: 0.3664, P3: 0.2468, P2: 0.1618, P4: 0.1039, P6: 0.0606, P7: 0.0606} (sum = 1.0)
    saturation_lambda: dampener coefficient (0.15)

    Returns: {lgd_code: {
        'dlmai_score': float,
        'value_driver_score': float,
        'saturation_penalty': float,
        'geometric_score': float,
        'pillar_scores': dict
    }}
    """
    results = {}
    driver_pillars = list(driver_weights.keys())

    for code, p_vals in pillar_scores.items():
        # 1. Positive Value Drivers Score V_i
        v_score = sum(driver_weights[p] * p_vals.get(p, 50.0) for p in driver_pillars)

        # 2. Saturation Penalty C_i
        p5_sat = p_vals.get("P5", 0.0)
        c_penalty = saturation_lambda * p5_sat

        # 3. Final Linear DLMAI Score
        dlmai = round(v_score - c_penalty, 4)

        # 4. Geometric Benchmark Score
        geom_val = 1.0
        for p in driver_pillars:
            geom_val *= (p_vals.get(p, 50.0) + 1.0) ** driver_weights[p]
        comp_discount = max(1.0 - (saturation_lambda * (p5_sat / 100.0)), 0.0)
        geom_score = round(geom_val * comp_discount, 4)

        results[code] = {
            "dlmai_score": dlmai,
            "value_driver_score": round(v_score, 4),
            "saturation_penalty": round(c_penalty, 4),
            "geometric_score": geom_score,
            "pillar_scores": dict(p_vals)
        }

    return results


def assign_ranks_and_tiers(results: Dict[int, Dict[str, Any]],
                           district_metadata: Dict[int, Dict[str, str]]) -> pd.DataFrame:
    """
    Constructs a tidy DataFrame with South India Rank, State Rank, and Quantile Tiers.
    """
    rows = []
    for code, res in results.items():
        meta = district_metadata.get(code, {})
        row = {
            "lgd_district_code": code,
            "district_name": meta.get("district_name", str(code)),
            "state_name": meta.get("state_name", "Unknown"),
            "dlmai_score": res["dlmai_score"],
            "value_driver_score": res["value_driver_score"],
            "saturation_penalty": res["saturation_penalty"],
            "geometric_score": res["geometric_score"],
        }
        for p, s in res["pillar_scores"].items():
            row[f"pillar_{p.lower()}_score"] = s
        rows.append(row)

    df = pd.DataFrame(rows)

    # South India Regional Rank
    df["south_india_rank"] = df["dlmai_score"].rank(ascending=False, method="min").astype(int)

    # State Rank
    df["state_rank"] = df.groupby("state_name")["dlmai_score"].rank(ascending=False, method="min").astype(int)

    # Quantile-Based Tiering
    p80 = df["dlmai_score"].quantile(0.80)
    p50 = df["dlmai_score"].quantile(0.50)
    p20 = df["dlmai_score"].quantile(0.20)

    def get_tier(score):
        if score >= p80:
            return "Tier 1 (High Priority)"
        elif score >= p50:
            return "Tier 2 (Growth Markets)"
        elif score >= p20:
            return "Tier 3 (Moderate Opportunity)"
        else:
            return "Tier 4 (Nascent / Rural)"

    df["commercial_tier"] = df["dlmai_score"].apply(get_tier)
    df = df.sort_values("south_india_rank").reset_index(drop=True)
    return df
