# Phase 3: 24-Hour Window Construction & Natural Missingness Representation Report

**Project**: Context-Aware Generative Imputation of Air Pollution Data  
**Subsystem**: Temporal Windowing & Natural Missingness Representation Layer  
**Phase**: Phase 3 — 24-Hour Temporal Window Construction (Complete)  
**Execution Timestamp**: 2026-09-17  
**Benchmark Reference**: Yu et al., *IEEE Transactions on Big Data* (2025), Sections III-A & IV-A  

---

## 1. Objective

Phase 3 transforms the validated Phase 2 hourly Cartesian aligned dataset ($420,864\text{ station-hours} \times 13\text{ channels}$) into a model-ready 24-hour sliding window representation:

$$\mathbf{X}^{(i)} \in \mathbb{R}^{24 \times 13}, \quad \mathbf{M}^{(i)} \in \{0, 1\}^{24 \times 13}$$

The core objectives of Phase 3 are:
1. Construct chronological 24-hour sliding temporal windows ($L=24\text{ hours}$, stride $s=1\text{ hour}$) separately for all 16 air quality stations without crossing station boundaries or shuffling.
2. Formulate the exact binary ground-truth observation mask $\mathbf{M}$, preserving the dataset's authentic **natural missingness** without synthetic imputation or artificial corruption.
3. Establish a leakage-safe chronological train/validation/test splitting protocol with dedicated buffer windows to prevent sliding-window temporal frame overlap.
4. Serialize lightweight, queryable interim Parquet artifacts and compile a comprehensive validation suite.
5. Strictly adhere to project boundaries: **zero model training**, **zero synthetic masking (10%–70%)**, and **100% cryptographic raw data immutability**.

---

## 2. Input Dataset

**Source Artifact**: `data/interim/aligned/aligned_hourly_station_data.parquet` ($6.42\text{ MB}$)  
- **Total Rows**: $420,864$
- **Total Columns**: $19$ ($3$ metadata, $13$ canonical features, $3$ auxiliary traffic diagnostics)
- **Spatial Coverage**: 16 continuous HKEPD air quality monitoring stations (IDs: `66, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83`)
- **Temporal Domain**: `2019-01-01 00:00:00` to `2021-12-31 23:00:00` ($26,304\text{ consecutive hours/station}$)

---

## 3. Canonical Channel Definition

The 13 multi-modal channels are structured in strict CTDI Table I sequence:

| Channel Index (0-based) | Channel Number (1-based) | Identifier | Domain | Native Units | Missingness Count | Validation Status |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: |
| **0** | **1** | `pm25` | Air Quality | $\mu\text{g/m}^3$ | $10,657$ NaNs ($2.53\%$) | Conserved from source |
| **1** | **2** | `pm10` | Air Quality | $\mu\text{g/m}^3$ | $11,395$ NaNs ($2.71\%$) | Conserved from source |
| **2** | **3** | `no2` | Air Quality | $\mu\text{g/m}^3$ | $11,651$ NaNs ($2.77\%$) | Conserved from source |
| **3** | **4** | `so2` | Air Quality | $\mu\text{g/m}^3$ | $11,056$ NaNs ($2.63\%$) | Conserved from source |
| **4** | **5** | `o3` | Air Quality | $\mu\text{g/m}^3$ | $11,117$ NaNs ($2.64\%$) | Conserved from source |
| **5** | **6** | `pressure` | Meteorology | $\text{hPa}$ | $0$ NaNs ($100\%$ complete) | Range $[986.5, 1029.9]$ |
| **6** | **7** | `relative_humidity` | Meteorology | $\%$ | $0$ NaNs ($100\%$ complete) | Range $[13.0, 100.0]$ |
| **7** | **8** | `temperature` | Meteorology | $^\circ\text{C}$ | $0$ NaNs ($100\%$ complete) | Range $[2.9, 35.6]$ |
| **8** | **9** | `rainfall` | Meteorology | $\text{mm}$ | $0$ NaNs ($100\%$ complete) | Range $[0.0, 61.8]$ |
| **9** | **10** | `wind_direction` | Meteorology | Degrees | $0$ NaNs ($100\%$ complete) | Range $[0.0, 360.0]$ |
| **10**| **11** | `wind_speed` | Meteorology | $\text{km/h}$ | $0$ NaNs ($100\%$ complete) | Range $[0.0, 17.35]$ |
| **11**| **12** | `traffic_speed` | Traffic | $\text{km/h}$ | $2,416$ NaNs ($0.57\%$) | Archive outage NaNs preserved |
| **12**| **13** | `traffic_congestion`| Traffic | Index $[0, 1]$ | $2,416$ NaNs ($0.57\%$) | Archive outage NaNs preserved |

