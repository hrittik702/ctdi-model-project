# Temporal Coverage & Calendar Accounting

---

## 1. Mathematical Breakdown of Study Period

- **Target Range**: `2019-01-01 00:00:00` to `2021-12-31 23:00:00` HKT (Asia/Hong_Kong, UTC+8).
- **Total Duration**: Exactly 3 full calendar years ($1,096$ continuous days).

### Annual Breakdown
| Calendar Year | Days | Leap Year? | Total Hours | Timestamp Range |
| :---: | :---: | :---: | :---: | :--- |
| **2019** | 365 | No | 8,760 hours | `2019-01-01 00:00` to `2019-12-31 23:00` |
| **2020** | 366 | **Yes (Feb 29)** | 8,784 hours | `2020-01-01 00:00` to `2020-12-31 23:00` |
| **2021** | 365 | No | 8,760 hours | `2021-01-01 00:00` to `2021-12-31 23:00` |
| **Total** | **1,096** | — | **26,304 hours** | `2019-01-01 00:00` to `2021-12-31 23:00` |

---

## 2. Chronological Dataset Partitioning (Zero Data Leakage)

To prevent temporal look-ahead bias and maintain standard machine learning integrity, the 26,304 hours are partitioned chronologically:

```text
[2019-01-01 00:00]                                                                   [2021-12-31 23:00]
├───────────────────────────────────────────────────────┼───────────────────┼───────────────────┤
│                   TRAIN (70%)                         │     VAL (15%)     │     TEST (15%)    │
│            18,412 continuous hours                    │    3,946 hours    │    3,946 hours    │
│            2019-01-01 00:00 to 2021-02-05 03:00       │ 2021-02-05 04:00  │ 2021-07-18 14:00  │
│                                                       │ to 2021-07-18 13:00│ to 2021-12-31 23:00│
└───────────────────────────────────────────────────────┴───────────────────┴───────────────────┘
```

### Partitioning Statistics
- **Training Set (70%)**: $18,412$ hours ($294,592$ station-hour rows across 16 stations).
- **Validation Set (15%)**: $3,946$ hours ($63,136$ station-hour rows across 16 stations).
- **Test Set (15%)**: $3,946$ hours ($63,136$ station-hour rows across 16 stations).
- **Sum**: $18,412 + 3,946 + 3,946 = 26,304$ hours ($420,864$ station-hour rows).
