# short_context_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Source-scoped short interest/short volume from short and FINRA short_review; no borrow/SSR. |
| operational_use | Short pressure/crowding/squeeze context after explicit source selection and as-of/lag join. |
| exclusions | Not borrow, not SSR, not intraday tape, not direct ML/RL table. |

## Source

| item | value |
| --- | --- |
| dataset_id | `short_context_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\short_context_table\short_context_table_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\short_context_table\short_context_table_v0_1\source_system=finra_official_free\observation_family=short_interest\observation_year=2017\data_0.parquet` |
| declared_rows_in_status_matrix | 7,145,337 |
| declared_file_or_partition_count_in_status_matrix | 32 |
| physical_parquet_files_seen | 32 |
| physical_rows_from_parquet_metadata | 7145337 |
| physical_row_groups_seen | 99 |
| sample_physical_columns | 79 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `short_context_id` | `string` |
| 1 | `ticker` | `string` |
| 2 | `instrument_id` | `string` |
| 3 | `source_dataset_id` | `string` |
| 4 | `source_family` | `string` |
| 5 | `source_scope` | `string` |
| 6 | `observation_date_type` | `string` |
| 7 | `observation_date` | `date32[day]` |
| 8 | `settlement_date` | `date32[day]` |
| 9 | `trade_date` | `date32[day]` |
| 10 | `as_of_date` | `date32[day]` |
| 11 | `as_of_semantics` | `string` |
| 12 | `short_interest` | `double` |
| 13 | `avg_daily_volume` | `double` |
| 14 | `days_to_cover` | `double` |
| 15 | `total_volume` | `double` |
| 16 | `short_volume` | `double` |
| 17 | `exempt_volume` | `double` |
| 18 | `non_exempt_volume` | `double` |
| 19 | `short_volume_ratio` | `double` |
| 20 | `nyse_short_volume` | `double` |
| 21 | `nyse_short_volume_exempt` | `double` |
| 22 | `nasdaq_carteret_short_volume` | `double` |
| 23 | `nasdaq_carteret_short_volume_exempt` | `double` |
| 24 | `nasdaq_chicago_short_volume` | `double` |
| 25 | `nasdaq_chicago_short_volume_exempt` | `double` |
| 26 | `adf_short_volume` | `double` |
| 27 | `adf_short_volume_exempt` | `double` |
| 28 | `orf_short_volume` | `double` |
| 29 | `orf_short_volume_exempt` | `double` |
| 30 | `local_certification_status` | `string` |
| 31 | `local_certification_reason` | `string` |
| 32 | `local_certified_date_start` | `date32[day]` |
| 33 | `local_certified_date_end` | `date32[day]` |
| 34 | `local_entity_id_nunique` | `int64` |
| 35 | `local_panel_min_date` | `date32[day]` |
| 36 | `local_panel_max_date` | `date32[day]` |
| 37 | `local_observation_inside_certified_window` | `bool` |
| 38 | `instrument_master_ticker_present` | `bool` |
| 39 | `instrument_identity_temporal_match` | `bool` |
| 40 | `instrument_identity_state` | `string` |
| 41 | `is_common_stock` | `bool` |
| 42 | `is_lt1b_operational` | `bool` |
| 43 | `lt1b_classification_1b` | `string` |
| 44 | `source_duplicate_key_flag` | `bool` |
| 45 | `source_duplicate_key_count` | `int64` |
| 46 | `source_duplicate_key_ordinal` | `int64` |
| 47 | `source_duplicate_excess_row` | `bool` |
| 48 | `finra_official_free_baseline` | `bool` |
| 49 | `local_polygon_operational_source` | `bool` |
| 50 | `short_volume_source_scope_not_consolidated_market_wide` | `bool` |
| 51 | `finra_pre_modern_short_interest_semantics_flag` | `bool` |
| 52 | `finra_pre_official_free_short_volume_window_flag` | `bool` |
| 53 | `full_2005_2026_official_free_history_claim` | `bool` |
| 54 | `borrow_data_present` | `bool` |
| 55 | `ssr_data_present` | `bool` |
| 56 | `execution_truth` | `bool` |
| 57 | `requires_availability_lag_assumption` | `bool` |
| 58 | `same_day_intraday_causal_claim_allowed` | `bool` |
| 59 | `prohibited_without_asof_filter` | `bool` |
| 60 | `contains_future_information_without_event_filter` | `bool` |
| 61 | `short_quality_state` | `string` |
| 62 | `valid_for_event_context_candidate` | `bool` |
| 63 | `valid_for_ml_feature_candidate` | `bool` |
| 64 | `valid_for_backtest_context_candidate` | `bool` |
| 65 | `valid_for_state_component_candidate` | `bool` |
| 66 | `valid_for_rl_training_direct` | `bool` |
| 67 | `source_root` | `string` |
| 68 | `source_file` | `string` |
| 69 | `source_file_relative_path` | `string` |
| 70 | `source_file_row_number` | `int64` |
| 71 | `instrument_master_build_run_id` | `string` |
| 72 | `instrument_master_schema_version` | `string` |
| 73 | `full_universe_claim` | `bool` |
| 74 | `materialization_scope` | `string` |
| 75 | `quality_policy_version` | `string` |
| 76 | `schema_version` | `string` |
| 77 | `build_run_id` | `string` |
| 78 | `created_at_utc` | `string` |
| 79 | `source_system` | `string` |
| 80 | `observation_family` | `string` |
| 81 | `observation_year` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `short_context_id` | 6c463138b1bb43d3b08ab3043585ec25f711ef7d36091c3c4c775d412b6f37d9 | ea7964032da31229965ad091972e34b106439deac6b4d2a40475186683e7c641 | 5a6146260dfef894d6065b640aca729c3ed785e14f38fb6c260061f69bd8fc08 | 8c60a81beba946ba74ffa0de0170ee6edaf37482cde8400ddef28cc12dfe6d81 | 51a6cc675519c2f16e5c916aa5ebcee7c2615a06c3caed3625731721d9aa55a5 |
| `ticker` | AVHI | AYTU | BDN | ACER | AKBA |
| `instrument_id` | figi_share_class:BBG01223ZV80 | figi_share_class:BBG001T21Q11 | figi_share_class:BBG001S6YGF4 | figi_share_class:BBG001S7Q351 | figi_share_class:BBG001T922S9 |
| `source_dataset_id` | short_review_finra_v0_1 | short_review_finra_v0_1 | short_review_finra_v0_1 | short_review_finra_v0_1 | short_review_finra_v0_1 |
| `source_family` | short_review | short_review | short_review | short_review | short_review |
| `source_scope` | finra_official_free_equity_short_interest | finra_official_free_equity_short_interest | finra_official_free_equity_short_interest | finra_official_free_equity_short_interest | finra_official_free_equity_short_interest |
| `observation_date_type` | settlement_date | settlement_date | settlement_date | settlement_date | settlement_date |
| `observation_date` | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 |
| `settlement_date` | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 |
| `trade_date` |  |  |  |  |  |
| `as_of_date` | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 |
| `as_of_semantics` | settlement_date_observation_requires_lag_contract | settlement_date_observation_requires_lag_contract | settlement_date_observation_requires_lag_contract | settlement_date_observation_requires_lag_contract | settlement_date_observation_requires_lag_contract |
| `short_interest` | 1252681.0 | 15243.0 | 6135190.0 | 40526.0 | 2913872.0 |
| `avg_daily_volume` | 58738.0 | 81607.0 | 1680895.0 | 47243.0 | 272724.0 |
| `days_to_cover` | 21.33 | 1.0 | 3.65 | 1.0 | 10.68 |
| `total_volume` |  |  |  |  |  |
| `short_volume` |  |  |  |  |  |
| `exempt_volume` |  |  |  |  |  |
| `non_exempt_volume` |  |  |  |  |  |
| `short_volume_ratio` |  |  |  |  |  |
| `nyse_short_volume` |  |  |  |  |  |
| `nyse_short_volume_exempt` |  |  |  |  |  |
| `nasdaq_carteret_short_volume` |  |  |  |  |  |
| `nasdaq_carteret_short_volume_exempt` |  |  |  |  |  |
| `nasdaq_chicago_short_volume` |  |  |  |  |  |
| `nasdaq_chicago_short_volume_exempt` |  |  |  |  |  |
| `adf_short_volume` |  |  |  |  |  |
| `adf_short_volume_exempt` |  |  |  |  |  |
| `orf_short_volume` |  |  |  |  |  |
| `orf_short_volume_exempt` |  |  |  |  |  |
| `local_certification_status` | REVIEW_TICKER_REUSE | REVIEW_TICKER_REUSE | REVIEW_REFERENCE_CONFLICT | REVIEW_TICKER_REUSE | REVIEW_REFERENCE_CONFLICT |
| `local_certification_reason` | outside_window_with_multi_entity_and_reference_context | outside_window_with_multi_entity_and_reference_context | outside_window_but_single_entity | outside_window_with_multi_entity_and_reference_context | outside_window_but_single_entity |
| `local_certified_date_start` | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 | 2017-12-29 |
| `local_certified_date_end` | 2024-04-08 | 2026-03-09 | 2026-03-09 | 2023-11-08 | 2026-03-09 |
| `local_entity_id_nunique` | 2 | 4 | 1 | 2 | 1 |
| `local_panel_min_date` | 2016-10-25 | 2017-10-20 | 2005-01-01 | 2017-09-21 | 2016-10-25 |
| `local_panel_max_date` | 2024-04-08 | 2026-12-31 | 2026-12-31 | 2023-11-08 | 2026-12-31 |
| `local_observation_inside_certified_window` |  |  |  |  |  |
| `instrument_master_ticker_present` | True | True | True | True | True |
| `instrument_identity_temporal_match` | True | True | True | True | True |
| `instrument_identity_state` | good_temporal_match | good_temporal_match | good_temporal_match | good_temporal_match | good_temporal_match |
| `is_common_stock` | True | True | True | True | True |
| `is_lt1b_operational` | True | True | True | True | True |
| `lt1b_classification_1b` | inactive_died_lt_1b | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable | inactive_died_lt_1b | active_lt_1b_last_classifiable |
| `source_duplicate_key_flag` | False | False | False | False | False |
| `source_duplicate_key_count` | 1 | 1 | 1 | 1 | 1 |
| `source_duplicate_key_ordinal` | 1 | 1 | 1 | 1 | 1 |
| `source_duplicate_excess_row` | False | False | False | False | False |
| `finra_official_free_baseline` | True | True | True | True | True |
| `local_polygon_operational_source` | False | False | False | False | False |
| `short_volume_source_scope_not_consolidated_market_wide` | False | False | False | False | False |
| `finra_pre_modern_short_interest_semantics_flag` | True | True | True | True | True |
| `finra_pre_official_free_short_volume_window_flag` | False | False | False | False | False |
| `full_2005_2026_official_free_history_claim` | False | False | False | False | False |
| `borrow_data_present` | False | False | False | False | False |
| `ssr_data_present` | False | False | False | False | False |
| `execution_truth` | False | False | False | False | False |
| `requires_availability_lag_assumption` | True | True | True | True | True |
| `same_day_intraday_causal_claim_allowed` | False | False | False | False | False |
| `prohibited_without_asof_filter` | True | True | True | True | True |
| `contains_future_information_without_event_filter` | True | True | True | True | True |
| `short_quality_state` | review_finra_pre_2021_short_interest_semantics | review_finra_pre_2021_short_interest_semantics | review_finra_pre_2021_short_interest_semantics | review_finra_pre_2021_short_interest_semantics | review_finra_pre_2021_short_interest_semantics |
| `valid_for_event_context_candidate` | True | True | True | True | True |
| `valid_for_ml_feature_candidate` | False | False | False | False | False |
| `valid_for_backtest_context_candidate` | True | True | True | True | True |
| `valid_for_state_component_candidate` | True | True | True | True | True |
| `valid_for_rl_training_direct` | False | False | False | False | False |
| `source_root` | E:/TSIS/data/short_review/finra_short | E:/TSIS/data/short_review/finra_short | E:/TSIS/data/short_review/finra_short | E:/TSIS/data/short_review/finra_short | E:/TSIS/data/short_review/finra_short |
| `source_file` | E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet | E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet | E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet | E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet | E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet |
| `source_file_relative_path` | artifacts/short_interest_all_biweekly_finra.parquet | artifacts/short_interest_all_biweekly_finra.parquet | artifacts/short_interest_all_biweekly_finra.parquet | artifacts/short_interest_all_biweekly_finra.parquet | artifacts/short_interest_all_biweekly_finra.parquet |
| `source_file_row_number` | 45059 | 47817 | 53620 | 3333 | 16230 |
| `instrument_master_build_run_id` | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z |
| `instrument_master_schema_version` | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 |
| `full_universe_claim` | False | False | False | False | False |
| `materialization_scope` | short_and_short_review_source_scoped_context_v0_1 | short_and_short_review_source_scoped_context_v0_1 | short_and_short_review_source_scoped_context_v0_1 | short_and_short_review_source_scoped_context_v0_1 | short_and_short_review_source_scoped_context_v0_1 |
| `quality_policy_version` | short_context_table_policy_v0_1 | short_context_table_policy_v0_1 | short_context_table_policy_v0_1 | short_context_table_policy_v0_1 | short_context_table_policy_v0_1 |
| `schema_version` | short_context_table_v0_1 | short_context_table_v0_1 | short_context_table_v0_1 | short_context_table_v0_1 | short_context_table_v0_1 |
| `build_run_id` | short_context_table_v0_1_20260626T215417Z | short_context_table_v0_1_20260626T215417Z | short_context_table_v0_1_20260626T215417Z | short_context_table_v0_1_20260626T215417Z | short_context_table_v0_1_20260626T215417Z |
| `created_at_utc` | 2026-06-26T21:54:17.194757+00:00 | 2026-06-26T21:54:17.194757+00:00 | 2026-06-26T21:54:17.194757+00:00 | 2026-06-26T21:54:17.194757+00:00 | 2026-06-26T21:54:17.194757+00:00 |
| `source_system` | finra_official_free | finra_official_free | finra_official_free | finra_official_free | finra_official_free |
| `observation_family` | short_interest | short_interest | short_interest | short_interest | short_interest |
| `observation_year` | 2017 | 2017 | 2017 | 2017 | 2017 |

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
