# Model Architecture Specifications

This directory specifies the deep learning modules comprising the **SLM-Conditioned Diffusion** framework.

---

## Architectural Modules

1. **[System Architecture](System%20Architecture.md)**: End-to-end framework layout, data flow, and tensor transformations.
2. **[Context Encoder](SLM%20Context%20Encoder.md)**: Deterministic prompt construction and Small Language Model (SLM) text embedding generation ($\mathbf{z}_C$).
3. **[Diffusion Model](Conditional%20Diffusion%20Model.md)**: Conditional Denoising Diffusion Probabilistic Model (DDPM) formulation and cosine noise schedule.
4. **[Temporal Model](Temporal%20Denoising%20Model.md)**: 24-hour temporal self-attention and Transformer denoising blocks.
5. **[Spatial Model](Spatial%20Model%20Prior.md)**: Spatial graph convolutional networks (GCN) and geographic distance priors.
6. **[Conditioning Mechanism](Conditioning%20Mechanism.md)**: Adaptive Layer Normalization (AdaLN) and cross-attention conditioning mechanics.
7. **[Loss Functions](Loss%20Functions%20&%20Objectives.md)**: Score-matching diffusion MSE loss, photochemical regularizers, and physical consistency constraints.
