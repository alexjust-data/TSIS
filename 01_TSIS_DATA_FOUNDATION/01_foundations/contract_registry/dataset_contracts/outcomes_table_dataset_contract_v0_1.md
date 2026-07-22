# Outcomes Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: outcomes_table_v0_1
family: data_foundation_outputs
class: outcome/label component table
grain: event_window_id + outcome_horizon + price_view
```

## 2. Purpose

`outcomes_table` materializes post-event labels and returns from governed event
windows.

It answers:

```text
Given an approved event window and a declared price view, what happened over the
declared post-event outcome horizon?
```

It does not answer:

- what feature was known before the event;
- what strategy should trade;
- what fill would have occurred;
- what reward an RL policy receives.

## 3. Source Lineage

Authoritative inputs v0.1:

- `event_windows_table_v0_1`
- `master_daily_table_v0_1`

The event-window source fixes temporal boundaries. The daily source provides
price-view-specific market observations and row-level quality gates.

## 4. Current v0.1 Scope

```text
materialization_scope: halt_next_session_daily_outcomes_v0_1
outcome_horizon: next_session_regular_daily
source_event_windows_scope: halts_intraday_lt1b_calendar_covered
full_universe_claim: false
```

v0.1 covers halt-derived LT1B/calendar-covered event windows only.

## 5. Price Semantics

The table preserves the three `master_daily_table_v0_1` price views:

```text
daily_raw
split_normalized
adjusted
```

Every outcome return is computed inside one price view:

```text
event close of price_view X -> outcome session open/high/low/close of price_view X
```

Consumers must not mix:

- adjusted labels with raw execution prices;
- raw labels with adjusted training features;
- price views across event and outcome sides.

## 6. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/outcomes_table/
  outcomes_table_v0_1.parquet
  _outcomes_table_summary_v0_1.csv
  _outcomes_table_manifest_v0_1.json
```

## 7. Expected Materialization v0.1

Expected after build:

```text
source next-session windows: 42796
price_views: 3
rows: 128388
```

Expected quality distribution from source coverage:

```text
good_daily_outcome: 121761
review_event_and_outcome_daily_missing: 1980
review_event_daily_missing: 789
review_outcome_daily_missing: 3858
```

Review rows are retained intentionally. They prove coverage gaps and prevent
silent label fabrication.

## 8. Current Materialization

```text
build_run_id: outcomes_table_v0_1_20260626T073950Z
path: E:/TSIS/data/data_foundation_outputs/outcomes_table/outcomes_table_v0_1.parquet
manifest: E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_summary_v0_1.csv
rows: 128388
event_windows: 42796
source_events: 42796
tickers: 3709
instruments: 3566
price_views: 3
output_sha256: ce793a75d747d50c053f44433d5e3e59ebb3616db7056c3e5087a005fb6db09e
source_event_windows_build_run_id: event_windows_table_v0_1_20260625T231016Z
source_master_daily_build_run_id: master_daily_table_v0_1_20260622T161747Z
```

Current validation:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

## 9. Allowed Consumers

Permitted:

- `outcome_research`
- `strategy_research`
- `ml_primary` only for rows where `valid_for_ml_label_candidate = true`
- `ml_flagged` with explicit quality masks
- `backtest_extended` for outcome evaluation
- `forensic_only`

Restricted:

- `event_engine` as pre-event feature source;
- `execution_simulator`;
- `rl_allowed` as reward source;
- `live_downstream_candidate`;
- `backtest_core` as fill/execution truth.

## 10. Quality Policy

Primary label rows require:

- event daily row exists;
- outcome daily row exists;
- both rows are `backtest_core_row_candidate` in `master_daily_table_v0_1`;
- event close is positive;
- price view is one of the declared views.

Rows that fail those conditions remain in the table with a review state and
must not be used as primary ML labels.

## 11. Change Policy

Version bump required when:

- grain changes;
- outcome horizon changes;
- threshold label definitions change;
- price views change;
- intraday outcomes are added;
- RL reward semantics are added;
- non-halt event families are added;
- row quality semantics change.
