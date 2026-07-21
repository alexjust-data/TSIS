# Event State Table Consumption Policy `v0_1`

## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.


## 1. Scope

Dataset target:

```text
event_state_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
```

## 1.1 Provisional Microstructure Source Rule

`event_state_table` inherits the upstream `market_state_table` source-root
policy. For the next controlled candidate loop, event-state rows may reference
market-state/microstructure candidates derived from:

```text
quotes_root_used = D:/quotes
quotes_root_state = pre_approval_d_recovery_lineage_requires_rebuild
target_official_quotes_root = E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root = E:/TSIS/data/quotes
```

This only permits controlled candidate samples, builder tests and forensic
validation. While this root state remains provisional, rows inheriting it must
not be consumed as:

```text
valid_for_ml_feature_candidate = true
valid_for_rl_state_candidate = true
valid_for_backtest_context_candidate = true
valid_for_execution_context_candidate = true
```

unless a later contract proves `E:/TSIS/data/quotes_` parity/audit and the
affected event-state candidate is recomputed or explicitly promoted.

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

If an event-state row carries `scanner__*` columns, consumers must treat them as
candidate-set lineage only. Scanner fields do not prove complete market state,
complete universe, strategy signal or execution feasibility.

## 4. State Role Rules

Allowed state roles:

```text
pre_event
at_event
post_event_review
research_replay
```

ML feature consumption may only use rows where `consumption_legality = decision_safe` and `state_role` is one of:

```text
pre_event
at_event
```

when:

```text
valid_for_ml_feature_candidate = true
```

`post_event_review` rows are forensic/research or outcome-adjacent and must not become pre-event or at-event input features.

Plain-language enforcement:

```text
post_event_review rows are forensic/research or outcome-adjacent, not pre-event/at-event ML features.
```


## 4.1 Consumption Legality Rules

`state_role` is not sufficient to authorize downstream consumption.
Every future materialized row must expose an independent classification:

```text
consumption_legality
```

Allowed values:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Meaning:

| consumption_legality | Meaning | Predictive/Input Use |
| --- | --- | --- |
| `decision_safe` | all information in the row is observable at the declared `decision_timestamp_utc` and role/window gates pass | may be used as X only if consumer gates also pass |
| `research_only` | valid for inspection, clustering, audits or exploratory research, but not approved as decision input | not valid as production/predictive X |
| `outcome_adjacent` | contains or references post-event context useful near outcome analysis without inline labels/rewards | not valid as pre-event/at-event X |
| `prohibited_as_input` | must not be used as model, policy, strategy or execution input | never valid as X |

State-role default guardrail:

```text
pre_event + valid gates -> may be decision_safe
at_event + known-at-cutoff event -> may be decision_safe
post_event_review -> research_only or outcome_adjacent; never decision_safe for event-time prediction
research_replay -> research_only unless a later replay contract says otherwise
```

ML/backtest feature consumption requires both:

```text
consumption_legality = decision_safe
valid_for_ml_feature_candidate = true
```

A row can be a valid Event State research row and still be prohibited as predictive input.

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

May use rows as event context after materialization and validation, respecting `consumption_legality`.

### Pattern Discovery

May use rows for state clustering only if leakage gates pass and `consumption_legality` is not `prohibited_as_input`.

### ML

May use rows as features only when:

```text
consumption_legality = decision_safe
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
