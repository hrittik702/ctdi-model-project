# SLM Context Architecture Specification

**Project**: Context-Aware Generative Imputation of Air Pollution Data  
**Direction**: SLM-Conditioned Diffusion for Spatio-Temporal Missing Data Imputation  
**Phase**: Phase 4A — Context Representation & SLM Architecture Specification  
**Status**: **`SPECIFICATION_COMPLETE`**  
**Date**: 2026-09-17  

---

## 1. Research Motivation & Theoretical Justification

### 1.1 The Failure Mode of Numerical Deep Imputation Under Extreme Missingness
Standard spatio-temporal missing data imputation models in atmospheric science—including the CTDI baseline (Yu et al., 2025), CSDI (Tashiro et al., 2021), PriSTI (Du et al., 2023), and SAITS (Du et al., 2023)—operate strictly on raw continuous floating-point tensors:
$$\mathbf{X} \in \mathbb{R}^{S \times K \times C}, \quad \mathbf{M} \in \{0, 1\}^{S \times K \times C}$$
Under moderate missingness ($10\%\text{--}30\%$), local temporal auto-regressive continuity and spatial inverse distance weighting (IDW) provide sufficient numerical covariance for deterministic neural networks to interpolate missing values.

However, under extreme missingness ($50\%\text{--}70\%$) or sustained multi-channel sensor blackouts, **local numerical covariance is obliterated**. When both pollutant sensors and local weather telemetry fail simultaneously across neighboring stations:
1. Numerical models lack sufficient observed floats to reconstruct cross-channel covariance.
2. Generative and deterministic models suffer regression collapse, defaulting to the unconditioned climatological mean or flat diurnal profiles.
3. Physical and chemical constraints (e.g., photochemical $\text{O}_3\text{--}\text{NO}_2$ titration, non-negativity) are violated because the network cannot infer the synoptic state of the atmosphere.

### 1.2 Synoptic Regimes and Atmospheric Inductive Priors
Atmospheric dispersion and photochemical transformation are governed by discrete macro-scale synoptic regimes rather than isolated local micro-fluctuations. In the Hong Kong and Pearl River Delta (PRD) airshed, air quality is predominantly dictated by distinct synoptic states:
- **East Asian Winter Monsoon**: Strong continental northeasterly winds transport regional background pollution (high $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{SO}_2$) southward from industrial PRD mainland centers.
- **East Asian Summer Monsoon**: Moist, maritime southerly/southwesterly air masses off the South China Sea bring clean background air, heavy convective rainfall, and vigorous vertical mixing, resulting in low aerosol concentrations but episodic photochemical $\text{O}_3$ formation.
- **Typhoon Peripheral Subsidence**: Deep atmospheric stagnation, high ambient temperature, intense solar radiation, and calm winds trigger severe secondary photochemical smog and ozone surges trapped in coastal urban canyons.
- **Urban Street Canyon Entrapment**: Heavy morning/evening vehicular traffic corridors trapped by dense high-rise topography create localized primary $\text{NO}_2$ accumulation decoupled from regional background winds.

### 1.3 Small Language Models as Semantic Atmospheric Encoders
While a numerical neural network requires millions of parameters and hundreds of epochs to infer these macro-states from subtle float gradients, **modern Small Language Models (SLMs, 0.5B–3B parameters)** have internalized physical, geographic, temporal, and atmospheric relationships through massive web-scale pre-training.

By translating 24-hour multi-modal observations into structured environmental narratives, the SLM acts as a **zero-shot atmospheric prior**:
- It maps sparse, discrete weather and traffic indicators directly to a continuous semantic regime representation $\mathbf{z}_C \in \mathbb{R}^{d}$.
- This semantic embedding conditions the generative diffusion backbone, providing high-level physical guidance that constrains reverse diffusion trajectories even when $70\%$ of local numerical floats are missing.

---

## 2. Role of the Environmental Context Builder

The **Environmental Context Builder** (`src/context/context_builder.py`) is a deterministic translation orchestrator that converts numerical 24-hour window slices into structured, leakage-free representations.

### Key Responsibilities:
1. **Deterministic Feature Aggregation**: Computes robust summary statistics (min, max, mean, sum, diurnal range) across the 24-hour horizon for exogenous variables.
2. **Standardized Qualitative Descriptor Mapping**: Discretizes continuous numerical values into standardized atmospheric and urban descriptors using official Hong Kong Observatory (HKO) and Transport Department scales.
3. **Observational & Missingness Profiling**: Analyzes the active evaluation mask $\mathbf{M}_{\text{eval}}$ to diagnose missingness severity, channel dropout topology, and outage type (e.g., sporadic dropout vs. sustained sensor blackout).
4. **Strict Information Boundary Enforcement**: Enforces an absolute programmatic firewall between observed variables and hidden evaluation targets ($\mathbf{X}_{\text{hidden}}$).

