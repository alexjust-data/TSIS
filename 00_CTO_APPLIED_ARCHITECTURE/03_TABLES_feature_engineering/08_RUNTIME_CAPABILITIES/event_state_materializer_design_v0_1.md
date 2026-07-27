# Event State Materializer Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_execution_plan_contract_design_v0_1`

This document defines the future Event State materializer.

It is design-only. It does not execute builders, create Event Instances, bind Event Windows, project instruments, execute or consume Market State dependency requests, read Market State candidate files, write Event State outputs, compute content hashes, create manifests, validate outputs or write registry entries.

## 1. Materializer Principle

```text
Event State Materializer
    = the future component that consumes one authorized frozen Event State execution plan
      and writes candidate Event State output artifacts.
```

The materializer must not:

```text
resolve Event State requests
resolve Event State profiles
resolve Event Type Registry entries
choose Event Types
run event detectors
choose Event Instance policies
choose Event Window policies
choose Instrument Projection policies
resolve Market State dependencies
search Market State parquet paths
choose builders
choose validators
alter output mode
promote datasets
authorize downstream consumption
```

It consumes plan decisions; it does not make them.

## 2. Required Future Inputs

The materializer may execute only when a later authorization provides:

```text
event_state_execution_plan_id
event_state_execution_plan_fingerprint
event_state_execution_plan_status = authorized_for_execution
event_state_request_fingerprint
event_state_dependency_resolution_fingerprint
resolved_request block
resolved_event_state_dependencies block
event_type_and_registry_plan block
event_instance_plan block
event_window_plan block
instrument_projection_plan block
market_state_dependency_plan block
logical_context_and_binding_plan block
partition_and_coverage block
resolved_builders block
output_plan block
quantitative_limits block
```

If any required plan block is missing, materialization must block before Event State rows or dependency artifacts are created.

## 3. Materializable Dispositions

For v0.1:

```text
materializable_dispositions =
    to_build
    to_rebuild
```

The materializer may reference but must not rebuild:

```text
reusable_validated
```

The materializer must not process:

```text
unavailable
blocked
quarantined
```

Partial execution remains prohibited unless a later execution authorization explicitly permits a subset of logical partitions.

## 4. Event Instance, Window And Projection Boundary

The materializer may only create future candidate Event Instance, Event Window Binding or Instrument Projection artifacts when the frozen execution plan and a later execution authorization explicitly allow it.

For v0.1:

```text
event_type_id = event_type:market_data:session_opened
native_subject_scope = exchange_session
instrument_id_in_native_event_instance_identity = false
detector_required = false
```

The materializer must preserve:

```text
regular_session_open_timestamp != first_observed_trade_timestamp
```

and must not convert execution facts, outcomes or broker state into Event Type identity.

## 5. Market State Dependency Boundary

Market State may enter Event State materialization only through the dependency plan:

```text
market_state_runtime_capability_id
market_state_capability_policy_id
market_state_dependency_request_fingerprint
market_state_dependency_execution_plan_fingerprint_or_ref
market_state_candidate_dataset_fingerprint_or_ref
market_state_dependency_access_mode
```

The materializer must not:

```text
search for Market State parquet directly
consume a physical path named outside the plan
substitute a different Market State profile
reuse a Market State candidate whose fingerprint does not match the plan
read Market State candidate files without later execution authorization
```

## 6. Exact-One Binding Responsibility

For every future Event State logical context, the materializer must enforce exactly-one binding for:

```text
Event Instance
Event Window
Instrument Projection
Market State Record or governed Market State candidate reference
State Role
Consumption Legality
```

If any binding is missing, duplicated, ambiguous or outside the plan, the materializer must block the context instead of emitting a partial Event State row.

## 7. Build Responsibility

The future materializer orchestrates Event State builder execution exactly as frozen in the execution plan:

```text
event_state_builder_id
event_state_builder_version
builder_contract_hash
input_dependency_blocks
output_record_schema_id
state_role_policy_id
consumption_legality_policy_id
```

