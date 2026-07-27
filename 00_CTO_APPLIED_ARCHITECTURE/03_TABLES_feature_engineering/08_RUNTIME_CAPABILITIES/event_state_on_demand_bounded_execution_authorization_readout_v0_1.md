# Event State On-Demand Bounded Execution Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`

```text
gate = event_state_on_demand_bounded_execution_authorization_v0_1
parent_gate = event_state_on_demand_execution_chain_joint_review_v0_1
authorized_next_gate = event_state_on_demand_bounded_execution_v0_1
authorized_requests_max = 1
authorized_dependency_resolutions_max = 1
authorized_execution_plans_max = 1
authorized_runs_max = 1
authorized_event_types_max = 1
authorized_exchanges_max = 1
authorized_sessions_max = 3
authorized_native_event_instances_max = 3
authorized_instruments_max = 3
authorized_instrument_session_projections_max = 9
authorized_market_state_dependency_contexts_max = 9
authorized_event_state_logical_contexts_max = 9
authorized_event_state_candidate_records_max = 9
event_state_requests_created = 0
dependency_resolver_executions = 0
execution_plans_created = 0
run_records_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_dependency_requests_executed = 0
market_state_candidate_files_read = 0
event_state_materializer_executions = 0
event_state_validator_executions = 0
registry_entries_written = 0
event_state_records_emitted = 0
datasets_written = 0
production = false
downstream = false
```

The first Event State on-demand bounded execution authorization is recorded. It freezes the next gate to a single small candidate run:

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_type_id = event_type:market_data:session_opened
subject_scope = exchange_session
exchange_scope = XNYS
session_dates = 2021-01-19, 2021-03-15, 2022-11-25
instrument_projection_scope = AAME, ABEO, ABUS stable FIGI share-class identifiers
maximum_event_state_logical_contexts = 9
output_mode = candidate
```

Native Event Instance identity remains exchange-session scoped. Instrument association is authorized only as a projection:

```text
native_event_instance_identity_includes_instrument_id = false
instrument_association_mode = instrument_session_projection_only
```

The future execution must resolve Market State dependency through the promoted Market State runtime capability and the consumption policy:

```text
market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
market_state_consumption_policy = market_state_capability_consumption_policy_v0_1
direct_market_state_path_authority = false
```

If bounded Market State dependency authority, fingerprint match or artifact availability cannot be proven, the future execution must close blocked before Event State materialization.

This gate created no Event State request, no dependency resolution, no execution plan, no run record, no Event Instance, no Event Window Binding, no Instrument Projection, executed no Market State dependency request, read no Market State candidate file, executed no materializer, executed no validator, wrote no registry entry, emitted no Event State record and wrote no dataset.

The next allowed gate is:

```text
event_state_on_demand_bounded_execution_v0_1
```