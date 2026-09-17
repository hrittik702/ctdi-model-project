# Empirical Investigation Reports & Technical Handbooks

This directory archives empirical investigation reports, verbatim benchmark table reproductions, data engineering handbooks, and phase completion audits produced during the project.

---

## 1. Primary Empirical Reports & Audits

| Report Title & Filename | Topic & Focus | Epistemic Status | Historical / Scientific Context |
| :--- | :--- | :---: | :--- |
| **[Phase 1 - Source-Specific Cleaning Report.md](Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)** | Source-specific data cleaning, schemas, and traffic extraction | **`ACTIVE`** | Comprehensive engineering report detailing transformations, bilingual header cleaning, and Phase 1.1 complete traffic extraction (774k snapshots, 466M records). |
| **[Phase 2 - Spatio-Temporal Alignment Report.md](Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md)** | Spatio-temporal alignment & 13-channel multimodal dataset report | **`ACTIVE`** | Documents the alignment of 16 stations × 26,304 hours = 420,864 rows, IDW spatial mapping of 632 links, and tensor validation. |
| **[Visibility Data Recovery & Provenance Report.md](Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)** | HKO visibility irrecoverability audit & rainfall substitution | **`DECISION`** | Proves retrospective 10-min HKO AWS visibility is irrecoverable from public sources; scientifically justifies ERA5 rainfall substitution. |
| **[CTDI Missingness Pattern Analysis.md](CTDI%20Missingness%20Pattern%20Analysis.md)** | Empirical replication of Figures 6–9 and diurnal analysis | **`VERIFIED`** | Explains the 1-hour interval-start vs. nominal logging convention, confirms 01:00 am calibration spike, and 20% pollutant parity. |
| **[ctdi table I reconstruction.md](ctdi%20table%20I%20reconstruction.md)** | Verbatim reproduction of Table I from Yu et al. (IEEE TBD 2025) | **`VERIFIED`** | Gold-standard reference discovered on 2026-09-13. Proves 13 channels, 607 road links, visibility, and traffic congestion. |
| **[ctdi traffic variable verification.md](ctdi%20traffic%20variable%20verification.md)** | Candidate traffic variable evidence matrix & 607-link proof | **`VERIFIED`** | Proves parent `speedmap.xml` contains 607 links and 774k continuous snapshots; refutes ATC and City Dashboard 2019. |
| **[ctdi channel reconstruction.md](ctdi%20channel%20reconstruction.md)** | Reconstructed 13-channel specification and code divergence analysis | **`VERIFIED`** | Explicitly documents the divergence between CTDI Table I (visibility, congestion) and prior interim code (rainfall, volume). |
| **[ctdi source fidelity report.md](ctdi%20source%20fidelity%20report.md)** | Source data fidelity compared to CTDI paper | **`VERIFIED`** | Compares raw source characteristics against published citations, proving exact coverage across air, met, and traffic. |
| **[Raw Data Availability & Verification.md](Raw%20Data%20Availability%20&%20Verification.md)** | Initial raw download availability and physical bounds check | **`VERIFIED`** | Validates the initial download of EPD air quality, Open-Meteo/ERA5 meteorology, and ATC census archives. |
| **[Data Processing - Hong Kong.md](Data%20Processing%20-%20Hong%20Kong.md)** | Complete end-to-end data processing handbook (454 lines) | **`ACTIVE`** | Authoritative, monolithic pipeline guide detailing normalization, sliding windowing, and SLM context generation. |
| **[Research Information Curation Report.md](Research%20Information%20Curation%20Report.md)** | Full curation and consolidation audit of the research knowledge base | **`CURATED`** | Details the 15-topic canonical architecture, duplicate resolution, link repairs, and 15-question fast navigation test. |

---

## 2. Evidence Discipline & Archival Policy

Investigation reports represent empirical, immutable evidence produced during discovery and pipeline validation. Scratch logs, preliminary unformatted console outputs, and redundant draft copies have been pruned to prevent cognitive clutter, leaving only authoritative, reproducible empirical records.
