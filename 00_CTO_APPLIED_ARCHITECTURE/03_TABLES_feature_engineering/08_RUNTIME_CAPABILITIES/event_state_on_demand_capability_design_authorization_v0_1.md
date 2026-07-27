# Event State On-Demand Capability Design Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-27`
Scope: `design_only_no_execution`

This authorization opens only the design of an Event State on-demand runtime
capability under `08_RUNTIME_CAPABILITIES`.

It consumes the fact that Market State on-demand now has an explicit restricted
consumption policy. It does not authorize Event State request execution, event
detection, Event Instance generation, Market State physical consumption, Event
State materialization, production or downstream consumption.

## Authorized Design Scope

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_state_profile_status_required = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
accepted_event_type_ids_allowed_for_design = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
halt_resumed_allowed = false
source_market_state_capability_policy_required = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
official_market_state_dataset_required = false
```

## Authorized Outputs

```text
configs/event_state_on_demand_capability_design_scope_v0_1.json
event_state_on_demand_capability_design_v0_1.md
event_state_on_demand_capability_contract_v0_1.json
event_state_on_demand_capability_design_readout_v0_1.md
```

## Boundaries

```text
event_state_request_execution_allowed = false
event_detection_allowed = false
event_instance_generation_allowed = false
event_window_generation_allowed = false
instrument_projection_execution_allowed = false
market_state_physical_consumption_allowed = false
event_state_materializer_execution_allowed = false
event_state_validator_execution_allowed = false
event_state_dataset_write_allowed = false
event_state_registry_write_allowed = false
official_event_state_dataset_promotion_allowed = false
production_allowed = false
downstream_consumption_allowed = false
```

## Closure

```text
accepted_design = event_state_on_demand_capability_design_v0_1
design_status = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
requests_executed = 0
market_state_dependency_requests_created = 0
event_instances_created = 0
event_window_bindings_created = 0
event_state_records_emitted = 0
datasets_written = 0
registry_entries_written = 0
next_allowed_gate = event_state_request_contract_design_v0_1
```
