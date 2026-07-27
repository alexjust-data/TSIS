# Event State Execution Plan Contract Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_dependency_resolution_design_v0_1`

This document defines the canonical Event State execution plan contract for future Event State on-demand generation.

It is design-only. It does not create a real execution plan, execute resolvers, create Event Instances, bind Event Windows, project instruments, execute Market State dependency requests, read Market State files, build Event State, write datasets or write registry entries.

## 1. Contract Principle

```text
Event State Request
    = what Event State representation is required

Event State Dependency Resolution
    = which governed dependencies the request may use

Event State Execution Plan
    = complete, immutable and reproducible resolution consumed by a future materializer
```

A future Event State materializer must consume a frozen execution plan. It must not re-resolve:

```text
request intent
Event State profile
Event Type Registry snapshot
Event Type status
Event Instance policy
Event Window policy
Instrument Projection policy
Market State dependency request
Market State candidate dependency
logical contexts
partition dispositions
builders
validators
output policy
quantitative limits
```

## 2. Plan Genealogy

Every Event State execution plan must derive from exactly one normalized Event State request and exactly one dependency-resolution block.

Required fields:

```text
event_state_execution_plan_id
event_state_execution_plan_contract_version
event_state_request_id
event_state_request_fingerprint
dependency_resolution_record_id_or_ref
event_state_dependency_resolution_fingerprint
created_at_utc
planner_id
planner_version
planner_contract_hash
```

`created_at_utc` is audit lineage. It does not participate in the semantic execution-plan fingerprint.

## 3. Resolved Request Block

The plan must embed or reference the normalized request meaning:

```text
request_contract_id
request_contract_hash
request_type
event_state_profile_id
event_state_profile_version
event_type_ids
event_subject_scope
resolution
grain
output_mode
reuse_policy
```

No unresolved policy such as `latest`, `compatible`, `default` or implicit version selection may remain in the plan.

## 4. Resolved Dependency Block

The plan must consume `resolved_event_state_dependencies_v0_1` and freeze all dependency identities:

```text
resolved_event_state_profile
resolved_event_type_registry
resolved_event_instance_policy
resolved_event_window_policy
resolved_instrument_projection_policy
resolved_market_state_dependency
event_state_dependency_resolution_fingerprint
```

Rule:

```text
one required dependency
    = exactly one governed resolution
```

Zero or multiple governed resolutions block the plan.

## 5. Event Type And Registry Plan

For v0.1 the plan is limited to:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
detector_required = false
event_detection_allowed = false
```

The plan must freeze:

```text
event_type_registry_snapshot_id
event_type_registry_snapshot_sha256
accepted_event_type_ids
blocked_event_type_ids
accepted_subject_scope
detector_required
event_detection_allowed
```

`event_type:regulatory:halt_resumed` remains outside execution-plan scope until separately admitted.

## 6. Event Instance Plan

The plan must freeze the policy that will later create or bind Event Instances, without creating them in this gate.

Required fields:

```text
event_instance_policy_contract_id
event_instance_policy_contract_hash
native_subject_scope
native_instance_grain
instrument_id_in_native_identity
event_anchor_timestamp_policy_id
first_observable_timestamp_policy_id
detector_required
future_instance_generation_authorized_by_plan
```

For `session_opened`, the native identity remains exchange-session level. `instrument_id` must not enter native Event Instance identity.

## 7. Event Window Plan

Required fields:

```text
event_window_policy_contract_id
event_window_policy_contract_hash
event_window_definition_ids_or_manifest_ref
state_role_set
consumption_legality_class_set
window_binding_grain
future_window_binding_generation_authorized_by_plan
```

The plan must preserve:

```text
state_role != consumption_legality
```

## 8. Instrument Projection Plan

Required fields:

```text
instrument_projection_policy_contract_id
instrument_projection_policy_contract_hash
projection_required_for_instrument_contexts
projection_grain
projection_must_not_change_native_event_instance_identity
future_projection_generation_authorized_by_plan
```

Instrument projection may contextualize an exchange-session Event Instance. It must not rewrite native Event Instance identity.

## 9. Market State Dependency Plan

The Event State plan may depend on Market State only through the promoted restricted runtime capability.

Required fields:

```text
market_state_profile_id
market_state_profile_version
market_state_runtime_capability_id
market_state_capability_policy_id
market_state_capability_policy_hash
market_state_dependency_request_contract_id
market_state_dependency_request_fingerprint
market_state_dependency_execution_plan_fingerprint_or_ref
market_state_candidate_dataset_fingerprint_or_ref
market_state_dependency_access_mode
direct_market_state_path_allowed
```

Boundary:

```text
direct_market_state_path_allowed = false
market_state_physical_consumption_authorized_by_plan = false
```

A future execution authorization must decide whether and how the Market State dependency request may be executed or reused.

## 10. Logical Context And Binding Plan

The plan must define future Event State logical contexts and exact-one binding obligations.

Required fields:

```text
requested_event_state_contexts_or_manifest_ref
logical_context_grain
event_instance_binding_requirement
event_window_binding_requirement
instrument_projection_requirement
market_state_binding_requirement
state_role_assignment_requirement
consumption_legality_assignment_requirement
exact_one_binding_policy
```

The future builder must block, not emit, any Event State row that lacks exactly one required binding.

## 11. Partition And Coverage Block

The plan must classify all requested logical partitions into mutually exclusive dispositions:

```text
requested_logical_partitions
reusable_validated_partitions
partitions_to_build
partitions_to_rebuild
unavailable_partitions
blocked_partitions
quarantined_partitions
partition_coverage_fingerprint
```

Required invariant:

```text
requested_logical_partitions
    = reusable_validated_partitions
    + partitions_to_build
    + partitions_to_rebuild
    + unavailable_partitions
    + blocked_partitions
    + quarantined_partitions