---

## 3. Role of the Small Language Model (SLM)

The SLM functions strictly and exclusively as a **Semantic Context Encoder**:
$$\mathbf{z}_{\text{raw}} = \text{Pool}\left( \text{SLM}_{\text{frozen}}(\text{Tokens}(C)) \right) \in \mathbb{R}^{d_{\text{slm}}}$$

### Explicit Operational Boundaries:
- **NO Direct Imputation**: The SLM does **NOT** generate numerical pollutant values directly. It never predicts numerical floats like "PM2.5 = 24.3".
- **NO Autoregressive Generation**: During inference, the SLM does not perform causal token-by-token generation (no `generate()` loop). It executes a single deterministic forward pass through its transformer layers to obtain the hidden representation $\mathbf{H} \in \mathbb{R}^{L \times d_{\text{slm}}}$.
- **Frozen Backbone**: The pre-trained weights $\boldsymbol{\theta}_{\text{slm}}$ are completely frozen (`requires_grad = False`). Only a lightweight linear projection head $\mathbf{W}_p \in \mathbb{R}^{d_{\text{diff}} \times d_{\text{slm}}}$ and LayerNorm are trained end-to-end with the diffusion objective.
- **Computational Efficiency**: Because the SLM is frozen and context $C$ is static for a given 24-hour window, context embeddings $\mathbf{z}_C$ can be pre-computed and cached during training or batched efficiently in half-precision (FP16/BF16).

---

## 4. End-to-End Information Flow & Dimensional Flow

```
                           Raw 24-Hour Multi-Modal Window
                          X ∈ R^(24 × 13),  M_nat ∈ {0,1}^(24 × 13)
                                          │
                                          ▼
                         [Experimental Masking Partition]
                        M_eval ∈ {0,1}^(24 × 13)  (MCAR/Block/Station)
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
          Observed Data Stream                          Hidden Ground Truth
          X_obs = X ⊙ M_eval                           X_hidden = X ⊙ (1 - M_eval)
          M_eval                                       (Strictly Firewalled)
                   │                                             │
         ┌─────────┴─────────┐                                   │
         │                   │                                   │
         ▼                   ▼                                   │
  [Diffusion Input]   [Context Builder]                          │
  Low-level floats:   Deterministic feature                      │
  • X_obs             extraction & HKO                           │
  • M_eval            threshold mapping                          │
         │                   │                                   │
         │                   ▼                                   │
         │             Context C                                 │
         │         (Structured Prompt)                           │
         │                   │                                   │
         │                   ▼                                   │
         │             [Frozen SLM]                              │
         │          Qwen2.5 / Llama-3.2                          │
         │                   │                                   │
         │                   ▼                                   │
         │            H ∈ R^(L × d_slm)                          │
         │                   │                                   │
         │                   ▼                                   │
         │             [Token Pool]                              │
         │            (Masked Mean)                              │
         │                   │                                   │
         │                   ▼                                   │
         │          z_raw ∈ R^(d_slm)                            │
         │                   │                                   │
         │                   ▼                                   │
         │         [Projection Layer W_p]                        │
         │                   │                                   │
         │                   ▼                                   │
         │          Semantic Context                             │
         │          z_C ∈ R^(d_diff)                             │
         │                   │                                   │
         └─────────┬─────────┘                                   │
                   │                                             │
                   ▼                                             │
      [Conditional Denoiser ε_θ]                                 │
      Forward diffusion step k, x_k                              │
      Conditioned on:                                            │
      • Low-level: X_obs, M_eval                                 │
      • Diffusion step: e_k                                      │
      • High-level semantic: z_C (via AdaLN)                     │
                   │                                             │
                   ▼                                             │
         Noise Prediction ε_θ(x_k, k, z_C, X_obs, M_eval)        │
                   │                                             │
                   ▼                                             │
         [Score Matching Loss] ◄─────────────────────────────────┘
         Evaluated ONLY on missing entries:
         L_diff = || (1 - M_eval) ⊙ (ε - ε_θ) ||^2
```

