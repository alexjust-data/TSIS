# Microstructure Features Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
microstructure_features_table_v0_1
```

`microstructure_features_table` is the scoped event-window microstructure
surface for CAPA 1.

It computes compact features from raw quotes and raw trades for explicit event
windows. It does not duplicate raw quote books or trade tapes.

## 2. Logical Unit

Unit:

```text
instrument event-window microstructure row
```

Grain:

```text
event_window_id + ticker + window_start_utc + window_end_utc
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table
```

Artifacts:

```text
microstructure_features_table_v0_1/
_microstructure_features_table_summary_v0_1.csv
_microstructure_features_table_manifest_v0_1.json
```

Layout:

```text
partitioned parquet dataset by year/month
```

Builder:

```text
scripts/materialize_microstructure_features_table.py
```

Seed input:

```text
configs/data_foundation_outputs/microstructure_features_seed_windows_v0_1.csv
```

## 4. Sources

Current materialization sources v0.1:

- `D:/quotes`
- `E:/TSIS/data/trades_ticks_prod_2005_2026`
- `instrument_master_v0_1`
- `dataset_certification_matrix_v0_1`
- `configs/data_foundation_outputs/microstructure_features_seed_windows_v0_1.csv`

Important:

```text
D:/quotes is a provisional legacy/recovery source for this v0.1 seed
materialization. The future official root is E:/TSIS/data/quotes after raw
storage parity is completed and audited.
```

The row-level output must preserve:

- `quotes_root_used`;
- `quotes_root_state`;
- `future_official_quotes_root`;
- `quotes_staging_root`;
- `trades_root_used`;
- `source_quotes_file`;
- `source_trades_file`;
- `source_quotes_file_sha256`;
- `source_trades_file_sha256`.

## 5. Required Columns

Identity:

- `microstructure_feature_id`
- `event_window_id`
- `ticker`
- `instrument_id`
- `instrument_identity_temporal_match`
- `session_date`
- `year`
- `month`
- `window_start_utc`
- `window_end_utc`
- `window_label`

Source lineage:

- `source_scope_note`
- `quotes_root_used`
- `quotes_root_state`
- `future_official_quotes_root`
- `quotes_staging_root`
- `trades_root_used`
- `trades_root_state`
- `source_quotes_file`
- `source_trades_file`
- `source_quotes_file_present`
- `source_trades_file_present`
- `source_quotes_file_sha256`
- `source_trades_file_sha256`

Instrument context:

- `is_common_stock`
- `is_lt1b_operational`
- `lt1b_classification_1b`
- `instrument_master_build_run_id`
- `instrument_master_schema_version`

Quote features:

- `quotes_rows`
- `quotes_window_rows`
- `quotes_first_ts_utc`
- `quotes_last_ts_utc`
- `quotes_ask_zero_pct`
- `quotes_bid_zero_pct`
- `quotes_ask_size_zero_pct`
- `quotes_bid_size_zero_pct`
- `quotes_two_sided_rows`
- `quotes_crossed_rows`
- `quotes_locked_rows`
- `quotes_crossed_ratio_pct_all_rows`
- `quotes_crossed_ratio_pct_two_sided`
- `quotes_locked_ratio_pct_two_sided`
- `quotes_spread_bps_median`
- `quotes_spread_bps_p90`
- `quotes_top_depth_mean`

Trade features:

- `trades_rows`
- `trades_window_rows`
- `trades_first_ts_utc`
- `trades_last_ts_utc`
- `trades_invalid_price_rows`
- `trades_invalid_size_rows`
- `trades_odd_lot_ratio_pct`
- `trades_duplicate_exact_ratio_pct`
- `trades_off_regular_session_ratio_pct`
- `trades_total_volume`
- `trades_dollar_volume`
- `trades_price_min`
- `trades_price_max`
- `trades_price_last`
- `trades_size_median`
- `trades_size_p90`

Family gates:

- `quotes_family_data_quality_verdict`
- `quotes_family_event_consumption_gate`
- `quotes_family_production_use_gate`
- `trades_family_data_quality_verdict`
- `trades_family_event_consumption_gate`
- `trades_family_production_use_gate`
- `dataset_certification_matrix_build_run_id`

Consumption flags:

- `microstructure_quality_state`
- `event_research_microstructure_candidate`
- `execution_sim_candidate`
- `backtest_core_microstructure_candidate`
- `full_universe_claim`
- `materialization_scope`

Versioning:

- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

## 6. Current v0.1 Materialization

```text
build_run_id: microstructure_features_table_v0_1_20260625T155732Z
materialization_scope: seed_event_window_smoke
full_universe_claim: false
rows: 1
tickers: 1
windows: 1
seed window: ZYXI 2025-12-01 full UTC day
quotes rows: 13288
trades rows: 18182
hard_fail_count: 0
execution_sim_candidate_rows: 0
backtest_core_microstructure_candidate_rows: 0
```

This is a smoke/event-window seed, not a production feature store and not a
full-universe microstructure table.

## 7. Structural Rules

Hard structural failures:

- zero output rows;
- duplicate `event_window_id + ticker + window_start_utc + window_end_utc`;
- missing source hash for a present source file;
- `full_universe_claim = true`;
- `execution_sim_candidate = true` in v0.1;
- `backtest_core_microstructure_candidate = true` in v0.1;
- manifest output tree hash does not match the physical parquet tree;
- contract, policy, registry or validator paths referenced in manifest are
  missing.

Review states, not structural failures:

- one side of quotes/trades missing for a requested window;
- non-zero crossed quote ratio;
- non-zero exact duplicate trade ratio;
- high odd-lot ratio;
- provisional `D:/quotes` lineage.

## 8. Interpretation

Permitted:

- scoped event-window microstructure diagnostics;
- research notebooks that preserve scope flags;
- source lineage validation while the quotes E/D parity audit is open;
- feature-design smoke tests.

Prohibited:

- core backtesting;
- execution simulation;
- full-universe ML/RL training;
- treating `D:/quotes` as final official root;
- treating this v0.1 seed as evidence that all quotes/trades windows have been
  materialized.
