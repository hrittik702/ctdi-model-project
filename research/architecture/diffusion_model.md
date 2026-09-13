# Conditional Diffusion Model Formulation

---

## 1. Denoising Diffusion Probabilistic Model (DDPM)

Following Tashiro et al. (CSDI 2021) and Ho et al. (DDPM 2020), the forward process adds Gaussian noise to the true ground-truth tensor $\mathbf{x}_0$ over $N = 50$ discrete diffusion steps:

$$q(\mathbf{x}_k \mid \mathbf{x}_0) = \mathcal{N}\left(\mathbf{x}_k; \sqrt{\bar{\alpha}_k} \mathbf{x}_0, (1 - \bar{\alpha}_k) \mathbf{I}\right)$$

where:
- $\beta_k \in [\beta_1, \beta_N]$ follows a smooth cosine variance schedule:
  $$\bar{\alpha}_k = \frac{f(k)}{f(0)}, \quad f(k) = \cos\left( \frac{k/N + s}{1 + s} \cdot \frac{\pi}{2} \right)^2$$
- $\alpha_k = 1 - \beta_k$ and $\bar{\alpha}_k = \prod_{s=1}^k \alpha_s$.

---

## 2. Reverse Denoising Sampling

The reverse transition $p_\theta(\mathbf{x}_{k-1} \mid \mathbf{x}_k, \mathbf{z}_C, \mathbf{x}_0 \odot \mathbf{M})$ is parameterized as:

$$\mathbf{x}_{k-1} = \frac{1}{\sqrt{\alpha_k}} \left( \mathbf{x}_k - \frac{\beta_k}{\sqrt{1 - \bar{\alpha}_k}} \boldsymbol{\epsilon}_\theta(\mathbf{x}_k, k, \mathbf{z}_C, \mathbf{x}_0 \odot \mathbf{M}) \right) + \sigma_k \mathbf{z}$$
where $\mathbf{z} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ for $k > 1$, and $\mathbf{z} = \mathbf{0}$ for $k = 1$.

### Imputation Reconstruction Condition
At each reverse step $k$, known observations are preserved by resetting:
$$\mathbf{x}_{k-1} \leftarrow \mathbf{M} \odot \mathbf{x}_{0, k-1} + (1 - \mathbf{M}) \odot \mathbf{x}_{k-1}$$
where $\mathbf{x}_{0, k-1} \sim q(\mathbf{x}_{k-1} \mid \mathbf{x}_0)$ is the forward noised ground truth. This guarantees exact preservation of true sensor readings.