### Tensor Dimensional Lifecycle:
1. Input Window: $[B, 24, 13]$
2. Input Mask: $[B, 24, 13]$
3. Serialized Prompt: $B$ text strings (length $L \le 256$ tokens)
4. SLM Token Embeddings: $\mathbf{H} \in [B, L, d_{\text{slm}}]$ (e.g., $d_{\text{slm}} = 896$ for Qwen-2.5-0.5B)
5. Pooled SLM Embedding: $\mathbf{z}_{\text{raw}} \in [B, d_{\text{slm}}]$
6. Projected Conditioning Vector: $\mathbf{z}_C \in [B, d_{\text{diff}}]$ (e.g., $d_{\text{diff}} = 128$)
7. Denoiser Latent State: $\mathbf{h} \in [B, S, K, d_{\text{diff}}]$
8. Final Imputed Output: $\hat{\mathbf{X}} \in [B, 24, 13]$

---

## 5. Context Modalities Definition ($C$)

The environmental context $C$ is decomposed into five distinct semantic modalities:

$$C = \langle C_{\text{temporal}}, \, C_{\text{spatial}}, \, C_{\text{meteorological}}, \, C_{\text{traffic}}, \, C_{\text{missingness}} \rangle$$

### 5.1 Temporal Modality ($C_{\text{temporal}}$)
Encodes cyclical calendar, astronomical, and diurnal phases:
- `start_timestamp`: ISO 8601 string (`YYYY-MM-DD HH:00:00`)
- `year`, `month`, `day`, `start_hour`
- `season`: Hong Kong climatological classification:
  - *Winter*: December, January, February (dominant continental monsoon)
  - *Spring*: March, April, May (high humidity, coastal advective fog)
  - *Summer*: June, July, August (heavy convective precipitation, tropical cyclones)
  - *Autumn*: September, October, November (dry, moderate winds, photochemically active)
- `temporal_split`: Chronological partition tag (`train`, `val`, `test`).

### 5.2 Spatial Modality ($C_{\text{spatial}}$)
Encodes geographic exposure, topography, and micro-environment:
- `station_id`: Integer identifier ($16$ target stations)
- `station_name`: Official station name (e.g., *Sham Shui Po*, *Tap Mun*, *Mong Kok*)
- `station_type`: Station classification:
  - `General`: Urban residential/commercial background (12 stations)
  - `Roadside`: High-density street canyon directly exposed to vehicular exhaust (3 stations: *Causeway Bay*, *Central*, *Mong Kok*)
  - `General (Rural Background)`: Isolated maritime background monitor (*Tap Mun*)
- `district`: Administrative territory of Hong Kong (e.g., *Sham Shui Po*, *Wan Chai*, *Islands*)
- `coordinates`: Latitude ($22.28^\circ\text{N}\text{--}22.48^\circ\text{N}$), Longitude ($113.94^\circ\text{E}\text{--}114.36^\circ\text{E}$)
- `sampling_height_m`: Inlet height above ground level ($3.0\text{ m}$ for roadside canyons, $11.0\text{--}28.0\text{ m}$ for general stations).

### 5.3 Meteorological Modality ($C_{\text{meteorological}}$)
Captures boundary-layer thermodynamic and dynamic properties (channels 5–10, 100% complete):
- `temperature`: Mean, min, max, and diurnal range in $^\circ\text{C}$; categorized via HKO bioclimatic scale.
- `relative_humidity`: Mean in $\%$; categorized from very dry ($<40\%$) to saturated marine fog ($\ge 90\%$).
- `surface_pressure`: Mean atmospheric pressure in $\text{hPa}$.
- `rainfall`: 24-hour total accumulation ($\text{mm}$) and peak hourly rate ($\text{mm/h}$); categorized into HKO rainstorm bands (light, moderate, heavy, torrential).
- `wind_speed`: 24-hour mean in $\text{m/s}$ and $\text{km/h}$; categorized via international Beaufort scale.
- `wind_direction`: 24-hour circular mean in degrees; mapped to 8 compass octants.
- `synoptic_regime`: Inferred air mass origin:
  - *Continental Outflow*: Northerly/Easterly ($0^\circ\text{--}112.5^\circ$, $337.5^\circ\text{--}360^\circ$)
  - *Maritime Inflow*: Southerly/Westerly ($112.5^\circ\text{--}292.5^\circ$)
  - *Stagnant Inversion*: Calm winds ($<1.5\text{ m/s}$) with weak dispersion.