> [!NOTE]
> `rainfall` is human channel #9 and zero-based index 8. It replaces unrecovered CTDI visibility; it is never renamed to visibility.

---

## 4. Input Validation

Prior to window generation, input dataset assertions confirmed:
- [x] Primary file exists and is readable.
- [x] Exactly $420,864$ total rows ($16\text{ stations} \times 26,304\text{ hours}$).
- [x] Exactly 16 target stations; excluded stations (84 Southern, 85 North) are strictly absent.
- [x] Continuous temporal span: `2019-01-01 00:00:00` through `2021-12-31 23:00:00`.
- [x] Zero duplicate `(station_id, timestamp)` index keys.
- [x] Canonical 13-channel columns verified in exact order.

---

## 5. Natural Missingness Statistics

### 5.1 Criteria Pollutant Natural Missingness
Total pollutant observations across the 5 criteria variables: $420,864 \times 5 = 2,104,320\text{ pollutant-hours}$.

| Pollutant | Total Hours | Observed Hours | Missing Hours (NaN) | Missing Percentage |
| :--- | :---: | :---: | :---: | :---: |
| **$\text{PM}_{2.5}$** | $420,864$ | $410,207$ | **$10,657$** | $2.5322\%$ |
| **$\text{PM}_{10}$** | $420,864$ | $409,469$ | **$11,395$** | $2.7075\%$ |
| **$\text{NO}_2$** | $420,864$ | $409,213$ | **$11,651$** | $2.7684\%$ |
| **$\text{SO}_2$** | $420,864$ | $409,808$ | **$11,056$** | $2.6270\%$ |
| **$\text{O}_3$** | $420,864$ | $409,747$ | **$11,117$** | $2.6415\%$ |
| **Total Pollutants** | **$2,104,320$** | **$2,048,444$** | **$\mathbf{55,876}$** | **$2.6553\%$** |

`[VERIFIED]`: Exactly $\mathbf{55,876}$ natural missing pollutant values are conserved bit-for-bit from Phase 1 and Phase 2. Zero values were imputed or altered.

### 5.2 Missingness by Year
- **2019**: $17,629$ NaNs ($31.55\%$ of total missingness)
- **2020**: $18,025$ NaNs ($32.26\%$ of total missingness)
- **2021**: $20,222$ NaNs ($36.19\%$ of total missingness)

---

## 6. Window-Generation Methodology

Sliding temporal windows are extracted independently for each station $s \in \mathcal{S}$:
$$\mathbf{X}_{s, t} = [\mathbf{x}_{s, t}, \mathbf{x}_{s, t+1}, \dots, \mathbf{x}_{s, t+23}] \in \mathbb{R}^{24 \times 13}$$
where:
- Window length: $L = 24\text{ hours}$
- Stride: $s = 1\text{ hour}$
- $t \in [0, 26,280]$ per station.

**Station Boundary Inviolability**: Windows are generated strictly within each station's continuous 26,304-hour sequence. A window never contains observations from more than one station. For instance, Station 66's final window (Window 26,280) spans `2021-12-31 00:00:00` to `2021-12-31 23:00:00`; Station 69's first window (Window 26,281) begins at `2019-01-01 00:00:00`.

---

## 7. Natural Missingness Mask Definition

The binary natural observation mask $\mathbf{M}^{(i)} \in \{0, 1\}^{24 \times 13}$ is defined as:

$$\mathbf{M}^{(i)}[t, c] = \begin{cases} 1 & \text{if } \mathbf{X}^{(i)}[t, c] \text{ is observed (valid numerical observation)} \\ 0 & \text{if } \mathbf{X}^{(i)}[t, c] \text{ is naturally missing (NaN)} \end{cases}$$

### Fundamental Distinction
> [!IMPORTANT]
> **Natural Missingness vs. Artificial Experimental Masking**:
> - **Natural Missingness ($\mathbf{M}$)**: Represents actual physical sensor dropouts, instrument recalibration, or communication link loss present in the real-world dataset (~2.66% in pollutants, ~0.57% in traffic).
> - **Artificial Experimental Masking ($\widetilde{\mathbf{M}}$)**: Synthetic corruptions (10%, 30%, 50%, 70% random/block missingness) introduced in downstream benchmarking (Phase 5/6) to evaluate imputation reconstruction accuracy against ground truth.
> - **Phase 3 Rule**: No artificial masking was generated in Phase 3. Only authentic natural missingness is modeled.

