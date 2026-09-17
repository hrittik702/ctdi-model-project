# Confirmed Research Findings

Only empirical facts supported by direct textual citations, mathematical derivations, official data archives, or reproducible script executions are recorded here.

---

## Finding F01: CTDI Benchmark Multimodal Feature Space Has Exactly 13 Channels
- **Finding**: The Hong Kong dataset in CTDI consists of exactly 13 feature channels across 16 stations from 2019-01-01 to 2021-12-31 ($X \in \mathbb{R}^{16 \times 26,304 \times 13}$).
- **Evidence**: Verbatim Table I on Page 2448 of Yu et al. (IEEE TBD 2025).
- **Date**: 2026-09-13
- **Source**: Published IEEE Transactions paper.
- **Confidence**: **`HIGH`**
- **Implication**: Any model claiming direct comparison with CTDI must evaluate on this 13-channel geometry.

---

## Finding F02: `traffic_volume` Does NOT Exist in CTDI
- **Finding**: CTDI does not use `traffic_volume`. The two traffic variables in CTDI Table I are `Traffic speed` and `Traffic congestion`.
- **Evidence**: Textual search of Yu et al. (2025) confirms zero occurrences of "traffic volume" in reference to experimental features. Table I lists `Traffic speed` ($\text{km/h}$) and `Traffic congestion` ($\text{N/A}$).
- **Date**: 2026-09-13
- **Source**: Paper analysis (`research/reports/ctdi_traffic_variable_verification.md`).
- **Confidence**: **`HIGH`**
- **Implication**: Previous project code utilizing Annual Traffic Census (ATC) volume counts was fundamentally misaligned with the published paper.

---

## Finding F03: The CTDI Traffic Network Uses 607 Road Links
- **Finding**: The traffic domain in CTDI comprises 607 road links across Hong Kong.
- **Evidence**: Table I explicitly states `Number of Data Nodes = 607 roads`. Inspection of snapshot `ffd32205bb2e...` (`2019-01-01 00:00 HKT`) from the parent Transport Department 1st Gen Traffic Speed Map (`speedmap.xml`) contains exactly $607$ unique `<LINK_ID>` elements.
- **Date**: 2026-09-13
- **Source**: DATA.GOV.HK historical XML archive (`hk-td-sm_1-traffic-speed-map`).
- **Confidence**: **`HIGH`**
- **Implication**: Resolves the apparent discrepancy with the City Dashboard portal version (which exposes only 6 links). The 6 links are an exact subset of the 607 parent links.

---

## Finding F04: CTDI Meteorological Channel 4 is Visibility (NOT Rainfall)
- **Finding**: CTDI utilizes `Visibility` ($\text{km}$) as its fourth weather feature, not `rainfall`.
- **Evidence**: Table I explicitly lists `Visibility` ($\text{km}$) alongside Pressure, Relative humidity, Temperature, Wind direction, and Wind speed.
- **Date**: 2026-09-13
- **Source**: Published IEEE Transactions paper (`research/reports/ctdi_table_i_reconstruction.md`).
- **Confidence**: **`HIGH`**
- **Implication**: Interim reanalysis data using rainfall must be updated or tracked as an explicit source-fidelity divergence.

---

## Finding F05: Identification and Rationale for the 2 Excluded Stations
- **Finding**: The two air quality stations excluded by CTDI authors for historical consistency are **Southern (#84)** and **North (#85)**.
- **Evidence**: EPD monthly records confirm both stations were commissioned on July 10, 2020 and did not exist during 2019 or the first half of 2020.
- **Date**: 2026-09-12
- **Source**: EPD station commissioning records (`research/dataset/station_inventory.md`).
- **Confidence**: **`HIGH`**
- **Implication**: Confirms the exact 16 stations required for 3-year continuous temporal alignment ($26,304$ hours).
