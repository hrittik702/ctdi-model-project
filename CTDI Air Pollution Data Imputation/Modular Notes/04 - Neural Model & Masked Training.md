# 04 - Neural Model & Masked Training

> [!INFO] Module Context
> - **Parent**: [[00 - Index (Map of Content)]]
> - **Previous**: [[03 - Data Engineering & Combining Sources]]
> - **Next**: [[05 - Backend Service & Diagnostics]]
> - **Tags**: `#machine-learning` `#pytorch` `#loss-function` `#baselines`

---

## 1. The Three-Mask Formulation

How do you train a neural network to reconstruct missing values when you don't know the ground truth of naturally broken data?

**The Solution**: We take valid real-world data and **artificially hide** values during training, creating three mathematical masks:

```
Observed Mask (M_obs):    [ 1  1  1  0  1  1 ]   (0 is a natural sensor NaN)
Artificially Hidden:      [ 0  1  0  0  1  1 ]   (We hide 30% of valid points)
Evaluation Mask (M_eval): [ 1  0  1  0  0  0 ]   (We ONLY grade the model here!)
```

### Mathematical Definitions:

1. **$M_{\text{obs}} \in \{0, 1\}$ (Natural Observation Mask)**:
   $$M_{\text{obs}}[t, f] = \begin{cases} 1, & \text{if sensor record is not NaN} \\ 0, & \text{if sensor naturally dropped out} \end{cases}$$
2. **$M_{\text{art}} \in \{0, 1\}$ (Model Visibility Mask)**:
   The simulated visibility mask passed to the model ($30\%$ random or block dropouts).
3. **$M_{\text{eval}} \in \{0, 1\}$ (Evaluation Mask)**:
   $$M_{\text{eval}} = M_{\text{obs}} \cdot (1 - M_{\text{art}})$$
   Equals $1$ **strictly where original data exists but was artificially hidden from the model**.

---

## 2. The Masked L1 Loss Function

- **Source**: `src/training/losses.py`
- **Class**: `MaskedImputationLoss`

Standard Mean Squared Error (MSE) would calculate loss across all cells, including cells that were already visible or cells where ground truth is unknown.

Instead, we compute loss **exclusively on $M_{\text{eval}}$**:

$$\mathcal{L}_{\text{MAE}} = \frac{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F |X_{\text{pred\_raw}}[b, t, f] - X_{\text{true}}[b, t, f]| \cdot M_{\text{eval}}[b, t, f]}{\sum_{b=1}^B \sum_{t=1}^{24} \sum_{f=1}^F M_{\text{eval}}[b, t, f] + \epsilon}$$

### Why this prevents cheating:
- The model is **never penalized** for reproducing known points ($M_{\text{art}}=1$), because those are copied directly.
- The model is **never graded** on natural sensor NaNs ($M_{\text{obs}}=0$), because there is no ground truth to verify against.
- The gradient flows **exclusively** through the predictions at the artificially hidden coordinates.

---

## 3. PyTorch Architecture Components

- **Source**: `src/models/temporal_transformer.py`
- **Class**: `CTDITemporalTransformer`

```python
# 1. Cross-Feature Mixer (1x1 Conv1d)
self.pre_conv = nn.Sequential(
    nn.Conv1d(in_channels=2 * num_features, out_channels=d_model, kernel_size=1),
    nn.BatchNorm1d(d_model),
    nn.GELU()
)

# 2. Sinusoidal Positional Encoding
self.pos_encoder = PositionalEncoding(d_model=d_model, max_len=window_size + 4)

# 3. Temporal Transformer Encoder
encoder_layer = nn.TransformerEncoderLayer(
    d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
    dropout=dropout, activation="gelu", batch_first=True
)
self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

# 4. Reconstruction Projection
self.post_conv = nn.Sequential(
    nn.Conv1d(in_channels=d_model, out_channels=d_model // 2, kernel_size=1),
    nn.GELU(),
    nn.Conv1d(in_channels=d_model // 2, out_channels=num_features, kernel_size=1)
)
```

---

## 4. Benchmark Baselines Suite

To prove that the neural architecture actually works, it is rigorously benchmarked against classical statistical and machine learning imputers on the exact same hidden points:

| Model | Technique | MAE (Norm) | MAE ($\mu g/m^3$) | Role in Research |
|---|---|---|---|---|
| **CTDI Transformer** | Spatial-Temporal Attention | **0.294** | **16.35** | **State of the Art (Winner)** |
| **Simple MLP** | Feedforward Autoencoder | 0.368 | 25.61 | Neural baseline without temporal attention |
| **Linear Interpolation** | 1D Pandas Time Interpolation | 0.404 | 25.93 | Standard environmental agency practice |
| **KNN ($k=5$)** | Distance-weighted Neighbors | 0.395 | 27.12 | Classical machine learning benchmark |
| **Mean Imputer** | Feature-wise Historical Average | 0.907 | 98.53 | Naive statistical lower bound |

### Key Benchmark Insight:
The CTDI Temporal Transformer achieves a **$37.0\%$ error reduction** over Linear Interpolation, specifically because it can reconstruct severe multi-hour block blackouts where linear cords fail.

---

👉 **Next Step**: Read [[05 - Backend Service & Diagnostics]] to learn how FastAPI serves this model and how to fix runtime issues.
