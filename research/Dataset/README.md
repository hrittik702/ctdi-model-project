# Dataset Documentation & Specifications

This directory contains the canonical specifications, source inventories, spatial topologies, and provenance records for the **Hong Kong Air Pollution Missing-Data Imputation Dataset**.

---

## 1. Primary Knowledge Documents

Open these documents first for complete, self-contained understanding of the dataset domains:

1. **[CTDIDataset Specifications](CTDIDataset%20Specifications.md)**: **Primary Benchmark Document**. Comprehensive reference for the published CTDI paper (Yu et al. 2025): verbatim Table I reproduction, 13-channel definitions, 47 AWS stations, 607 road links, IDW ($p=2$) mapping, side-by-side visual comparisons (Figures 6–9), and an explicit comparative divergence table against our dataset.
2. **[Dataset Provenance & Specifications](Dataset%20Provenance%20&%20Specifications.md)**: **Primary Reconstruction Document**. Complete unbroken chain of custody across all 4 components (Air Quality, Meteorology, Traffic, Distance Matrix), ERA5 rainfall substitution rationale, the complete 3-year historical traffic archive extraction (774,686 snapshots, 466M records), and cryptographic SHA-256 hashes.
3. **[Missingness Architecture & Empirical Distribution](Missingness%20Architecture%20&%20Empirical%20Distribution.md)**: **Primary Missingness Document**. Unifies the theoretical missingness architecture (natural $M_{\text{obs}}$ vs. simulated $M_{\text{eval}}$ masks) with empirical findings across diurnal dynamics (Hour 1 & 4 calibration peaks), 20% criteria pollutant parity, and spatial station reliability.

---

## 2. Domain Specifications & Structural Audits

Detailed reference notes for specific spatial, temporal, and variable dimensions:

4. **[Canonical Dataset Definition](Canonical%20Dataset%20Definition.md)**: Target tensor mathematical formulation ($\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$), coordinate system, and observation mask geometry.
5. **[CTDI 13-Channel Specification](CTDI%2013-Channel%20Specification.md)**: Exhaustive breakdown of the exact 13 channels (5 air pollutants, 6 meteorological variables, 2 traffic variables) matching CTDI Table I.
6. **[Station Inventory & Spatial Network](Station%20Inventory%20&%20Spatial%20Network.md)**: The 16 included continuous monitoring stations, sampling heights, district classifications, and empirical proof of why Southern (#84) and North (#85) were excluded.
7. **[Temporal Coverage & Calendar Accounting](Temporal%20Coverage%20&%20Calendar%20Accounting.md)**: Detailed accounting of the 1,096-day study period (2019-01-01 to 2021-12-31, including 2020 leap year), totaling 26,304 continuous hours.
8. **[Spatial Alignment & Network Geometry](Spatial%20Alignment%20&%20Network%20Geometry.md)**: Inverse Distance Weighting ($p=2$) mathematical formulation, road link centroids, AWS weather stations, and the $16 \times 16$ spatial distance matrix.
9. **[Data Source Inventory & Fidelity Audit](Data%20Source%20Inventory%20&%20Fidelity%20Audit.md)**: Rigorous audit of official data sources (HKEPD, HKO, HKTD), distinguishing `ACTUAL SOURCE`, `REFERENCE SOURCE`, `INFERRED SOURCE`, and `IMPLEMENTATION ASSUMPTION`.
10. **[CTDI Dataset Consistency Matrix](CTDI%20Dataset%20Consistency%20Matrix.md)**: 100-check audit matrix comparing our reconstructed data against published figures and tables in Yu et al. (2025).
11. **[Raw Data Integrity Manifest](Raw%20Data%20Integrity%20Manifest.md)**: Cryptographic SHA-256 baseline and post-investigation manifest guaranteeing 100% bit-for-bit raw data immutability.

---

## 3. Paper Reference Figures

Curated visual evidence from the published CTDI benchmark paper:
- **`air - missing by hour year.png`**: Published Figure 6 (Diurnal missingness curves by year).
- **`air - pollution hour vs missing.png`**: Published Figure 7 (Hourly missing data proportions).
- **`air - pollutant by missing.png`**: Published Figure 8 (Proportion of different pollutants in missing data).
- **`air - station vs missing.png`**: Published Figure 9 (Proportion of missing data across stations).
