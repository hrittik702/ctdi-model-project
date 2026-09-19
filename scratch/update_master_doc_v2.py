with open("research/MASTER_RESEARCH_DOCUMENT.md") as f:
    text = f.read()

# 1. Header updates
text = text.replace(
    "**Current Date**: 13 September 2026",
    "**Current Date**: 2026-09-17"
)

text = text.replace(
    "**Operational Status**: **`CTDI_ALIGNED_RECONSTRUCTION_WITH_DOCUMENTED_DIFFERENCES`**",
    "**Operational Status**: **`PHASE_2_ALIGNED_DATASET_READY`**"
)

# 2. Section 1 Status
old_s1 = """- **Current Development Status**: **`CTDI_ALIGNED_RECONSTRUCTION_WITH_DOCUMENTED_DIFFERENCES`**. Comprehensive consistency resolution and visibility recovery audit completed. Air quality is verified as an `EXACT SOURCE MATCH` ($420,864$ rows, $55,876$ missing items matching paper's $55,875$ with $99.99995\%$ fidelity). Traffic is verified as a `SOURCE-SYSTEM MATCH` (parent 1st Gen Speedmap, 607 baseline links, 315,648 expected 5-min intervals). Retrospective public 10-minute HKO AWS data and visibility proved `[IRRECOVERABLE]` from open archives (paper authors received offline data from Dr. Yang Han at HKU; HKO API `LTMV` only returns real-time snapshot without historical queries). 100% cryptographic immutability of existing raw data verified (678 files). Documented in [`CTDIDataset Specifications.md`](Dataset/CTDIDataset%20Specifications.md), [`Visibility Data Recovery & Provenance Report.md`](Reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md), and [`Raw Data Integrity Manifest.md`](Dataset/Raw%20Data%20Integrity%20Manifest.md). Ready for CTDI-aligned Preprocessing."""

new_s1 = """- **Current Development Status**: **`PHASE_2_ALIGNED_DATASET_READY`**. 
  - **Phase 1 Source-Specific Cleaning**: **`COMPLETE`**. Air quality ($420,864$ rows, $55,876$ natural missing NaNs preserved, 0 duplicates, 0 negative values) and meteorology (ERA5 surface reanalysis, 0 NaNs, physical bounds verified) standardized independently.
  - **Phase 1.1 Complete Traffic Extraction**: **`COMPLETE`**. All 36 monthly archives extracted: **774,686 snapshots**, **466,829,497 records**, 632 unique links union (590 core links), speeds in $[0, 111]\text{ km/h}$ (mean $57.66\text{ km/h}$), saturation mapped ordinally (0.0, 0.5, 1.0).
  - **Phase 2 Spatio-Temporal Alignment**: **`COMPLETE`**. Unified Cartesian grid constructed across $16 \text{ stations} \times 26,304 \text{ hours} = \mathbf{420,864} \text{ station-hours}$ across all 13 canonical channels ($5,471,232$ float values). IDW ($p=2$) spatial mapping validated without coordinate fabrication. $16 \times 16$ symmetric Haversine distance matrix verified. Automated validation passed 9/9 checks with 0 errors (`data/interim/aligned/alignment_validation.json`).
  - **Cryptographic Immutability**: 100% verified across 683 raw files in `data/raw/` (0 modified, 0 deleted, 0 added).
  - **Next Phase**: Phase 3 (24-hour sliding window segmentation and missingness mask generation)."""

text = text.replace(old_s1, new_s1)

# 3. Add Phase 1.1 and Phase 2 to Section 7 chronological logs
target_p1 = """  - Published comprehensive research report: [`Phase 1 - Source-Specific Cleaning Report.md`](Reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)."""

