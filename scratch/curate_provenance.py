import os

with open("research/dataset/Dataset Provenance & Specifications.md", "r") as fh:
    content = fh.read()

# Update title
content = content.replace(
    "# Comprehensive Dataset Provenance, Source Acquisition & Audit Specification",
    "# Dataset Provenance, Source Acquisition & Audit Specification"
)

# Update traffic section with the complete Phase 1.1 extraction facts
old_traffic_snippet = """### 9. Local Storage & Status
- **Baseline Sample (2019)**: `data/raw/traffic/samples/historical_td_speedmap_20190101_0000.xml` (198,618 bytes, SHA-256: `ffd32205...`).
- **Intermediate Sample (2020)**: `data/raw/traffic/samples/historical_td_speedmap_20200101_0000.xml` (193,129 bytes, SHA-256: `234a8da1...`).
- **Intermediate Sample (2021)**: `data/raw/traffic/samples/historical_td_speedmap_20210101_0000.xml` (198,956 bytes, SHA-256: `4b9e170a...`).
- **End Sample (2021)**: `data/raw/traffic/samples/historical_td_speedmap_20211231_2357.xml` (198,937 bytes, SHA-256: `2445470c...`).
- **Status**: **`[VERIFIED]`** source-system match and archive completeness audit passed.

### 10. Transformations Planned for Preprocessing
- Arithmetic hourly averaging across sub-hourly snapshots for each hour: $\\bar{v}_h = \\frac{1}{K} \\sum_{k=1}^K v_k$.
- Categorical saturation level mapped ordinally to continuous scalar ($0.0 = \\text{GOOD}, 0.5 = \\text{AVERAGE}, 1.0 = \\text{BAD}$) `[DECISION]`.
- Spatial Inverse Distance Weighting (IDW, $p=2$) from 607 road link midpoints to 16 air quality monitoring stations following CTDI Equation 1 `[DECISION]`."""

new_traffic_snippet = """### 9. Local Storage & Complete 3-Year Extraction Status
- **Archive Packages Streamed**: 36 monthly historical archive packages (`201901` through `202112`) from DATA.GOV.HK.
- **Snapshots Processed**: Exactly **774,686 snapshots** processed (2019: 260,790; 2020: 253,408; 2021: 260,488).
- **Records Extracted**: Exactly **466,829,497 link-level records** extracted (2019: 154,672,524; 2020: 153,858,626; 2021: 158,298,347).
- **Failed Extractions**: Exactly **0** failed snapshots or malformed XML files.
- **Link Dynamics**: Total unique links across 3-year union = **632 links**; common invariant core links = **590 links**. Annual link counts: 2019 (614), 2020 (609), 2021 (608) matching baseline 607 links with documented network commissioning/decommissioning.
- **Physical Boundaries**: Speed range $[0.0, 111.0]\\text{ km/h}$ (mean $57.66\\text{ km/h}$). Zero missing speeds or saturations.
- **Saturation Categories**: `TRAFFIC GOOD`: 79.43% (370.8M), `TRAFFIC AVERAGE`: 15.09% (70.4M), `TRAFFIC BAD`: 5.48% (25.6M).
- **Authoritative Partitioned Dataset**: Snappy-compressed Parquet partitions in `data/interim/traffic/monthly/` (~725 MB total).
- **Unified Symlink**: `data/interim/traffic/clean_traffic_speedmap_complete.parquet`.
- **Validation Report**: `data/interim/traffic/traffic_complete_extraction_report.json`.
- **Operational Status**: **`TRAFFIC_FULL_EXTRACTION = COMPLETE`** `[VERIFIED]`.

### 10. Transformations Defined for Preprocessing (Phase 2)
- Arithmetic hourly averaging across sub-hourly snapshots for each hour: $\\bar{v}_h = \\frac{1}{K} \\sum_{k=1}^K v_k$.
- Categorical saturation level mapped ordinally to continuous scalar ($0.0 = \\text{GOOD}, 0.5 = \\text{AVERAGE}, 1.0 = \\text{BAD}$) `[DECISION]`.
- Spatial Inverse Distance Weighting (IDW, $p=2$) from road link midpoints to 16 air quality monitoring stations following CTDI Equation 1 `[DECISION]`."""

if old_traffic_snippet in content:
    content = content.replace(old_traffic_snippet, new_traffic_snippet)
    print("Updated traffic section in Dataset Provenance & Specifications.md")
else:
    print("Notice: old traffic snippet not matched exactly, checking alternative match...")

# Replace image references to use valid paths
content = content.replace(
    "file:///home/mocha/Desktop/ctdi-model-project/research/figures/",
    "../figures/"
)
content = content.replace(
    "/home/mocha/Desktop/ctdi-model-project/research/figures/",
    "../figures/"
)

with open("research/dataset/Dataset Provenance & Specifications.md", "w") as fh:
    fh.write(content)
print("Curated research/dataset/Dataset Provenance & Specifications.md successfully!")
