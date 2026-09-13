# Experimental Protocols & Benchmarking

This directory defines the experimental plans, benchmark baselines, missingness scenarios, and evaluation metrics for validating the **SLM-Conditioned Diffusion** framework.

---

## Experimental Documents

1. **[Experimental Protocol](experimental_protocol.md)**: Train/val/test splits, optimizer hyperparameters, random seeds, and training schedules.
2. **[Baselines](baselines.md)**: Mathematical heuristics, deterministic DL models (BRITS, CTDI), generative models (VAE, CSDI, PriSTI).
3. **[Missingness Scenarios](missingness_scenarios.md)**: MCAR, continuous temporal block missingness, and spatial station outages at 10%, 30%, 50%, 70%.
4. **[Evaluation Metrics](evaluation_metrics.md)**: Mathematical definitions of MAE, RMSE, MAPE, CRPS, and 95% Prediction Interval Coverage Probability (PICP).
5. **[Ablation Plan](ablation_plan.md)**: Systematic ablation matrix evaluating SLM conditioning, spatial graph priors, and physical loss regularizers.
6. **[Cross-Dataset Evaluation](cross_dataset_evaluation.md)**: Evaluation protocol for external benchmarks (e.g., Beijing multi-station air quality).