It must not substitute builder versions, infer missing builder definitions or generate output columns outside the output schema.

## 8. Output Staging And Atomic Commit

A future materialization run must use:

```text
staging_root
candidate_output_root
execution_run_id
atomic_commit_policy
```

Required behavior:

```text
write to staging
complete all authorized candidate outputs
compute candidate output hashes
write output and lineage manifests
leave validation to the validator gate
commit only after the future run policy allows
```

This design does not authorize staging directory creation, content hash computation or output writes.

## 9. Candidate Output Status

The materializer may only create future outputs with:

```text
output_status = candidate_unvalidated
```

A validator gate may later move the output to:

```text
validated_candidate
quarantined_candidate
failed_candidate
```

The materializer must not create:

```text
official_dataset
production_dataset
downstream_consumable_dataset
```

## 10. Required Future Artifacts

Future materializer execution must be able to emit:

```text
event_state_candidate_data_files
event_state_candidate_output_manifest.json
event_state_lineage_manifest.json
event_instance_candidate_manifest_or_binding_report.json
event_window_binding_report.json
instrument_projection_report.json
market_state_dependency_binding_report.json
logical_context_build_report.json
blocked_binding_report.json
builder_execution_report.json
materializer_run_readout.md
```

These artifacts are not created by this design gate.

## 11. Manifest Requirements

The future output manifest must preserve:

```text
event_state_request_fingerprint
event_state_dependency_resolution_fingerprint
event_state_execution_plan_fingerprint
event_state_profile_contract_hash
event_type_registry_snapshot_sha256
event_instance_policy_contract_hash
event_window_policy_contract_hash
instrument_projection_policy_contract_hash
market_state_dependency_request_fingerprint
market_state_candidate_dataset_fingerprint_or_ref
builder_contract_hashes
output_schema_hash
candidate_file_hashes
logical_context_counts
materialized_context_counts
blocked_or_skipped_context_counts
```

## 12. Lineage Requirements

For each candidate Event State output context, lineage must preserve:

```text
logical_context_id
partition_disposition_consumed
event_type_id
event_instance_id_or_candidate_ref
event_window_binding_id_or_candidate_ref
instrument_projection_id_or_candidate_ref
market_state_record_id_or_candidate_ref
market_state_candidate_dataset_fingerprint_or_ref
state_role
consumption_legality
builder_id
builder_version
event_state_profile_contract_hash
event_type_registry_snapshot_id
market_state_dependency_request_fingerprint
```

## 13. Blocking Rules

The future materializer must block before emitting rows if:

```text
execution_plan_status_not_authorized
execution_plan_fingerprint_missing
execution_plan_contains_unresolved_blocks
required_dependency_resolution_missing
unsupported_event_type_requested
subject_scope_not_exchange_session
event_detection_requested
native_event_instance_identity_contains_instrument_id
market_state_dependency_direct_path_requested
market_state_dependency_fingerprint_missing
market_state_candidate_reference_unavailable_when_required
market_state_candidate_fingerprint_mismatch
logical_context_binding_policy_missing
exact_one_binding_failure
partition_disposition_not_materializable
partial_execution_not_authorized
builder_contract_missing
output_schema_missing
output_plan_missing
quantitative_limits_missing
candidate_output_root_authority_missing
atomic_commit_policy_missing
```

## 14. Boundary To Validator

The next gate must design:

```text
event_state_validator_design_v0_1
```

The validator may inspect candidate outputs and decide validation status in a future execution gate. The materializer must not self-certify its outputs.

## 15. Closure

```text
event_state_materializer_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_materializer_executions = 0
event_state_builder_executions = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_dependency_requests_executed = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_records_emitted = 0
event_state_candidate_files_written = 0
event_state_output_manifests_created = 0
event_state_lineage_manifests_created = 0
event_state_validation_reports_created = 0
event_state_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = event_state_validator_design_v0_1
```
