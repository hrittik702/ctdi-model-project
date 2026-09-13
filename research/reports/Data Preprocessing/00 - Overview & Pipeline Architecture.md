# 00 - Overview & Pipeline Architecture

> **Research Framework**: Context-Aware Generative Imputation of Air Pollution Using SLM-Conditioned Diffusion  
> **Benchmark Reference**: Yu et al., *"CTDI: CNN-Transformer-Based Spatial-Temporal Missing Air Pollution Data Imputation"*, IEEE Transactions on Big Data, 2025.  
> **Target Domain**: Hong Kong SAR (2019-01-01 to 2021-12-31, 1,096 days = 26,304 continuous hours across 16 monitoring stations).

---

## 1. Map of Content (Modular Navigation)

This modular documentation suite guides you through every phase of the data engineering lifecycle—from raw public data acquisition to the final model-ready tensors:

| Step | Modular Document | Core Purpose |
| :---: | :--- | :--- |
| **01** | [[01 - Raw Data Sources & Ingestion]] | Discovery, scraping, and download of EPD air quality, HKO/Open-Meteo meteorology, TD traffic, and station metadata. |
| **02** | [[02 - Cleaning, Translation & Formatting]] | Eliminating Chinese/bilingual text, standardizing column schemas, parsing 24-hour time conventions, and sanitizing missing flags. |
| **03** | [[03 - Missingness Architecture (Natural vs Simulated)]] | Distinguishing between the ~2.5% natural missingness ($\mathbf{M}_{\text{obs}}$) and benchmark simulated missingness ($\mathbf{M}_{\text{eval}}$ at 10%, 30%, 50%, 70%). |
| **04** | [[04 - Spatial Alignment & 13-Channel Formulation]] | Anchoring meteorology and traffic to the 16 air stations; constructing the canonical $\mathbf{X} \in \mathbb{R}^{16 \times 26,304 \times 13}$ master tensor. |
| **05** | [[05 - Feature Engineering & Normalization]] | Chronological train/val/test splits (70/15/15), zero-data-leakage scaling, and cyclical $\sin/\cos$ temporal embeddings. |
| **06** | [[06 - 24-Hour Sliding Window Segmentation]] | Atmospheric diurnal cycles, sliding window extraction, and structuring $[B, 16, 24, 13]$ PyTorch DataLoader batches. |
| **07** | [[07 - Environmental Context Builder for SLM]] | Synthesizing structured English atmospheric and urban prompts for Small Language Model (SLM) conditioning vectors $\mathbf{c}_{\text{text}}$. |
| **08** | [[08 - Canonical Data Storage & File Layout]] | Storage formats (`.npy`, `.parquet`, `.json`), directory organization, and memory efficiency specifications. |
| **09** | [[09 - Quality Assurance & Verification Playbook]] | Automated test scripts, numerical assertions, and verification checklists. |

---

## 2. High-Level Data Transformation Flowchart

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: RAW INGESTION                                                                 │
│  - HK EPD: 36 monthly archives -> 420,864 hourly pollutant rows                        │
│  - Open-Meteo: 6 hourly weather channels at 16 exact coordinates                       │
│  - HKO: 6 official daily reference CSVs for physical calibration                       │
│  - Transport Dept: ATC survey archives (2019, 2020, 2021) + detector points            │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CLEANING & TRANSLATION                                                        │
│  - Strip Chinese characters -> Standard snake_case English identifiers                 │
│  - Standardize 1..24 hours -> Continuous ISO timestamps (2019-01-01 to 2021-12-31)     │
│  - Filter 16 continuous stations (exclude Southern #84 and North #85)                  │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: SPATIAL ANCHORING & CANONICAL TENSOR                                          │
│  - Master Feature Tensor: X ∈ R^(16 stations x 26,304 hours x 13 channels)             │
│  - Natural Observation Mask: M_obs ∈ {0, 1}^(16 x 26,304 x 13)                         │
│  - Total Numerical Elements: 5,471,232 float values                                    │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: PREPROCESSING & NORMALIZATION                                                 │
│  - Chronological Split: Train (70%), Val (15%), Test (15%)                             │
│  - Fit Scalers strictly on observed Train split (Zero Data Leakage)                    │
│  - Cyclical time encodings (Hour, Day-of-week, Month sin/cos)                          │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: WINDOWING, MASKS & SLM CONTEXT                                                │
│  - 24-Hour Sliding Windows: Batches [B, 16, 24, 13]                                    │
│  - Benchmark Missingness Injection: 10%, 30%, 50%, 70% (Point, Block, Spatial)        │
│  - SLM English Context Narrative: Station + meteorology text prompts                   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
                                READY FOR MODEL TRAINING
               [Tensor: (B, 16, 24, 13), Mask: (B, 16, 24, 13), Context: text]
```

---

## 3. Mathematical Dimensions at a Glance

- **Spatial Nodes ($S$)**: $16$ monitoring stations
- **Total Study Hours ($T$)**: $1,096 \text{ days} \times 24 \text{ hours/day} = \mathbf{26,304}$ timestamps
- **Feature Channels ($C$)**: $13$ variables
  - Pollutants ($5$): $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{O}_3, \text{SO}_2$
  - Meteorology ($6$): $\text{TEMP}, \text{RH}, \text{WS}, \text{WD}, \text{PRES}, \text{RAIN}$
  - Traffic ($2$): $\text{SPEED}, \text{VOL}$
- **Canonical Tensor Volume**: $16 \times 26,304 \times 13 = \mathbf{5,471,232}$ values
- **Sample Window Length ($L$)**: $24$ hours
- **Sample Window Tensor Shape**: $[16, 24, 13]$ ($4,992$ values per sample)
