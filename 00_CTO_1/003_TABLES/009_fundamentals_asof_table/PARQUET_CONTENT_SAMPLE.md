# fundamentals_asof_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Additional financial statement rows with filing_date as as_of_date; ratios and standalone financial_v0_1 excluded. |
| operational_use | Filing-date-aware fundamental context after explicit as-of join. |
| exclusions | Not a latest-before-event snapshot; not ratios/market-cap/float authority; not direct ML/RL table. |

## Source

| item | value |
| --- | --- |
| dataset_id | `fundamentals_asof_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\fundamentals_asof_table_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\fundamentals_asof_table\fundamentals_asof_table_v0_1\statement_family=balance_sheets\as_of_year=2010\data_0.parquet` |
| declared_rows_in_status_matrix | 621,756 |
| declared_file_or_partition_count_in_status_matrix | 51 |
| physical_parquet_files_seen | 51 |
| physical_rows_from_parquet_metadata | 621756 |
| physical_row_groups_seen | 51 |
| sample_physical_columns | 111 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `fundamental_asof_id` | `string` |
| 1 | `ticker` | `string` |
| 2 | `instrument_id` | `string` |
| 3 | `source_dataset_id` | `string` |
| 4 | `source_subblock` | `string` |
| 5 | `period_end` | `date32[day]` |
| 6 | `filing_date` | `date32[day]` |
| 7 | `as_of_date` | `date32[day]` |
| 8 | `fiscal_year` | `int64` |
| 9 | `fiscal_quarter` | `int64` |
| 10 | `timeframe` | `string` |
| 11 | `cik` | `string` |
| 12 | `source_tickers` | `string` |
| 13 | `instrument_master_ticker_present` | `bool` |
| 14 | `instrument_identity_temporal_match` | `bool` |
| 15 | `instrument_identity_state` | `string` |
| 16 | `is_common_stock` | `bool` |
| 17 | `is_lt1b_operational` | `bool` |
| 18 | `lt1b_classification_1b` | `string` |
| 19 | `fundamental_quality_state` | `string` |
| 20 | `valid_for_event_context_candidate` | `bool` |
| 21 | `valid_for_ml_feature_candidate` | `bool` |
| 22 | `valid_for_backtest_context_candidate` | `bool` |
| 23 | `valid_for_state_component_candidate` | `bool` |
| 24 | `valid_for_rl_training_direct` | `bool` |
| 25 | `as_of_semantics` | `string` |
| 26 | `period_end_is_availability_date` | `bool` |
| 27 | `requires_event_time_filter` | `bool` |
| 28 | `prohibited_without_asof_filter` | `bool` |
| 29 | `contains_future_information_without_event_filter` | `bool` |
| 30 | `ratios_excluded_from_core_v0_1` | `bool` |
| 31 | `standalone_financial_root_excluded_from_core_v0_1` | `bool` |
| 32 | `source_root` | `string` |
| 33 | `source_file` | `string` |
| 34 | `source_file_relative_path` | `string` |
| 35 | `source_file_row_number` | `int64` |
| 36 | `source_path_ticker` | `string` |
| 37 | `source_empty_sentinel` | `bool` |
| 38 | `_dataset` | `string` |
| 39 | `_ingested_utc` | `string` |
| 40 | `instrument_master_build_run_id` | `string` |
| 41 | `instrument_master_schema_version` | `string` |
| 42 | `full_universe_claim` | `bool` |
| 43 | `materialization_scope` | `string` |
| 44 | `quality_policy_version` | `string` |
| 45 | `schema_version` | `string` |
| 46 | `build_run_id` | `string` |
| 47 | `created_at_utc` | `string` |
| 48 | `revenue` | `double` |
| 49 | `cost_of_revenue` | `double` |
| 50 | `gross_profit` | `double` |
| 51 | `selling_general_administrative` | `double` |
| 52 | `other_operating_expenses` | `double` |
| 53 | `total_operating_expenses` | `double` |
| 54 | `operating_income` | `double` |
| 55 | `interest_expense` | `double` |
| 56 | `other_income_expense` | `double` |
| 57 | `total_other_income_expense` | `double` |
| 58 | `income_before_income_taxes` | `double` |
| 59 | `income_taxes` | `double` |
| 60 | `consolidated_net_income_loss` | `double` |
| 61 | `net_income_loss_attributable_common_shareholders` | `double` |
| 62 | `basic_earnings_per_share` | `double` |
| 63 | `diluted_earnings_per_share` | `double` |
| 64 | `basic_shares_outstanding` | `double` |
| 65 | `diluted_shares_outstanding` | `double` |
| 66 | `ebitda` | `double` |
| 67 | `cash_and_equivalents` | `double` |
| 68 | `receivables` | `double` |
| 69 | `inventories` | `double` |
| 70 | `other_current_assets` | `double` |
| 71 | `total_current_assets` | `double` |
| 72 | `property_plant_equipment_net` | `double` |
| 73 | `intangible_assets_net` | `double` |
| 74 | `other_assets` | `double` |
| 75 | `total_assets` | `double` |
| 76 | `accounts_payable` | `double` |
| 77 | `accrued_and_other_current_liabilities` | `double` |
| 78 | `total_current_liabilities` | `double` |
| 79 | `other_noncurrent_liabilities` | `double` |
| 80 | `total_liabilities` | `double` |
| 81 | `common_stock` | `double` |
| 82 | `additional_paid_in_capital` | `double` |
| 83 | `accumulated_other_comprehensive_income` | `double` |
| 84 | `retained_earnings_deficit` | `double` |
| 85 | `other_equity` | `double` |
| 86 | `total_equity_attributable_to_parent` | `double` |
| 87 | `total_equity` | `double` |
| 88 | `total_liabilities_and_equity` | `double` |
| 89 | `long_term_debt_and_capital_lease_obligations` | `double` |
| 90 | `goodwill` | `double` |
| 91 | `debt_current` | `double` |
| 92 | `preferred_stock` | `double` |
| 93 | `other_operating_activities` | `double` |
| 94 | `change_in_other_operating_assets_and_liabilities_net` | `double` |
| 95 | `other_investing_activities` | `double` |
| 96 | `long_term_debt_issuances_repayments` | `double` |
| 97 | `dividends` | `double` |
| 98 | `other_financing_activities` | `double` |
| 99 | `net_income` | `double` |
| 100 | `depreciation_depletion_and_amortization` | `double` |
| 101 | `cash_from_operating_activities_continuing_operations` | `double` |
| 102 | `net_cash_from_operating_activities` | `double` |
| 103 | `purchase_of_property_plant_and_equipment` | `double` |
| 104 | `sale_of_property_plant_and_equipment` | `double` |
| 105 | `net_cash_from_investing_activities_continuing_operations` | `double` |
| 106 | `net_cash_from_investing_activities` | `double` |
| 107 | `net_cash_from_financing_activities_continuing_operations` | `double` |
| 108 | `net_cash_from_financing_activities` | `double` |
| 109 | `change_in_cash_and_equivalents` | `double` |
| 110 | `effect_of_currency_exchange_rate` | `double` |
| 111 | `statement_family` | `string` |
| 112 | `as_of_year` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `fundamental_asof_id` | 165a7c6939af03f42a8315149ff0fb533bd5b77843cdc0fd7bf200b5fbd4d8fa | c960d4e15123db1edaf7e1807701bcac769dd29f1104b2d720d7c48b60ff4827 | 77986f1319f2bc3ac087901d8cdeacd10e9c2425d772206805f6c554b92fb6a2 | ea1e85bae4dc65892d2a193a248a62aea50dc0b651efa0017dce320ee83d9ea7 | 2dae94de26e2193aec76e0f5c52010b35514b9e58e37ae4fbdffbd2157b1959c |
| `ticker` | NBR | NBR | PHR | PHR | PHR |
| `instrument_id` | cik_ticker:0001163739:NBR | cik_ticker:0001163739:NBR |  |  |  |
| `source_dataset_id` | additional_v0_1 | additional_v0_1 | additional_v0_1 | additional_v0_1 | additional_v0_1 |
| `source_subblock` | financials_core | financials_core | financials_core | financials_core | financials_core |
| `period_end` | 2010-06-30 | 2010-09-30 | 2010-03-31 | 2010-06-30 | 2010-09-30 |
| `filing_date` | 2010-08-09 | 2010-11-05 | 2010-05-07 | 2010-08-09 | 2010-11-05 |
| `as_of_date` | 2010-08-09 | 2010-11-05 | 2010-05-07 | 2010-08-09 | 2010-11-05 |
| `fiscal_year` | 2010 | 2010 | 2010 | 2010 | 2010 |
| `fiscal_quarter` | 2 | 3 | 1 | 2 | 3 |
| `timeframe` | quarterly | quarterly | quarterly | quarterly | quarterly |
| `cik` | 0001163739 | 0001163739 | 0001137774 | 0001137774 | 0001137774 |
| `source_tickers` | [NBR] | [NBR] | [PFK, PHR, PRU] | [PFK, PHR, PRU] | [PFK, PHR, PRU] |
| `instrument_master_ticker_present` | True | True | True | True | True |
| `instrument_identity_temporal_match` | True | True | False | False | False |
| `instrument_identity_state` | good_temporal_match | good_temporal_match | review_no_temporal_identity | review_no_temporal_identity | review_no_temporal_identity |
| `is_common_stock` | True | True |  |  |  |
| `is_lt1b_operational` | True | True |  |  |  |
| `lt1b_classification_1b` | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable |  |  |  |
| `fundamental_quality_state` | good_statement_asof | good_statement_asof | review_no_temporal_identity | review_no_temporal_identity | review_no_temporal_identity |
| `valid_for_event_context_candidate` | True | True | False | False | False |
| `valid_for_ml_feature_candidate` | True | True | False | False | False |
| `valid_for_backtest_context_candidate` | True | True | False | False | False |
| `valid_for_state_component_candidate` | True | True | False | False | False |
| `valid_for_rl_training_direct` | False | False | False | False | False |
| `as_of_semantics` | filing_date_available_from_date_only | filing_date_available_from_date_only | filing_date_available_from_date_only | filing_date_available_from_date_only | filing_date_available_from_date_only |
| `period_end_is_availability_date` | False | False | False | False | False |
| `requires_event_time_filter` | True | True | True | True | True |
| `prohibited_without_asof_filter` | True | True | True | True | True |
| `contains_future_information_without_event_filter` | True | True | True | True | True |
| `ratios_excluded_from_core_v0_1` | True | True | True | True | True |
| `standalone_financial_root_excluded_from_core_v0_1` | True | True | True | True | True |
| `source_root` | E:/TSIS/data/additional/financials | E:/TSIS/data/additional/financials | E:/TSIS/data/additional/financials | E:/TSIS/data/additional/financials | E:/TSIS/data/additional/financials |
| `source_file` | E:\TSIS\data\additional\financials\balance_sheets\ticker=NBR\balance_sheets_NBR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=NBR\balance_sheets_NBR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet |
| `source_file_relative_path` | E:\TSIS\data\additional\financials\balance_sheets\ticker=NBR\balance_sheets_NBR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=NBR\balance_sheets_NBR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet | E:\TSIS\data\additional\financials\balance_sheets\ticker=PHR\balance_sheets_PHR.parquet |
| `source_file_row_number` | 0 | 1 | 0 | 1 | 2 |
| `source_path_ticker` | NBR\balance_sheets_NBR.parquet | NBR\balance_sheets_NBR.parquet | PHR\balance_sheets_PHR.parquet | PHR\balance_sheets_PHR.parquet | PHR\balance_sheets_PHR.parquet |
| `source_empty_sentinel` | False | False | False | False | False |
| `_dataset` | balance_sheets | balance_sheets | balance_sheets | balance_sheets | balance_sheets |
| `_ingested_utc` | 2026-04-05T18:31:43.656291+00:00 | 2026-04-05T18:31:43.656291+00:00 | 2026-04-05T18:33:27.743784+00:00 | 2026-04-05T18:33:27.743784+00:00 | 2026-04-05T18:33:27.743784+00:00 |
| `instrument_master_build_run_id` | instrument_master_v0_1_20260621T145725Z | instrument_master_v0_1_20260621T145725Z |  |  |  |
| `instrument_master_schema_version` | instrument_master_v0_1 | instrument_master_v0_1 |  |  |  |
| `full_universe_claim` | False | False | False | False | False |
| `materialization_scope` | additional_financials_core_lt1b_statement_asof_v0_1 | additional_financials_core_lt1b_statement_asof_v0_1 | additional_financials_core_lt1b_statement_asof_v0_1 | additional_financials_core_lt1b_statement_asof_v0_1 | additional_financials_core_lt1b_statement_asof_v0_1 |
| `quality_policy_version` | fundamentals_asof_table_policy_v0_1 | fundamentals_asof_table_policy_v0_1 | fundamentals_asof_table_policy_v0_1 | fundamentals_asof_table_policy_v0_1 | fundamentals_asof_table_policy_v0_1 |
| `schema_version` | fundamentals_asof_table_v0_1 | fundamentals_asof_table_v0_1 | fundamentals_asof_table_v0_1 | fundamentals_asof_table_v0_1 | fundamentals_asof_table_v0_1 |
| `build_run_id` | fundamentals_asof_table_v0_1_20260626T101617Z | fundamentals_asof_table_v0_1_20260626T101617Z | fundamentals_asof_table_v0_1_20260626T101617Z | fundamentals_asof_table_v0_1_20260626T101617Z | fundamentals_asof_table_v0_1_20260626T101617Z |
| `created_at_utc` | 2026-06-26T10:16:17.923065+00:00 | 2026-06-26T10:16:17.923065+00:00 | 2026-06-26T10:16:17.923065+00:00 | 2026-06-26T10:16:17.923065+00:00 | 2026-06-26T10:16:17.923065+00:00 |
| `revenue` |  |  |  |  |  |
| `cost_of_revenue` |  |  |  |  |  |
| `gross_profit` |  |  |  |  |  |
| `selling_general_administrative` |  |  |  |  |  |
| `other_operating_expenses` |  |  |  |  |  |
| `total_operating_expenses` |  |  |  |  |  |
| `operating_income` |  |  |  |  |  |
| `interest_expense` |  |  |  |  |  |
| `other_income_expense` |  |  |  |  |  |
| `total_other_income_expense` |  |  |  |  |  |
| `income_before_income_taxes` |  |  |  |  |  |
| `income_taxes` |  |  |  |  |  |
| `consolidated_net_income_loss` |  |  |  |  |  |
| `net_income_loss_attributable_common_shareholders` |  |  |  |  |  |
| `basic_earnings_per_share` |  |  |  |  |  |
| `diluted_earnings_per_share` |  |  |  |  |  |
| `basic_shares_outstanding` |  |  |  |  |  |
| `diluted_shares_outstanding` |  |  |  |  |  |
| `ebitda` |  |  |  |  |  |
| `cash_and_equivalents` | 747593000.0 | 639683000.0 | 9626000000.0 | 11352000000.0 | 11973000000.0 |
| `receivables` | 762589000.0 | 1002974000.0 |  |  |  |
| `inventories` | 107549000.0 | 142973000.0 |  |  |  |
| `other_current_assets` | 262394000.0 | 647508000.0 |  |  |  |
| `total_current_assets` | 2025408000.0 | 2565924000.0 | 192247000000.0 | 190612000000.0 | 206436000000.0 |
| `property_plant_equipment_net` | 7641563000.0 | 7884874000.0 |  |  |  |
| `intangible_assets_net` |  |  |  |  |  |
| `other_assets` | 669092000.0 | 706503000.0 | 299614000000.0 | 305376000000.0 | 320488000000.0 |
| `total_assets` | 10500141000.0 | 11620728000.0 | 491861000000.0 | 495988000000.0 | 526924000000.0 |
| `accounts_payable` | 255476000.0 | 368780000.0 |  |  |  |
| `accrued_and_other_current_liabilities` | 386787000.0 | 450026000.0 |  |  |  |
| `total_current_liabilities` | 1988082000.0 | 2261520000.0 | 0.0 | 0.0 | 0.0 |
| `other_noncurrent_liabilities` | 918947000.0 | 1002702000.0 | 436468000000.0 | 438569000000.0 | 465482000000.0 |
| `total_liabilities` | 5271732000.0 | 6330970000.0 | 464355000000.0 | 465719000000.0 | 492856000000.0 |
| `common_stock` | 314000.0 | 314000.0 | 6000000.0 | 6000000.0 | 6000000.0 |
| `additional_paid_in_capital` | 2245592000.0 | 2249796000.0 | 23186000000.0 | 23199000000.0 | 23222000000.0 |
| `accumulated_other_comprehensive_income` | 251268000.0 | 277995000.0 | 620000000.0 | 2200000000.0 | 4729000000.0 |
| `retained_earnings_deficit` | 3697007000.0 | 3657400000.0 | 14478000000.0 | 15555000000.0 | 16794000000.0 |
| `other_equity` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| `total_equity_attributable_to_parent` | 5216308000.0 | 5207632000.0 | 27000000000.0 | 29724000000.0 | 33546000000.0 |
| `total_equity` | 5228409000.0 | 5220570000.0 | 27506000000.0 | 30269000000.0 | 34068000000.0 |
| `total_liabilities_and_equity` | 10500141000.0 | 11620728000.0 | 491861000000.0 | 495988000000.0 | 526924000000.0 |
| `long_term_debt_and_capital_lease_obligations` | 2364703000.0 | 3066748000.0 | 27887000000.0 | 27150000000.0 | 27374000000.0 |
| `goodwill` | 164078000.0 | 463427000.0 |  |  |  |
| `debt_current` | 1345819000.0 | 1442714000.0 |  |  |  |
| `preferred_stock` |  |  |  |  |  |
| `other_operating_activities` |  |  |  |  |  |
| `change_in_other_operating_assets_and_liabilities_net` |  |  |  |  |  |
| `other_investing_activities` |  |  |  |  |  |
| `long_term_debt_issuances_repayments` |  |  |  |  |  |
| `dividends` |  |  |  |  |  |
| `other_financing_activities` |  |  |  |  |  |
| `net_income` |  |  |  |  |  |
| `depreciation_depletion_and_amortization` |  |  |  |  |  |
| `cash_from_operating_activities_continuing_operations` |  |  |  |  |  |
| `net_cash_from_operating_activities` |  |  |  |  |  |
| `purchase_of_property_plant_and_equipment` |  |  |  |  |  |
| `sale_of_property_plant_and_equipment` |  |  |  |  |  |
| `net_cash_from_investing_activities_continuing_operations` |  |  |  |  |  |
| `net_cash_from_investing_activities` |  |  |  |  |  |
| `net_cash_from_financing_activities_continuing_operations` |  |  |  |  |  |
| `net_cash_from_financing_activities` |  |  |  |  |  |
| `change_in_cash_and_equivalents` |  |  |  |  |  |
| `effect_of_currency_exchange_rate` |  |  |  |  |  |
| `statement_family` | balance_sheets | balance_sheets | balance_sheets | balance_sheets | balance_sheets |
| `as_of_year` | 2010 | 2010 | 2010 | 2010 | 2010 |

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
