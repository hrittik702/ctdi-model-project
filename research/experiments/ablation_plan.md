# Systematic Ablation Study Plan

To isolate the specific scientific contributions of each module, the following 7-part ablation matrix will be executed:

---

## 1. Ablation Configurations Matrix

| ID | Architecture Variant | Components Active | Primary Hypothesis Tested |
| :---: | :--- | :--- | :--- |
| **A0** | Standard Tabular CSDI | Diffusion + Flattened Attention | Unconditioned tabular diffusion baseline. |
| **A1** | Spatial Diffusion | Diffusion + Spatial Graph GCN + Temporal Transformer | Gain from geographic distance prior $\mathbf{A}$. |
| **A2** | Multi-Modal Tabular | Diffusion + Spatial Graph + Raw Tabular Met & Traffic | Gain from raw float numerical concatenation. |
| **A3** | **Full SLM-Diffusion** | Diffusion + Spatial Graph + SLM Context $\mathbf{z}_C$ + Physical Loss | Proposed complete framework. |
| **A4** | Frozen vs Tuned SLM | SLM-Diffusion with Frozen SLM vs LoRA Fine-Tuned SLM | Does domain-specific atmospheric text tuning improve conditioning? |
| **A5** | No Physical Loss | Full Architecture with $\lambda_1 = 0, \lambda_2 = 0$ | Evaluates impact of photochemical & non-negative loss on plausibility. |
| **A6** | Generative VAE Baseline | Spatial Graph + SLM Context + 1-Step VAE Latent | Tests whether iterative diffusion beats single-step VAEs. |
