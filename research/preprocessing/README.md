# Data Preprocessing Pipeline

This directory contains the engineering specifications, transformation rules, and quality assurance protocols for the data preprocessing pipeline.

---

## Modular Pipeline Documents

1. **[Raw Ingestion](ingestion.md)**: Procedures for scraping and downloading EPD, HKO, and TD datasets.
2. **[Cleaning & Validation](cleaning_and_validation.md)**: Sanitizing bilingual Chinese headers, converting 1..24 hour format to ISO datetime, and standardizing missing flags.
3. **[Temporal Alignment](temporal_alignment.md)**: Generating the complete Cartesian grid ($16 \text{ stations} \times 26,304 \text{ hours} = 420,864 \text{ rows}$) and chronological sorting.
4. **[Spatial Alignment](spatial_alignment.md)**: Inverse Distance Weighting ($p=2$) mapping of road traffic and meteorology to the 16 station coordinates.
5. **[Feature Engineering](feature_engineering.md)**: Cyclical sine/cosine temporal encodings (hour of day, day of week, month of year).
6. **[Normalization](normalization.md)**: Zero-data-leakage scaling protocols (fitting scalers strictly on observed Train split values).
7. **[Data Quality Assurance](data_quality_assurance.md)**: Verification playbook, automated assertions, and continuous integrity checks.
