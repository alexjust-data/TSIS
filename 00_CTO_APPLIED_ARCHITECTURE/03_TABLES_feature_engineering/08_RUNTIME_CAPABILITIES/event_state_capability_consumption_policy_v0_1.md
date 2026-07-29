# Event State Capability Consumption Policy v0.1

Status: `CLOSED_PASS_EVENT_STATE_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION`
Date: `2026-07-28`

This policy defines how the promoted restricted Event State on-demand runtime
capability may be inspected, reused or served.

It does not promote an official physical Event State dataset and does not open
production, downstream research/backtest, ML/RL or live consumption.

## Governing Decision

```text
policy_id = event_state_capability_consumption_policy_v0_1_20260728T135626Z
capability_id = event_state_on_demand_runtime_capability_v0_1
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
allowed_event_type_ids = [event_type:market_data:session_opened]
accepted_subject_scope = exchange_session
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = runtime_user_invocation_interface_v0_1
```

## Allowed

```text
inspect capability metadata
inspect request, dependency, plan, lineage, validation and registry evidence
serve candidate metadata to internal runtime components
reuse exact-match validated candidate evidence when all fingerprints match
reuse incremental validated candidate compositions when lineage-chain evidence matches
request new candidate generation only under separate authorization
```

## Conditionally Allowed

Candidate content may be served only to future authorized runtime-internal
validation, reuse and audit flows, and only when all required reuse conditions
pass.

## Prohibited

```text
official Event State dataset resolution
official parquet promotion
production use
live trading use
downstream backtest consumption
downstream ML/RL consumption
additional Event Types beyond session_opened
halt_resumed consumption
full-universe or unbounded generation
silent registry mutation
silent promotion of candidate evidence
direct Market State path consumption
```

## Consumer Classes

Allowed in v0.1:

```text
runtime_internal_request_resolver
runtime_internal_execution_planner
runtime_internal_candidate_reuse_resolver
runtime_validator
applied_architecture_review
human_audit_metadata_review
```

Prohibited in v0.1:

```text
production_trading
live_execution
downstream_backtest
downstream_ml
downstream_rl
unbounded_event_state_builder
official_dataset_resolver
unauthorized_strategy_engine
```
