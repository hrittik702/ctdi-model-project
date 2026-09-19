# Evaluation Metrics

## 1. Point Imputation Metrics (Matching CTDI Benchmark)

Computed on the median trajectory $\hat{\mathbf{x}}$ of $50$ posterior samples:

### 1.1 Mean Absolute Error (MAE)
$$\text{MAE} = \frac{\sum_{s,t,c} (1 - M_{s,t,c}) \cdot |\hat{X}_{s,t,c} - X_{s,t,c}|}{\sum_{s,t,c} (1 - M_{s,t,c})}$$

### 1.2 Root Mean Square Error (RMSE)
$$\text{RMSE} = \sqrt{\frac{\sum_{s,t,c} (1 - M_{s,t,c}) \cdot (\hat{X}_{s,t,c} - X_{s,t,c})^2}{\sum_{s,t,c} (1 - M_{s,t,c})}}$$

### 1.3 Mean Absolute Percentage Error (MAPE)
$$\text{MAPE} = \frac{100\%}{\sum (1 - M)} \sum_{s,t,c} (1 - M_{s,t,c}) \frac{|\hat{X}_{s,t,c} - X_{s,t,c}|}{X_{s,t,c} + \epsilon}$$

## 2. Probabilistic & Uncertainty Quantification Metrics

### 2.1 Continuous Ranked Probability Score (CRPS)
Measures distance between predicted cumulative distribution function $F$ and empirical ground truth $y$:
$$\text{CRPS}(F, y) = \int_{-\infty}^{\infty} (F(z) - \mathbf{1}_{\{z \ge y\}})^2 dz$$
Evaluated empirically across the 50 generated posterior trajectories.

### 2.2 Prediction Interval Coverage Probability (PICP)
Percentage of true unobserved values falling within the $95\%$ confidence bounds $[\hat{x}_{0.025}, \hat{x}_{0.975}]$:
$$\text{PICP}_{95} = \frac{1}{\sum (1 - M)} \sum_{s,t,c} (1 - M_{s,t,c}) \cdot \mathbf{1}_{\{ \hat{x}_{0.025} \le X_{s,t,c} \le \hat{x}_{0.975} \}}$$
Target: $\ge 95.0\%$.

### 2.3 Mean Prediction Interval Width (MPIW)
$$\text{MPIW}_{95} = \frac{1}{\sum (1 - M)} \sum_{s,t,c} (1 - M_{s,t,c}) \cdot (\hat{x}_{0.975} - \hat{x}_{0.025})$$
