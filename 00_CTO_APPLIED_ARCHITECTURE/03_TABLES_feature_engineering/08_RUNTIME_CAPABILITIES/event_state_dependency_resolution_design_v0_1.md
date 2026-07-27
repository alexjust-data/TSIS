# Event State Dependency Resolution Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_request_contract_design_v0_1`

This document defines the dependency-resolution design for future Event State on-demand generation.

It is design-only. It does not create dependency-resolution records, create Event Instances, bind windows, project instruments, execute Market State dependency requests, read Market State candidate files, create Event State execution plans, materialize Event State, write datasets or write registry entries.

## 1. Contract Principle

```text
Event State Request
    = what event-conditioned representation is required

Resolved Event State Dependencies
    = all governed dependencies resolved exactly once before planning

Event State Execution Plan
    = frozen construction instructions produced later
```

The future execution plan must consume a resolved dependency block. The materializer must not resolve profile, Event Type, Event Instance policy, Event Window policy, Instrument Projection policy or Market State dependency by itself.

## 2. Input

The resolver consumes only a validated Event State request:

```text
event_state_request_contract = event_state_request_contract_v0_1
request_type = event_state
event_state_request_fingerprint = required
request_status = VALIDATED_INTENT_NO_EXECUTION
```

This design creates no request records and executes no resolver.

## 3. Resolved Dependency Blocks

### 3.1 Event State Profile

```text
profile_id = event_state_core_four_intraday_profile_v0_1
required_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
profile_manifest = official_profiles/event_state_core_four_intraday_profile_v0_1/PROFILE_MANIFEST.json
official_physical_dataset_required = false
official_event_state_parquet_required = false
```

The profile is semantic authority, not a physical dataset authority.

### 3.2 Event Type Registry

```text
registry_snapshot_id = tsis_event_type_registry_v0_1_post_initial_admission_001
registry_snapshot_sha256 = f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43
accepted_event_type_ids_v0_1 = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
halt_resumed_allowed = false
event_detection_allowed = false
```

Only accepted or accepted-with-restrictions Event Types can resolve. For v0.1 the only accepted Event Type in scope is `session_opened`.

### 3.3 Event Instance Policy

```text
contract_id = event_instance_binding_design_contract_v0_1
native_subject_scope = exchange_session
native_grain = event_type_id + exchange_id + session_date + calendar_version + event_anchor_timestamp_utc
instrument_id_in_native_identity = false
detector_required = false
future_instance_creation_authorized_by_this_gate = false
```

Resolution may select the governed policy. It may not create Event Instances.

### 3.4 Event Window Policy

```text
contract_id = event_window_binding_design_contract_v0_1
state_roles = pre_event | at_event | post_event | post_event_review
consumption_legality_classes = decision_safe | research_only | outcome_adjacent | prohibited_as_input
future_window_binding_creation_authorized_by_this_gate = false
```

Resolution may select window policy authority. It may not bind windows.

### 3.5 Instrument Projection Policy

```text
contract_id = event_state_instrument_session_projection_design_contract_v0_1
projection_required_for_instrument_contexts = true
projection_must_not_change_native_event_instance_identity = true
future_projection_creation_authorized_by_this_gate = false
```

Instrument association remains a projection over an exchange-session Event Instance.

### 3.6 Market State Dependency

```text
market_state_profile_id = market_state_core_four_intraday_profile_v0_1
market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
market_state_capability_design_id = market_state_on_demand_capability_v0_1
identity_relation = promoted_runtime_identity_of
market_state_consumption_policy = market_state_capability_consumption_policy_v0_1
dependency_request_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability
direct_market_state_path_allowed = false
market_state_physical_consumption_authorized_by_this_gate = false
```

The resolver must produce Market State dependency request semantics. It must not search or read a Market State parquet path directly.

## 4. Exact-One Resolution

Each dependency must resolve exactly once:

```text
one request fingerprint -> one dependency resolution candidate
one profile request -> one profile contract
one event_type_id -> one accepted registry entry
one event_instance_policy_id -> one policy contract
one event_window_policy_id -> one policy contract
one projection policy id -> one policy contract
one Market State dependency intent -> one Market State subrequest semantics
```

Zero or multiple candidates block before execution planning.

## 5. Blocking Conditions

The resolver must block if:

```text
validated request missing
request type is not event_state
request fingerprint missing
Event State profile missing or not official semantic profile
Event Type Registry snapshot missing or hash mismatch
Event Type not accepted
Event Type outside v0.1 scope
subject scope is not exchange_session
halt_resumed requested
event detection requested
Event Instance policy missing
Event Window policy missing
Instrument Projection policy missing
Market State runtime capability missing
Market State consumption policy missing or not restricted candidate runtime
Market State dependency direct path requested
Market State dependency subrequest semantics ambiguous
multiple candidates resolve for a required dependency
Execution State or Outcome requested as Event State
physical consumption attempted in design gate
```

Blocked dependency resolution is a valid governance result. It must not be repaired by fallback inference.

## 6. Dependency Resolution Fingerprint

The future `event_state_dependency_resolution_fingerprint` must include:

```text
event_state_request_fingerprint
event_state_profile_id
event_state_profile_contract_hash
event_type_registry_snapshot_id
event_type_registry_snapshot_sha256
accepted_event_type_ids
accepted_subject_scope
event_instance_policy_contract_hash
event_window_policy_contract_hash
instrument_projection_policy_contract_hash
market_state_runtime_capability_id
market_state_consumption_policy_hash
market_state_dependency_request_fingerprint
blocking_findings
```

It must exclude:

```text
resolution_record_id
resolved_at_utc
resolver_run_id
machine_id
temporary path
log path
heartbeat
```

## 7. Boundary To Execution Plan

The next gate must define:

```text
event_state_execution_plan_contract_design_v0_1
```

The execution plan will freeze resolved dependencies plus builders, validators, output policy, quantitative limits and future run constraints. It must not leave unresolved version policies or physical consumption authority implicit.

## 8. Closure

```text
event_state_dependency_resolution_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

dependency_resolution_records_created = 0
event_state_execution_plans_created = 0
event_state_requests_executed = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_dependency_requests_created = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_records_emitted = 0
event_state_datasets_written = 0
event_state_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = event_state_execution_plan_contract_design_v0_1
```