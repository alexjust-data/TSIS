# Event State On-Demand Bounded Deterministic Rerun Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`

```text
gate = event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1
parent_gate = event_state_on_demand_bounded_candidate_dataset_review_v0_1
authorized_next_gate = event_state_on_demand_bounded_deterministic_rerun_v0_1
authorization_scope = bounded_event_state_deterministic_rerun_only
baseline_execution_run_id = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z
baseline_review_run_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T202013Z
baseline_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33
baseline_logical_dataset_fingerprint = 1b981958488e69f8f553c9197861bbffeed2d5388437c1113f9e21422b9cf970
requested_contexts = 9
represented_contexts = 8
unavailable_contexts = 1
event_state_candidate_records = 8
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
determinism_comparisons_created = 0
registry_entries_written = 0
event_state_records_emitted = 0
datasets_written = 0
reuse_eligibility_changes = 0
official_dataset = false
production = false
downstream = false
```

The deterministic rerun authorization is recorded. It freezes the approved
bounded Event State candidate as the baseline and authorizes exactly one future
rerun to rebuild Event State from the same governed request, dependencies,
Event Type Registry snapshot, policies, bindings, builders and validators.

The key boundary is:

```text
Event State candidate reuse = prohibited
Event State materializer execution = required
Market State dependency rematerialization = not required
Market State dependency exact runtime reuse = allowed only if fingerprints match
```

The Market State dependency remains:

```text
market_state_dependency_request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
market_state_dependency_execution_plan_fingerprint = 5555fed758d30b6c8f281517eb747523d3dfaf9bbae1713b4e9f1c28c6fdd733
market_state_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
```

The future rerun must reproduce:

```text
same 3 native Event Instances
same 3 Event Window Bindings
same 9 Instrument Session Projections
same 8 represented Event State record IDs
same 8 Event State record fingerprints
same 8 source Market State record bindings
same unavailable AAME 2022-11-25 context
same state_role = at_event
same consumption_legality = research_only
same restrictions and lineage semantics
```

This gate created no request, no run, no Event Instance, no window, no
projection, no materialization, no validation report, no comparison, no registry
entry and no dataset. It changed no reuse eligibility and opened no official
dataset, production or downstream authority.

The next allowed gate is:

```text
event_state_on_demand_bounded_deterministic_rerun_v0_1
```