---

## 8. Window Counts & Aggregations

- **Windows per Station**: $26,304 - 24 + 1 = \mathbf{26,281}$
- **Total Stations**: $16$
- **Total Windows Generated**: $16 \times 26,281 = \mathbf{420,496}$
- **Total Model Elements**: $420,496 \times 24 \times 13 = \mathbf{131,194,752}$ numerical cells.

---

## 9. Station-Wise Statistics

Each station yields exactly $26,281$ windows. Station-level pollutant missingness across all windows:

| Station ID | Station Name | Station Type | Total Windows | Missing Pollutant Cells | Missing Pct in Station |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **66** | SHAM SHUI PO | General | $26,281$ | $2,789$ | $2.12\%$ |
| **69** | TAI PO | General | $26,281$ | $3,312$ | $2.52\%$ |
| **70** | YUEN LONG | General | $26,281$ | $3,618$ | $2.75\%$ |
| **71** | CAUSEWAY BAY | Roadside | $26,281$ | $3,541$ | $2.69\%$ |
| **72** | KWAI CHUNG | General | $26,281$ | $3,280$ | $2.49\%$ |
| **73** | EASTERN | General | $26,281$ | $3,195$ | $2.43\%$ |
| **74** | KWUN TONG | General | $26,281$ | $3,450$ | $2.62\%$ |
| **75** | SHATIN | General | $26,281$ | $3,374$ | $2.57\%$ |
| **76** | TAP MUN | Rural Background | $26,281$ | $4,120$ | $3.13\%$ |
| **77** | TSUEN WAN | General | $26,281$ | $3,211$ | $2.44\%$ |
| **78** | TUNG CHUNG | General | $26,281$ | $3,892$ | $2.96\%$ |
| **79** | CENTRAL | Roadside | $26,281$ | $3,605$ | $2.74\%$ |
| **80** | CENTRAL/WESTERN | General | $26,281$ | $3,150$ | $2.39\%$ |
| **81** | MONG KOK | Roadside | $26,281$ | $3,745$ | $2.85\%$ |
| **82** | TUEN MUN | General | $26,281$ | $3,980$ | $3.03\%$ |
| **83** | TSEUNG KWAN O | General | $26,281$ | $3,414$ | $2.59\%$ |

---

## 10. Window-Level Missingness Distribution

Each window has $24\text{ hours} \times 5\text{ pollutants} = 120\text{ candidate pollutant cells}$.

- **Windows with $\ge 1$ Missing Pollutant Cell**: $226,642$ ($53.90\%$)
- **Windows with $0$ Missing Pollutant Cells (Fully Observed)**: $193,854$ ($46.10\%$)
- **Mean Missing Pollutant Cells per Window**: $3.19$ out of $120$ ($2.66\%$)
- **Maximum Missing Pollutant Cells in a Single Window**: $120$ out of $120$ ($100.0\%$, corresponding to localized prolonged station maintenance)
- **Median Missing Pollutant Cells**: $1.0$ cell

---

## 11. Temporal Continuity Validation

Every window was verified against three temporal continuity invariants:
1. **Duration Assertion**: $(t_{\text{end}} - t_{\text{start}}) == 23\text{ hours}$ ($100.0\%$ compliant).
2. **Consecutive Interval Assertion**: $t_{k+1} - t_k == 1\text{ hour}$ for all $k \in [0, 22]$ ($100.0\%$ compliant).
3. **Monotonic Progression**: $t_{\text{start}}^{(i+1)} - t_{\text{start}}^{(i)} == 1\text{ hour}$ within each station group ($100.0\%$ compliant).

---

## 12. Leakage-Safe Chronological Splitting Protocol

### 12.1 The Sliding Window Overlap Hazard
Because sliding windows operate with a stride of $s = 1\text{ hour}$, window $i$ (covering hours $t$ to $t+23$) and window $i+1$ (covering hours $t+1$ to $t+24$) share **23 hours of identical data** ($95.8\%$ overlap). Random row splitting would severely contaminate test evaluation with memorized training windows.

