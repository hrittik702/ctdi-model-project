"""Unit tests for Environmental Context Builder and SLM Context Encoder scaffolding."""

import numpy as np
import pandas as pd
import pytest
import torch

from src.context import (
    CHANNEL_NAMES,
    EnvironmentalContextBuilder,
    MockSLMContextEncoder,
    describe_temperature,
    describe_humidity,
    describe_rainfall,
    describe_wind,
    describe_traffic,
    describe_missingness,
    serialize_context,
)


def test_descriptors():
    """Test qualitative atmospheric descriptor functions with HKO thresholds."""
    # Temperature
    assert describe_temperature(6.5) == "intensely cold"
    assert describe_temperature(11.0) == "cold"
    assert describe_temperature(15.0) == "cool"
    assert describe_temperature(21.0) == "mild"
    assert describe_temperature(26.0) == "warm"
    assert describe_temperature(30.0) == "hot"
    assert describe_temperature(34.5) == "very hot"

    # Humidity
    assert describe_humidity(35.0) == "very dry"
    assert describe_humidity(55.0) == "dry"
    assert describe_humidity(70.0) == "comfortable"
    assert describe_humidity(85.0) == "humid"
    assert describe_humidity(95.0) == "very humid"

    # Rainfall
    assert describe_rainfall(0.0, 0.0) == "no rain"
    assert describe_rainfall(4.0, 2.0) == "light rain"
    assert describe_rainfall(20.0, 8.0) == "moderate rain"
    assert describe_rainfall(45.0, 18.0) == "heavy rain"
    assert describe_rainfall(80.0, 35.0) == "torrential downpour"

    # Wind
    speed_cat, dir_cat, regime = describe_wind(4.0, 45.0)
    assert speed_cat == "moderate breeze"
    assert dir_cat == "northeasterly"
    assert "continental outflow" in regime

    speed_cat_m, dir_cat_m, regime_m = describe_wind(2.5, 180.0)
    assert speed_cat_m == "light breeze"
    assert dir_cat_m == "southerly"
    assert "maritime inflow" in regime_m

    # Traffic
    s_cat, c_cat = describe_traffic(32.0, 0.35)
    assert s_cat == "heavy corridor congestion"
    assert c_cat == "severe saturation"

    s_cat_f, c_cat_f = describe_traffic(68.0, 0.05)
    assert s_cat_f == "smooth free-flow traffic"
    assert c_cat_f == "low saturation"


def test_missingness_description():
    """Test missingness pattern characterization."""
    mask = np.ones((24, 13), dtype=np.int64)
    res = describe_missingness(mask)
    assert res["missing_cells"] == 0
    assert res["severity"] == "none"

    # Create block missingness on NO2 (idx 2)
    mask[5:15, 2] = 0
    res_block = describe_missingness(mask)
    assert res_block["missing_cells"] == 10
    assert res_block["severity"] == "minor"
    assert "gap" in res_block["pattern"] or "dropouts" in res_block["pattern"]
    assert res_block["affected_pollutants"] == [("no2", 10)]


def test_context_builder_with_real_window():
    """Test EnvironmentalContextBuilder on actual dataset parquet windows."""
    df_win = pd.read_parquet("data/interim/windows/24h_windows.parquet")
    df_mask = pd.read_parquet("data/interim/windows/missingness_masks.parquet")
    df_meta = pd.read_parquet("data/interim/windows/window_metadata.parquet")

    builder = EnvironmentalContextBuilder()

    # Pass Series directly
    row_w = df_win.iloc[0]
    row_m = df_mask.iloc[0]
    meta = df_meta.iloc[0].to_dict()

    ctx = builder.build_context(row_w, row_m, meta)
    assert "temporal" in ctx
    assert "spatial" in ctx
    assert "meteorological" in ctx
    assert "traffic" in ctx
    assert "missingness" in ctx

    # Test narrative prompt
    prompt_narrative = builder.build_prompt(row_w, row_m, meta, format_type="narrative")
    assert "[ENVIRONMENTAL CONTEXT: HONG KONG]" in prompt_narrative
    assert "Sham Shui Po" in prompt_narrative or "SHAM SHUI PO" in prompt_narrative
    assert "Meteorology:" in prompt_narrative

    # Test key-value prompt
    prompt_kv = builder.build_prompt(row_w, row_m, meta, format_type="key_value")
    assert "STATION:" in prompt_kv
    assert "MET:" in prompt_kv

    # Test json prompt
    prompt_json = builder.build_prompt(row_w, row_m, meta, format_type="json")
    assert '"meteorological"' in prompt_json


def test_information_leakage_audit():
    """Test information leakage prevention audit."""
    w_data = np.zeros((24, 13))
    w_data[:, 0] = 99.45  # PM2.5 target values
    eval_mask = np.ones((24, 13))
    eval_mask[10:20, 0] = 0  # hide hours 10..19

    clean_prompt = "Station: Central. Mild weather, no rain, smooth traffic."
    # Clean prompt should pass audit
    assert EnvironmentalContextBuilder.audit_leakage(w_data, eval_mask, clean_prompt) is True

    leaky_prompt = "Station: Central. Hidden value is 99.45 ug/m3."
    with pytest.raises(AssertionError, match="LEAKAGE DETECTED"):
        EnvironmentalContextBuilder.audit_leakage(w_data, eval_mask, leaky_prompt)


def test_mock_slm_encoder_forward():
    """Test Mock SLM context encoder pooling and projection dimensions."""
    prompts = [
        "Environmental Context: Station Eastern, mild weather.",
        "Environmental Context: Station Mong Kok, heavy congestion.",
    ]

    for pool in ["mean", "last_token", "attention_pool"]:
        encoder = MockSLMContextEncoder(d_slm=896, d_diff=128, pooling_strategy=pool)
        z_C = encoder(prompts)
        assert z_C.shape == (2, 128)
        assert z_C.dtype == torch.float32

        # Verify gradients flow only to projection layer
        loss = z_C.sum()
        loss.backward()
        assert encoder.projection.weight.grad is not None
