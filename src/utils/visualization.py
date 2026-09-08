"""Visualization utilities for 24-hour actual vs. imputed air pollution sequences."""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
from src.data.preprocessing import AirPollutionScaler

def plot_24h_imputation_comparison(
    sample_idx: int,
    x_test_true: np.ndarray,
    m_test_art: np.ndarray,
    eval_mask: np.ndarray,
    imputations: Dict[str, np.ndarray],
    feature_names: List[str],
    timestamps: Optional[np.ndarray] = None,
    scaler: Optional[AirPollutionScaler] = None,
    target_pollutant: str = "PM2.5",
    save_path: Optional[str] = "results/plots/actual_vs_imputed_sample.png"
) -> str:
    """
    Plots a 24-hour air pollution trajectory comparing Ground Truth, Observed points,
    and reconstructions from different models for a chosen pollutant.
    """
    if target_pollutant not in feature_names:
        feat_idx = 0
        target_pollutant = feature_names[0]
    else:
        feat_idx = feature_names.index(target_pollutant)
        
    hours = np.arange(24)
    time_labels = [f"{h:02d}:00" for h in hours]
    if timestamps is not None and sample_idx < len(timestamps):
        sample_ts = timestamps[sample_idx]
        if hasattr(sample_ts[0], "strftime"):
            time_labels = [ts.strftime("%H:%M") for ts in sample_ts]
            
    # Physical or normalized values
    if scaler is not None:
        y_true = scaler.inverse_transform_array(x_test_true[sample_idx:sample_idx+1])[0, :, feat_idx]
        unit_label = r"$\mu g / m^3$"
    else:
        y_true = x_test_true[sample_idx, :, feat_idx]
        unit_label = "Normalized Units"
        
    obs_mask = m_test_art[sample_idx, :, feat_idx] == 1.0
    art_hidden_mask = eval_mask[sample_idx, :, feat_idx] == 1.0
    
    plt.figure(figsize=(12, 6), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # 1. Ground Truth complete 24h curve
    plt.plot(hours, y_true, label="Ground Truth (Actual)", color="#111827", linewidth=2.5, linestyle="-", zorder=3)
    
    # 2. Observed points (visible to model)
    if np.any(obs_mask):
        plt.scatter(hours[obs_mask], y_true[obs_mask], color="#2563EB", s=60, label="Observed Points (Visible)", zorder=4, edgecolor="black", linewidth=0.5)
        
    # 3. Artificially hidden points (ground truth target)
    if np.any(art_hidden_mask):
        plt.scatter(hours[art_hidden_mask], y_true[art_hidden_mask], facecolors="none", edgecolors="#DC2626", s=110, linewidth=2, label="Hidden Ground Truth", zorder=5)
        
    # 4. Model Imputations
    color_palette = {
        "Mean": "#9CA3AF",
        "Linear_Interpolation": "#F59E0B",
        "KNN": "#8B5CF6",
        "MLP": "#06B6D4",
        "Temporal_Transformer": "#10B981"
    }
    
    style_palette = {
        "Mean": ":",
        "Linear_Interpolation": "--",
        "KNN": "-.",
        "MLP": "-.",
        "Temporal_Transformer": "-"
    }
    
    for model_name, imp_arr in imputations.items():
        if scaler is not None:
            y_imp = scaler.inverse_transform_array(imp_arr[sample_idx:sample_idx+1])[0, :, feat_idx]
        else:
            y_imp = imp_arr[sample_idx, :, feat_idx]
            
        color = color_palette.get(model_name, "#4B5563")
        linestyle = style_palette.get(model_name, "--")
        linewidth = 2.4 if "Transformer" in model_name else 1.6
        
        plt.plot(hours, y_imp, label=f"Imputed: {model_name}", color=color, linestyle=linestyle, linewidth=linewidth, alpha=0.9, zorder=3)
        
    plt.title(f"24-Hour Air Pollution Imputation | {target_pollutant} (Sample #{sample_idx})", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Hour of Day", fontsize=12, labelpad=8)
    plt.ylabel(f"{target_pollutant} Concentration ({unit_label})", fontsize=12, labelpad=8)
    plt.xticks(hours[::2], time_labels[::2], rotation=0)
    plt.legend(frameon=True, facecolor="white", edgecolor="#E5E7EB", loc="best", fontsize=10)
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"[Visualization] Saved 24h actual-vs-imputed plot to {save_path}")
        
    plt.close()
    return save_path

def plot_multichannel_comparison(
    sample_idx: int,
    x_test_true: np.ndarray,
    eval_mask: np.ndarray,
    imputations: Dict[str, np.ndarray],
    feature_names: List[str],
    scaler: Optional[AirPollutionScaler] = None,
    save_path: Optional[str] = "results/plots/multichannel_comparison.png"
) -> str:
    """
    Plots a multi-panel subplot grid showing all pollutants for a 24-hour sequence.
    """
    num_feats = min(6, len(feature_names))
    fig, axes = plt.subplots(num_feats, 1, figsize=(12, 2.5 * num_feats), sharex=True, dpi=300)
    if num_feats == 1:
        axes = [axes]
        
    hours = np.arange(24)
    
    if scaler is not None:
        true_phys = scaler.inverse_transform_array(x_test_true[sample_idx:sample_idx+1])[0]
        imp_phys_dict = {
            m: scaler.inverse_transform_array(arr[sample_idx:sample_idx+1])[0]
            for m, arr in imputations.items()
        }
    else:
        true_phys = x_test_true[sample_idx]
        imp_phys_dict = {m: arr[sample_idx] for m, arr in imputations.items()}
        
    for f in range(num_feats):
        ax = axes[f]
        feat_name = feature_names[f]
        y_true = true_phys[:, f]
        hidden_mask = eval_mask[sample_idx, :, f] == 1.0
        
        ax.plot(hours, y_true, color="#111827", label="Actual", linewidth=2.0)
        if np.any(hidden_mask):
            ax.scatter(hours[hidden_mask], y_true[hidden_mask], edgecolors="#DC2626", facecolors="none", s=70, linewidth=1.8, label="Hidden Actual")
            
        if "Linear_Interpolation" in imp_phys_dict:
            ax.plot(hours, imp_phys_dict["Linear_Interpolation"][:, f], color="#F59E0B", linestyle="--", label="Linear Interp")
        if "Temporal_Transformer" in imp_phys_dict:
            ax.plot(hours, imp_phys_dict["Temporal_Transformer"][:, f], color="#10B981", linestyle="-", linewidth=2.2, label="Temporal Transformer")
            
        ax.set_ylabel(feat_name, fontweight="bold", fontsize=10)
        if f == 0:
            ax.legend(loc="upper right", ncol=4, fontsize=9)
            
    axes[-1].set_xlabel("Hour of Day (24h Window)", fontsize=11)
    fig.suptitle(f"Multi-Pollutant Reconstruction (Test Sample #{sample_idx})", fontsize=13, fontweight="bold")
    fig.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path)
        print(f"[Visualization] Saved multichannel plot to {save_path}")
        
    plt.close(fig)
    return save_path
