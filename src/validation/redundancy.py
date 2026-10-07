"""
Multicollinearity & Indicator Redundancy Analysis Module for South India DLMAI.
Computes pairwise Pearson and Spearman correlation matrices and flags collinear pairs.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd


def generate_indicator_redundancy_report(
    analytical_matrix_df: pd.DataFrame,
    indicator_columns: List[str],
    high_corr_threshold: float = 0.70
) -> pd.DataFrame:
    """
    Computes pairwise correlation between all indicator columns and produces a redundancy audit report.
    """
    numeric_df = analytical_matrix_df[indicator_columns].astype(float)
    corr_matrix = numeric_df.corr(method="spearman")

    rows = []
    seen_pairs = set()

    for ind_a in indicator_columns:
        for ind_b in indicator_columns:
            if ind_a == ind_b:
                continue
            pair = tuple(sorted([ind_a, ind_b]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            r_val = corr_matrix.loc[ind_a, ind_b]
            if np.isnan(r_val):
                continue

            abs_r = abs(r_val)
            if abs_r >= high_corr_threshold:
                conceptual_overlap = "HIGH (Potential collinear redundancy)"
                recommendation = "Review indicator pairing; ensure one is rate/density or distinct clinical domain"
            elif abs_r >= 0.40:
                conceptual_overlap = "MODERATE (Complementary domain signal)"
                recommendation = "Retain; entropy weighting handles variance weighting"
            else:
                conceptual_overlap = "LOW (Independent information)"
                recommendation = "Retain as orthogonal domain indicator"

            rows.append({
                "indicator_a": ind_a,
                "indicator_b": ind_b,
                "spearman_correlation": round(r_val, 4),
                "absolute_correlation": round(abs_r, 4),
                "conceptual_overlap": conceptual_overlap,
                "recommendation": recommendation
            })

    return pd.DataFrame(rows).sort_values("absolute_correlation", ascending=False).reset_index(drop=True)
