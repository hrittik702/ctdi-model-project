"""Automated test suite for the upgraded Model Comparison Lab features.

Covers:
1. EXP-LAB-7840 canonical CSV loading, invariance validation, and metric reproduction
2. Data quality detection (cell counts, sampling interval, preliminary flag)
3. Bootstrap 95% Confidence Intervals for MAE
4. Model Win Matrix & multi-dimensional win summary
5. Enhanced Peak Reconstruction & catalog
6. Model Delta View time-series computation
7. Model Registry 13+ factual metadata fields & non-fabrication
8. Native publication-grade PDF export API
9. Experiment deterministic re-run API
"""

import os
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api import app
from src.comparison.registry import get_default_registry
from src.comparison.canonical_data import CanonicalPredictionData, PointRecord
from src.comparison.evaluation_engine import EvaluationEngine
from src.comparison.experiment_controller import ExperimentController
from src.comparison.export_pdf import generate_experiment_pdf_report


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def controller():
    return ExperimentController()


REFERENCE_CSV_PATH = "results/experiments/EXP-LAB-7840_predictions.csv"


class TestModelComparisonUpgrade:
    """Test suite for upgraded scientific features in Model Comparison Lab."""

    def test_canonical_csv_loading_and_invariance(self):
        """Verifies loading EXP-LAB-7840 canonical predictions and validating observed value invariance."""
        assert os.path.exists(REFERENCE_CSV_PATH), f"Missing {REFERENCE_CSV_PATH}"
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)

        assert len(canonical.records) == 120, f"Expected 120 records, got {len(canonical.records)}"
        assert len(canonical.pollutants) == 5
        assert set(canonical.model_ids) == {"delhi_ctdi_original", "delhi_ctdi_keras", "simple_mlp"}

        obs_count = sum(1 for r in canonical.records if r.mask == 1)
        eval_count = sum(1 for r in canonical.records if r.is_eval == 1)
        assert obs_count == 64, f"Expected 64 observed cells, got {obs_count}"
        assert eval_count == 56, f"Expected 56 evaluated cells, got {eval_count}"

        # Invariance check: output_obs == input_obs
        is_valid, max_diff, violations = canonical.validate_invariance(tolerance=1e-3)
        assert is_valid is True, f"Invariance check failed with {len(violations)} violations, max diff {max_diff}"
        assert max_diff < 1e-3

    def test_evaluation_engine_metrics_on_exp_lab_7840(self):
        """
        Verifies that EvaluationEngine reproduces reference metrics on EXP-LAB-7840
        strictly from calculated points (no fabrication or hardcoding).
        """
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)
        engine = EvaluationEngine(
            canonical,
            model_names={
                "delhi_ctdi_original": "Delhi CTDI (PyTorch)",
                "delhi_ctdi_keras": "Delhi CTDI (Keras)",
                "simple_mlp": "Simple MLP"
            }
        )
        eval_results = engine.compute_all_evaluations()

        metrics = eval_results["overall_metrics"]

        # Keras CTDI
        keras_m = metrics["delhi_ctdi_keras"]
        assert keras_m["count"] == 56
        assert abs(keras_m["MAE"] - 3.75) < 0.1, f"Expected Keras MAE ~3.75, got {keras_m['MAE']}"
        assert abs(keras_m["RMSE"] - 7.71) < 0.1, f"Expected Keras RMSE ~7.71, got {keras_m['RMSE']}"
        assert abs(keras_m["R2"] - 0.988) < 0.05, f"Expected Keras R2 ~0.988, got {keras_m['R2']}"
        assert abs(keras_m["Correlation"] - 0.995) < 0.02

        # Original CTDI
        orig_m = metrics["delhi_ctdi_original"]
        assert orig_m["count"] == 56
        assert abs(orig_m["MAE"] - 9.82) < 0.1, f"Expected Original MAE ~9.82, got {orig_m['MAE']}"
        assert abs(orig_m["RMSE"] - 14.17) < 0.1, f"Expected Original RMSE ~14.17, got {orig_m['RMSE']}"
        assert abs(orig_m["R2"] - 0.960) < 0.05, f"Expected Original R2 ~0.960, got {orig_m['R2']}"

        # Simple MLP
        mlp_m = metrics["simple_mlp"]
        assert mlp_m["count"] == 56
        assert abs(mlp_m["MAE"] - 40.98) < 0.1, f"Expected MLP MAE ~40.98, got {mlp_m['MAE']}"
        assert abs(mlp_m["RMSE"] - 52.80) < 0.1, f"Expected MLP RMSE ~52.80, got {mlp_m['RMSE']}"

        # Model Rankings
        rankings = eval_results["model_rankings"]
        assert rankings[0]["model_id"] == "delhi_ctdi_keras"
        assert rankings[1]["model_id"] == "delhi_ctdi_original"
        assert rankings[2]["model_id"] == "simple_mlp"

    def test_data_quality_and_sampling_interval_detection(self):
        """Verifies sampling interval detection and cell count accuracy."""
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)
        engine = EvaluationEngine(canonical)
        dq = engine.compute_data_quality()

        assert dq["total_cells"] == 120
        assert dq["observed_cells"] == 64
        assert dq["evaluated_cells"] == 56
        assert dq["sampling_interval"] == "1 hour"
        # Since evaluated_cells = 56 < 100, is_preliminary MUST be True
        assert dq["is_preliminary"] is True
        assert "preliminary_warning" in dq

        # Pollutant breakdown
        assert len(dq["pollutant_breakdown"]) == 5
        for pol, stats in dq["pollutant_breakdown"].items():
            assert stats["total"] == 24
            assert stats["observed"] + stats["evaluated"] <= 24
            assert 0.0 <= stats["missing_rate"] <= 1.0
            assert stats["max_gap_hours"] >= 0

    def test_bootstrap_confidence_intervals(self):
        """Verifies 95% Bootstrap Confidence Interval generation when n >= 30 and fallback when n < 30."""
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)
        engine = EvaluationEngine(canonical)
        eval_results = engine.compute_all_evaluations()

        metrics = eval_results["overall_metrics"]
        # n = 56 >= 30 -> CI must be computed
        for m_id in canonical.model_ids:
            ci = metrics[m_id].get("mae_ci_95")
            assert ci is not None, f"Expected MAE CI for {m_id} with n=56"
            assert "low" in ci and "high" in ci and "mean" in ci
            assert ci["low"] <= ci["mean"] <= ci["high"]

        # Test small sample fallback n < 30
        ci_small = engine._bootstrap_ci(np.array([1.0, 2.0, 3.0]))
        assert ci_small is None

    def test_model_win_matrix_and_win_summary(self):
        """Verifies Model Win Matrix across pollutants and multi-dimensional win summary."""
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)
        engine = EvaluationEngine(canonical)
        eval_results = engine.compute_all_evaluations()

        win_matrix = eval_results["model_win_matrix"]
        assert win_matrix is not None
        assert "MAE" in win_matrix
        assert "RMSE" in win_matrix
        assert "Correlation" in win_matrix

        # Each model must have pollutant entries with ranks and values
        for m_id in canonical.model_ids:
            assert m_id in win_matrix["MAE"]
            for pol in canonical.pollutants:
                assert pol in win_matrix["MAE"][m_id]
                assert "rank" in win_matrix["MAE"][m_id][pol]
                assert "value" in win_matrix["MAE"][m_id][pol]

        # Win summary
        win_summary = eval_results["win_summary"]
        assert win_summary["overall_winner"] == "delhi_ctdi_keras"
        assert "pollutant_winners" in win_summary
        assert "peak_winner" in win_summary
        assert "long_gap_winner" in win_summary

    def test_peak_reconstruction_and_catalog(self):
        """Verifies peak amplitude error, recovery rate, and 1-click zoom catalog."""
        canonical = CanonicalPredictionData.from_csv_file(REFERENCE_CSV_PATH)
        engine = EvaluationEngine(canonical)
        eval_results = engine.compute_all_evaluations()

        peak_recon = eval_results["peak_reconstruction"]
        for m_id in canonical.model_ids:
            p_data = peak_recon[m_id]
            assert "peak_count" in p_data
            assert "amplitude_error" in p_data
            assert "recovery_rate_pct" in p_data

        catalog = eval_results["peak_analysis"]["peaks_catalog"]
        assert len(catalog) > 0
        for entry in catalog:
            assert "pollutant" in entry
            assert "ground_truth" in entry
            assert "predictions" in entry
            assert "amplitude_errors" in entry

        # Keras should have superior peak MAE and closer recovery rate to 100% than MLP
        assert peak_recon["delhi_ctdi_keras"]["peak_mae"] < peak_recon["simple_mlp"]["peak_mae"]
        keras_rec_diff = abs(peak_recon["delhi_ctdi_keras"]["recovery_rate_pct"] - 100.0)
        mlp_rec_diff = abs(peak_recon["simple_mlp"]["recovery_rate_pct"] - 100.0)
        assert keras_rec_diff < mlp_rec_diff

    def test_model_registry_factual_metadata_fields(self):
        """Verifies all 13+ factual metadata fields are populated without fabrication."""
        registry = get_default_registry()
        models = registry.list_models()

        required_fields = [
            "id", "name", "city", "dataset_id", "framework", "architecture",
            "version", "checkpoint_path", "scaler_path", "preprocessing_version",
            "feature_version", "training_date", "parameter_count", "model_size_mb", "status"
        ]

        for m in models:
            for field in required_fields:
                assert field in m, f"Model {m['id']} missing metadata field '{field}'"
                val = m[field]
                assert val is not None and str(val).strip() != "", f"Field '{field}' is empty for {m['id']}"

        # Deep learning models must point to real checkpoint files with physical file sizes
        delhi_orig = registry.get("delhi_ctdi_original").get_metadata()
        delhi_keras = registry.get("delhi_ctdi_keras").get_metadata()

        assert delhi_orig["framework"] == "PyTorch"
        assert "Keras 3" in delhi_keras["framework"]
        assert float(delhi_orig["model_size_mb"]) > 1.0
        assert float(delhi_keras["model_size_mb"]) > 1.0
        assert delhi_orig["training_date"] != "Not available"
        assert delhi_keras["training_date"] != "Not available"

    def test_model_deltas_computation(self, controller):
        """Verifies computation of model deltas (Prediction Difference time series)."""
        res = controller.run_canonical_experiment(REFERENCE_CSV_PATH, experiment_id="EXP-LAB-TEST-DELTA")
        assert "model_deltas" in res
        deltas = res["model_deltas"]
        assert len(deltas) >= 1

        for pol in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
            assert pol in deltas
            assert len(deltas[pol]) == 24
            pt0 = deltas[pol][0]
            assert "delta" in pt0
            assert "model_a_pred" in pt0
            assert "model_b_pred" in pt0
            assert "ground_truth" in pt0

    def test_pdf_export_generation(self):
        """Verifies that generate_experiment_pdf_report produces valid PDF bytes."""
        controller = ExperimentController()
        exp_data = controller.run_canonical_experiment(REFERENCE_CSV_PATH, experiment_id="EXP-LAB-TEST-PDF")

        pdf_bytes = generate_experiment_pdf_report(exp_data)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 5000, "PDF size suspiciously small"
        assert pdf_bytes.startswith(b"%PDF-"), "Invalid PDF signature"

    def test_pdf_export_endpoint(self, client):
        """Verifies GET /api/comparison/export/{id}?format=pdf returns valid application/pdf."""
        # 1. Run canonical experiment
        res_run = client.post("/api/comparison/run", json={"dataset_id": "exp_lab_7840"})
        assert res_run.status_code == 200
        exp_id = res_run.json()["experiment_id"]

        # 2. Request PDF
        res_pdf = client.get(f"/api/comparison/export/{exp_id}?format=pdf")
        assert res_pdf.status_code == 200
        assert res_pdf.headers.get("content-type") == "application/pdf"
        assert res_pdf.content.startswith(b"%PDF-")

    def test_experiment_rerun_reproducibility(self, client):
        """Verifies POST /api/comparison/re-run/{id} produces identical results."""
        # 1. Run standard experiment
        res1 = client.post("/api/comparison/run", json={
            "dataset_id": "delhi_24h_sample",
            "num_windows": 1,
            "missing_rate": 0.25,
            "seed": 9999
        })
        assert res1.status_code == 200
        exp1 = res1.json()
        orig_id = exp1["experiment_id"]

        # 2. Re-run experiment
        res_rerun = client.post(f"/api/comparison/re-run/{orig_id}")
        assert res_rerun.status_code == 200
        rerun_data = res_rerun.json()

        assert rerun_data["missingness"]["random_seed"] == 9999
        assert rerun_data["windows_evaluated"] == 1
        assert rerun_data["total_points_evaluated"] == exp1["total_points_evaluated"]

        # Compare MAEs across both runs
        ranks1 = {r["model_id"]: r["MAE"] for r in exp1["evaluation"]["model_rankings"]}
        ranks2 = {r["model_id"]: r["MAE"] for r in rerun_data["evaluation"]["model_rankings"]}
        for m_id, mae in ranks1.items():
            assert abs(mae - ranks2[m_id]) < 1e-4
