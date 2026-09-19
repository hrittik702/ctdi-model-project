"""Environmental and spatio-temporal context construction module.

Provides:
- context_features: Numerical extraction & HKO-standard descriptor functions.
- context_serializer: Multi-format serialization (narrative, key-value, JSON).
- context_builder / builder: EnvironmentalContextBuilder orchestrator.
- slm_encoder: BaseSLMContextEncoder, MockSLMContextEncoder, HuggingFaceSLMContextEncoder.
"""

from src.context.context_features import (
    CHANNEL_NAMES,
    POLLUTANT_INDICES,
    MET_INDICES,
    TRAFFIC_INDICES,
    describe_temperature,
    describe_humidity,
    describe_rainfall,
    describe_wind,
    describe_traffic,
    describe_missingness,
    extract_window_features,
)
from src.context.context_serializer import (
    serialize_to_narrative,
    serialize_to_key_value,
    serialize_to_json,
    serialize_context,
)
from src.context.context_builder import (
    EnvironmentalContextBuilder,
    build_environmental_context,
)
from src.context.slm_encoder import (
    BaseSLMContextEncoder,
    MockSLMContextEncoder,
    HuggingFaceSLMContextEncoder,
)

__all__ = [
    "CHANNEL_NAMES",
    "POLLUTANT_INDICES",
    "MET_INDICES",
    "TRAFFIC_INDICES",
    "describe_temperature",
    "describe_humidity",
    "describe_rainfall",
    "describe_wind",
    "describe_traffic",
    "describe_missingness",
    "extract_window_features",
    "serialize_to_narrative",
    "serialize_to_key_value",
    "serialize_to_json",
    "serialize_context",
    "EnvironmentalContextBuilder",
    "build_environmental_context",
    "BaseSLMContextEncoder",
    "MockSLMContextEncoder",
    "HuggingFaceSLMContextEncoder",
]
