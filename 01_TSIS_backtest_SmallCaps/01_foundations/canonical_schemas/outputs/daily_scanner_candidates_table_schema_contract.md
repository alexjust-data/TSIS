# Daily Scanner Candidates Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical target schema for:

```text
daily_scanner_candidates_table_v0_1
```

`daily_scanner_candidates_table` is the governed candidate-generation surface
for CAPA 1.

It reconstructs which instruments were in-play under a declared scanner
definition at a declared session/as-of time.

It is not the final `market_state_table`.
It is not the complete tradable universe.
It is not a label, reward, strategy signal or execution truth.

## 2. Logical Unit

Unit:

```text
one instrument selected or evaluated by one scanner run
```

Recommended grain:

```text
scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id
```

If the same scanner is replayed at multiple intraday timestamps on the same
session, each timestamp must produce a separate `as_of_utc`.

## 3. Physical Layout

Target root:

```text
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table
```

Target artifacts:

```text
daily_scanner_candidates_table_v0_1/
_daily_scanner_candidates_table_manifest_v0_1.json
_daily_scanner_candidates_table_summary_v0_1.csv
```

Recommended layout:

```text
partitioned parquet dataset by scanner_definition_id/year/month
```

The official E-root table is not materialized yet.

A controlled replay candidate exists under test-run evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

That replay validates builder shape, scanner comparison, lineage, denominator
counts and prohibition flags. It is not the official promoted dataset and does
not change the target root above.

## 4. Source Components

Allowed source components:

```text
instrument_master_v0_1
market_calendar_v0_1
master_daily_table_v0_1
master_intraday_bar_table_v0_1 when scope and price view allow
fundamentals_asof_table_v0_1 when used for market cap or float context
short_context_table_v0_1 when used for short-pressure filters
regime_context_table_v0_1 when used for market/regime filters
news_context_table_v0_1 when used for catalyst-aware variants
real_time_corporate_event_alerts_table_v0_1 when materialized
```

Allowed external/live source classes after separate contracts:

```text
broker_live_scanner
vendor_market_snapshot
broker_api_snapshot
TradeStation/DAS/SageTrader equivalent scanner feed
```

Any live/vendor/broker source must preserve `received_at_utc`, vendor lineage,
latency policy and replayability constraints.

## 5. Required Columns

Identity:

- `scanner_candidate_id`
- `scanner_run_id`
- `scanner_definition_id`
- `scanner_definition_version`
- `scanner_family`
- `scanner_name`
- `scanner_mode`
- `scanner_role`

Instrument/session:

- `instrument_id`
- `ticker`
- `session_date`
- `as_of_utc`
- `market_timezone`
- `exchange`
- `is_common_stock`
- `is_lt1b_operational`

Universe and denominator:

- `universe_definition_id`
- `population_scope`
- `population_denominator_count`
- `evaluated_candidate_count`
- `selected_candidate_count`
- `full_universe_claim`
- `top_n`
- `rank`
- `rank_metric`
- `rank_metric_value`
- `included_in_top_n`
- `rank_pct_chg_1d`
- `rank_volume_acceleration`
- `rank_dollar_volume_to_time`
- `rank_rvol_to_time`
- `rank_composite_in_play`
- `selected_trade_station_like_top25`
- `selected_broad_discovery`
- `selected_by_pct_chg_rank`
- `selected_by_volume_acceleration_rank`
- `selected_by_dollar_volume_rank`
- `selected_by_composite_in_play_rank`

Scanner filters:

