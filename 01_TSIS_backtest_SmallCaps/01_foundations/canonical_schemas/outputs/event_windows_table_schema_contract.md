# Event Windows Table Schema Contract `v0_1`

Status: `canonical_schema_contract`

Dataset: `event_windows_table_v0_1`

Physical target:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
```

## 1. Role

`event_windows_table_v0_1` is a governed CAPA 1 output table that turns
eligible source events into explicit time windows.

It exists because downstream state builders, microstructure feature builders,
outcome builders, backtests and ML/RL datasets must agree on the same event
boundaries.

This v0.1 is derived only from:

```text
halts_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
```

It does not cover news, offerings, filings, short pressure, regime shifts or
all future Event Engine events.

## 2. Grain

One row per:

```text
source_event_id + window_role
```

`event_window_id` must be unique.

The v0.1 source scope is:

```text
materialization_scope = halts_intraday_lt1b_calendar_covered
```

Only halt events that satisfy all of these conditions are materialized:

- `halts_table_v0_1.valid_for_intraday_mask = true`;
- ticker resolves temporally to `instrument_master_v0_1`;
- event date exists in `market_calendar_v0_1`.

## 3. Window Roles

Required v0.1 roles:

- `prior_session_regular`
- `pre_event_30m`
- `event_to_resume_or_30m`
- `same_session_regular`
- `next_session_regular`

`next_session_regular` may be absent when the market calendar has no next
session for the event date.

## 4. Required Columns

| Column | Required | Semantics |
| --- | --- | --- |
| `event_window_id` | yes | stable unique id for this event/window row |
| `source_event_id` | yes | upstream halt event id |
| `event_source_dataset_id` | yes | expected `halts_table_v0_1` |
| `event_family` | yes | expected `halt` for v0.1 |
| `event_type` | nullable | source halt type |
| `event_code` | nullable | source halt code |
| `event_source` | yes | upstream source, normally `nasdaq` or `nyse` in v0.1 |
| `ticker` | yes | uppercase ticker label |
| `instrument_id` | yes | resolved instrument id from `instrument_master_v0_1` |
| `issuer_name` | nullable | source issuer/security name |
| `listing_exchange` | nullable | source listing/exchange field |
| `session_date` | yes | market-calendar session date |
| `event_time_utc` | yes | halt start timestamp localized from ET into UTC |
| `resume_trade_utc` | nullable | trade resume timestamp localized from ET into UTC |
| `event_session_phase` | yes | `premarket`, `regular` or `afterhours` |
| `window_role` | yes | one of the v0.1 window roles |
| `window_start_utc` | yes | UTC start of this window |
| `window_end_utc` | yes | UTC end of this window |
| `window_duration_minutes` | yes | positive duration in minutes |
| `window_start_source` | yes | deterministic rule used for start |
| `window_end_source` | yes | deterministic rule used for end |
| `contains_event_time` | yes | whether `[start,end)` contains event time |
| `contains_post_event_information` | yes | true when the window extends after event time |
| `leakage_safe_as_pre_event_feature` | yes | true only when the window ends no later than event time |
| `source_event_quality_state` | yes | inherited halt quality state |
| `source_halt_event_state` | yes | inherited halt event state |
| `source_resume_trade_observed` | yes | whether upstream resume trade timestamp exists |
| `event_response_end_observed` | yes | true when event-response window uses observed resume |
| `event_window_quality_state` | yes | `good` or `review_resume_fallback` |
| `event_window_consumption_state` | yes | role-specific consumption class |
| `session_open_utc` | yes | regular session open from market calendar |
| `session_close_utc` | yes | regular session close from market calendar |
| `session_minutes` | yes | calendar session length |
| `is_early_close` | yes | calendar early-close flag |
| `calendar` | yes | calendar code |
| `timezone` | yes | calendar timezone |
| `previous_session_date` | nullable | prior calendar session date |
| `next_session_date` | nullable | next calendar session date |
| `instrument_identity_temporal_match` | yes | true for every v0.1 row |
| `is_common_stock` | yes | inherited instrument flag |
| `is_lt1b_operational` | yes | inherited instrument flag |
| `lt1b_classification_1b` | yes | inherited universe classification |
| `valid_for_event_engine` | yes | allowed as event-window input |
| `valid_for_microstructure_feature_candidate` | yes | candidate window for future microstructure builds |
| `valid_for_ml_feature_candidate` | yes | true only for pre-event-safe feature windows |
| `valid_for_outcome_window_candidate` | yes | true for event-response or post-event outcome windows |
| `valid_for_backtest_event_window_candidate` | yes | true when event source occurs during regular session |
| `valid_for_rl_state_component_candidate` | yes | false for v0.1 |
| `requires_decision_time_availability_contract` | yes | always true |
| `full_universe_claim` | yes | always false for v0.1 |
| `materialization_scope` | yes | expected `halts_intraday_lt1b_calendar_covered` |
| `quality_policy_version` | yes | expected `event_windows_table_policy_v0_1` |
| `schema_version` | yes | expected `event_windows_table_v0_1` |
| `build_run_id` | yes | materialization run id |
| `created_at_utc` | yes | materialization timestamp |
| `source_halts_table_path` | yes | upstream halts table path |
| `source_halts_table_sha256` | yes | upstream halts table hash |
| `source_instrument_master_path` | yes | upstream instrument master path |
| `source_instrument_master_sha256` | yes | upstream instrument master hash |
| `source_market_calendar_path` | yes | upstream calendar path |
| `source_market_calendar_sha256` | yes | upstream calendar hash |

Physical file:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
```

`year` and `month` remain ordinary columns derived from `session_date`.

## 5. Rules

Hard failures:

- missing required column;
- duplicate `event_window_id`;
- `window_end_utc <= window_start_utc`;
- missing `source_event_id`;
- missing `instrument_id`;
- any `valid_for_rl_state_component_candidate = true` in v0.1;
- any `full_universe_claim = true` in v0.1;
- `valid_for_ml_feature_candidate = true` while
  `leakage_safe_as_pre_event_feature = false`.

Review states are expected for `event_to_resume_or_30m` windows when no
observed resume-trade timestamp exists and a fixed 30-minute fallback is used.

## 6. Non-Goals

This schema does not:

- define all event families;
- replace `event_table`;
- build outcomes;
- compute microstructure features;
- prove live decision-time availability;
- authorize RL training;
- authorize execution simulation.
