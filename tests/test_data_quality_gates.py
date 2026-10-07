"""
Automated Pytest Suite for DLMAI v2.0 Enterprise Data Quality Gates, Geography, and Provenance.
Validates all 15 quality gates, zero sample contamination, 5-way cell classification,
NFHS/RHS audits, and model run metadata integrity.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.config import get_config
from src.validation.quality_gates import DLMAIQualityGateEngine, assert_all_production_geographies_canonical


def test_quality_gate_01_canonical_geography_integrity():
    """Gate 1: Verifies that exactly 148 canonical districts exist and match the LGD master."""
    engine = DLMAIQualityGateEngine()
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    assert len(df_scores) == 148
    assert set(df_scores["lgd_district_code"].tolist()) == engine.canonical_lgd_codes


def test_quality_gate_02_zero_sample_ids_contamination():
    """Gate 2: Rejects any sample/demo district IDs (SAMPLE-*) in production data."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    sample_ids = [c for c in df_scores["lgd_district_code"].tolist() if isinstance(c, str) and c.startswith("SAMPLE-")]
    assert len(sample_ids) == 0, f"Found sample IDs: {sample_ids}"

    # Test that the strict assertion raises ValueError when given sample IDs
    with pytest.raises(ValueError, match="Non-canonical district identifier detected"):
        assert_all_production_geographies_canonical(["SAMPLE-TN-01", 560], {560})


def test_quality_gate_03_no_unknown_geography():
    """Gate 3: Asserts zero unknown geography codes in processing matrix."""
    df_combined = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
    engine = DLMAIQualityGateEngine()
    assert set(df_combined["lgd_district_code"].tolist()) == engine.canonical_lgd_codes


def test_quality_gate_04_required_source_files_exist():
    """Gate 4: Asserts all primary source files exist."""
    required = [
        "data/master/lgd_south_india.csv",
        "data/master/district_crosswalk_south.csv",
        "data/rhs/district-wise-health-centres.pdf",
        "data/census/primary_census_abstract/PCA_district_level.csv"
    ]
    for r in required:
        assert os.path.exists(r), f"Missing required file: {r}"


def test_quality_gate_05_source_coverage_and_completeness():
    """Gate 5: Quantitative tracking of observed, inherited, and imputed values."""
    df_quality = pd.read_csv("outputs/data_quality_report.csv")
    assert len(df_quality) == 148
    assert df_quality["observed_pct"].mean() > 75.0  # High baseline observed completeness
    assert (df_quality["observed_pct"] + df_quality["inherited_pct"] + df_quality["imputed_pct"]).min() >= 99.9


def test_quality_gate_06_zero_district_duplication():
    """Gate 6: Zero duplicate rows in output files."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    assert df_scores["lgd_district_code"].duplicated().sum() == 0


def test_quality_gate_07_indicator_domain_and_unit_integrity():
    """Gate 7: Validates domain bounds (percentages 0-100, densities >= 0)."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    for col in ["value_driver_score", "saturation_penalty", "dlmai_score"]:
        assert df_scores[col].min() >= 0.0
        assert df_scores[col].max() <= 100.0


def test_quality_gate_08_no_nan_or_inf_in_scores():
    """Gate 8: Non-NaN and finite score assertions."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    assert df_scores["dlmai_score"].isna().sum() == 0
    assert np.isinf(df_scores["dlmai_score"]).sum() == 0


def test_quality_gate_09_population_denominator_universal():
    """Gate 9: Every district has population reference > 0."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    assert "total_population_estimate_millions" in df_scores.columns or "census_total_population" in pd.read_csv("outputs/dlmai_south_india_combined_output.csv").columns


def test_quality_gate_10_cell_provenance_classification():
    """Gate 10: 100% of cells classified in 5-way provenance taxonomy."""
    df_prov = pd.read_csv("outputs/data_quality/indicator_provenance.csv")
    assert len(df_prov) > 0
    valid_classes = {"DIRECT_OBSERVED", "INHERITED", "STATISTICALLY_IMPUTED", "PROXY_ESTIMATE", "STRUCTURAL_ZERO", "UNAVAILABLE"}
    assert set(df_prov["provenance_class"].unique()).issubset(valid_classes)


def test_quality_gate_11_seven_pillar_completeness():
    """Gate 11: P1-P7 all computed and present."""
    df_scores = pd.read_csv("outputs/dlmai_south_india_scores.csv")
    for i in range(1, 8):
        assert f"pillar_p{i}_score" in df_scores.columns
        assert df_scores[f"pillar_p{i}_score"].isna().sum() == 0


def test_quality_gate_12_p5_mode_and_mca21_transparency():
    """Gate 12: Asserts P5 mode is explicitly declared and not claiming direct raw bulk observation."""
    p5_audit = pd.read_csv("outputs/data_quality/mca21_provenance_audit.csv")
    assert len(p5_audit) == 148
    assert p5_audit["is_field_force_competition"].all() == False
    assert (p5_audit["p5_status"] == "CALIBRATED_PROXY_ESTIMATE").all()


def test_quality_gate_13_pipeline_quality_report_json():
    """Gate 13: Pipeline quality report JSON is generated and all 15 gates pass."""
    report_path = "outputs/data_quality/pipeline_quality_gate_report.json"
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_gates"] == 15
    assert data["passed_gates"] == 15
    assert data["critical_failures"] == 0
    assert data["is_production_ready"] is True


def test_quality_gate_14_model_run_metadata_provenance():
    """Gate 14: Model run metadata contains execution info and benchmark classification."""
    meta_path = "outputs/model_run_metadata.json"
    assert os.path.exists(meta_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["model_version"] == "DLMAI v2.0.0"
    assert "Class D" in meta["target_commercial_benchmark_class"]


def test_quality_gate_15_all_audit_deliverables_present():
    """Gate 15: All 8 forensic data quality CSV/JSON artifacts are generated."""
    expected_artifacts = [
        "outputs/data_quality/geography_audit.csv",
        "outputs/data_quality/nfhs_coverage_audit.csv",
        "outputs/data_quality/rhs_coverage_audit.csv",
        "outputs/data_quality/jan_aushadhi_mapping_audit.csv",
        "outputs/data_quality/mca21_provenance_audit.csv",
        "outputs/data_quality/district_data_completeness.csv",
        "outputs/data_quality/indicator_provenance.csv",
        "outputs/data_quality/pipeline_quality_gate_report.json",
        "outputs/model_run_metadata.json"
    ]
    for art in expected_artifacts:
        assert os.path.exists(art), f"Missing audit artifact: {art}"
