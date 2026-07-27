# Event State Candidate Dataset Registry Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Parent Gate: `event_state_validator_design_v0_1`

This document defines the future Event State candidate dataset registry.

It is design-only. It does not write registry entries, read registry runtime state, register datasets, supersede datasets, quarantine artifacts, read candidate files, read Market State files, validate outputs, materialize Event State, promote datasets, authorize production or authorize downstream consumption.

## 1. Registry Principle

```text
Event State Candidate Dataset Registry
    = the future component that records governed identity, evidence,
      validation state, coverage, exact-one binding evidence, Market State
      dependency references, hashes, lineage references and eligibility of one
      candidate Event State materialization.
```

The registry records decisions and evidence produced by other components. It must not build Event State, validate candidate files, repair rows, resolve requests or dependencies, create Event Instances, create Event Window Bindings, create Instrument Projections, read Market State candidate files, promote datasets or enable downstream consumption.

## 2. Runtime Position

```text
Materializer
    = creates candidate Event State output

Validator
    = evaluates candidate Event State output

Candidate Dataset Registry
    = records identity, evidence, status, coverage, lineage and eligibility
```

The registry must not collapse these responsibilities.

## 3. Dataset Identity

The registry must separate:

```text
dataset_id
```

from:

```text
event_state_candidate_dataset_fingerprint
```

`dataset_id` is the stable registry identity. It must be non-path-based and not derived from a temporary run folder.

Conceptually:

```text
event_state_candidate_dataset:<profile_id>:<event_scope>:<coverage_id>:<registry_entry_version>
```

`event_state_candidate_dataset_fingerprint` identifies governed content and construction context. It must include request, dependency-resolution, execution-plan, Event Type Registry, policy, Market State dependency, builder, schema, context-ledger and file-hash evidence.

Rule:

```text
same governed Event State content
    =
same event_state_candidate_dataset_fingerprint
```

## 4. Required Registry Entry Fields

A future entry must include identity, request, dependency and plan fields:

```text
dataset_id
dataset_kind
registry_entry_version
registry_status
created_at_utc
event_state_request_id
event_state_request_fingerprint
event_state_dependency_resolution_id
event_state_dependency_resolution_fingerprint
event_state_execution_plan_id
event_state_execution_plan_fingerprint
```

It must include semantic authority fields:

```text
event_state_profile_id
event_state_profile_version
event_state_profile_contract_hash
event_type_registry_snapshot_id
event_type_registry_snapshot_sha256
accepted_event_type_ids
accepted_subject_scope
```

It must include dependency, content and validation fields:

```text
market_state_dependency_request_fingerprint
market_state_candidate_dataset_fingerprint_or_ref
event_state_candidate_dataset_fingerprint
event_state_validation_result_fingerprint
registry_entry_fingerprint
```

It must include coverage and context fields:

```text
coverage_start
coverage_end
exchange_scope
event_type_count
event_instance_count
instrument_count
session_count
logical_context_count
requested_context_count
represented_context_count
materialized_context_count
reusable_context_count
blocked_context_count
unavailable_context_count
quarantined_context_count
not_built_context_count
```

It must include evidence refs:

```text
logical_context_ledger_ref
binding_manifest_ref
file_manifest_ref
lineage_manifest_ref
validation_report_ref
validation_evidence_manifest_ref
market_state_dependency_binding_report_ref
restriction_set_ref
```

It must keep governance states separate:

```text
validation_status
reuse_eligibility
promotion_review_eligibility
downstream_eligibility
supersedes_dataset_id
superseded_by_dataset_id
quarantine_reference
```

## 5. State Separation

Closed registry status model:

```text
planned
candidate_unvalidated
validated_candidate
quarantined
blocked
failed
superseded
deprecated
```

Closed validation status model:

```text
not_validated
pass
pass_with_restrictions
blocked
quarantined
fail
```

Closed reuse eligibility model:

```text
not_evaluated
eligible
ineligible
pending_determinism
pending_policy_review
```

Closed promotion-review eligibility model:

```text
not_eligible
eligible_with_restrictions
eligible
```

For v0.1:

```text
downstream_eligibility = false
```

## 6. Coverage And Binding Reconciliation

Coverage must be ledger-based, not date-range-only.

```text
requested_logical_contexts
    =
represented_contexts
+ blocked_contexts
+ unavailable_contexts
+ quarantined_contexts
+ not_built_contexts
```

Every represented row must preserve exact-one evidence for:

```text
Event Instance binding
Event Window binding
Instrument Projection binding
Market State dependency binding
state_role assignment
consumption_legality assignment
```

A registry entry must not imply validity if any binding was missing, ambiguous or substituted by fallback.

## 7. Market State Dependency Boundary

Event State registry entries may reference Market State only through runtime capability evidence:

```text
market_state_dependency_request_fingerprint
market_state_candidate_dataset_fingerprint_or_ref
market_state_dependency_binding_report_ref
```

Direct Market State parquet path authority is prohibited.

## 8. Reuse Eligibility

Future reuse requires matching Event State request, dependency resolution, execution plan, profile, Event Type Registry snapshot, Event Instance policy, Event Window policy, Instrument Projection policy, Market State dependency fingerprint or ref, builders and schema. It also requires an allowed validation status, proven determinism, no quarantine and no unresolved blocking findings.

Therefore:

```text
registry_status = validated_candidate
```

does not automatically imply:

```text
reuse_eligibility = eligible
```

## 9. Supersession And Quarantine

The registry must support supersession without deleting prior entries. Quarantine preserves original hashes, findings, binding evidence, lineage, reason and authority. Quarantine does not authorize repair.

## 10. Registry Entry Fingerprint

Each entry should include:

```text
registry_entry_fingerprint
```

Conceptually this hashes dataset identity, candidate dataset fingerprint, validation fingerprint, Event State profile hash, Event Type Registry snapshot hash, Market State dependency fingerprint or ref, logical context ledger hash, binding manifest hash, lineage manifest hash, registry status and restriction set hash.

## 11. Closed Gate Counters

```text
registry_entries_written = 0
registry_runtime_reads = 0
datasets_registered = 0
datasets_promoted = 0
datasets_superseded = 0
quarantine_transitions = 0
event_state_records_emitted = 0
event_state_datasets_written = 0
event_state_candidate_files_read = 0
market_state_candidate_files_read = 0
source_market_data_rows_read = 0
validation_executions = 0
official_event_state_dataset = false
production = false
downstream = false
```

## 12. Next Gate

```text
event_state_on_demand_execution_chain_joint_review_v0_1
```

That gate may review whether the Event State on-demand chain is coherent enough to open a bounded execution authorization. It must not execute Event State by itself.