```

For v0.1, partial execution is not automatically authorized.

## 12. Builders, Validators And Output

The plan must freeze future builder, validator and output obligations before execution.

Builder fields:

```text
event_state_builder_id
event_state_builder_version
builder_contract_id
builder_contract_hash
input_dependency_blocks
output_record_schema_id
state_role_policy_id
consumption_legality_policy_id
```

Validator fields:

```text
validator_id
validator_version
validator_contract_hash
validation_scope
blocking_severity
expected_validation_reports
```

Output fields:

```text
output_mode
output_format
output_schema_id
output_schema_hash
partition_policy_id
candidate_output_root_authority
maximum_files
maximum_rows
maximum_bytes
manifest_requirements
lineage_requirements
hash_requirements
```

Only candidate output mode is in scope for v0.1.

## 13. Quantitative Limits

The plan must freeze:

```text
maximum_event_types
maximum_exchanges
maximum_sessions
maximum_instruments
maximum_event_instances
maximum_event_window_bindings
maximum_instrument_projections
maximum_market_state_dependency_contexts
maximum_event_state_contexts
maximum_output_rows
maximum_output_bytes
maximum_partitions
```

If estimated work exceeds authorized limits, the plan must be blocked before execution.

## 14. Fingerprint Policy

```text
event_state_request_fingerprint
    = meaning of the request

event_state_execution_plan_fingerprint
    = concrete resolution of the request and dependencies
```

The execution-plan fingerprint must include request fingerprint, dependency-resolution fingerprint, Event Type Registry snapshot, Event Instance policy, Event Window policy, Instrument Projection policy, Market State dependency plan, logical context binding plan, partition and coverage plan, builders, validators, output schema and quantitative limits.

It must exclude run start time, machine name, temporary output paths, heartbeat state, log paths, wall-clock runtime values, runtime output path and authorization consumption timestamp.

Rule:

```text
same request
same dependencies
same authorities
same plan contract
    -> same event_state_execution_plan_fingerprint
```

## 15. Plan Status Model

```text
draft
resolved
blocked
authorized_for_execution
consumed
superseded
quarantined
```

Plan status must remain separate from `blocking_findings`.

## 16. Resolution Classes

```text
invalid_request
unresolvable_dependencies
partially_resolvable_dependencies
fully_resolved_dependencies
```

For v0.1:

```text
partial execution = not automatically authorized
```

## 17. Boundary To Future Gates

The next gates must consume this contract:

```text
event_state_materializer_design_v0_1
event_state_validator_design_v0_1
event_state_candidate_dataset_registry_design_v0_1
event_state_on_demand_execution_chain_joint_review_v0_1
```

Future components must not invent structures incompatible with the frozen execution-plan contract.

## 18. Closure

```text
event_state_execution_plan_contract_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_execution_plans_created = 0
event_state_requests_executed = 0
dependency_resolution_records_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_dependency_requests_created = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_records_emitted = 0
event_state_datasets_written = 0
event_state_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = event_state_materializer_design_v0_1
```
