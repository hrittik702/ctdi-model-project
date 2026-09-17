# Experimental Training & Evaluation Protocol

---

## 1. Dataset Partitioning

- **Study Period**: `2019-01-01 00:00` to `2021-12-31 23:00` ($26,304$ hours across 16 stations).
- **Training Set (70%)**: $18,412$ hours (`2019-01-01 00:00` to `2021-02-05 03:00`).
- **Validation Set (15%)**: $3,946$ hours (`2021-02-05 04:00` to `2021-07-18 13:00`).
- **Test Set (15%)**: $3,946$ hours (`2021-07-18 14:00` to `2021-12-31 23:00`).

---

## 2. Training Hyperparameters

| Hyperparameter | Value | Description |
| :--- | :---: | :--- |
| **Batch Size** ($B$) | $32$ | 24-hour multi-modal windows $[32, 16, 24, 13]$ |
| **Diffusion Steps** ($N$) | $50$ | Forward noise injection steps (cosine schedule) |
| **Optimizer** | AdamW | Weight decay: $10^{-4}$ |
| **Learning Rate** | $1 \times 10^{-4}$ | Cosine annealing with 5-epoch warmup |
| **Max Epochs** | $100$ | Early stopping on validation loss (patience: 15 epochs) |
| **Random Seeds** | `[42, 123, 999]` | All experiments repeated across 3 seeds |
| **Sampling Count** | $50$ | Number of reverse diffusion trajectories per test sample |
