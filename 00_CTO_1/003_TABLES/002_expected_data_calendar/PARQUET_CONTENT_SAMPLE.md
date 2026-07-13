# expected_data_calendar_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Expected rows by dataset family/year, 2005-01-03 to 2026-03-09. |
| operational_use | Coverage denominator and absence diagnostics. |
| exclusions | Not proof of physical data presence; must be joined to actual validators. |

## Source

| item | value |
| --- | --- |
| dataset_id | `expected_data_calendar_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1\dataset_family=daily_raw\year=2005\data_0.parquet` |
| declared_rows_in_status_matrix | 29,478,796 |
| declared_file_or_partition_count_in_status_matrix | 88 |
| physical_parquet_files_seen | 88 |
| physical_rows_from_parquet_metadata | 29478796 |
| physical_row_groups_seen | 444 |
| sample_physical_columns | 21 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `expected_dataset_id` | `string` |
| 1 | `expected_source_root` | `string` |
| 2 | `instrument_id` | `string` |
| 3 | `ticker` | `string` |
| 4 | `session_date` | `date32[day]` |
| 5 | `expected_session` | `bool` |
| 6 | `expected_reason` | `string` |
| 7 | `expectation_scope` | `string` |
| 8 | `calendar` | `string` |
| 9 | `timezone` | `string` |
| 10 | `month` | `int32` |
| 11 | `valid_from` | `date32[day]` |
| 12 | `valid_to` | `date32[day]` |
| 13 | `instrument_master_schema_version` | `string` |
| 14 | `instrument_master_build_run_id` | `string` |
| 15 | `market_calendar_schema_version` | `string` |
| 16 | `market_calendar_build_run_id` | `string` |
| 17 | `expectation_policy_version` | `string` |
| 18 | `build_run_id` | `string` |
| 19 | `schema_version` | `string` |
| 20 | `created_at_utc` | `string` |
| 21 | `dataset_family` | `string` |
| 22 | `year` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `expected_dataset_id` | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 | daily_core_v0_1 |
| `expected_source_root` | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily |
| `instrument_id` | cik_ticker:0001864943:FGI | cik_ticker:0001864943:FGI | cik_ticker:0001864943:FGI | cik_ticker:0001864943:FGI | cik_ticker:0001864943:FGI |
| `ticker` | FGI | FGI | FGI | FGI | FGI |
| `session_date` | 2005-12-30 | 2005-12-29 | 2005-12-28 | 2005-12-27 | 2005-12-23 |
| `expected_session` | True | True | True | True | True |
| `expected_reason` | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session |
| `expectation_scope` | core_session_presence | core_session_presence | core_session_presence | core_session_presence | core_session_presence |
| `calendar` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `timezone` | America/New_York | America/New_York | America/New_York | America/New_York | America/New_York |
| `month` | 12 | 12 | 12 | 12 | 12 |
| `valid_from` | 2005-12-23 | 2005-12-23 | 2005-12-23 | 2005-12-23 | 2005-12-23 |
| `valid_to` | 2026-03-09 | 2026-03-09 | 2026-03-09 | 2026-03-09 | 2026-03-09 |
| `instrument_master_schema_version` | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 |
| `instrument_master_build_run_id` | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z |
| `market_calendar_schema_version` | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 |
| `market_calendar_build_run_id` | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z |
| `expectation_policy_version` | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 |
| `build_run_id` | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z | expected_data_calendar_v0_1_20260630T194807Z |
| `schema_version` | expected_data_calendar_v0_1 | expected_data_calendar_v0_1 | expected_data_calendar_v0_1 | expected_data_calendar_v0_1 | expected_data_calendar_v0_1 |
| `created_at_utc` | 2026-06-30T19:48:07.470685+00:00 | 2026-06-30T19:48:07.470685+00:00 | 2026-06-30T19:48:07.470685+00:00 | 2026-06-30T19:48:07.470685+00:00 | 2026-06-30T19:48:07.470685+00:00 |
| `dataset_family` | daily_raw | daily_raw | daily_raw | daily_raw | daily_raw |
| `year` | 2005 | 2005 | 2005 | 2005 | 2005 |

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
