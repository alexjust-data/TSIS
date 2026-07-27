# Market State Capability Consumption Policy v0.1

Status: `CLOSED_PASS_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION`
Date: `2026-07-27`

This policy defines how the promoted restricted Market State on-demand runtime
capability may be inspected, reused or served.

It does not promote an official physical Market State dataset and does not open
production, downstream research/backtest, ML/RL or Event State materialization.

## Governing Decision

```text
policy_id = market_state_capability_consumption_policy_v0_1_20260727T142133Z
capability_id = market_state_on_demand_runtime_capability_v0_1
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
official_dataset = false
production = false
downstream = false
event_state_on_demand_execution = false
next_allowed_gate = event_state_on_demand_capability_design_authorization_v0_1
```

## Allowed

```text
inspect capability metadata
inspect request, plan, lineage, validation and registry evidence
serve candidate metadata to internal runtime components
reuse exact-match validated candidate evidence when all fingerprints match
reuse incremental validated candidate compositions when lineage-chain evidence matches
use Market State capability metadata for Event State on-demand planning
```

## Conditionally Allowed

Candidate files may be served only to runtime-internal validation, reuse and
audit flows, and only when all required reuse conditions pass:

```text
request_fingerprint_match
execution_plan_fingerprint_match
profile_contract_hash_match
source_fingerprint_match
builder_version_match
schema_hash_match
validation_status_allows_candidate_reuse
determinism_evidence_present
artifact_availability_available
no_quarantine
no_unresolved_blocking_findings
restriction_set_propagated
```

New candidate generation remains allowed only through a separate bounded,
incremental or scale authorization. This policy never authorizes a build by
itself.

## Prohibited

```text
official Market State dataset resolution
official parquet promotion
production use
live trading use
downstream backtest consumption
downstream ML/RL consumption
Event State physical materialization
full-universe or unbounded generation
silent registry mutation
silent promotion of candidate evidence
```

## Consumer Classes

Allowed in v0.1:

```text
runtime_internal_request_resolver
runtime_internal_execution_planner
runtime_internal_candidate_reuse_resolver
runtime_validator
applied_architecture_review
event_state_design_planning_metadata_only
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
```
