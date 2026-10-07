"""
Comprehensive Unit, Integration, and Regression Test Suite for South India DLMAI.
Validates geographic configuration, AHP mathematics, entropy weighting, normalization,
saturation dampening, inheritance, imputation hierarchy, tiering, and Monte Carlo reproducibility.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_config
from src.harmonization.crosswalk import SouthDistrictCrosswalk, normalize_name
from src.harmonization.inheritance import SouthInheritanceResolver
from src.scoring.normalizer import min_max_normalize
from src.scoring.entropy import calculate_entropy_weights
from src.scoring.ahp import calculate_ahp_weights
from src.scoring.composite import compute_composite_scores, assign_ranks_and_tiers
from src.sensitivity.monte_carlo import run_monte_carlo_sensitivity
from src.imputation.engine import SouthImputationEngine


def test_geographic_scope_and_district_count():
    """Validates that exactly 148 canonical South Indian districts are loaded across 7 States/UTs."""
    cfg = get_config()
    target_states = [s["state_name"] for s in cfg.geography["target_states"]]
    assert len(target_states) == 7
    assert "Tamil Nadu" in target_states
    assert "Kerala" in target_states
    assert "Karnataka" in target_states
    assert "Andhra Pradesh" in target_states
    assert "Telangana" in target_states
    assert "Goa" in target_states
    assert "Puducherry" in target_states

    crosswalk = SouthDistrictCrosswalk()
    assert len(crosswalk.districts) == 148
    states_found = set(d.state_name for d in crosswalk.districts.values())
    assert states_found == set(target_states)


def test_indicator_count_and_pillar_reconciliation():
    """Validates that exactly 20 core scored indicators exist and are mapped to 7 pillars."""
    cfg = get_config()
    scored_indicators = [k for k, v in cfg.indicators["indicators"].items() if v.get("is_scored", True)]
    assert len(scored_indicators) == 20

    # Verify pillar bindings
    p_indicators = []
    for p_code, p_meta in cfg.pillars["pillars"].items():
        p_indicators.extend(p_meta["indicators"])

    assert sorted(scored_indicators) == sorted(p_indicators)
    assert len(cfg.pillars["pillars"]) == 7


def test_ahp_mathematics_and_consistency():
    """Validates AHP matrix reciprocity, eigenvalue decomposition, and CR < 0.10 threshold."""
    cfg = get_config()
    matrix = np.array(cfg.weights["ahp_matrix"]["pairwise_comparison_matrix"])
    crit = cfg.weights["ahp_matrix"]["criteria"]

    # Reciprocity validation: A[i,j] * A[j,i] == 1
    assert np.allclose(matrix * matrix.T, np.ones((7, 7)), atol=1e-3)

    ahp_res = calculate_ahp_weights(matrix, crit)
    assert ahp_res.is_consistent is True
    assert ahp_res.consistency_ratio < 0.10
    assert abs(sum(ahp_res.weights.values()) - 1.0) < 1e-4

    # Verify P1 Demand carries highest weight (~35%) and P3 Infrastructure second (~24%)
    assert ahp_res.weights["P1"] > ahp_res.weights["P3"]
    assert ahp_res.weights["P3"] > ahp_res.weights["P2"]
    assert ahp_res.weights["P2"] > ahp_res.weights["P4"]


def test_direction_aware_normalization():
    """Validates positive and negative normalization logic."""
    raw_vals = {1: 10.0, 2: 50.0, 3: 90.0}

    # Positive: min(10)->0, max(90)->100
    norm_pos = min_max_normalize(raw_vals, direction="POSITIVE")
    assert norm_pos[1] == 0.0
    assert norm_pos[2] == 50.0
    assert norm_pos[3] == 100.0

    # Negative: min(10)->100, max(90)->0
    norm_neg = min_max_normalize(raw_vals, direction="NEGATIVE")
    assert norm_neg[1] == 100.0
    assert norm_neg[2] == 50.0
    assert norm_neg[3] == 0.0


def test_intra_pillar_entropy_weights():
    """Validates Shannon Information Entropy weight calculation properties."""
    # 3 districts, 2 indicators: one with high variance, one with zero variance
    norm_matrix = {
        1: {"ind_high_var": 0.0, "ind_no_var": 50.0},
        2: {"ind_high_var": 50.0, "ind_no_var": 50.0},
        3: {"ind_high_var": 100.0, "ind_no_var": 50.0}
    }
    weights = calculate_entropy_weights(norm_matrix, ["ind_high_var", "ind_no_var"])
    assert abs(sum(weights.values()) - 1.0) < 1e-4
    # Indicator with higher variance should receive higher entropy weight
    assert weights["ind_high_var"] > weights["ind_no_var"]


def test_saturation_dampener_mathematics():
    """Validates that high saturation correctly subtracts a penalty without score inversion."""
    pillar_scores_low_sat = {"P1": 80.0, "P2": 80.0, "P3": 80.0, "P4": 80.0, "P5": 0.0, "P6": 80.0, "P7": 80.0}
    pillar_scores_high_sat = {"P1": 80.0, "P2": 80.0, "P3": 80.0, "P4": 80.0, "P5": 100.0, "P6": 80.0, "P7": 80.0}

    driver_w = {"P1": 0.3664, "P3": 0.2468, "P2": 0.1618, "P4": 0.1039, "P6": 0.0606, "P7": 0.0606}
    sat_lambda = 0.15

    res = compute_composite_scores(
        {1: pillar_scores_low_sat, 2: pillar_scores_high_sat},
        driver_weights=driver_w,
        saturation_lambda=sat_lambda
    )

    # District 1: 0 penalty -> DLMAI = 80.0
    assert abs(res[1]["dlmai_score"] - 80.0) < 1e-2
    assert res[1]["saturation_penalty"] == 0.0

    # District 2: 15 penalty -> DLMAI = 65.0
    assert abs(res[2]["dlmai_score"] - 65.0) < 1e-2
    assert res[2]["saturation_penalty"] == 15.0
    assert res[1]["dlmai_score"] > res[2]["dlmai_score"]


def test_multi_generation_inheritance():
    """Validates multi-generation parent-child lineage inheritance resolution."""
    crosswalk = SouthDistrictCrosswalk()
    resolver = SouthInheritanceResolver(crosswalk)

    # Simulate child district with nulls and parent with observed value
    # E.g. Alluri Sitharama Raju (new AP district) parent is Visakhapatnam
    test_vals = {}
    asr_code = None
    vizag_code = None
    for code, d in crosswalk.districts.items():
        if d.district_name == "Alluri Sitharama Raju":
            asr_code = code
        elif d.district_name == "Visakhapatnam":
            vizag_code = code

    if asr_code and vizag_code:
        test_vals[asr_code] = None
        test_vals[vizag_code] = 75.5

        filled, mask = resolver.fill_missing(test_vals)
        assert filled[asr_code] == 75.5
        assert "INHERITED" in mask[asr_code]
        assert mask[vizag_code] == "OBSERVED"


def test_quantile_tier_distribution():
    """Validates that quantile tiering divides districts into expected percentiles."""
    crosswalk = SouthDistrictCrosswalk()
    meta = {code: {"district_name": d.district_name, "state_name": d.state_name} for code, d in crosswalk.districts.items()}

    # Generate synthetic scores for 148 districts
    mock_res = {}
    for i, code in enumerate(crosswalk.districts.keys()):
        mock_res[code] = {
            "dlmai_score": float(i + 1),
            "value_driver_score": float(i + 1),
            "saturation_penalty": 0.0,
            "geometric_score": float(i + 1),
            "pillar_scores": {f"P{p}": 50.0 for p in range(1, 8)}
        }

    df_ranked = assign_ranks_and_tiers(mock_res, meta)
    tier_counts = df_ranked["commercial_tier"].value_counts()

    # Top 20% should be Tier 1 (~30 districts)
    assert tier_counts["Tier 1 (High Priority)"] == 30
    assert tier_counts["Tier 4 (Nascent / Rural)"] == 30


def test_monte_carlo_reproducibility():
    """Validates that fixed random seed produces identical Monte Carlo stability correlations."""
    driver_w = {"P1": 0.3664, "P3": 0.2468, "P2": 0.1618, "P4": 0.1039, "P6": 0.0606, "P7": 0.0606}
    mock_pillars = {
        1: {"P1": 80.0, "P2": 70.0, "P3": 60.0, "P4": 50.0, "P5": 20.0, "P6": 40.0, "P7": 60.0},
        2: {"P1": 40.0, "P2": 50.0, "P3": 70.0, "P4": 60.0, "P5": 10.0, "P6": 50.0, "P7": 40.0},
        3: {"P1": 90.0, "P2": 85.0, "P3": 80.0, "P4": 75.0, "P5": 30.0, "P6": 60.0, "P7": 70.0}
    }

    mc_1 = run_monte_carlo_sensitivity(mock_pillars, driver_w, iterations=100, random_seed=42)
    mc_2 = run_monte_carlo_sensitivity(mock_pillars, driver_w, iterations=100, random_seed=42)

    assert mc_1.mean_spearman_rho == mc_2.mean_spearman_rho
    assert mc_1.district_stability_df.equals(mc_2.district_stability_df)


def test_output_deliverables_integrity():
    """Validates that all required CSV and JSON output deliverables exist and are non-empty."""
    required_outputs = [
        "outputs/dlmai_south_india_scores.csv",
        "outputs/dlmai_south_india_combined_output.csv",
        "outputs/district_coverage_matrix.csv",
        "outputs/data_quality_report.csv",
        "outputs/indicator_redundancy_report.csv",
        "outputs/robustness_comparison.csv",
        "outputs/sensitivity_results.csv",
        "outputs/ahp_validation.json",
        "outputs/refresh_metadata.json"
    ]

    for out_path in required_outputs:
        assert os.path.exists(out_path), f"Missing deliverable: {out_path}"
        assert os.path.getsize(out_path) > 0, f"Empty deliverable: {out_path}"

    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    assert len(df_scores) == 148
    assert "south_india_rank" in df_scores.columns
    assert "dlmai_score" in df_scores.columns
    assert "commercial_tier" in df_scores.columns
