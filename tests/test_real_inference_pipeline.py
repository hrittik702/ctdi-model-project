"""Comprehensive automated test suite for CTDI Real Inference Pipeline (All 12 Required Tests)."""

import os
import io
import pytest
import numpy as np
import pandas as pd
import torch

from src.inference.validation import (
    load_and_validate_csv,
    extract_24h_windows,
    ValidationError
)
from src.inference.preprocessing_adapter import PreprocessingAdapter
from src.inference.model_adapter import PyTorchTemporalModelAdapter
from src.inference.model_loader import get_model_instance
from src.inference.imputation_service import ImputationService
from src.inference.postprocessing import InferenceIntegrityError


def make_synthetic_24h_df(
    start_time: str = "2025-01-01 00:00:00",
    base_val: float = 100.0,
    with_weather: bool = True
) -> pd.DataFrame:
    """Helper creating a valid 24-hour hourly DataFrame."""
    dates = pd.date_range(start=start_time, periods=24, freq="1h")
    df = pd.DataFrame({
        "timestamp": dates,
        "PM2.5": [base_val + i * 2.0 for i in range(24)],
        "PM10": [base_val * 1.5 + i * 3.0 for i in range(24)],
        "NO2": [40.0 + i * 0.5 for i in range(24)],
        "SO2": [20.0 + i * 0.2 for i in range(24)],
        "O3": [50.0 + i * 1.0 for i in range(24)]
    })
    if with_weather:
        df["Temp_2m_C"] = [25.0 for _ in range(24)]
        df["Humidity_Percent"] = [60.0 for _ in range(24)]
        df["Wind_Speed_10m_kmh"] = [10.0 for _ in range(24)]
        df["Wind_Dir_10m"] = [180.0 for _ in range(24)]
        df["Precipitation_mm"] = [0.0 for _ in range(24)]
    return df


def test_1_complete_24h_data_preservation():
    """TEST 1: Complete 24-hour data with no missing values -> output == input."""
    service = ImputationService()
    df = make_synthetic_24h_df(base_val=80.0)
    result = service.process_csv(df, filename="complete_24h.csv")

    assert result["status"] == "success"
    assert result["statistics"]["missing_values"] == 0
    assert result["statistics"]["imputed_values"] == 0

    # Every pollutant in imputed should equal observed
    for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
        obs = np.array(result["data"]["observed"][p], dtype=float)
        imp = np.array(result["data"]["imputed"][p], dtype=float)
        assert np.allclose(obs, imp, atol=1e-4), f"Complete data altered for {p}!"


def test_2_single_missing_value():
    """TEST 2: One missing value -> observed values unchanged, missing value replaced."""
    service = ImputationService()
    df = make_synthetic_24h_df(base_val=90.0)
    orig_pm25_h12 = df.loc[12, "PM2.5"]
    df.loc[12, "PM2.5"] = np.nan  # Single missing value

    result = service.process_csv(df, filename="single_missing.csv")
    assert result["statistics"]["missing_values"] == 1
    assert result["statistics"]["imputed_values"] == 1

    imp_pm25 = result["data"]["imputed"]["PM2.5"]
    obs_pm25 = result["data"]["observed"]["PM2.5"]

    # Missing hour 12 must be replaced with valid number (not None, not NaN)
    assert imp_pm25[12] is not None
    assert not np.isnan(imp_pm25[12])
    assert obs_pm25[12] is None  # Observed list reflects null

    # All other 23 hours must be strictly identical
    for h in range(24):
        if h != 12:
            assert abs(imp_pm25[h] - obs_pm25[h]) < 1e-4


def test_3_four_consecutive_missing_hours():
    """TEST 3: Four consecutive missing hours -> all missing positions imputed."""
    service = ImputationService()
    df = make_synthetic_24h_df(base_val=110.0)
    df.loc[10:13, "PM2.5"] = np.nan

    result = service.process_csv(df, filename="four_hours.csv")
    assert result["statistics"]["missing_values"] == 4

    imp_pm25 = result["data"]["imputed"]["PM2.5"]
    for h in range(10, 14):
        assert imp_pm25[h] is not None
        assert not np.isnan(imp_pm25[h])
        assert imp_pm25[h] > 0.0


