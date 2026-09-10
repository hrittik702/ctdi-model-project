"""Thread-safe singleton model loader and inference locking."""

import threading
from typing import Optional
from src.inference.model_adapter import PyTorchTemporalModelAdapter, ImputationModel

_model_lock = threading.Lock()
_cached_model: Optional[ImputationModel] = None
_default_ckpt = "checkpoints/delhi/best_temporal_transformer.pt"


def get_model_instance(checkpoint_path: str = _default_ckpt) -> ImputationModel:
    """
    Returns cached model instance or instantiates once thread-safely.
    """
    global _cached_model
    if _cached_model is None:
        with _model_lock:
            if _cached_model is None:
                _cached_model = PyTorchTemporalModelAdapter(checkpoint_path=checkpoint_path)
    return _cached_model


def run_threadsafe_inference(
    model: ImputationModel,
    x_obs,
    mask,
    context=None
):
    """
    Executes model inference under lock to guarantee thread safety.
    """
    with _model_lock:
        return model.impute(x_obs, mask, context)
