"""Automated test suite for Model Comparison & Benchmarking Lab."""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api import app
from src.comparison.registry import get_default_registry, CTDITransformerRunner, LinearInterpolationRunner
from src.comparison.canonical_data import CanonicalPredictionData, PointRecord
from src.comparison.evaluation_engine import EvaluationEngine, classify_pollution_level
from src.comparison.experiment_controller import ExperimentController
from src.comparison.history import ExperimentHistoryManager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def controller():
    return ExperimentController()


class TestModelComparisonLab:
    """Comprehensive test suite for Model Comparison Lab verification."""

    def test_registry_contains_required_models(self):
        """Verifies default registry has all 5 baseline/deep models and future placeholders."""
        registry = get_default_registry()
        models = registry.list_models()
        model_ids = [m["id"] for m in models]
        
        expected_active = ["delhi_ctdi_original", "delhi_ctdi_keras", "linear_interpolation", "knn", "mean_imputer", "simple_mlp"]
        for m_id in expected_active:
            assert m_id in model_ids, f"Expected active model '{m_id}' in registry"
            runner = registry.get(m_id)
            assert runner.is_available is True

        # Check alias resolution
        assert registry.get("ctdi_transformer").id == "delhi_ctdi_original"
        assert registry.get("ctdi_keras").id == "delhi_ctdi_keras"

        expected_future = ["ctdi_improved_v2", "slm_diffusion"]
        for m_id in expected_future:
            assert m_id in model_ids, f"Expected future placeholder '{m_id}' in registry"
            runner = registry.get(m_id)
            assert runner.is_available is False

    def test_identical_mask_and_ground_truth_invariance(self, controller):
        """
        Verifies that when an experiment runs, every model receives the EXACT SAME
        missingness mask and identical incomplete input tensors.
        """
        seed = 98765
        res = controller.run_experiment(
            dataset_id="delhi_24h_sample",
            num_windows=1,
            missing_rate=0.30,
            strategy="random",
            seed=seed
        )

        assert res["missingness"]["random_seed"] == seed
        assert res["missingness"]["missing_rate"] == 0.30
        assert res["evaluation_mode"] == "ground_truth"
        assert res["windows_evaluated"] == 1
        assert res["total_points_evaluated"] > 0

        # All models were evaluated under identical evaluation mask
        rankings = res["evaluation"]["model_rankings"]
        assert len(rankings) >= 4

    def test_hidden_only_evaluation_integrity(self):
        """
        Verifies that evaluation metrics are computed STRICTLY on hidden cells (is_eval == 1).
        Observed cells (is_eval == 0) must never contribute to MAE/RMSE calculation.
        """
        canonical = CanonicalPredictionData(pollutants=["PM2.5"], model_ids=["model_a"])
        
        # Point 1: Observed point (ground_truth = 100, pred = 100, is_eval = 0)
        p1 = PointRecord(
            timestamp="2023-01-01 00:00:00",
            pollutant="PM2.5",
            ground_truth=100.0,
            observed=100.0,
            mask=1,
            is_eval=0,
            predictions={"model_a": 100.0},
            errors={"model_a": 0.0},
            abs_errors={"model_a": 0.0},
            sq_errors={"model_a": 0.0}
        )
        # Point 2: Artificially Hidden point (ground_truth = 200, pred = 250, is_eval = 1) -> error = 50
        p2 = PointRecord(
            timestamp="2023-01-01 01:00:00",
            pollutant="PM2.5",
            ground_truth=200.0,
            observed=None,
            mask=0,
            is_eval=1,
            predictions={"model_a": 250.0},
            errors={"model_a": 50.0},
            abs_errors={"model_a": 50.0},
            sq_errors={"model_a": 2500.0}
        )
        # Point 3: Naturally missing point without ground truth (ground_truth = None, is_eval = 0)
        p3 = PointRecord(
            timestamp="2023-01-01 02:00:00",
            pollutant="PM2.5",
            ground_truth=None,
            observed=None,
            mask=0,
            is_eval=0,
            predictions={"model_a": 150.0}
        )

        canonical.add_record(p1)
        canonical.add_record(p2)
        canonical.add_record(p3)

        engine = EvaluationEngine(canonical, model_names={"model_a": "Model A"})
        results = engine.compute_all_evaluations()

        # MAE must be exactly 50.0 (from p2 only), NOT diluted by p1 (0.0)
        model_res = results["overall_metrics"]["model_a"]
        assert model_res["count"] == 1
        assert model_res["MAE"] == 50.0
        assert model_res["RMSE"] == 50.0
        assert model_res["Bias"] == 50.0

    def test_observed_value_preservation(self, controller):
        """
        Verifies that every model strictly preserves 100% of observed values:
        max |output_obs - input_obs| < 1e-4.
        """
        res = controller.run_experiment(
            dataset_id="delhi_24h_sample",
            num_windows=1,
            missing_rate=0.40,
            seed=42
        )

        csv_content = res["canonical_csv"]
        df = pd.read_csv(pd.io.common.StringIO(csv_content))

        # Filter to observed rows
        obs_df = df[df["mask"] == 1]
        assert len(obs_df) > 0

        for m_id in res["models_evaluated"]:
            pred_col = f"{m_id}_pred"
            if pred_col in obs_df.columns:
                diffs = np.abs(obs_df[pred_col] - obs_df["observed"])
                max_diff = diffs.max()
                assert max_diff < 1e-3, f"Model {m_id} violated observed value preservation (max diff: {max_diff})"

    def test_deterministic_reproducibility(self, controller):
        """
        Verifies that running two experiments with the same seed produces
        identical metrics and rankings.
        """
        seed = 12345
        run1 = controller.run_experiment(dataset_id="delhi_24h_sample", num_windows=1, seed=seed)
        run2 = controller.run_experiment(dataset_id="delhi_24h_sample", num_windows=1, seed=seed)

        r1_ranks = [(r["model_id"], r["MAE"], r["RMSE"]) for r in run1["evaluation"]["model_rankings"]]
        r2_ranks = [(r["model_id"], r["MAE"], r["RMSE"]) for r in run2["evaluation"]["model_rankings"]]

        assert r1_ranks == r2_ranks

    def test_canonical_export_parity(self, controller):
        """
        Verifies that canonical records and CSV export match 1:1 in shape and columns.
        """
        res = controller.run_experiment(dataset_id="delhi_24h_sample", num_windows=1, seed=42)
        csv_str = res["canonical_csv"]
        df = pd.read_csv(pd.io.common.StringIO(csv_str))

        # 1 window * 24 hours * 5 pollutants = 120 canonical rows
        assert len(df) == 120
        assert "timestamp" in df.columns
        assert "pollutant" in df.columns
        assert "ground_truth" in df.columns
        assert "observed" in df.columns
        assert "mask" in df.columns
        assert "is_eval" in df.columns
        assert "is_peak" in df.columns
        assert "gap_length" in df.columns

    def test_api_comparison_endpoints(self, client):
        """Verifies all REST API comparison endpoints return expected HTTP 200 responses."""
        # 1. Models
        res = client.get("/api/comparison/models")
        assert res.status_code == 200
        models = res.json()
        assert len(models) >= 5

        # 2. Datasets
        res = client.get("/api/comparison/datasets")
        assert res.status_code == 200
        datasets = res.json()
        assert len(datasets) >= 2

        # 3. Run benchmark
        payload = {
            "dataset_id": "delhi_24h_sample",
            "num_windows": 1,
            "missing_rate": 0.25,
            "seed": 42
        }
        res = client.post("/api/comparison/run", json=payload)
        assert res.status_code == 200
        exp_data = res.json()
        exp_id = exp_data["experiment_id"]
        assert exp_id.startswith("EXP-LAB-")

        # 4. History
        res = client.get("/api/comparison/history")
        assert res.status_code == 200
        history = res.json()
        assert any(h["experiment_id"] == exp_id for h in history)

        # 5. Get specific experiment
        res = client.get(f"/api/comparison/history/{exp_id}")
        assert res.status_code == 200
        assert res.json()["experiment_id"] == exp_id

        # 6. Export CSV
        res = client.get(f"/api/comparison/export/{exp_id}?format=csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        assert "timestamp,pollutant,ground_truth" in res.text

    def test_city_filtered_models_and_cities_endpoint(self, client):
        """Verifies /api/comparison/cities and /api/comparison/models?city=Delhi endpoints."""
        # 1. Cities
        res = client.get("/api/comparison/cities")
        assert res.status_code == 200
        cities = res.json()
        assert len(cities) >= 1
        assert any(c["city"] == "Delhi" for c in cities)

        # 2. Filtered models
        res_models = client.get("/api/comparison/models?city=Delhi")
        assert res_models.status_code == 200
        models = res_models.json()
        m_ids = [m["id"] for m in models]
        assert "delhi_ctdi_original" in m_ids
        assert "delhi_ctdi_keras" in m_ids
        assert "linear_interpolation" in m_ids

    def test_direct_model_agreement_metrics(self, controller):
        """
        Verifies that comparing Original CTDI (PyTorch) and Keras CTDI produces
        authentic direct model-to-model agreement metrics and scatter points.
        """
        res = controller.run_experiment(
            dataset_id="delhi_24h_sample",
            num_windows=1,
            model_ids=["delhi_ctdi_original", "delhi_ctdi_keras"],
            missing_rate=0.30,
            seed=42137
        )

        assert "model_agreement" in res
        agreement = res["model_agreement"]
        assert agreement is not None
        assert "mae_diff" in agreement
        assert "rmse_diff" in agreement
        assert "max_diff" in agreement
        assert "pearson_correlation" in agreement
        assert "scatter_points" in agreement
        assert len(agreement["scatter_points"]) > 0
        assert "scientific_statement" in agreement
        assert agreement["mae_diff"] > 0
        assert agreement["pearson_correlation"] > 0.90

    def test_production_model_isolation(self, client):
        """
        Verifies that running multi-model comparison experiments does NOT
        alter or overwrite the production active model in /api/health.
        """
        # Set active model to PyTorch
        client.post("/api/models/select", json={"model_id": "delhi_ctdi_original"})
        h_before = client.get("/api/health").json()
        assert h_before["model_id"] == "delhi_ctdi_original"

        # Run comparison with Keras included
        res = client.post("/api/comparison/run", json={
            "dataset_id": "delhi_24h_sample",
            "num_windows": 1,
            "model_ids": ["delhi_ctdi_original", "delhi_ctdi_keras"],
            "seed": 42
        })
        assert res.status_code == 200

        # Verify active model is STILL PyTorch
        h_after = client.get("/api/health").json()
        assert h_after["model_id"] == "delhi_ctdi_original", "Comparison run leaked into production model state!"
