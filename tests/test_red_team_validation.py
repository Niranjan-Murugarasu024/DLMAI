"""
AUTOMATED RED-TEAM, STATISTICAL & EXTERNAL COMMERCIAL VALIDATION TEST SUITE
Validates mathematical exactness, AHP consistency, geography, indicator domains,
reproducibility, non-compensatory bounds, provenance transparency, and external validation integrity.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path


def test_01_independent_score_reconciliation():
    """Validates that independent mathematical recalculation perfectly reproduces production scores."""
    reconcile_path = "outputs/red_team_validation_v2/test01_independent_recalculation.csv"
    assert os.path.exists(reconcile_path), f"Missing {reconcile_path}"
    df = pd.read_csv(reconcile_path)
    
    score_diffs = np.abs(df["indep_dlmai_score"] - df["dlmai_score"])
    rank_diffs = np.abs(df["indep_south_india_rank"] - df["south_india_rank"])
    
    assert np.max(score_diffs) <= 2e-4, f"Max score diff {np.max(score_diffs)} exceeds tolerance"
    assert np.max(rank_diffs) == 0, f"Max rank difference is non-zero: {np.max(rank_diffs)}"


def test_02_ahp_mathematical_consistency():
    """Validates AHP principal eigenvalue, consistency ratio < 0.10, and driver weight sum == 1.0."""
    summary_path = "outputs/red_team_validation_v2/test01_reconciliation_summary.json"
    assert os.path.exists(summary_path), f"Missing {summary_path}"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["ahp_consistency_ratio"] < 0.10
    assert summary["cr_below_0_10"] is True

    import yaml
    with open("config/weights.yaml", "r", encoding="utf-8") as f:
        w_cfg = yaml.safe_load(f)
    driver_sum = sum(w_cfg["value_driver_weights_renormalized"].values())
    assert abs(driver_sum - 1.0) < 1e-5


def test_03_canonical_geography_integrity():
    """Validates exact 148 districts, 7 target states, and no duplicate LGD codes."""
    geo_path = "outputs/red_team_validation_v2/test01_geography_validation.csv"
    assert os.path.exists(geo_path), f"Missing {geo_path}"
    df = pd.read_csv(geo_path)
    
    assert len(df) == 148
    assert df["lgd_district_code"].nunique() == 148
    assert df["state_name"].nunique() == 7


def test_04_indicator_catalog_and_domain_integrity():
    """Validates all 20 scored indicators have 0 NaNs, 0 Infs, and valid numerical domains."""
    int_path = "outputs/red_team_validation_v2/test01_indicator_integrity.csv"
    assert os.path.exists(int_path), f"Missing {int_path}"
    df = pd.read_csv(int_path)
    
    assert len(df) == 20
    assert (df["missing_count"] == 0).all()
    assert (df["inf_count"] == 0).all()
    assert (df["domain_valid"] == True).all()


def test_05_dlmai_linear_identity_exactness():
    """Validates exact linear identity: DLMAI = ValueDriver - Penalty (within rounding error)."""
    scores_path = "outputs/dlmai_south_india_scores.csv"
    assert os.path.exists(scores_path), f"Missing {scores_path}"
    df = pd.read_csv(scores_path)
    
    residuals = np.abs((df["value_driver_score"] - df["saturation_penalty"]) - df["dlmai_score"])
    assert np.max(residuals) <= 2e-4


def test_06_normalization_decomposition_stability():
    """Validates normalization sensitivity outputs and confirms Robust IQR scaling preserves rank ordering."""
    decomp_path = "outputs/red_team_validation_v2/test02_normalization_effect_decomposition.csv"
    assert os.path.exists(decomp_path), f"Missing {decomp_path}"
    df = pd.read_csv(decomp_path)
    
    rob_row = df[df["normalization_method"] == "2_Robust_IQR"].iloc[0]
    assert rob_row["fixed_weights_rho"] == 1.0000


def test_07_topn_inclusion_probabilities():
    """Validates that Top-N inclusion probabilities fall strictly in [0, 100] and are non-null."""
    topn_path = "outputs/red_team_validation_v2/test03_topn_robustness.csv"
    assert os.path.exists(topn_path), f"Missing {topn_path}"
    df = pd.read_csv(topn_path)
    
    assert len(df) == 148
    assert (df["top_10_frequency_pct"] >= 0.0).all() and (df["top_10_frequency_pct"] <= 100.0).all()
    assert (df["top_20_frequency_pct"] >= 0.0).all() and (df["top_20_frequency_pct"] <= 100.0).all()


def test_08_data_quality_bias_absence():
    """Validates that data completeness does not exhibit strong artificial positive bias on DLMAI score."""
    corr_path = "outputs/red_team_validation_v2/test04_data_quality_correlations.csv"
    assert os.path.exists(corr_path), f"Missing {corr_path}"
    df = pd.read_csv(corr_path)
    
    obs_corr = df[df["quality_metric"] == "observed_pct"].iloc[0]["pearson_r_with_dlmai_score"]
    assert obs_corr <= 0.10, f"Unexpected positive quality bias: {obs_corr}"


def test_09_monte_carlo_convergence():
    """Validates that Monte Carlo mean rank stability rho exceeds 0.95 across both 1k and 5k iterations."""
    mc_path = "outputs/red_team_validation_v2/test07_monte_carlo_global.csv"
    assert os.path.exists(mc_path), f"Missing {mc_path}"
    df = pd.read_csv(mc_path)
    
    assert (df["mean_spearman_rho"] >= 0.95).all()
    assert (df["mean_kendall_tau"] >= 0.85).all()


def test_10_master_validation_dataset_completeness():
    """Validates that the master validation dataset dlmai_district_validation_master.csv exists with 148 rows."""
    master_path = "outputs/red_team_validation_v2/dlmai_district_validation_master.csv"
    assert os.path.exists(master_path), f"Missing {master_path}"
    df = pd.read_csv(master_path)
    
    assert len(df) == 148
    assert "annual_pharma_sales_inr_cr" in df.columns
    assert "chronic_ncd_sales_inr_cr" in df.columns
    assert "need_score" in df.columns
    assert "access_score" in df.columns
    assert "growth_score" in df.columns
    assert "competition_score" in df.columns


def test_11_test08_provenance_transparency():
    """Validates that Test 8 provenance audit correctly flags all 148 districts as synthetic/calibrated."""
    prov_path = "outputs/red_team_validation_v2/test08_district_provenance_summary.json"
    assert os.path.exists(prov_path), f"Missing {prov_path}"
    with open(prov_path, "r", encoding="utf-8") as f:
        p_summary = json.load(f)
    
    assert p_summary["total_districts_evaluated"] == 148
    assert p_summary["number_with_directly_observed_district_sales"] == 0
    assert p_summary["number_with_derived_sales"] == 148
    assert "CALIBRATED" in p_summary["district_provenance_classification"]


def test_12_test08_no_direct_dlmai_leakage():
    """Validates that DLMAI composite score itself was not used to generate sales benchmark."""
    circ_path = "outputs/red_team_validation_v2/test08_circularity_matrix.csv"
    assert os.path.exists(circ_path), f"Missing {circ_path}"
    df = pd.read_csv(circ_path)
    
    dlmai_row = df[df["variable_name"] == "dlmai_score"].iloc[0]
    assert bool(dlmai_row["used_in_benchmark_construction"]) is False


def test_13_test08_baseline_comparison_exists():
    """Validates that baseline comparisons exist and confirm population scale outperforms DLMAI on absolute turnover."""
    base_path = "outputs/red_team_validation_v2/test08_baseline_comparison.csv"
    assert os.path.exists(base_path), f"Missing {base_path}"
    df = pd.read_csv(base_path)
    
    assert len(df) == 5
    pop_row = df[df["model_id"] == "Baseline_A"].iloc[0]
    dlmai_row = df[df["model_id"] == "Model_E"].iloc[0]
    assert pop_row["oos_5fold_r2"] > dlmai_row["oos_5fold_r2"]


def test_14_test08_small_sample_warning_flags():
    """Validates that LOSO cross-validation flags Goa and Puducherry with insufficient sample warnings."""
    loso_path = "outputs/red_team_validation_v2/test08_leave_one_state_out_cv.csv"
    assert os.path.exists(loso_path), f"Missing {loso_path}"
    df = pd.read_csv(loso_path)
    
    goa_row = df[df["held_out_state"] == "Goa"].iloc[0]
    pudu_row = df[df["held_out_state"] == "Puducherry"].iloc[0]
    
    assert "INSUFFICIENT_SAMPLE" in goa_row["interpretability_flag"]
    assert "INSUFFICIENT_SAMPLE" in pudu_row["interpretability_flag"]
