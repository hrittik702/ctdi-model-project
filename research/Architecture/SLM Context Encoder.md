# Environmental Context Builder & SLM Encoder

---

## 1. Deterministic Context Synthesis

The context builder (`src/context/builder.py`) converts numerical aggregates of each 24-hour window into structured atmospheric English descriptors:

```python
class EnvironmentalContextBuilder:
    def build_prompt(
        self,
        station_name: str,
        station_type: str,
        date_str: str,
        met_summary: Dict[str, float],
        traffic_summary: Dict[str, float]
    ) -> str:
        prompt = (
            f"[ATMOSPHERIC CONTEXT: HONG KONG]\n"
            f"Date: {date_str} | Target Station: {station_name} ({station_type})\n"
            f"Meteorology: Temp {met_summary['temp']:.1f}°C, RH {met_summary['rh']:.0f}%, "
            f"Pressure {met_summary['pres']:.1f} hPa, Wind {met_summary['ws']:.1f} km/h from {met_summary['wd']}°.\n"
            f"Urban State: Corridor Traffic Speed {traffic_summary['speed']:.1f} km/h, "
            f"Saturation Level: {traffic_summary['congestion']}.\n"
            f"Synoptic Evaluation: {self._deduce_synoptic_regime(met_summary)}"
        )
        return prompt
```

---

## 2. SLM Embedding Extraction

The prompt is tokenized and passed through a lightweight Small Language Model:
$$\mathbf{H} = \text{SLM}(\text{Tokens}) \in \mathbb{R}^{L \times d_{\text{slm}}}$$

The contextual representation is obtained via mean-pooling across non-padding tokens:
$$\mathbf{z}_{\text{raw}} = \frac{1}{L} \sum_{l=1}^L \mathbf{H}_l$$

A trainable projection layer aligns the embedding dimension to the diffusion model:
$$\mathbf{z}_C = \mathbf{W}_p \mathbf{z}_{\text{raw}} + \mathbf{b}_p \in \mathbb{R}^{d_{\text{diff}}}$$
where $W_p \in \mathbb{R}^{d_{\text{diff}} \times d_{\text{slm}}}$ is updated during diffusion training while the SLM weights remain frozen.