### 5.4 Traffic Modality ($C_{\text{traffic}}$)
Captures corridor-level vehicular emissions and urban mobility state (channels 11–12):
- `traffic_speed`: Spatial IDW projected corridor speed in $\text{km/h}$; categorized into *heavy congestion* ($<40\text{ km/h}$), *moderate flow* ($40\text{--}60\text{ km/h}$), or *smooth free-flow* ($>60\text{ km/h}$).
- `traffic_congestion`: Speed saturation index ($[0, 1]$); categorized into *light* ($<0.10$), *moderate* ($0.10\text{--}0.25$), or *severe* ($>0.25$).

### 5.5 Missingness Modality ($C_{\text{missingness}}$)
Profiles the active sensor observational state derived from the observation mask:
- `missing_cells`: Total missing pollutant cells out of $120$ ($24\text{ hours} \times 5\text{ pollutants}$).
- `missing_pct`: Missingness rate ($0.0\%\text{--}100.0\%$).
- `severity`: Missingness class (*none*, *minor*, *moderate*, *severe*, *extreme blackout*).
- `pattern`: Missingness topology (*complete*, *intermittent sporadic dropouts*, *sustained block outage*, *total station blackout*).
- `affected_pollutants`: Explicit list of channels experiencing data loss and their specific missing hour counts.

---

## 6. Context Construction & Serialization Formats

The system supports two serialization paradigms evaluated in our design:

### Approach A: Serialized Natural Language Atmospheric Narrative (Primary)
Serializes the 5 modalities into a syntactically coherent, grammatically fluid English paragraph designed to activate the pre-trained semantic weights of general-purpose SLMs:

```text
[ENVIRONMENTAL CONTEXT: HONG KONG]
Station: Sham Shui Po (General Air Quality Station, Sham Shui Po District)
Temporal Window: 2019-01-01 00:00:00 (Season: Winter, Start Hour: 00:00)
Meteorology: Mild temperature (mean 18.5°C, min 15.2°C, max 21.0°C); comfortable relative humidity (mean 68%); surface pressure 1018.2 hPa. No measurable rainfall (0.0 mm). Wind: moderate breeze (4.2 m/s) from easterly (95°), consistent with continental outflow bringing regional inland air.
Urban Mobility: Moderate vehicular flow (corridor speed 52.3 km/h), low saturation (saturation index 0.08).
Observational Status: Minor missingness (2/120 cells, 1.7% missing; pattern: intermittent sporadic dropouts). Affected channels: no2 (2h missing).
```

### Approach B: Dense Key-Value Structured Representation (Token-Efficient Alternative)
Eliminates conversational syntax in favor of dense, delimiter-separated key-value pairs to maximize token efficiency for highly constrained context windows:

```text
STATION: Sham Shui Po | TYPE: General | DISTRICT: Sham Shui Po
TIME: 2019-01-01 00:00:00 | SEASON: winter | HOUR: 00
MET: Temp 18.5C (mild) | RH 68% (comfortable) | Rain 0.0mm (no rain) | Wind 4.2m/s easterly (continental outflow)
TRAFFIC: Speed 52.3 km/h (moderate) | Congestion 0.08 (low saturation)
MISSINGNESS: 2/120 (1.7%) | Pattern: intermittent sporadic dropouts
```

### Trade-Off Analysis:
| Dimension | Approach A: Narrative English | Approach B: Key-Value Structured |
| :--- | :--- | :--- |
| **Token Count** | ~140–180 tokens | ~70–95 tokens |
| **SLM Activation** | Optimal; matches natural pre-training corpora | Sub-optimal for causal LLMs trained on natural text |
| **Parsing Overhead** | Negligible ($<0.1\text{ ms}$ string formatting) | Negligible ($<0.05\text{ ms}$ string formatting) |
| **Generalization** | Rich semantic cross-modal associations | Rigid tabular structure resembling CSV |
| **Recommendation** | **Adopt as primary baseline** | Retain for token-budget ablation |

---

## 7. SLM Input Specification

### 7.1 Tokenizer Requirements
- Must use the official pre-trained tokenizer associated with the chosen SLM (e.g., `Qwen/Qwen2.5-0.5B` Byte-Pair Encoding tokenizer with $151,643$ vocabulary).
- **Padding Configuration**: Right-padding with `pad_token = eos_token` for causal language models.
- **Attention Mask**: Strict binary attention mask $\mathbf{m}_{\text{attn}} \in \{0, 1\}^{B \times L}$ passed to ensure padding tokens are excluded from mean-pooling.

### 7.2 Context Length Budget
- Full narrative prompt: $\le 200$ tokens.
- Maximum allocated context length: $L_{\text{max}} = 512$ tokens.
- Truncation safety: Never truncates environmental narratives (as prompt is guaranteed $< 250$ tokens).

