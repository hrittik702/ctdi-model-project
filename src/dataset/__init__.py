"""Dataset construction, windowing, feature normalization, and missingness simulation module."""

from src.dataset.normalization import (
    CANONICAL_13_CHANNELS,
    POLLUTANT_CHANNELS,
    MET_CHANNELS,
    TRAFFIC_CHANNELS,
    FeatureNormalizer,
)
from src.dataset.missingness import (
    DEFAULT_TARGET_CHANNELS,
    ExperimentalMaskGenerator,
    simulate_missingness,
)
from src.dataset.split import (
    SPLIT_NAMES,
    ChronologicalSplitManager,
)

__all__ = [
    "CANONICAL_13_CHANNELS",
    "POLLUTANT_CHANNELS",
    "MET_CHANNELS",
    "TRAFFIC_CHANNELS",
    "FeatureNormalizer",
    "DEFAULT_TARGET_CHANNELS",
    "ExperimentalMaskGenerator",
    "simulate_missingness",
    "SPLIT_NAMES",
    "ChronologicalSplitManager",
]
