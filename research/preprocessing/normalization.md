# Normalization & Zero Data Leakage Protocol

---

## 1. Zero Data Leakage Rule

In time-series machine learning, fitting scalers across the full dataset contaminates the training set with test-set distribution statistics (extreme values, mean, variance).

**MANDATORY PROTOCOL**:
1. All normalization scalers (Min-Max or Standard Z-score) must be computed **strictly on observed values ($\mathbf{M}_{\text{obs}} = 1$) within the Training partition only** (`2019-01-01 00:00` to `2021-02-05 03:00`, $18,412$ hours).
2. The Validation and Test sets are transformed using these frozen training statistics.
3. Test-set observations must never influence any scaling parameter.

---

## 2. Mathematical Scaling Formulations

### 2.1 Standard Z-Score Normalization (Default for Diffusion)
For each channel $c \in \{1, \dots, C\}$:
$$\mu_c = \frac{\sum_{s=1}^S \sum_{t \in \mathcal{T}_{\text{train}}} M_{s,t,c} X_{s,t,c}}{\sum_{s=1}^S \sum_{t \in \mathcal{T}_{\text{train}}} M_{s,t,c}}$$

$$\sigma_c = \sqrt{\frac{\sum_{s=1}^S \sum_{t \in \mathcal{T}_{\text{train}}} M_{s,t,c} (X_{s,t,c} - \mu_c)^2}{\sum_{s=1}^S \sum_{t \in \mathcal{T}_{\text{train}}} M_{s,t,c}}}$$

$$\tilde{X}_{s,t,c} = \frac{X_{s,t,c} - \mu_c}{\sigma_c + \epsilon}$$

### 2.2 Preservation of Scaler Parameters
All computed parameters ($\mu_c, \sigma_c, \min_c, \max_c$) are exported to `configs/normalization_stats.json` to guarantee exact mathematical inversion during test evaluation.