new_p1_p2 = """  - Published comprehensive research report: [`Phase 1 - Source-Specific Cleaning Report.md`](Reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md).
- **2026-09-17 (Phase 1.1: Complete Historical Traffic Extraction Complete)**:
  - Extracted and processed all 36 monthly archives (2019-01 to 2021-12) from Transport Department Traffic Speed Map.
  - Processed **774,686 snapshots** across 1,096 calendar days (0 missing days, 0 failures).
  - Extracted **466,829,497 total link records** across 632 unique links union (590 common core links present in every snapshot).
  - Validated speeds in $[0, 111]\text{ km/h}$ (mean $57.66\text{ km/h}$); mapped categorical saturation ordinally (`GOOD`=0.0, `AVERAGE`=0.5, `BAD`=1.0).
  - Serialized complete table to `data/interim/traffic/clean_traffic_speedmap_complete.parquet`.
- **2026-09-17 (Phase 2: Spatio-Temporal Alignment & 13-Channel Dataset Complete)**:
  - Assembled unified Cartesian grid: $\mathcal{S} \times \mathcal{T} = 16 \text{ stations} \times 26,304 \text{ hours} = \mathbf{420,864} \text{ station-hour observations}$.
  - Unified all 13 canonical channels: 5 air pollutants (`pm25`, `pm10`, `no2`, `so2`, `o3`), 6 meteorological variables (`pressure`, `relative_humidity`, `temperature`, `rainfall`, `wind_direction`, `wind_speed`), and 2 traffic variables (`traffic_speed`, `traffic_congestion`).
  - Executed spatial IDW ($p=2$) projection of 632 road links to 16 stations (418,448 rows, 99.43% coverage, 2,416 natural archive missing hours preserved as NaN with zero artificial 0 km/h filling).
  - Verified 3D tensor reshapeability: $(420864, 13) \to (16, 26304, 13) = \mathbf{5,471,232} \text{ values}$.
  - Verified $16 \times 16$ symmetric Haversine distance matrix (`data/interim/aligned/spatial_distance_matrix.npy`).
  - Automated validation suite: 9/9 assertions passed with 0 errors (`data/interim/aligned/alignment_validation.json`).
  - Serialized primary dataset to `data/interim/aligned/aligned_hourly_station_data.parquet`.
  - Published comprehensive engineering report: [`Phase 2 - Spatio-Temporal Alignment Report.md`](Reports/Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md)."""

text = text.replace(target_p1, new_p1_p2)

# 4. Section 19 Timeline additions
old_tl = """- **2026-09-14**: [CTDI Empirical Missingness Analysis (Figs. 6–10) & 1-Hour Temporal Offset Resolution](Checkpoints/2026-09-14.md)"""
new_tl = """- **2026-09-14**: [CTDI Empirical Missingness Analysis (Figs. 6–10) & 1-Hour Temporal Offset Resolution](Checkpoints/2026-09-14.md)
- **2026-09-17**: [Phase 1 Source-Specific Cleaning & Standardization](Reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)
- **2026-09-17**: [Phase 1.1 Complete Historical Traffic Extraction (774k snapshots, 466M records)](Checkpoints/2026-09-17_phase_1_1.md)
- **2026-09-17**: [Phase 2 Spatio-Temporal Alignment & 13-Channel Multimodal Dataset](Checkpoints/2026-09-17_phase_2.md)"""

text = text.replace(old_tl, new_tl)

# 5. Section 20 Current Stopping Point
old_sp = """CURRENT STOPPING POINT
===============================================================================
Date:                   2026-09-14
Operational Status:     CTDI_ALIGNED_RECONSTRUCTION_WITH_DOCUMENTED_DIFFERENCES
Completed Today:        1. Created and fully executed Jupyter Notebook notebooks/01_ctdi_style_missingness_analysis.ipynb
                           (32 cells, all assertions passing, exact 55,876 missing count conservation verified).
                        2. Generated publication-quality reproductions of CTDI Figures 6, 7, 8, 9, 10, and
                           a composite 3-panel distribution suite (research/figures/).
                        3. Discovered and resolved critical 1-hour temporal offset ($h \to h-1$) between EPD 1-indexed
                           interval-end logging (HOUR 1..24) and ISO interval-start timestamps (00:00..23:00).
                        4. Mathematically reconciled diurnal curve: nominal CTDI hour = (dt.hour + 1) % 24.
                        5. Verified bit-for-bit match with published CTDI paper (Yu et al., Section IV-B, Page 2448):
                           • Hour 1 (01:00 am): Primary nocturnal calibration peak (~9,000 items, 16.0%)
                           • Hour 4 (04:00 am): Secondary operational outage spike (~5,728 items, 10.3%)
                           • Hour 12 (12:00 pm): Midday maintenance peak (~4,189 items, 7.5%)
                           • Hour 0 (Midnight): Nocturnal baseline lull (~1,298 items, 2.3%)
                        6. Formulated multimodal alignment rule: air quality interval [t, t+1h) pairs with
                           meteorology and traffic conditions at interval end (t + 1h).
                        7. Updated CTDI Missingness Pattern Analysis.md, MASTER_RESEARCH_DOCUMENT.md,
                           research_status.md, and research_timeline.md.
Verified Today:         • Figures 6, 7, 8, 9, 10 match CTDI empirical characteristics bit-for-bit.
                        • Zero label collisions in Figure 7 24-hour pie chart (boxed callouts & pointer arrows).
                        • 100% cryptographic immutability of existing raw data preserved.
Failed / Rejected:      • Naive dt.hour grouping on interval-start timestamps (rejected due to 1-hour backward shift).
Remaining Work:         1. Update channel schema in src/preprocessing/canonical.py.
                        2. Batch ingestion of parent 1st Gen Speedmap snapshots to build hourly traffic table.
                        3. Execute spatial IDW (p=2) mapping across 607 road links in Data Preprocessing phase.
                        4. Assemble canonical tensor X ∈ R^(16 × 26304 × 13) and binary mask tensor.
                        5. Implement and train SLM-Conditioned Diffusion model.
What Must Happen Next:  Begin Phase 2 "CTDI-Aligned Dataset Preprocessing": update canonical channel
                        definitions and execute traffic batch extraction and spatial IDW projection.
Known Limitations:      • Meteorological features use ERA5 surface reanalysis (with rainfall) rather than
                        in-situ 47-station AWS visibility due to open-access data availability constraints.
Files Changed Today:    • notebooks/01_ctdi_style_missingness_analysis.ipynb (Created & Executed)
                        • scripts/generate_missingness_notebook.py (Created & Updated)
                        • scripts/generate_pie_charts.py (Created & Updated)
                        • research/figures/*.png (Generated / Updated)
                        • research/reports/CTDI Missingness Pattern Analysis.md (Updated)
                        • research/MASTER_RESEARCH_DOCUMENT.md (Updated)
                        • research/research_status.md (Updated)
                        • research/research_timeline.md (Updated)
                        • research/checkpoints/2026-09-14.md (Created)
==============================================================================="""

