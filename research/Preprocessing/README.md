# Data Preprocessing Pipeline

This directory contains the engineering specifications, transformation rules, and quality assurance protocols for the data preprocessing pipeline.

---

## Modular Pipeline Documents

1. **[Raw Ingestion](Raw%20Data%20Ingestion%20Protocol.md)**: Procedures for scraping and downloading EPD, HKO, and TD datasets.
2. **[Cleaning & Validation](Cleaning,%20Translation%20&%20Validation%20Rules.md)**: Sanitizing bilingual Chinese headers, converting 1..24 hour format to ISO datetime, and standardizing missing flags.
3. **[Temporal Alignment](Temporal%20Alignment%20&%20Grid%20Assembly.md)**: Generating the complete Cartesian grid ($16 \text{ stations} \times 26,304 \text{ hours} = 420,864 \text{ rows}$) and chronological sorting.
4. **[Spatial Alignment](Spatial%20Alignment%20Implementation.md)**: Inverse Distance Weighting ($p=2$) mapping of road traffic and meteorology to the 16 station coordinates.
5. **[Feature Engineering](Feature%20Engineering%20&%20Encodings.md)**: Cyclical sine/cosine temporal encodings (hour of day, day of week, month of year).
6. **[Normalization](Normalization%20&%20Zero-Leakage%20Protocol.md)**: Zero-data-leakage scaling protocols (fitting scalers strictly on observed Train split values).
7. **[Data Quality Assurance](Data%20Quality%20Assurance%20Playbook.md)**: Verification playbook, automated assertions, and continuous integrity checks.
