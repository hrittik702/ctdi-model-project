# SLM-Conditioned Diffusion for Air Pollution Imputation

A context-aware generative framework for recovering missing air-pollution observations using a Small Language Model (SLM) and conditional diffusion.

The project extends spatial-temporal deep-learning approaches for air-pollution data imputation by introducing semantic environmental context into the generative process. Environmental conditions such as season, meteorology, traffic intensity, industrial influence, and station characteristics are converted into compact semantic representations using an SLM. These representations condition a diffusion model that learns to generate plausible missing pollution observations while preserving temporal and spatial relationships.

Unlike deterministic imputation methods that produce a single estimated value, the proposed framework can generate multiple conditional reconstructions, enabling uncertainty estimation through the resulting distribution of possible imputations.

## Core Components

- **Data Preprocessing:** Construction of structured temporal samples from air-pollution and environmental data.
- **Numerical Encoding:** Representation of observed pollution values and missingness masks.
- **SLM Context Encoder:** Converts structured environmental conditions into semantic embeddings.
- **Conditional Diffusion:** Generates missing pollution values through iterative denoising.
- **Spatio-Temporal Denoiser:** Captures temporal dependencies and spatial relationships between monitoring stations.
- **Context-Diffusion Alignment:** Injects semantic environmental context into the diffusion process.
- **Uncertainty Estimation:** Generates multiple reconstructions to estimate prediction uncertainty.
- **Consistency Constraints:** Evaluates temporal, spatial, and contextual consistency of generated values.

## Research Objective

The primary objective is to investigate whether semantic environmental context can improve the reconstruction of missing air-pollution observations, particularly under high missingness and long missing blocks.

The framework will be evaluated against classical statistical methods, machine-learning approaches, deep-learning imputers, and the existing VAE-based generative approach.

> **Note:** Experimental results will be added only after the proposed experiments are actually conducted.
