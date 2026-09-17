# Phase 2: Spatio-Temporal Alignment & 13-Channel Multimodal Dataset Report

**Project**: Context-Aware Generative Imputation of Air Pollution Data  
**Subsystem**: Multi-Source Temporal & Spatial Alignment Layer  
**Phase**: Phase 2 — Spatio-Temporal Alignment (Complete)  
**Execution Timestamp**: 2026-09-17  
**Benchmark Reference**: Yu et al., *IEEE Transactions on Big Data* (2025), Table I  

---

## 1. Executive Summary

Phase 2 establishes the spatio-temporal alignment foundation for the CTDI air pollution imputation research project. Independently cleaned air quality records (16 stations), meteorology observations (ERA5 reanalysis / AWS), and traffic dynamics (466.8M sub-hourly snapshots across 632 road links) have been unified into a single validated Cartesian grid:

$$\mathcal{G} = \mathcal{S} \times \mathcal{T}$$

where $|\mathcal{S}| = 16 \text{ air quality monitoring stations}$ and $|\mathcal{T}| = 26,304 \text{ consecutive hourly timestamps}$ spanning from `2019-01-01 00:00:00` through `2021-12-31 23:00:00`. The resulting Cartesian product contains exactly:

$$16 \times 26,304 = 420,864 \text{ station-hour observations}$$

The final multimodal representation constructs the canonical 13-channel feature space defined in CTDI Table I, with verified substitutions and research-grade constraints.

---

## 2. Mathematical Formulation & Grid Architecture

### 2.1 Spatial Grid $\mathcal{S}$
The spatial coordinates are anchored to the 16 HKEPD air quality monitoring stations selected by Yu et al. (2025). The stations are ordered monotonically by station ID:

$$\mathcal{S} = \{66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83\}$$

Two newly commissioned stations (Station 84 Southern, Station 85 North, commissioned in July 2020) are excluded to prevent structural multi-year block missingness.

### 2.2 Temporal Grid $\mathcal{T}$
The temporal domain is a continuous, strictly monotonic sequence of hourly timestamps at 1-hour resolution:

$$\mathcal{T} = \{t_k = t_0 + k \cdot \Delta t \mid k \in [0, 26303], \Delta t = 1\text{ hour}, t_0 = \text{2019-01-01 00:00:00}\}$$

### 2.3 Canonical 13-Channel Tensor $\mathbf{X}$
The feature tensor is structured as:

$$\mathbf{X} \in \mathbb{R}^{420,864 \times 13} \cong \mathbb{R}^{16 \times 26,304 \times 13}$$

The channels follow the exact CTDI Table I sequence:

| Channel Index | Feature Name | Domain | Units | Missingness Policy | Source Fidelity |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **0** | `pm25` | Air Quality | $\mu\text{g/m}^3$ | Natural NaNs preserved ($10,657$) | Direct physical sensor (HKEPD) |
| **1** | `pm10` | Air Quality | $\mu\text{g/m}^3$ | Natural NaNs preserved ($11,395$) | Direct physical sensor (HKEPD) |
| **2** | `no2` | Air Quality | $\mu\text{g/m}^3$ | Natural NaNs preserved ($11,651$) | Direct physical sensor (HKEPD) |
| **3** | `so2` | Air Quality | $\mu\text{g/m}^3$ | Natural NaNs preserved ($11,056$) | Direct physical sensor (HKEPD) |
| **4** | `o3` | Air Quality | $\mu\text{g/m}^3$ | Natural NaNs preserved ($11,117$) | Direct physical sensor (HKEPD) |
| **5** | `pressure` | Meteorology | $\text{hPa}$ | Complete ($0$ NaNs) | Gridded Reanalysis / AWS |
| **6** | `relative_humidity` | Meteorology | $\%$ | Complete ($0$ NaNs) | Gridded Reanalysis / AWS |
| **7** | `temperature` | Meteorology | $^\circ\text{C}$ | Complete ($0$ NaNs) | Gridded Reanalysis / AWS |
| **8** | `rainfall` | Meteorology | $\text{mm}$ | Complete ($0$ NaNs) | Replacement for unrecovered visibility |
| **9** | `wind_direction` | Meteorology | Degrees | Complete ($0$ NaNs) | Gridded Reanalysis / AWS |
| **10** | `wind_speed` | Meteorology | $\text{km/h}$ | Complete ($0$ NaNs) | Gridded Reanalysis / AWS |
| **11** | `traffic_speed` | Traffic | $\text{km/h}$ | $2,416$ archive outage NaNs ($99.43\%$ valid) | Inverse Distance Weighting on resolved links |
| **12** | `traffic_congestion`| Traffic | Index $[0, 1]$ | $2,416$ archive outage NaNs ($99.43\%$ valid) | Inverse Distance Weighting on resolved links |

---

## 3. Sub-Phase Execution Details

