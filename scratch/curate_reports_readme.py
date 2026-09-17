content = """# Investigation Reports, Execution Logs & Archival Analyses

This directory archives empirical investigation reports, verbatim table reconstructions, execution logs, and detailed reference manuals produced during the project.

---

## 1. Primary Empirical Reports & Audits

| Report Title & Filename | Topic & Focus | Epistemic Status | Historical / Scientific Context |
| :--- | :--- | :---: | :--- |
| **[ctdi table I reconstruction.md](ctdi%20table%20I%20reconstruction.md)** | Verbatim reproduction of Table I from Yu et al. (IEEE TBD 2025) | **`VERIFIED`** | Gold-standard reference discovered on 2026-09-13. Proves 13 channels, 607 road links, visibility, and traffic congestion. |
| **[ctdi traffic variable verification.md](ctdi%20traffic%20variable%20verification.md)** | Candidate traffic variable evidence matrix & 607-link proof | **`VERIFIED`** | Proves parent `speedmap.xml` contains 607 links and 774k continuous snapshots; refutes ATC and City Dashboard 2019. |
| **[ctdi channel reconstruction.md](ctdi%20channel%20reconstruction.md)** | Reconstructed 13-channel specification and code divergence analysis | **`VERIFIED`** | Explicitly documents the divergence between CTDI Table I (visibility, congestion) and prior interim code (rainfall, volume). |
| **[ctdi source fidelity report.md](ctdi%20source%20fidelity%20report.md)** | Source data fidelity compared to CTDI paper | **`VERIFIED`** | Compares raw source characteristics against published citations, proving exact coverage across air, met, and traffic. |
| **[CTDI Missingness Pattern Analysis.md](CTDI%20Missingness%20Pattern%20Analysis.md)** | Empirical replication of Figures 6–9 and diurnal analysis | **`VERIFIED`** | Explains the 1-hour interval-start vs. nominal logging convention, confirms 01:00 am calibration spike, and 20% pollutant parity. |
| **[Visibility Data Recovery & Provenance Report.md](Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)** | HKO visibility irrecoverability audit & rainfall substitution | **`DECISION`** | Proves retrospective 10-min HKO AWS visibility is irrecoverable from public sources; scientifically justifies ERA5 rainfall substitution. |
| **[Raw Data Availability & Verification.md](Raw%20Data%20Availability%20&%20Verification.md)** | Initial raw download availability and physical bounds check | **`VERIFIED`** | Validates the initial download of EPD air quality, Open-Meteo/ERA5 meteorology, and ATC census archives. |
| **[Phase 1 - Source-Specific Cleaning Report.md](Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)** | Source-specific data cleaning, schemas, and traffic extraction | **`ACTIVE`** | Comprehensive engineering report detailing transformations, bilingual header cleaning, and Phase 1.1 complete traffic extraction. |

---

## 2. Working Notes, Blueprints & Execution Logs

| Report Title & Filename | Topic & Focus | Epistemic Status | Historical / Scientific Context |
| :--- | :--- | :---: | :--- |
| **[Alignment - PY.md](Alignment%20-%20PY.md)** | Execution output and console log of `src/preprocessing/alignment.py` | **`OBSERVED`** | Documents Cartesian grid verification (420,864 rows) and clean safety halt when real traffic was absent. |
| **[CTDI Dataset Description.md](CTDI%20Dataset%20Description.md)** | Comprehensive background dataset description (Authored 2026-09-12) | **`PARTIALLY_SUPERSEDED`** | Station metadata is **VERIFIED**; early references to `rainfall` and `traffic_volume` are **SUPERSEDED** by Table I discovery. |
| **[Data Processing - Hong Kong.md](Data%20Processing%20-%20Hong%20Kong.md)** | 454-line comprehensive data engineering handbook | **`ACTIVE / PRESERVED`** | Authoritative pipeline guide detailing normalization, sliding windowing, and SLM context generation. |
| **[Phase 1.md](Phase%201.md)** | Phase 1 raw data verification execution log | **`OBSERVED`** | Raw terminal output of running `scripts/verify_raw_datasets.py` on verified air quality and meteorology. |
| **[Phase 2.md](Phase%202.md)** | Spatial alignment and canonical tensor construction plan | **`SUPERSEDED`** | Early planning document for Phase 2 & 3; superseded by the modular data preprocessing playbook. |
| **[Data Preprocessing/](Data%20Preprocessing/)** | 10-chapter modular data engineering guides (Chapters 00 to 09) | **`ACTIVE / PRESERVED`** | Detailed modular specifications for each pipeline phase, connected with bidirectional Obsidian wikilinks. |

---

## 3. Preservation Philosophy

Existing investigation reports are preserved as immutable empirical evidence. Outdated information is never silently erased; it is explicitly marked with status badges (`SUPERSEDED` / `PARTIALLY_SUPERSEDED`) and cross-referenced to the modern primary standards in `research/dataset/` and `research/MASTER_RESEARCH_DOCUMENT.md`.
"""

with open("research/reports/README.md", "w") as fh:
    fh.write(content)
print("Updated research/reports/README.md successfully!")
