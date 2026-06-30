# Event State Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: event_state_table_v0_1
family: data_foundation_outputs
class: event_anchored_state_view
grain: event_window_id + decision_timestamp_utc + state_role + state_schema_version
status: contract_defined_not_materialized
```

## 2. Purpose

`event_state_table` is the future governed event-anchored view of market state.

It answers:

```text
For this event/window and decision timestamp, what feature-state was legally
knowable and auditable?
```

It does not answer:

- what the future outcome was;
- what label belongs to the event;
- what reward was earned;
- what action a strategy should take;
- whether execution/fill occurred.

## 3. Source Components

Required upstream when materialized:

```text
market_state_table_v0_1
event_windows_table_v0_1 or future governed event table
```

Allowed context references:

```text
instrument_master_v0_1
market_calendar_v0_1
dataset_certification_matrix_v0_1
daily_scanner_candidates_table_v0_1 as candidate-set lineage when present
halts_table_v0_1
```

Label/outcome source for later joins only:

```text
outcomes_table_v0_1
```

`outcomes_table_v0_1` values must not be inlined as event-state features.

## 4. Current Scope

```text
materialized: false
builder_implemented: false
full_universe_claim: false
direct_rl_training_allowed: false
execution_truth: false
```

The current contract defines the future dataset. It is not evidence that an
event-state table exists.

## 5. Required Semantics

Each row must anchor:

- one event or event window;
- one decision timestamp;
- one state role;
- one linked market state snapshot;
- one legal cutoff.

Allowed state roles:

```text
pre_event
at_event
post_event_review
research_replay
```

Only `pre_event` and legal `at_event` rows may become ML feature candidates.

## 6. Label Separation

`event_state_table` may expose:

```text
outcome_join_key
label_join_key
```

It must not contain:

```text
outcome__*
label__*
reward__*
```

The training dataset builder must join labels separately and emit independent
feature, label and join manifests.

## 7. Allowed Consumers

Allowed only after materialization and validators pass:

- `event_engine`
- `pattern_discovery`
- `ml_feature_builder`
- `backtest_extended` as context
- `forensic_review`

Not enabled by this contract:

- direct `rl_training`;
- execution/fill simulation direct;
- strategy signal authority;
- live trading authority.

## 8. Change Policy

Version bump required when:

- event grain changes;
- allowed state roles change;
- outcome/label join semantics change;
- any label/outcome/reward column family becomes inline;
- event source precedence changes;
- direct RL state/training eligibility changes.
