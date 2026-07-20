# halts_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Nasdaq/NYSE halts and SEC suspensions from halts_v0_1. |
| operational_use | Event interruption context, halt masks, date/intraday halt state. |
| exclusions | No decision-time availability model, no live latency contract; review/bad rows preserved. |

## Source

| item | value |
| --- | --- |
| dataset_id | `halts_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\halts_table\halts_table_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\halts_table\halts_table_v0_1.parquet` |
| declared_rows_in_status_matrix | 133,116 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 133116 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 50 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `halt_event_id` | `string` |
| 1 | `source_event_key` | `string` |
| 2 | `source_row_number` | `int64` |
| 3 | `duplicate_source_event_key` | `bool` |
| 4 | `source_dataset_id` | `string` |
| 5 | `source` | `string` |
| 6 | `source_priority` | `int64` |
| 7 | `ticker` | `string` |
| 8 | `issuer_name` | `string` |
| 9 | `listing_exchange` | `string` |
| 10 | `halt_date` | `timestamp[ns]` |
| 11 | `halt_start_et` | `timestamp[ns]` |
| 12 | `resume_quote_et` | `timestamp[ns]` |
| 13 | `resume_trade_et` | `timestamp[ns]` |
| 14 | `halt_code` | `string` |
| 15 | `halt_type` | `string` |
| 16 | `raw_reason` | `string` |
| 17 | `release_no` | `string` |
| 18 | `item_link` | `string` |
| 19 | `url_source` | `string` |
| 20 | `is_sec_suspension` | `bool` |
| 21 | `halt_event_state` | `string` |
| 22 | `event_granularity` | `string` |
| 23 | `quality_state` | `string` |
| 24 | `intraday_consumption_state` | `string` |
| 25 | `source_allowed` | `bool` |
| 26 | `has_ticker` | `bool` |
| 27 | `has_halt_date` | `bool` |
| 28 | `has_halt_start_et` | `bool` |
| 29 | `has_resume_quote_et` | `bool` |
| 30 | `has_resume_trade_et` | `bool` |
| 31 | `future_date_flag` | `bool` |
| 32 | `timestamp_order_review_flag` | `bool` |
| 33 | `parse_suspect_flag` | `bool` |
| 34 | `missing_core_event_flag` | `bool` |
| 35 | `valid_for_event_engine` | `bool` |
| 36 | `valid_for_intraday_mask` | `bool` |
| 37 | `valid_for_date_context` | `bool` |
| 38 | `valid_for_backtest_event_mask_candidate` | `bool` |
| 39 | `valid_for_ml_flagged_candidate` | `bool` |
| 40 | `valid_for_execution_context_candidate` | `bool` |
| 41 | `prohibited_as_alpha` | `bool` |
| 42 | `requires_decision_time_availability_contract` | `bool` |
| 43 | `visual_case_bucket` | `string` |
| 44 | `market_overlay_state` | `string` |
| 45 | `source_master_path` | `string` |
| 46 | `source_master_sha256` | `string` |
| 47 | `schema_version` | `string` |
| 48 | `build_run_id` | `string` |
| 49 | `created_at_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `halt_event_id` | ecd42f826c5d081c67bebbc6dd3ed0de4bce4c664a0bebf4c882363cd4aa367d | 60e838076f68ae31ca270bcb319df147317496d76e07a60939c1875cffab86e7 | 4bf82e46948e5eb4ad666165c6d9853f4d95b3fbddbebd0509e9b333c476b68d | 2fd13c269dda8ff8214aa1a16b5af8e3e685fa53cbe588e1da7d5232f2e5372e | 78cd01f75543fed0da42dd161e1617391299c436f37e2dcf1617eaa77af1a407 |
| `source_event_key` | 06f1c724b97a55a14c9bb0727d10a5a338409055524afa4fc6bcab20696ef9f5 | fe2e73cb0cd4517eac30d5e48f8069c5ee51fe8b3335648b06140568468b52d4 | 59c20a05702e5a4b4a4169c1eb3accf71d4d16ae4204a641a3db7439790756b2 | ed280f35079042b6980a6d6bacf9772e371f71187fd120a1ae7010de7ff68059 | 853fce61a12bfcb7153e937e4a139d99a811470aeaef5cf388cfc3c303f819c4 |
| `source_row_number` | 0 | 1 | 2 | 3 | 4 |
| `duplicate_source_event_key` | False | False | False | False | False |
| `source_dataset_id` | halts_v0_1 | halts_v0_1 | halts_v0_1 | halts_v0_1 | halts_v0_1 |
| `source` | sec | sec | sec | sec | sec |
| `source_priority` | 1 | 1 | 1 | 1 | 1 |
| `ticker` |  |  |  |  |  |
| `issuer_name` | Garcis U.S.A., Inc. | Environmental Chemicals Group, Inc. | The Enstar Group, Inc. | Lanstar Semiconductor, Inc. | Comparator Systems Corp. |
| `listing_exchange` |  |  |  |  |  |
| `halt_date` | 1995-10-13T00:00:00 | 1995-12-12T00:00:00 | 1996-03-29T00:00:00 | 1996-05-03T00:00:00 | 1996-05-14T00:00:00 |
| `halt_start_et` |  |  |  |  |  |
| `resume_quote_et` |  |  |  |  |  |
| `resume_trade_et` |  |  |  |  |  |
| `halt_code` | SEC | SEC | SEC | SEC | SEC |
| `halt_type` | SEC suspension | SEC suspension | SEC suspension | SEC suspension | SEC suspension |
| `raw_reason` | SEC suspension | SEC suspension | SEC suspension | SEC suspension | SEC suspension |
| `release_no` | 34-36366 | 34-36571 | 34-37043 | 34-37166 | 34-37209 |
| `item_link` | https://www.sec.gov/files/litigation/admin/3436366.txt | https://www.sec.gov/enforcement-litigation/trading-suspensions/34-36571 | https://www.sec.gov/files/litigation/admin/3437043.txt | https://www.sec.gov/files/litigation/admin/3437166.txt | https://www.sec.gov/files/litigation/admin/3437209.txt |
| `url_source` | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 | https://www.sec.gov/enforcement-litigation/trading-suspensions?page=13 |
| `is_sec_suspension` | True | True | True | True | True |
| `halt_event_state` | regulatory_context_only | regulatory_context_only | regulatory_context_only | regulatory_context_only | regulatory_context_only |
| `event_granularity` | regulatory_context | regulatory_context | regulatory_context | regulatory_context | regulatory_context |
| `quality_state` | good | good | good | good | good |
| `intraday_consumption_state` | regulatory_context_only | regulatory_context_only | regulatory_context_only | regulatory_context_only | regulatory_context_only |
| `source_allowed` | True | True | True | True | True |
| `has_ticker` | False | False | False | False | False |
| `has_halt_date` | True | True | True | True | True |
| `has_halt_start_et` | False | False | False | False | False |
| `has_resume_quote_et` | False | False | False | False | False |
| `has_resume_trade_et` | False | False | False | False | False |
| `future_date_flag` | False | False | False | False | False |
| `timestamp_order_review_flag` | False | False | False | False | False |
| `parse_suspect_flag` | False | False | False | False | False |
| `missing_core_event_flag` | False | False | False | False | False |
| `valid_for_event_engine` | True | True | True | True | True |
| `valid_for_intraday_mask` | False | False | False | False | False |
| `valid_for_date_context` | True | True | True | True | True |
| `valid_for_backtest_event_mask_candidate` | False | False | False | False | False |
| `valid_for_ml_flagged_candidate` | True | True | True | True | True |
| `valid_for_execution_context_candidate` | False | False | False | False | False |
| `prohibited_as_alpha` | True | True | True | True | True |
| `requires_decision_time_availability_contract` | True | True | True | True | True |
| `visual_case_bucket` | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 |
| `market_overlay_state` | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 | not_materialized_in_halts_table_v0_1 |
| `source_master_path` | E:/TSIS/data/Halts/processed/halts_master_multisource.parquet | E:/TSIS/data/Halts/processed/halts_master_multisource.parquet | E:/TSIS/data/Halts/processed/halts_master_multisource.parquet | E:/TSIS/data/Halts/processed/halts_master_multisource.parquet | E:/TSIS/data/Halts/processed/halts_master_multisource.parquet |
| `source_master_sha256` | f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213 | f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213 | f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213 | f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213 | f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213 |
| `schema_version` | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 |
| `build_run_id` | halts_table_v0_1_20260625T191305Z | halts_table_v0_1_20260625T191305Z | halts_table_v0_1_20260625T191305Z | halts_table_v0_1_20260625T191305Z | halts_table_v0_1_20260625T191305Z |
| `created_at_utc` | 2026-06-25T19:13:05.462059+00:00 | 2026-06-25T19:13:05.462059+00:00 | 2026-06-25T19:13:05.462059+00:00 | 2026-06-25T19:13:05.462059+00:00 | 2026-06-25T19:13:05.462059+00:00 |

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
