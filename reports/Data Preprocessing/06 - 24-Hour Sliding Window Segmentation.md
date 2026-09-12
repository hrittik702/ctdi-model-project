# 06 - 24-Hour Sliding Window Segmentation

> **Previous**: [[05 - Feature Engineering & Normalization]] | **Next**: [[07 - Environmental Context Builder for SLM]] | **Index**: [[00 - Overview & Pipeline Architecture]]

---

## 1. Overview

Rather than training models on the monolithic 3-year timeline all at once, the CTDI benchmark segments continuous time-series data into **24-hour periods** ($T_{\text{window}} = 24$).

This document explains the physical rationale behind the 24-hour window, the sliding window segmentation geometry, and the batch structuring for PyTorch data loaders.

---

## 2. Atmospheric & Urban Rationale for 24 Hours

In urban air quality science, 24 hours corresponds to one complete **diurnal atmospheric cycle**:

```
Hour:   00  02  04  06  08  10  12  14  16  18  20  22  24
        ┌──────────────────────────────────────────────┐
NO2:    │       ▲ (Morning rush)         ▲ (Eve rush)  │ (Vehicle emissions)
O3:     │                    ▲ (Solar noon)            │ (Photochemical smog)
Temp:   │  ▼ (Dawn min)          ▲ (Midday max)        │ (Diurnal heating)
PBL:    │  ▼ (Shallow nocturnal) ▲ (Deep convective)   │ (Boundary layer height)
        └──────────────────────────────────────────────┘
```

1. **Morning Rush Hour (07:00 - 09:00)**: Sharp peak in vehicular combustion emissions ($\text{NO}_2, \text{PM}_{2.5}, \text{CO}$).
2. **Midday Photochemistry (12:00 - 15:00)**: Maximum solar insolation triggers atmospheric photochemical reactions, converting $\text{NO}_x$ and volatile organics into secondary Ozone ($\text{O}_3$).
3. **Evening Rush Hour (17:30 - 20:00)**: Secondary commuter traffic peak.
4. **Nighttime Boundary Layer Collapse (00:00 - 06:00)**: Ground cooling creates a nocturnal temperature inversion, trapping pollutants close to ground level.

A window of 24 hours captures the full periodic rhythm of emission, accumulation, chemical reaction, and nighttime dispersion.

---

## 3. Sliding Window Formulation

```
Sample 0:  [t=0  ----------------- t=23]
Sample 1:     [t=1  ----------------- t=24]    <-- Stride = 1 hour (Training)
Sample 2:        [t=2  ----------------- t=25]
...
Sample K:  [t=K  ----------------- t=K+23]
```

### 3.1 Training Split Windowing (Overlapping)
- **Window Length ($L$)**: $24$ hours
- **Stride ($S_{\text{train}}$)**: $1$ hour
- **Total Training Hours**: $\approx 18,412$ hours (2019-01-01 to 2021-02-05)
- **Number of Training Windows**:
  $$N_{\text{train}} = 18,412 - 24 + 1 = \mathbf{18,389}\text{ samples}$$
- **Advantage**: Dense overlapping sampling maximizes sample efficiency and teaches the model to handle missingness at any arbitrary hour of the day.

### 3.2 Testing Split Windowing (Contiguous / Non-Overlapping)
- **Window Length ($L$)**: $24$ hours
- **Stride ($S_{\text{test}}$)**: $24$ hours (stride equal to window length)
- **Total Testing Hours**: $\approx 3,946$ hours (2021-07-19 to 2021-12-31)
- **Number of Testing Windows**:
  $$N_{\text{test}} = \lfloor 3,946 / 24 \rfloor = \mathbf{164}\text{ full 24-hour test days}$$
- **Advantage**: Non-overlapping contiguous days prevent double-counting test hours and ensure mathematically unbiased performance reporting.

---

## 4. Tensor Dimensions & PyTorch Data Structure

### 4.1 Single Sample Window
Each sample window contains the complete spatial network across the 24 hours:

$$\mathbf{X}_{\text{sample}} \in \mathbb{R}^{16 \times 24 \times 13}$$

- Axis 0 ($S = 16$): Spatial nodes (16 monitoring stations).
- Axis 1 ($T = 24$): Hourly timestamps ($0..23$).
- Axis 2 ($C = 13$): Multi-modal channels ($5\text{ pollutants} + 6\text{ met} + 2\text{ traffic}$).
- **Total values per window**: $16 \times 24 \times 13 = \mathbf{4,992}\text{ elements}$.

### 4.2 Single Mask Window
$$\mathbf{M}_{\text{sample}} \in \{0, 1\}^{16 \times 24 \times 13}$$
Indicates which values are observed ($1$) versus missing ($0$) within that 24-hour slice.

### 4.3 PyTorch Batched DataLoader Tensor
When queried by a PyTorch `DataLoader` with batch size $B$ (e.g. $B = 32$):

$$\mathbf{X}_{\text{batch}} \in \mathbb{R}^{B \times 16 \times 24 \times 13}$$
$$\mathbf{M}_{\text{batch}} \in \{0, 1\}^{B \times 16 \times 24 \times 13}$$

Memory per batch (float32):
$$\text{Batch Memory} = 32 \times 16 \times 24 \times 13 \times 4\text{ bytes} \approx 638.9\text{ KB}$$
Extremely lightweight and fast for GPU loading.
