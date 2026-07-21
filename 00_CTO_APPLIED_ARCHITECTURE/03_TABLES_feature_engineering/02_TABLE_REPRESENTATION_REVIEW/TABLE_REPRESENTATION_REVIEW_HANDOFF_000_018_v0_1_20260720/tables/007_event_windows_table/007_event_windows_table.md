# event_windows_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Halt-derived event windows for LT1B/calendar-covered intraday halt events. |
| operational_use | Event-window boundaries, pre-event feature windows, outcome-window candidates. |
| exclusions | Halts only; not all event families; not primary ML/RL/execution truth. |

## Source

| item | value |
| --- | --- |
| dataset_id | `event_windows_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet` |
| declared_rows_in_status_matrix | 214,112 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 214112 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 63 |

## Sample Selection

First rows from the official single-file parquet; the partial timeout sibling folder is not used.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `event_window_id` | `string` |
| 1 | `source_event_id` | `string` |
| 2 | `event_source_dataset_id` | `string` |
| 3 | `event_family` | `string` |
| 4 | `event_type` | `string` |
| 5 | `event_code` | `string` |
| 6 | `event_source` | `string` |
| 7 | `ticker` | `string` |
| 8 | `instrument_id` | `string` |
| 9 | `issuer_name` | `string` |
| 10 | `listing_exchange` | `string` |
| 11 | `session_date` | `timestamp[ns]` |
| 12 | `year` | `int64` |
| 13 | `month` | `int64` |
| 14 | `event_time_utc` | `timestamp[ns, tz=UTC]` |
| 15 | `resume_trade_utc` | `timestamp[ns, tz=UTC]` |
| 16 | `event_session_phase` | `string` |
| 17 | `window_role` | `string` |
| 18 | `window_start_utc` | `timestamp[ns, tz=UTC]` |
| 19 | `window_end_utc` | `timestamp[ns, tz=UTC]` |
| 20 | `window_duration_minutes` | `double` |
| 21 | `window_start_source` | `string` |
| 22 | `window_end_source` | `string` |
| 23 | `contains_event_time` | `bool` |
| 24 | `contains_post_event_information` | `bool` |
| 25 | `leakage_safe_as_pre_event_feature` | `bool` |
| 26 | `source_event_quality_state` | `string` |
| 27 | `source_halt_event_state` | `string` |
| 28 | `source_resume_trade_observed` | `bool` |
| 29 | `event_response_end_observed` | `bool` |
| 30 | `event_window_quality_state` | `string` |
| 31 | `event_window_consumption_state` | `string` |
| 32 | `session_open_utc` | `timestamp[ns, tz=UTC]` |
| 33 | `session_close_utc` | `timestamp[ns, tz=UTC]` |
| 34 | `session_minutes` | `double` |
| 35 | `is_early_close` | `bool` |
| 36 | `calendar` | `string` |
| 37 | `timezone` | `string` |
| 38 | `previous_session_date` | `timestamp[ns]` |
| 39 | `next_session_date` | `timestamp[ns]` |
| 40 | `instrument_identity_temporal_match` | `bool` |
| 41 | `is_common_stock` | `bool` |
| 42 | `is_lt1b_operational` | `bool` |
| 43 | `lt1b_classification_1b` | `string` |
| 44 | `valid_for_event_engine` | `bool` |
| 45 | `valid_for_microstructure_feature_candidate` | `bool` |
| 46 | `valid_for_ml_feature_candidate` | `bool` |
| 47 | `valid_for_outcome_window_candidate` | `bool` |
| 48 | `valid_for_backtest_event_window_candidate` | `bool` |
| 49 | `valid_for_rl_state_component_candidate` | `bool` |
| 50 | `requires_decision_time_availability_contract` | `bool` |
| 51 | `full_universe_claim` | `bool` |
| 52 | `materialization_scope` | `string` |
| 53 | `quality_policy_version` | `string` |
| 54 | `schema_version` | `string` |
| 55 | `build_run_id` | `string` |
| 56 | `created_at_utc` | `string` |
| 57 | `source_halts_table_path` | `string` |
| 58 | `source_halts_table_sha256` | `string` |
| 59 | `source_instrument_master_path` | `string` |
| 60 | `source_instrument_master_sha256` | `string` |
| 61 | `source_market_calendar_path` | `string` |
| 62 | `source_market_calendar_sha256` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `event_window_id` | 66f6b4ec9efafd08a5bc2d953a658151fe2337c79ba6b2a57a929a090ea898c5 | 7021094a6173673d386f1d7bdd5bee1422d6f3fed208d9337d0f7dd1aed28b35 | f5c138149cc8e3892d1e174f06899e4ba226b6448cea07db1d7d8b2a096b745e | 396bec234060f8104ba7c0cc61e651a6bc719b4e93b71fab57955757671d9dd8 | 2125c0255918b1b167d41610b7bff27e807301cf533525ac9bf4b3eaffdfb630 |
| `source_event_id` | 00017e432df5b908022ceaf0fd727980f80608ca6c3b2a21ba5946a488edf06f | 00017e432df5b908022ceaf0fd727980f80608ca6c3b2a21ba5946a488edf06f | 00017e432df5b908022ceaf0fd727980f80608ca6c3b2a21ba5946a488edf06f | 00017e432df5b908022ceaf0fd727980f80608ca6c3b2a21ba5946a488edf06f | 00017e432df5b908022ceaf0fd727980f80608ca6c3b2a21ba5946a488edf06f |
| `event_source_dataset_id` | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 |
| `event_family` | halt | halt | halt | halt | halt |
| `event_type` | News and resumption pending | News and resumption pending | News and resumption pending | News and resumption pending | News and resumption pending |
| `event_code` | T3 | T3 | T3 | T3 | T3 |
| `event_source` | nasdaq | nasdaq | nasdaq | nasdaq | nasdaq |
| `ticker` | NXU | NXU | NXU | NXU | NXU |
| `instrument_id` | figi_share_class:BBG01G96Y7P0 | figi_share_class:BBG01G96Y7P0 | figi_share_class:BBG01G96Y7P0 | figi_share_class:BBG01G96Y7P0 | figi_share_class:BBG01G96Y7P0 |
| `issuer_name` |  |  |  |  |  |
| `listing_exchange` |  |  |  |  |  |
| `session_date` | 2025-03-28T00:00:00 | 2025-03-28T00:00:00 | 2025-03-28T00:00:00 | 2025-03-28T00:00:00 | 2025-03-28T00:00:00 |
| `year` | 2025 | 2025 | 2025 | 2025 | 2025 |
| `month` | 3 | 3 | 3 | 3 | 3 |
| `event_time_utc` | 2025-03-28T23:50:00+00:00 | 2025-03-28T23:50:00+00:00 | 2025-03-28T23:50:00+00:00 | 2025-03-28T23:50:00+00:00 | 2025-03-28T23:50:00+00:00 |
| `resume_trade_utc` | 2025-03-31T13:00:00+00:00 | 2025-03-31T13:00:00+00:00 | 2025-03-31T13:00:00+00:00 | 2025-03-31T13:00:00+00:00 | 2025-03-31T13:00:00+00:00 |
| `event_session_phase` | afterhours | afterhours | afterhours | afterhours | afterhours |
| `window_role` | prior_session_regular | pre_event_30m | event_to_resume_or_30m | same_session_regular | next_session_regular |
| `window_start_utc` | 2025-03-27T13:30:00+00:00 | 2025-03-28T23:20:00+00:00 | 2025-03-28T23:50:00+00:00 | 2025-03-28T13:30:00+00:00 | 2025-03-31T13:30:00+00:00 |
| `window_end_utc` | 2025-03-27T20:00:00+00:00 | 2025-03-28T23:50:00+00:00 | 2025-03-31T13:00:00+00:00 | 2025-03-28T20:00:00+00:00 | 2025-03-31T20:00:00+00:00 |
| `window_duration_minutes` | 390.0 | 30.0 | 3670.0 | 390.0 | 390.0 |
| `window_start_source` | previous_session_open_utc | event_time_utc_minus_30m | event_time_utc | session_open_utc | next_session_open_utc |
| `window_end_source` | previous_session_close_utc | event_time_utc | resume_trade_utc | session_close_utc | next_session_close_utc |
| `contains_event_time` | False | False | True | False | False |
| `contains_post_event_information` | False | False | True | False | True |
| `leakage_safe_as_pre_event_feature` | True | True | False | True | False |
| `source_event_quality_state` | good | good | good | good | good |
| `source_halt_event_state` | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event |
| `source_resume_trade_observed` | True | True | True | True | True |
| `event_response_end_observed` | False | False | True | False | False |
| `event_window_quality_state` | good | good | good | good | good |
| `event_window_consumption_state` | pre_event_context_window | pre_event_feature_candidate | event_response_window | session_context_window | outcome_candidate_window |
| `session_open_utc` | 2025-03-28T13:30:00+00:00 | 2025-03-28T13:30:00+00:00 | 2025-03-28T13:30:00+00:00 | 2025-03-28T13:30:00+00:00 | 2025-03-28T13:30:00+00:00 |
| `session_close_utc` | 2025-03-28T20:00:00+00:00 | 2025-03-28T20:00:00+00:00 | 2025-03-28T20:00:00+00:00 | 2025-03-28T20:00:00+00:00 | 2025-03-28T20:00:00+00:00 |
| `session_minutes` | 390.0 | 390.0 | 390.0 | 390.0 | 390.0 |
| `is_early_close` | False | False | False | False | False |
| `calendar` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `timezone` | America/New_York | America/New_York | America/New_York | America/New_York | America/New_York |
| `previous_session_date` | 2025-03-27T00:00:00 | 2025-03-27T00:00:00 | 2025-03-27T00:00:00 | 2025-03-27T00:00:00 | 2025-03-27T00:00:00 |
| `next_session_date` | 2025-03-31T00:00:00 | 2025-03-31T00:00:00 | 2025-03-31T00:00:00 | 2025-03-31T00:00:00 | 2025-03-31T00:00:00 |
| `instrument_identity_temporal_match` | True | True | True | True | True |
| `is_common_stock` | True | True | True | True | True |
| `is_lt1b_operational` | True | True | True | True | True |
| `lt1b_classification_1b` | inactive_died_lt_1b | inactive_died_lt_1b | inactive_died_lt_1b | inactive_died_lt_1b | inactive_died_lt_1b |
| `valid_for_event_engine` | True | True | True | True | True |
| `valid_for_microstructure_feature_candidate` | False | True | False | True | False |
| `valid_for_ml_feature_candidate` | True | True | False | False | False |
| `valid_for_outcome_window_candidate` | False | False | True | False | True |
| `valid_for_backtest_event_window_candidate` | False | False | False | False | False |
| `valid_for_rl_state_component_candidate` | False | False | False | False | False |
| `requires_decision_time_availability_contract` | True | True | True | True | True |
| `full_universe_claim` | False | False | False | False | False |
| `materialization_scope` | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered |
| `quality_policy_version` | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 |
| `schema_version` | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 |
| `build_run_id` | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z |
| `created_at_utc` | 2026-06-25T23:10:16.507875+00:00 | 2026-06-25T23:10:16.507875+00:00 | 2026-06-25T23:10:16.507875+00:00 | 2026-06-25T23:10:16.507875+00:00 | 2026-06-25T23:10:16.507875+00:00 |
| `source_halts_table_path` | E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet |
| `source_halts_table_sha256` | b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8 | b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8 | b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8 | b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8 | b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8 |
| `source_instrument_master_path` | E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet |
| `source_instrument_master_sha256` | 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2 | 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2 | 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2 | 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2 | 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2 |
| `source_market_calendar_path` | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet |
| `source_market_calendar_sha256` | 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5 | 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5 | 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5 | 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5 | 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5 |

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
