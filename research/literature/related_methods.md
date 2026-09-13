# Related Imputation Methods & Comparative Analysis

---

## 1. Taxonomic Overview of Imputation Paradigms

Missing data imputation methods can be categorized into four methodological generations:

```
Generational Paradigm:
1. Classical Statistical    (Mean, Linear/Spline, KNN, MICE)
         ↓
2. Autoregressive / RNN DL   (GRU-D, BRITS, NAOMI)
         ↓
3. Deterministic Transformer (SAITS, CTDI)
         ↓
4. Generative Diffusion     (CSDI, PriSTI, SLM-Diffusion [Ours])
```

---

## 2. Detailed Method Comparison

| Model | Citation & Venue | Architecture Type | Modeling Strengths | Known Failure Modes / Limitations | Relation to Our Project |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BRITS** | Cao et al., *NeurIPS 2018* | Bidirectional RNN with dynamical decay | Models non-linear temporal correlations and tracks time gaps dynamically. | Recurrent structure is slow; cannot capture multi-station spatial dependencies; deterministic. | Standard deterministic DL baseline. |
| **SAITS** | Du et al., *Expert Syst. Appl. 2023* | Dual self-attention Transformer | Fast parallel training; explicitly models cross-variable and cross-time attention. | Lacks spatial graph geometry; produces point estimates with zero uncertainty quantification. | Competitive transformer baseline. |
| **CSDI** | Tashiro et al., *NeurIPS 2021* | Conditional Score-based Diffusion | First robust diffusion model for multivariate time series; yields probabilistic samples. | Quadratic attention across flattened features; ignores spatial geographic topology; tabular only. | Foundational diffusion framework from which our denoiser is developed. |
| **PriSTI** | Du et al., *KDD 2023* | Spatio-temporal diffusion with graph prior | Incorporates geographic distance matrix as spatial prior; separates spatial and temporal denoising. | Designed strictly for univariate spatial networks (traffic speeds); lacks multi-modal chemical coupling and semantic context. | Informs our spatial graph convolution design. |
| **CTDI** | Yu et al., *IEEE TBD 2025* | CNN-Transformer (State of Art) | CNN for local spatial urban features + Transformer for long-range temporal trends. Tested on Hong Kong. | Deterministic point regression; lacks predictive distributions; treats weather/traffic purely as numerical floats. | **Primary published competitive target**. |
| **SLM-Diffusion (Ours)** | *Proposed* | SLM-Conditioned Generative Diffusion | Combines natural-language synoptic atmospheric context with spatial graph priors and probabilistic diffusion sampling. | Higher test-time sampling latency compared to single-pass feedforward models. | **Our research contribution**. |

---

## 3. Methodological Justification for Diffusion over GANs & VAEs

1. **Against GANs (e.g., GAIN)**: GANs rely on adversarial min-max games that suffer from mode collapse, discriminator saturation, and hyperparameter sensitivity on continuous environmental time-series.
2. **Against VAEs (e.g., GP-VAE)**: VAEs compress inputs into a single low-dimensional Gaussian latent vector $\mathbf{z}$, which acts as an informational bottleneck. When reconstructing high-frequency temporal spikes (such as abrupt pollution surges), VAEs produce overly smooth, blurry averages.
3. **For Conditional Diffusion**: Denoising diffusion defines a tractable forward marginal distribution and reverses noise addition through iterative score matching. This preserves fine-grained physical variance, multi-modal distributions, and high-frequency peaks.
