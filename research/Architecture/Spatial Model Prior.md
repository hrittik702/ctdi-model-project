# Spatial Model: Geographic Distance Graph Prior

---

## 1. Spatial Adjacency Matrix Formulation

Spatial dependency across the $S = 16$ monitoring stations is parameterized using the verified Haversine distance matrix $\mathbf{D} \in \mathbb{R}^{16 \times 16}$ (`data/interim/spatial_distance_matrix.npy`).

We construct a normalized Gaussian kernel adjacency matrix $\mathbf{A} \in \mathbb{R}^{16 \times 16}$:
$$A_{ij} = \exp\left( -\frac{D_{ij}^2}{\sigma_d^2} \right) \quad \text{for } D_{ij} \le \kappa, \quad \text{else } 0$$
where:
- $\sigma_d$ is the standard deviation of geographic distances ($\approx 12.5\text{ km}$).
- $\kappa$ is a sparsity cutoff threshold (e.g., $25\text{ km}$).
- Normalized with symmetric degree scaling: $\tilde{\mathbf{A}} = \mathbf{D}_{\text{deg}}^{-1/2} \mathbf{A} \mathbf{D}_{\text{deg}}^{-1/2}$.

---

## 2. Spatial Graph Convolution Layer

In each denoising layer, spatial message passing updates station hidden features:
$$\mathbf{H}_{\text{spatial}} = \tilde{\mathbf{A}} \mathbf{H} \mathbf{W}_S + \mathbf{b}_S$$

This ensures that stations in close proximity (e.g., Causeway Bay, Central, Mong Kok) share strong diffusion priors, while isolated rural stations (e.g., Tap Mun) are regularized by regional background dynamics.
