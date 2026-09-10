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

def torch_compute_gap_features(mask: torch.Tensor) -> torch.Tensor:
    """
    Computes vectorized temporal missingness structure features strictly from mask tensor:
    - dt_prev: Steps since last observed point (normalized [0, 1])
    - dt_next: Steps until next observed point (normalized [0, 1])
    - gap_len: Contiguous outage length (normalized [0, 1])
    - is_boundary: Flag indicating boundary step adjacent to observed value
    """
    B, T, F = mask.shape
    device = mask.device
    
    dt_prev = torch.zeros_like(mask)
    curr = torch.zeros(B, 1, F, device=device)
    for t in range(T):
        m_t = mask[:, t:t+1, :]
        curr = torch.where(m_t == 1.0, torch.zeros_like(curr), curr + 1.0)
        dt_prev[:, t:t+1, :] = curr
        
    dt_next = torch.zeros_like(mask)
    curr = torch.zeros(B, 1, F, device=device)
    for t in range(T - 1, -1, -1):
        m_t = mask[:, t:t+1, :]
        curr = torch.where(m_t == 1.0, torch.zeros_like(curr), curr + 1.0)
        dt_next[:, t:t+1, :] = curr
        
    norm_T = float(T)
    dt_prev = dt_prev * (1.0 - mask) / norm_T
    dt_next = dt_next * (1.0 - mask) / norm_T
    gap_len = (dt_prev * norm_T + dt_next * norm_T - 1.0).clamp(min=0.0) / norm_T * (1.0 - mask)
    
    prev_obs = torch.cat([torch.ones(B, 1, F, device=device), mask[:, :-1, :]], dim=1) == 1.0
    next_obs = torch.cat([mask[:, 1:, :], torch.ones(B, 1, F, device=device)], dim=1) == 1.0
    is_boundary = ((1.0 - mask) * ((prev_obs.float() + next_obs.float()) > 0).float())
    
    return torch.cat([dt_prev, dt_next, gap_len, is_boundary], dim=-1)

class MultiScaleTemporalBlock(nn.Module):
    """
    Parallel multi-scale temporal convolutions capturing:
    k=1: Pointwise cross-feature mixing
    k=3: Sharp rapid hourly transitions & peak events
    k=5: Short-term trends (3-5h buildups/decays)
    k=7: Diurnal shifts & atmospheric weather movements
    """
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        b_dim = out_channels // 4
        self.conv1 = nn.Conv1d(in_channels, b_dim, kernel_size=1)
        self.conv3 = nn.Conv1d(in_channels, b_dim, kernel_size=3, padding=1)
        self.conv5 = nn.Conv1d(in_channels, b_dim, kernel_size=5, padding=2)
        self.conv7 = nn.Conv1d(in_channels, b_dim, kernel_size=7, padding=3)
        self.proj = nn.Conv1d(b_dim * 4, out_channels, kernel_size=1)
        self.bn = nn.BatchNorm1d(out_channels)
        self.act = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        b1 = self.conv1(x)
        b3 = self.conv3(x)
        b5 = self.conv5(x)
        b7 = self.conv7(x)
        cat = torch.cat([b1, b3, b5, b7], dim=1)
        return self.act(self.bn(self.proj(cat)))