def test_4_independent_pollutant_missingness():
    """TEST 4: Different pollutants missing independently -> per-feature mask works."""
    service = ImputationService()
    df = make_synthetic_24h_df()
    # Missing at different hours for different pollutants
    df.loc[4, "PM2.5"] = np.nan
    df.loc[8, "PM10"] = np.nan
    df.loc[15, "NO2"] = np.nan

    result = service.process_csv(df)
    assert result["data"]["mask"]["PM2.5"][4] == 0
    assert result["data"]["mask"]["PM2.5"][8] == 1
    assert result["data"]["mask"]["PM10"][8] == 0
    assert result["data"]["mask"]["NO2"][15] == 0

    assert result["data"]["imputed"]["PM2.5"][4] is not None
    assert result["data"]["imputed"]["PM10"][8] is not None
    assert result["data"]["imputed"]["NO2"][15] is not None


def test_5_all_pollutants_missing_at_one_timestamp():
    """TEST 5: All five pollutants missing at one timestamp -> correct mask."""
    service = ImputationService()
    df = make_synthetic_24h_df()
    for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
        df.loc[7, p] = np.nan

    result = service.process_csv(df)
    for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
        assert result["data"]["mask"][p][7] == 0
        assert result["data"]["imputed"][p][7] is not None
        assert not np.isnan(result["data"]["imputed"][p][7])


def test_6_missing_values_at_beginning_of_window():
    """TEST 6: Missing values at beginning of window (hours 0-3) -> boundary interpolation handled."""
    service = ImputationService()
    df = make_synthetic_24h_df()
    df.loc[0:3, "PM2.5"] = np.nan

    result = service.process_csv(df)
    imp_pm25 = result["data"]["imputed"]["PM2.5"]
    for h in range(4):
        assert imp_pm25[h] is not None
        assert not np.isnan(imp_pm25[h])


def test_7_missing_values_at_end_of_window():
    """TEST 7: Missing values at end of window (hours 20-23) -> boundary interpolation handled."""
    service = ImputationService()
    df = make_synthetic_24h_df()
    df.loc[20:23, "PM10"] = np.nan

    result = service.process_csv(df)
    imp_pm10 = result["data"]["imputed"]["PM10"]
    for h in range(20, 24):
        assert imp_pm10[h] is not None
        assert not np.isnan(imp_pm10[h])


def test_8_no_context_supplied_fallback():
    """TEST 8: No weather context supplied -> graceful fallback to training norm stats."""
    service = ImputationService()
    df = make_synthetic_24h_df(with_weather=False)
    df.loc[5:7, "PM2.5"] = np.nan

    result = service.process_csv(df)
    assert result["status"] == "success"
    # Should report fallback weather features used
    assert len(result["metadata"]["fallback_meteorology_used"]) == 5
    assert result["data"]["imputed"]["PM2.5"][5] is not None


def test_9_observed_value_preservation_strict():
    """TEST 9: Observed-value preservation -> max absolute diff on observed == 0."""
    service = ImputationService()
    df = make_synthetic_24h_df(base_val=135.5)
    # Mask random hours
    df.loc[[2, 6, 14, 18], "PM2.5"] = np.nan

    result = service.process_csv(df)
    for p in ["PM2.5", "PM10", "NO2", "SO2", "O3"]:
        obs = result["data"]["observed"][p]
        imp = result["data"]["imputed"][p]
        mask = result["data"]["mask"][p]
        for t in range(24):
            if mask[t] == 1:
                assert obs[t] == imp[t], f"Observed value mismatch at {p} t={t}: {obs[t]} vs {imp[t]}"