- `market_cap_usd`
- `market_cap_asof_date`
- `market_cap_source`
- `last_price`
- `previous_close`
- `open_price`
- `pct_chg_1d`
- `gap_pct`
- `volume_today`
- `dollar_volume_today`
- `volume_to_time`
- `volume_since_04_00`
- `volume_last_5m`
- `volume_last_15m`
- `volume_acceleration`
- `dollar_volume_to_time`
- `rvol_to_time`
- `volume_tier`
- `price_min_filter`
- `price_max_filter`
- `volume_min_filter`
- `market_cap_max_filter`
- `price_filter_passed`
- `volume_filter_passed`
- `market_cap_filter_passed`
- `asset_type_filter_passed`
- `exchange_filter_passed`
- `all_filters_passed`
- `candidate_reasons`
- `candidate_reason_count`
- `reason_pct_chg_1d_move`
- `reason_gap_pct_move`
- `reason_volume_acceleration`
- `reason_rvol_to_time`
- `reason_afterhours_breakout`
- `reason_premarket_new_high`
- `reason_prior_day_high_reclaim`
- `reason_unusual_range_expansion`
- `reason_news_context`
- `reason_halt_or_reopen_context`

Source lineage:

- `source_master_daily_table_path`
- `source_master_daily_table_build_run_id`
- `source_instrument_master_build_run_id`
- `source_market_calendar_build_run_id`
- `source_intraday_table_path`
- `source_intraday_table_build_run_id`
- `source_live_snapshot_id`
- `source_vendor`
- `source_vendor_dataset`
- `source_snapshot_received_at_utc`
- `source_snapshot_latency_ms`
- `source_manifest`

Quality and legality:

- `scanner_quality_state`
- `scanner_replayable`
- `requires_asof_filter`
- `contains_future_information_without_event_filter`
- `data_availability_state`
- `market_cap_stale_flag`
- `price_available`
- `volume_available`
- `instrument_identity_temporal_match`
- `calendar_session_valid`
- `valid_for_event_discovery_candidate`
- `valid_for_market_state_seed_candidate`
- `valid_for_sampling_lineage`
- `valid_for_ml_feature_candidate`
- `valid_for_rl_state_candidate`
- `valid_for_live_downstream_candidate`

Versioning:

- `schema_version`
- `quality_policy_version`
- `scanner_policy_version`
- `build_run_id`
- `created_at_utc`

## 6. Canonical Scanner Definitions

The first governed scanner framework has two definitions:

```text
trade_station_like_scanner_v0_1
broad_in_play_discovery_scanner_v0_1
```

`trade_station_like_scanner_v0_1` models operational small-cap momentum
visibility:

```text
market_cap_usd < 100000000
volume_today > 500000
0.5 < last_price <= 20
rank by pct_chg_1d desc
top_n = 25
```

`broad_in_play_discovery_scanner_v0_1` models broad research discovery and must
not use `volume_today > 500000` or `% change 1D` as the only way to enter the
candidate set. It must preserve `candidate_reasons` and the independent ranks
listed in this schema when source fields exist.

Authoritative scanner framework:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
configs/data_foundation_outputs/scanner_definitions/
```

## 7. Required Semantics

Rows must preserve whether they represent:

```text
evaluated_not_selected
selected_in_top_n
selected_by_threshold_without_top_n
manual_research_seed
live_scanner_candidate
historical_replay_candidate
```

The builder must distinguish:

```text
scanner input data available
scanner filter passed
scanner rank selected
downstream state context available
```

These are different concepts and must not be collapsed.

## 8. Prohibited Semantics

The table must not contain:

- post-event outcomes;
- labels;
- rewards;
- strategy decisions;
- order actions;
- fills;
- PnL;
- hand-picked examples without `scanner_mode = manual_research_seed`;
- hidden scanner definitions;
- claims that top-N candidates are the complete universe.

## 9. Downstream Flags

Default target flags before materialization:

```text
valid_for_event_discovery_candidate = true after validators pass
valid_for_market_state_seed_candidate = true after validators pass
valid_for_sampling_lineage = true after validators pass
valid_for_ml_feature_candidate = false unless a later feature contract allows scanner-derived features
valid_for_rl_state_candidate = false unless composed into market_state_table
valid_for_live_downstream_candidate = false unless a live latency contract exists
```

## 10. Change Policy

Version bump required when:

- grain changes;
- scanner definition semantics change;
- ranking semantics change;
- a new source class becomes authoritative;
- scanner-derived features become ML/RL features;
- live scanner rows become allowed for downstream automation;
- denominator/universe rules change.
