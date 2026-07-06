# Market State Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema target for:

```text
market_state_table_v0_1
```

`market_state_table` is the future governed state snapshot table for TSIS. It
will compose CAPA 1 context components under one legal decision-time cutoff.

It is not materialized in v0.1.

It is not a signal table, not a strategy table, not a label table, not an
outcomes table, not an execution/fill table and not a direct RL training table.

## 2. Logical Unit

Unit:

```text
one instrument state snapshot at one decision timestamp and horizon
```

Target grain:

```text
instrument_id + decision_timestamp_utc + state_horizon + state_scope + state_schema_version
```

Primary key:

```text
market_state_id
```

## 3. Physical Layout

Future root:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table
```

Future dataset:

```text
market_state_table_v0_1/
  decision_year=<YYYY>/
    decision_month=<MM>/
```

No v0.1 parquet is allowed until the builder, manifest and tests exist.

## 4. Required Identity Columns

- `market_state_id`
- `instrument_id`
- `ticker`
- `decision_timestamp_utc`
- `decision_date`
- `decision_session_date`
- `state_horizon`
- `state_scope`
- `state_schema_version`
- `state_builder_version`
- `state_quality_state`

## 5. Required Lineage Columns

- `build_run_id`
- `created_at_utc`
- `source_cutoff_policy_version`
- `leakage_policy_version`
- `feature_namespace_version`
- `component_manifest_hash_bundle`
- `component_build_run_id_bundle`
- `component_quality_bundle`
- `component_availability_bundle`

Bundle columns may be structured JSON strings in v0.1, but their schema must be
documented by the builder config before materialization.

## 6. Required Consumer Gates

- `valid_for_event_context_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_backtest_context_candidate`
- `valid_for_rl_state_candidate`
- `valid_for_rl_training_direct`
- `valid_for_execution_simulator_direct`
- `contains_future_information_without_event_filter`
- `requires_asof_filter`
- `full_universe_claim`
- `execution_truth`

Default v0.1 target values before a real builder:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
execution_truth = false
requires_asof_filter = true
```

## 7. Required Component Availability Columns

- `identity_component_state`
- `calendar_component_state`
- `scanner_component_state`
- `daily_component_state`
- `intraday_component_state`
- `microstructure_component_state`
- `halt_component_state`
- `fundamentals_component_state`
- `news_component_state`
- `short_context_component_state`
- `short_constraints_component_state`
- `regime_component_state`
- `quality_component_state`

Allowed component states:

```text
included_good
included_review
missing_optional
missing_required
blocked_by_policy
not_requested
not_available
```

## 8. Required Feature Namespaces

Every feature column must begin with one of these prefixes:

```text
identity__
calendar__
scanner__
daily__
intraday__
microstructure__
halt__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
```

No un-namespaced feature column is allowed.

## 9. Prohibited Columns

The following column families are prohibited inside `market_state_table`:

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
strategy__*
signal__*
```

Allowed reference keys:

```text
outcome_join_key
label_join_key
```

Allowed reference keys must not include outcome, label or reward values.

## 10. Required As-Of Fields By Component

The table must preserve component cutoff evidence:

- `identity_as_of_utc`
- `calendar_as_of_utc`
- `scanner_as_of_utc`
- `daily_as_of_utc`
- `intraday_as_of_utc`
- `microstructure_as_of_utc`
- `halt_as_of_utc`
- `fundamentals_as_of_utc`
- `news_as_of_utc`
- `short_context_as_of_utc`
- `short_constraints_as_of_utc`
- `regime_as_of_utc`

Every non-null component as-of timestamp must satisfy:

```text
component_as_of_utc <= decision_timestamp_utc
```

## 11. Initial Quality States

Allowed `state_quality_state` values:

- `state_good_for_declared_cutoff`
- `state_review_missing_optional_component`
- `state_review_scoped_intraday_component`
- `state_review_microstructure_seed_only`
- `state_review_short_constraints_missing`
- `state_blocked_future_information_detected`
- `state_blocked_required_component_missing`
- `state_blocked_invalid_component_quality`
- `state_bad_duplicate_state_id`
- `state_bad_missing_decision_timestamp`

## 12. Current Status

```text
market_state_table_v0_1 materialized = false
builder_implemented = false
schema_status = target_schema_defined
controlled_candidate_materialized = true
candidate_dataset_id = market_state_table_v0_1_candidate
candidate_status = controlled_candidate_not_promoted
candidate_scope = halt_event_window_microstructure_controlled_candidate
candidate_rows = 50
candidate_manifest = E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
additional_controlled_candidate_scope = intraday_quote_guarded_scoped_candidate
additional_controlled_candidate_rows = 10835
additional_controlled_candidate_manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json
```

The schema exists so future builders have a strict target. It does not certify
that the official institutional state dataset exists. The controlled candidates are integration proofs only. The microstructure/halt candidate inherits provisional `D:/quotes` lineage from the upstream microstructure component. The intraday quote-guarded candidate proves `intraday__*` consumption from the scoped E-root master intraday candidate under closed-bar timestamps, but it is not official, not full-universe and not ML/RL ready.
