# Architectural & Methodological Decision Records (ADRs)

This directory maintains the formal decision records for the **Air Pollution Missing-Data Imputation (SLM-Conditioned Diffusion)** project.

Every significant scientific, architectural, dataset, or experimental choice must be documented here using the standard ADR format:

```markdown
# Decision: <Semantic Title>

Date: YYYY-MM-DD
Status: PROPOSED / ACCEPTED / SUPERSEDED / REJECTED

## Context
[What was the problem, dilemma, or requirement?]

## Evidence
[What papers, data inspections, or experiments informed this decision?]

## Decision
[What was explicitly decided?]

## Alternatives Considered
[What alternative paths were evaluated?]

## Why Alternatives Were Rejected
[Specific technical or scientific reasons why alternatives failed or were dismissed]

## Consequences
[What are the positive and negative implications of this decision?]

## Revisit Conditions
[Under what conditions should this decision be re-evaluated?]
```

---

## Index of Decision Records

1. **[Dataset Decisions](Dataset%20Decisions.md)**:
   - D01: Strict adoption of CTDI Table I 13-channel formulation.
   - D02: Rejection of `traffic_volume` and adoption of `traffic_congestion`.
   - D03: Investigation of `visibility` vs `rainfall` for CTDI source alignment (superseded by D07).
   - D04: Absolute prohibition against synthetic data injection & Phase 1.1 resolution.
   - D05: Exclusion of Southern (#84) and North (#85) monitoring stations.
   - D06: Distinguishing source-system reconstruction from exact raw dataset reproduction.
   - D07: Formal adoption of ERA5 rainfall substitution for Channel 9.
2. **[Architecture Decisions](Architecture%20Decisions.md)**:
   - A01: Adoption of SLM conditioning for generative diffusion.
   - A02: Discrete cosine diffusion variance schedule.
   - A03: Multi-modal spatial graph attention coupled with temporal transformer blocks.
3. **[Preprocessing Decisions](Preprocessing%20Decisions.md)**:
   - P01: Inverse Distance Weighting (IDW, $p=2$) for spatial feature mapping.
   - P02: Air quality stations as immutable spatial coordinate anchors.
   - P03: Zero Data Leakage: chronological splitting and train-only scaler fitting.
   - P04: 24-hour sliding window geometry.
4. **[Experimental Decisions](Experimental%20Decisions.md)**:
   - E01: Multi-scale missingness benchmark (MCAR, block, station outage at 10%, 30%, 50%, 70%).
   - E02: Evaluation with both deterministic (MAE, RMSE, MAPE) and probabilistic (CRPS, PICP) metrics.
   - E03: Selection of primary published baseline: Yu et al. (CTDI, IEEE TBD 2025).
