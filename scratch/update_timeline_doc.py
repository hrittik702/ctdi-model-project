with open("research/research_timeline.md") as f:
    text = f.read()

replacements = [
    ("research/dataset/ctdi_paper_dataset_specification.md", "research/dataset/CTDIDataset Specifications.md"),
    ("research/dataset/ctdi_consistency_matrix.md", "research/dataset/CTDI Dataset Consistency Matrix.md"),
    ("research/dataset/raw_data_integrity_manifest.md", "research/dataset/Raw Data Integrity Manifest.md"),
    ("research/reports/ctdi_table_i_reconstruction.md", "research/reports/ctdi table I reconstruction.md"),
    ("research/reports/ctdi_traffic_variable_verification.md", "research/reports/ctdi traffic variable verification.md"),
    ("research/reports/ctdi_channel_reconstruction.md", "research/reports/ctdi channel reconstruction.md"),
    ("research/reports/ctdi_source_fidelity_report.md", "research/reports/ctdi source fidelity report.md"),
    ("research/reports/visibility_data_recovery_report.md", "research/reports/Visibility Data Recovery & Provenance Report.md"),
    ("research/reports/raw_data_availability_and_verification.md", "research/reports/Raw Data Availability & Verification.md"),
    ("research/reports/source_specific_cleaning_report.md", "research/reports/Phase 1 - Source-Specific Cleaning Report.md"),
    ("research/reports/ctdi_missingness_pattern_analysis.md", "research/reports/CTDI Missingness Pattern Analysis.md"),
    ("research/reports/temporal_spatial_alignment_report.md", "research/reports/Phase 2 - Spatio-Temporal Alignment Report.md"),
    ("ctdi_table_i_reconstruction.md", "ctdi table I reconstruction.md"),
    ("ctdi_traffic_variable_verification.md", "ctdi traffic variable verification.md"),
    ("ctdi_channel_reconstruction.md", "ctdi channel reconstruction.md"),
    ("ctdi_source_fidelity_report.md", "ctdi source fidelity report.md"),
    ("visibility_data_recovery_report.md", "Visibility Data Recovery & Provenance Report.md"),
    ("ctdi_missingness_pattern_analysis.md", "CTDI Missingness Pattern Analysis.md"),
    ("ctdi_consistency_matrix.md", "CTDI Dataset Consistency Matrix.md"),
    ("raw_data_integrity_manifest.md", "Raw Data Integrity Manifest.md"),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"Replaced: {old[:40]}...")
    else:
        print(f"NOT FOUND: {old[:40]}...")

with open("research/research_timeline.md", "w") as f:
    f.write(text)

print("Updated research_timeline.md successfully.")
