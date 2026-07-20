# corporate_actions_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Splits/dividends/ticker changes from reference/additional. |
| operational_use | Corporate-action context, price-view support, event context. |
| exclusions | Does not solve full economic continuity across ticker changes. |

## Source

| item | value |
| --- | --- |
| dataset_id | `corporate_actions_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\corporate_actions_table\corporate_actions_table_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\corporate_actions_table\corporate_actions_table_v0_1.parquet` |
| declared_rows_in_status_matrix | 104,757 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 104757 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 36 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `corporate_action_id` | `string` |
| 1 | `instrument_id` | `string` |
| 2 | `ticker` | `string` |
| 3 | `action_type` | `string` |
| 4 | `action_date` | `timestamp[us]` |
| 5 | `action_year` | `int32` |
| 6 | `source_system` | `string` |
| 7 | `source_dataset` | `string` |
| 8 | `source_root` | `string` |
| 9 | `source_priority` | `int32` |
| 10 | `source_event_id` | `string` |
| 11 | `is_reference_primary_source` | `bool` |
| 12 | `is_additional_secondary_source` | `bool` |
| 13 | `split_from` | `double` |
| 14 | `split_to` | `double` |
| 15 | `split_ratio` | `double` |
| 16 | `cash_amount` | `double` |
| 17 | `currency` | `string` |
| 18 | `declaration_date` | `timestamp[us]` |
| 19 | `ex_dividend_date` | `timestamp[us]` |
| 20 | `pay_date` | `timestamp[us]` |
| 21 | `record_date` | `timestamp[us]` |
| 22 | `dividend_type` | `string` |
| 23 | `dividend_frequency` | `int32` |
| 24 | `ticker_change_date` | `timestamp[us]` |
| 25 | `ticker_change_ticker` | `string` |
| 26 | `event_name` | `string` |
| 27 | `source_ingested_utc` | `string` |
| 28 | `valid_from` | `timestamp[us]` |
| 29 | `valid_to` | `timestamp[us]` |
| 30 | `within_instrument_valid_window` | `bool` |
| 31 | `instrument_master_schema_version` | `string` |
| 32 | `instrument_master_build_run_id` | `string` |
| 33 | `build_run_id` | `string` |
| 34 | `schema_version` | `string` |
| 35 | `created_at_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `corporate_action_id` | 3d70dd8f850a726a3fad29392d88ebbffcec43a08c52f71cbbb9f7413c1abfa7 | d9687331795e4f23eb701714416bed01c0a05a0657878ceca5c4486f566226ff | 93841aeda6bf4943f2bd9398a2662b24f82ae969c0600db89cac210568f90f02 | d955404ab2b0f37772dd3dd4d8852eb953134a0a80ef9c0acfb0262da9bdc53b | 0729985cbfcfbc84b3c60755b7771c1341162053db115cc2bf56f44069f1e484 |
| `instrument_id` | figi_share_class:BBG00ZKGK109 | figi_share_class:BBG00ZKGK109 | figi_share_class:BBG001S6DRN4 | figi_share_class:BBG001S6DRN4 | figi_share_class:BBG001S6DRN4 |
| `ticker` | AAGR | AAGR | AAIC | AAIC | AAIC |
| `action_type` | ticker_change | ticker_change | split | split | dividend |
| `action_date` | 1969-12-31T00:00:00 | 1969-12-31T00:00:00 | 2009-10-07T00:00:00 | 2009-10-07T00:00:00 | 2010-03-29T00:00:00 |
| `action_year` | 1969 | 1969 | 2009 | 2009 | 2010 |
| `source_system` | reference | additional | reference | additional | additional |
| `source_dataset` | events | ticker_events | splits | splits | dividends |
| `source_root` | E:/TSIS/data/reference/events | E:/TSIS/data/additional/corporate_actions/ticker_events | E:/TSIS/data/reference/splits | E:/TSIS/data/additional/corporate_actions/splits | E:/TSIS/data/additional/corporate_actions/dividends |
| `source_priority` | 1 | 2 | 1 | 2 | 2 |
| `source_event_id` | 111fc254d288f55a3d567a2801278967aecea4496db812197615d94d98ed9e12 | a3600b6b1cb93683a749ed3f090028d4a63f4db3b9995b34f248dca4767c5122 | E801b7d99d0d4dbb65401d5309ef09db1700a93d4262f0b28996ea8a78fbbe1f6 | E801b7d99d0d4dbb65401d5309ef09db1700a93d4262f0b28996ea8a78fbbe1f6 | Ed90f993b6345fda6f73ad530a8aad3e2d3eed49e87109190882a62972c895edc |
| `is_reference_primary_source` | True | False | True | False | False |
| `is_additional_secondary_source` | False | True | False | True | True |
| `split_from` |  |  | 20.0 | 20.0 |  |
| `split_to` |  |  | 1.0 | 1.0 |  |
| `split_ratio` |  |  | 0.05 | 0.05 |  |
| `cash_amount` |  |  |  |  | 0.35 |
| `currency` |  |  |  |  | USD |
| `declaration_date` |  |  |  |  |  |
| `ex_dividend_date` |  |  |  |  | 2010-03-29T00:00:00 |
| `pay_date` |  |  |  |  | 2010-04-30T00:00:00 |
| `record_date` |  |  |  |  | 2010-03-31T00:00:00 |
| `dividend_type` |  |  |  |  | CD |
| `dividend_frequency` |  |  |  |  | 4 |
| `ticker_change_date` | 1969-12-31T00:00:00 | 1969-12-31T00:00:00 |  |  |  |
| `ticker_change_ticker` | AAGR | AAGR |  |  |  |
| `event_name` | AFRICAN AGRI HLDGS INC | AFRICAN AGRI HLDGS INC |  |  |  |
| `source_ingested_utc` | 2026-03-11T10:17:40.852974+00:00 | 2026-04-05T18:21:09.264626+00:00 | 2026-03-11T10:17:41.142742+00:00 | 2026-04-05T18:21:08.977348+00:00 | 2026-04-05T18:21:09.138354+00:00 |
| `valid_from` | 2023-12-07T00:00:00 | 2023-12-07T00:00:00 | 2020-10-26T00:00:00 | 2020-10-26T00:00:00 | 2020-10-26T00:00:00 |
| `valid_to` | 2024-09-25T00:00:00 | 2024-09-25T00:00:00 | 2023-12-14T00:00:00 | 2023-12-14T00:00:00 | 2023-12-14T00:00:00 |
| `within_instrument_valid_window` | False | False | False | False | False |
| `instrument_master_schema_version` | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 |
| `instrument_master_build_run_id` | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z |
| `build_run_id` | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z |
| `schema_version` | corporate_actions_table_v0_1 | corporate_actions_table_v0_1 | corporate_actions_table_v0_1 | corporate_actions_table_v0_1 | corporate_actions_table_v0_1 |
| `created_at_utc` | 2026-06-22T14:48:45.682188+00:00 | 2026-06-22T14:48:45.682188+00:00 | 2026-06-22T14:48:45.682188+00:00 | 2026-06-22T14:48:45.682188+00:00 | 2026-06-22T14:48:45.682188+00:00 |

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
