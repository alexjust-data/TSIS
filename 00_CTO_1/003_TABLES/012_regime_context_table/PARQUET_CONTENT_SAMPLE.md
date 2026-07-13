# regime_context_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Session-level regime proxy context from regime_indicators minute bars; day.parquet blocked. |
| operational_use | Market/regime context after explicit as-of join. |
| exclusions | Not same-session intraday causal state, not execution truth, not direct ML/RL table. |

## Source

| item | value |
| --- | --- |
| dataset_id | `regime_context_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\regime_context_table\regime_context_table_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\regime_context_table\regime_context_table_v0_1\source_proxy_family=etf\observation_year=2004\data_0.parquet` |
| declared_rows_in_status_matrix | 154,692 |
| declared_file_or_partition_count_in_status_matrix | 25 |
| physical_parquet_files_seen | 25 |
| physical_rows_from_parquet_metadata | 154692 |
| physical_row_groups_seen | 25 |
| sample_physical_columns | 68 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `regime_context_id` | `string` |
| 1 | `regime_symbol` | `string` |
| 2 | `source_symbol_dir` | `string` |
| 3 | `regime_proxy_role` | `string` |
| 4 | `source_dataset_id` | `string` |
| 5 | `source_granularity` | `string` |
| 6 | `context_granularity` | `string` |
| 7 | `trading_date` | `date32[day]` |
| 8 | `session_open_utc` | `timestamp[us, tz=UTC]` |
| 9 | `as_of_utc` | `timestamp[us, tz=UTC]` |
| 10 | `as_of_date` | `date32[day]` |
| 11 | `as_of_semantics` | `string` |
| 12 | `first_bar_timestamp` | `timestamp[ns]` |
| 13 | `last_bar_timestamp` | `timestamp[ns]` |
| 14 | `bars_observed` | `int64` |
| 15 | `distinct_timestamp_count` | `int64` |
| 16 | `duplicate_timestamp_rows` | `int64` |
| 17 | `bar_coverage_state` | `string` |
| 18 | `open_price` | `double` |
| 19 | `high_price` | `double` |
| 20 | `low_price` | `double` |
| 21 | `close_price` | `double` |
| 22 | `previous_close_price` | `double` |
| 23 | `intraday_return` | `double` |
| 24 | `close_to_previous_close_return` | `double` |
| 25 | `high_to_open_return` | `double` |
| 26 | `low_to_open_return` | `double` |
| 27 | `intraday_range_pct` | `double` |
| 28 | `volume` | `double` |
| 29 | `vwap` | `double` |
| 30 | `null_ohlc_bar_count` | `int64` |
| 31 | `non_positive_price_bar_count` | `int64` |
| 32 | `source_bad_ohlc_bar_count` | `int64` |
| 33 | `negative_volume_bar_count` | `int64` |
| 34 | `missing_volume_bar_count` | `int64` |
| 35 | `missing_vwap_bar_count` | `int64` |
| 36 | `market_calendar_covered` | `bool` |
| 37 | `session_minutes` | `double` |
| 38 | `is_early_close` | `bool` |
| 39 | `market_calendar` | `string` |
| 40 | `market_timezone` | `string` |
| 41 | `timestamp_timezone_state` | `string` |
| 42 | `daily_source_files_blocked` | `bool` |
| 43 | `built_from_blocked_day_parquet` | `bool` |
| 44 | `built_from_minute_parquet` | `bool` |
| 45 | `intraday_regime_features_source_included` | `bool` |
| 46 | `regime_quality_state` | `string` |
| 47 | `valid_for_event_context_candidate` | `bool` |
| 48 | `valid_for_ml_feature_candidate` | `bool` |
| 49 | `valid_for_state_component_candidate` | `bool` |
| 50 | `valid_for_backtest_core_direct` | `bool` |
| 51 | `valid_for_rl_training_direct` | `bool` |
| 52 | `requires_asof_filter` | `bool` |
| 53 | `contains_future_information_without_event_filter` | `bool` |
| 54 | `same_session_intraday_causal_claim_allowed` | `bool` |
| 55 | `execution_truth` | `bool` |
| 56 | `source_root` | `string` |
| 57 | `source_file` | `string` |
| 58 | `source_file_relative_path` | `string` |
| 59 | `market_calendar_source` | `string` |
| 60 | `market_calendar_build_run_id` | `string` |
| 61 | `market_calendar_schema_version` | `string` |
| 62 | `full_universe_claim` | `bool` |
| 63 | `materialization_scope` | `string` |
| 64 | `quality_policy_version` | `string` |
| 65 | `schema_version` | `string` |
| 66 | `build_run_id` | `string` |
| 67 | `created_at_utc` | `string` |
| 68 | `source_proxy_family` | `string` |
| 69 | `observation_year` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `regime_context_id` | e508e98cb2d25eb93eac1c9c52f2ede2d906f7394540330a760691cc50ae056b | c4042586410d9eda6f9e492016eaea0e9677f0c5f06e2c6be2d50a409b2e76cd | 14469293142c890cbd2d26af249d52fae31b3926e66d8b7b5ce442186638f106 | 2b317b836bc243143f8df9632c54831d0e9c1f364a7ceb3acc9bc84854a9d4fc | 23263544048bf2292ebafc6dca41b45c6ee112f6701576365427d128c573e701 |
| `regime_symbol` | XLF | XLF | XLF | XLF | XLF |
| `source_symbol_dir` | XLF | XLF | XLF | XLF | XLF |
| `regime_proxy_role` | sector_etf | sector_etf | sector_etf | sector_etf | sector_etf |
| `source_dataset_id` | regime_indicators_v0_1 | regime_indicators_v0_1 | regime_indicators_v0_1 | regime_indicators_v0_1 | regime_indicators_v0_1 |
| `source_granularity` | minute | minute | minute | minute | minute |
| `context_granularity` | minute_aggregated_daily | minute_aggregated_daily | minute_aggregated_daily | minute_aggregated_daily | minute_aggregated_daily |
| `trading_date` | 2004-02-20 | 2004-02-23 | 2004-02-24 | 2004-02-25 | 2004-02-26 |
| `session_open_utc` |  |  |  |  |  |
| `as_of_utc` |  |  |  |  |  |
| `as_of_date` | 2004-02-20 | 2004-02-23 | 2004-02-24 | 2004-02-25 | 2004-02-26 |
| `as_of_semantics` | session_close_aggregate_from_minute_bars | session_close_aggregate_from_minute_bars | session_close_aggregate_from_minute_bars | session_close_aggregate_from_minute_bars | session_close_aggregate_from_minute_bars |
| `first_bar_timestamp` | 2004-02-20T14:31:00 | 2004-02-23T14:30:00 | 2004-02-24T14:30:00 | 2004-02-25T14:30:00 | 2004-02-26T14:30:00 |
| `last_bar_timestamp` | 2004-02-20T21:09:00 | 2004-02-23T21:11:00 | 2004-02-24T21:09:00 | 2004-02-25T21:07:00 | 2004-02-26T20:59:00 |
| `bars_observed` | 301 | 282 | 211 | 141 | 172 |
| `distinct_timestamp_count` | 301 | 282 | 211 | 141 | 172 |
| `duplicate_timestamp_rows` | 0 | 0 | 0 | 0 | 0 |
| `bar_coverage_state` | partial_session_like | partial_session_like | partial_session_like | partial_session_like | partial_session_like |
| `open_price` | 26.2038 | 26.3355 | 26.1161 | 25.9054 | 26.1161 |
| `high_price` | 26.2653 | 26.3355 | 26.1512 | 26.1599 | 26.1775 |
| `low_price` | 26.0019 | 26.0634 | 25.8527 | 25.9054 | 25.9844 |
| `close_price` | 26.0985 | 26.0985 | 25.9844 | 26.1073 | 26.1687 |
| `previous_close_price` | 26.1599 | 26.0985 | 26.0985 | 25.9844 | 26.1073 |
| `intraday_return` | -0.004018501133423391 | -0.008999259554593575 | -0.005042866277889857 | 0.007793741845329549 | 0.0020140832666439845 |
| `close_to_previous_close_return` | -0.0023471037733324707 | 0.0 | -0.00437189876812849 | 0.004729760933483096 | 0.002351832629188033 |
| `high_to_open_return` | 0.002346987841458148 | 0.0 | 0.0013439985296426205 | 0.009824206536088953 | 0.0023510401629645017 |
| `low_to_open_return` | -0.007704989352689373 | -0.01033206128609665 | -0.010085732555779825 | 0.0 | -0.005042866277889857 |
| `intraday_range_pct` | 0.010051977194147441 | 0.010332061286096646 | 0.011429731085422428 | 0.009824206536089007 | 0.0073939064408544 |
| `volume` | 2166427.862800002 | 1662811.4162000064 | 3370391.2702 | 3300789.4496000013 | 721307.2471999999 |
| `vwap` | 26.091676169944275 | 26.15445040076717 | 26.02614012235105 | 26.077764166896742 | 26.10865235312698 |
| `null_ohlc_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `non_positive_price_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `source_bad_ohlc_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `negative_volume_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `missing_volume_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `missing_vwap_bar_count` | 0 | 0 | 0 | 0 | 0 |
| `market_calendar_covered` | False | False | False | False | False |
| `session_minutes` |  |  |  |  |  |
| `is_early_close` |  |  |  |  |  |
| `market_calendar` |  |  |  |  |  |
| `market_timezone` |  |  |  |  |  |
| `timestamp_timezone_state` | vendor_naive_timestamp_review | vendor_naive_timestamp_review | vendor_naive_timestamp_review | vendor_naive_timestamp_review | vendor_naive_timestamp_review |
| `daily_source_files_blocked` | True | True | True | True | True |
| `built_from_blocked_day_parquet` | False | False | False | False | False |
| `built_from_minute_parquet` | True | True | True | True | True |
| `intraday_regime_features_source_included` | False | False | False | False | False |
| `regime_quality_state` | review_no_market_calendar_session | review_no_market_calendar_session | review_no_market_calendar_session | review_no_market_calendar_session | review_no_market_calendar_session |
| `valid_for_event_context_candidate` | False | False | False | False | False |
| `valid_for_ml_feature_candidate` | False | False | False | False | False |
| `valid_for_state_component_candidate` | False | False | False | False | False |
| `valid_for_backtest_core_direct` | False | False | False | False | False |
| `valid_for_rl_training_direct` | False | False | False | False | False |
| `requires_asof_filter` | True | True | True | True | True |
| `contains_future_information_without_event_filter` | True | True | True | True | True |
| `same_session_intraday_causal_claim_allowed` | False | False | False | False | False |
| `execution_truth` | False | False | False | False | False |
| `source_root` | E:/TSIS/data/regime_indicators | E:/TSIS/data/regime_indicators | E:/TSIS/data/regime_indicators | E:/TSIS/data/regime_indicators | E:/TSIS/data/regime_indicators |
| `source_file` | E:/TSIS/data/regime_indicators/etfs/XLF/minute.parquet | E:/TSIS/data/regime_indicators/etfs/XLF/minute.parquet | E:/TSIS/data/regime_indicators/etfs/XLF/minute.parquet | E:/TSIS/data/regime_indicators/etfs/XLF/minute.parquet | E:/TSIS/data/regime_indicators/etfs/XLF/minute.parquet |
| `source_file_relative_path` | etfs/XLF/minute.parquet | etfs/XLF/minute.parquet | etfs/XLF/minute.parquet | etfs/XLF/minute.parquet | etfs/XLF/minute.parquet |
| `market_calendar_source` | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet |
| `market_calendar_build_run_id` |  |  |  |  |  |
| `market_calendar_schema_version` |  |  |  |  |  |
| `full_universe_claim` | False | False | False | False | False |
| `materialization_scope` | regime_indicators_minute_aggregated_daily_context_v0_1 | regime_indicators_minute_aggregated_daily_context_v0_1 | regime_indicators_minute_aggregated_daily_context_v0_1 | regime_indicators_minute_aggregated_daily_context_v0_1 | regime_indicators_minute_aggregated_daily_context_v0_1 |
| `quality_policy_version` | regime_context_table_policy_v0_1 | regime_context_table_policy_v0_1 | regime_context_table_policy_v0_1 | regime_context_table_policy_v0_1 | regime_context_table_policy_v0_1 |
| `schema_version` | regime_context_table_v0_1 | regime_context_table_v0_1 | regime_context_table_v0_1 | regime_context_table_v0_1 | regime_context_table_v0_1 |
| `build_run_id` | regime_context_table_v0_1_20260627T084649Z | regime_context_table_v0_1_20260627T084649Z | regime_context_table_v0_1_20260627T084649Z | regime_context_table_v0_1_20260627T084649Z | regime_context_table_v0_1_20260627T084649Z |
| `created_at_utc` | 2026-06-27T08:46:49.042047+00:00 | 2026-06-27T08:46:49.042047+00:00 | 2026-06-27T08:46:49.042047+00:00 | 2026-06-27T08:46:49.042047+00:00 | 2026-06-27T08:46:49.042047+00:00 |
| `source_proxy_family` | etf | etf | etf | etf | etf |
| `observation_year` | 2004 | 2004 | 2004 | 2004 | 2004 |

## Interpretation

Use this file to understand the physical/logical shape and example values of the represented Data Foundation output.
For completeness, pass/fail status, official scope, and exclusions, use the cloned target contract and status matrix in the parent folder.

## Scope Guard

Excluded from this operational sample set:

- `master_intraday_bar_table`: scoped pilot/candidate, not official full-universe 1m.
- `microstructure_features_table`: seed/candidate controlled, not full-universe.
- `market_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `event_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `intraday_scanner_candidates_table`: strategy/candidate surface, not a validated Data Foundation full table.
