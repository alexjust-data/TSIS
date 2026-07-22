# Regime Context Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
regime_context_table_v0_1
```

`regime_context_table` is a governed Data Foundation context/state component for
market regime proxies. It converts validated minute bars from
`regime_indicators_v0_1` into session-level context rows that can be joined to
events under an explicit as-of cutoff.

It is not a trading signal, not a ticker-level causal proof, not an execution
dataset, not a direct RL training dataset and not a replacement for the future
`market_state_table` / `event_state_table`.

## 2. Logical Unit

Unit:

```text
one regime proxy x trading_date daily aggregate from minute.parquet
```

Grain:

```text
regime_symbol + trading_date + source_granularity
```

Logical key:

```text
regime_context_id
```

`regime_symbol` is the source proxy symbol/identifier from
`E:/TSIS/data/regime_indicators`, for example `SPY`, `QQQ`, `IWM`, sector ETFs
or index proxies such as `I_COMP`.

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/regime_context_table
```

Dataset:

```text
regime_context_table_v0_1/
  source_proxy_family=<etf|index>/
    observation_year=<YYYY>/
```

Artifacts:

```text
_regime_context_table_manifest_v0_1.json
_regime_context_table_summary_v0_1.csv
```

Builder:

```text
scripts/materialize_regime_context_table.py
```

## 4. Sources

Governed v0.1 sources:

```text
E:/TSIS/data/regime_indicators/**/minute.parquet
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

Source contract:

```text
01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md
```

Important exclusion:

```text
E:/TSIS/data/regime_indicators/**/day.parquet
```

is blocked from this output because the audited daily files show invalid 1970
date semantics. v0.1 must not repair or consume those daily files silently.

Important non-source:

```text
E:/TSIS/data/intraday_regime_features
```

is not included in v0.1. It is a pilot ticker-day feature layer, not the global
regime source for this table.

## 5. Required Columns

Identity and lineage:

- `regime_context_id`
- `regime_symbol`
- `source_symbol_dir`
- `regime_proxy_role`
- `source_dataset_id`
- `source_granularity`
- `context_granularity`
- `source_proxy_family`
- `source_root`
- `source_file`
- `source_file_relative_path`
- `observation_year`

Time and as-of fields:

- `trading_date`
- `session_open_utc`
- `as_of_utc`
- `as_of_date`
- `as_of_semantics`
- `first_bar_timestamp`
- `last_bar_timestamp`
- `timestamp_timezone_state`

Aggregate price/volume fields:

- `open_price`
- `high_price`
- `low_price`
- `close_price`
- `previous_close_price`
- `intraday_return`
- `close_to_previous_close_return`
- `high_to_open_return`
- `low_to_open_return`
- `intraday_range_pct`
- `volume`
- `vwap`

Coverage and source-quality fields:

- `bars_observed`
- `distinct_timestamp_count`
- `duplicate_timestamp_rows`
- `bar_coverage_state`
- `null_ohlc_bar_count`
- `non_positive_price_bar_count`
- `source_bad_ohlc_bar_count`
- `negative_volume_bar_count`
- `missing_volume_bar_count`
- `missing_vwap_bar_count`
- `daily_source_files_blocked`
- `built_from_blocked_day_parquet`
- `built_from_minute_parquet`
- `intraday_regime_features_source_included`

Calendar lineage:

- `market_calendar_covered`
- `session_minutes`
- `is_early_close`
- `market_calendar`
- `market_timezone`
- `market_calendar_source`
- `market_calendar_build_run_id`
- `market_calendar_schema_version`

Consumer gates:

- `regime_quality_state`
- `valid_for_event_context_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_state_component_candidate`
- `valid_for_backtest_core_direct`
- `valid_for_rl_training_direct`
- `requires_asof_filter`
- `contains_future_information_without_event_filter`
- `same_session_intraday_causal_claim_allowed`
- `execution_truth`

Build lineage:

- `full_universe_claim`
- `materialization_scope`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

## 6. Quality States

Allowed `regime_quality_state` values:

- `good_minute_aggregated_regime_context`
- `review_no_market_calendar_session`
- `review_source_bar_integrity`
- `review_sparse_minute_coverage`

Primary event/state context candidates require:

```text
regime_quality_state = good_minute_aggregated_regime_context
market_calendar_covered = true
built_from_minute_parquet = true
built_from_blocked_day_parquet = false
intraday_regime_features_source_included = false
```

ML feature candidates additionally require finite, interpretable price-return
fields after the downstream as-of join.

## 7. Current Materialization

```text
build_run_id: regime_context_table_v0_1_20260627T084649Z
rows: 154692
regime_symbols: 33
parquet_files: 25
source_minute_rows_aggregated: 64348953
source_minute_files: 33
blocked_day_files: 34
output_tree_sha256: 6cb774257e72ec1fa0e0c4fd514141b684f21e262de0a82206362bdbfbcba48c
```

Quality distribution:

```text
good_minute_aggregated_regime_context: 143840
review_no_market_calendar_session: 9214
review_source_bar_integrity: 107
review_sparse_minute_coverage: 1531
```

Consumer gates:

```text
valid_for_event_context_candidate_rows: 143840
valid_for_ml_feature_candidate_rows: 143834
valid_for_state_component_candidate_rows: 143840
valid_for_backtest_core_direct_rows: 0
valid_for_rl_training_direct_rows: 0
```

## 8. Leakage Rule

This table is a session-close daily aggregate from minute bars.

Consumers must never use a row without applying:

```text
as_of_utc <= event decision timestamp
```

and must respect:

```text
requires_asof_filter = true
contains_future_information_without_event_filter = true
same_session_intraday_causal_claim_allowed = false
```

Therefore a same-session 10:00 event cannot use that session's completed
regime row as causal pre-event information. It may use prior-session regime
rows, or a future intraday-specific regime builder with its own cutoff contract.
