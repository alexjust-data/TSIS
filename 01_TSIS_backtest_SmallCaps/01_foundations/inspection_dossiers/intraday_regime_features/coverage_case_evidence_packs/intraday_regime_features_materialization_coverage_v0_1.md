# Intraday Regime Features Materialization Coverage v0.1

This casepack documents physical coverage for:

```text
intraday_regime_features_v0_1
```

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/intraday_regime_features_inventory_v0_1.csv` | File-level parquet inventory. |
| `../evidence_assets/intraday_regime_features_materialization_summary_v0_1.csv` | Source materialization summary. |
| `../evidence_assets/intraday_regime_features_key_quality_summary_v0_1.csv` | Aggregate key quality. |
| `../evidence_assets/intraday_regime_features_read_errors_v0_1.csv` | Read-error evidence. |

## Physical Footprint

| Metric | Value |
| --- | ---: |
| Ticker directories | 8 |
| Parquet files | 8 |
| Ticker-day rows | 243 |
| Date minimum | 2006-03-01 |
| Date maximum | 2025-02-28 |
| Read errors | 0 |
| Duplicate `ticker + date` rows | 0 |

Materialized tickers:

- `BNGO`
- `BXRX`
- `CEI`
- `COSM`
- `EFSH`
- `LIVE`
- `PD`
- `SAVA`

## Interpretation

The footprint is coherent for a semantic pilot. It is intentionally not
full-universe coverage.
