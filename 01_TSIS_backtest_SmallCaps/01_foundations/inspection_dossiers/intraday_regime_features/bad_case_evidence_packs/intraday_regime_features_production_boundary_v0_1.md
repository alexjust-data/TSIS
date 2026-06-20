# Intraday Regime Features Production Boundary v0.1

This file documents what is blocked for:

```text
intraday_regime_features_v0_1
```

The current pilot is not blocked by an observed internal data defect. It is
blocked from production promotion by scope.

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/intraday_regime_features_inventory_v0_1.csv` | Only 8 pilot parquet files exist. |
| `../evidence_assets/intraday_regime_features_materialization_summary_v0_1.csv` | Only 8 pilot tickers and 243 ticker-day rows are materialized. |
| `../evidence_assets/intraday_regime_features_audit_summary_v0_1.json` | Confirms the pilot footprint and scoped state. |

## Blocked Conclusions

The current evidence must not be used to claim:

- full-universe `<1B>` feature coverage;
- production feature-store readiness;
- model/alpha validity;
- leakage-cleared ML readiness;
- live or RL readiness;
- replacement of upstream `ohlcv_1m_split_normalized` validation.

## Promotion Debt

Before any production promotion, a new version must add:

- explicit target universe;
- reproducible full materialization;
- coverage expected/present/healthy/usable tables;
- duplicate/key/null/outlier profiles over the full target universe;
- leakage gate;
- feature drift audit;
- downstream model-consumer contract.
