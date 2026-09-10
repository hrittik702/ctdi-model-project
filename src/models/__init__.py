"""Model implementations for Air Pollution Imputation."""

from src.models.baselines import MeanImputer, LinearInterpolationImputer, KNNPollutionImputer
from src.models.temporal_transformer import CTDITemporalTransformer, SimpleMLPImputer

__all__ = [
    "MeanImputer",
    "LinearInterpolationImputer",
    "KNNPollutionImputer",
    "CTDITemporalTransformer",
    "SimpleMLPImputer",
    "KerasTemporalModelAdapter",
    "build_keras_temporal_model",
    "TemporalModelConfig",
]

def __getattr__(name):
    if name in ("KerasTemporalModelAdapter", "build_keras_temporal_model", "TemporalModelConfig"):
        import models
        return getattr(models, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
