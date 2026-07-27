# Event State On-Demand Capability Design Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`

```text
authorization_id = event_state_on_demand_capability_design_authorization_v0_1
target_design_gate = event_state_on_demand_capability_design_v0_1
market_state_consumption_policy = market_state_capability_consumption_policy_v0_1
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
accepted_event_type_ids_allowed_for_design = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
event_state_request_execution_allowed = false
event_detection_allowed = false
event_instances_created = 0
event_window_bindings_created = 0
market_state_physical_consumption_allowed = false
event_state_records_emitted = 0
datasets_written = 0
registry_entries_written = 0
official_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_on_demand_capability_design_v0_1
```

The authorization records a design-only opening for Event State on-demand. It
allows the next gate to define request, dependency resolution, materializer,
validator and registry concepts for Event State on-demand. It does not execute
or materialize Event State.
