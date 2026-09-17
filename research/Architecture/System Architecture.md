# End-to-End System Architecture

---

## 1. System Pipeline Overview

```
                         24-Hour Input Tensor
                    X_0 ∈ R^(16 stations × 24 hrs × 13 ch)
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
         ▼                                                 ▼
[Observed & Masked Tensors]                    [Environmental Context Builder]
x_0 = X_0 ⊙ M_eval                             Synthesizes English atmospheric prompt
         │                                                 │
         ▼                                                 ▼
[Diffusion Forward Process]                    [Small Language Model (SLM)]
Injects noise: x_k ~ q(x_k | x_0)              Produces context vector z_C ∈ R^d
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  Conditional Denoiser     │
                    │      ε_θ(x_k, k, z_C)     │
                    │  • Spatial Graph Prior    │
                    │  • Temporal Transformer   │
                    │  • AdaLN Conditioning     │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  Reverse Diffusion Loop   │
                    │  x_(k-1) ~ p_θ(x_(k-1)|x_k)│
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  Probabilistic Ensemble   │
                    │  • Imputed missing values │
                    │  • Preserved observations │
                    │  • Mean, Median, 95% CI   │
                    └───────────────────────────┘
```

---

## 2. Dimensional Flow
- Input Window: $[B, 16, 24, 13]$
- Mask: $[B, 16, 24, 13]$
- Context Prompt: $B$ text strings
- SLM Embedding: $\mathbf{z}_C \in [B, d_{\text{context}}]$ (e.g., $d = 512$)
- Denoising Hidden Dimension: $d_{\text{model}} = 128$
- Output Imputation: $[B, 16, 24, 13]$
