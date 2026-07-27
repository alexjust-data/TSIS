# Event State Request Contract Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`

```text
gate = event_state_request_contract_design_v0_1
parent_gate = event_state_on_demand_capability_design_v0_1
contract = event_state_request_contract_v0_1
request_type = event_state
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_type_scope_v0_1 = event_type:market_data:session_opened
accepted_subject_scope_v0_1 = exchange_session
event_state_profile_version_policy_v0_1 = exact
event_type_registry_snapshot_policy_v0_1 = exact
market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability
source_market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
direct_market_state_path_consumption = false
output_mode_v0_1 = candidate
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
next_allowed_gate = event_state_dependency_resolution_design_v0_1
```

The Event State request contract now defines normalized request intent for the initial `session_opened` / `exchange_session` scope. It does not resolve dependencies, create Event Instances, bind windows, consume Market State, materialize data or register outputs.

The next gate should define dependency resolution: how a validated Event State request resolves Event Type registry authority, Event Instance policy, Event Window policy, Instrument Projection policy and Market State dependency subrequest semantics before execution planning.