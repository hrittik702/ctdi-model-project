# 05 - Feature Engineering & Normalization

> **Previous**: [[04 - Spatial Alignment & 13-Channel Formulation]] | **Next**: [[06 - 24-Hour Sliding Window Segmentation]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Overview

Before training deep generative diffusion models or transformers, numerical features must be:
1. **Chronologically Partitioned**: Separated into Train, Validation, and Test sets without look-ahead bias.
2. **Normalized**: Scaled to zero mean and unit variance (or $[0, 1]$ bounds) using statistics derived **strictly from the training split** (the Zero Data Leakage rule).
3. **Temporally Encoded**: Augmented with cyclical sine/cosine embeddings that capture diurnal (daily) and seasonal rhythms without mathematical discontinuities at midnight or year-end.

---

## 2. Chronological Dataset Partitioning

In time-series modeling, random shuffling produces catastrophic data leakage (the model memorizes the future to predict the past). Therefore, we apply strict chronological splitting:

```
[2019-01-01 00:00]                                                                   [2021-12-31 23:00]
├───────────────────────────────────────────────────────┼───────────────────┼───────────────────┤
│                   TRAIN (70%)                         │     VAL (15%)     │     TEST (15%)    │
│            ~18,412 continuous hours                   │   ~3,946 hours    │   ~3,946 hours    │
│            2019-01-01 to 2021-02-05                   │ 2021-02 to 2021-07│ 2021-07 to 2021-12│
└───────────────────────────────────────────────────────┴───────────────────┴───────────────────┘
```

| Split | Ratio | Time Interval | Total Hours | Total Values ($16 \text{ stns} \times 13 \text{ ch}$) |
| :---: | :---: | :--- | :---: | :---: |
| **Train** | $70\%$ | `2019-01-01 00:00` to `2021-02-05 06:00` | $18,412$ | $3,829,696$ |
| **Validation** | $15\%$ | `2021-02-05 07:00` to `2021-07-19 16:00` | $3,946$ | $820,768$ |
| **Test** | $15\%$ | `2021-07-19 17:00` to `2021-12-31 23:00` | $3,946$ | $820,768$ |
| **Total** | $100\%$ | `2019-01-01 00:00` to `2021-12-31 23:00` | **26,304** | **5,471,232** |

---

## 3. Data Normalization (The Zero-Leakage Rule)

```
[Raw Train Data (Observed Only)] ──> Compute (Mean μ_c, Std σ_c) ──> Store in scalers.json
                                                                            │
      ┌─────────────────────────────────────────────────────────────────────┴─────────────┐
      ▼                                                                     ▼             ▼
Train Normalized:                                                    Val Normalized: Test Normalized:
(X_train - μ) / σ                                                    (X_val - μ) / σ (X_test - μ) / σ
```

### 3.1 Z-Score Standardization
For each channel $c \in [0, 12]$, mean $\mu_c$ and standard deviation $\sigma_c$ are calculated **strictly over the observed cells ($\mathbf{M}_{\text{obs}} = 1$) in the Training set**:

$$\mu_c = \frac{\sum_{s, t \in \text{Train}} \mathbf{M}_{\text{obs}}[s, t, c] \cdot \mathbf{X}[s, t, c]}{\sum_{s, t \in \text{Train}} \mathbf{M}_{\text{obs}}[s, t, c]}$$

$$\sigma_c = \sqrt{\frac{\sum_{s, t \in \text{Train}} \mathbf{M}_{\text{obs}}[s, t, c] \cdot \big(\mathbf{X}[s, t, c] - \mu_c\big)^2}{\sum_{s, t \in \text{Train}} \mathbf{M}_{\text{obs}}[s, t, c]} + \epsilon}$$

where $\epsilon = 10^{-6}$ prevents division by zero.

### 3.2 Transforming the Data
$$\mathbf{X}_{\text{norm}}[s, t, c] = \frac{\mathbf{X}[s, t, c] - \mu_c}{\sigma_c}$$

- **Inverse Transform (for Evaluation)**: When the model outputs imputed predictions $\hat{\mathbf{X}}_{\text{norm}}$, they are inverted back to original units ($\mu\text{g/m}^3, ^\circ\text{C}$, etc.) before computing physical metrics:
  $$\hat{\mathbf{X}}_{\text{phys}}[s, t, c] = \hat{\mathbf{X}}_{\text{norm}}[s, t, c] \cdot \sigma_c + \mu_c$$

### 3.3 Artifact Storage
The parameters $\{\mu_c, \sigma_c\}_{c=0}^{12}$ are saved to `data/processed/scalers.json` so inference and evaluation can reproduce the exact scaling.

---

## 4. Cyclical Temporal Embeddings

Linear time representations (e.g. Hour = $0, 1, ..., 23$) introduce an artificial discontinuity between 23:00 and 00:00 (a distance of 23 instead of 1). We map continuous timestamps onto circular sine and cosine coordinates:

```
                  HOUR CYCLICAL CIRCLE (24 Hours)
                             00:00 (Midnight)
                             [sin=0, cos=1]
                                    │
       06:00 (Dawn)                 │                 18:00 (Dusk)
    [sin=1, cos=0] ─────────────────┼──────────────── [sin=-1, cos=0]
                                    │
                                    │
                             12:00 (Noon)
                            [sin=0, cos=-1]
```

### Mathematical Definitions
1. **Hour of Day ($h \in [0, 23]$)**:
   $$\text{Hour}_{\sin} = \sin\left(\frac{2\pi h}{24}\right), \quad \text{Hour}_{\cos} = \cos\left(\frac{2\pi h}{24}\right)$$
2. **Day of Week ($d \in [0, 6]$)**:
   $$\text{Day}_{\sin} = \sin\left(\frac{2\pi d}{7}\right), \quad \text{Day}_{\cos} = \cos\left(\frac{2\pi d}{7}\right)$$
3. **Month of Year ($m \in [1, 12]$)**:
   $$\text{Month}_{\sin} = \sin\left(\frac{2\pi (m - 1)}{12}\right), \quad \text{Month}_{\cos} = \cos\left(\frac{2\pi (m - 1)}{12}\right)$$

These 6 cyclical features can either be concatenated into the temporal positional encoding of the Transformer/UNet or appended as auxiliary conditioning channels.