### 7.3 Batching Strategy
- Batch dimension matches diffusion training batch size: $B \in [32, 128]$.
- Dynamic batch padding: Sequences are padded only to the longest sequence in the current mini-batch rather than global $L_{\text{max}}$, saving memory.

---

## 8. SLM Output Representation & Pooling Methods

The raw token output of the frozen SLM backbone is:
$$\mathbf{H} = \text{SLM}(\text{Tokens}) \in \mathbb{R}^{B \times L \times d_{\text{slm}}}$$

To collapse sequence length $L$ into a single window-level vector $\mathbf{z}_{\text{raw}} \in \mathbb{R}^{B \times d_{\text{slm}}}$, three pooling operators are formalized:

### Method 1: Masked Mean Pooling (Primary Recommended)
Averages hidden states over valid, non-padding tokens:
$$\mathbf{z}_{\text{raw}} = \frac{\sum_{l=1}^L \mathbf{H}_l \odot \mathbf{m}_{\text{attn}, l}}{\sum_{l=1}^L \mathbf{m}_{\text{attn}, l} + \epsilon}$$
*Advantage*: Captures information uniformly across all descriptive tokens (meteorology, traffic, station type).

### Method 2: Last-Token Pooling
Extracts the hidden state corresponding to the final non-padding token:
$$\mathbf{z}_{\text{raw}} = \mathbf{H}_{B, \, L_{\text{valid}}-1}$$
*Advantage*: Standard for causal/auto-regressive language models whose autoregressive attention allows the final token to attend to the entire prefix.

### Method 3: Multi-Head Attention Pooling
Applies a learnable query vector $\mathbf{q} \in \mathbb{R}^{1 \times d_{\text{slm}}}$ to compute attention weights over the sequence:
$$\boldsymbol{\alpha} = \text{softmax}\left( \frac{\mathbf{q} \mathbf{H}^T}{\sqrt{d_{\text{slm}}}} + (1 - \mathbf{m}_{\text{attn}}) \cdot (-10^9) \right) \in \mathbb{R}^{1 \times L}$$
$$\mathbf{z}_{\text{raw}} = \boldsymbol{\alpha} \mathbf{H} \in \mathbb{R}^{d_{\text{slm}}}$$
*Advantage*: Dynamically weights informative tokens (e.g., "continental outflow", "severe saturation") over boilerplate text.

---

## 9. Mathematical Definition of Context Embedding $\mathbf{z}_C$

The final diffusion conditioning vector $\mathbf{z}_C$ is obtained by projecting the pooled SLM embedding through a dedicated linear projection head and LayerNorm:

$$\mathbf{z}_C = \text{LayerNorm}\left( \mathbf{W}_p \mathbf{z}_{\text{raw}} + \mathbf{b}_p \right) \in \mathbb{R}^{d_{\text{diff}}}$$

where:
- $\mathbf{W}_p \in \mathbb{R}^{d_{\text{diff}} \times d_{\text{slm}}}$ is a trainable linear transformation matrix.
- $\mathbf{b}_p \in \mathbb{R}^{d_{\text{diff}}}$ is a trainable bias vector.
- $\text{LayerNorm}(\cdot)$ stabilizes variance across heterogeneous mini-batches.

### Parameter and Dimensional Budget:
| Component | Dimension ($d_{\text{slm}}$) | Conditioning Dim ($d_{\text{diff}}$) | Projection Parameters |
| :--- | :---: | :---: | :---: |
| **Qwen-2.5-0.5B** | $896$ | $128$ | $896 \times 128 + 128 = 114,816$ (~$0.11\text{ M}$) |
| **Qwen-2.5-1.5B** | $1536$ | $128$ | $1536 \times 128 + 128 = 196,736$ (~$0.20\text{ M}$) |
| **Llama-3.2-1B** | $2048$ | $128$ | $2048 \times 128 + 128 = 262,272$ (~$0.26\text{ M}$) |
| **Phi-3-Mini-4K** | $3072$ | $128$ | $3072 \times 128 + 128 = 393,344$ (~$0.39\text{ M}$) |

---

## 10. Diffusion Conditioning Interface

The conditional denoising network predicts the injected Gaussian noise $\boldsymbol{\epsilon}$:
$$\boldsymbol{\epsilon}_\theta\left( \mathbf{x}_k, \, k, \, \mathbf{z}_C, \, \mathbf{x}_0 \odot \mathbf{M}_{\text{eval}}, \, \mathbf{M}_{\text{eval}} \right)$$

