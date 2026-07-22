# Regime Context Table Validators `v0_1`

## 1. Scope

This validator contract governs:

```text
regime_context_table_v0_1
```

## 2. Required Inputs

Required governed sources:

- `E:/TSIS/data/regime_indicators/**/minute.parquet`
- `E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet`
- `E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json`

Blocked sources that must remain excluded:

- `E:/TSIS/data/regime_indicators/**/day.parquet`
- `E:/TSIS/data/intraday_regime_features`

## 3. Hard Validation Checks

The build must fail if:

- `regime_context_id` is duplicated;
- any output row is `bad_*`;
- output row count is zero;
- any row is built from blocked `day.parquet`;
- any row includes `intraday_regime_features` as a source;
- the manifest `output_tree` does not match the parquet tree.

Review rows are not hard failures. They preserve missing-calendar, sparse
coverage or source-bar-integrity evidence for consumers and auditors.

## 4. Required Quality Checks

The validator must emit:

- row count;
- regime symbol count;
- first and last `trading_date`;
- source proxy family counts;
- regime proxy role counts;
- `regime_quality_state` distribution;
- source minute rows aggregated;
- source minute file count;
- blocked day file count;
- no-calendar row count;
- sparse coverage row count;
- source bar-integrity row count;
- source bad OHLC bar count;
- duplicate timestamp row count;
- consumer-gate row counts.

## 5. Required Consumer Gates

Every row must satisfy:

```text
full_universe_claim = false
execution_truth = false
valid_for_backtest_core_direct = false
valid_for_rl_training_direct = false
requires_asof_filter = true
contains_future_information_without_event_filter = true
same_session_intraday_causal_claim_allowed = false
built_from_minute_parquet = true
built_from_blocked_day_parquet = false
intraday_regime_features_source_included = false
```

Rows may have `valid_for_event_context_candidate = true` only when:

```text
regime_quality_state = good_minute_aggregated_regime_context
market_calendar_covered = true
bars_observed >= 60
source_bad_ohlc_bar_count = 0
```

## 6. Current Expected v0.1 Counts

```text
rows: 154692
regime_symbols: 33
parquet_files: 25
source_minute_files: 33
blocked_day_files: 34
source_minute_rows_aggregated: 64348953
calendar_covered_rows: 145478
no_calendar_rows: 9214
bad_rows: 0
valid_for_event_context_candidate_rows: 143840
valid_for_ml_feature_candidate_rows: 143834
valid_for_state_component_candidate_rows: 143840
valid_for_backtest_core_direct_rows: 0
valid_for_rl_training_direct_rows: 0
```

Quality:

```text
good_minute_aggregated_regime_context: 143840
review_no_market_calendar_session: 9214
review_source_bar_integrity: 107
review_sparse_minute_coverage: 1531
```

Source proxy families:

```text
etf: 154603
index: 89
```

## 7. Test Evidence

The pytest contract is:

```text
tests/data_foundation_outputs/test_regime_context_table_contract.py
```

Evidence must be written under:

```text
C:/TSIS_Data/tests/test_runs/<date>/data_foundation_outputs_regime_context_table_v0_1/
```
