# master_daily_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Daily rows x three price views, 2005-01-03 to 2026-03-09. |
| operational_use | Daily event context, outcome research, and backtest core rows where flags allow. |
| exclusions | No full row-level audit labels; no execution/microstructure truth. |

## Source

| item | value |
| --- | --- |
| dataset_id | `master_daily_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1\year=2005\price_view=adjusted\data_0.parquet` |
| declared_rows_in_status_matrix | 22,109,097 |
| declared_file_or_partition_count_in_status_matrix | 66 |
| physical_parquet_files_seen | 66 |
| physical_rows_from_parquet_metadata | 22109097 |
| physical_row_groups_seen | 233 |
| sample_physical_columns | 71 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `master_daily_id` | `string` |
| 1 | `instrument_id` | `string` |
| 2 | `ticker` | `string` |
| 3 | `session_date` | `date32[day]` |
| 4 | `month` | `int32` |
| 5 | `quality_gate_family` | `string` |
| 6 | `source_dataset` | `string` |
| 7 | `source_root` | `string` |
| 8 | `expected_session` | `bool` |
| 9 | `expected_reason` | `string` |
| 10 | `expected_dataset_id` | `string` |
| 11 | `expected_source_root` | `string` |
| 12 | `data_present` | `bool` |
| 13 | `missing_expected_data` | `bool` |
| 14 | `source_daily_present` | `bool` |
| 15 | `source_adjusted_present` | `bool` |
| 16 | `open` | `double` |
| 17 | `high` | `double` |
| 18 | `low` | `double` |
| 19 | `close` | `double` |
| 20 | `volume` | `double` |
| 21 | `vwap` | `double` |
| 22 | `source_raw_vwap` | `double` |
| 23 | `transaction_count` | `int64` |
| 24 | `source_t_epoch_ms` | `int64` |
| 25 | `prior_close` | `double` |
| 26 | `gap_pct` | `double` |
| 27 | `daily_return_pct` | `double` |
| 28 | `intraday_return_pct` | `double` |
| 29 | `daily_range_pct` | `double` |
| 30 | `dollar_volume` | `double` |
| 31 | `volume_20d_avg` | `double` |
| 32 | `rvol_20d` | `double` |
| 33 | `future_split_factor` | `double` |
| 34 | `future_dividend_sum` | `double` |
| 35 | `future_dividend_factor` | `double` |
| 36 | `future_adjustment_factor` | `double` |
| 37 | `adjusted_materialized_price_view` | `string` |
| 38 | `adjusted_proxy_open` | `double` |
| 39 | `adjusted_proxy_high` | `double` |
| 40 | `adjusted_proxy_low` | `double` |
| 41 | `adjusted_proxy_close` | `double` |
| 42 | `source_daily_file` | `string` |
| 43 | `source_splits_file` | `string` |
| 44 | `source_dividends_file` | `string` |
| 45 | `corporate_action_count` | `int32` |
| 46 | `split_action_count` | `int32` |
| 47 | `dividend_action_count` | `int32` |
| 48 | `ticker_change_action_count` | `int32` |
| 49 | `has_split_action` | `bool` |
| 50 | `has_dividend_action` | `bool` |
| 51 | `has_ticker_change_action` | `bool` |
| 52 | `has_any_corporate_action` | `bool` |
| 53 | `row_level_price_integrity_state` | `string` |
| 54 | `selected_price_hard_invalid` | `bool` |
| 55 | `negative_volume` | `bool` |
| 56 | `backtest_core_row_candidate` | `bool` |
| 57 | `family_data_quality_verdict` | `string` |
| 58 | `family_foundations_completion_status` | `string` |
| 59 | `family_visual_inspection_status` | `string` |
| 60 | `family_production_use_gate` | `string` |
| 61 | `family_event_consumption_gate` | `string` |
| 62 | `gate_quality_policy_version` | `string` |
| 63 | `expected_data_calendar_build_run_id` | `string` |
| 64 | `dataset_certification_matrix_build_run_id` | `string` |
| 65 | `corporate_actions_build_run_id` | `string` |
| 66 | `expectation_policy_version` | `string` |
| 67 | `quality_policy_version` | `string` |
| 68 | `schema_version` | `string` |
| 69 | `build_run_id` | `string` |
| 70 | `created_at_utc` | `string` |
| 71 | `year` | `int32` |
| 72 | `price_view` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `master_daily_id` | d16cf62921a174edacad589490c91e58fa4f0a97191d8e8ec65c8d1566aff92d | b93008411154d9dddb93d6ef89defbb263c39d33d3f8aacb87e84a0c4a952905 | 5ecdfb6b630a65ca978735b06c6121099095b771bb8330108d1144f84ac3430c | 7769e23cf09e9c725c57c25eb7717d130d2034b1b79389bb8c52f00250652680 | 5871dc481d745bf66fb486197a24c397d5a3c8207439a12de578192f34a36798 |
| `instrument_id` | figi_share_class:BBG008NZ8QB1 | figi_share_class:BBG008NZ8QB1 | figi_share_class:BBG008NZ8QB1 | figi_share_class:BBG008NZ8QB1 | figi_share_class:BBG008NZ8QB1 |
| `ticker` | AC | AC | AC | AC | AC |
| `session_date` | 2005-01-03 | 2005-01-04 | 2005-01-05 | 2005-01-06 | 2005-01-07 |
| `month` | 1 | 1 | 1 | 1 | 1 |
| `quality_gate_family` | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted |
| `source_dataset` | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily_adjusted |
| `source_root` | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted |
| `expected_session` | True | True | True | True | True |
| `expected_reason` | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session |
| `expected_dataset_id` | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 |
| `expected_source_root` | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily |
| `data_present` | True | True | True | True | True |
| `missing_expected_data` | False | False | False | False | False |
| `source_daily_present` | True | True | True | True | True |
| `source_adjusted_present` | True | True | True | True | True |
| `open` | 39.405044622715664 | 39.03197911149469 | 37.95941576673439 | 38.0433555067591 | 38.09931533344225 |
| `high` | 39.405044622715664 | 39.143898764860985 | 38.36978782907746 | 38.40709438019955 | 38.23921490015012 |
| `low` | 38.79881316698158 | 38.09931533344225 | 37.86614938892914 | 38.006048955637006 | 37.60500353107445 |
| `close` | 39.143898764860985 | 38.164601797905924 | 38.0433555067591 | 38.006048955637006 | 37.70759654666022 |
| `volume` | 201100.0 | 262600.0 | 136500.0 | 124400.0 | 132800.0 |
| `vwap` |  |  |  |  |  |
| `source_raw_vwap` | 41.9305 | 41.4404 | 40.8413 | 40.9506 | 40.5401 |
| `transaction_count` | 575 | 584 | 517 | 388 | 517 |
| `source_t_epoch_ms` | 1104728400000 | 1104814800000 | 1104901200000 | 1104987600000 | 1105074000000 |
| `prior_close` |  | 39.143898764860985 | 38.164601797905924 | 38.0433555067591 | 38.006048955637006 |
| `gap_pct` |  | -0.002859185132237263 | -0.005376344086021501 | 0.0 | 0.0024539877300613355 |
| `daily_return_pct` |  | -0.02501786990707644 | -0.0031769305962856542 | -0.0009806325079675382 | -0.007852760736196451 |
| `intraday_return_pct` | -0.006627218934911139 | -0.022222222222222143 | 0.0022113022113019465 | -0.0009806325079675382 | -0.010281517747858127 |
| `daily_range_pct` | 0.015624999999999778 | 0.027417380660954782 | 0.013300492610837544 | 0.010552147239263787 | 0.016865079365079527 |
| `dollar_volume` | 7871838.041613544 | 10022024.432130096 | 5192918.026672617 | 4727952.490081243 | 5007568.8213964775 |
| `volume_20d_avg` |  | 201100.0 | 231850.0 | 200066.66666666666 | 181150.0 |
| `rvol_20d` |  | 1.3058180009945302 | 0.5887427215872332 | 0.6217927357547485 | 0.7330941208942865 |
| `future_split_factor` | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| `future_dividend_sum` | 3.9000000000000004 | 3.9000000000000004 | 3.9000000000000004 | 3.9000000000000004 | 3.9000000000000004 |
| `future_dividend_factor` | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 |
| `future_adjustment_factor` | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 | 0.9326637780524418 |
| `adjusted_materialized_price_view` | daily_adjusted_v0_1 | daily_adjusted_v0_1 | daily_adjusted_v0_1 | daily_adjusted_v0_1 | daily_adjusted_v0_1 |
| `adjusted_proxy_open` | 39.405044622715664 | 39.03197911149469 | 37.95941576673439 | 38.0433555067591 | 38.09931533344225 |
| `adjusted_proxy_high` | 39.405044622715664 | 39.143898764860985 | 38.36978782907746 | 38.40709438019955 | 38.23921490015012 |
| `adjusted_proxy_low` | 38.79881316698158 | 38.09931533344225 | 37.86614938892914 | 38.006048955637006 | 37.60500353107445 |
| `adjusted_proxy_close` | 39.143898764860985 | 38.164601797905924 | 38.0433555067591 | 38.006048955637006 | 37.70759654666022 |
| `source_daily_file` | D:\ohlcv_daily\ticker=AC\year=2005\day_aggs_AC_2005.parquet | D:\ohlcv_daily\ticker=AC\year=2005\day_aggs_AC_2005.parquet | D:\ohlcv_daily\ticker=AC\year=2005\day_aggs_AC_2005.parquet | D:\ohlcv_daily\ticker=AC\year=2005\day_aggs_AC_2005.parquet | D:\ohlcv_daily\ticker=AC\year=2005\day_aggs_AC_2005.parquet |
| `source_splits_file` | C:\TSIS_Data\data\additional\corporate_actions\splits\ticker=AC\splits_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\splits\ticker=AC\splits_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\splits\ticker=AC\splits_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\splits\ticker=AC\splits_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\splits\ticker=AC\splits_AC.parquet |
| `source_dividends_file` | C:\TSIS_Data\data\additional\corporate_actions\dividends\ticker=AC\dividends_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\dividends\ticker=AC\dividends_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\dividends\ticker=AC\dividends_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\dividends\ticker=AC\dividends_AC.parquet | C:\TSIS_Data\data\additional\corporate_actions\dividends\ticker=AC\dividends_AC.parquet |
| `corporate_action_count` | 0 | 0 | 0 | 0 | 0 |
| `split_action_count` | 0 | 0 | 0 | 0 | 0 |
| `dividend_action_count` | 0 | 0 | 0 | 0 | 0 |
| `ticker_change_action_count` | 0 | 0 | 0 | 0 | 0 |
| `has_split_action` | False | False | False | False | False |
| `has_dividend_action` | False | False | False | False | False |
| `has_ticker_change_action` | False | False | False | False | False |
| `has_any_corporate_action` | False | False | False | False | False |
| `row_level_price_integrity_state` | row_candidate | row_candidate | row_candidate | row_candidate | row_candidate |
| `selected_price_hard_invalid` | False | False | False | False | False |
| `negative_volume` | False | False | False | False | False |
| `backtest_core_row_candidate` | True | True | True | True | True |
| `family_data_quality_verdict` | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope |
| `family_foundations_completion_status` | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready |
| `family_visual_inspection_status` | visual_complete | visual_complete | visual_complete | visual_complete | visual_complete |
| `family_production_use_gate` | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed |
| `family_event_consumption_gate` | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy |
| `gate_quality_policy_version` | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 |
| `expected_data_calendar_build_run_id` | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z |
| `dataset_certification_matrix_build_run_id` | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z |
| `corporate_actions_build_run_id` | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z |
| `expectation_policy_version` | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 |
| `quality_policy_version` | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 |
| `schema_version` | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 |
| `build_run_id` | master_daily_table_v0_1_20260630T201044Z | master_daily_table_v0_1_20260630T201044Z | master_daily_table_v0_1_20260630T201044Z | master_daily_table_v0_1_20260630T201044Z | master_daily_table_v0_1_20260630T201044Z |
| `created_at_utc` | 2026-06-30T20:10:44.783816+00:00 | 2026-06-30T20:10:44.783816+00:00 | 2026-06-30T20:10:44.783816+00:00 | 2026-06-30T20:10:44.783816+00:00 | 2026-06-30T20:10:44.783816+00:00 |
| `year` | 2005 | 2005 | 2005 | 2005 | 2005 |
| `price_view` | adjusted | adjusted | adjusted | adjusted | adjusted |

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
