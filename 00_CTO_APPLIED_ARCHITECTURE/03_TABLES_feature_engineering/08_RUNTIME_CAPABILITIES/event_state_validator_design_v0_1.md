# Event State Validator Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_materializer_design_v0_1`

This document defines the future Event State validator.

It is design-only. It does not execute validators, read candidate files, open Market State files, create validation reports, change partition statuses, quarantine artifacts, write dataset registry entries, emit Event State records, write datasets, promote outputs or authorize downstream consumption.

## 1. Validator Principle

```text
Event State Validator
    = the future component that evaluates whether one candidate Event State
      materialization faithfully satisfies its frozen Execution Plan,
      Event State profile, Event Type authority, binding contracts,
      Market State dependency lineage and temporal legality rules.
```

The validator must not:

```text
modify rows
fill nulls
repair data
re-resolve Event State requests
re-resolve Event Type Registry entries
create Event Instances
bind Event Windows
project instruments
resolve or execute Market State dependency requests
choose replacement builders
rebuild outputs
rewrite candidate files
write dataset registry entries
promote datasets
authorize downstream consumption
```

If it finds a problem, it reports, classifies, blocks or recommends quarantine. It never repairs silently.

## 2. Required Future Inputs

A future validator may execute only when a later authorization provides:

```text
frozen_event_state_execution_plan
event_state_execution_plan_fingerprint
materializer_run_manifest
event_state_candidate_output_manifest
event_state_candidate_output_files
event_state_lineage_manifest
event_instance_candidate_manifest_or_binding_report
event_window_binding_report
instrument_projection_report
market_state_dependency_binding_report
logical_context_build_report
blocked_binding_report
builder_execution_report
event_state_profile_contract
expected_event_state_schema
event_type_registry_snapshot
validation_policy
```

The validator consumes these artifacts. It does not rediscover them.

## 3. Validation Blocks

The future validator must support these validation blocks.

### 3.1 Scope Compliance

It must verify that every candidate output is inside the frozen execution plan:

```text
authorized Event State profile
authorized Event Type ids
authorized subject scope
authorized Event Type Registry snapshot
authorized Event Instance policy
authorized Event Window policy
authorized Instrument Projection policy
authorized Market State dependency plan
authorized output roots
quantitative limits
```

No candidate output may include out-of-plan contexts.

### 3.2 Schema Validation

It must verify:

```text
expected columns
column types
nullable policy
required fields
enum values
schema version
contractual column order, if required
```

### 3.3 Grain Validation

It must verify that each candidate row is exactly at the Event State profile grain.

For the initial `session_opened` scope, the validator must preserve the distinction between:

```text
native Event Instance grain = exchange_session
instrument projection grain = instrument_session_context
Event State row grain = profile-defined event-state context
```

It must block:

```text
duplicate canonical event-state keys
missing key fields
multiple rows for one canonical event-state context
instrument_id inserted into native Event Instance identity
```

### 3.4 Event Type And Registry Validation

It must verify:

```text
event_type_id is accepted or accepted_with_restrictions
event_type_id is inside v0.1 scope
registry snapshot id matches the plan
registry snapshot hash matches the plan
halt_resumed is not present
event detection was not executed for session_opened
```

### 3.5 Event Instance, Window And Projection Binding Validation

For every emitted Event State row, the validator must verify exactly-one binding for:

```text
Event Instance
Event Window
Instrument Projection
Market State dependency reference
State Role
Consumption Legality
```

Missing, duplicated or ambiguous bindings are blocking.

### 3.6 State Role And Consumption Legality Validation

The validator must preserve:

```text
state_role != consumption_legality
```

It must block if a row becomes decision-safe only because it is `pre_event` or `at_event` without a contractual legality rule.

### 3.7 Temporal Legality

It must verify:

```text
event_anchor_timestamp policy respected
first_observable_timestamp policy respected
regular_session_open_timestamp != first_observed_trade_timestamp
Market State decision timestamps are lawful for the Event Window
source timestamps do not violate as-of policy
future-information exclusion is preserved
calendar/session alignment is preserved
```

The validator must distinguish:

```text
timestamp present
```

from:

```text
timestamp legally valid
```

Temporal legality failures are blocking for reuse and promotion review.

### 3.8 Market State Dependency Lineage

Each candidate Event State row must demonstrate:

```text
market_state_runtime_capability_id
market_state_dependency_request_fingerprint
market_state_dependency_execution_plan_fingerprint_or_ref
market_state_candidate_dataset_fingerprint_or_ref
market_state_record_id_or_candidate_ref
market_state_dependency_access_mode
market_state_dependency_binding_status
```

The validator must block direct Market State path consumption or any Market State dependency not named in the execution plan.

### 3.9 Lineage Completeness

Each candidate output must demonstrate:

```text
event_state_request_fingerprint
event_state_dependency_resolution_fingerprint
event_state_execution_plan_fingerprint
event_state_profile_contract_hash
event_type_registry_snapshot_id
event_instance_policy_contract_hash
event_window_policy_contract_hash
instrument_projection_policy_contract_hash
builder_id
builder_version
output_schema_hash
```

Incomplete lineage blocks reuse eligibility.

### 3.10 Context And Partition Completeness

For each logical context:

```text
requested_contexts
    =
emitted_contexts
+ blocked_contexts
+ quarantined_contexts
+ unavailable_contexts
```

