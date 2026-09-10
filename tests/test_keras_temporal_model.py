import os
os.environ.setdefault("KERAS_BACKEND", "torch")

import pytest
import numpy as np
import torch
import keras

from models.model_config import TemporalModelConfig
from models.keras_temporal_model import build_keras_temporal_model
from models.model_adapter import KerasTemporalModelAdapter

from src.models.baselines import (
    MeanImputer,
    LinearInterpolationImputer,
    KNNPollutionImputer,
)
from src.models.temporal_transformer import SimpleMLPImputer
from src.evaluation.evaluate import evaluate_all_models


def test_1_dataset_loading():
    """Verify existing processed datasets load without issues."""
    windows_dir = "data/processed/24h_windows"
    assert os.path.exists(windows_dir), f"Directory {windows_dir} missing"
    
    train_x = np.load(os.path.join(windows_dir, "train_X.npy"))
    train_m = np.load(os.path.join(windows_dir, "train_mask.npy"))
    test_x = np.load(os.path.join(windows_dir, "test_X.npy"))
    test_m = np.load(os.path.join(windows_dir, "test_mask.npy"))
    
    assert train_x.shape[1:] == (24, 14)
    assert train_m.shape[1:] == (24, 5)
    assert test_x.shape[1:] == (24, 14)
    assert test_m.shape[1:] == (24, 5)


def test_2_baseline_models_run_independently():
    """Verify all existing baseline models continue to run without regression."""
    N, T, F = 10, 24, 5
    x = np.random.uniform(20.0, 150.0, (N, T, F)).astype(np.float32)
    m = (np.random.rand(N, T, F) > 0.2).astype(np.float32)
    x_masked = np.where(m == 1.0, x, 0.0)

    # 1. MeanImputer
    mean_imp = MeanImputer().fit(x, m)
    out_mean = mean_imp.impute(x_masked, m)
    assert out_mean.shape == (N, T, F)
    assert not np.isnan(out_mean).any()

    # 2. LinearInterpolationImputer
    lin_imp = LinearInterpolationImputer()
    out_lin = lin_imp.impute(x_masked, m)
    assert out_lin.shape == (N, T, F)
    assert not np.isnan(out_lin).any()

    # 3. KNNPollutionImputer
    knn_imp = KNNPollutionImputer(n_neighbors=2).fit(x_masked, m)
    out_knn = knn_imp.impute(x_masked, m)
    assert out_knn.shape == (N, T, F)
    assert not np.isnan(out_knn).any()

    # 4. SimpleMLPImputer
    mlp = SimpleMLPImputer(num_features=F, window_size=T)
    t_obs = torch.tensor(x_masked, dtype=torch.float32)
    t_m = torch.tensor(m, dtype=torch.float32)
    mlp_imp, mlp_raw = mlp(t_obs, t_m)
    assert mlp_imp.shape == (N, T, F)
    assert not torch.isnan(mlp_imp).any()


def test_3_keras_adapter_input_output_shapes():
    """Verify required interface: impute(x_obs, mask, context) -> (B, 24, 5)."""
    adapter = KerasTemporalModelAdapter()
    
    B = 8
    x_obs = np.random.uniform(10.0, 100.0, (B, 24, 5)).astype(np.float32)
    mask = np.ones((B, 24, 5), dtype=np.float32)
    mask[:, 6:12, :] = 0.0
    x_obs_masked = np.where(mask == 1.0, x_obs, 0.0)
    context = np.random.randn(B, 24, 9).astype(np.float32)

    # Call with context
    x_imputed = adapter.impute(x_obs_masked, mask, context)
    assert isinstance(x_imputed, np.ndarray)
    assert x_imputed.shape == (B, 24, 5)

    # Call with context=None (graceful default)
    x_imputed_no_ctx = adapter.impute(x_obs_masked, mask, context=None)
    assert x_imputed_no_ctx.shape == (B, 24, 5)


def test_4_strict_preservation_and_no_nans():
    """Verify observed values are 100% unchanged, missing get predictions, no NaNs/Infs."""
    adapter = KerasTemporalModelAdapter()

    B = 4
    x_obs = np.random.uniform(15.0, 200.0, (B, 24, 5)).astype(np.float32)
    mask = np.ones((B, 24, 5), dtype=np.float32)
    # Mask out hour 10-18 for all channels
    mask[:, 10:18, :] = 0.0
    x_masked = np.where(mask == 1.0, x_obs, 0.0)
    context = np.random.randn(B, 24, 9).astype(np.float32)

    x_imputed = adapter.impute(x_masked, mask, context)

    # 1. Observed values MUST be exactly identical
    obs_indices = mask == 1.0
    assert np.allclose(x_imputed[obs_indices], x_obs[obs_indices], atol=1e-5), \
        "Observed sensor readings were altered by the model!"

    # 2. Missing positions MUST receive non-zero / updated values
    missing_indices = mask == 0.0
    assert not np.all(x_imputed[missing_indices] == 0.0), \
        "Missing positions failed to receive imputed values!"

    # 3. Zero NaN or Infinite values
    assert not np.isnan(x_imputed).any(), "NaN detected in imputation output!"
    assert not np.isinf(x_imputed).any(), "Inf detected in imputation output!"


