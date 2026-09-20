"""Unit tests for FastAPI dataset-backed endpoints in api.py."""

import pytest
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["stations_loaded"] == 16
    assert data["windows_indexed"] > 0


def test_health_endpoint():
    response = client.get("/api/health?station=CW")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["station_code"] == "CW"
    assert data["total_stations"] == 16


def test_stations_catalog_endpoint():
    response = client.get("/api/stations")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["total"] == 16
    stations = data["stations"]
    assert len(stations) == 16

    codes = [s["code"] for s in stations]
    assert "CW" in codes
    assert "CB" in codes
    assert "TMN" in codes

    # Check structure of station item
    cw = next(s for s in stations if s["code"] == "CW")
    assert cw["name"] == "Central / Western"
    assert cw["type"] == "General"
    assert cw["station_id"] == 80
    assert abs(cw["lat"] - 22.2848) < 0.01


def test_metadata_endpoint():
    # CW
    res_cw = client.get("/api/metadata?station=CW")
    assert res_cw.status_code == 200
    data_cw = res_cw.json()
    assert data_cw["station_code"] == "CW"
    assert data_cw["station_type"] == "General"
    assert len(data_cw["channels"]) == 13

    # Roadside station CB
    res_cb = client.get("/api/metadata?station=CB")
    assert res_cb.status_code == 200
    data_cb = res_cb.json()
    assert data_cb["station_code"] == "CB"
    assert data_cb["station_type"] == "Roadside"
    assert data_cb["district"] == "Wan Chai"


def test_samples_endpoint_station_specificity():
    # Fetch window 1797 for Central / Western (CW)
    res_cw = client.get("/api/samples/1797?station=CW")
    assert res_cw.status_code == 200
    data_cw = res_cw.json()
    assert data_cw["station_code"] == "CW"
    assert data_cw["sample_idx"] == 1797
    assert data_cw["is_synthetic_preview"] is False
    assert len(data_cw["hours"]) == 24
    assert len(data_cw["timestamps"]) == 24
    assert "PM2.5" in data_cw["pollutants"]

    cw_pm25 = data_cw["pollutants"]["PM2.5"]["actual"]
    assert len(cw_pm25) == 24

    # Fetch window 1797 for Causeway Bay (CB)
    res_cb = client.get("/api/samples/1797?station=CB")
    assert res_cb.status_code == 200
    data_cb = res_cb.json()
    assert data_cb["station_code"] == "CB"
    cb_pm25 = data_cb["pollutants"]["PM2.5"]["actual"]
    assert len(cb_pm25) == 24

    # Crucial scientific check: CW and CB must have distinct real sensor measurements
    assert cw_pm25 != cb_pm25, "Station CW and CB returned identical data! Data must be station-specific."


def test_samples_endpoint_buffer_boundary():
    # Window 18390 falls within purged leakage buffer
    res = client.get("/api/samples/18390?station=CW")
    assert res.status_code == 200
    data = res.json()
    assert data["station_code"] == "CW"
    assert len(data["pollutants"]["PM2.5"]["actual"]) == 24
