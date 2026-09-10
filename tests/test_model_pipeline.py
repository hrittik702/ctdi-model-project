import pytest
import numpy as np
import torch

from src.models.temporal_transformer import CTDITemporalTransformer, torch_linear_interpolate_24h
from src.data.masking import generate_artificial_mask
from src.evaluation.metrics import compute_masked_mae, compute_masked_rmse, compute_masked_mape
from src.models.baselines import LinearInterpolationImputer, MeanImputer

def test_torch_linear_interpolate_shapes():
    B, T, F = 4, 24, 5
    p_obs = torch.randn(B, T, F)
    mask = torch.ones(B, T, F)
    # Mask out hour 10 to 14
    mask[:, 10:15, :] = 0.0
    p_obs = p_obs * mask
    
    interp = torch_linear_interpolate_24h(p_obs, mask)
    assert interp.shape == (B, T, F)
    assert not torch.isnan(interp).any()
    # Observed points must match original
    assert torch.allclose(interp[:, :10, :], p_obs[:, :10, :])

def test_transformer_forward():
    B, T, F_poll, F_ctx = 4, 24, 5, 9
    x_input = torch.randn(B, T, F_ctx + F_poll)
    mask = torch.ones(B, T, F_poll)
    mask[:, 5:10, :] = 0.0
    
    model = CTDITemporalTransformer(
        num_features=F_poll,
        num_context=F_ctx,
        d_model=64,
        nhead=4,
        num_layers=2,
        dim_feedforward=128,
        dropout=0.1,
        window_size=24
    )
    model.eval()
    
    with torch.no_grad():
        x_imp, x_raw = model(x_input, mask)
        
    assert x_imp.shape == (B, T, F_poll)
    assert x_raw.shape == (B, T, F_poll)
    assert not torch.isnan(x_imp).any()
    assert not torch.isnan(x_raw).any()

def test_metrics_evaluation():
    y_true = np.array([[[10.0, 20.0], [30.0, 40.0]]], dtype=np.float32)
    y_pred = np.array([[[12.0, 20.0], [33.0, 40.0]]], dtype=np.float32)
    m_eval = np.array([[[1.0, 0.0], [1.0, 0.0]]], dtype=np.float32)
    
    # At eval positions (1.0):
    # pos (0,0,0): |12-10| = 2
    # pos (0,1,0): |33-30| = 3
    # Mean error = (2 + 3) / 2 = 2.5
    mae = compute_masked_mae(y_pred, y_true, m_eval)
    assert np.isclose(mae, 2.5)

def test_baselines():
    x = np.ones((2, 24, 3)) * 50.0
    mask = np.ones((2, 24, 3))
    mask[:, 5:10, :] = 0.0
    x_masked = np.where(mask == 1.0, x, 0.0)
    
    lin = LinearInterpolationImputer()
    imp = lin.impute(x_masked, mask)
    assert imp.shape == (2, 24, 3)
    assert np.allclose(imp, 50.0)

def test_benchmark_transformer_forward(benchmark):
    model = CTDITemporalTransformer(num_features=5, num_context=9, d_model=128, nhead=8, num_layers=3, dim_feedforward=256, dropout=0.0, window_size=24)
    model.eval()
    x = torch.randn(32, 24, 14)
    m = torch.ones(32, 24, 5)
    
    with torch.no_grad():
        benchmark(model, x, m)