For the run:

```text
planned_partitions
    =
written_partitions
+ blocked_partitions
+ quarantined_partitions
+ not_executed_partitions
```

Contexts cannot disappear without a recorded disposition.

### 3.11 Fingerprint And Manifest Validation

It must verify:

```text
candidate file hashes
partition hashes
event_state_candidate_dataset_fingerprint
row-level event_state_output_fingerprints
manifest hashes
validation input artifact hashes
```

The future validator must detect post-materialization mutation.

### 3.12 Determinism Readiness

The validator must emit enough evidence for a later rerun comparison:

```text
canonical event-state ids
row-level fingerprints
partition fingerprints
dataset fingerprint
manifest fingerprint
normalized findings
```

This gate does not run determinism tests.

## 4. Severity Model

Findings must use a closed severity set:

```text
INFO
WARNING
RESTRICTION
BLOCKING
CRITICAL
```

The final validation status must use a closed status set:

```text
PASS
PASS_WITH_RESTRICTIONS
BLOCKED
QUARANTINED
FAIL
```

Free text may explain a finding, but it must not define the machine-readable state.

## 5. Candidate Eligibility Recommendations

The validator may emit recommendations:

```text
eligible_for_candidate_registry
eligible_for_reuse
eligible_for_promotion_review
reuse_eligibility_reason
promotion_review_eligibility_reason
```

These are recommendations only. The Dataset Registry and later promotion gates remain separate authorities.

Example:

```text
validation_status = PASS_WITH_RESTRICTIONS
eligible_for_candidate_registry = true
eligible_for_reuse = false
eligible_for_promotion_review = false
reuse_eligibility_reason = pending_determinism_validation
```

## 6. Reuse Eligibility

Reuse requires more than a passing validation status.

Future reuse eligibility requires:

```text
complete lineage
stable Event State profile version
stable Event Type Registry snapshot
stable Event Instance policy
stable Event Window policy
stable Instrument Projection policy
stable Market State dependency fingerprint
stable builder version
no quarantined partitions
no unresolved blocking findings
determinism proven
```

For v0.1 design, the validator may emit:

```text
reuse_eligibility = pending_determinism_validation
```

## 7. Quarantine Policy

A partition or output artifact should be recommended for quarantine when it exists physically but cannot be considered safe or reusable.

Examples:

```text
hash_mismatch
corrupt_candidate_file
lineage_inconsistency
temporal_leakage_detected
duplicate_canonical_event_state_identity
schema_contract_violation
exact_one_binding_failure
market_state_dependency_fingerprint_mismatch
```

The validator does not delete quarantined artifacts. It preserves them as evidence and emits a quarantine recommendation for a later authority.

## 8. Required Future Reports

Future validator execution must be able to emit:

```text
event_state_validation_report.json
event_state_binding_validation_report.json
event_state_partition_validation_report.json
event_state_lineage_validation_report.json
event_state_temporal_legality_report.json
event_state_market_state_dependency_validation_report.json
validation_evidence_manifest.json
event_state_validation_readout.md
```

These reports are not created by this design gate.

## 9. Validation Fingerprint

The future validator must produce:

```text
event_state_validation_result_fingerprint
```

Conceptually:

```text
hash(
    event_state_execution_plan_fingerprint
    + event_state_candidate_dataset_fingerprint
    + market_state_dependency_fingerprints
    + validator versions
    + validation policy version
    + normalized findings
)
```

This allows TSIS to know when a validation result is obsolete because the dataset, validator, policy, profile, plan, registry snapshot or Market State dependency changed.

## 10. Blocking Rules

The future validator must block or fail validation when:

```text
execution_plan_missing
execution_plan_fingerprint_missing
materializer_run_manifest_missing
candidate_output_manifest_missing
lineage_manifest_missing
event_state_profile_contract_missing
expected_schema_missing
validation_policy_missing
out_of_scope_output_detected
schema_contract_violation
duplicate_canonical_event_state_identity
missing_required_event_state_identity
event_state_output_fingerprint_missing
event_state_output_fingerprint_mismatch
event_type_registry_hash_mismatch
unsupported_event_type_present
native_event_instance_identity_violation
exact_one_binding_failure
state_role_consumption_legality_conflation
temporal_leakage_detected
market_state_dependency_lineage_incomplete
market_state_dependency_fingerprint_mismatch
direct_market_state_path_consumption_detected
partition_reconciliation_failure
critical_content_rule_failure
file_hash_mismatch
manifest_hash_mismatch
```

## 11. Non-Responsibilities

The validator must not evaluate:

```text
profitability
edge
strategy performance
outcomes
ML usefulness
backtest quality
execution realism
broker state
locates
fills
slippage
```

It validates that Event State represents what its contracts declare.

## 12. Closed Boundaries

This design gate records:

```text
event_state_validator_executions = 0
event_state_candidate_files_read = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
event_state_validation_reports_created = 0
event_state_partition_status_changes = 0
event_state_quarantine_actions = 0
event_state_registry_entries_written = 0
event_state_records_emitted = 0
event_state_datasets_written = 0
production = false
downstream_consumption = false
```

## 13. Next Gate

```text
next_allowed_gate =
event_state_candidate_dataset_registry_design_v0_1
```

That gate may define how validation outcomes are recorded. It must not be treated as already open by this document.
