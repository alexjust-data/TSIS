# Regime Indicators Inventory And Coverage Evidence v0.1

This casepack documents physical coverage and inventory for:

```text
regime_indicators_v0_1
```

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/regime_indicators_inventory_v0_1.csv` | File-level parquet inventory. |
| `../evidence_assets/regime_indicators_file_counts_v0_1.csv` | Counts by group and file kind. |
| `../evidence_assets/regime_indicators_metadata_summary_v0_1.csv` | Metadata presence and top-level shape. |
| `../evidence_assets/regime_indicators_read_errors_v0_1.csv` | Read error table. |

## Physical Footprint

| Group | File kind | Files |
| --- | --- | ---: |
| `etfs` | `day` | 31 |
| `etfs` | `minute` | 31 |
| `indices` | `day` | 3 |
| `indices` | `minute` | 2 |

Additional root files:

- `download_metadata.json`;
- `ticker_ranges.json`.

## Readability

| Metric | Value |
| --- | ---: |
| Parquet files | 67 |
| JSON files | 2 |
| Parquet read errors | 0 |

## Interpretation

Physical readability is not the same as data-quality approval.

The family has a clear inventory and readable files. Daily files are still
blocked by invalid date semantics. Minute files remain scoped/review because
they need deeper coverage, OHLC, session and symbol-mapping validation.
