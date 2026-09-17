# Baseline Imputation Models

To ensure rigorous benchmarking, the proposed model will be evaluated against 7 baseline models:

---

## 1. Classical Heuristics & Statistical Models
1. **Historical Mean / Median**: Computes the channel-wise median observed in the training split for each station.
2. **Linear / Cubic Spline Interpolation**: Piecewise 1D interpolation along the temporal dimension for each channel independently.
3. **K-Nearest Neighbors (KNN)**: Spatial KNN ($K = 3$) based on pairwise geographic distance.

---

## 2. Deterministic Deep Learning Baselines
4. **BRITS (Cao et al., NeurIPS 2018)**: Bidirectional Recurrent Imputation for Time Series.
5. **CTDI (Yu et al., IEEE TBD 2025)**: **Primary published state-of-the-art**. CNN spatial extractor + Transformer temporal encoder trained on Dataset AU (13 channels) and Dataset A (5 channels).

---

## 3. Generative Baselines
6. **Spatial-Temporal VAE**: Standard conditional variational autoencoder mapping windows into a Gaussian latent bottleneck.
7. **CSDI (Tashiro et al., NeurIPS 2021)**: Score-based conditional diffusion model operating on flattened time-series without spatial graph priors or SLM context.
