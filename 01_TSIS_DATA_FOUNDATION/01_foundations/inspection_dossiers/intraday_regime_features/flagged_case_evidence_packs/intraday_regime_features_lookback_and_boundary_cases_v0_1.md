# Intraday Regime Features Lookback And Boundary Cases v0.1

This file documents scoped review cases for:

```text
intraday_regime_features_v0_1
```

These are not data defects inside the pilot. They are boundaries a downstream
consumer must understand.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/intraday_regime_features_null_summary_v0_1.csv` | Aggregate null profile. |
| `../evidence_assets/intraday_regime_features_semantic_case_manifest_v0_1.csv` | Boundary semantic cases. |
| `../evidence_assets/intraday_regime_features_numeric_extreme_summary_v0_1.csv` | Numeric range profile. |

## Expected Lookback Nulls

Nulls concentrate in history-dependent cross-session features:

| Column | Nulls | Null pct |
| --- | ---: | ---: |
| `overnight_gap_zscore_20` | 48 | 19.753086 |
| `multi_session_return_5d_to_open` | 40 | 16.460905 |
| `multi_session_return_3d_to_open` | 24 | 9.876543 |
| `distance_to_n_day_high_5` | 16 | 6.584362 |
| `distance_to_n_day_low_5` | 16 | 6.584362 |

Interpretation:

- these nulls are expected at the start of a ticker's available history;
- the schema contract explicitly allows lookback-driven nulls;
- they must not be interpreted as random missing data without checking lookback.

## Boundary Semantic Cases

| Case | Role | Max absolute gap difference | Reading |
| --- | --- | ---: | --- |
| `PD 2006-03` | forward split | 49.81% | Coherent boundary: below the strong `>50%` gap threshold but still split-sensitive. |
| `SAVA 2023-12` | forward split | 28.49% | Coherent boundary: local difference, not a contradiction of split semantics. |

## Consumer Rule

Consumers must preserve:

```text
feature layer state = scoped semantic pilot
```

They must not convert this pilot into a full production feature layer without a
new coverage, leakage and drift audit.
