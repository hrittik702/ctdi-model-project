# Experimental Protocols & Benchmarking

This directory defines the experimental plans, benchmark baselines, missingness scenarios, and evaluation metrics for validating the **SLM-Conditioned Diffusion** framework.

---

## Experimental Documents

1. **[Experimental Protocol](Experimental%20Training%20Protocol.md)**: Train/val/test splits, optimizer hyperparameters, random seeds, and training schedules.
2. **[Baselines](Baseline%20Imputation%20Models.md)**: Mathematical heuristics, deterministic DL models (BRITS, CTDI), generative models (VAE, CSDI, PriSTI).
3. **[Missingness Scenarios](Missingness%20Scenarios%20&%20Benchmark%20Masks.md)**: MCAR, continuous temporal block missingness, and spatial station outages at 10%, 30%, 50%, 70%.
4. **[Evaluation Metrics](Evaluation%20Metrics.md)**: Mathematical definitions of MAE, RMSE, MAPE, CRPS, and 95% Prediction Interval Coverage Probability (PICP).
5. **[Ablation Plan](Ablation%20Study%20Plan.md)**: Systematic ablation matrix evaluating SLM conditioning, spatial graph priors, and physical loss regularizers.
6. **[Cross-Dataset Evaluation](Cross-Dataset%20Evaluation.md)**: Evaluation protocol for external benchmarks (e.g., Beijing multi-station air quality).