def test_10_model_output_shape():
    """TEST 10: Model output shape -> (B, 24, 5)."""
    model = get_model_instance()
    B = 2
    x_obs = np.random.randn(B, 24, 5).astype(np.float32)
    mask = np.ones((B, 24, 5), dtype=np.float32)
    mask[:, 5:10, :] = 0.0
    context = np.random.randn(B, 24, 9).astype(np.float32)

    x_imp, x_raw = model.impute(x_obs, mask, context)
    assert x_imp.shape == (B, 24, 5)
    assert x_raw.shape == (B, 24, 5)
    assert not np.isnan(x_imp).any()


def test_11_csv_round_trip():
    """TEST 11: CSV round-trip -> upload -> inference -> export -> reload preserves data."""
    service = ImputationService()
    df = make_synthetic_24h_df(base_val=75.0)
    df.loc[8:11, "PM2.5"] = np.nan

    # 1. Inference
    result = service.process_csv(df, filename="round_trip.csv")
    imputed_df = result["imputed_df"]

    # 2. Export to CSV string
    csv_buffer = io.StringIO()
    imputed_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # 3. Reload CSV
    reloaded_df = pd.read_csv(csv_buffer)
    assert len(reloaded_df) == 24
    assert "timestamp" in reloaded_df.columns
    assert "PM2.5_imputed" in reloaded_df.columns
    assert not reloaded_df["PM2.5_imputed"].isna().any()


def test_12_invalid_input_rejection():
    """TEST 12: Invalid input -> useful validation error."""
    service = ImputationService()

    # 1. Less than 24 hours
    short_df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=10, freq="1h"),
        "PM2.5": [10.0] * 10,
        "PM10": [20.0] * 10,
        "NO2": [30.0] * 10,
        "SO2": [40.0] * 10,
        "O3": [50.0] * 10
    })
    with pytest.raises(ValidationError, match="Model requires at least 24"):
        service.process_csv(short_df)

    # 2. Missing pollutant column
    missing_col_df = short_df.copy()
    missing_col_df = missing_col_df.drop(columns=["O3"])
    with pytest.raises(ValidationError, match="Missing required pollutant"):
        service.process_csv(missing_col_df)

    # 3. Completely empty CSV
    with pytest.raises(ValidationError, match="completely empty"):
        service.process_csv(pd.DataFrame())


def test_13_fastapi_endpoints_upload_and_preview():
    """TEST 13: End-to-end FastAPI integration testing for /api/impute/preview and /api/impute/upload."""
    from fastapi.testclient import TestClient
    from api import app

    client = TestClient(app)

    # Prepare sample CSV
    df = make_synthetic_24h_df(base_val=105.0)
    df.loc[6:9, "PM2.5"] = np.nan
    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    # 1. Test preview
    res_prev = client.post(
        "/api/impute/preview",
        files={"file": ("delhi_sensor.csv", csv_bytes.getvalue(), "text/csv")}
    )
    assert res_prev.status_code == 200
    prev_json = res_prev.json()
    assert prev_json["status"] == "success"
    assert prev_json["summary"]["total_missing"] == 4

    # 2. Test upload and inference
    res_upload = client.post(
        "/api/impute/upload",
        files={"file": ("delhi_sensor.csv", csv_bytes.getvalue(), "text/csv")}
    )
    assert res_upload.status_code == 200
    upload_json = res_upload.json()
    assert upload_json["status"] == "success"
    assert upload_json["model"]["name"] == "CTDI Temporal Transformer"
    assert upload_json["statistics"]["missing_values"] == 4
    assert upload_json["statistics"]["imputed_values"] == 4
    assert upload_json["statistics"]["observed_preserved_pct"] == 100.0
    assert upload_json["statistics"]["processing_time_ms"]["total_ms"] > 0
    # Imputed PM2.5 at hour 6 must be non-null and positive
    assert upload_json["data"]["imputed"]["PM2.5"][6] is not None
    assert upload_json["data"]["imputed"]["PM2.5"][6] > 0.0
    # Observed PM2.5 at hour 6 is None
    assert upload_json["data"]["observed"]["PM2.5"][6] is None
    # Observed PM2.5 at hour 0 is identical
    assert upload_json["data"]["observed"]["PM2.5"][0] == upload_json["data"]["imputed"]["PM2.5"][0]
