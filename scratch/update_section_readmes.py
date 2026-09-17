import os, urllib.parse

updates = {
    "research/decisions/README.md": [
        ("dataset_decisions.md", "Dataset%20Decisions.md"),
        ("architecture_decisions.md", "Architecture%20Decisions.md"),
        ("preprocessing_decisions.md", "Preprocessing%20Decisions.md"),
        ("experimental_decisions.md", "Experimental%20Decisions.md"),
    ],
    "research/findings/README.md": [
        ("confirmed_findings.md", "Confirmed%20Research%20Findings.md"),
        ("negative_findings.md", "Negative%20Findings%20&%20Dead%20Ends.md"),
        ("unresolved_questions.md", "Living%20Unresolved%20Questions.md"),
        ("research_limitations.md", "Research%20Boundaries%20&%20Limitations.md"),
    ],
    "research/literature/README.md": [
        ("ctdi_paper_analysis.md", "CTDI%20Paper%20Exhaustive%20Analysis.md"),
        ("slm_conditioned_diffusion_research.md", "SLM-Conditioned%20Diffusion%20Research.md"),
        ("related_methods.md", "Related%20Imputation%20Methods.md"),
    ],
    "research/experiments/README.md": [
        ("experimental_protocol.md", "Experimental%20Training%20Protocol.md"),
        ("baselines.md", "Baseline%20Imputation%20Models.md"),
        ("missingness_scenarios.md", "Missingness%20Scenarios%20&%20Benchmark%20Masks.md"),
        ("evaluation_metrics.md", "Evaluation%20Metrics.md"),
        ("ablation_plan.md", "Ablation%20Study%20Plan.md"),
        ("cross_dataset_evaluation.md", "Cross-Dataset%20Evaluation.md"),
    ],
    "research/architecture/README.md": [
        ("system_architecture.md", "System%20Architecture.md"),
        ("context_encoder.md", "SLM%20Context%20Encoder.md"),
        ("diffusion_model.md", "Conditional%20Diffusion%20Model.md"),
        ("temporal_model.md", "Temporal%20Denoising%20Model.md"),
        ("spatial_model.md", "Spatial%20Model%20Prior.md"),
        ("conditioning_mechanism.md", "Conditioning%20Mechanism.md"),
        ("loss_functions.md", "Loss%20Functions%20&%20Objectives.md"),
    ],
    "research/preprocessing/README.md": [
        ("ingestion.md", "Raw%20Data%20Ingestion%20Protocol.md"),
        ("cleaning_and_validation.md", "Cleaning,%20Translation%20&%20Validation%20Rules.md"),
        ("temporal_alignment.md", "Temporal%20Alignment%20&%20Grid%20Assembly.md"),
        ("spatial_alignment.md", "Spatial%20Alignment%20Implementation.md"),
        ("feature_engineering.md", "Feature%20Engineering%20&%20Encodings.md"),
        ("normalization.md", "Normalization%20&%20Zero-Leakage%20Protocol.md"),
        ("data_quality_assurance.md", "Data%20Quality%20Assurance%20Playbook.md"),
    ]
}

for path, replacements in updates.items():
    with open(path, "r") as fh:
        text = fh.read()
    for old_val, new_val in replacements:
        text = text.replace(old_val, new_val)
    with open(path, "w") as fh:
        fh.write(text)
    print(f"Updated {path}")