def test_5_native_keras_serialization():
    """Verify model saves to .keras and restores cleanly without warnings or degradation."""
    temp_path = "tests/test_checkpoint.keras"
    adapter = KerasTemporalModelAdapter()

    B = 2
    x_obs = np.random.randn(B, 24, 5).astype(np.float32)
    mask = np.ones((B, 24, 5), dtype=np.float32)
    mask[:, 5:10, :] = 0.0
    context = np.random.randn(B, 24, 9).astype(np.float32)

    pred_before = adapter.impute(x_obs, mask, context)

    # Save to .keras
    adapter.save(temp_path)
    assert os.path.exists(temp_path)

    # Reload through adapter classmethod
    loaded_adapter = KerasTemporalModelAdapter.load(temp_path)
    pred_after = loaded_adapter.impute(x_obs, mask, context)

    assert np.allclose(pred_before, pred_after, atol=1e-5), \
        "Output differed between saved and loaded Keras model!"

    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_6_model_training_step():
    """Verify model can execute forward + backward training step and update weights."""
    model = build_keras_temporal_model(TemporalModelConfig())
    optimizer = keras.optimizers.AdamW(learning_rate=1e-3)

    B = 8
    x_obs = np.random.randn(B, 24, 5).astype(np.float32)
    mask = np.ones((B, 24, 5), dtype=np.float32)
    mask[:, 10:14, :] = 0.0
    prior = x_obs.copy()
    context = np.random.randn(B, 24, 9).astype(np.float32)
    target = x_obs.copy() + 0.5

    # Compile with Huber / Smooth L1 loss
    model.compile(
        optimizer=optimizer,
        loss={"x_imputed": "huber", "pred_raw": "huber"},
        loss_weights={"x_imputed": 1.0, "pred_raw": 0.5}
    )

    # Fit for 1 epoch on mini-batch
    history = model.fit(
        x=[x_obs, mask, prior, context],
        y=[target, target],
        epochs=1,
        batch_size=B,
        verbose=0
    )
    assert "loss" in history.history
    assert history.history["loss"][0] > 0


def test_7_torch_tensor_compatibility():
    """Verify PyTorch tensors pass through adapter cleanly and return torch.Tensors."""
    adapter = KerasTemporalModelAdapter()
    
    B = 4
    t_obs = torch.randn(B, 24, 5)
    t_mask = torch.ones(B, 24, 5)
    t_mask[:, 12:18, :] = 0.0
    t_ctx = torch.randn(B, 24, 9)

    t_imp = adapter.impute(t_obs, t_mask, t_ctx)
    assert isinstance(t_imp, torch.Tensor)
    assert t_imp.shape == (B, 24, 5)
    assert not torch.isnan(t_imp).any()

    # Legacy call: model(t_obs, t_mask)
    t_bundled = torch.cat([t_ctx, t_obs], dim=-1)  # (B, 24, 14)
    t_imp2, t_raw = adapter(t_bundled, t_mask)
    assert isinstance(t_imp2, torch.Tensor)
    assert t_imp2.shape == (B, 24, 5)


def test_8_evaluation_pipeline_integration():
    """Verify existing evaluate_all_models pipeline works with the Keras adapter."""
    N, T, F = 10, 24, 5
    x_test_true = np.random.uniform(30.0, 120.0, (N, T, F)).astype(np.float32)
    m_test_art = np.ones((N, T, F), dtype=np.float32)
    m_test_art[:, 8:14, :] = 0.0
    eval_mask = (1.0 - m_test_art).astype(np.float32)
    x_test_obs = np.where(m_test_art == 1.0, x_test_true, 0.0)

    feature_names = ["PM2.5", "PM10", "NO2", "SO2", "O3"]
    linear_imputer = LinearInterpolationImputer()
    adapter = KerasTemporalModelAdapter()

    summary_df, imputations = evaluate_all_models(
        x_test_true=x_test_true,
        x_test_obs=x_test_obs,
        m_test_art=m_test_art,
        eval_mask=eval_mask,
        feature_names=feature_names,
        linear_imputer=linear_imputer,
        transformer_model=adapter
    )

    assert "Temporal_Transformer" in imputations
    assert "Linear_Interpolation" in imputations
    assert imputations["Temporal_Transformer"].shape == (N, T, F)
    assert len(summary_df) >= 2