Four conditioning architectures are compared:

### Mechanism 1: Adaptive Layer Normalization (AdaLN / FiLM) — **Primary Proposed**
Modulates normalized intermediate feature representations $\mathbf{h} \in \mathbb{R}^{B \times S \times K \times d_{\text{diff}}}$ using affine scale and shift heads conditioned on the sum of time-step embedding $\mathbf{e}_k$ and SLM context $\mathbf{z}_C$:

$$\mathbf{c} = \mathbf{e}_k + \mathbf{z}_C \in \mathbb{R}^{d_{\text{diff}}}$$
$$\boldsymbol{\gamma} = \mathbf{W}_\gamma \mathbf{c} + \mathbf{b}_\gamma, \quad \boldsymbol{\beta} = \mathbf{W}_\beta \mathbf{c} + \mathbf{b}_\beta$$
$$\text{AdaLN}(\mathbf{h}, \mathbf{c}) = (1 + \boldsymbol{\gamma}) \odot \left( \frac{\mathbf{h} - \mu(\mathbf{h})}{\sigma(\mathbf{h})} \right) + \boldsymbol{\beta}$$

*Rationale*: Matches the dominant paradigm in Diffusion Transformers (DiT, Peebles & Xie, 2023) and continuous time-series diffusion. Initializing $\mathbf{W}_\gamma, \mathbf{W}_\beta$ near zero ensures the network begins training identically to an unconditioned model and smoothly assimilates semantic context.

### Mechanism 2: Cross-Attention
Computes multi-head attention where intermediate spatio-temporal features act as Queries, and the unpooled SLM token sequence $\mathbf{H} \in \mathbb{R}^{B \times L \times d_{\text{slm}}}$ acts as Keys and Values:
$$\mathbf{Q} = \mathbf{h} \mathbf{W}_Q, \quad \mathbf{K} = \mathbf{H} \mathbf{W}_K, \quad \mathbf{V} = \mathbf{H} \mathbf{W}_V$$
$$\text{CrossAttn}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left( \frac{\mathbf{Q} \mathbf{K}^T}{\sqrt{d_k}} \right) \mathbf{V}$$
*Rationale*: Allows temporal steps to attend to specific phrases in the prompt (e.g., midday hours attend to "peak hourly rainfall").

### Mechanism 3: Direct Feature-Wise Concatenation
Projects $\mathbf{z}_C$ and spatially/temporally broadcasts it across $[B, S, K, d_{\text{proj}}]$, concatenating it directly to the input tensor before the first denoising convolution.
*Rationale*: Simplest approach; serves as a strong tabular-style baseline.

### Mechanism 4: Spatio-Temporal Hypernetwork
Uses an auxiliary MLP conditioned on $\mathbf{z}_C$ to dynamically generate the convolutional kernel weights of the denoising network.
*Rationale*: Highly expressive but parameter-heavy and prone to training instability.

---

## 11. Information Leakage Boundaries & Audit Protocol

### 11.1 The Information Boundary Principle
A fundamental flaw in naive multi-modal imputation is **label leakage**: accidentally passing information about the missing values being imputed into the conditioning module.

In our framework, the boundary is mathematically partitioned:
$$\mathbf{X} = \mathbf{X}_{\text{obs}} + \mathbf{X}_{\text{hidden}}$$
where:
$$\mathbf{X}_{\text{obs}} = \mathbf{X} \odot \mathbf{M}_{\text{eval}}, \quad \mathbf{X}_{\text{hidden}} = \mathbf{X} \odot (\mathbf{1} - \mathbf{M}_{\text{eval}})$$

### Strict Audit Rules:
1. **Target Values Exclusion**: $\mathbf{X}_{\text{hidden}}$ must NEVER enter `EnvironmentalContextBuilder` or the SLM.
2. **Exogenous Completeness**: Meteorological variables (temp, RH, rain, pressure, wind) and traffic variables are exogenous and 100% complete; their inclusion in the prompt is physically valid because weather and traffic sensors operate independently of air pollution sensors.
3. **Observation-Only Pollutant Statistics**: By default, `include_observed_aq = False`. If enabled, the prompt builder strictly accesses $\mathbf{X}_{\text{obs}}$ and checks that $\sum \mathbf{M}_{\text{eval}} > 0$. Any attempt to access a cell where $\mathbf{M}_{\text{eval}} = 0$ triggers an immediate `AssertionError`.
4. **Temporal Boundary**: Features for window $[t, t+23]$ are derived strictly within that 24-hour interval. No future timestamps ($t > t+23$) or global dataset statistics are accessed.
5. **Standardization Firewall**: Normalization parameters (mean, std) must be fit strictly on the training partition (`train`, 2019-2020) and never computed across validation or test windows.

