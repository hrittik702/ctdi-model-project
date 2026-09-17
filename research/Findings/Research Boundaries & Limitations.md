# Research Boundaries & Known Limitations

---

## 1. Source Fidelity vs. Exact Dataset Reproduction

- **Limitation**: While we have accurately reconstructed the source system schemas (607-link parent Speedmap, EPD criteria pollutants, IDW power $p=2$), reproducing the original authors' exact floating-point numbers byte-for-byte is impossible without access to their private local caches or raw code.
- **Scientific Impact**: Benchmarking will test the fidelity of our reconstructed dataset against their published performance metrics (MAE/RMSE), noting any residual variance as source-system variance.

---

## 2. Spatial Point Centroid Approximation

- **Limitation**: Road links are linear geometries with varying lengths ($100\text{m}$ to $3\text{km}$), but following CTDI Section III-A, they are approximated as dimensionless spatial points located at their geographic midpoints.
- **Scientific Impact**: High-curvature roads or extensive highway segments are collapsed to single coordinate pairs, which may introduce minor spatial smoothing in IDW calculations.

---

## 3. Hourly Temporal Aggregation of Categorical Congestion

- **Limitation**: Road saturation levels are reported at 5-minute intervals as discrete strings (`GOOD`, `AVERAGE`, `BAD`). Aggregating 12 snapshots into a single hourly float requires numerical averaging of categorical labels.
- **Scientific Impact**: Hourly averages (e.g., $0.35$) represent fractional congestion intensity rather than discrete traffic states.

---

## 4. Test-Time Sampling Latency of Diffusion Models

- **Limitation**: Generating 50 posterior trajectories across 50 reverse diffusion steps requires $50 \times 50 = 2,500$ forward evaluations of the denoising backbone per test sample.
- **Scientific Impact**: Point regression models (like CTDI or BRITS) produce imputations in a single feedforward pass ($<10\text{ms}$), whereas diffusion sampling requires $\approx 1\text{--}3\text{ seconds}$ per batch.
