with open("research/research_status.md") as f:
    text = f.read()

replacements = [
    ("`research/dataset/ctdi_paper_dataset_specification.md`", "[`CTDIDataset Specifications.md`](dataset/CTDIDataset%20Specifications.md)"),
    ("`research/reports/visibility_data_recovery_report.md`", "[`Visibility Data Recovery & Provenance Report.md`](reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)"),
    ("(`ctdi_consistency_matrix.md`)", "([`CTDI Dataset Consistency Matrix.md`](dataset/CTDI%20Dataset%20Consistency%20Matrix.md))"),
    ("(`ctdi_source_fidelity_report.md`)", "([`ctdi source fidelity report.md`](reports/ctdi%20source%20fidelity%20report.md))"),
    ("`research/dataset/raw_data_integrity_manifest.md`", "[`Raw Data Integrity Manifest.md`](dataset/Raw%20Data%20Integrity%20Manifest.md)"),
    ("`research/reports/temporal_spatial_alignment_report.md`", "[`Phase 2 - Spatio-Temporal Alignment Report.md`](reports/Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md)"),
    ("(`research/reports/ctdi_missingness_pattern_analysis.md`)", "([`CTDI Missingness Pattern Analysis.md`](reports/CTDI%20Missingness%20Pattern%20Analysis.md))"),
    ("`research/preprocessing/normalization.md`", "[`Normalization & Zero-Leakage Protocol.md`](preprocessing/Normalization%20&%20Zero-Leakage%20Protocol.md)"),
    ("`research/architecture/context_encoder.md`", "[`SLM Context Encoder.md`](architecture/SLM%20Context%20Encoder.md)"),
    ("`research/architecture/diffusion_model.md`", "[`Conditional Diffusion Model.md`](architecture/Conditional%20Diffusion%20Model.md)"),
    ("`research/architecture/loss_functions.md`", "[`Loss Functions & Objectives.md`](architecture/Loss%20Functions%20&%20Objectives.md)"),
    ("`research/experiments/evaluation_metrics.md`", "[`Evaluation Metrics.md`](experiments/Evaluation%20Metrics.md)"),
    ("`research/experiments/baselines.md`", "[`Baseline Imputation Models.md`](experiments/Baseline%20Imputation%20Models.md)"),
    ("`research/experiments/ablation_plan.md`", "[`Ablation Study Plan.md`](experiments/Ablation%20Study%20Plan.md)"),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"Replaced: {old[:40]}...")
    else:
        print(f"NOT FOUND: {old[:40]}...")

with open("research/research_status.md", "w") as f:
    f.write(text)

print("Updated research_status.md successfully.")
