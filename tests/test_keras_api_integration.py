"""Integration tests verifying 'Delhi (Keras)' API endpoints and frontend contract."""

import pytest
import numpy as np
from fastapi.testclient import TestClient
from api import app, load_resources


@pytest.fixture(scope="module")
def client():
    load_resources()
    with TestClient(app) as c:
        yield c


def test_stations_contains_delhi_and_keras(client):
    res = client.get("/api/stations")
    assert res.status_code == 200
    data = res.json()
    stn_map = {s["id"]: s for s in data["stations"]}
    
    # Pure geographic stations catalog: Delhi is present, synthetic cities are separated
    assert "Delhi" in stn_map
    assert stn_map["Delhi"]["model_trained"] is True
    assert "trained_models" in stn_map["Delhi"]
    assert "delhi_ctdi_original" in stn_map["Delhi"]["trained_models"]
    assert "delhi_ctdi_keras" in stn_map["Delhi"]["trained_models"]
    assert "Delhi (Keras)" not in stn_map, "Delhi (Keras) must not be a separate city"


def test_station_selection_lifecycle(client):
    # Select Delhi (Keras)
    res = client.post("/api/stations/select", json={"station": "Delhi (Keras)"})
    assert res.status_code == 200
    assert res.json()["active_station"] == "Delhi (Keras)"

    # Health endpoint verifies Keras active model
    h = client.get("/api/health").json()
    assert h["status"] == "ok"
    assert h["model_loaded"] is True
    assert "Keras 3" in h["framework"]
    assert "best_temporal_transformer.keras" in h["checkpoint"]

    # Metadata reflects Keras framework
    meta = client.get("/api/metadata").json()
    assert meta["station"] in ["Delhi", "Delhi (Keras)"]
    assert "Keras" in meta["framework"]

    # Metrics returns Keras summary
    metrics = client.get("/api/metrics").json()
    assert any("Keras" in m["Model"] for m in metrics)

    # Pollutant metrics returns per-pollutant metrics
    pol_metrics = client.get("/api/metrics/pollutants").json()
    for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
        assert p in pol_metrics
        assert "ctdi_mae" in pol_metrics[p]
        assert pol_metrics[p]["ctdi_mae"] > 0

    # Switch back to Delhi
    res_back = client.post("/api/stations/select", json={"station": "Delhi"})
    assert res_back.status_code == 200
    assert res_back.json()["active_station"] == "Delhi"

    h_pt = client.get("/api/health").json()
    assert h_pt["framework"] == "PyTorch"


def test_sample_endpoint_keras_strict_observation_lock(client):
    # Fetch sample 0 for Delhi (Keras)
    res = client.get("/api/samples/0?station=Delhi%20(Keras)")
    assert res.status_code == 200
    data = res.json()
    assert data["station"] == "Delhi (Keras)"
    assert "Keras" in data["framework"]

    for pol, p_data in data["pollutants"].items():
        actual = p_data["actual"]
        pred = p_data["transformer"]
        obs_mask = p_data["observed_mask"]

        # Strictly verify observation lock: observed values MUST equal prediction
        for t in range(24):
            if obs_mask[t] == 1 and actual[t] is not None:
                assert pred[t] is not None
                assert abs(pred[t] - actual[t]) < 1e-4, f"Mismatch on observed point {t} for {pol}"


def test_live_impute_keras(client):
    res = client.post("/api/impute", json={
        "sample_idx": 5,
        "station": "Delhi (Keras)",
        "missing_rate": 0.35,
        "mechanism": "random",
        "seed": 123
    })
    assert res.status_code == 200
    data = res.json()
    assert data["station"] == "Delhi (Keras)"
    assert "Keras" in data["framework"]

    for pol, p_data in data["pollutants"].items():
        actual = p_data["actual"]
        pred = p_data["transformer"]
        obs_mask = p_data["observed_mask"]

        for t in range(24):
            if obs_mask[t] == 1 and actual[t] is not None:
                assert pred[t] is not None
                assert abs(pred[t] - actual[t]) < 1e-4


def test_model_config_keras(client):
    res = client.get("/api/model/config?station=Delhi%20(Keras)")
    assert res.status_code == 200
    cfg = res.json()
    assert "Keras 3" in cfg["framework"]
    assert cfg["d_model"] == 128
    assert cfg["nhead"] == 8
    assert cfg["num_layers"] == 3
    assert cfg["checkpoint_exists"] is True


def test_active_model_selection_endpoint(client):
    # Select Keras active model
    res = client.post("/api/models/select", json={"model_id": "delhi_ctdi_keras"})
    assert res.status_code == 200
    assert res.json()["active_model"] == "delhi_ctdi_keras"

    h = client.get("/api/health").json()
    assert h["model_id"] == "delhi_ctdi_keras"
    assert "Keras" in h["framework"]

    # Select PyTorch active model
    res2 = client.post("/api/models/select", json={"model_id": "delhi_ctdi_original"})
    assert res2.status_code == 200
    assert res2.json()["active_model"] == "delhi_ctdi_original"

    h2 = client.get("/api/health").json()
    assert h2["model_id"] == "delhi_ctdi_original"
    assert h2["framework"] == "PyTorch"