---

## 12. Candidate SLMs Evaluation Matrix

| Model | Parameters | Hidden Dim ($d_{\text{slm}}$) | Context Length | Weight Footprint (FP16) | HuggingFace Repo | License | Viability Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| **Qwen-2.5-0.5B** | **$0.49\text{ B}$** | **$896$** | $32\text{k}$ | **~$1.0\text{ GB}$** | `Qwen/Qwen2.5-0.5B` | Apache 2.0 | **Top Candidate**: Extremely lightweight, lowest VRAM footprint, excellent instruction following. |
| **Qwen-2.5-1.5B** | $1.54\text{ B}$ | $1536$ | $32\text{k}$ | ~$3.1\text{ GB}$ | `Qwen/Qwen2.5-1.5B` | Apache 2.0 | **Strong Alternative**: Higher capacity, still fits comfortably within 4 GB GPU cache. |
| **Llama-3.2-1B** | $1.23\text{ B}$ | $2048$ | $128\text{k}$ | ~$2.5\text{ GB}$ | `meta-llama/Llama-3.2-1B` | Llama 3.2 Community | **Strong Candidate**: Highly robust embeddings, widely benchmarked. |
| **Phi-3-Mini-4K** | $3.82\text{ B}$ | $3072$ | $4\text{k}$ | ~$7.6\text{ GB}$ | `microsoft/Phi-3-mini-4k-instruct` | MIT | Viable but heavier; higher VRAM overhead during batch training. |
| **Gemma-2-2B** | $2.61\text{ B}$ | $2304$ | $8\text{k}$ | ~$5.2\text{ GB}$ | `google/gemma-2-2b` | Gemma Terms | High reasoning capacity; slightly higher inference latency. |
| **TinyLlama-1.1B**| $1.10\text{ B}$ | $2048$ | $2\text{k}$ | ~$2.2\text{ GB}$ | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | Apache 2.0 | Mature open baseline; lower reasoning score than Qwen2.5. |

---

## 13. Systematic Ablation Study Design

To empirically prove that the SLM contributes meaningful semantic conditioning rather than acting as a redundant parameter sink, the following systematic ablation matrix is specified:

```
                                    Ablation Configurations
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
    [Model A]                            [Model B]                            [Model C]
Pure Denoising Diffusion             Diffusion + Handcrafted              Diffusion + SLM Context
(No Semantic Context)                Deterministic Vector                 (Proposed Architecture)
Input: X_obs, M                      Input: X_obs, M, v_rule              Input: X_obs, M, z_C
Conditioning: Time-step e_k only     Conditioning: Rule-based vector      Conditioning: Frozen SLM z_C
```

### Detailed Ablation Configurations:
- **Ablation Model A (Pure Numerical Diffusion)**:
  - Input: Masked numerical observations $\mathbf{X}_{\text{obs}} \odot \mathbf{M}$ and binary mask $\mathbf{M}$.
  - Conditioning: Denoising diffusion step embedding $\mathbf{e}_k$.
  - Isolates the raw generative capacity of the spatio-temporal diffusion backbone without contextual guidance.
- **Ablation Model B (Diffusion + Handcrafted Deterministic Context)**:
  - Input: $\mathbf{X}_{\text{obs}}$, $\mathbf{M}$, plus a flat numerical feature vector $\mathbf{v}_{\text{rule}} \in \mathbb{R}^{24}$ constructed from window summary statistics (mean temp, mean RH, rain sum, mean wind speed, sin/cos wind direction, mean traffic speed, missingness percentage).
  - Conditioning: Projected through MLP into $\mathbb{R}^{d_{\text{diff}}}$ and injected via AdaLN.
  - Tests whether continuous language model semantics outperform handcrafted tabular summary statistics.
- **Ablation Model C (Full Proposed SLM-Diffusion Architecture)**:
  - Input: $\mathbf{X}_{\text{obs}}$, $\mathbf{M}$, and $\mathbf{z}_C$ synthesized by frozen SLM from structured environmental narrative.
  - Conditioning: Injected via AdaLN.
- **Ablation Model D (SLM Token-Level Cross-Attention)**:
  - Tests Cross-Attention over full sequence $\mathbf{H} \in \mathbb{R}^{L \times d_{\text{slm}}}$ vs. pooled AdaLN vector $\mathbf{z}_C$.
