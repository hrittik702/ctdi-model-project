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

def torch_linear_interpolate_24h(p_obs: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """
    Vectorized 1D linear interpolation along time dimension (T=24) for (B, T, F).
    Boundary positions filled with nearest observed value.
    """
    B, T, F = p_obs.shape
    device = p_obs.device
    time_idx = torch.arange(T, device=device, dtype=torch.float32).view(1, T, 1)
    
    left_v = torch.zeros(B, T, F, device=device)
    left_t = torch.zeros(B, T, F, device=device)
    curr_v = torch.zeros(B, 1, F, device=device)
    curr_t = torch.full((B, 1, F), -1.0, device=device)
    for t in range(T):
        m_t = mask[:, t:t+1, :]
        p_t = p_obs[:, t:t+1, :]
        curr_v = torch.where(m_t == 1.0, p_t, curr_v)
        curr_t = torch.where(m_t == 1.0, time_idx[:, t:t+1, :], curr_t)
        left_v[:, t:t+1, :] = curr_v
        left_t[:, t:t+1, :] = curr_t
        
    right_v = torch.zeros(B, T, F, device=device)
    right_t = torch.zeros(B, T, F, device=device)
    curr_v = torch.zeros(B, 1, F, device=device)
    curr_t = torch.full((B, 1, F), float(T), device=device)
    for t in range(T - 1, -1, -1):
        m_t = mask[:, t:t+1, :]
        p_t = p_obs[:, t:t+1, :]
        curr_v = torch.where(m_t == 1.0, p_t, curr_v)
        curr_t = torch.where(m_t == 1.0, time_idx[:, t:t+1, :], curr_t)
        right_v[:, t:t+1, :] = curr_v
        right_t[:, t:t+1, :] = curr_t
        
    dt = right_t - left_t
    valid_interval = (left_t >= 0) & (right_t < T) & (dt > 0)
    w = torch.where(valid_interval, (time_idx - left_t) / dt, torch.zeros_like(dt))
    interp = torch.where(
        valid_interval,
        (1.0 - w) * left_v + w * right_v,
        torch.where(left_t >= 0, left_v, torch.where(right_t < T, right_v, torch.zeros_like(p_obs)))
    )
    return torch.where(mask == 1.0, p_obs, interp)

class CTDITemporalTransformer(nn.Module):
    """
    CTDI-Inspired Spatio-Temporal Imputation Transformer with Linear Prior Residual Learning.
    
    Architecture:
    1. Continuous Linear Prior: Exact 1D temporal interpolation as inductive base
    2. Input channels: [X_pollutant_obs, Mask_pollutant, X_linear_prior, Context]
       Total input channels: 5 + 5 + 5 + 9 = 24 channels
    3. Dual-Stage 1D CNN: Pointwise channel mixing + Local temporal neighborhood convolution
    4. Positional Encoding
    5. Temporal Transformer Encoder (Pre-LN, multi-head self-attention across 24 hours)
    6. Post CNN: Deep atmospheric & meteorological non-linear adjustment
    7. Residual Reconstruction: X_pred = X_linear_prior + Delta_transformer
    """
    def __init__(
        self,
        num_features: int = 5,
        num_context: int = 9,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 3,
        dim_feedforward: int = 256,
        dropout: float = 0.1,
        window_size: int = 24
    ):
        super().__init__()
        self.num_features = num_features
        self.num_context = num_context
        self.d_model = d_model
        self.window_size = window_size
        
        in_channels = 3 * num_features + num_context
        
        # Dual-Stage 1D CNN: Pointwise channel mixing + Local temporal neighborhood convolution (kernel_size=3)
        self.pre_conv = nn.Sequential(
            nn.Conv1d(in_channels=in_channels, out_channels=d_model, kernel_size=1),
            nn.BatchNorm1d(d_model),
            nn.GELU(),
            nn.Conv1d(in_channels=d_model, out_channels=d_model, kernel_size=3, padding=1),
            nn.BatchNorm1d(d_model),
            nn.GELU()
        )
        
        # Positional Encoding for 24 hours
        self.pos_encoder = PositionalEncoding(d_model=d_model, max_len=window_size + 8, dropout=dropout)
        
        # Pre-LN Temporal Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Post CNN: Local temporal smoothing + channel projection back to target pollutants
        self.post_conv = nn.Sequential(
            nn.Conv1d(in_channels=d_model, out_channels=d_model, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Dropout(p=dropout),
            nn.Conv1d(in_channels=d_model, out_channels=num_features, kernel_size=1)
        )
        
    def forward(
        self, 
        x_obs: torch.Tensor, 
        mask: torch.Tensor, 
        context: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x_obs: (B, T=24, F_pollutant) Observed pollutant values (0 where missing)
                   OR (B, T=24, F_all=14) if context is bundled into x_obs.
            mask: (B, T=24, F_pollutant=5) Binary mask (1=observed, 0=missing)
            context: (B, T=24, F_context=9) Optional meteorological/temporal context
            
        Returns:
            x_imputed: (B, T=24, F_pollutant) Tensor with missing values replaced
            x_pred_raw: (B, T=24, F_pollutant) Complete raw predicted tensor
        """
        # Determine pollutants vs context if passed together in x_obs
        if context is not None:
            pollutants_obs = x_obs
            ctx = context
        elif x_obs.shape[-1] == self.num_features + self.num_context and self.num_context > 0:
            ctx = x_obs[..., :self.num_context]
            pollutants_obs = x_obs[..., self.num_context:]
        elif x_obs.shape[-1] == self.num_features and self.num_context > 0:
            # If context was configured but not passed, pad with zeros
            pollutants_obs = x_obs
            ctx = torch.zeros(x_obs.shape[0], x_obs.shape[1], self.num_context, device=x_obs.device)
        else:
            pollutants_obs = x_obs
            ctx = None
            
        # Compute exact continuous 1D linear interpolation baseline prior
        p_interp = torch_linear_interpolate_24h(pollutants_obs, mask)
        
        # Concatenate: [pollutants_obs, mask, p_interp, ctx]
        if ctx is not None:
            x_cat = torch.cat([pollutants_obs, mask, p_interp, ctx], dim=-1)
        else:
            x_cat = torch.cat([pollutants_obs, mask, p_interp], dim=-1)
            
        # 1x1 CNN expects shape: (B, Channels, Length)
        x_trans = x_cat.transpose(1, 2)  # (B, Channels, T)
        x_emb = self.pre_conv(x_trans)   # (B, d_model, T)
        
        # Transpose back to (B, T, d_model) for Transformer
        x_seq = x_emb.transpose(1, 2)    # (B, T, d_model)
        x_pe = self.pos_encoder(x_seq)
        
        # Temporal Transformer self-attention across 24 hours
        h = self.transformer_encoder(x_pe)  # (B, T, d_model)
        
        # Post CNN: deep atmospheric & cross-pollutant non-linear adjustment
        h_trans = h.transpose(1, 2)         # (B, d_model, T)
        delta_pred = self.post_conv(h_trans).transpose(1, 2) # (B, T, num_features)
        
        # Combined residual prediction: linear interpolation baseline + transformer non-linear meteorological adjustment
        x_pred_raw = p_interp + delta_pred
        
        # Strictly preserve observed values, replace ONLY missing entries
        x_imputed = mask * pollutants_obs + (1.0 - mask) * x_pred_raw
        
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
