# Outcomes Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
outcomes_table_v0_1
```

`outcomes_table` is the governed label/outcome component for CAPA 1 event
research.

It converts approved post-event windows into explicit forward outcomes while
preserving price-view discipline, source lineage and leakage boundaries.

It is not a feature table, not a strategy table and not an execution/reward
table.

## 2. Logical Unit

Unit:

```text
event window outcome row
```

Grain:

```text
event_window_id + outcome_horizon + price_view
```

v0.1 materializes:

```text
outcome_horizon = next_session_regular_daily
```

for `event_windows_table_v0_1` rows where:

```text
window_role = next_session_regular
valid_for_outcome_window_candidate = true
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/outcomes_table
```

Artifacts:

```text
outcomes_table_v0_1.parquet
_outcomes_table_summary_v0_1.csv
_outcomes_table_manifest_v0_1.json
```

Builder:

```text
scripts/materialize_outcomes_table.py
```

## 4. Sources

Governed sources v0.1:

- `event_windows_table_v0_1`
- `master_daily_table_v0_1`

The table intentionally uses daily price views from `master_daily_table_v0_1`.
It does not derive intraday fills, halt-resume returns, slippage or execution
rewards.

## 5. Required Columns

Identity and event lineage:

- `outcome_id`
- `event_window_id`
- `source_event_id`
- `event_source_dataset_id`
- `event_family`
- `event_type`
- `event_code`
- `event_source`
- `ticker`
- `instrument_id`
- `issuer_name`
- `listing_exchange`
- `event_session_date`
- `outcome_session_date`
- `outcome_horizon`
- `price_view`

Event-window boundaries:

- `event_time_utc`
- `resume_trade_utc`
- `event_session_phase`
- `window_role`
- `window_start_utc`
- `window_end_utc`
- `window_duration_minutes`
- `event_window_quality_state`
- `event_window_consumption_state`
- `source_event_quality_state`
- `source_halt_event_state`
- `source_resume_trade_observed`
- `event_response_end_observed`

Identity and calendar context:

- `calendar`
- `timezone`
- `instrument_identity_temporal_match`
- `is_common_stock`
- `is_lt1b_operational`
- `lt1b_classification_1b`

Daily join lineage:

- `event_master_daily_id`
- `outcome_master_daily_id`
- `event_quality_gate_family`
- `outcome_quality_gate_family`
- `event_daily_source_dataset`
- `outcome_daily_source_dataset`
- `event_daily_source_root`
- `outcome_daily_source_root`

Daily quality and presence:

- `event_expected_session`
- `outcome_expected_session`
- `event_expected_reason`
- `outcome_expected_reason`
- `event_data_present`
- `outcome_data_present`
- `event_missing_expected_data`
- `outcome_missing_expected_data`
- `event_source_daily_present`
- `outcome_source_daily_present`
- `event_source_adjusted_present`
- `outcome_source_adjusted_present`

Event daily market fields:

- `event_open`
- `event_high`
- `event_low`
- `event_close`
- `event_volume`
- `event_vwap`
- `event_source_raw_vwap`
- `event_transaction_count`
- `event_prior_close`
- `event_gap_pct`
- `event_daily_return_pct`
- `event_intraday_return_pct`
- `event_daily_range_pct`
- `event_dollar_volume`
- `event_rvol_20d`

Outcome daily market fields:

- `outcome_open`
- `outcome_high`
- `outcome_low`
- `outcome_close`
- `outcome_volume`
- `outcome_vwap`
- `outcome_source_raw_vwap`
- `outcome_transaction_count`
- `outcome_prior_close`
- `outcome_gap_pct`
- `outcome_daily_return_pct`
- `outcome_intraday_return_pct`
- `outcome_daily_range_pct`
- `outcome_dollar_volume`
- `outcome_rvol_20d`

Corporate-action context:

- `event_future_split_factor`
- `outcome_future_split_factor`
- `event_future_dividend_sum`
- `outcome_future_dividend_sum`
- `event_future_dividend_factor`
- `outcome_future_dividend_factor`
- `event_future_adjustment_factor`
- `outcome_future_adjustment_factor`
- `event_corporate_action_count`
- `outcome_corporate_action_count`
- `event_split_action_count`
- `outcome_split_action_count`
- `event_dividend_action_count`
- `outcome_dividend_action_count`
- `event_ticker_change_action_count`
- `outcome_ticker_change_action_count`
- `event_has_split_action`
- `outcome_has_split_action`
- `event_has_dividend_action`
- `outcome_has_dividend_action`
- `event_has_ticker_change_action`
- `outcome_has_ticker_change_action`
- `event_has_any_corporate_action`
- `outcome_has_any_corporate_action`

Daily row gates:

- `event_row_level_price_integrity_state`
- `outcome_row_level_price_integrity_state`
- `event_selected_price_hard_invalid`
- `outcome_selected_price_hard_invalid`
- `event_negative_volume`
- `outcome_negative_volume`
- `event_daily_backtest_core_row_candidate`
- `outcome_daily_backtest_core_row_candidate`
- `event_family_data_quality_verdict`
- `outcome_family_data_quality_verdict`
- `event_family_foundations_completion_status`
- `outcome_family_foundations_completion_status`
- `event_family_visual_inspection_status`
- `outcome_family_visual_inspection_status`
- `event_family_production_use_gate`
- `outcome_family_production_use_gate`
- `event_family_event_consumption_gate`
- `outcome_family_event_consumption_gate`
- `event_gate_quality_policy_version`
- `outcome_gate_quality_policy_version`

Continuous outcome fields:

- `event_close_to_outcome_open_return_pct`
- `event_close_to_outcome_high_return_pct`
- `event_close_to_outcome_low_return_pct`
- `event_close_to_outcome_close_return_pct`
- `outcome_intraday_open_to_close_return_pct`
- `outcome_intraday_range_pct`

Discrete label fields:

- `label_next_close_positive`
- `label_next_close_ge_5pct`
- `label_next_close_ge_10pct`
- `label_next_close_le_minus_5pct`
- `label_next_close_le_minus_10pct`
- `label_next_high_ge_10pct`
- `label_next_high_ge_20pct`
- `label_next_low_le_minus_10pct`
- `label_next_open_ge_5pct`
- `label_next_open_le_minus_5pct`

Outcome gates:

- `outcome_quality_state`
- `valid_for_outcome_research`
- `valid_for_ml_label_candidate`
- `valid_for_strategy_label_candidate`
- `valid_for_backtest_outcome_candidate`
- `valid_for_rl_reward_candidate`
- `contains_post_event_information`
- `prohibited_as_pre_event_feature`
- `requires_feature_label_separation`
- `full_universe_claim`

Build lineage:

- `expected_data_calendar_build_run_id`
- `dataset_certification_matrix_build_run_id`
- `corporate_actions_build_run_id`
- `expectation_policy_version`
- `event_daily_quality_policy_version`
- `outcome_daily_quality_policy_version`
- `event_daily_schema_version`
- `outcome_daily_schema_version`
- `event_daily_build_run_id`
- `outcome_daily_build_run_id`
- `source_event_window_materialization_scope`
- `source_event_window_quality_policy_version`
- `source_event_window_schema_version`
- `source_event_window_build_run_id`
- `source_full_universe_claim`
- `materialization_scope`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`
- `source_event_windows_table_path`
- `source_event_windows_table_sha256`
- `source_master_daily_table_path`
- `source_master_daily_table_tree_sha256`

