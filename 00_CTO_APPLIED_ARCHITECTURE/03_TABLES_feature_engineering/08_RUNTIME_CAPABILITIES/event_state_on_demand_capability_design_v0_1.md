# Event State On-Demand Capability Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Runtime Architecture: `runtime_capabilities_architecture_v0_1`
Authorization: `event_state_on_demand_capability_design_authorization_v0_1`

This document defines the first Event State on-demand runtime capability. It is
design-only. It does not execute requests, detect events, create Event
Instances, bind windows, consume physical Market State, materialize Event State,
write registry entries or authorize downstream consumption.

## 1. Capability Definition

```text
Event State on-demand capability
    = the governed ability to accept an Event State request
      and later, only when separately authorized, resolve:

        Event State profile
        Event Type registry authority
        Event Instance policy
        Event Window policy
        Instrument Projection policy
        Market State dependency
        Execution Plan
        Materializer
        Validator
        Candidate Dataset Registry
```

The capability is not the same as an official Event State dataset.

```text
official Event State semantic profile exists = true
official Event State physical dataset exists = false
runtime capability design exists = true
runtime capability execution exists = false
```

## 2. Supported Initial Semantic Scope

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
accepted_event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
halt_resumed_allowed = false
complete_tsis_event_state = false
```

The initial capability design is scoped to `session_opened` only. It does not
admit `halt_resumed`, does not execute detectors and does not populate Event
Instances.

## 3. Request-Centered Flow

```text
Event State Request
-> request contract validation
-> Event State profile resolver
-> Event Type registry resolver
-> Event Instance policy resolver
-> Event Window policy resolver
-> Instrument Projection policy resolver
-> Market State dependency resolver
-> Event State execution plan, only in a later design gate
-> materializer, only after future execution authorization
-> validator, only after future execution authorization
-> candidate dataset registry, only after future execution authorization
```

## 4. Market State Dependency Rule

Event State on-demand depends on the promoted restricted Market State runtime
capability. It must not depend on a hard-coded Market State parquet path.

```text
source_market_state_capability_design_id = market_state_on_demand_capability_v0_1
source_market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
identity_relation = promoted_runtime_identity_of
source_market_state_consumption_policy = market_state_capability_consumption_policy_v0_1
source_market_state_consumption_policy_status_required = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
official_market_state_dataset_required = false
direct_candidate_path_consumption_allowed = false
```

The future Market State Dependency Resolver must either emit or resolve a Market
State subrequest through the governed Market State runtime capability.

It must not do this:

```text
Event State resolver
-> search for Market State parquet
-> read it directly
```

It must do this instead:

```text
Event State request
-> calculate required Market State dependency
-> emit or resolve Market State dependency request
-> consult promoted restricted Market State runtime capability
-> receive candidate metadata or authorized candidate reference
-> defer physical consumption to a later explicit authorization
```

## 5. Permission Model

The design distinguishes policy permission under a future gate from the current
gate execution permission.

```text
policy_permission_under_separate_authorization:
    Market State metadata inspection = true
    Market State candidate reuse resolution = true
    Market State candidate file service to runtime validation = conditional future permission
    Event State candidate generation = requires future bounded execution authorization

current_gate_execution_permission:
    event_state_requests_created = 0
    market_state_dependency_requests_created = 0
    event_instances_created = 0
    event_window_bindings_created = 0
    instrument_projections_created = 0
    market_state_candidate_files_read = 0
    event_state_records_emitted = 0
    datasets_written = 0
    registry_entries_written = 0
```

```text
design_time_market_state_access = metadata_only
execution_time_market_state_access = requires_separate_dependency_execution_authorization
direct_candidate_path_consumption = false
```

## 6. Historical Policy Handling

The Event State operational registry / consumption policy document remains a
historical closed design artifact. It still records the next gate that was true
at its own closure time.

```text
historical_next_gate_at_policy_closure = market_state_on_demand_capability_design_authorization_v0_1
current_next_gate_authority = 99_ruta_de_trabajo.md + AGENT.md + 08_RUNTIME_CAPABILITIES/README.md
```

This design does not rewrite that historical policy because its hash is already
used as evidence in later authorization scope.

## 7. Required Future Component Designs

```text
event_state_request_contract_design_v0_1
event_state_dependency_resolution_design_v0_1
event_state_execution_plan_contract_design_v0_1
event_state_materializer_design_v0_1
event_state_validator_design_v0_1
event_state_candidate_dataset_registry_design_v0_1
```

The next immediate gate is the Event State request contract. That contract must
answer what a user can ask for before any resolver decides how to build it.

## 8. Required Future Fingerprints

```text
event_state_request_fingerprint
market_state_dependency_request_fingerprint
market_state_candidate_dataset_fingerprint
event_type_registry_snapshot_id
event_instance_policy_version
event_window_policy_version
instrument_projection_policy_version
event_state_execution_plan_fingerprint
```

These identifiers prevent future Event State output from depending on an
untracked or merely compatible Market State table.

## 9. Blocking Rules For Future Requests

Future Event State requests must block before execution if any of the following
are unresolved:

```text
Event State profile is not official as semantic profile
Event Type is not accepted or is outside scope
subject scope is not exchange_session for session_opened v0.1
Market State consumption policy is missing
Market State dependency resolution is ambiguous
direct Market State parquet path consumption is attempted
Event Instance policy is missing
Event Window policy is missing
Instrument Projection policy is missing
execution authorization is missing
```

## 10. Closure

```text
event_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_requests_created = 0
market_state_dependency_requests_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_records_emitted = 0
datasets_written = 0
registry_entries_written = 0
official_event_state_dataset = false
production = false
downstream_consumption = false

next_allowed_gate = event_state_request_contract_design_v0_1
```
