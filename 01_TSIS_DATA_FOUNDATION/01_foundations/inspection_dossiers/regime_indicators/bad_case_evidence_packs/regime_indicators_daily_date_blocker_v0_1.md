# Regime Indicators Daily Date Blocker v0.1

This casepack documents the blocking daily defect in:

```text
regime_indicators_v0_1
```

## Evidence Assets

| Asset | Reading |
| --- | --- |
| `../evidence_assets/regime_indicators_daily_date_quality_v0_1.csv` | Per-file daily date/datetime statistics. |
| `../evidence_assets/regime_indicators_daily_blocking_date_manifest_v0_1.csv` | Compact blocking manifest for all daily files. |
| `../evidence_assets/sample_payloads/spy_day_broken_sample_v0_1.csv` | Representative ETF daily rows. |
| `../evidence_assets/sample_payloads/i_ndx_day_broken_sample_v0_1.csv` | Representative index daily rows. |

## Blocking Finding

| Metric | Value |
| --- | ---: |
| Daily files | 34 |
| Daily rows | 153,397 |
| Files with only `1970-01-01` as `date` | 34 |
| Maximum per-file `date` unique count | 1 |
| Daily read errors | 0 |

Observed date range:

```text
date_min = 1970-01-01
date_max = 1970-01-01
```

Observed datetime range:

```text
1970-01-01 00:17:43.166400 to 1970-01-01 00:29:24.568800
```

## Technical Interpretation

The daily files are structurally readable, but the calendar key is invalid.

This blocks:

- `symbol + date` joins;
- daily regime features;
- master daily table inputs;
- backtest context;
- ML/RL/live inputs.

## Required Repair Gate

Before daily bars can be consumed, a repair or regeneration must prove:

- valid `symbol + date` keys;
- realistic date ranges;
- `symbol + date` uniqueness;
- consistency with metadata and source provenance;
- no silent metadata-based overwrite without a repair contract.
