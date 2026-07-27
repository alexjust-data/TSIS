# Event State Request Contract Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_on_demand_capability_design_v0_1`

This document defines the canonical request contract for future Event State on-demand generation.

It is design-only. It does not create a request, resolve dependencies, read Market State, detect events, create Event Instances, bind windows, project instruments, create an execution plan, build Event State, write datasets or write registry entries.

## 1. Contract Principle

```text
Event State Request
    = normalized user or system intent for an event-conditioned state table

Dependency Resolution
    = governed resolution of Event Type, Event Instance policy,
      Event Window policy, Instrument Projection policy and
      Market State dependency

Execution Plan
    = frozen construction instructions after dependency resolution
```

A request declares what event-conditioned representation is required. It must not decide how that representation will be built.

A request may name governed identities such as:

```text
event_state_profile_id
event_state_profile_version_policy
event_type_ids
event_type_registry_snapshot_id
event_subject_scope
event_instance_policy_id
event_window_policy_id
instrument_projection_policy_id
market_state_profile_id
market_state_dependency_mode
universe_definition_id or explicit_instrument_ids
session/date scope
calendar_authority_id
point_in_time_policy_id
output_mode
validation_level
reuse_policy
```

A request must not name or select:

```text
physical Market State parquet paths
Market State candidate file paths
Event State output paths
source parquet files
builder implementations
materializer implementations
validator implementations
resolved partitions
runtime registry dataset ids
broker/execution state fields
outcome/profit fields
machine-specific state
```

Those belong to later dependency resolution, execution planning or execution gates.

## 2. Required Blocks

### 2.1 Request Identity

```text
request_type
request_contract_version
request_id
requested_at_utc
requested_by
request_purpose
```

Only `request_type = event_state` is valid for this contract. `requested_at_utc` and `requested_by` are audit fields and do not participate in the semantic fingerprint.

### 2.2 Event State Representation Intent

```text
event_state_profile_id
event_state_profile_version_policy
event_state_profile_version
resolution
grain
```

For v0.1:

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_state_profile_version_policy = exact
```

### 2.3 Event Type Intent

```text
event_type_ids
event_type_registry_snapshot_policy
event_type_registry_snapshot_id
event_subject_scope
```

For v0.1:

```text
event_type_ids = [event_type:market_data:session_opened]
event_subject_scope = exchange_session
event_type_registry_snapshot_policy = exact
halt_resumed_allowed = false
event_detection_request_allowed = false
```

The request may ask for `session_opened` Event State context. It may not ask to detect new event types or include `halt_resumed`.

### 2.4 Event Occurrence And Window Intent

```text
event_instance_policy_id
event_anchor_policy_id
event_window_policy_id
event_window_definition_ids
```

These fields name governed policies. They do not create Event Instances or Event Window Bindings.

For `session_opened`, the native occurrence remains exchange-session scoped. Instrument association is a later projection, not native Event Type identity.

### 2.5 Instrument Scope And Projection Intent

```text
instrument_projection_policy_id
universe_definition_id
explicit_instrument_ids
universe_selection_mode
instrument_filter_mode
exchange_scope
start_date
end_date
session_dates
```

The request must define one temporal scope: either `start_date + end_date` or `session_dates`.

The request must define one universe selection mode: either `universe_definition_id` or `explicit_instrument_ids`. Both may appear together only if one is the primary universe and the other is an explicit filter.

### 2.6 Market State Dependency Intent

```text
market_state_dependency_mode
market_state_profile_id
market_state_profile_version_policy
market_state_profile_version
market_state_capability_policy_id
market_state_dependency_reuse_policy
```

For v0.1:

```text
market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability
market_state_profile_id = market_state_core_four_intraday_profile_v0_1
market_state_profile_version_policy = exact
market_state_capability_policy_id = market_state_capability_consumption_policy_v0_1
direct_market_state_candidate_path_allowed = false
```

The Event State request can declare the required Market State dependency. It cannot grant permission to read Market State files.

### 2.7 Temporal And Source Policy

```text
calendar_authority_id
point_in_time_policy_id
as_of_policy_id
source_version_policy
```

For v0.1:

```text
source_version_policy = exact_governed_or_block
```

No fallback is permitted.

### 2.8 Output Intent

```text
output_mode
output_format
partition_policy
validation_level
reuse_policy
```

For v0.1:

```text
output_mode = candidate
reuse_policy = reuse_if_exact_validated_dependency_match
```

Official output modes remain prohibited until a separate promotion and consumption authority exists.

## 3. Event State Request Fingerprint

The `event_state_request_fingerprint` is a deterministic hash of normalized request intent.

It must include the event profile, exact profile version policy, Event Type set, Event Type registry snapshot, subject scope, event policies, window policies, projection policy, instrument/date scope, temporal policy, Market State dependency intent, output intent, validation level and reuse policy.

It must exclude:

```text
request_id
requested_at_utc
requested_by
run_id
output_path
temporary path
machine id
heartbeat timestamps
wall-clock runtime values
physical Market State paths
```

Rule:

```text
same normalized Event State request intent
    -> same event_state_request_fingerprint
```

But:

```text
same event_state_request_fingerprint
    != guaranteed same Event State dataset
```

The future dependency resolution and execution plan fingerprints will capture exact Event Type registry snapshots, Event Instance policies, window policies, projection policies, Market State dependency request fingerprints, source fingerprints, builders, validators and outputs.

## 4. Validation And Blocking

The request contract must block before dependency resolution if:

```text
request_type is not event_state
event_state_profile_id is missing
event_state_profile_version_policy is not exact
event_state_profile_version is missing
event_type is not accepted or is outside v0.1 scope
event_subject_scope is not exchange_session
halt_resumed is requested
event detection is requested
event_instance_id is requested in v0.1
event_type_registry_snapshot_id is missing
event_type_registry_snapshot_policy is not exact
event_instance_policy_id is missing
event_window_policy_id is missing
instrument_projection_policy_id is missing
temporal scope is missing
universe selection is missing
calendar_authority_id is missing
point_in_time_policy_id is missing
source_version_policy permits fallback
market_state_dependency_mode does not use runtime capability subrequest
direct Market State path consumption is requested
output_mode is official or production
unknown fields attempt to name physical paths
Execution State or Outcome fields are requested as Event State
```

Blocked requests are valid governance outcomes. They must not be repaired by resolver inference.

## 5. Request Status Model

This contract defines statuses only for request records once a future gate authorizes request creation.

```text
DRAFT_REQUEST
VALIDATED_INTENT_NO_EXECUTION
BLOCKED_BEFORE_DEPENDENCY_RESOLUTION
RESOLVED_NO_EXECUTION
AUTHORIZED_FOR_BOUNDED_EXECUTION
RUNNING
VALIDATING
CLOSED_PASS_WITH_RESTRICTIONS
FAILED
QUARANTINED
```

This gate creates no request records.

## 6. Boundary To Dependency Resolution

The next gate must define:

```text
event_state_dependency_resolution_design_v0_1
```

Dependency resolution will consume a validated Event State request and resolve exact Event State profile contract, Event Type registry snapshot, Event Instance policy, Event Window policy, Instrument Projection policy and Market State dependency request semantics.

The materializer must later consume a frozen execution plan, not the raw request.

## 7. Closure

```text
event_state_request_contract_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_request_records_created = 0
event_state_requests_executed = 0
market_state_dependency_requests_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_execution_plans_created = 0
event_state_records_emitted = 0
event_state_datasets_written = 0
event_state_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = event_state_dependency_resolution_design_v0_1
```