# instrument_master_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | LT1B universe identity snapshot/window. |
| operational_use | Identity context, event/backtest/materialization scope with flags. |
| exclusions | Not final lifecycle engine; no daily PTI market-cap reconstruction. |

## Source

| item | value |
| --- | --- |
| dataset_id | `instrument_master_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet` |
| declared_rows_in_status_matrix | 4,824 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 4824 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 53 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `instrument_id` | `string` |
| 1 | `ticker` | `string` |
| 2 | `identity_resolution_level` | `string` |
| 3 | `ticker_identity_scope` | `string` |
| 4 | `valid_from` | `timestamp[us]` |
| 5 | `valid_to` | `timestamp[us]` |
| 6 | `name` | `string` |
| 7 | `market` | `string` |
| 8 | `locale` | `string` |
| 9 | `primary_exchange` | `string` |
| 10 | `ticker_type_code` | `string` |
| 11 | `ticker_type_description` | `string` |
| 12 | `is_common_stock` | `bool` |
| 13 | `active_in_reference` | `bool` |
| 14 | `currency_name` | `string` |
| 15 | `cik` | `string` |
| 16 | `composite_figi` | `string` |
| 17 | `share_class_figi` | `string` |
| 18 | `exchange_name` | `string` |
| 19 | `exchange_acronym` | `string` |
| 20 | `exchange_mic` | `string` |
| 21 | `exchange_operating_mic` | `string` |
| 22 | `overview_request_date` | `timestamp[us]` |
| 23 | `overview_market_cap` | `double` |
| 24 | `overview_sic_code` | `string` |
| 25 | `overview_sic_description` | `string` |
| 26 | `overview_list_date` | `timestamp[us]` |
| 27 | `overview_ticker_root` | `string` |
| 28 | `overview_weighted_shares_outstanding` | `int64` |
| 29 | `is_lt1b_operational` | `bool` |
| 30 | `lt1b_first_seen_date` | `timestamp[us]` |
| 31 | `lt1b_last_observed_date` | `timestamp[us]` |
| 32 | `lt1b_anchor_date_used` | `timestamp[us]` |
| 33 | `lt1b_status_rebuilt` | `string` |
| 34 | `lt1b_classification_1b` | `string` |
| 35 | `lt1b_classification_reason_1b` | `string` |
| 36 | `lt1b_market_cap_t` | `double` |
| 37 | `lt1b_is_small_cap_t` | `bool` |
| 38 | `lt1b_shares_source` | `string` |
| 39 | `lt1b_shares_observed_date` | `timestamp[us]` |
| 40 | `lt1b_shares_age_days` | `double` |
| 41 | `has_reference_events` | `bool` |
| 42 | `ticker_change_event_count` | `int64` |
| 43 | `first_ticker_change_date` | `timestamp[us]` |
| 44 | `latest_ticker_change_date` | `timestamp[us]` |
| 45 | `reference_snapshot_date` | `timestamp[us]` |
| 46 | `reference_snapshot_timing` | `string` |
| 47 | `reference_last_updated_utc` | `string` |
| 48 | `source_reference_root` | `string` |
| 49 | `source_lt1b_universe_path` | `string` |
| 50 | `build_run_id` | `string` |
| 51 | `schema_version` | `string` |
| 52 | `created_at_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `instrument_id` | cik_ticker:0001853138:AACT | figi_share_class:BBG00ZKGK109 | figi_share_class:BBG001S6DRN4 | figi_share_class:BBG003PNL145 | figi_share_class:BBG001S5N8T1 |
| `ticker` | AACT | AAGR | AAIC | AAMC | AAME |
| `identity_resolution_level` | cik_ticker | share_class_figi | share_class_figi | share_class_figi | share_class_figi |
| `ticker_identity_scope` | lt1b_ticker_grain_v0_1 | lt1b_ticker_grain_v0_1 | lt1b_ticker_grain_v0_1 | lt1b_ticker_grain_v0_1 | lt1b_ticker_grain_v0_1 |
| `valid_from` | 2023-06-12T00:00:00 | 2023-12-07T00:00:00 | 2020-10-26T00:00:00 | 2014-08-15T00:00:00 | 2016-10-25T00:00:00 |
| `valid_to` | 2025-09-24T00:00:00 | 2024-09-25T00:00:00 | 2023-12-14T00:00:00 | 2024-09-16T00:00:00 | 2026-03-09T00:00:00 |
| `name` | Ares Acquisition Corporation II | African Agriculture Holdings Inc. Common Stock | Arlington Asset Investment Corp. | Altisource Asset Mgmt Corp | Atlantic American Corp |
| `market` | stocks | stocks | stocks | stocks | stocks |
| `locale` | us | us | us | us | us |
| `primary_exchange` | XNYS | XNAS | XNYS | XASE | XNAS |
| `ticker_type_code` | CS | CS | CS | CS | CS |
| `ticker_type_description` | Common Stock | Common Stock | Common Stock | Common Stock | Common Stock |
| `is_common_stock` | True | True | True | True | True |
| `active_in_reference` | True | True | True | True | True |
| `currency_name` | usd | usd | usd | usd | usd |
| `cik` | 0001853138 | 0001848898 | 0001209028 | 0001555074 | 0000008177 |
| `composite_figi` |  | BBG00ZKGK0R2 | BBG000BD1373 | BBG003PNL136 | BBG000B9XB24 |
| `share_class_figi` |  | BBG00ZKGK109 | BBG001S6DRN4 | BBG003PNL145 | BBG001S5N8T1 |
| `exchange_name` | New York Stock Exchange | Nasdaq | New York Stock Exchange | NYSE American, LLC | Nasdaq |
| `exchange_acronym` |  |  |  | AMEX |  |
| `exchange_mic` | XNYS | XNAS | XNYS | XASE | XNAS |
| `exchange_operating_mic` | XNYS | XNAS | XNYS | XNYS | XNAS |
| `overview_request_date` | 2025-09-24T00:00:00 | 2024-09-25T00:00:00 | 2023-12-13T00:00:00 | 2024-09-16T00:00:00 | 2026-03-09T00:00:00 |
| `overview_market_cap` | 587048666.88 | 7673141.658 | 137081993.84 | 3193140.0 | 56500321.56 |
| `overview_sic_code` | 7373 | 0100 | 6798 | 6500 | 6311 |
| `overview_sic_description` | SERVICES-COMPUTER INTEGRATED SYSTEMS DESIGN |  | REAL ESTATE INVESTMENT TRUSTS | REAL ESTATE | LIFE INSURANCE |
| `overview_list_date` | 2023-06-12T00:00:00 | 2023-12-07T00:00:00 | 1997-12-23T00:00:00 | 2012-12-12T00:00:00 | 1973-01-02T00:00:00 |
| `overview_ticker_root` | AACT | AAGR | AAIC | AAMC | AAME |
| `overview_weighted_shares_outstanding` | 61859712 | 57866830 | 28322726 | 2554512 | 20397228 |
| `is_lt1b_operational` | True | True | True | True | True |
| `lt1b_first_seen_date` | 2023-06-12T00:00:00 | 2023-12-07T00:00:00 | 2020-10-26T00:00:00 | 2014-08-15T00:00:00 | 2016-10-25T00:00:00 |
| `lt1b_last_observed_date` | 2025-09-24T00:00:00 | 2024-09-25T00:00:00 | 2023-12-14T00:00:00 | 2024-09-16T00:00:00 | 2026-03-09T00:00:00 |
| `lt1b_anchor_date_used` | 2025-09-24T00:00:00 | 2024-09-25T00:00:00 | 2023-12-13T00:00:00 | 2024-09-16T00:00:00 | 2026-03-06T00:00:00 |
| `lt1b_status_rebuilt` | inactive | inactive | inactive | inactive | active |
| `lt1b_classification_1b` | inactive_died_lt_1b | inactive_died_lt_1b | inactive_died_lt_1b | inactive_died_lt_1b | active_lt_1b_last_classifiable |
| `lt1b_classification_reason_1b` | inactive_and_market_cap_t_lt_1b | inactive_and_market_cap_t_lt_1b | inactive_and_market_cap_t_lt_1b | inactive_and_market_cap_t_lt_1b | active_and_market_cap_t_lt_1b |
| `lt1b_market_cap_t` | 526418750.845 | 3765133.14255 | 141536120.0 | 3193140.0 | 53440140.0 |
| `lt1b_is_small_cap_t` | True | True | True | True | True |
| `lt1b_shares_source` | diluted | diluted | diluted | diluted | diluted |
| `lt1b_shares_observed_date` | 2025-08-12T00:00:00 | 2024-05-20T00:00:00 | 2023-11-14T00:00:00 | 2024-08-14T00:00:00 | 2025-11-14T00:00:00 |
| `lt1b_shares_age_days` | 43.0 | 128.0 | 29.0 | 33.0 | 112.0 |
| `has_reference_events` | False | True | False | False | True |
| `ticker_change_event_count` | 0 | 1 | 0 | 0 | 1 |
| `first_ticker_change_date` |  | 1969-12-31T00:00:00 |  |  | 2003-09-10T00:00:00 |
| `latest_ticker_change_date` |  | 1969-12-31T00:00:00 |  |  | 2003-09-10T00:00:00 |
| `reference_snapshot_date` | 2025-09-24T00:00:00 | 2024-09-25T00:00:00 | 2023-12-13T00:00:00 | 2024-09-16T00:00:00 | 2026-03-04T00:00:00 |
| `reference_snapshot_timing` | exact_anchor | exact_anchor | exact_anchor | exact_anchor | before_anchor |
| `reference_last_updated_utc` | 2025-09-25T06:05:34.542055915Z | 2024-12-03T20:10:24.459777Z | 2024-12-03T20:07:18.962586Z | 2024-12-03T20:10:19.261244Z | 2026-03-05T07:07:10.591434407Z |
| `source_reference_root` | E:/TSIS/data/reference | E:/TSIS/data/reference | E:/TSIS/data/reference | E:/TSIS/data/reference | E:/TSIS/data/reference |
| `source_lt1b_universe_path` | C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active... | C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active... | C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active... | C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active... | C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active... |
| `build_run_id` | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z |
| `schema_version` | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 | instrument_master_v0_1 |
| `created_at_utc` | 2026-06-21T14:57:25.220444+00:00 | 2026-06-21T14:57:25.220444+00:00 | 2026-06-21T14:57:25.220444+00:00 | 2026-06-21T14:57:25.220444+00:00 | 2026-06-21T14:57:25.220444+00:00 |

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
