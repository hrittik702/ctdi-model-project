"""Interactive Streamlit Dashboard for Air Pollution Imputation Exploration."""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import torch

from src.models.temporal_transformer import CTDITemporalTransformer
from src.data.masking import generate_artificial_mask, prepare_masked_inputs
from src.evaluation.metrics import compute_all_metrics

# Streamlit Page Config
st.set_page_config(
    page_title="Air Pollution Imputation UI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2563EB;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_cached_evaluation(cache_path="results/eval_cache.npz"):
    if not os.path.exists(cache_path):
        st.error(f"Cache file {cache_path} not found. Please run 'python src/evaluation/export_cache.py' first.")
        st.stop()
    data = np.load(cache_path, allow_pickle=True)
    return {
        "x_test_true_phys": data["x_test_true_phys"],
        "x_test_true_norm": data["x_test_true_norm"],
        "x_test_obs": data["x_test_obs"],
        "m_test_art": data["m_test_art"],
        "m_test_eval": data["m_test_eval"],
        "imp_transformer": data["imp_transformer"],
        "imp_linear": data["imp_linear"],
        "imp_knn": data["imp_knn"],
        "imp_mlp": data["imp_mlp"],
        "imp_mean": data["imp_mean"],
        "pollutants": list(data["pollutants"]),
        "means": data["means"],
        "stds": data["stds"],
        "timestamps": data["timestamps"]
    }

@st.cache_data
def load_summary_csv(csv_path="results/metrics_summary.csv"):
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

cache = load_cached_evaluation()
summary_df = load_summary_csv()

num_samples = len(cache["x_test_true_phys"])
pollutants = cache["pollutants"]

# Sidebar
st.sidebar.markdown("### ⚙️ Navigation & Controls")
sample_idx = st.sidebar.slider("Select 24h Window Sample", min_value=0, max_value=num_samples - 1, value=0, step=1)
target_pollutant = st.sidebar.selectbox("Select Target Pollutant", pollutants, index=0)

feat_idx = pollutants.index(target_pollutant)
sample_timestamps = cache["timestamps"][sample_idx]
time_range_str = f"{sample_timestamps[0]} → {sample_timestamps[-1]}"
st.sidebar.caption(f"📅 **Time Window:** {time_range_str}")

st.sidebar.markdown("---")
st.sidebar.markdown("#### Model Visibility")
show_ground_truth = st.sidebar.checkbox("Ground Truth (Actual)", value=True)
show_observed = st.sidebar.checkbox("Observed Points (Visible)", value=True)
show_hidden_truth = st.sidebar.checkbox("Hidden Ground Truth Target", value=True)
show_transformer = st.sidebar.checkbox("CTDI Temporal Transformer", value=True)
show_linear = st.sidebar.checkbox("Linear Interpolation", value=True)
show_knn = st.sidebar.checkbox("KNN Imputer", value=False)
show_mlp = st.sidebar.checkbox("MLP Autoencoder", value=False)
show_mean = st.sidebar.checkbox("Mean Baseline", value=False)

# Main Area Header
st.markdown('<div class="main-title">🌍 CTDI Air Pollution Imputation Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive visual exploration of 24-hour sequence reconstructions, missingness masks, and multi-model benchmark results.</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 24h Trajectory Explorer",
    "📊 Multi-Pollutant Grid",
    "🏆 Benchmark Scoreboard",
    "🧪 Live Imputation Sandbox"
])

