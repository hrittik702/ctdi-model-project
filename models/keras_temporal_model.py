"""Keras 3 implementation of CTDI Spatial-Temporal Transformer for Pollution Imputation."""

import os
# Ensure Keras uses PyTorch backend if not already specified
os.environ.setdefault("KERAS_BACKEND", "torch")

import math
import numpy as np
import keras
from keras import ops
from typing import Optional

from models.model_config import TemporalModelConfig


@keras.saving.register_keras_serializable(package="ctdi_models")
class PositionalEncoding(keras.layers.Layer):
    """Sinusoidal positional encoding layer for 24-hour time sequences."""
    def __init__(self, d_model: int = 128, max_len: int = 48, dropout: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        self.d_model = int(d_model)
        self.max_len = int(max_len)
        self.dropout_rate = float(dropout)
        self.dropout = keras.layers.Dropout(rate=self.dropout_rate)

        # Precompute sinusoidal matrix
        pe = np.zeros((self.max_len, self.d_model), dtype=np.float32)
        position = np.arange(0, self.max_len, dtype=np.float32)[:, np.newaxis]
        div_term = np.exp(
            np.arange(0, self.d_model, 2, dtype=np.float32) * (-math.log(10000.0) / self.d_model)
        )
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        self.pe_array = pe[np.newaxis, :, :]  # Shape: (1, max_len, d_model)

    def build(self, input_shape):
        self.pe = self.add_weight(
            name="pe_matrix",
            shape=self.pe_array.shape,
            initializer=keras.initializers.Constant(self.pe_array),
            trainable=False,
            dtype="float32",
        )
        super().build(input_shape)

    def call(self, x, training=None):
        # x shape: (batch, seq_len, d_model)
        seq_len = ops.shape(x)[1]
        x = x + self.pe[:, :seq_len, :]
        return self.dropout(x, training=training)

    def get_config(self):
        config = super().get_config()
        config.update({
            "d_model": self.d_model,
            "max_len": self.max_len,
            "dropout": self.dropout_rate,
        })
        return config


@keras.saving.register_keras_serializable(package="ctdi_models")
class TransformerEncoderBlock(keras.layers.Layer):
    """Pre-LN Transformer Encoder block matching PyTorch TransformerEncoderLayer(norm_first=True)."""
    def __init__(
        self,
        d_model: int = 128,
        num_heads: int = 8,
        feed_forward_dim: int = 256,
        dropout: float = 0.1,
        activation: str = "gelu",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.d_model = int(d_model)
        self.num_heads = int(num_heads)
        self.feed_forward_dim = int(feed_forward_dim)
        self.dropout_rate = float(dropout)
        self.activation = activation

        self.norm1 = keras.layers.LayerNormalization(epsilon=1e-5, name="ln_1")
        self.mha = keras.layers.MultiHeadAttention(
            num_heads=self.num_heads,
            key_dim=self.d_model // self.num_heads,
            dropout=self.dropout_rate,
            name="mha",
        )
        self.dropout1 = keras.layers.Dropout(self.dropout_rate, name="drop_1")

        self.norm2 = keras.layers.LayerNormalization(epsilon=1e-5, name="ln_2")
        self.ffn_dense1 = keras.layers.Dense(self.feed_forward_dim, activation=self.activation, name="ffn_dense1")
        self.ffn_drop1 = keras.layers.Dropout(self.dropout_rate, name="ffn_drop1")
        self.ffn_dense2 = keras.layers.Dense(self.d_model, name="ffn_dense2")
        self.ffn_drop2 = keras.layers.Dropout(self.dropout_rate, name="ffn_drop2")

    def build(self, input_shape):
        self.norm1.build(input_shape)
        self.mha.build(query_shape=input_shape, value_shape=input_shape, key_shape=input_shape)
        self.dropout1.build(input_shape)
        self.norm2.build(input_shape)
        self.ffn_dense1.build(input_shape)
        self.ffn_drop1.build(input_shape)
        mid_shape = list(input_shape)
        mid_shape[-1] = self.feed_forward_dim
        self.ffn_dense2.build(tuple(mid_shape))
        self.ffn_drop2.build(input_shape)
        super().build(input_shape)

    def call(self, x, training=None):
        # 1. Pre-LN Self-Attention with residual connection
        x_norm = self.norm1(x)
        attn_out = self.mha(query=x_norm, value=x_norm, key=x_norm, training=training)
        attn_out = self.dropout1(attn_out, training=training)
        x = x + attn_out

        # 2. Pre-LN Feedforward network with residual connection
        x_norm2 = self.norm2(x)
        ffn_out = self.ffn_dense1(x_norm2)
        ffn_out = self.ffn_drop1(ffn_out, training=training)
        ffn_out = self.ffn_dense2(ffn_out)
        ffn_out = self.ffn_drop2(ffn_out, training=training)
        x = x + ffn_out
        return x

    def get_config(self):
        config = super().get_config()
        config.update({
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "feed_forward_dim": self.feed_forward_dim,
            "dropout": self.dropout_rate,
            "activation": self.activation,
        })
        return config


@keras.saving.register_keras_serializable(package="ctdi_models")
class StrictObservationLock(keras.layers.Layer):
    """
    Guarantees strict preservation of observed values without arbitrary lambda serialization:
    x_imputed = mask * x_obs + (1.0 - mask) * x_pred_raw
    """
    def call(self, inputs):
        x_obs, mask, x_pred_raw = inputs
        return mask * x_obs + (1.0 - mask) * x_pred_raw

    def get_config(self):
        return super().get_config()


def build_keras_temporal_model(
    config: Optional[TemporalModelConfig] = None,
    name: str = "CTDI_Keras_Temporal_Transformer"
) -> keras.Model:
    """
    Constructs the Keras 3 CTDI Spatial-Temporal Transformer Imputation Model.

    Inputs:
        pollutant_observations: (batch, 24, 5)
        observation_mask:       (batch, 24, 5)
        linear_prior:           (batch, 24, 5)
        context:                (batch, 24, 9)

    Outputs:
        x_imputed:  (batch, 24, 5) with observed values strictly preserved
        x_pred_raw: (batch, 24, 5) complete raw model prediction
    """
    if config is None:
        config = TemporalModelConfig()

    # 1. Define explicit inputs matching project contract
    x_obs = keras.Input(
        shape=(config.window_size, config.num_features),
        name="pollutant_observations"
    )
    mask = keras.Input(
        shape=(config.window_size, config.num_features),
        name="observation_mask"
    )
    linear_prior = keras.Input(
        shape=(config.window_size, config.num_features),
        name="linear_interpolation_prior"
    )
    context = keras.Input(
        shape=(config.window_size, config.num_context),
        name="context"
    )

    # 2. Concatenate inputs along feature dimension:
    # 5 (pollutants) + 5 (mask) + 5 (prior) + 9 (context) = 24 features
    x_cat = keras.layers.Concatenate(axis=-1, name="feature_concatenation")(
        [x_obs, mask, linear_prior, context]
    )

    # 3. Pointwise 1x1 feature-mixing convolution
    h = keras.layers.Conv1D(
        filters=config.d_model,
        kernel_size=1,
        padding="same",
        name="pointwise_conv1d"
    )(x_cat)
    h = keras.layers.BatchNormalization(name="pre_bn1")(h)
    h = keras.layers.Activation(config.activation, name="pre_act1")(h)

    # 4. Local temporal Conv1D (kernel_size=3, padding="same")
    h = keras.layers.Conv1D(
        filters=config.d_model,
        kernel_size=config.kernel_size,
        padding="same",
        name="temporal_conv1d"
    )(h)
    h = keras.layers.BatchNormalization(name="pre_bn2")(h)
    h = keras.layers.Activation(config.activation, name="pre_act2")(h)

    # 5. Positional Encoding
    h = PositionalEncoding(
        d_model=config.d_model,
        max_len=config.window_size + 8,
        dropout=config.dropout,
        name="positional_encoding"
    )(h)

    # 6. Pre-LN Transformer Encoder Layers
    for i in range(config.num_transformer_layers):
        h = TransformerEncoderBlock(
            d_model=config.d_model,
            num_heads=config.num_heads,
            feed_forward_dim=config.feed_forward_dim,
            dropout=config.dropout,
            activation=config.activation,
            name=f"transformer_encoder_layer_{i}"
        )(h)

    # 7. Post-Transformer temporal reconstruction head
    h = keras.layers.Conv1D(
        filters=config.d_model,
        kernel_size=config.kernel_size,
        padding="same",
        activation=config.activation,
        name="post_temporal_conv1d"
    )(h)
    h = keras.layers.Dropout(config.dropout, name="post_dropout")(h)
    delta_prediction = keras.layers.Conv1D(
        filters=config.num_features,
        kernel_size=1,
        padding="same",
        name="delta_prediction"
    )(h)

    # 8. Residual Prediction: linear_prior + delta_prediction
    x_pred_raw = keras.layers.Add(name="pred_raw")([linear_prior, delta_prediction])

    # 9. Strict preservation of observed values via dedicated serializable lock
    x_imputed = StrictObservationLock(name="x_imputed")(
        [x_obs, mask, x_pred_raw]
    )

    # Return model with both outputs
    model = keras.Model(
        inputs=[x_obs, mask, linear_prior, context],
        outputs=[x_imputed, x_pred_raw],
        name=name
    )
    return model