## 6. Allowed Price Views

Allowed `price_view` values:

- `daily_raw`
- `split_normalized`
- `adjusted`

Consumers must select one price view intentionally.

Rules:

- `daily_raw` is the raw observed daily price view.
- `split_normalized` is split-comparable daily OHLC.
- `adjusted` is economic-continuity daily OHLC.
- No row may mix event prices and outcome prices from different price views.

## 7. Quality States

Allowed `outcome_quality_state` values:

- `good_daily_outcome`
- `review_event_daily_missing`
- `review_outcome_daily_missing`
- `review_event_and_outcome_daily_missing`
- `review_daily_quality_gate`

Only `good_daily_outcome` may set:

```text
valid_for_ml_label_candidate = true
```

Review rows must be preserved for coverage accounting and forensic analysis,
but must not be used as primary labels.

## 8. Prohibited Interpretations

`outcomes_table_v0_1` must not be interpreted as:

- pre-event feature table;
- execution simulator result;
- intraday halt-resume outcome;
- RL reward table;
- strategy recommendation;
- final event-state table.

## 9. v0.1 Limitations

v0.1 intentionally excludes:

- intraday outcomes;
- raw quote/trade replay outcomes;
- fill probability;
- slippage;
- position sizing;
- action/reward definitions;
- non-halt event families.

