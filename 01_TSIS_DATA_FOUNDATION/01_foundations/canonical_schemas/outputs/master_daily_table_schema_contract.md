# Master Daily Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
master_daily_table_v0_1
```

`master_daily_table` is the compact daily market-state table for CAPA 1.

It combines:

- daily expected coverage denominator;
- raw daily OHLCV;
- split-normalized daily OHLC;
- adjusted daily OHLC;
- corporate-action day flags;
- family-level quality gates;
- basic daily context metrics.

It does not replace raw daily files or daily inspection dossiers.

## 2. Logical Unit

Unit:

```text
instrument daily price-view row
```

Grain:

```text
instrument_id + ticker + session_date + price_view
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/master_daily_table
```

Artifacts:

```text
master_daily_table_v0_1/
_master_daily_table_summary_v0_1.csv
_master_daily_table_manifest_v0_1.json
```

Layout:

```text
partitioned parquet dataset by year/price_view
```

Builder:

```text
scripts/materialize_master_daily_table.py
```

## 4. Sources

Governed sources v0.1:

- `expected_data_calendar_v0_1`
- `corporate_actions_table_v0_1`
- `dataset_certification_matrix_v0_1`
- `E:/TSIS/data/ohlcv_daily`
- `E:/TSIS/data/ohlcv_daily_adjusted`

## 5. Required Columns

Identity:

- `master_daily_id`
- `instrument_id`
- `ticker`
- `session_date`
- `year`
- `month`
- `price_view`

Expectation and source:

- `quality_gate_family`
- `source_dataset`
- `source_root`
- `expected_session`
- `expected_reason`
- `expected_dataset_id`
- `expected_source_root`
- `data_present`
- `missing_expected_data`
- `source_daily_present`
- `source_adjusted_present`

Selected price-view values:

- `open`
- `high`
- `low`
- `close`
- `volume`
- `vwap`
- `source_raw_vwap`
- `transaction_count`
- `source_t_epoch_ms`

Daily context:

- `prior_close`
- `gap_pct`
- `daily_return_pct`
- `intraday_return_pct`
- `daily_range_pct`
- `dollar_volume`
- `volume_20d_avg`
- `rvol_20d`

Adjustment lineage:

- `future_split_factor`
- `future_dividend_sum`
- `future_dividend_factor`
- `future_adjustment_factor`
- `adjusted_materialized_price_view`
- `adjusted_proxy_open`
- `adjusted_proxy_high`
- `adjusted_proxy_low`
- `adjusted_proxy_close`
- `source_daily_file`
- `source_splits_file`
- `source_dividends_file`

Corporate-action context:

- `corporate_action_count`
- `split_action_count`
- `dividend_action_count`
- `ticker_change_action_count`
- `has_split_action`
- `has_dividend_action`
- `has_ticker_change_action`
- `has_any_corporate_action`

Quality and consumption:

- `row_level_price_integrity_state`
- `selected_price_hard_invalid`
- `negative_volume`
- `backtest_core_row_candidate`
- `family_data_quality_verdict`
- `family_foundations_completion_status`
- `family_visual_inspection_status`
- `family_production_use_gate`
- `family_event_consumption_gate`
- `gate_quality_policy_version`

Lineage:

- `expected_data_calendar_build_run_id`
- `dataset_certification_matrix_build_run_id`
- `corporate_actions_build_run_id`
- `expectation_policy_version`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

## 6. Price Views

Allowed `price_view` values v0.1:

- `daily_raw`
- `split_normalized`
- `adjusted`

Rules:

- `daily_raw` uses selected OHLCV from `E:/TSIS/data/ohlcv_daily`.
- `split_normalized` uses OHLC from `ohlcv_daily_adjusted` split-normalized columns.
- `adjusted` uses OHLC from `ohlcv_daily_adjusted` adjusted columns.
- `vwap` is populated only for `daily_raw`; derived views preserve `source_raw_vwap` but do not invent adjusted VWAP.

## 7. Structural Rules

Hard structural failures:

- zero rows;
- duplicate `ticker + session_date + price_view`;
- missing price view;
- missing one of the three price views;
- output row count not equal to `daily expected rows * 3`;
- missing manifest or summary;
- missing contract/schema/policy/registry/validator paths.

Quality flags, not structural hard failures:

- `missing_expected_data`;
- `selected_price_hard_invalid`;
- `negative_volume`;
- no prior close for first observed row;
- null RVOL when fewer than 20 prior observations exist.

## 8. Interpretation

Permitted:

- daily event context;
- daily backtest candidate filtering;
- adjusted daily research;
- gap, return, range, dollar-volume and RVOL features;
- corporate-action-aware event interpretation;
- joining downstream event windows to daily context.

Not permitted:

- execution simulation;
- quote/trade microstructure truth;
- treating `adjusted` as raw observed market price;
- treating family-level gates as row-level daily audit labels;
- using absent fundamentals/news/halts/regime fields by implication.

## 9. v0.1 Limitations

v0.1 intentionally excludes:

- fundamentals as-of fields;
- live/news context;
- short data;
- halt overlays;
- regime context;
- row-level daily audit labels beyond price-integrity flags.

Those require later sidecars or versioned joins.

