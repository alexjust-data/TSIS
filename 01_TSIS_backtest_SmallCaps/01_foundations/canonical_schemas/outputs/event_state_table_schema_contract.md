# Event State Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema target for:

```text
event_state_table_v0_1
```

`event_state_table` is the future governed event-anchored state view. It links a
market state snapshot to an event/window and a decision role.

It is not materialized in v0.1.

It is not a label table, not an outcomes table, not a strategy table, not an
execution/fill table and not a direct RL transition table.

## 2. Logical Unit

Unit:

```text
one event-window decision state
```

Target grain:

```text
event_window_id + decision_timestamp_utc + state_role + state_schema_version
```

Primary key:

```text
event_state_id
```

## 3. Physical Layout

Future root:

```text
E:/TSIS/data/data_foundation_outputs/event_state_table
```

Future dataset:

```text
event_state_table_v0_1/
  event_family=<event_family>/
    decision_year=<YYYY>/
```

No v0.1 parquet is allowed until the builder, manifest and tests exist.

## 4. Required Identity Columns

- `event_state_id`
- `event_id`
- `event_window_id`
- `market_state_id`
- `instrument_id`
- `ticker`
- `event_family`
- `event_timestamp_utc`
- `decision_timestamp_utc`
- `decision_date`
- `state_role`
- `consumption_legality`
- `state_schema_version`
- `state_builder_version`
- `state_quality_state`

## 5. Required Event Anchoring Columns

- `event_window_start_utc`
- `event_window_end_utc`
- `pre_event_window_start_utc`
- `pre_event_window_end_utc`
- `state_cutoff_utc`
- `state_cutoff_reason`
- `event_source_dataset_id`
- `event_source_quality_state`

Allowed `state_role` values:

```text
pre_event
at_event
post_event_review
research_replay
```

Only `pre_event` and legal `at_event` rows may become ML feature candidates.
`post_event_review` is forensic/research context and must not be used as
pre-event feature state.


Required independent consumption legality classification:

```text
consumption_legality
```

Allowed `consumption_legality` values:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

`state_role` and `consumption_legality` are independent classifications.
`state_role` describes the event-relative snapshot role.
`consumption_legality` describes whether that row may be consumed as predictive/input state.

Default interpretation:

| state_role | allowed consumption_legality | Predictive X use |
| --- | --- | --- |
| `pre_event` | `decision_safe` when all cutoff/gates pass; otherwise `research_only` or `prohibited_as_input` | allowed only when `decision_safe` and consumer gates pass |
| `at_event` | `decision_safe` only when the event and all fields are known at the decision cutoff; otherwise `research_only` or `prohibited_as_input` | allowed only when `decision_safe` and consumer gates pass |
| `post_event_review` | `research_only` or `outcome_adjacent` | prohibited as pre-event/at-event input |
| `research_replay` | `research_only` or `prohibited_as_input` unless a later replay contract authorizes more | not a default predictive input |

A `post_event_review` row can be a valid Event State row for research and still be invalid as X for prediction at the event timestamp.

## 6. Required Label Separation Columns

- `outcome_join_key`
- `label_join_key`
- `outcome_values_inline_allowed`
- `label_columns_inline_allowed`
- `reward_columns_inline_allowed`

Required values:

```text
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
```

## 7. Required Consumer Gates

- `consumption_legality`
- `valid_for_pattern_discovery`
- `valid_for_ml_feature_candidate`
- `valid_for_backtest_context_candidate`
- `valid_for_rl_state_candidate`
- `valid_for_rl_training_direct`
- `valid_for_execution_context_candidate`
- `valid_for_execution_simulator_direct`
- `contains_future_information_without_event_filter`
- `requires_asof_filter`
- `full_universe_claim`
- `execution_truth`

Default v0.1 target values before a real builder:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
consumption_legality != decision_safe unless all temporal, role and consumer gates pass
execution_truth = false
requires_asof_filter = true
```

## 8. Required Lineage Columns

- `build_run_id`
- `created_at_utc`
- `market_state_build_run_id`
- `event_windows_build_run_id`
- `component_manifest_hash_bundle`
- `source_cutoff_policy_version`
- `leakage_policy_version`
- `feature_namespace_version`

## 9. Allowed Feature Columns

Event state may carry a controlled subset of market-state feature columns, but
the original namespaces must be preserved:

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
event__
```

The `event__` namespace may only describe event metadata known at or before the
decision cutoff. It must not contain outcome labels.

The `scanner__` namespace may only carry candidate-set lineage from
`daily_scanner_candidates_table`. It must not be interpreted as complete state,
complete universe or strategy signal.

## 10. Prohibited Columns

The following column families are prohibited inside `event_state_table`:

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

## 11. Initial Quality States

Allowed `state_quality_state` values:

- `event_state_good_for_declared_cutoff`
- `event_state_review_missing_optional_component`
- `event_state_review_scoped_intraday_component`
- `event_state_review_microstructure_seed_only`
- `event_state_review_short_constraints_missing`
- `event_state_blocked_future_information_detected`
- `event_state_blocked_required_component_missing`
- `event_state_blocked_invalid_component_quality`
- `event_state_bad_duplicate_state_id`
- `event_state_bad_missing_decision_timestamp`
- `event_state_bad_missing_event_window`

## 12. Current Status

```text
event_state_table_v0_1 materialized = false
builder_implemented = false
schema_status = target_schema_defined
controlled_candidate_materialized = true
candidate_dataset_id = event_state_table_v0_1_candidate
candidate_status = controlled_candidate_not_promoted
candidate_scope = halt_event_window_event_state_controlled_candidate
candidate_rows = 50
candidate_manifest = E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
```

The schema exists so future event-state builders have a strict target. It does
not certify that the official institutional event-state dataset exists. The
controlled candidate is an integration proof only and inherits provisional
market/microstructure lineage.

## Evidencia 2026-07-05 - Event State Intradia Quote-Guarded Controlado

```text
script = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
dataset_path = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
manifest = C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
joined_event_state_rows = 15
event_count = 5
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
consumption_legality_counts = not_emitted_by_current_controlled_candidate_v0_1; future builders must emit it explicitly
validator_status = passed
full_universe_claim_rows = 0
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
execution_truth_rows = 0
```

Lectura correcta: esta evidencia no promociona `event_state_table_v0_1` oficial. Es un candidato controlado intradia para pattern discovery y para construir outcomes separados.