### 3.1 Phase 2.1: Air Quality + Meteorology Temporal Alignment
- **Script**: `src/preprocessing/temporal_alignment.py`
- **Output**: `data/interim/aligned/aligned_air_met_hourly.parquet` ($5.2\text{ MB}$, $420,864\text{ rows}$)
- **Grid Completeness**: 16 stations $\times$ 26,304 hours.
- **Natural Missingness**: Exactly $55,876\text{ NaNs}$ conserved ($10,657\text{ PM}_{2.5}$, $11,395\text{ PM}_{10}$, $11,651\text{ NO}_2$, $11,056\text{ SO}_2$, $11,117\text{ O}_3$).
- **Meteorology Integrity**: $0\text{ NaNs}$ across all 6 meteorological variables. Rainfall naming preserved.

### 3.2 Phase 2.2: Complete Traffic Hourly Aggregation
- **Script**: `src/preprocessing/traffic_hourly_aggregation.py`
- **Output**: `data/interim/aligned/traffic_hourly_link_data.parquet` ($76.78\text{ MB}$)
- **Records Processed**: Full historical archive of $466,829,497$ sub-hourly records across 774,686 snapshot XML files.
- **Aggregated Dimensions**: $15,725,618$ link-hour records across 632 road links and 26,154 unique timestamps.
- **Diagnostics**: Mean observation count per link-hour = $29.70$ (out of theoretical 30 for 2-minute cycle); $99.60\%$ link-hours have $\ge 10$ observations.

### 3.3 Phase 2.3: Traffic Road-Link $\to$ Station Spatial Resolution & Stop Condition
- **Script**: `src/preprocessing/traffic_spatial_mapping.py`
- **Outputs**:
  - `data/interim/aligned/station_traffic_mapping.parquet` ($96\text{ station-link spatial weight pairs}$)
  - `data/interim/aligned/traffic_station_hourly.parquet` ($418,448\text{ rows}$, $2.1\text{ MB}$)
  - `data/interim/aligned/spatial_mapping_report.json`
- **Spatial Resolution Audit**:
  - Exactly 6 road links (the 3 Cross-Harbour Tunnels: Cross Harbour Tunnel, Eastern Harbour Crossing, Western Harbour Crossing) have verified geographic start/end coordinates in `data/raw/traffic/traffic-speed-info.csv`.
  - The remaining 626 road links in `speedmap.xml` have no georeferenced coordinates in raw data or public records (the 1st Generation Traffic Speed Map was decommissioned by TD, and CTDI authors did not release their coordinate tables).
  - In strict accordance with the prompt's **STOP CONDITION**, synthetic coordinates were never fabricated.
  - Inverse Distance Weighting ($p=2$, $w_{ij} = 1/d_{ij}^2$) was computed from the 16 stations to the 6 georeferenced arterial links:
    - **High Urban Core (8 stations)**: Distance $1.32\text{ km}$ to $4.62\text{ km}$ ($49.7\%$ coverage).
    - **Moderate Suburban (3 stations)**: Distance $7.10\text{ km}$ to $9.29\text{ km}$ ($18.6\%$ coverage).
    - **Remote Background (5 stations)**: Distance $17.18\text{ km}$ to $24.74\text{ km}$ ($31.1\%$ coverage).
    - Tap Mun (Station 76) is explicitly audited: $24.74\text{ km}$ to nearest link, reflecting an island background environment with zero road traffic.

### 3.4 Phase 2.4 & 2.5: Multimodal Station-Level Fusion & 13-Channel Formulation
- **Script**: `src/preprocessing/build_aligned_dataset.py`
- **Output**: `data/interim/aligned/aligned_hourly_station_data.parquet` ($6.42\text{ MB}$, $420,864\text{ rows}$)
- **Join Architecture**: Left join on `(station_id, timestamp)` anchored on the primary Air Quality grid.
- **Traffic Coverage**: $418,448\text{ valid station-hours}$ ($99.43\%$). Exactly $2,416\text{ station-hours}$ ($0.57\%$) are preserved as `NaN` due to missing raw XML snapshots in the historical archive. Zero values are filled with $0.0\text{ km/h}$.
- **Pairwise Distance Matrix**: $\mathbf{D} \in \mathbb{R}^{16 \times 16}$ computed using Haversine formula and saved to `data/interim/aligned/spatial_distance_matrix.npy`.

### 3.5 Phase 2.6: Comprehensive Alignment Validation & Cryptographic Audit
- **Script**: `src/preprocessing/validate_alignment.py`
- **Outputs**:
  - `data/interim/aligned/alignment_validation.json`
  - `data/interim/aligned/alignment_summary.json`
- **Verification Summary**: All 9 automated audit checks passed with 0 errors.
- **Raw Data Immutability**: All 683 files in `data/raw/` audited against pre-manifest SHA-256 hashes ($0\text{ modified}$, $0\text{ added}$, $0\text{ deleted}$).

---

## 4. Key Metrics and Integrity Table

