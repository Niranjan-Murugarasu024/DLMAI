"""
Monte Carlo Stochastic Sensitivity & Rank Stability Engine.
Applies log-normal weight perturbations across 1,000 iterations and evaluates Spearman rank correlations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


@dataclass
class SensitivitySummary:
    iterations: int
    mean_spearman_rho: float
    median_spearman_rho: float
    p05_spearman_rho: float
    p95_spearman_rho: float
    stability_assessment: str
    district_stability_df: pd.DataFrame


def run_monte_carlo_sensitivity(
    pillar_scores: Dict[int, Dict[str, float]],
    baseline_weights: Dict[str, float],
    saturation_lambda: float = 0.15,
    iterations: int = 1000,
    random_seed: int = 42,
    noise_sigma: float = 0.20
) -> SensitivitySummary:
    """
    baseline_weights: {P1: 0.3664, P3: 0.2468, P2: 0.1618, P4: 0.1039, P6: 0.0606, P7: 0.0606} (sum = 1.0)
    """
    np.random.seed(random_seed)
    districts = list(pillar_scores.keys())
    driver_pillars = list(baseline_weights.keys())
    base_w_arr = np.array([baseline_weights[p] for p in driver_pillars])

    # 1. Baseline scores and ranks
    base_scores = {}
    for code in districts:
        p_vals = pillar_scores[code]
        v = sum(baseline_weights[p] * p_vals.get(p, 50.0) for p in driver_pillars)
        c = saturation_lambda * p_vals.get("P5", 0.0)
        base_scores[code] = v - c

    base_s_series = pd.Series(base_scores)
    base_ranks = base_s_series.rank(ascending=False, method="min")

    # 2. Monte Carlo Iterations
    sim_ranks = {code: [] for code in districts}
    sim_scores = {code: [] for code in districts}
    spearman_corrs = []

    for _ in range(iterations):
        # Multiplicative log-normal noise
        eps = np.random.normal(0, noise_sigma, size=len(driver_pillars))
        pert_w = base_w_arr * np.exp(eps)
        norm_w = pert_w / np.sum(pert_w)
        w_dict = {p: norm_w[i] for i, p in enumerate(driver_pillars)}

        iter_scores = {}
        for code in districts:
            p_vals = pillar_scores[code]
            v = sum(w_dict[p] * p_vals.get(p, 50.0) for p in driver_pillars)
            c = saturation_lambda * p_vals.get("P5", 0.0)
            iter_scores[code] = v - c

        iter_s_series = pd.Series(iter_scores)
        iter_rank_series = iter_s_series.rank(ascending=False, method="min")

        for code in districts:
            sim_ranks[code].append(iter_rank_series[code])
            sim_scores[code].append(iter_scores[code])

        rho, _ = spearmanr(base_ranks, iter_rank_series)
        spearman_corrs.append(rho)

    # 3. Calculate summary metrics per district
    dist_stats = []
    for code in districts:
        ranks = np.array(sim_ranks[code])
        scores = np.array(sim_scores[code])
        b_rank = base_ranks[code]

        dist_stats.append({
            "lgd_district_code": code,
            "baseline_rank": int(b_rank),
            "mean_sim_rank": round(float(np.mean(ranks)), 2),
            "median_sim_rank": round(float(np.median(ranks)), 2),
            "rank_std_dev": round(float(np.std(ranks)), 2),
            "rank_ci_lower_2_5": int(np.percentile(ranks, 2.5)),
            "rank_ci_upper_97_5": int(np.percentile(ranks, 97.5)),
            "top_10_frequency_pct": round(float(np.mean(ranks <= 10) * 100), 2),
            "top_20_frequency_pct": round(float(np.mean(ranks <= 20) * 100), 2),
        })

    df_dist_stats = pd.DataFrame(dist_stats).sort_values("baseline_rank").reset_index(drop=True)

    mean_rho = float(np.mean(spearman_corrs))
    med_rho = float(np.median(spearman_corrs))
    p05_rho = float(np.percentile(spearman_corrs, 5.0))
    p95_rho = float(np.percentile(spearman_corrs, 95.0))

    if mean_rho >= 0.95:
        assessment = "HIGHLY_STABLE (Target Met)"
    elif mean_rho >= 0.90:
        assessment = "STABLE"
    elif mean_rho >= 0.75:
        assessment = "MODERATELY_SENSITIVE"
    else:
        assessment = "HIGHLY_SENSITIVE"

    return SensitivitySummary(
        iterations=iterations,
        mean_spearman_rho=round(mean_rho, 4),
        median_spearman_rho=round(med_rho, 4),
        p05_spearman_rho=round(p05_rho, 4),
        p95_spearman_rho=round(p95_rho, 4),
        stability_assessment=assessment,
        district_stability_df=df_dist_stats
    )
