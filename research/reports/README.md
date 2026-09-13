# Investigation Reports, Execution Logs & Archival Analyses

This directory archives raw empirical reports, verbatim table reconstructions, execution logs, and detailed reference manuals produced during the project.

---

## Reports Inventory & Epistemic Status

| Report Filename | Topic & Focus | Epistemic Status | Historical / Scientific Context |
| :--- | :--- | :---: | :--- |
| **[ctdi_table_i_reconstruction.md](ctdi_table_i_reconstruction.md)** | Verbatim reproduction of Table I from Yu et al. (IEEE TBD 2025) | **`VERIFIED`** | Gold-standard reference discovered on 2026-09-13. Proves 13 channels, 607 road links, visibility, and traffic congestion. |
| **[ctdi_traffic_variable_verification.md](ctdi_traffic_variable_verification.md)** | Exhaustive candidate traffic variable evidence matrix & 607-link proof | **`VERIFIED`** | Proves parent `speedmap.xml` contains 607 links and 774k continuous snapshots; refutes ATC and City Dashboard 2019. |
| **[ctdi_channel_reconstruction.md](ctdi_channel_reconstruction.md)** | Reconstructed 13-channel specification and code divergence analysis | **`VERIFIED`** | Explicitly documents the divergence between CTDI Table I (visibility, congestion) and prior interim code (rainfall, volume). |
| **[Alignment - PY.md](Alignment%20-%20PY.md)** | Standalone execution output of `src/preprocessing/alignment.py` | **`OBSERVED`** | Documents pipeline execution, Cartesian grid verification (420,864 rows), and clean safety halt when real traffic is absent. |
| **[CTDI Dataset Description.md](CTDI%20Dataset%20Description.md)** | Comprehensive background dataset description (Authored 2026-09-12) | **`PARTIALLY_SUPERSEDED`** | Station metadata and exclusion of Southern (#84) & North (#85) are **VERIFIED**; references to `rainfall` and `traffic_volume` are **SUPERSEDED** by Table I discovery on 2026-09-13. |
| **[Data Processing - Hong Kong.md](Data%20Processing%20-%20Hong%20Kong.md)** | 454-line comprehensive data engineering handbook | **`PARTIALLY_SUPERSEDED`** | Normalization, windowing, and SLM context design are **VERIFIED**; early channel listings with rainfall/volume are **SUPERSEDED** by Table I discovery. |
| **[Phase 1.md](Phase%201.md)** | Phase 1 raw data verification execution log | **`OBSERVED`** | Verifies air quality (420,864 rows) and meteorology raw caches. Refers to ATC census which was later found non-continuous. |
| **[Phase 2.md](Phase%202.md)** | Phase 2 & 3 spatial alignment and tensor construction plan | **`SUPERSEDED`** | Early plan mentioning Open-Meteo rainfall and ATC traffic volume; superseded by strict 607-road Speedmap reconstruction. |
| **[Data Preprocessing/](Data%20Preprocessing/)** | 10-part modular data engineering guides (00 to 09) | **`ACTIVE / PRESERVED`** | Modular guides detailing ingestion, cleaning, missingness, windowing, and context generation. |

---

## Preservation Philosophy
Existing documentation files are preserved as immutable historical evidence. Outdated information is never silently deleted or rewritten; it is explicitly marked with status badges (`SUPERSEDED` / `PARTIALLY_SUPERSEDED`) and referenced to the modern verified standards in `research/dataset/` and `research/MASTER_RESEARCH_DOCUMENT.md`.
