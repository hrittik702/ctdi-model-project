# Architecture Decision Records

---

## Decision A01: Adoption of Small Language Model (SLM) Context Conditioning

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Standard deep imputation models (CTDI, CSDI, SAITS) operate strictly on numerical tensor floats. In extreme missingness ($70\%$), numerical representations alone often collapse to climatological means because the local numerical covariance is obliterated.

### Evidence
Meteorological and urban processes are characterized by discrete synoptic regimes (e.g., "winter continental monsoon transport", "stagnant urban inversion"). Small Language Models (SLMs, e.g., Phi-3-Mini, Gemma-2B, Llama-3.2-1B) possess rich pre-trained representations of atmospheric, physical, and spatial concepts.

### Decision
Condition the reverse diffusion process on a dense semantic context vector $\mathbf{z}_C$ synthesized by an SLM from structured natural-language descriptions of 24-hour weather and traffic conditions.

### Alternatives Considered
1. *Pure numerical concatenation*: Concatenate weather floats directly into the diffusion state.
2. *Large Foundation LLMs (e.g., GPT-4o / Claude 3.5 Sonnet via API)*: Too computationally expensive, non-reproducible, and introduces high API latency.

### Why Alternatives Were Rejected
Tabular concatenation lacks high-level regime abstraction; cloud LLMs are too slow and expensive for batch training on $26,000+$ windows. Lightweight SLMs run locally with sub-millisecond inference per window.

### Consequences
Requires building a deterministic `EnvironmentalContextBuilder` and maintaining an SLM inference pipeline during training.

### Revisit Conditions
If empirical ablations show $\mathbf{z}_C$ does not improve over tabular concatenation.

---

## Decision A02: Conditional Denoising Diffusion Probabilistic Model (DDPM) Backbone

- **Date**: 2026-09-12
- **Status**: **`ACCEPTED`**

### Context
Selecting the generative architecture for missing air pollution imputation: GANs, VAEs, or Score-Based Diffusion.

### Evidence
1. GANs suffer from mode collapse and training instability on spatial-temporal time-series.
2. VAEs produce blurry, over-smoothed imputations due to variational bottleneck constraints and single-step latent sampling.
3. Diffusion models (CSDI, Tashiro et al. 2021; PriSTI, Du et al. 2023) achieve state-of-the-art results on continuous time-series, providing sharp sample diversity and calibrated uncertainty quantification (CRPS).

### Decision
Adopt a conditional Denoising Diffusion Probabilistic Model (DDPM) operating on 24-hour multi-modal window slices $[B, 16, 24, 13]$.

### Alternatives Considered
Spatial-Temporal VAE, Conditional GAN, Deterministic Transformer (CTDI).

### Why Alternatives Were Rejected
Diffusion models inherently generate full posterior distributions rather than single point estimates, enabling critical prediction intervals for public health applications.

### Consequences
Inference requires multiple sampling steps (e.g., 50 diffusion steps), increasing test-time latency compared to single-pass deterministic models.

### Revisit Conditions
If fast-sampling diffusion techniques (e.g., DDIM or flow matching) can reduce sampling steps to $<10$.

---

## Decision A03: Decoupled Spatial Graph and Temporal Transformer Denoising Layers

- **Date**: 2026-09-13
- **Status**: **`ACCEPTED`**

### Context
Joint spatio-temporal attention across $S = 16$ stations, $K = 24$ hours, and $C = 13$ channels requires evaluating attention over $16 \times 24 = 384$ tokens, which can blur spatial vs. temporal inductive biases.

### Evidence
PriSTI (Du et al., KDD 2023) and CTDI (Yu et al., IEEE TBD 2025) demonstrate that decoupling spatial representation (via distance graph priors) from temporal representation (via self-attention) yields superior inductive bias and lower computational overhead.

### Decision
Structure each residual denoising block with:
1. Spatial Graph Convolution / Spatial Attention using the verified Haversine distance matrix.
2. Temporal Self-Attention over the 24-hour sequence.
3. Adaptive Layer Normalization (AdaLN) or Cross-Attention conditioned on SLM context $\mathbf{z}_C$.

### Alternatives Considered
Full 2D spatio-temporal flattened self-attention.

### Why Alternatives Were Rejected
Flattened attention destroys physical inductive biases and increases parameter count unnecessarily.

### Consequences
Clean, modular layer architecture in PyTorch.

### Revisit Conditions
None expected.
