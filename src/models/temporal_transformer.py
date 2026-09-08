"""CTDI-inspired 1x1 CNN + Temporal Transformer Imputation Architecture."""

import math
import torch
import torch.nn as nn
from typing import Tuple, Optional

class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for 24-hour sequence."""
    def __init__(self, d_model: int, max_len: int = 48, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (B, T, d_model)
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)

class CTDITemporalTransformer(nn.Module):
    """
    CTDI-Inspired Spatio-Temporal Baseline (Single-Station V0.1).
    
    Architecture:
    1. Input: Concatenated [X_obs, Mask] with shape (B, T, 2*F)
    2. Initial 1x1 CNN (Pointwise Conv): projects (2*F) -> d_model to mix cross-pollutant features
    3. Positional Encoding
    4. Temporal Transformer Encoder: models dependencies across the 24 hours
    5. Output 1x1 CNN: projects d_model -> F
    6. Masked Reconstruction Assembly: replaces ONLY missing entries
    """
    def __init__(
        self,
        num_features: int,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
        window_size: int = 24
    ):
        super().__init__()
        self.num_features = num_features
        self.d_model = d_model
        self.window_size = window_size
        
        # 1x1 CNN for cross-feature mixing: in_channels = 2 * F (data + mask)
        self.pre_conv = nn.Sequential(
            nn.Conv1d(in_channels=2 * num_features, out_channels=d_model, kernel_size=1),
            nn.BatchNorm1d(d_model),
            nn.GELU()
        )
        
        # Positional Encoding for 24 hours
        self.pos_encoder = PositionalEncoding(d_model=d_model, max_len=window_size + 4, dropout=dropout)
        
        # Temporal Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Post 1x1 CNN mapping back to feature dimension
        self.post_conv = nn.Sequential(
            nn.Conv1d(in_channels=d_model, out_channels=d_model // 2, kernel_size=1),
            nn.GELU(),
            nn.Conv1d(in_channels=d_model // 2, out_channels=num_features, kernel_size=1)
        )
        
    def forward(self, x_obs: torch.Tensor, mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x_obs: (B, T=24, F) Observed tensor (zeros where masked)
            mask: (B, T=24, F) Binary mask (1=observed, 0=missing)
            
        Returns:
            x_imputed: (B, T=24, F) Tensor with missing values replaced
            x_pred_raw: (B, T=24, F) Complete raw predicted tensor
        """
        B, T, F = x_obs.shape
        
        # Concatenate data and mask along feature dimension -> (B, T, 2*F)
        x_cat = torch.cat([x_obs, mask], dim=-1)
        
        # 1x1 CNN expects shape: (B, Channels, Length)
        x_trans = x_cat.transpose(1, 2)  # (B, 2*F, T)
        x_emb = self.pre_conv(x_trans)   # (B, d_model, T)
        
        # Transpose back to (B, T, d_model) for Transformer
        x_seq = x_emb.transpose(1, 2)    # (B, T, d_model)
        x_pe = self.pos_encoder(x_seq)
        
        # Temporal Transformer self-attention across 24 hours
        h = self.transformer_encoder(x_pe)  # (B, T, d_model)
        
        # Post 1x1 CNN expects (B, Channels, Length)
        h_trans = h.transpose(1, 2)         # (B, d_model, T)
        pred_trans = self.post_conv(h_trans) # (B, F, T)
        x_pred_raw = pred_trans.transpose(1, 2) # (B, T, F)
        
        # Strictly preserve observed values, replace ONLY missing entries
        x_imputed = mask * x_obs + (1.0 - mask) * x_pred_raw
        
        return x_imputed, x_pred_raw

class SimpleMLPImputer(nn.Module):
    """A straightforward feedforward autoencoder baseline for sanity checking."""
    def __init__(self, num_features: int, window_size: int = 24, hidden_dim: int = 128):
        super().__init__()
        in_dim = window_size * num_features * 2
        out_dim = window_size * num_features
        self.num_features = num_features
        self.window_size = window_size
        
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim)
        )
        
    def forward(self, x_obs: torch.Tensor, mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        B, T, F = x_obs.shape
        x_flat = torch.cat([x_obs, mask], dim=-1).reshape(B, -1)
        pred_flat = self.net(x_flat)
        x_pred_raw = pred_flat.reshape(B, T, F)
        x_imputed = mask * x_obs + (1.0 - mask) * x_pred_raw
        return x_imputed, x_pred_raw
