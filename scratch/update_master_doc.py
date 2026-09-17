import re

with open("research/MASTER_RESEARCH_DOCUMENT.md") as f:
    text = f.read()

replacements = [
    ("file:///home/mocha/Desktop/ctdi-model-project/research/dataset/provenance.md", "dataset/Dataset%20Provenance%20&%20Specifications.md"),
    ("research/dataset/provenance.md", "dataset/Dataset%20Provenance%20&%20Specifications.md"),
    ("`ctdi_paper_dataset_specification.md`, `visibility_data_recovery_report.md`, and `raw_data_integrity_manifest.md`",
     "[`CTDIDataset Specifications.md`](dataset/CTDIDataset%20Specifications.md), [`Visibility Data Recovery & Provenance Report.md`](reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md), and [`Raw Data Integrity Manifest.md`](dataset/Raw%20Data%20Integrity%20Manifest.md)"),
    ("`ctdi_table_i_reconstruction.md`, `ctdi_traffic_variable_verification.md`, and `ctdi_channel_reconstruction.md`",
     "[`ctdi table I reconstruction.md`](reports/ctdi%20table%20I%20reconstruction.md), [`ctdi traffic variable verification.md`](reports/ctdi%20traffic%20variable%20verification.md), and [`ctdi channel reconstruction.md`](reports/ctdi%20channel%20reconstruction.md)"),
    ("`research/reports/raw_data_availability_and_verification.md`",
     "[`Raw Data Availability & Verification.md`](reports/Raw%20Data%20Availability%20&%20Verification.md)"),
    ("`research/dataset/ctdi_paper_dataset_specification.md`",
     "[`CTDIDataset Specifications.md`](dataset/CTDIDataset%20Specifications.md)"),
    ("`research/reports/visibility_data_recovery_report.md`",
     "[`Visibility Data Recovery & Provenance Report.md`](reports/Visibility%20Data%20Recovery%20&%20Provenance%20Report.md)"),
    ("`research/dataset/raw_data_integrity_manifest.md`",
     "[`Raw Data Integrity Manifest.md`](dataset/Raw%20Data%20Integrity%20Manifest.md)"),
    ("`research/reports/ctdi_missingness_pattern_analysis.md`",
     "[`CTDI Missingness Pattern Analysis.md`](reports/CTDI%20Missingness%20Pattern%20Analysis.md)"),
    ("`research/reports/source_specific_cleaning_report.md`",
     "[`Phase 1 - Source-Specific Cleaning Report.md`](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md)"),
    ("(`ctdi_table_i_reconstruction.md`)",
     "([`ctdi table I reconstruction.md`](reports/ctdi%20table%20I%20reconstruction.md))"),
    ("(`ctdi_traffic_variable_verification.md`)",
     "([`ctdi traffic variable verification.md`](reports/ctdi%20traffic%20variable%20verification.md))"),
    ("ctdi_missingness_pattern_analysis.md",
     "CTDI Missingness Pattern Analysis.md"),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"Replaced: {old[:40]}...")
    else:
        print(f"NOT FOUND: {old[:40]}...")

with open("research/MASTER_RESEARCH_DOCUMENT.md", "w") as f:
    f.write(text)

print("Updated MASTER_RESEARCH_DOCUMENT.md successfully.")
