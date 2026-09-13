# Dataset Documentation & Specifications

This directory contains the canonical specifications, source inventories, spatial topologies, and provenance records for the **Hong Kong Air Pollution Missing-Data Imputation Dataset**.

---

## Documents in This Section

1. **[Dataset Definition](dataset_definition.md)**: Target tensor mathematical formulation ($X \in \mathbb{R}^{16 \times 26,304 \times 13}$), coordinate system, and observation mask geometry.
2. **[Source Inventory](source_inventory.md)**: Rigorous audit of official data sources (HKEPD, HKO, HKTD), distinguishing `ACTUAL SOURCE`, `REFERENCE SOURCE`, `INFERRED SOURCE`, and `IMPLEMENTATION ASSUMPTION`.
3. **[Station Inventory](station_inventory.md)**: The 16 included continuous monitoring stations, sampling heights, district classifications, and empirical proof of why Southern (#84) and North (#85) were excluded.
4. **[Channel Definition](channel_definition.md)**: Exhaustive breakdown of the exact 13 channels (5 pollutants, 6 weather, 2 traffic) matching CTDI Table I.
5. **[Temporal Coverage](temporal_coverage.md)**: Detailed accounting of the 1,096-day study period (2019-01-01 to 2021-12-31, including 2020 leap year), totaling 26,304 continuous hours.
6. **[Spatial Alignment](spatial_alignment.md)**: Inverse Distance Weighting ($p=2$) mathematical formulation, road link centroids, AWS weather stations, and the 16×16 spatial distance matrix.
7. **[Missingness Analysis](missingness_analysis.md)**: Empirical audit of natural sensor missingness in EPD air quality (~2.5%) vs. benchmark simulated evaluation masks ($M_{\text{eval}}$ at 10%, 30%, 50%, 70%).
8. **[Provenance & Checksums](provenance.md)**: SHA-256 cryptographic hashes, exact file sizes, and raw data directory trees.
