# Event State Table Consumption Policy `v0_1`

## 1. Scope

Dataset target:

```text
event_state_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
```

## 2. Permitted Meaning

Permitted meaning after materialization:

```text
event-anchored legal feature-state view for one decision timestamp
```

Forbidden meaning:

```text
label table, outcome table, reward table, action table or fill table
```

## 3. Required Event Cutoff Rule

Consumers must only use rows where:

```text
state_cutoff_utc <= decision_timestamp_utc
```

and where all linked component as-of timestamps are legal under the upstream
`market_state_table` policy.

## 4. State Role Rules

Allowed state roles:

```text
pre_event
at_event
post_event_review
research_replay
```

ML feature consumption may only use:

```text
pre_event
at_event
```

when:

```text
valid_for_ml_feature_candidate = true
```

`post_event_review` rows are forensic/research and must not become pre-event
features.

Plain-language enforcement:

```text
post_event_review rows are forensic/research, not pre-event ML features.
```

## 5. Label Separation Rule

Allowed reference keys:

```text
outcome_join_key
label_join_key
```

Forbidden inline values:

```text
outcome__*
label__*
reward__*
```

ML training builders must join labels separately and emit independent feature,
label and leakage manifests.

## 6. Consumer Rules

### Event Engine

May use rows as event context after materialization and validation.

### Pattern Discovery

May use rows for state clustering only if leakage gates pass.

### ML

May use rows as features only when:

```text
valid_for_ml_feature_candidate = true
```

### Offline RL

May use rows as state candidates only after:

```text
valid_for_rl_state_candidate = true
```

Direct RL training remains blocked:

```text
valid_for_rl_training_direct = false
```

### Execution Simulator

May not treat rows as execution truth or fills.

## 7. Final Rule

`event_state_table` is an event-anchored feature-state view. Outcomes and
rewards live elsewhere.