class GatedResidualHead(nn.Module):
    """
    Gated non-linear reconstruction head:
    x_pred = p_interp + Gate(h) * Delta(h)
    where Gate in [0, 2] dynamically trusts linear prior on flat gaps
    and permits large excursions for sharp peaks without drift.
    """
    def __init__(self, d_model: int, num_features: int, kernel_size: int = 3, dropout: float = 0.1):
        super().__init__()
        self.post_conv = nn.Sequential(
            nn.Conv1d(d_model, d_model, kernel_size=kernel_size, padding=kernel_size // 2),
            nn.GELU(),
            nn.Dropout(p=dropout)
        )
        self.delta_head = nn.Conv1d(d_model, num_features, kernel_size=1)
        self.gate_head = nn.Conv1d(d_model, num_features, kernel_size=1)
        # Initialize gate weights and bias to 0 so gate is identically 1.0 (neutral baseline) at step 0
        nn.init.zeros_(self.gate_head.weight)
        nn.init.zeros_(self.gate_head.bias)

    def forward(self, h: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:

        # h: (B, d_model, T)
        feat = self.post_conv(h)
        delta = self.delta_head(feat)
        gate = 2.0 * torch.sigmoid(self.gate_head(feat))
        return delta, gate

class CTDITemporalTransformer(nn.Module):
    """
    Upgraded CTDI Spatio-Temporal Imputation Transformer:
    1. Multi-scale temporal feature mixing (k=1, 3, 5, 7)
    2. Vectorized structural missingness gap features (dt_prev, dt_next, gap_len, boundary)
    3. Cross-pollutant interaction projection
    4. Pre-LN Temporal Transformer Encoder (multi-head self-attention across 24h)
    5. Gated residual correction head (learned amplitude scaling [0, 2])
    6. Exact observation lock: x_imputed = mask * x_obs + (1 - mask) * x_pred
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
        window_size: int = 24,
        use_gap_features: bool = False,
        use_multiscale: bool = False,
        use_gated_residual: bool = False
    ):

        super().__init__()
        self.num_features = num_features
        self.num_context = num_context
        self.d_model = d_model
        self.window_size = window_size
        self.use_gap_features = use_gap_features
        self.use_multiscale = use_multiscale
        self.use_gated_residual = use_gated_residual
        
        # Channel calculation:
        # Base: pollutants_obs (num_features) + mask (num_features) + p_interp (num_features) + context
        base_channels = 3 * num_features + num_context
        gap_channels = 4 * num_features if use_gap_features else 0
        in_channels = base_channels + gap_channels
        
        if use_multiscale:
            self.pre_conv = MultiScaleTemporalBlock(in_channels=in_channels, out_channels=d_model)
        else:
            self.pre_conv = nn.Sequential(
                nn.Conv1d(in_channels=in_channels, out_channels=d_model, kernel_size=1),
                nn.BatchNorm1d(d_model),
                nn.GELU(),
                nn.Conv1d(in_channels=d_model, out_channels=d_model, kernel_size=3, padding=1),
                nn.BatchNorm1d(d_model),
                nn.GELU()
            )
            
        # Cross-pollutant interaction mixing projection
        if use_multiscale:
            self.cross_pollutant_proj = nn.Sequential(
                nn.Conv1d(d_model, d_model, kernel_size=1),
                nn.BatchNorm1d(d_model),
                nn.GELU()
            )
        else:
            self.cross_pollutant_proj = None

        
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
        
        if use_gated_residual:
            self.head = GatedResidualHead(d_model=d_model, num_features=num_features, dropout=dropout)
        else:
            self.post_conv = nn.Sequential(
                nn.Conv1d(in_channels=d_model, out_channels=d_model, kernel_size=3, padding=1),
                nn.GELU(),
                nn.Dropout(p=dropout),
                nn.Conv1d(in_channels=d_model, out_channels=num_features, kernel_size=1)
            )
            self.head = None
        
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
        if context is not None:
            pollutants_obs = x_obs
            ctx = context
        elif x_obs.shape[-1] == self.num_features + self.num_context and self.num_context > 0:
            ctx = x_obs[..., :self.num_context]
            pollutants_obs = x_obs[..., self.num_context:]
        elif x_obs.shape[-1] == self.num_features and self.num_context > 0:
            pollutants_obs = x_obs
            ctx = torch.zeros(x_obs.shape[0], x_obs.shape[1], self.num_context, device=x_obs.device)
        else:
            pollutants_obs = x_obs
            ctx = None
            
        # 1. 1D linear interpolation baseline prior
        p_interp = torch_linear_interpolate_24h(pollutants_obs, mask)
        
        # 2. Structural temporal missingness gap features
        features_list = [pollutants_obs, mask, p_interp]
        if self.use_gap_features:
            gap_feats = torch_compute_gap_features(mask)
            features_list.append(gap_feats)
        if ctx is not None:
            features_list.append(ctx)
            
        x_cat = torch.cat(features_list, dim=-1) # (B, T, Channels)
        x_trans = x_cat.transpose(1, 2)         # (B, Channels, T)
        
        # 3. Multi-scale temporal feature extraction + cross-pollutant interaction
        x_emb = self.pre_conv(x_trans)          # (B, d_model, T)
        if self.cross_pollutant_proj is not None:
            x_emb = self.cross_pollutant_proj(x_emb) # (B, d_model, T)

        
        # 4. Positional Encoding + Temporal Transformer Self-Attention
        x_seq = x_emb.transpose(1, 2)           # (B, T, d_model)
        x_pe = self.pos_encoder(x_seq)
        h = self.transformer_encoder(x_pe)      # (B, T, d_model)
        
        # 5. Gated Residual or Standard Residual Reconstruction Head
        h_trans = h.transpose(1, 2)             # (B, d_model, T)
        if self.use_gated_residual:
            delta, gate = self.head(h_trans)
            delta_pred = (gate * delta).transpose(1, 2) # (B, T, num_features)
        else:
            delta_pred = self.post_conv(h_trans).transpose(1, 2)
            
        x_pred_raw = p_interp + delta_pred
        
        # 6. Strict observation lock: preserve original values exactly
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
