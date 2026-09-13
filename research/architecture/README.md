# Model Architecture Specifications

This directory specifies the deep learning modules comprising the **SLM-Conditioned Diffusion** framework.

---

## Architectural Modules

1. **[System Architecture](system_architecture.md)**: End-to-end framework layout, data flow, and tensor transformations.
2. **[Context Encoder](context_encoder.md)**: Deterministic prompt construction and Small Language Model (SLM) text embedding generation ($\mathbf{z}_C$).
3. **[Diffusion Model](diffusion_model.md)**: Conditional Denoising Diffusion Probabilistic Model (DDPM) formulation and cosine noise schedule.
4. **[Temporal Model](temporal_model.md)**: 24-hour temporal self-attention and Transformer denoising blocks.
5. **[Spatial Model](spatial_model.md)**: Spatial graph convolutional networks (GCN) and geographic distance priors.
6. **[Conditioning Mechanism](conditioning_mechanism.md)**: Adaptive Layer Normalization (AdaLN) and cross-attention conditioning mechanics.
7. **[Loss Functions](loss_functions.md)**: Score-matching diffusion MSE loss, photochemical regularizers, and physical consistency constraints.
