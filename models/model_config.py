"""Configuration dataclass and default parameters for CTDI Temporal Model in Keras 3."""

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class TemporalModelConfig:
    """Hyperparameters for the CTDI Spatial-Temporal Transformer in Keras 3."""
    num_features: int = 5          # Criteria pollutants (PM2.5, PM10, NO2, SO2, O3)
    num_context: int = 9           # Calendar (4) + Meteorological (5) features
    window_size: int = 24          # Sequence window length (hours)
    d_model: int = 128             # Transformer embedding & CNN channel dimension
    num_heads: int = 8             # Multi-head attention heads
    feed_forward_dim: int = 256    # Feedforward expansion dimension
    num_transformer_layers: int = 3 # Number of Pre-LN Transformer encoder blocks
    dropout: float = 0.1           # Dropout rate
    kernel_size: int = 3           # Local temporal convolution kernel size
    activation: str = "gelu"       # Activation function
    use_gap_features: bool = True  # Enable structural missingness gap features
    use_multiscale: bool = True    # Enable multi-scale temporal convolutions (k=1, 3, 5, 7)

    @property
    def total_input_channels(self) -> int:
        """Total input channels: pollutants(5) + mask(5) + prior(5) + context(9) + [gap_features(20)]."""
        base = 3 * self.num_features + self.num_context
        return base + (4 * self.num_features if self.use_gap_features else 0)


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalModelConfig":
        valid_keys = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)