new_sp = """CURRENT STOPPING POINT
===============================================================================
Date:                   2026-09-17
Operational Status:     PHASE_2_ALIGNED_DATASET_READY
Completed Deliverables: 1. Phase 1 Source-Specific Cleaning: Air Quality (420,864 rows, 55,876 NaNs preserved)
                           and Meteorology (ERA5 surface reanalysis, 0 NaNs) standardized independently.
                        2. Phase 1.1 Complete Traffic Extraction: 774,686 snapshots across all 36 months,
                           466,829,497 records, 632 unique links union, 590 core links, 0 failed snapshots.
                        3. Phase 2 Spatio-Temporal Alignment: Unified 13-channel Cartesian grid
                           (420,864 station-hours, shape (16, 26304, 13) = 5,471,232 values) validated.
                        4. Spatial IDW (p=2) mapping executed on 632 georeferenced road links to 16 stations;
                           2,416 natural archive missing hours preserved as NaN (zero 0 km/h filling).
                        5. Pairwise 16x16 symmetric Haversine distance matrix computed and verified.
                        6. Automated validation suite: 9/9 assertions passed with 0 errors (alignment_validation.json).
                        7. 100% cryptographic raw-data immutability preserved across all 683 raw files.
                        8. Research Knowledge Base fully curated, consolidated into 15 core topics,
                           and directories renamed to Title Case matching file naming convention.
Verified Today:         • Aligned dataset: data/interim/aligned/aligned_hourly_station_data.parquet (6.42 MB).
                        • Intermediate tables: traffic_hourly_link_data.parquet, traffic_station_hourly.parquet.
                        • Zero broken markdown links and zero broken <img> tags across repository.
Remaining Work:         1. Phase 3: 24-Hour Sliding Window Segmentation (K = 26,281 windows of shape (24, 16, 13)).
                        2. Phase 3: Missingness Mask Generation (Random, Spatial-Block, Temporal-Block at 10%, 30%, 50%, 70%).
                        3. Phase 3: Zero-data-leakage MinMax feature normalization (fit on Train split ONLY).
                        4. SLM Environmental Context Builder and conditional diffusion training.
What Must Happen Next:  Begin Phase 3 "24-Hour Sliding Window Segmentation & Missingness Mask Generation"
                        upon user authorization.
Known Boundaries:       • Meteorological features use ERA5 surface reanalysis (with rainfall) rather than
                        in-situ 47-station AWS visibility due to open-access data availability constraints.
                        • Categorical traffic saturation mapped ordinally (0.0, 0.5, 1.0) under documented assumption.
==============================================================================="""

text = text.replace(old_sp, new_sp)

with open("research/MASTER_RESEARCH_DOCUMENT.md", "w") as f:
    f.write(text)

print("Updated research/MASTER_RESEARCH_DOCUMENT.md successfully.")
