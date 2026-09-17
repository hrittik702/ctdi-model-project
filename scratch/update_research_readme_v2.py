with open("research/README.md") as f:
    text = f.read()

# Replace rows in table
text = text.replace(
    "[CTDI Dataset Description.md](reports/CTDI%20Dataset%20Description.md)<br>[Cleaning, Translation & Validation Rules.md](preprocessing/Cleaning,%20Translation%20&%20Validation%20Rules.md)",
    "[Station Inventory & Spatial Network.md](dataset/Station%20Inventory%20&%20Spatial%20Network.md)<br>[Cleaning, Translation & Validation Rules.md](preprocessing/Cleaning,%20Translation%20&%20Validation%20Rules.md)"
)

text = text.replace(
    "[Alignment - PY.md](reports/Alignment%20-%20PY.md)<br>[Spatial Alignment Implementation.md](preprocessing/Spatial%20Alignment%20Implementation.md)",
    "[Phase 2 - Spatio-Temporal Alignment Report.md](reports/Phase%202%20-%20Spatio-Temporal%20Alignment%20Report.md)<br>[Spatial Alignment Implementation.md](preprocessing/Spatial%20Alignment%20Implementation.md)"
)

text = text.replace(
    "[Data Preprocessing/](reports/Data%20Preprocessing/) (10 modular chapters)<br>[preprocessing/README.md](preprocessing/README.md) | [Phase 1.md](reports/Phase%201.md)<br>[Phase 2.md](reports/Phase%202.md)",
    "[preprocessing/README.md](preprocessing/README.md)<br>[Phase 1 - Source-Specific Cleaning Report.md](reports/Phase%201%20-%20Source-Specific%20Cleaning%20Report.md) | [2026-09-17_phase_1_1.md](checkpoints/2026-09-17_phase_1_1.md)<br>[2026-09-17_phase_2.md](checkpoints/2026-09-17_phase_2.md)"
)

# Tree replacement
old_reports_tree = """└── reports/                                # Empirical investigation reports, execution logs & handbooks
    ├── README.md                           # Index of reports, execution logs, and archival analyses
    ├── Alignment - PY.md                   # Execution log of alignment pipeline and safety halt
    ├── CTDI Dataset Description.md         # Comprehensive background dataset documentation (2026-09-12)
    ├── CTDI Missingness Pattern Analysis.md # Detailed empirical analysis replicating Figures 6–9
    ├── Data Processing - Hong Kong.md      # 454-line comprehensive data engineering handbook
    ├── Phase 1.md                          # Phase 1 raw data verification execution log
    ├── Phase 1 - Source-Specific Cleaning Report.md # Source-specific cleaning & Phase 1.1 traffic extraction
    ├── Phase 2.md                          # Early Phase 2 spatial alignment and tensor plan (historical)
    ├── Phase 2 - Spatio-Temporal Alignment Report.md # Phase 2 completion report: 420k row Cartesian grid
    ├── Research Information Curation Report.md # Comprehensive knowledge base curation & audit report
    ├── Raw Data Availability & Verification.md # Initial raw download availability and physical checks
    ├── Visibility Data Recovery & Provenance Report.md # HKO AWS visibility irrecoverability audit
    ├── ctdi channel reconstruction.md      # 13-channel specification and code divergence analysis
    ├── ctdi source fidelity report.md      # Source data fidelity compared against published citations
    ├── ctdi table I reconstruction.md      # Exact reproduction and analytical breakdown of CTDI Table I
    ├── ctdi traffic variable verification.md # Candidate traffic variable evidence matrix & 607-link proof
    └── Data Preprocessing/                 # 10-chapter modular data engineering guides (Chapters 00–09)"""

new_reports_tree = """└── reports/                                # Empirical investigation reports & engineering handbooks
    ├── README.md                           # Index of reports and empirical analyses
    ├── CTDI Missingness Pattern Analysis.md # Detailed empirical analysis replicating Figures 6–9
    ├── Data Processing - Hong Kong.md      # 454-line comprehensive data engineering handbook
    ├── Phase 1 - Source-Specific Cleaning Report.md # Source-specific cleaning & Phase 1.1 traffic extraction
    ├── Phase 2 - Spatio-Temporal Alignment Report.md # Phase 2 completion report: 420k row Cartesian grid
    ├── Raw Data Availability & Verification.md # Initial raw download availability and physical checks
    ├── Research Information Curation Report.md # Comprehensive knowledge base curation & audit report
    ├── Visibility Data Recovery & Provenance Report.md # HKO AWS visibility irrecoverability audit
    ├── ctdi channel reconstruction.md      # 13-channel specification and code divergence analysis
    ├── ctdi source fidelity report.md      # Source data fidelity compared against published citations
    ├── ctdi table I reconstruction.md      # Exact reproduction and analytical breakdown of CTDI Table I
    └── ctdi traffic variable verification.md # Candidate traffic variable evidence matrix & 607-link proof"""

text = text.replace(old_reports_tree, new_reports_tree)

with open("research/README.md", "w") as f:
    f.write(text)

print("Updated research/README.md successfully.")
