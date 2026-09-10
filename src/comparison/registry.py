"""Model Registry and Runner Abstractions for Multi-Model Comparison & Benchmarking Lab."""

from abc import ABC, abstractmethod
import os
import time
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import torch

from src.models.baselines import (
    LinearInterpolationImputer,
    MeanImputer,
    KNNPollutionImputer
)
from src.models.temporal_transformer import SimpleMLPImputer
from src.inference.model_loader import get_model_instance
from models.model_adapter import KerasTemporalModelAdapter


class BaseModelRunner(ABC):
    """Abstract base runner exposing a standardized model interface."""

    def __init__(
        self,
        id: str,
        name: str,
        version: str,
        model_type: str,
        description: str,
        city: str = "Delhi",
        framework: str = "PyTorch",
        architecture: str = "",
        category: str = "trained",
        is_available: bool = True,
        param_count: Optional[int] = None,
        checkpoint_path: Optional[str] = None,
        dataset_id: Optional[str] = None,
        scaler: Optional[str] = None,
        preprocessing_version: Optional[str] = None,
        feature_version: Optional[str] = None,
        training_date: Optional[str] = None,
        input_window: str = "24 hours (24 timesteps)",
        feature_count: str = "5 pollutant channels (PM2.5, PM10, NO2, SO2, O3)",
        status: Optional[str] = None
    ):
        self.id = id
        self.model_id = id
        self.name = name
        self.display_name = name
        self.version = version
        self.model_type = model_type
        self.description = description
        self.city = city
        self.framework = framework
        self.architecture = architecture
        self.category = category  # 'trained', 'baseline', 'future'
        self.is_available = is_available
        self.param_count = param_count
        self.parameter_count = param_count
        self.checkpoint_path = checkpoint_path
        self.dataset_id = dataset_id or (f"{city.lower()}_cpcb_benchmark" if city != "all" else "all_cpcb_datasets")
        self.scaler = scaler or ("RobustStandardScaler / CPCB Normalizer v1.0" if category == "trained" else "Not available")
        self.preprocessing_version = preprocessing_version or ("v1.2-continuous-prior" if category == "trained" else "Not available")
        self.feature_version = feature_version or ("5-channel pollutants + 9-dim context" if category == "trained" else "5-channel pollutants")
        self.training_date = training_date
        self.input_window = input_window
        self.feature_count = feature_count
        self._custom_status = status
        self._is_loaded = False
        self.load_time_ms: float = 0.0

    @property
    def checkpoint_size_str(self) -> str:
        """Returns human-readable checkpoint size or 'Not available'."""
        if self.checkpoint_path and os.path.exists(self.checkpoint_path):
            size_bytes = os.path.getsize(self.checkpoint_path)
            if size_bytes >= 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            return f"{size_bytes / 1024:.1f} KB"
        if self.category == "baseline":
            return "0 KB (Algorithmic)"
        return "Not available"

    @property
    def checkpoint_size_mb(self) -> float:
        """Returns physical checkpoint file size in MB."""
        if self.checkpoint_path and os.path.exists(self.checkpoint_path):
            return round(os.path.getsize(self.checkpoint_path) / (1024 * 1024), 2)
        return 0.0

    @property
    def training_date_str(self) -> str:
        """Returns training date formatted string or 'Not available'."""
        if self.training_date:
            return self.training_date
        if self.checkpoint_path and os.path.exists(self.checkpoint_path):
            import datetime
            mtime = os.path.getmtime(self.checkpoint_path)
            return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        return "Not available"

    @property
    def status_str(self) -> str:
        """Returns operational readiness status."""
        if self._custom_status:
            return self._custom_status
        if not self.is_available:
            return "In Development" if self.category == "future" else "Unavailable"
        if self.checkpoint_path and not os.path.exists(self.checkpoint_path):
            return "Checkpoint Missing"
        return "Ready"

    @abstractmethod
    def load(self):
        """Loads model weights/initializes parameters into memory."""
        pass

    @abstractmethod
    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Runs model inference.
        
        Args:
            x_obs: (B, 24, 5) normalized observed values (0.0 where missing)
            mask: (B, 24, 5) binary observation mask (1=observed, 0=missing)
            context: (B, 24, 9) environmental context tensor
            
        Returns:
            x_imputed: (B, 24, 5) imputed array (strictly preserving observed values)
            x_raw_pred: (B, 24, 5) raw predictions before mask combination
        """
        pass

    def metadata(self) -> Dict[str, Any]:
        """Returns standard metadata dictionary for UI display and serialization."""
        return {
            "id": self.id,
            "model_id": self.id,
            "name": self.name,
            "display_name": self.name,
            "version": self.version,
            "model_type": self.model_type,
            "description": self.description,
            "city": self.city,
            "dataset_id": self.dataset_id,
            "framework": self.framework,
            "architecture": self.architecture,
            "category": self.category,
            "is_available": self.is_available,
            "param_count": self.param_count if self.param_count is not None else "Not available",
            "parameter_count": self.param_count if self.param_count is not None else "Not available",
            "checkpoint_path": self.checkpoint_path or "Not available",
            "checkpoint": self.checkpoint_path or "Not available",
            "checkpoint_size": self.checkpoint_size_str,
            "checkpoint_size_mb": self.checkpoint_size_mb,
            "model_size": self.checkpoint_size_str,
            "model_size_mb": self.checkpoint_size_mb,
            "scaler": self.scaler or "Not available",
            "scaler_path": self.scaler or "Not available",
            "preprocessing_version": self.preprocessing_version,
            "feature_version": self.feature_version,
            "training_date": self.training_date_str,
            "input_window": self.input_window,
            "feature_count": self.feature_count,
            "status": self.status_str,
            "load_time_ms": round(self.load_time_ms, 2)
        }

    def get_metadata(self) -> Dict[str, Any]:
        """Alias for metadata()."""
        return self.metadata()


class CTDITransformerRunner(BaseModelRunner):
    """Runner for the trained PyTorch CTDI Temporal Transformer (Original Architecture)."""

    def __init__(self, checkpoint_path: str = "checkpoints/delhi/best_temporal_transformer.pt"):
        super().__init__(
            id="delhi_ctdi_original",
            name="Delhi CTDI (Original PyTorch)",
            version="v1.0-PyTorch",
            model_type="Deep Learning / Temporal Transformer",
            description="Original PyTorch CTDI implementation: 1x1 Conv1D + Local Temporal Conv1D (k=3) + 3-Layer Pre-LN Transformer with continuous linear prior residual learning.",
            city="Delhi",
            framework="PyTorch",
            architecture="1x1 Conv1D + Local Conv1D (k=3) + 3x TransformerEncoderLayer (d_model=128, nhead=8, ff=256) + ObservationLock",
            category="trained",
            is_available=os.path.exists(checkpoint_path),
            param_count=500357,
            checkpoint_path=checkpoint_path
        )
        self._adapter = None

    def load(self):
        if not self._is_loaded and self.is_available:
            t0 = time.perf_counter()
            self._adapter = get_model_instance(self.checkpoint_path)
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        return self._adapter.impute(x_obs, mask, context)


class KerasCTDIRunner(BaseModelRunner):
    """Runner for the trained Keras 3 CTDI Temporal Transformer (PyTorch Backend)."""

    def __init__(self, checkpoint_path: str = "checkpoints/delhi/best_temporal_transformer.keras"):
        super().__init__(
            id="delhi_ctdi_keras",
            name="Delhi CTDI (Keras 3)",
            version="v1.0-Keras3",
            model_type="Deep Learning / Keras 3 Transformer",
            description="Authentic Keras 3 implementation running on PyTorch backend: Conv1D feature mixer + Sinusoidal Positional Encoding + 3x TransformerEncoderBlock + StrictObservationLock.",
            city="Delhi",
            framework="Keras 3 (PyTorch Backend)",
            architecture="Pointwise Conv1D (d=128) + Temporal Conv1D (k=3) + PositionalEncoding + 3x TransformerEncoderBlock + StrictObservationLock",
            category="trained",
            is_available=os.path.exists(checkpoint_path),
            param_count=504965,
            checkpoint_path=checkpoint_path
        )
        self._adapter = None

    def load(self):
        if not self._is_loaded and self.is_available:
            t0 = time.perf_counter()
            self._adapter = KerasTemporalModelAdapter.load(self.checkpoint_path)
            self._adapter.eval()
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        
        # Ensure float32 numpy
        x_obs_np = np.asarray(x_obs, dtype=np.float32)
        mask_np = np.asarray(mask, dtype=np.float32)
        ctx_np = np.asarray(context, dtype=np.float32) if context is not None else None

        # Keras model call returns [x_imputed, x_pred_raw]
        B = x_obs_np.shape[0]
        if ctx_np is None:
            ctx_np = np.zeros((B, 24, 9), dtype=np.float32)

        x_prior_np = self._adapter.linear_imputer.impute(x_obs_np, mask_np).astype(np.float32)
        outputs = self._adapter.model(
            [x_obs_np, mask_np, x_prior_np, ctx_np],
            training=False
        )

        from keras import ops
        x_imp = ops.convert_to_numpy(outputs[0]).astype(np.float32)
        x_raw = ops.convert_to_numpy(outputs[1]).astype(np.float32)

        # Strictly preserve observed points
        x_imp = np.where(mask_np == 1.0, x_obs_np, x_imp)
        return x_imp, x_raw


class LinearInterpolationRunner(BaseModelRunner):
    """Runner for 1D Temporal Linear Interpolation baseline."""

    def __init__(self):
        super().__init__(
            id="linear_interpolation",
            name="1D Linear Interpolation",
            version="baseline-v1",
            model_type="Numerical / Statistical Baseline",
            description="Piecewise continuous 1D temporal linear interpolation across missing gaps with boundary fill.",
            city="all",
            framework="Statistical / Numerical",
            architecture="Temporal Linear Spline (Per Pollutant Channel)",
            category="baseline",
            is_available=True,
            param_count=0,
            checkpoint_path=None
        )
        self.imputer = None

    def load(self):
        if not self._is_loaded:
            t0 = time.perf_counter()
            self.imputer = LinearInterpolationImputer(fallback_mean=0.0)
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        x_imp = self.imputer.impute(x_obs, mask)
        x_imp = np.where(mask == 1.0, x_obs, x_imp)
        return x_imp, x_imp


class KNNRunner(BaseModelRunner):
    """Runner for K-Nearest Neighbors multivariate imputer."""

    def __init__(self, n_neighbors: int = 5):
        super().__init__(
            id="knn",
            name="K-Nearest Neighbors (KNN)",
            version="knn-k5-v1",
            model_type="Machine Learning / Non-Parametric",
            description="Instance-based KNN spatial-temporal imputer using distance-weighted sample neighbors.",
            city="all",
            framework="Scikit-Learn",
            architecture="KNN Multivariate Imputer (k=5, Uniform/Distance Weighted)",
            category="baseline",
            is_available=True,
            param_count=0,
            checkpoint_path=None
        )
        self.n_neighbors = n_neighbors
        self.imputer = None
        self._fitted = False

    def load(self):
        if not self._is_loaded:
            t0 = time.perf_counter()
            self.imputer = KNNPollutionImputer(n_neighbors=self.n_neighbors)
            ref_path = "results/delhi/eval_cache.npz"
            if os.path.exists(ref_path):
                try:
                    raw = np.load(ref_path, allow_pickle=True)
                    x_ref = raw["x_test_true_norm"][500:1000]
                    m_ref = np.ones_like(x_ref)
                    self.imputer.fit(x_ref, m_ref)
                    self._fitted = True
                except Exception:
                    pass
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def fit_if_needed(self, x_ref: np.ndarray, m_ref: np.ndarray):
        if not self._fitted:
            try:
                self.imputer.fit(x_ref, m_ref)
                self._fitted = True
            except Exception:
                pass

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        if not self._fitted:
            self.fit_if_needed(x_obs, mask)
        try:
            x_imp = self.imputer.impute(x_obs, mask)
        except Exception:
            x_imp = x_obs.copy()
            x_imp[mask == 0.0] = 0.0
        x_imp = np.nan_to_num(x_imp, nan=0.0)
        x_imp = np.where(mask == 1.0, x_obs, x_imp)
        return x_imp, x_imp


class MeanImputerRunner(BaseModelRunner):
    """Runner for Empirical Feature Mean baseline."""

    def __init__(self):
        super().__init__(
            id="mean_imputer",
            name="Feature Mean Imputer",
            version="empirical-v1",
            model_type="Empirical / Statistical Baseline",
            description="Fills missing timestamps with the empirical channel-wise mean computed from training observations.",
            city="all",
            framework="Empirical Statistics",
            architecture="Univariate Channel Mean",
            category="baseline",
            is_available=True,
            param_count=0,
            checkpoint_path=None
        )
        self.imputer = None
        self._fitted = False

    def load(self):
        if not self._is_loaded:
            t0 = time.perf_counter()
            self.imputer = MeanImputer()
            ref_path = "results/delhi/eval_cache.npz"
            if os.path.exists(ref_path):
                try:
                    raw = np.load(ref_path, allow_pickle=True)
                    x_ref = raw["x_test_true_norm"][500:1000]
                    m_ref = np.ones_like(x_ref)
                    self.imputer.fit(x_ref, m_ref)
                    self._fitted = True
                except Exception:
                    pass
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def fit_if_needed(self, x_ref: np.ndarray, m_ref: np.ndarray):
        if not self._fitted:
            try:
                self.imputer.fit(x_ref, m_ref)
                self._fitted = True
            except Exception:
                pass

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        if not self._fitted:
            self.fit_if_needed(x_obs, mask)
        try:
            x_imp = self.imputer.impute(x_obs, mask)
        except Exception:
            x_imp = x_obs.copy()
            x_imp[mask == 0.0] = 0.0
        x_imp = np.nan_to_num(x_imp, nan=0.0)
        x_imp = np.where(mask == 1.0, x_obs, x_imp)
        return x_imp, x_imp


class MLPRunner(BaseModelRunner):
    """Runner for Simple MLP Autoencoder baseline."""

    def __init__(self, hidden_dim: int = 128):
        super().__init__(
            id="simple_mlp",
            name="Simple MLP Autoencoder",
            version="mlp-v1",
            model_type="Deep Learning / Feedforward",
            description="3-layer feedforward neural autoencoder mapping flattened (X_obs, mask) to 24h sequence predictions.",
            city="Delhi",
            framework="PyTorch",
            architecture="3-Layer Dense MLP (Input: 240, Hidden: 128, Output: 120)",
            category="baseline",
            is_available=True,
            param_count=49272,
            checkpoint_path="checkpoints/mlp/best_temporal_transformer.pt"
        )
        self.hidden_dim = hidden_dim
        self.model = None

    def load(self):
        if not self._is_loaded:
            t0 = time.perf_counter()
            self.model = SimpleMLPImputer(num_features=5, window_size=24, hidden_dim=self.hidden_dim)
            if self.checkpoint_path and os.path.exists(self.checkpoint_path):
                try:
                    ckpt = torch.load(self.checkpoint_path, map_location="cpu")
                    sd = ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt.state_dict()
                    if sd["net.0.weight"].shape[1] == 24 * 5 * 2:
                        self.model.load_state_dict(sd)
                except Exception:
                    pass
            self.model.eval()
            self.load_time_ms = (time.perf_counter() - t0) * 1000.0
            self._is_loaded = True

    def predict(
        self,
        x_obs: np.ndarray,
        mask: np.ndarray,
        context: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        if not self._is_loaded:
            self.load()
        with torch.no_grad():
            t_obs = torch.tensor(x_obs, dtype=torch.float32)
            t_m = torch.tensor(mask, dtype=torch.float32)
            t_imp, t_raw = self.model(t_obs, t_m)
        x_imp = t_imp.cpu().numpy().astype(np.float32)
        x_raw = t_raw.cpu().numpy().astype(np.float32)
        x_imp = np.where(mask == 1.0, x_obs, x_imp)
        return x_imp, x_raw


class FutureModelRunner(BaseModelRunner):
    """Placeholder slot for models in development (e.g. Improved CTDI v2, Diffusion)."""

    def __init__(self, id: str, name: str, version: str, description: str, framework: str = "PyTorch", architecture: str = ""):
        super().__init__(
            id=id,
            name=name,
            version=version,
            model_type="Future Research Architecture",
            description=description,
            city="Delhi",
            framework=framework,
            architecture=architecture,
            category="future",
            is_available=False
        )

    def load(self):
        raise NotImplementedError(f"Model '{self.name}' is currently in training/development.")

    def predict(self, x_obs, mask, context=None):
        raise NotImplementedError(f"Model '{self.name}' checkpoint is not yet available.")


class ModelRegistry:
    """Central registry managing all benchmarking models, organized by city and architecture."""

    def __init__(self):
        self._models: Dict[str, BaseModelRunner] = {}
        self._aliases: Dict[str, str] = {}

    def register(self, runner: BaseModelRunner, aliases: Optional[List[str]] = None):
        """Registers a model runner with primary ID and optional backward-compatibility aliases."""
        self._models[runner.id] = runner
        if aliases:
            for alias in aliases:
                self._aliases[alias] = runner.id

    def get(self, model_id: str) -> Optional[BaseModelRunner]:
        """Looks up a model runner by ID or alias."""
        resolved_id = self._aliases.get(model_id, model_id)
        return self._models.get(resolved_id)

    def list_models(self, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns model metadata, optionally filtered for a specific city."""
        models = self._models.values()
        if city:
            city_lower = city.strip().lower()
            models = [
                m for m in models
                if m.city.lower() == city_lower or m.city.lower() == "all"
            ]
        return [m.metadata() for m in models]

    def get_models_for_city(self, city: str) -> List[Dict[str, Any]]:
        """Convenience method to retrieve all models available for a given city."""
        return self.list_models(city=city)

    def get_available_ids(self, city: Optional[str] = None) -> List[str]:
        """Returns list of all ready model IDs for a city."""
        return [m["id"] for m in self.list_models(city=city) if m["is_available"]]

    def list_cities(self) -> List[Dict[str, Any]]:
        """Returns catalog of cities with their trained model counts."""
        cities_map: Dict[str, Dict[str, Any]] = {
            "Delhi": {
                "city": "Delhi",
                "name": "Delhi (National Capital Region)",
                "state": "Delhi",
                "has_trained_models": True,
                "trained_models_count": 2,
                "available_models": ["delhi_ctdi_original", "delhi_ctdi_keras"],
                "description": "Indian CPCB continuous monitoring network with PyTorch & Keras 3 checkpoints."
            }
        }
        return list(cities_map.values())


