# Cross-Dataset & External Generalization Plan

---

## 1. Motivation for External Validation

To demonstrate that the **SLM-Conditioned Diffusion** framework generalizes beyond the microclimate and topography of Hong Kong, the model will be evaluated on at least one external benchmark dataset without structural modification.

---

## 2. Target External Benchmarks

1. **Beijing Multi-Station Air Quality Dataset (KDD Cup / UCI)**:
   - 12 urban air quality stations in Beijing.
   - Criteria pollutants: $\text{PM}_{2.5}, \text{PM}_{10}, \text{NO}_2, \text{SO}_2, \text{O}_3, \text{CO}$.
   - Surface meteorology: Temperature, Pressure, Dew Point, Precipitation, Wind Speed/Direction.
   - Temporal duration: 2013-03-01 to 2017-02-28 (35,064 hours).
2. **Evaluation Protocol**:
   - The same deterministic `EnvironmentalContextBuilder` and SLM prompt encoder will be applied to Beijing atmospheric observations.
   - Benchmarked against published CSDI and PriSTI results on Beijing air quality.