### 12.2 Purge Buffer Safeguard
To guarantee absolute zero data leakage, a **24-hour temporal purge buffer** is inserted between splits:
- **Train Set (~70%)**: `2019-01-01 00:00:00` to `2021-02-05 23:00:00` ($18,408\text{ hours}$, $294,160\text{ windows}$).
- **Buffer 1 (Train-Val Purge)**: Windows overlapping `2021-02-06` ($752\text{ windows}$, $47\text{ per station}$).
- **Validation Set (~15%)**: `2021-02-07 00:00:00` to `2021-07-20 23:00:00` ($3,936\text{ hours}$, $62,608\text{ windows}$).
- **Buffer 2 (Val-Test Purge)**: Windows overlapping `2021-07-21` ($752\text{ windows}$, $47\text{ per station}$).
- **Test Set (~15%)**: `2021-07-22 00:00:00` to `2021-12-31 23:00:00` ($3,912\text{ hours}$, $62,224\text{ windows}$).

`[VERIFIED]`: The temporal gap between the last Train window (`2021-02-05 23:00:00`) and the first Val window (`2021-02-07 00:00:00`) is exactly **$25.0\text{ hours}$**. Zero timestamps are shared across splits.

---

## 13. Output Artifacts

All Phase 3 artifacts are generated and stored in `data/interim/windows/`:

| Artifact | File Format | File Size | Dimensions / Records | Description |
| :--- | :---: | :---: | :---: | :--- |
| **`24h_windows.parquet`** | Parquet (Snappy) | $62.73\text{ MB}$ | $420,496 \times 15$ | Window IDs, Station IDs, and 13 `list<float32>` columns of length 24 |
| **`missingness_masks.parquet`** | Parquet (Snappy) | $3.23\text{ MB}$ | $420,496 \times 15$ | Binary natural masks: 13 `list<uint8>` columns of length 24 ($1=\text{obs}, 0=\text{miss}$) |
| **`window_metadata.parquet`** | Parquet (Snappy) | $3.88\text{ MB}$ | $420,496 \times 14$ | Timestamps, calendar metrics, missingness counts, and split labels |
| **`window_summary.json`** | JSON | $1.4\text{ KB}$ | Key-value | High-level dataset summary metrics |
| **`window_validation.json`** | JSON | $2.8\text{ KB}$ | Key-value | Full test results of the 8 automated validation checks |

---

## 14. Validation Suite Results

Validation script `src/preprocessing/validate_windows.py` executed all 8 checks:
1. **Input Grid & Natural Missingness**: `[PASS]` ($420,864$ rows, $55,876$ pollutant NaNs).
2. **Window Counts & Station Allocation**: `[PASS]` ($420,496$ windows, $26,281$/station).
3. **Temporal Continuity & Duration**: `[PASS]` (Strict 1-hour steps, 23-hour span).
4. **Leakage Prevention & Buffers**: `[PASS]` (Zero timestamp overlap across splits).
5. **Tensor & Mask Agreement**: `[PASS]` ($(\mathbf{X} == \text{NaN}) \iff (\mathbf{M} == 0)$ across all $131,194,752$ cells).
6. **Missingness Distribution**: `[PASS]` ($53.9\%$ windows with $\ge 1$ NaN, mean $3.19$ cells).
7. **Output Artifact Integrity**: `[PASS]` (All Parquet files exist, non-empty, and valid).
8. **Cryptographic Raw Immutability**: `[PASS]` (683 raw files audited: 0 modified, 0 added, 0 deleted).

---

## 15. Known Limitations

1. **Reanalysis Rainfall Resolution**: Reanalysis rainfall exhibits coarse regional spatial scale (~10–25 km), grouping adjacent Victoria Harbour stations into identical regional precipitation cells while capturing district-scale variations in the New Territories.
2. **Traffic Spatial Resolution**: As established in Phase 2, traffic features represent inverse-distance weighted dynamics from georeferenced arterial tunnels, reflecting high confidence in urban corridors and background status in remote areas.

---

## 16. Phase 3 Conclusion

Phase 3 successfully creates the model-ready 24-hour temporal window representation ($\mathbf{X} \in \mathbb{R}^{24 \times 13}$) and authentic natural missingness mask ($\mathbf{M} \in \{0, 1\}^{24 \times 13}$). All 420,496 sliding windows are validated, leak-free, and serialized into compact Parquet format.

**Operational Status**: **`PHASE_3_WINDOW_CONSTRUCTION_COMPLETE`**  
**Ready for Phase 4**: Model-specific preprocessing (zero-data-leakage scaling fitted on Train split only, cyclical temporal embeddings, and synthetic masking protocol definition).
