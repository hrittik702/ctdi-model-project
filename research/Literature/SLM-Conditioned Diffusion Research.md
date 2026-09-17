# SLM-Conditioned Diffusion Research

---

## 1. Research Motivation: Beyond Tabular Concatenation

In traditional environmental deep learning, auxiliary features (such as wind speed, temperature, or traffic index) are merely flattened and concatenated into an input tensor:
$$\mathbf{X}_{\text{in}} = [\mathbf{X}_{\text{pollutants}} \,\|\, \mathbf{X}_{\text{met}} \,\|\, \mathbf{X}_{\text{traffic}}] \in \mathbb{R}^{S \times K \times 13}$$

While mathematically straightforward, this approach has profound scientific limitations:
1. **Curse of Dimensionality & Local Minima**: Neural networks must deduce non-linear physical interactions (e.g., how the interaction of solar radiation, high temperature, and low wind speeds drives secondary photochemical ozone formation) entirely from point-wise float gradients.
2. **Vulnerability to Partial Outages**: If both a pollutant sensor and local meteorological sensors fail simultaneously at a station, tabular concatenation provides zero predictive signal for that spatial node.
3. **Inability to Leverage Pre-Trained Scientific Reasoning**: Large and small language models have ingested millions of tokens of scientific literature, meteorology textbooks, and atmospheric chemistry reports. Tabular models start from tabula rasa.

---

## 2. Theoretical Architecture of SLM-Conditioned Diffusion

Our framework decouples high-level atmospheric regime identification from low-level continuous numerical diffusion:

```
┌──────────────────────────────────────┐
│  24-Hour Regional Sensor Readings    │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│   Environmental Context Builder      │
│  Transforms tabular summaries into   │
│  structured atmospheric narratives   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│     Small Language Model (SLM)       │
│  (e.g., Phi-3-Mini / Gemma-2B)       │
│  Produces dense embedding z_C        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│   Conditional Diffusion Denoiser     │
│   Reverse process conditioned on     │
│   noisy x_k, mask M, and z_C         │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  Posterior Missing-Data Imputation   │
└──────────────────────────────────────┘
```

### 2.1 Context Synthesis
The deterministic `EnvironmentalContextBuilder` synthesizes structured prompts describing:
- Synoptic pressure regimes (e.g., high-pressure ridge, subtropical anticyclone, winter monsoon).
- Dispersion conditions (boundary layer ventilation index, wind shear).
- Photochemical potential (temperature, humidity, diurnal solar phase).
- Regional traffic congestion states along strategic corridors.

### 2.2 Conditioning Mechanism in Diffusion
The reverse diffusion step models the score function $\boldsymbol{\epsilon}_\theta(\mathbf{x}_k, k, \mathbf{z}_C, \mathbf{x}_0 \odot \mathbf{M})$ where $\mathbf{z}_C \in \mathbb{R}^{d}$ modulates the hidden features of the denoising network via:
1. **Adaptive Layer Normalization (AdaLN)**:
   $$\text{AdaLN}(\mathbf{h}, \mathbf{z}_C) = \gamma(\mathbf{z}_C) \odot \left( \frac{\mathbf{h} - \mu}{\sigma} \right) + \beta(\mathbf{z}_C)$$
   where $\gamma(\cdot)$ and $\beta(\cdot)$ are linear projections of $\mathbf{z}_C$.
2. **Cross-Attention**:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$
   where queries $Q$ arise from intermediate spatio-temporal features, while keys $K$ and values $V$ arise from the SLM token sequence.

---

## 3. Anticipated Research Advantages

1. **Faster Convergence**: Pre-conditioned representations provide strong directional priors, reducing the number of diffusion epochs needed to learn spatial correlations.
2. **Superior Performance on Block and Outage Scenarios**: Under 70% missingness or total station failure, the semantic context vector $\mathbf{z}_C$—derived from territory-wide conditions—keeps generated trajectories grounded in physically plausible atmospheric regimes.
3. **Calibrated Uncertainty Bounds**: Generative diffusion sampling produces calibrated posterior distributions that reflect real atmospheric stochasticity.
