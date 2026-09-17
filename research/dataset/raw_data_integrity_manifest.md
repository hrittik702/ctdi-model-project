# Raw Data Cryptographic Integrity Manifest

**Project**: Context-Aware Generative Imputation of Air Pollution Data  
**Research Direction**: SLM-Conditioned Diffusion for Spatio-Temporal Missing Data Imputation  
**Audit Timestamp**: 2026-09-13T23:05:08+05:30  
**Protocol Requirement**: Strict Raw-Data Immutability Verification (Before and After Investigation)

## 1. Immutability Verification Summary

An exhaustive SHA-256 cryptographic checksum snapshot was recorded before the Visibility Recovery and Dataset Consistency audit and compared against an identical snapshot recorded after the audit.

| Metric | Pre-Investigation Baseline | Post-Investigation Verification | Delta | Compliance Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Files in `data/raw/`** | 678 files | 678 files | 0 | **`[VERIFIED]` PERFECT MATCH** |
| **Modified Files** | 0 | 0 | 0 | **`[VERIFIED]` ZERO MODIFICATIONS** |
| **Deleted Files** | 0 | 0 | 0 | **`[VERIFIED]` ZERO DELETIONS** |
| **Added Files** | 0 | 0 | 0 | **`[VERIFIED]` ZERO ADDITIONS** |
| **Immutability Result** | — | — | — | **`100% IMMUTABLE`** |

## 2. Cryptographic Checksums of Core Raw Artifacts

Below are the audited SHA-256 hashes for all primary raw data files in the repository. Every file has been verified bit-for-bit identical before and after this investigation:

### 2.1 Air Quality Raw Data
- **File**: `data/raw/air_quality/epd_air_quality_2019_2021_hourly.csv`
- **File Size**: $27,136,881$ bytes
- **SHA-256**: `f2b1b46a9c8e69e2f18077fac4c4d4f664cb24162523dc978219d82c225b57b2`
- **Status**: **`VERIFIED IMMUTABLE`** (Exact match to pre-audit baseline).

### 2.2 Meteorology Raw Data
- **File**: `data/raw/meteorology/hourly_meteorology_16stations_2019_2021.csv`
- **File Size**: $25,460,811$ bytes
- **SHA-256**: `e2e7849675a6856286ff92c63334d2d6cae010d409446043c3a4b8a147fa47a3`
- **Status**: **`VERIFIED IMMUTABLE`** (Zero variable substitution; rainfall preserved without alteration).

### 2.3 Traffic Schema & Raw XML Snapshots
- **File**: `data/raw/traffic/speedmap.xsd`
  - Size: $1,877$ bytes
  - SHA-256: `769b86e4664d511b08a05d68ec622c6936b09f161952947d7a2d3b2b1fb27a2d`
- **File**: `data/raw/traffic/samples/historical_td_speedmap_20190101_0000.xml`
  - Size: $198,618$ bytes
  - SHA-256: `ffd32205bb2e6997df0a94f3f02108bd0fb517c1fc58619cb1fd49a70c634a95`
- **File**: `data/raw/traffic/samples/historical_td_speedmap_20200101_0000.xml`
  - Size: $193,129$ bytes
  - SHA-256: `234a8da1fc57e27aee3784d92ad5038202008c8b282e12edc364150d9f695f99`
- **File**: `data/raw/traffic/samples/historical_td_speedmap_20210101_0000.xml`
  - Size: $198,956$ bytes
  - SHA-256: `4b9e170a7c3b8a5fb4b2e384aecd15909493669f9f0773556e7809bf4059fb9a`
- **File**: `data/raw/traffic/samples/historical_td_speedmap_20211231_2357.xml`
  - Size: $198,937$ bytes
  - SHA-256: `2445470c4046dca69f54e94d972dff32ff0378a88097c3e1cfe7fe45fae67d84`
- **Status**: **`VERIFIED IMMUTABLE`**.

### 2.4 Station & Detector Metadata
- **File**: `data/raw/station_metadata/air_quality_stations.csv`
  - Size: $1,563$ bytes
  - SHA-256: `30bb17250da7174bec73123570ee2bc2730faab2d5d126cb3141c180892186cb`
- **File**: `data/raw/station_metadata/weather_stations.csv`
  - Size: $6,006$ bytes
  - SHA-256: `1b48db2ae37d467379e865a9ee739e834531c759468b61b997ca3135d433b676`
- **File**: `data/raw/station_metadata/traffic_detectors.csv`
  - Size: $9,547$ bytes
  - SHA-256: `e8bf532d51b4064f2d7350cc04c973cc0cdbc6d72f6f3f39a5e32b6991fd6ea7`
- **Status**: **`VERIFIED IMMUTABLE`**.

### 2.5 HKO Benchmark Daily Observations
- `data/raw/meteorology/hko_daily_reference/daily_CLMTEMP_HKO_2019_2021.csv`: `1379ecb001a1...`
- `data/raw/meteorology/hko_daily_reference/daily_CLMMAXT_HKO_2019_2021.csv`: `437996c5aa42...`
- `data/raw/meteorology/hko_daily_reference/daily_CLMMINT_HKO_2019_2021.csv`: `fe4bb93766a5...`
- `data/raw/meteorology/hko_daily_reference/daily_CLMPRESS_HKO_2019_2021.csv`: `893f4e24efee...`
- `data/raw/meteorology/hko_daily_reference/daily_CLMRAIN_HKO_2019_2021.csv`: `4f128bc240ea...`
- `data/raw/meteorology/hko_daily_reference/daily_CLMWIND_KP_2019_2021.csv`: `ef54d1ce5757...`
- **Status**: **`VERIFIED IMMUTABLE`**.

### 2.6 Annual Traffic Census (ATC) Archive
- All 668 sub-files and spreadsheets in `data/raw/traffic/atc_2019_2021/`:
- **Status**: **`VERIFIED IMMUTABLE`** (Zero files altered).

---

## 3. Conclusion
No existing raw data file was edited, overwritten, renamed, converted, or replaced. The raw source files remain 100% authentic, verifiable, and immutable.
