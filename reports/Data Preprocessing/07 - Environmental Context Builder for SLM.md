# 07 - Environmental Context Builder for SLM

> **Previous**: [[06 - 24-Hour Sliding Window Segmentation]] | **Next**: [[08 - Canonical Data Storage & File Layout]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Research Motivation: Why Add an SLM?

Standard imputation architectures (like CTDI, SAITS, or CSDI) rely solely on numerical matrices. However, human atmospheric scientists and meteorologists rely on **high-level synoptic reasoning**:
- *"A strong dry winter monsoon is transporting continental industrial aerosols into the Pearl River Delta."*
- *"Heavy convective summer rainfall is washing out airborne particulates across the territory."*
- *"A stagnant high-pressure ridge with light easterly winds is causing street-canyon accumulation in Mong Kok and Causeway Bay."*

Our novel research direction—**Context-Aware Generative Imputation Using SLM-Conditioned Diffusion**—introduces a Small Language Model (SLM) that translates raw numerical weather and urban conditions into rich atmospheric text prompts. These prompts are encoded into continuous conditioning vectors $\mathbf{c}_{\text{text}}$ that guide the reverse diffusion denoising process.

---

## 2. Context Builder Architecture

The context builder module (`src/context/builder.py`) processes each 24-hour sample window and synthesizes an English narrative prompt:

```
┌─────────────────────────────────────────────────────────────┐
│ 24-HOUR SAMPLE WINDOW                                       │
│ • Meteorology: Mean Temp, Humidity, Pressure, Wind, Rain    │
│ • Date: Season, Day-of-week, Holiday flag                  │
│ • Spatial Network: Roadside vs General station distributions│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ CONTEXT BUILDER ENGINE (src/context/builder.py)             │
│ • Rule-based meteorological classifier                      │
│ • Atmospheric regime determination (Typhoon, Monsoon, etc.) │
│ • Topographic & roadside emission description               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ SYNTHESIZED TEXT CONTEXT PROMPT                             │
│ "Season: Winter. Synoptic: Moderate continental north-east  │
│  monsoon. Temp: 14.2°C, RH: 55%, Pressure: 1024 hPa. Dry    │
│  conditions with light rainfall. Regional inflow expected." │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ SMALL LANGUAGE MODEL EMBEDDING (SLM)                        │
│ • Ingestion through lightweight frozen/LoRA SLM             │
│ • Generates text-conditioning embedding vector c_text       │
│ • Injected into Diffusion model via Cross-Attention / AdaLN │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Atmospheric Narrative Templates

### 3.1 Scenario A: Winter Continental Haze Episode (High Pollution)
```text
"Date: 2019-12-18, Season: Winter (Weekday).
Atmospheric Regime: Dry continental north-easterly monsoon.
Synoptic Conditions: High barometric pressure (1026.2 hPa), low ambient temperature (13.5°C), relative humidity 52%.
Wind Dynamics: Gentle 2.8 m/s breeze from 020° (North-Northeast), facilitating long-range transport of continental air masses into Hong Kong.
Precipitation: 0.0 mm (absence of wet deposition).
Spatial Impact: Elevated regional background PM2.5 and PM10 across inland stations (Yuen Long, Tuen Mun, Tai Po). High roadside NO2 along urban street canyons (Causeway Bay, Mong Kok)."
```

### 3.2 Scenario B: Summer Oceanic Monsoon & Rain Scavenging (Low Pollution)
```text
"Date: 2020-07-22, Season: Summer (Weekend).
Atmospheric Regime: Maritime south-westerly airstream accompanied by convective precipitation.
Synoptic Conditions: Low barometric pressure (1004.1 hPa), high ambient temperature (31.8°C), relative humidity 88%.
Wind Dynamics: Fresh 6.4 m/s breeze from 210° (South-Southwest), delivering clean maritime air from the South China Sea.
Precipitation: 28.5 mm total rainfall, driving significant atmospheric wet scavenging.
Spatial Impact: Particulate concentrations (PM2.5, PM10) strongly suppressed across all 16 stations. Moderate ozone photochemistry limited by dense cloud cover."
```

### 3.3 Scenario C: Autumn Photochemical Smog (High Ozone)
```text
"Date: 2021-10-14, Season: Autumn (Weekday).
Atmospheric Regime: Intense solar insolation under a subsiding continental air mass.
Synoptic Conditions: Stable pressure (1016.4 hPa), warm temperature (28.6°C), moderate humidity 64%.
Wind Dynamics: Light and variable winds (1.5 m/s, prevailing East-Southeast), indicating poor territory-wide dispersion.
Precipitation: 0.0 mm.
Spatial Impact: Strong secondary photochemical reaction producing high afternoon Ozone peaks (O3 > 200 μg/m³) at western and rural stations (Tung Chung, Tap Mun). Traffic-dense roadside stations exhibit strong NO titration."
```

---

## 4. Integration with the Generative Diffusion Model

In standard DDPM or Score-based diffusion models, the reverse step at noise level $t$ estimates the score or added noise $\boldsymbol{\epsilon}_\theta$:

$$\boldsymbol{\epsilon}_\theta\big(\mathbf{X}_t, t, \mathbf{M}_{\text{sim}}, \mathbf{c}_{\text{text}}\big)$$

Where:
- $\mathbf{X}_t \in \mathbb{R}^{16 \times 24 \times 13}$ is the noisy tensor at diffusion step $t$.
- $\mathbf{M}_{\text{sim}} \in \{0, 1\}^{16 \times 24 \times 13}$ is the missingness mask.
- $\mathbf{c}_{\text{text}} \in \mathbb{R}^{D}$ is the SLM context embedding vector.

Cross-attention layers inside the spatio-temporal UNet attend to $\mathbf{c}_{\text{text}}$, allowing the physical narrative (e.g. knowing it is a rainy day or a high-pressure winter inversion) to directly constrain the generative probability distribution of the imputed values.
