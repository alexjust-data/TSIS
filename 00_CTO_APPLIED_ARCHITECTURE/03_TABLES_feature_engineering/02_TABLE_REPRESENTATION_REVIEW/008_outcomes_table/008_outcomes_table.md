# outcomes_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Next-session daily outcomes for halt-derived event windows x three daily price views. |
| operational_use | Daily post-event labels/outcome research with feature/label separation. |
| exclusions | Daily labels only; not intraday execution outcome, not RL reward, not all event families. |

## Source

| item | value |
| --- | --- |
| dataset_id | `outcomes_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\outcomes_table\outcomes_table_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\outcomes_table\outcomes_table_v0_1.parquet` |
| declared_rows_in_status_matrix | 128,388 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 128388 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 179 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `outcome_id` | `string` |
| 1 | `event_window_id` | `string` |
| 2 | `source_event_id` | `string` |
| 3 | `event_source_dataset_id` | `string` |
| 4 | `event_family` | `string` |
| 5 | `event_type` | `string` |
| 6 | `event_code` | `string` |
| 7 | `event_source` | `string` |
| 8 | `ticker` | `string` |
| 9 | `instrument_id` | `string` |
| 10 | `issuer_name` | `string` |
| 11 | `listing_exchange` | `string` |
| 12 | `event_session_date` | `timestamp[us]` |
| 13 | `outcome_session_date` | `timestamp[us]` |
| 14 | `outcome_horizon` | `string` |
| 15 | `price_view` | `string` |
| 16 | `event_time_utc` | `timestamp[us, tz=Europe/Madrid]` |
| 17 | `resume_trade_utc` | `timestamp[us, tz=Europe/Madrid]` |
| 18 | `event_session_phase` | `string` |
| 19 | `window_role` | `string` |
| 20 | `window_start_utc` | `timestamp[us, tz=Europe/Madrid]` |
| 21 | `window_end_utc` | `timestamp[us, tz=Europe/Madrid]` |
| 22 | `window_duration_minutes` | `double` |
| 23 | `event_window_quality_state` | `string` |
| 24 | `event_window_consumption_state` | `string` |
| 25 | `source_event_quality_state` | `string` |
| 26 | `source_halt_event_state` | `string` |
| 27 | `source_resume_trade_observed` | `bool` |
| 28 | `event_response_end_observed` | `bool` |
| 29 | `calendar` | `string` |
| 30 | `timezone` | `string` |
| 31 | `instrument_identity_temporal_match` | `bool` |
| 32 | `is_common_stock` | `bool` |
| 33 | `is_lt1b_operational` | `bool` |
| 34 | `lt1b_classification_1b` | `string` |
| 35 | `event_master_daily_id` | `string` |
| 36 | `outcome_master_daily_id` | `string` |
| 37 | `event_quality_gate_family` | `string` |
| 38 | `outcome_quality_gate_family` | `string` |
| 39 | `event_daily_source_dataset` | `string` |
| 40 | `outcome_daily_source_dataset` | `string` |
| 41 | `event_daily_source_root` | `string` |
| 42 | `outcome_daily_source_root` | `string` |
| 43 | `event_expected_session` | `bool` |
| 44 | `outcome_expected_session` | `bool` |
| 45 | `event_expected_reason` | `string` |
| 46 | `outcome_expected_reason` | `string` |
| 47 | `event_data_present` | `bool` |
| 48 | `outcome_data_present` | `bool` |
| 49 | `event_missing_expected_data` | `bool` |
| 50 | `outcome_missing_expected_data` | `bool` |
| 51 | `event_source_daily_present` | `bool` |
| 52 | `outcome_source_daily_present` | `bool` |
| 53 | `event_source_adjusted_present` | `bool` |
| 54 | `outcome_source_adjusted_present` | `bool` |
| 55 | `event_open` | `double` |
| 56 | `event_high` | `double` |
| 57 | `event_low` | `double` |
| 58 | `event_close` | `double` |
| 59 | `event_volume` | `double` |
| 60 | `event_vwap` | `double` |
| 61 | `event_source_raw_vwap` | `double` |
| 62 | `event_transaction_count` | `int64` |
| 63 | `event_prior_close` | `double` |
| 64 | `event_gap_pct` | `double` |
| 65 | `event_daily_return_pct` | `double` |
| 66 | `event_intraday_return_pct` | `double` |
| 67 | `event_daily_range_pct` | `double` |
| 68 | `event_dollar_volume` | `double` |
| 69 | `event_rvol_20d` | `double` |
| 70 | `outcome_open` | `double` |
| 71 | `outcome_high` | `double` |
| 72 | `outcome_low` | `double` |
| 73 | `outcome_close` | `double` |
| 74 | `outcome_volume` | `double` |
| 75 | `outcome_vwap` | `double` |
| 76 | `outcome_source_raw_vwap` | `double` |
| 77 | `outcome_transaction_count` | `int64` |
| 78 | `outcome_prior_close` | `double` |
| 79 | `outcome_gap_pct` | `double` |
| 80 | `outcome_daily_return_pct` | `double` |
| 81 | `outcome_intraday_return_pct` | `double` |
| 82 | `outcome_daily_range_pct` | `double` |
| 83 | `outcome_dollar_volume` | `double` |
| 84 | `outcome_rvol_20d` | `double` |
| 85 | `event_future_split_factor` | `double` |
| 86 | `outcome_future_split_factor` | `double` |
| 87 | `event_future_dividend_sum` | `double` |
| 88 | `outcome_future_dividend_sum` | `double` |
| 89 | `event_future_dividend_factor` | `double` |
| 90 | `outcome_future_dividend_factor` | `double` |
| 91 | `event_future_adjustment_factor` | `double` |
| 92 | `outcome_future_adjustment_factor` | `double` |
| 93 | `event_corporate_action_count` | `int32` |
| 94 | `outcome_corporate_action_count` | `int32` |
| 95 | `event_split_action_count` | `int32` |
| 96 | `outcome_split_action_count` | `int32` |
| 97 | `event_dividend_action_count` | `int32` |
| 98 | `outcome_dividend_action_count` | `int32` |
| 99 | `event_ticker_change_action_count` | `int32` |
| 100 | `outcome_ticker_change_action_count` | `int32` |
| 101 | `event_has_split_action` | `bool` |
| 102 | `outcome_has_split_action` | `bool` |
| 103 | `event_has_dividend_action` | `bool` |
| 104 | `outcome_has_dividend_action` | `bool` |
| 105 | `event_has_ticker_change_action` | `bool` |
| 106 | `outcome_has_ticker_change_action` | `bool` |
| 107 | `event_has_any_corporate_action` | `bool` |
| 108 | `outcome_has_any_corporate_action` | `bool` |
| 109 | `event_row_level_price_integrity_state` | `string` |
| 110 | `outcome_row_level_price_integrity_state` | `string` |
| 111 | `event_selected_price_hard_invalid` | `bool` |
| 112 | `outcome_selected_price_hard_invalid` | `bool` |
| 113 | `event_negative_volume` | `bool` |
| 114 | `outcome_negative_volume` | `bool` |
| 115 | `event_daily_backtest_core_row_candidate` | `bool` |
| 116 | `outcome_daily_backtest_core_row_candidate` | `bool` |
| 117 | `event_family_data_quality_verdict` | `string` |
| 118 | `outcome_family_data_quality_verdict` | `string` |
| 119 | `event_family_foundations_completion_status` | `string` |
| 120 | `outcome_family_foundations_completion_status` | `string` |
| 121 | `event_family_visual_inspection_status` | `string` |
| 122 | `outcome_family_visual_inspection_status` | `string` |
| 123 | `event_family_production_use_gate` | `string` |
| 124 | `outcome_family_production_use_gate` | `string` |
| 125 | `event_family_event_consumption_gate` | `string` |
| 126 | `outcome_family_event_consumption_gate` | `string` |
| 127 | `event_gate_quality_policy_version` | `string` |
| 128 | `outcome_gate_quality_policy_version` | `string` |
| 129 | `event_close_to_outcome_open_return_pct` | `double` |
| 130 | `event_close_to_outcome_high_return_pct` | `double` |
| 131 | `event_close_to_outcome_low_return_pct` | `double` |
| 132 | `event_close_to_outcome_close_return_pct` | `double` |
| 133 | `outcome_intraday_open_to_close_return_pct` | `double` |
| 134 | `outcome_intraday_range_pct` | `double` |
| 135 | `label_next_close_positive` | `bool` |
| 136 | `label_next_close_ge_5pct` | `bool` |
| 137 | `label_next_close_ge_10pct` | `bool` |
| 138 | `label_next_close_le_minus_5pct` | `bool` |
| 139 | `label_next_close_le_minus_10pct` | `bool` |
| 140 | `label_next_high_ge_10pct` | `bool` |
| 141 | `label_next_high_ge_20pct` | `bool` |
| 142 | `label_next_low_le_minus_10pct` | `bool` |
| 143 | `label_next_open_ge_5pct` | `bool` |
| 144 | `label_next_open_le_minus_5pct` | `bool` |
| 145 | `outcome_quality_state` | `string` |
| 146 | `valid_for_outcome_research` | `bool` |
| 147 | `valid_for_ml_label_candidate` | `bool` |
| 148 | `valid_for_strategy_label_candidate` | `bool` |
| 149 | `valid_for_backtest_outcome_candidate` | `bool` |
| 150 | `valid_for_rl_reward_candidate` | `bool` |
| 151 | `contains_post_event_information` | `bool` |
| 152 | `prohibited_as_pre_event_feature` | `bool` |
| 153 | `requires_feature_label_separation` | `bool` |
| 154 | `full_universe_claim` | `bool` |
| 155 | `expected_data_calendar_build_run_id` | `string` |
| 156 | `dataset_certification_matrix_build_run_id` | `string` |
| 157 | `corporate_actions_build_run_id` | `string` |
| 158 | `expectation_policy_version` | `string` |
| 159 | `event_daily_quality_policy_version` | `string` |
| 160 | `outcome_daily_quality_policy_version` | `string` |
| 161 | `event_daily_schema_version` | `string` |
| 162 | `outcome_daily_schema_version` | `string` |
| 163 | `event_daily_build_run_id` | `string` |
| 164 | `outcome_daily_build_run_id` | `string` |
| 165 | `source_event_window_materialization_scope` | `string` |
| 166 | `source_event_window_quality_policy_version` | `string` |
| 167 | `source_event_window_schema_version` | `string` |
| 168 | `source_event_window_build_run_id` | `string` |
| 169 | `source_full_universe_claim` | `bool` |
| 170 | `materialization_scope` | `string` |
| 171 | `quality_policy_version` | `string` |
| 172 | `schema_version` | `string` |
| 173 | `build_run_id` | `string` |
| 174 | `created_at_utc` | `string` |
| 175 | `source_event_windows_table_path` | `string` |
| 176 | `source_event_windows_table_sha256` | `string` |
| 177 | `source_master_daily_table_path` | `string` |
| 178 | `source_master_daily_table_tree_sha256` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `outcome_id` | 0aafa38601edd8bc41bf965932b13c3b10fd4502109818c5a1a4c449205a603c | f639813f55992d85897bce7c0590ccfe0555917acad7bfbe59837e370c6de25d | 6ce55e700a79669294c23a9f5439b949849770a3b8f81d506100886b6d44c7ac | 822e73197722ad1c6cbf09badd3e8691896c9bed53b459cc292228e93ab02f0a | 610c1b8885c617b01d6134e9705b4c9dcb9c86c07615f94777ff839c09fca3ae |
| `event_window_id` | cdb1dfbdb8a277fa9ed1618a4cedf6825b5ca56ff8df5c018525c48982606cba | cdb1dfbdb8a277fa9ed1618a4cedf6825b5ca56ff8df5c018525c48982606cba | cdb1dfbdb8a277fa9ed1618a4cedf6825b5ca56ff8df5c018525c48982606cba | 3599b3a7a3df8a036768417b2d1b4bad8a71a7d74f98e2398363cec51d601138 | 3599b3a7a3df8a036768417b2d1b4bad8a71a7d74f98e2398363cec51d601138 |
| `source_event_id` | ee825dc6579df38fa817f076fe86b27bf10c562ef90c82b921a547d2c2956a95 | ee825dc6579df38fa817f076fe86b27bf10c562ef90c82b921a547d2c2956a95 | ee825dc6579df38fa817f076fe86b27bf10c562ef90c82b921a547d2c2956a95 | fbddcd3991e9ef0a54572ebb042703f90c5f16b03d47a85fe9ed3da9f28bc1fb | fbddcd3991e9ef0a54572ebb042703f90c5f16b03d47a85fe9ed3da9f28bc1fb |
| `event_source_dataset_id` | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 | halts_table_v0_1 |
| `event_family` | halt | halt | halt | halt | halt |
| `event_type` | News and resumption pending | News and resumption pending | News and resumption pending | News and resumption pending | News and resumption pending |
| `event_code` | T3 | T3 | T3 | T3 | T3 |
| `event_source` | nasdaq | nasdaq | nasdaq | nasdaq | nasdaq |
| `ticker` | DSS | DSS | DSS | AP | AP |
| `instrument_id` | figi_share_class:BBG001SJTPW3 | figi_share_class:BBG001SJTPW3 | figi_share_class:BBG001SJTPW3 | figi_share_class:BBG001S5NS08 | figi_share_class:BBG001S5NS08 |
| `issuer_name` |  |  |  |  |  |
| `listing_exchange` |  |  |  |  |  |
| `event_session_date` | 2005-01-19T00:00:00 | 2005-01-19T00:00:00 | 2005-01-19T00:00:00 | 2005-01-27T00:00:00 | 2005-01-27T00:00:00 |
| `outcome_session_date` | 2005-01-20T00:00:00 | 2005-01-20T00:00:00 | 2005-01-20T00:00:00 | 2005-01-28T00:00:00 | 2005-01-28T00:00:00 |
| `outcome_horizon` | next_session_regular_daily | next_session_regular_daily | next_session_regular_daily | next_session_regular_daily | next_session_regular_daily |
| `price_view` | adjusted | daily_raw | split_normalized | adjusted | daily_raw |
| `event_time_utc` | 2005-01-19T22:00:38+01:00 | 2005-01-19T22:00:38+01:00 | 2005-01-19T22:00:38+01:00 | 2005-01-27T22:34:52+01:00 | 2005-01-27T22:34:52+01:00 |
| `resume_trade_utc` | 2005-01-19T22:36:12+01:00 | 2005-01-19T22:36:12+01:00 | 2005-01-19T22:36:12+01:00 | 2005-01-28T15:01:49+01:00 | 2005-01-28T15:01:49+01:00 |
| `event_session_phase` | afterhours | afterhours | afterhours | afterhours | afterhours |
| `window_role` | next_session_regular | next_session_regular | next_session_regular | next_session_regular | next_session_regular |
| `window_start_utc` | 2005-01-20T15:30:00+01:00 | 2005-01-20T15:30:00+01:00 | 2005-01-20T15:30:00+01:00 | 2005-01-28T15:30:00+01:00 | 2005-01-28T15:30:00+01:00 |
| `window_end_utc` | 2005-01-20T22:00:00+01:00 | 2005-01-20T22:00:00+01:00 | 2005-01-20T22:00:00+01:00 | 2005-01-28T22:00:00+01:00 | 2005-01-28T22:00:00+01:00 |
| `window_duration_minutes` | 390.0 | 390.0 | 390.0 | 390.0 | 390.0 |
| `event_window_quality_state` | good | good | good | good | good |
| `event_window_consumption_state` | outcome_candidate_window | outcome_candidate_window | outcome_candidate_window | outcome_candidate_window | outcome_candidate_window |
| `source_event_quality_state` | good | good | good | good | good |
| `source_halt_event_state` | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event | good_full_intraday_event |
| `source_resume_trade_observed` | True | True | True | True | True |
| `event_response_end_observed` | False | False | False | False | False |
| `calendar` | XNYS | XNYS | XNYS | XNYS | XNYS |
| `timezone` | America/New_York | America/New_York | America/New_York | America/New_York | America/New_York |
| `instrument_identity_temporal_match` | True | True | True | True | True |
| `is_common_stock` | True | True | True | True | True |
| `is_lt1b_operational` | True | True | True | True | True |
| `lt1b_classification_1b` | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable | active_lt_1b_last_classifiable |
| `event_master_daily_id` | 39bfd9b2e094de276e7c50f3b6ed56249192f9b3db6b65e8710e5196fe0064bf | 5cc0946b0a164a93c967033169cda3a9b5a5878cc6a136333a737bad931e7431 | c7c0d0e8519a694bcb68ee164ff498e0ba05a6044b962232781b063de0c550d8 | c700137d93ea89b735f1662e09a7173b41c66a716a5187b1e1c4574704723794 | f2f989cf9a6ea408cddd2d1db78730a948ce78e900c9bf807d7b7d86a84d2746 |
| `outcome_master_daily_id` | 840a907e6ad6aa8f9e2ad375542f24f082eb92222c354181efd921391f7ac60d | 658f5c2a6a72dadf4525f2af6b9f539687ecf243ebade923c104bd0e37ab288f | 30f327c77e3515fc923556da51f7c7ac3801639eb55da29dbb6c099f1bbc53f6 | ce836bba3bcf1d30500b0c3f8ba12895a32959dcb68003607200b8b7833d5e16 | bfb1f74d851150a36ce96308ac105be1a3d35ec2903e2c0764e33895bfc47bc4 |
| `event_quality_gate_family` | ohlcv_daily_adjusted | daily | ohlcv_daily_adjusted | ohlcv_daily_adjusted | daily |
| `outcome_quality_gate_family` | ohlcv_daily_adjusted | daily | ohlcv_daily_adjusted | ohlcv_daily_adjusted | daily |
| `event_daily_source_dataset` | ohlcv_daily_adjusted | ohlcv_daily | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily |
| `outcome_daily_source_dataset` | ohlcv_daily_adjusted | ohlcv_daily | ohlcv_daily_adjusted | ohlcv_daily_adjusted | ohlcv_daily |
| `event_daily_source_root` | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily |
| `outcome_daily_source_root` | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily_adjusted | E:/TSIS/data/ohlcv_daily |
| `event_expected_session` | True | True | True | True | True |
| `outcome_expected_session` | True | True | True | True | True |
| `event_expected_reason` | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session |
| `outcome_expected_reason` | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session | instrument_valid_window_and_xnys_session |
| `event_data_present` | True | True | True | True | True |
| `outcome_data_present` | True | True | True | True | True |
| `event_missing_expected_data` | False | False | False | False | False |
| `outcome_missing_expected_data` | False | False | False | False | False |
| `event_source_daily_present` | True | True | True | True | True |
| `outcome_source_daily_present` | True | True | True | True | True |
| `event_source_adjusted_present` | True | True | True | True | True |
| `outcome_source_adjusted_present` | True | True | True | True | True |
| `event_open` | 2.62 | 6288.0 | 2.62 | 7.940247861793861 | 13.48 |
| `event_high` | 2.7600000000000002 | 6624.0 | 2.7600000000000002 | 7.975590211327067 | 13.54 |
| `event_low` | 2.6 | 6240.0 | 2.6 | 7.940247861793861 | 13.48 |
| `event_close` | 2.6300000000000003 | 6312.0 | 2.6300000000000003 | 7.957919036560464 | 13.51 |
| `event_volume` | 560.333333 | 560.333333 | 560.333333 | 900.0 | 900.0 |
| `event_vwap` |  | 6466.536 |  |  | 13.5208 |
| `event_source_raw_vwap` | 6466.536 | 6466.536 | 6466.536 | 13.5208 | 13.5208 |
| `event_transaction_count` | 668 | 668 | 668 | 5 | 5 |
| `event_prior_close` | 2.6500000000000004 | 6360.0 | 2.6500000000000004 | 7.975590211327067 | 13.54 |
| `event_gap_pct` | -0.01132075471698124 | -0.01132075471698113 | -0.01132075471698124 | -0.004431314623338123 | -0.004431314623338123 |
| `event_daily_return_pct` | -0.007547169811320753 | -0.007547169811320753 | -0.007547169811320753 | -0.0022156573116690614 | -0.0022156573116690614 |
| `event_intraday_return_pct` | 0.003816793893129944 | 0.003816793893129722 | 0.003816793893129944 | 0.002225519287833766 | 0.002225519287833766 |
| `event_daily_range_pct` | 0.06153846153846154 | 0.06153846153846154 | 0.06153846153846154 | 0.004451038575667532 | 0.004451038575667532 |
| `event_dollar_volume` | 1473.6766657900002 | 3536823.9978960003 | 1473.6766657900002 | 7162.1271329044175 | 12159.0 |
| `event_rvol_20d` | 1.5799040905187467 | 1.5799040905187467 | 1.5799040905187467 | 0.12056737588652482 | 0.12056737588652482 |
| `outcome_open` | 2.98 | 7152.0 | 2.98 | 7.963809428149332 | 13.52 |
| `outcome_high` | 3.0 | 7200.0 | 3.0 | 7.999151777682539 | 13.58 |
| `outcome_low` | 2.74 | 6576.0 | 2.74 | 7.963809428149332 | 13.52 |
| `outcome_close` | 2.8400000000000003 | 6816.0 | 2.8400000000000003 | 7.999151777682539 | 13.58 |
| `outcome_volume` | 1024.416667 | 1024.416667 | 1024.416667 | 200.0 | 200.0 |
| `outcome_vwap` |  | 6810.372 |  |  | 13.55 |
| `outcome_source_raw_vwap` | 6810.372 | 6810.372 | 6810.372 | 13.55 | 13.55 |
| `outcome_transaction_count` | 1302 | 1302 | 1302 | 2 | 2 |
| `outcome_prior_close` | 2.6300000000000003 | 6312.0 | 2.6300000000000003 | 7.957919036560464 | 13.51 |
| `outcome_gap_pct` | 0.13307984790874516 | 0.13307984790874516 | 0.13307984790874516 | 0.0007401924500369805 | 0.0007401924500369805 |
| `outcome_daily_return_pct` | 0.07984790874524705 | 0.07984790874524705 | 0.07984790874524705 | 0.005181347150259086 | 0.005181347150259086 |
| `outcome_intraday_return_pct` | -0.04697986577181201 | -0.046979865771812124 | -0.04697986577181201 | 0.004437869822485174 | 0.004437869822485174 |
| `outcome_daily_range_pct` | 0.0948905109489051 | 0.0948905109489051 | 0.0948905109489051 | 0.004437869822485174 | 0.004437869822485174 |
| `outcome_dollar_volume` | 2909.3433342800004 | 6982424.002272 | 2909.3433342800004 | 1599.8303555365078 | 2716.0 |
| `outcome_rvol_20d` | 2.7552741442859947 | 2.7552741442859947 | 2.7552741442859947 | 0.028169014084507043 | 0.028169014084507043 |
| `event_future_split_factor` | 0.0004166666666666667 | 0.0004166666666666667 | 0.0004166666666666667 | 1.0 | 1.0 |
| `outcome_future_split_factor` | 0.0004166666666666667 | 0.0004166666666666667 | 0.0004166666666666667 | 1.0 | 1.0 |
| `event_future_dividend_sum` | 0.0 | 0.0 | 0.0 | 7.609999999999999 | 7.609999999999999 |
| `outcome_future_dividend_sum` | 0.0 | 0.0 | 0.0 | 7.609999999999999 | 7.609999999999999 |
| `event_future_dividend_factor` | 1.0 | 1.0 | 1.0 | 0.5890391588867849 | 0.5890391588867849 |
| `outcome_future_dividend_factor` | 1.0 | 1.0 | 1.0 | 0.5890391588867849 | 0.5890391588867849 |
| `event_future_adjustment_factor` | 1.0 | 1.0 | 1.0 | 0.5890391588867849 | 0.5890391588867849 |
| `outcome_future_adjustment_factor` | 1.0 | 1.0 | 1.0 | 0.5890391588867849 | 0.5890391588867849 |
| `event_corporate_action_count` | 0 | 0 | 0 | 0 | 0 |
| `outcome_corporate_action_count` | 0 | 0 | 0 | 0 | 0 |
| `event_split_action_count` | 0 | 0 | 0 | 0 | 0 |
| `outcome_split_action_count` | 0 | 0 | 0 | 0 | 0 |
| `event_dividend_action_count` | 0 | 0 | 0 | 0 | 0 |
| `outcome_dividend_action_count` | 0 | 0 | 0 | 0 | 0 |
| `event_ticker_change_action_count` | 0 | 0 | 0 | 0 | 0 |
| `outcome_ticker_change_action_count` | 0 | 0 | 0 | 0 | 0 |
| `event_has_split_action` | False | False | False | False | False |
| `outcome_has_split_action` | False | False | False | False | False |
| `event_has_dividend_action` | False | False | False | False | False |
| `outcome_has_dividend_action` | False | False | False | False | False |
| `event_has_ticker_change_action` | False | False | False | False | False |
| `outcome_has_ticker_change_action` | False | False | False | False | False |
| `event_has_any_corporate_action` | False | False | False | False | False |
| `outcome_has_any_corporate_action` | False | False | False | False | False |
| `event_row_level_price_integrity_state` | row_candidate | row_candidate | row_candidate | row_candidate | row_candidate |
| `outcome_row_level_price_integrity_state` | row_candidate | row_candidate | row_candidate | row_candidate | row_candidate |
| `event_selected_price_hard_invalid` | False | False | False | False | False |
| `outcome_selected_price_hard_invalid` | False | False | False | False | False |
| `event_negative_volume` | False | False | False | False | False |
| `outcome_negative_volume` | False | False | False | False | False |
| `event_daily_backtest_core_row_candidate` | True | True | True | True | True |
| `outcome_daily_backtest_core_row_candidate` | True | True | True | True | True |
| `event_family_data_quality_verdict` | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope |
| `outcome_family_data_quality_verdict` | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope | usable_for_declared_scope |
| `event_family_foundations_completion_status` | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready |
| `outcome_family_foundations_completion_status` | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready |
| `event_family_visual_inspection_status` | visual_complete | visual_complete | visual_complete | visual_complete | visual_complete |
| `outcome_family_visual_inspection_status` | visual_complete | visual_complete | visual_complete | visual_complete | visual_complete |
| `event_family_production_use_gate` | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed |
| `outcome_family_production_use_gate` | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed | declared_scope_allowed |
| `event_family_event_consumption_gate` | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy |
| `outcome_family_event_consumption_gate` | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy | allowed_with_family_policy |
| `event_gate_quality_policy_version` | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 |
| `outcome_gate_quality_policy_version` | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 |
| `event_close_to_outcome_open_return_pct` | 13.307984790874517 | 13.307984790874517 | 13.307984790874517 | 0.07401924500369805 | 0.07401924500369805 |
| `event_close_to_outcome_high_return_pct` | 14.068441064638758 | 14.068441064638781 | 14.068441064638758 | 0.5181347150259086 | 0.5181347150259086 |
| `event_close_to_outcome_low_return_pct` | 4.1825095057034245 | 4.1825095057034245 | 4.1825095057034245 | 0.07401924500369805 | 0.07401924500369805 |
| `event_close_to_outcome_close_return_pct` | 7.984790874524705 | 7.984790874524705 | 7.984790874524705 | 0.5181347150259086 | 0.5181347150259086 |
| `outcome_intraday_open_to_close_return_pct` | -4.697986577181201 | -4.697986577181212 | -4.697986577181201 | 0.4437869822485174 | 0.4437869822485174 |
| `outcome_intraday_range_pct` | 9.489051094890502 | 9.48905109489051 | 9.489051094890502 | 0.4437869822485171 | 0.44378698224852436 |
| `label_next_close_positive` | True | True | True | True | True |
| `label_next_close_ge_5pct` | True | True | True | False | False |
| `label_next_close_ge_10pct` | False | False | False | False | False |
| `label_next_close_le_minus_5pct` | False | False | False | False | False |
| `label_next_close_le_minus_10pct` | False | False | False | False | False |
| `label_next_high_ge_10pct` | True | True | True | False | False |
| `label_next_high_ge_20pct` | False | False | False | False | False |
| `label_next_low_le_minus_10pct` | False | False | False | False | False |
| `label_next_open_ge_5pct` | True | True | True | False | False |
| `label_next_open_le_minus_5pct` | False | False | False | False | False |
| `outcome_quality_state` | good_daily_outcome | good_daily_outcome | good_daily_outcome | good_daily_outcome | good_daily_outcome |
| `valid_for_outcome_research` | True | True | True | True | True |
| `valid_for_ml_label_candidate` | True | True | True | True | True |
| `valid_for_strategy_label_candidate` | True | True | True | True | True |
| `valid_for_backtest_outcome_candidate` | True | True | True | True | True |
| `valid_for_rl_reward_candidate` | False | False | False | False | False |
| `contains_post_event_information` | True | True | True | True | True |
| `prohibited_as_pre_event_feature` | True | True | True | True | True |
| `requires_feature_label_separation` | True | True | True | True | True |
| `full_universe_claim` | False | False | False | False | False |
| `expected_data_calendar_build_run_id` | expected_data_calendar_v0_1_20260622T141019Z | expected_data_calendar_v0_1_20260622T141019Z | expected_data_calendar_v0_1_20260622T141019Z | expected_data_calendar_v0_1_20260622T141019Z | expected_data_calendar_v0_1_20260622T141019Z |
| `dataset_certification_matrix_build_run_id` | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z |
| `corporate_actions_build_run_id` | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z | corporate_actions_table_v0_1_20260622T144845Z |
| `expectation_policy_version` | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 | expected_data_calendar_policy_v0_1 |
| `event_daily_quality_policy_version` | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 |
| `outcome_daily_quality_policy_version` | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 | master_daily_table_policy_v0_1 |
| `event_daily_schema_version` | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 |
| `outcome_daily_schema_version` | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 | master_daily_table_v0_1 |
| `event_daily_build_run_id` | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z |
| `outcome_daily_build_run_id` | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z | master_daily_table_v0_1_20260622T161747Z |
| `source_event_window_materialization_scope` | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered | halts_intraday_lt1b_calendar_covered |
| `source_event_window_quality_policy_version` | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 | event_windows_table_policy_v0_1 |
| `source_event_window_schema_version` | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 | event_windows_table_v0_1 |
| `source_event_window_build_run_id` | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z | event_windows_table_v0_1_20260625T231016Z |
| `source_full_universe_claim` | False | False | False | False | False |
| `materialization_scope` | halt_next_session_daily_outcomes_v0_1 | halt_next_session_daily_outcomes_v0_1 | halt_next_session_daily_outcomes_v0_1 | halt_next_session_daily_outcomes_v0_1 | halt_next_session_daily_outcomes_v0_1 |
| `quality_policy_version` | outcomes_table_policy_v0_1 | outcomes_table_policy_v0_1 | outcomes_table_policy_v0_1 | outcomes_table_policy_v0_1 | outcomes_table_policy_v0_1 |
| `schema_version` | outcomes_table_v0_1 | outcomes_table_v0_1 | outcomes_table_v0_1 | outcomes_table_v0_1 | outcomes_table_v0_1 |
| `build_run_id` | outcomes_table_v0_1_20260626T073950Z | outcomes_table_v0_1_20260626T073950Z | outcomes_table_v0_1_20260626T073950Z | outcomes_table_v0_1_20260626T073950Z | outcomes_table_v0_1_20260626T073950Z |
| `created_at_utc` | 2026-06-26T07:39:50.995003+00:00 | 2026-06-26T07:39:50.995003+00:00 | 2026-06-26T07:39:50.995003+00:00 | 2026-06-26T07:39:50.995003+00:00 | 2026-06-26T07:39:50.995003+00:00 |
| `source_event_windows_table_path` | E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet | E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet |
| `source_event_windows_table_sha256` | cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e | cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e | cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e | cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e | cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e |
| `source_master_daily_table_path` | E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1 | E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1 | E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1 | E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1 | E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1 |
| `source_master_daily_table_tree_sha256` | 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e | 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e | 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e | 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e | 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e |

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