- **Ablation Model E (Frozen vs. LoRA Fine-Tuned SLM)**:
  - Tests whether domain-specific LoRA fine-tuning ($r=8$) on meteorological texts improves imputation over frozen general-purpose representations.

---

## 14. Open Design Decisions (`[DESIGN DECISION REQUIRED]`)

The following six design choices are formally recorded as open decisions requiring experimental verification in Phase 5:

1. **`[DESIGN DECISION REQUIRED - D01]`**: **Intermediate Bioclimatic Descriptor Thresholds**
   - *Issue*: HKO defines statutory warnings for Cold ($\le 12^\circ\text{C}$) and Very Hot ($\ge 33^\circ\text{C}$), but intermediate boundaries (Cool $12\text{--}18^\circ\text{C}$, Mild $18\text{--}24^\circ\text{C}$, Warm $24\text{--}28^\circ\text{C}$, Hot $28\text{--}33^\circ\text{C}$) are bioclimatic conventions.
   - *Resolution Plan*: Test sensitivity of $\mathbf{z}_C$ when varying bin boundaries by $\pm 2^\circ\text{C}$.
2. **`[DESIGN DECISION REQUIRED - D02]`**: **Observed Pollutant Statistics Inclusion**
   - *Issue*: Should the prompt include observed background concentrations of non-missing pollutants?
   - *Trade-off*: Inclusion provides real-time ambient pollution scale, but risks subtle cross-pollutant co-adaptation during partial masking.
   - *Default Setting*: Set to `include_observed_aq = False` (exogenous weather and traffic only) to ensure zero risk of target leakage.
3. **`[DESIGN DECISION REQUIRED - D03]`**: **Narrative English vs. Dense Key-Value Prompting**
   - *Issue*: Natural language narrative (~150 tokens) vs. dense key-value representation (~80 tokens).
   - *Resolution Plan*: Benchmark both formats under identical SLM backbone in Ablation studies.
4. **`[DESIGN DECISION REQUIRED - D04]`**: **Token Pooling Mechanism**
   - *Issue*: Masked Mean Pooling vs. Last-Token Pooling vs. Learnable Attention Pooling.
   - *Default Setting*: Masked Mean Pooling (preserves distributed multi-sentence context).
5. **`[DESIGN DECISION REQUIRED - D05]`**: **Diffusion Conditioning Injection**
   - *Issue*: AdaLN modulation vs. multi-head Cross-Attention.
   - *Default Setting*: AdaLN (computationally efficient, constant memory scaling with sequence length).
6. **`[DESIGN DECISION REQUIRED - D06]`**: **SLM Model Selection**
   - *Issue*: Final selection between `Qwen/Qwen2.5-0.5B` and `meta-llama/Llama-3.2-1B`.
   - *Default Scaffolding*: `Qwen/Qwen2.5-0.5B` prioritized due to sub-$1\text{ GB}$ footprint and high execution throughput.

---

## 15. Limitations & Boundary Conditions

1. **Inference Latency Overhead**:
   - Running the SLM forward pass on every window introduces computational cost. In production, this is mitigated by pre-encoding and caching static training window embeddings $\mathbf{z}_C$.
2. **Linguistic Representation Bias**:
   - General-purpose SLMs are pre-trained predominantly on global English text. Local Hong Kong micro-climates (e.g., street canyon wind channeling, localized sea breeze fronts) may be partially abstracted by English descriptions.
3. **Loss of High-Frequency Intra-Day Dynamics**:
   - The 24-hour summary narrative compresses temporal trajectory shapes into summary descriptors (e.g., "diurnal range 6°C"). High-frequency hourly variations must be captured by the numerical low-level input $\mathbf{X}_{\text{obs}}$.
4. **Strict Architectural Scope**:
   - This document serves as an **architectural specification only**. No SLM training, fine-tuning, or diffusion reverse loops have been executed in Phase 4A.

---

## 16. Summary & Sign-off

- **Architecture Formalized**: Environmental Context Builder $\to$ Frozen SLM $\to$ Trainable Projection $W_p \to \mathbf{z}_C \to$ AdaLN Conditional Diffusion.
- **Code Modules Implemented**:
  - `src/context/context_features.py`
  - `src/context/context_serializer.py`
  - `src/context/context_builder.py`
  - `src/context/slm_encoder.py`
- **Unit Test Coverage**: 5/5 unit tests verified in `tests/test_context.py`.
- **Status**: Ready for Phase 4B (Dataset Preprocessing & Artificial Masking Design).
