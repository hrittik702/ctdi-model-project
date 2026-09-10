# 02 - Input-Process-Output Architecture

> [!INFO] Module Context
> - **Parent**: [[00 - Index (Map of Content)]]
> - **Previous**: [[01 - Problem & Real-World Impact]]
> - **Next**: [[03 - Data Engineering & Combining Sources]]
> - **Tags**: `#architecture` `#pipeline` `#deep-learning` `#transformers`

---

## 1. The High-Level Pipeline

The CTDI framework operates as a **spatial-temporal generative reconstructor**. It takes broken telemetry as input and outputs a continuous, physically consistent 24-hour sequence.

```
       INPUT                                PROCESS                             OUTPUT
┌──────────────────┐               ┌───────────────────────┐            ┌──────────────────┐
│  Broken Sequence │               │ 1. 1x1 CNN Mixer      │            │ Complete 24-Hour │
│   X_obs (24, F)  │               │    (Cross-Pollutant)  │            │ Continuous Data  │
│   (Zeros at gaps)│ ────────────> │ 2. Positional Encoding│ ─────────> │   (Zero NaNs)    │
│         +        │               │    (Hour-of-day clock)│            │                  │
│ Visibility Mask  │               │ 3. Self-Attention     │            │ Real values kept │
│   M_art (24, F)  │               │    (Temporal context) │            │ Missing values   │
│   (1=real, 0=gap)│               │ 4. Identity Replace   │            │ reconstructed!   │
└──────────────────┘               └───────────────────────┘            └──────────────────┘
```

---

## 2. Step 1: The Input

The neural network does not accept raw, unmasked data with `NaN`s. Instead, for each 24-hour window, it receives **two paired matrices**:

### A. The Observed Values Tensor: $X_{\text{obs}} \in \mathbb{R}^{B \times 24 \times F}$
- $B$ is the batch size (e.g. 64 during training, 1 during live inference).
- $T = 24$ continuous hourly intervals (e.g. `00:00` through `23:00`).
- $F = 6$ pollutant channels (`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`).
- **Missing Entry Representation**: Any missing coordinate is filled with `0.0`.

### B. The Visibility Mask Tensor: $M_{\text{art}} \in \{0.0, 1.0\}^{B \times 24 \times F}$
- Contains a binary flag for every single number in $X_{\text{obs}}$:
  $$M_{\text{art}}[t, f] = \begin{cases} 1.0, & \text{if sensor value is valid & observed} \\ 0.0, & \text{if sensor was offline / missing} \end{cases}$$

### C. Concatenation Along Channel Dimension
Before entering the network, the data and mask are concatenated:
$$\mathbf{X}_{\text{cat}} = [X_{\text{obs}} \,\|\, M_{\text{art}}] \in \mathbb{R}^{B \times 24 \times 2F}$$
For 6 pollutants, this produces a $(24 \times 12)$ matrix per sample. The model is explicitly informed: *"Here is the measurement, and here is a flag telling you whether to trust it."*

---

## 3. Step 2: The Process (Neural Brain)

```
[X_obs, M_art] (B, 24, 12)
       │
       ▼
1x1 Conv1d + BatchNorm1d + GELU (Cross-Pollutant Mixer)
       │
       ▼  Shape: (B, 24, d_model = 64)
Add Sinusoidal Positional Encoding (Hour of Day)
       │
       ▼
Temporal Transformer Encoder (2 Layers, 4 Heads)
       │
       ▼  Shape: (B, 24, 64)
Post 1x1 Conv1d (64 -> 32 -> 6)
       │
       ▼
Raw Output: X_pred_raw (B, 24, 6)
       │
       ▼
Assembly: X_imputed = M_art * X_obs + (1 - M_art) * X_pred_raw
```

### 1. Cross-Pollutant Feature Mixing ($1\times 1$ Conv1d)
Pollutants do not behave randomly; they obey strict atmospheric chemistry:
- High $\text{PM}_{10}$ usually indicates high $\text{PM}_{2.5}$ because both originate from combustion and road dust.
- Solar radiation converts $\text{NO}_2$ into $\text{O}_3$ via photolysis.
The $1\times 1$ Conv1d layer acts as a **pointwise feature mixer**, learning linear and non-linear combinations across all 12 input channels and projecting them into an internal representation space $d_{\text{model}} = 64$.

### 2. Diurnal Rhythm (Sinusoidal Positional Encoding)
Cities follow predictable diurnal patterns:
- Morning rush hour ($07:00 - 09:00$) and evening rush hour ($17:00 - 20:00$).
- Atmospheric boundary layer collapse at midnight (trapping emissions near the ground).
Sinusoidal positional encoding gives each of the 24 hours a unique geometric position, enabling the attention layers to distinguish between noon and midnight.

### 3. Temporal Self-Attention
The multi-head attention mechanism computes attention scores across all 24 hours:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
If a sensor drops out between 14:00 and 18:00, the attention heads attend to the trajectory before the gap (10:00–13:00) and the trajectory after the gap (19:00–23:00) to deduce what must have happened in between.

### 4. Identity Preservation
A fundamental rule of scientific data imputation is **zero corruption of observed telemetry**:
$$X_{\text{imputed}}[t, f] = M_{\text{art}}[t, f] \cdot X_{\text{obs}}[t, f] + (1 - M_{\text{art}}[t, f]) \cdot X_{\text{pred\_raw}}[t, f]$$
If a point was physically measured by a working sensor, the model **keeps the exact measured value**. Only the gaps receive the neural prediction.

---

## 4. Step 3: The Output

The system produces two distinct outputs:

### 1. The Reconstructed Telemetry Matrix
- Shape: $(24, 6)$ in physical scientific units ($\mu g/m^3$).
- Zero `NaN` values.
- Seamlessly continuous and ready for plotting, dashboard viewing, or feeding into downstream AI pipelines.

### 2. Rigorous Validation Metrics
- **MAE (Mean Absolute Error)**: Average deviation from ground truth in $\mu g/m^3$.
- **RMSE (Root Mean Square Error)**: Heavily penalizes large unpredicted spike errors.
- **Percentage Improvement**: Evaluates error reduction compared to classical baselines:
  $$\text{Gain} = \frac{\text{MAE}_{\text{linear}} - \text{MAE}_{\text{transformer}}}{\text{MAE}_{\text{linear}}} \times 100\%$$

---

👉 **Next Step**: Read [[03 - Data Engineering & Combining Sources]] to learn how to add your own data and combine multiple sensor files.