# ----------------- TAB 1: 24h Trajectory Explorer -----------------
with tab1:
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    # Calculate sample-specific MAE
    y_true_s = cache["x_test_true_phys"][sample_idx, :, feat_idx]
    mask_eval_s = cache["m_test_eval"][sample_idx, :, feat_idx] == 1.0
    num_hidden = int(np.sum(mask_eval_s))
    
    tf_pred_s = cache["imp_transformer"][sample_idx, :, feat_idx]
    lin_pred_s = cache["imp_linear"][sample_idx, :, feat_idx]
    
    tf_sample_mae = np.mean(np.abs(tf_pred_s[mask_eval_s] - y_true_s[mask_eval_s])) if num_hidden > 0 else 0.0
    lin_sample_mae = np.mean(np.abs(lin_pred_s[mask_eval_s] - y_true_s[mask_eval_s])) if num_hidden > 0 else 0.0
    
    with col_metric1:
        st.metric(label="Target Pollutant", value=target_pollutant)
    with col_metric2:
        st.metric(label="Artificially Hidden Hours", value=f"{num_hidden} / 24 hrs")
    with col_metric3:
        st.metric(label="Transformer Sample MAE", value=f"{tf_sample_mae:.2f} µg/m³")
    with col_metric4:
        st.metric(label="Linear Interp Sample MAE", value=f"{lin_sample_mae:.2f} µg/m³", delta=f"{tf_sample_mae - lin_sample_mae:.2f} µg/m³", delta_color="inverse")
        
    # Plotly Figure
    hours = np.arange(24)
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    fig = go.Figure()
    
    # Ground Truth
    if show_ground_truth:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=y_true_s,
            mode='lines',
            name='Ground Truth (Actual)',
            line=dict(color='#111827', width=3),
            hoverinfo='x+y+name'
        ))
        
    # Observed points
    obs_mask_s = cache["m_test_art"][sample_idx, :, feat_idx] == 1.0
    if show_observed and np.any(obs_mask_s):
        fig.add_trace(go.Scatter(
            x=[hour_labels[h] for h in hours if obs_mask_s[h]],
            y=y_true_s[obs_mask_s],
            mode='markers',
            name='Observed (Visible)',
            marker=dict(color='#2563EB', size=10, line=dict(color='white', width=1)),
            hoverinfo='x+y+name'
        ))
        
    # Hidden ground truth
    if show_hidden_truth and np.any(mask_eval_s):
        fig.add_trace(go.Scatter(
            x=[hour_labels[h] for h in hours if mask_eval_s[h]],
            y=y_true_s[mask_eval_s],
            mode='markers',
            name='Hidden Actual Target',
            marker=dict(symbol='circle-open', color='#DC2626', size=14, line=dict(width=2.5)),
            hoverinfo='x+y+name'
        ))
        
    # Model reconstructions
    if show_transformer:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=tf_pred_s,
            mode='lines',
            name='CTDI Temporal Transformer',
            line=dict(color='#10B981', width=3),
            hoverinfo='x+y+name'
        ))
    if show_linear:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=lin_pred_s,
            mode='lines',
            name='Linear Interpolation',
            line=dict(color='#F59E0B', width=2, dash='dash'),
            hoverinfo='x+y+name'
        ))
    if show_knn:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=cache["imp_knn"][sample_idx, :, feat_idx],
            mode='lines',
            name='KNN Imputer',
            line=dict(color='#8B5CF6', width=2, dash='dashdot'),
            hoverinfo='x+y+name'
        ))
    if show_mlp:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=cache["imp_mlp"][sample_idx, :, feat_idx],
            mode='lines',
            name='MLP Baseline',
            line=dict(color='#06B6D4', width=2, dash='dot'),
            hoverinfo='x+y+name'
        ))
    if show_mean:
        fig.add_trace(go.Scatter(
            x=hour_labels, y=cache["imp_mean"][sample_idx, :, feat_idx],
            mode='lines',
            name='Mean Baseline',
            line=dict(color='#9CA3AF', width=2, dash='dot'),
            hoverinfo='x+y+name'
        ))
        
    fig.update_layout(
        title=f"<b>24-Hour Sequence Imputation Comparison: {target_pollutant}</b> (Sample #{sample_idx})",
        xaxis_title="Hour of Day",
        yaxis_title=f"{target_pollutant} Concentration (µg/m³)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        hovermode="x unified",
        height=540,
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ----------------- TAB 2: Multi-Pollutant Grid -----------------
with tab2:
    st.markdown(f"#### Synchronized 24-Hour View Across All 6 Pollutants (Sample #{sample_idx})")
    
    fig_grid = make_subplots(
        rows=3, cols=2,
        subplot_titles=[f"<b>{p}</b>" for p in pollutants],
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    positions = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]
    
    for idx, p in enumerate(pollutants):
        row, col = positions[idx]
        y_true_p = cache["x_test_true_phys"][sample_idx, :, idx]
        m_eval_p = cache["m_test_eval"][sample_idx, :, idx] == 1.0
        tf_p = cache["imp_transformer"][sample_idx, :, idx]
        lin_p = cache["imp_linear"][sample_idx, :, idx]
        
        # Ground truth
        fig_grid.add_trace(
            go.Scatter(x=hour_labels, y=y_true_p, mode='lines', line=dict(color='#111827', width=2), showlegend=(idx==0), name="Actual"),
            row=row, col=col
        )
        # Hidden targets
        if np.any(m_eval_p):
            fig_grid.add_trace(
                go.Scatter(x=[hour_labels[h] for h in hours if m_eval_p[h]], y=y_true_p[m_eval_p], mode='markers',
                           marker=dict(symbol='circle-open', color='#DC2626', size=8, line=dict(width=2)),
                           showlegend=(idx==0), name="Hidden Actual"),
                row=row, col=col
            )
        # Linear
        fig_grid.add_trace(
            go.Scatter(x=hour_labels, y=lin_p, mode='lines', line=dict(color='#F59E0B', width=1.5, dash='dash'), showlegend=(idx==0), name="Linear Interp"),
            row=row, col=col
        )
        # Transformer
        fig_grid.add_trace(
            go.Scatter(x=hour_labels, y=tf_p, mode='lines', line=dict(color='#10B981', width=2.5), showlegend=(idx==0), name="Temporal Transformer"),
            row=row, col=col
        )
        
    fig_grid.update_layout(
        height=800,
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_grid, use_container_width=True)

# ----------------- TAB 3: Benchmark Scoreboard -----------------
with tab3:
    st.markdown("#### Overall Test Set Performance on Artificially Hidden Positions")
    if summary_df is not None:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### 📋 Summary Table")
            st.dataframe(summary_df.style.highlight_min(subset=["MAE (Original Units)", "RMSE (Original Units)", "MAPE (%)"], color="#D1FAE5"), use_container_width=True)
            
            st.info("""
            **Key Evaluation Properties:**
            - **Strict Observation Masking**: Error metrics are evaluated **exclusively on artificially hidden positions** where ground truth was known and withheld.
            - **Zero Normalization Leakage**: Standardization statistics (mean/std) were fit exclusively on training data.
            """)
            
        with c2:
            st.markdown("##### 📊 Comparative Error Chart")
            bar_fig = go.Figure(data=[
                go.Bar(name='MAE (µg/m³)', x=summary_df['Model'], y=summary_df['MAE (Original Units)'], marker_color='#3B82F6'),
                go.Bar(name='RMSE (µg/m³)', x=summary_df['Model'], y=summary_df['RMSE (Original Units)'], marker_color='#EF4444')
            ])
            bar_fig.update_layout(
                barmode='group',
                template="plotly_white",
                height=380,
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title="Model",
                yaxis_title="Error (µg/m³)"
            )
            st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.warning("No summary CSV found at results/metrics_summary.csv")

# ----------------- TAB 4: Live Imputation Sandbox -----------------
with tab4:
    st.markdown("#### 🧪 Test Live Custom Missingness Rates")
    st.markdown("Select a missingness rate or pattern, and run live inference using our trained CTDI Temporal Transformer checkpoint.")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        live_missing_rate = st.slider("Simulated Missing Rate", min_value=0.10, max_value=0.80, value=0.40, step=0.05)
    with col_s2:
        live_mechanism = st.selectbox("Missingness Pattern", ["random (MCAR)", "block (consecutive hours)"])
    with col_s3:
        live_seed = st.number_input("Random Seed", value=42, step=1)
        
    if st.button("🚀 Run Live Imputation on Current Sample", type="primary"):
        with st.spinner("Executing forward pass through CTDI Temporal Transformer..."):
            # Prepare sample
            norm_sample = cache["x_test_true_norm"][sample_idx:sample_idx+1]  # (1, 24, F)
            m_obs_sample = np.ones_like(norm_sample)
            
            mech = "random" if "random" in live_mechanism else "block"
            m_art_live, m_eval_live = generate_artificial_mask(
                m_obs_sample, missing_rate=live_missing_rate, mechanism=mech, seed=live_seed
            )
            x_obs_live = prepare_masked_inputs(norm_sample, m_art_live)
            
            # Run model
            ckpt_path = "checkpoints/transformer/best_temporal_transformer.pt"
            num_feats = len(pollutants)
            model = CTDITemporalTransformer(num_features=num_feats, d_model=64, nhead=4, num_layers=2)
            model.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
            model.eval()
            
            with torch.no_grad():
                t_obs = torch.tensor(x_obs_live, dtype=torch.float32)
                t_mask = torch.tensor(m_art_live, dtype=torch.float32)
                imp_norm, _ = model(t_obs, t_mask)
                imp_norm = imp_norm.cpu().numpy()
                
            # Inverse transform
            means = cache["means"]
            stds = cache["stds"]
            live_true_phys = norm_sample * stds + means
            live_imp_phys = imp_norm * stds + means
            
            live_mae = np.mean(np.abs(live_imp_phys[m_eval_live == 1.0] - live_true_phys[m_eval_live == 1.0]))
            
            st.success(f"Imputation completed! Reconstructed {int(np.sum(m_eval_live))} missing values with MAE: **{live_mae:.2f} µg/m³**")
            
            # Plot
            fig_live = go.Figure()
            y_live_true = live_true_phys[0, :, feat_idx]
            y_live_imp = live_imp_phys[0, :, feat_idx]
            m_live_eval = m_eval_live[0, :, feat_idx] == 1.0
            m_live_obs = m_art_live[0, :, feat_idx] == 1.0
            
            fig_live.add_trace(go.Scatter(x=hour_labels, y=y_live_true, mode='lines', name='Actual Ground Truth', line=dict(color='#111827', width=2.5)))
            fig_live.add_trace(go.Scatter(x=[hour_labels[h] for h in hours if m_live_obs[h]], y=y_live_true[m_live_obs], mode='markers', name='Observed', marker=dict(color='#2563EB', size=10)))
            fig_live.add_trace(go.Scatter(x=[hour_labels[h] for h in hours if m_live_eval[h]], y=y_live_true[m_live_eval], mode='markers', name='Artificially Hidden', marker=dict(symbol='circle-open', color='#DC2626', size=14, line=dict(width=2.5))))
            fig_live.add_trace(go.Scatter(x=hour_labels, y=y_live_imp, mode='lines', name='Live Imputed (CTDI Transformer)', line=dict(color='#10B981', width=3)))
            
            fig_live.update_layout(
                title=f"Live Custom Imputation: {target_pollutant} at {int(live_missing_rate*100)}% Missingness",
                template="plotly_white",
                height=450,
                xaxis_title="Hour of Day",
                yaxis_title=f"{target_pollutant} (µg/m³)"
            )
            st.plotly_chart(fig_live, use_container_width=True)
