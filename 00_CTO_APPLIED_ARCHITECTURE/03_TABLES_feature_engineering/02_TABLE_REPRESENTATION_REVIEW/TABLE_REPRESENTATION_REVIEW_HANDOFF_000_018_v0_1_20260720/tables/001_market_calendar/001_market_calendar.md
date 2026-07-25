# market_calendar_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | XNYS sessions, 2005-01-03 to 2026-03-09. |
| operational_use | Session calendar for event/backtest/materialization. |
| exclusions | Not venue-specific liquidity calendar; no live future extension beyond current source limit. |

## Source

| item | value |
| --- | --- |
| dataset_id | `market_calendar_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet` |
| declared_rows_in_status_matrix | 5,328 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 5328 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 16 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `session_date` | `date32[day]` |
| 1 | `open_utc` | `timestamp[ns, tz=UTC]` |
| 2 | `close_utc` | `timestamp[ns, tz=UTC]` |
| 3 | `open_et` | `timestamp[ns, tz=America/New_York]` |
| 4 | `close_et` | `timestamp[ns, tz=America/New_York]` |
| 5 | `session_minutes` | `double` |
| 6 | `is_early_close` | `bool` |
| 7 | `year` | `int16` |
| 8 | `month` | `int8` |
| 9 | `dow` | `string` |
| 10 | `calendar` | `string` |
| 11 | `timezone` | `string` |
| 12 | `source_calendar_artifact` | `string` |
| 13 | `build_run_id` | `string` |
| 14 | `schema_version` | `string` |
| 15 | `created_at_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `session_date` | 2005-01-03 | 2005-01-04 | 2005-01-05 | 2005-01-06 | 2005-01-07 |
| `open_utc` | 2005-01-03T14:30:00+00:00 | 2005-01-04T14:30:00+00:00 | 2005-01-05T14:30:00+00:00 | 2005-01-06T14:30:00+00:00 | 2005-01-07T14:30:00+00:00 |
| `close_utc` | 2005-01-03T21:00:00+00:00 | 2005-01-04T21:00:00+00:00 | 2005-01-05T21:00:00+00:00 | 2005-01-06T21:00:00+00:00 | 2005-01-07T21:00:00+00:00 |
| `open_et` | 2005-01-03T09:30:00-05:00 | 2005-01-04T09:30:00-05:00 | 2005-01-05T09:30:00-05:00 | 2005-01-06T09:30:00-05:00 | 2005-01-07T09:30:00-05:00 |
| `close_et` | 2005-01-03T16:00:00-05:00 | 2005-01-04T16:00:00-05:00 | 2005-01-05T16:00:00-05:00 | 2005-01-06T16:00:00-05:00 | 2005-01-07T16:00:00-05:00 |
| `session_minutes` | 390.0 | 390.0 | 390.0 | 390.0 | 390.0 |
| `is_early_close` | False | False | False | False | False |
| `year` | 2005 | 2005 | 2005 | 2005 | 2005 |
| `month` | 1 | 1 | 1 | 1 | 1 |
| `dow` | Monday | Tuesday | Wednesday | Thursday | Friday |
| `calendar` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `timezone` | America/New_York | America/New_York | America/New_York | America/New_York | America/New_York |
| `source_calendar_artifact` | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet |
| `build_run_id` | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z | market_calendar_v0_1_20260630T193931Z |
| `schema_version` | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 | market_calendar_v0_1 |
| `created_at_utc` | 2026-06-30T19:39:31.308479+00:00 | 2026-06-30T19:39:31.308479+00:00 | 2026-06-30T19:39:31.308479+00:00 | 2026-06-30T19:39:31.308479+00:00 | 2026-06-30T19:39:31.308479+00:00 |

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
