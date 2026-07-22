# Event Windows Table Consumption Policy `v0_1`

## 1. Role

This policy governs:

```text
event_windows_table_v0_1
```

It governs explicit event windows derived from governed source events. It does
not replace future Event Engine contracts or outcome-table contracts.

## 2. Principle

Event windows are boundaries.

They are not:

- features by themselves;
- labels by themselves;
- price data;
- execution truth;
- live alerts;
- alpha.

## 3. Required Consumer Behavior

Every consumer must preserve:

- `source_event_id`;
- `event_source_dataset_id`;
- `window_role`;
- `window_start_utc`;
- `window_end_utc`;
- `contains_post_event_information`;
- `leakage_safe_as_pre_event_feature`;
- `event_window_quality_state`;
- `valid_for_ml_feature_candidate`;
- `valid_for_outcome_window_candidate`;
- source hashes and build ids.

## 4. Allowed Uses

Allowed:

- define event windows for Event Engine;
- feed future microstructure feature builders;
- feed future outcome builders;
- align halts with calendar sessions;
- support forensic review and data quality reports.

## 5. Restricted Uses

ML:

- may use only `valid_for_ml_feature_candidate = true` rows as pre-event
  features;
- must keep outcome windows separate.

Backtesting:

- may use only rows with `valid_for_backtest_event_window_candidate = true`
  for regular-session event backtests;
- must preserve `event_session_phase`.

Outcome research:

- may use `valid_for_outcome_window_candidate = true` rows as candidate label
  windows;
- must not feed those rows into features.

## 6. Prohibited Uses

Blocked:

- `strategy_alpha`;
- primary ML dataset by itself;
- RL dataset by itself;
- execution fill simulation;
- live alerting;
- treating halt windows as offering/news/catalyst windows;
- using post-event windows as pre-event features.

## 7. Final Rule

If a consumer cannot explain whether a window is pre-event, event-response,
session context or post-event outcome, it is not allowed to consume this table.