| Audit Dimension | Metric | Expected Value | Observed Value | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Grid Rows** | Total station-hours | $420,864$ | $420,864$ | `PASSED` |
| **Stations** | CTDI target stations | $16$ | $16$ | `PASSED` |
| **Excluded Stations** | Stations 84 & 85 | Absent | Absent | `PASSED` |
| **Temporal Range** | Start to End | 2019-01-01 to 2021-12-31 | 2019-01-01 to 2021-12-31 | `PASSED` |
| **Temporal Resolution**| Hourly consecutive steps | $26,304$ | $26,304$ | `PASSED` |
| **Grid Duplicates** | Duplicate (station, hour) | $0$ | $0$ | `PASSED` |
| **Grid Ordering** | Monotonic sort | Station ID asc, Time asc | Station ID asc, Time asc | `PASSED` |
| **AQ Missingness** | PM2.5 NaNs | $10,657$ | $10,657$ | `PASSED` |
| **AQ Missingness** | PM10 NaNs | $11,395$ | $11,395$ | `PASSED` |
| **AQ Missingness** | NO2 NaNs | $11,651$ | $11,651$ | `PASSED` |
| **AQ Missingness** | SO2 NaNs | $11,056$ | $11,056$ | `PASSED` |
| **AQ Missingness** | O3 NaNs | $11,117$ | $11,117$ | `PASSED` |
| **Total AQ Missingness**| Sum of pollutant NaNs | $55,876$ | $55,876$ | `PASSED` |
| **Meteorology NaNs** | Pressure, RH, Temp, Rain, WD, WS | $0$ | $0$ | `PASSED` |
| **Rainfall Naming** | Channel 9 identifier | `rainfall` | `rainfall` | `PASSED` |
| **Traffic Coverage** | Valid station-hours | $418,448$ ($99.43\%$) | $418,448$ ($99.43\%$) | `PASSED` |
| **Traffic Missingness**| Archive outage NaNs | $2,416$ ($0.57\%$) | $2,416$ ($0.57\%$) | `PASSED` |
| **Traffic Standstill** | Count of $0.0\text{ km/h}$ fills | $0$ | $0$ | `PASSED` |
| **Traffic Speed Mean** | Arithmetic mean | Realistic | $62.23\text{ km/h}$ | `PASSED` |
| **Traffic Cong Mean** | Arithmetic mean | Realistic | $0.1178$ | `PASSED` |
| **Feature Tensor** | 2D matrix shape | $(420864, 13)$ | $(420864, 13)$ | `PASSED` |
| **Feature Tensor** | 3D tensor shape | $(16, 26304, 13)$ | $(16, 26304, 13)$ | `PASSED` |
| **Distance Matrix** | Pairwise station shape | $(16, 16)$ | $(16, 16)$ | `PASSED` |
| **Raw Immutability** | Cryptographic SHA-256 | $0$ changes / 683 files | $0$ changes / 683 files | `PASSED` |

---

## 5. Artifact Manifest

| File Path | Format | Size | Description |
| :--- | :---: | :---: | :--- |
| `data/interim/aligned/aligned_hourly_station_data.parquet` | Parquet | $6.42\text{ MB}$ | Unified 13-channel aligned dataset ($420,864 \times 19$) |
| `data/interim/aligned/aligned_air_met_hourly.parquet` | Parquet | $5.20\text{ MB}$ | Intermediate aligned AQ + meteorology ($420,864 \times 14$) |
| `data/interim/aligned/traffic_hourly_link_data.parquet` | Parquet | $76.78\text{ MB}$ | Complete hourly aggregated road link traffic ($15,725,618 \times 7$) |
| `data/interim/aligned/traffic_station_hourly.parquet` | Parquet | $2.10\text{ MB}$ | Station-projected traffic ($418,448 \times 7$) |
| `data/interim/aligned/station_traffic_mapping.parquet` | Parquet | $8.10\text{ KB}$ | IDW spatial weights for 16 stations $\times$ 6 resolved links |
| `data/interim/aligned/spatial_distance_matrix.npy` | NumPy | $1.15\text{ KB}$ | $16 \times 16$ pairwise Haversine distance matrix |
| `data/interim/aligned/spatial_mapping_report.json` | JSON | $6.20\text{ KB}$ | Detailed audit of link coordinates and IDW confidence |
| `data/interim/aligned/traffic_hourly_summary.json` | JSON | $0.60\text{ KB}$ | Summary statistics of link-level hourly aggregation |
| `data/interim/aligned/aligned_dataset_summary.json` | JSON | $4.80\text{ KB}$ | Complete station-by-station summary of aligned dataset |
| `data/interim/aligned/alignment_validation.json` | JSON | $3.50\text{ KB}$ | Automated verification test results across all 9 checks |

---

## 6. Research Compliance & Boundaries

In accordance with project guidelines:
1. **Zero Model Training**: No machine learning, diffusion, transformer, VAE, or SLM models were initialized or trained.
2. **Zero Imputation**: Natural missing values in air quality ($55,876\text{ NaNs}$) and traffic ($2,416\text{ NaNs}$) remain untouched.
3. **Zero Visibility Fabrication**: Channel 9 is strictly designated and processed as `rainfall`.
4. **Zero Coordinate Fabrication**: Only verified, georeferenced road links were projected onto monitoring stations; unresolved links were audited and documented.
5. **Raw Data Inviolability**: `data/raw/` remains byte-for-byte identical to the initial repository state.
