"""Model adapter wrapping Keras 3 Temporal Transformer for seamless application integration."""

import os
os.environ.setdefault("KERAS_BACKEND", "torch")

from typing import Optional, Union, Tuple, Dict, Any
import numpy as np
import keras
from keras import ops

# Reuse the existing linear baseline imputer directly (Requirement: zero duplicate implementations)
from src.models.baselines import LinearInterpolationImputer
from models.model_config import TemporalModelConfig
from models.keras_temporal_model import (
    build_keras_temporal_model,
    PositionalEncoding,
    TransformerEncoderBlock,
    StrictObservationLock,
)


class KerasTemporalModelAdapter:
    """
    Adapter providing a clean, framework-agnostic interface to the Keras 3 Temporal Model.
    
    Adheres strictly to the application's required interface:
        impute(x_obs, mask, context) -> x_imputed

    Expected input shapes:
        x_obs:   (batch, 24, 5)
        mask:    (batch, 24, 5)
        context: (batch, 24, 9)
    Output shape:
        x_imputed: (batch, 24, 5)
    """

    def __init__(
        self,
        model: Optional[keras.Model] = None,
        config: Optional[TemporalModelConfig] = None,
        weights_path: Optional[str] = None
    ):
        self.config = config or TemporalModelConfig()
        # Strictly reuse the existing LinearInterpolationImputer baseline
        self.linear_imputer = LinearInterpolationImputer()
        self._training_mode = False

        if model is not None:
            self.model = model
        elif weights_path is not None and os.path.exists(weights_path):
            self.model = keras.models.load_model(weights_path)
        else:
            self.model = build_keras_temporal_model(self.config)

    def eval(self) -> "KerasTemporalModelAdapter":
        """Sets evaluation mode (compatibility with PyTorch model interface)."""
        self._training_mode = False
        return self

    def train(self, mode: bool = True) -> "KerasTemporalModelAdapter":
        """Sets training mode (compatibility with PyTorch model interface)."""
        self._training_mode = mode
        return self

    def impute(
        self,
        x_obs: Any,
        mask: Any,
        context: Optional[Any] = None
    ) -> Any:
        """
        Primary imputation method required by application contract.

        Args:
            x_obs:   (B, 24, 5) observed pollutant values (numpy or torch.Tensor)
            mask:    (B, 24, 5) binary observation mask (1=observed, 0=missing)
            context: (B, 24, 9) optional meteorological/calendar context features

        Returns:
            x_imputed: (B, 24, 5) imputed array matching input type
        """
        x_obs_np, is_torch, device = self._to_numpy(x_obs)
        mask_np, _, _ = self._to_numpy(mask)

        # Validate input shapes
        if x_obs_np.ndim == 2:
            x_obs_np = np.expand_dims(x_obs_np, axis=0)
            mask_np = np.expand_dims(mask_np, axis=0)
            squeeze_batch = True
        elif x_obs_np.ndim == 3:
            squeeze_batch = False
        else:
            raise ValueError(f"Expected 2D or 3D tensor for x_obs, got shape {x_obs_np.shape}")

        B, T, F = x_obs_np.shape
        if T != self.config.window_size or F != self.config.num_features:
            raise ValueError(
                f"Expected x_obs of shape (B, {self.config.window_size}, {self.config.num_features}), got {x_obs_np.shape}"
            )

        # Prepare context
        if context is not None:
            ctx_np, _, _ = self._to_numpy(context)
            if ctx_np.ndim == 2:
                ctx_np = np.expand_dims(ctx_np, axis=0)
            if ctx_np.shape[1] != self.config.window_size or ctx_np.shape[2] != self.config.num_context:
                raise ValueError(
                    f"Expected context of shape (B, {self.config.window_size}, {self.config.num_context}), got {ctx_np.shape}"
                )
        else:
            # Default zero context if omitted
            ctx_np = np.zeros((B, self.config.window_size, self.config.num_context), dtype=np.float32)

        # 1. Compute linear temporal interpolation prior using EXISTING baseline imputer
        x_prior_np = self.linear_imputer.impute(x_obs_np, mask_np).astype(np.float32)

        # 2. Run Keras 3 model
        outputs = self.model(
            [x_obs_np.astype(np.float32), mask_np.astype(np.float32), x_prior_np, ctx_np.astype(np.float32)],
            training=self._training_mode
        )
        x_imputed_np = ops.convert_to_numpy(outputs[0])

        # 3. Strict preservation assertion (observed values must NEVER be altered)
        obs_idx = mask_np == 1.0
        if np.any(obs_idx):
            max_diff = np.max(np.abs(x_imputed_np[obs_idx] - x_obs_np[obs_idx]))
            if max_diff > 1e-5:
                raise AssertionError(f"Observed value corruption detected! Max diff: {max_diff}")

        # 4. Check no NaNs or Infs
        if np.isnan(x_imputed_np).any() or np.isinf(x_imputed_np).any():
            raise ValueError("Keras model produced NaN or Infinite values.")

        if squeeze_batch:
            x_imputed_np = np.squeeze(x_imputed_np, axis=0)

        # Return in format matching input
        if is_torch:
            import torch
            return torch.from_numpy(x_imputed_np).to(device)
        return x_imputed_np

    def __call__(
        self,
        x_obs: Any,
        mask: Any,
        context: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        """
        Legacy callable interface for backward-compatibility with code expecting:
            x_imputed, x_pred_raw = model(x_obs, mask)
        """
        x_obs_np, is_torch, device = self._to_numpy(x_obs)
        mask_np, _, _ = self._to_numpy(mask)

        # Handle concatenated (B, 24, 14) inputs where 9 context + 5 pollutants are bundled
        if x_obs_np.shape[-1] == self.config.num_context + self.config.num_features:
            ctx_np = x_obs_np[..., :self.config.num_context]
            pollutants_obs_np = x_obs_np[..., self.config.num_context:]
        elif x_obs_np.shape[-1] == self.config.num_features:
            pollutants_obs_np = x_obs_np
            if context is not None:
                ctx_np, _, _ = self._to_numpy(context)
            else:
                ctx_np = np.zeros((x_obs_np.shape[0], self.config.window_size, self.config.num_context), dtype=np.float32)
        else:
            raise ValueError(f"Unexpected channel dimension in x_obs: {x_obs_np.shape[-1]}")

        # Compute prior using existing baseline
        x_prior_np = self.linear_imputer.impute(pollutants_obs_np, mask_np).astype(np.float32)

        # Forward through Keras 3 model
        outputs = self.model(
            [pollutants_obs_np.astype(np.float32), mask_np.astype(np.float32), x_prior_np, ctx_np.astype(np.float32)],
            training=self._training_mode
        )
        x_imputed_np = ops.convert_to_numpy(outputs[0])
        x_raw_np = ops.convert_to_numpy(outputs[1])

        if is_torch:
            import torch
            return torch.from_numpy(x_imputed_np).to(device), torch.from_numpy(x_raw_np).to(device)
        return x_imputed_np, x_raw_np

    def save(self, filepath: str):
        """Saves Keras 3 model in native .keras format."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        self.model.save(filepath)

    @classmethod
    def load(cls, filepath: str) -> "KerasTemporalModelAdapter":
        """Loads native .keras model and wraps in adapter."""
        model = keras.models.load_model(filepath)
        return cls(model=model)

    def parameters(self):
        """Compatibility iterator returning trainable weights for PyTorch optimizers if needed."""
        return self.model.trainable_weights

    @staticmethod
    def _to_numpy(t: Any) -> Tuple[np.ndarray, bool, Optional[Any]]:
        """Converts tensor or array to numpy float32 while recording original type/device."""
        if hasattr(t, "detach"):
            # PyTorch tensor
            device = t.device
            return t.detach().cpu().numpy().astype(np.float32), True, device
        return np.asarray(t, dtype=np.float32), False, None
