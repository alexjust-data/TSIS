# Event State On-Demand Bounded Deterministic Rerun Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`

```text
gate = event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1
parent_gate = event_state_on_demand_bounded_candidate_dataset_review_v0_1
authorized_next_gate = event_state_on_demand_bounded_deterministic_rerun_v0_1
authorization_scope = bounded_event_state_deterministic_rerun_only
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

This authorization opens exactly one future deterministic rerun gate for the
first bounded Event State on-demand candidate dataset.

It does not execute that rerun.

## Baseline Authority

The rerun must use the candidate approved by:

```text
baseline_review_gate = event_state_on_demand_bounded_candidate_dataset_review_v0_1
baseline_review_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T000000Z
baseline_review_run_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T202013Z
baseline_review_status = CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION
baseline_execution_run_id = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z
baseline_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
baseline_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33
baseline_logical_dataset_fingerprint = 1b981958488e69f8f553c9197861bbffeed2d5388437c1113f9e21422b9cf970
baseline_validation_result_fingerprint = 2f4797da1a74c06a7061fe1e597299d0d1e9f5d55c82ec147ff66b5891550361
baseline_registry_entry_fingerprint = 5a78f487ee549ff38e13547bf0324add50556e9aed054a536017b6a4f111fa4b
```

## Frozen Baseline Fingerprints

```text
event_state_request_fingerprint = f82e424b60a69e2e9edec00e3dcf456c2042d18b334366dab76622286fac6ade
event_state_dependency_resolution_fingerprint = c89dc7ece24ba916dadd1046b8784b66febe6c91175781a6a609f3ae2f379ec8
event_state_execution_plan_fingerprint = 2dc97d398c7c7dd56789628be951b96a19c7f2389febe1c5922d753a7f7f4276
event_type_registry_snapshot_sha256 = f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43
market_state_dependency_request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
market_state_dependency_execution_plan_fingerprint = 5555fed758d30b6c8f281517eb747523d3dfaf9bbae1713b4e9f1c28c6fdd733
market_state_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
market_state_validation_result_fingerprint = 38064d86af50c4a2df2ec0d2561b25390421df7acad4679e957faceaf1791fdb
```

## Frozen Baseline Content

```text
requested_event_state_contexts = 9
represented_event_state_contexts = 8
unavailable_event_state_contexts = 1
event_state_candidate_records = 8
native_event_instances = 3
event_window_bindings = 3
instrument_session_projections = 9
market_state_bindings_found = 8
missing_exact_market_state_bindings = 1
fallback_uses = 0
hard_validation_failures = 0
```

The unavailable context is frozen as:

```text
instrument_id = figi_share_class:BBG001S5N8T1
ticker_label_non_authoritative = AAME
session_date = 2022-11-25
exchange_id = XNYS
event_anchor_timestamp_utc = 2022-11-25T14:30:00Z
blocking_reason = missing_exact_market_state_binding
fallback_used = false
```

## Rerun Policy

The future rerun must rebuild Event State, not reuse the previous Event State candidate:

```text
event_state_reuse_policy = force_rebuild_for_determinism_test
reuse_existing_event_state_candidate = false
return_event_state_registry_match_without_materializer = false
skip_event_state_materializer = false
event_state_materializer_execution_required = true
new_event_state_candidate_output_required = true
```

The Market State dependency must be resolved again through the promoted runtime capability, but it is not forced to rematerialize Market State:

```text
market_state_dependency_mode = resolve_same_runtime_subrequest
market_state_dependency_reuse_policy = reuse_if_exact_validated_dependency_match_or_block
market_state_dependency_expected_request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
market_state_dependency_expected_execution_plan_fingerprint = 5555fed758d30b6c8f281517eb747523d3dfaf9bbae1713b4e9f1c28c6fdd733
market_state_dependency_expected_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
market_state_dependency_switch_allowed = false
market_state_dependency_rematerialization_required = false
```

This separation is mandatory. The gate tests deterministic Event State
reconstruction, not a fresh Market State runtime materialization.

## Required Comparison Artifact

The future rerun must emit:

```text
event_state_bounded_deterministic_rerun_comparison_v0_1.json
```

The comparison must verify:

```text
request_fingerprint_match
dependency_resolution_fingerprint_match
execution_plan_fingerprint_match
event_type_registry_snapshot_match
event_instance_set_match
event_window_binding_set_match
instrument_projection_set_match
market_state_dependency_fingerprint_match
market_state_binding_set_match
event_state_record_id_set_match
event_state_record_fingerprint_set_match
state_output_fingerprint_set_match
normalized_record_content_match
unavailable_context_set_match
restriction_set_match
lineage_semantics_match
validation_status_match
```

## Allowed Runtime Differences

Only predeclared runtime fields may differ:

```text
rerun_run_id
created_at_utc
started_at_utc
finished_at_utc
heartbeat_timestamps
run_local_output_paths
authorization_consumption_timestamp
event_state_materialization_run_id
runtime_manifest_identity_if_path_or_timestamp_dependent
physical_file_hash_if serialization contains run-local metadata
```

No post-hoc allowlist expansion is authorized.

## Closure Expectations

If the normalized scientific result matches:

```text
expected_closure = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS
scientific_determinism = PROVEN_FOR_BOUNDED_SCOPE
reuse_transition_ready = true
reuse_eligibility_changes = 0
```

If the prior Event State candidate is returned without rebuilding:

```text
closure = CLOSED_FAIL_FORCE_REBUILD_NOT_PROVEN
```

If the Market State dependency resolves to a different scientific dependency:

```text
closure = CLOSED_BLOCKED_MARKET_STATE_DEPENDENCY_CHANGED
```

If Event State content differs outside allowed runtime fields:

```text
closure = CLOSED_BLOCKED_DETERMINISM_FAILURE
```

## Explicit Prohibitions

This authorization does not allow:

```text
reuse of the previous Event State candidate as output
Event State registry cache hit as execution substitute
new Event Types
halt_resumed
event detection
instrument-level native session_opened identity
new Market State profiles
fresh Market State materialization as part of this Event State determinism test
official Event State dataset promotion
official Market State dataset promotion
production
downstream consumption
backtesting
ML/RL consumption
strategy evaluation
reuse eligibility transition
incremental Event State execution
scale validation
```

## Closure

This document records authorization only. It does not consume the authorization.

The next allowed gate is:

```text
event_state_on_demand_bounded_deterministic_rerun_v0_1
```