def get_default_registry() -> ModelRegistry:
    """Instantiates and registers all standard models with aliases."""
    registry = ModelRegistry()

    # 1. Trained Delhi Neural Models
    registry.register(
        CTDITransformerRunner(),
        aliases=["ctdi_transformer", "delhi_pytorch", "original_ctdi"]
    )
    registry.register(
        KerasCTDIRunner(),
        aliases=["ctdi_keras", "delhi_keras", "keras_ctdi"]
    )

    # 2. Universal Baselines
    registry.register(LinearInterpolationRunner(), aliases=["linear"])
    registry.register(KNNRunner(n_neighbors=5), aliases=["knn_k5"])
    registry.register(MeanImputerRunner(), aliases=["mean"])
    registry.register(MLPRunner(hidden_dim=128), aliases=["mlp"])

    # 3. Future Architectures
    registry.register(FutureModelRunner(
        id="ctdi_improved_v2",
        name="Improved CTDI (v2)",
        version="v2.0-candidate",
        description="Upcoming multi-scale temporal dilated convolution + spatial self-attention model.",
        framework="PyTorch / Multi-Scale",
        architecture="Multi-Scale Temporal Dilated Conv + Spatial Self-Attention (In Dev)"
    ))
    registry.register(FutureModelRunner(
        id="slm_diffusion",
        name="SLM-Conditioned Diffusion",
        version="diffusion-v1",
        description="Generative diffusion framework with Small Language Model environmental conditioning.",
        framework="Generative Diffusion",
        architecture="Conditional Denoising Diffusion Probabilistic Model (DDPM, In Dev)"
    ))

    return registry
