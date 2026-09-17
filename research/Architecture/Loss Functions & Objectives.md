# Loss Functions & Optimization Objectives

---

## 1. Denoising Score-Matching Loss

Following standard DDPM formulations, the core objective trains the network to predict the injected Gaussian noise $\boldsymbol{\epsilon} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$.

Crucially, the loss is computed **strictly on simulated missing entries** ($\mathbf{M}_{\text{eval}} = 0$):

$$\mathcal{L}_{\text{diff}}(\theta) = \mathbb{E}_{k, \mathbf{x}_0, \boldsymbol{\epsilon}} \left[ \frac{1}{\sum (1 - M)} \left\| (\mathbf{1} - \mathbf{M}_{\text{eval}}) \odot \left( \boldsymbol{\epsilon} - \boldsymbol{\epsilon}_\theta(\mathbf{x}_k, k, \mathbf{z}_C, \mathbf{x}_0 \odot \mathbf{M}_{\text{eval}}) \right) \right\|_2^2 \right]$$

---

## 2. Physical & Chemical Regularization Loss

To prevent physically impossible generations, we introduce composite regularizers:

### 2.1 Non-Negativity Constraint
Air pollutant concentrations are strictly non-negative:
$$\mathcal{L}_{\text{nonneg}} = \frac{1}{S \cdot K \cdot C} \sum_{s,t,c} \text{ReLU}(-\hat{\mathbf{x}}_{0, s,t,c})^2$$

### 2.2 Photochemical Ozone Consistency
During daylight hours ($08:00\text{--}17:00$ HKT), photochemical reactions dictate a strong negative covariance between $\text{NO}_2$ and $\text{O}_3$ in the presence of sunlight:
$$\mathcal{L}_{\text{photo}} = \max\left( 0, \text{Corr}(\hat{\text{NO}}_2, \hat{\text{O}}_3) + 0.3 \right)$$
Penalizes positive daytime correlations between $\text{NO}_2$ and $\text{O}_3$.

---

## 3. Composite Training Objective

$$\mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{diff}}(\theta) + \lambda_1 \mathcal{L}_{\text{nonneg}} + \lambda_2 \mathcal{L}_{\text{photo}}$$
where $\lambda_1 = 0.1$ and $\lambda_2 = 0.05$.
