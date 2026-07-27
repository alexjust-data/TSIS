# Event State On-Demand Capability Design Readout v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`

```text
gate = event_state_on_demand_capability_design_v0_1
capability_id = event_state_on_demand_capability_v0_1
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
accepted_event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
source_market_state_capability_design_id = market_state_on_demand_capability_v0_1
source_market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
identity_relation = promoted_runtime_identity_of
design_time_market_state_access = metadata_only
execution_time_market_state_access = requires_separate_dependency_execution_authorization
direct_candidate_path_consumption = false
event_state_requests_created = 0
market_state_dependency_requests_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_candidate_files_read = 0
event_state_records_emitted = 0
datasets_written = 0
registry_entries_written = 0
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_request_contract_design_v0_1
```

The design closes as a runtime capability design only. It defines the future
Event State request/resolution/materialization/validation/registry chain and the
Market State Dependency Resolver principle, but it does not execute any part of
that chain.
