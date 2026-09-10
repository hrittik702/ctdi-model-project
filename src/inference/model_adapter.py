"""Model adapter interface and PyTorch checkpoint wrapper for CTDI Temporal Model."""

from abc import ABC, abstractmethod
import os
from typing import Dict, Any, Tuple, Optional
import numpy as np
import torch

from src.models.temporal_transformer import CTDITemporalTransformer


class ImputationModel(ABC):
    """Abstract base class for imputation model serving adapters."""

    @abstractmethod
    def impute(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Executes inference.
        
        Args:
            x_obs: (B, 24, 5) normalized observed pollutant tensor
            mask: (B, 24, 5) binary observation mask (1=observed, 0=missing)
            context: (B, 24, 9) environmental context tensor
            
        Returns:
            x_imputed: (B, 24, 5) tensor with missing values replaced
            x_pred_raw: (B, 24, 5) raw predicted tensor before mask combination
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Returns model metadata including architecture, framework, and checkpoint path."""
        pass


class PyTorchTemporalModelAdapter(ImputationModel):
    """
    Adapter wrapping the genuinely trained PyTorch CTDI Temporal Transformer checkpoint.
    
    Architecture:
    - 24-channel input: [pollutants_obs (5), mask (5), linear_prior (5), context (9)]
    - 1x1 CNN + Local Conv1D feature mixing
    - Sinusoidal Positional Encoding
    - 3-Layer Pre-LN Temporal Transformer Encoder (d_model=128, nhead=8, dim_feedforward=256)
    - Post-CNN projection
    - Residual connection over linear prior: X_pred = X_prior + Delta
    - Observation lock: X_imputed = mask * X_obs + (1 - mask) * X_pred
    """

    def __init__(
        self,
        checkpoint_path: str = "checkpoints/delhi/best_temporal_transformer.pt",
        device: Optional[str] = None
    ):
        self.checkpoint_path = checkpoint_path
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Trained PyTorch checkpoint not found at: {checkpoint_path}")

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Instantiate verified architecture
        self.model = CTDITemporalTransformer(
            num_features=5,
            num_context=9,
            d_model=128,
            nhead=8,
            num_layers=3,
            dim_feedforward=256,
            dropout=0.1,
            window_size=24
        )

        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        state_dict = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint.state_dict()
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        self.param_count = sum(p.numel() for p in self.model.parameters())

    def impute(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Runs model inference in eval mode without gradients.
        """
        # Ensure 3D shape (B, 24, F)
        if x_obs.ndim == 2:
            x_obs = np.expand_dims(x_obs, axis=0)
            mask = np.expand_dims(mask, axis=0)
            if context is not None and context.ndim == 2:
                context = np.expand_dims(context, axis=0)

        t_obs = torch.tensor(x_obs, dtype=torch.float32, device=self.device)
        t_mask = torch.tensor(mask, dtype=torch.float32, device=self.device)
        t_ctx = torch.tensor(context, dtype=torch.float32, device=self.device) if context is not None else None

        with torch.no_grad():
            t_imputed, t_raw = self.model(t_obs, t_mask, t_ctx)

        x_imputed = t_imputed.cpu().numpy().astype(np.float32)
        x_pred_raw = t_raw.cpu().numpy().astype(np.float32)

        return x_imputed, x_pred_raw

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "CTDI Temporal Transformer",
            "version": "v1.0 (Delhi 15-Feature)",
            "framework": "PyTorch",
            "device": str(self.device),
            "parameters": self.param_count,
            "architecture": "1x1 Conv1D + Local Conv1D + 3-layer Pre-LN Transformer + Linear Prior Residual",
            "checkpoint": self.checkpoint_path,
            "num_features": 5,
            "num_context": 9,
            "d_model": 128,
            "num_layers": 3,
            "nhead": 8,
            "window_size": 24,
            "transfer_learning": False
        }
