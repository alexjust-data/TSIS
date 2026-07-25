# Market State Candidate Dataset Registry Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_validator_design_v0_1`

This document defines the future Market State candidate dataset registry.

It is design-only. It does not write registry entries, read registry runtime
state, register datasets, supersede datasets, quarantine artifacts, read source
market data, validate parquet, materialize data, promote datasets, authorize
production or authorize downstream consumption.

## 1. Registry Principle

```text
Market State Candidate Dataset Registry
    = the future component that records the governed identity, evidence,
      validation state, coverage, hashes, lineage references and eligibility
      of one candidate Market State materialization.
```

The registry must not:

```text
build data
validate parquet
repair candidate files
resolve requests
resolve sources
materialize outputs
promote datasets
enable downstream consumption
```

It records decisions and evidence produced by other components.

## 2. Registry Position In The Runtime Chain

```text
Materializer
    = creates candidate output

Validator
    = evaluates candidate output

Candidate Dataset Registry
    = records identity, evidence, status, coverage and eligibility
```

The registry must not collapse these responsibilities.

## 3. Dataset Identity

The registry must separate:

```text
dataset_id
```

from:

```text
candidate_dataset_fingerprint
```

### 3.1 `dataset_id`

`dataset_id` is the stable registry identity.

Conceptually:

```text
market_state_candidate_dataset:<profile_id>:<coverage_id>:<registry_entry_version>
```

The exact format may be constrained by a later implementation gate, but the
identity must be stable, non-path-based and not derived from a temporary run
folder.

### 3.2 `candidate_dataset_fingerprint`

`candidate_dataset_fingerprint` identifies governed content and construction
context.

It must depend on:

```text
request_fingerprint
execution_plan_fingerprint
profile_version
source_fingerprints
builder_versions
logical_partition_manifest_hash
candidate_file_hashes
schema_hash
```

Rule:

```text
same governed content
    =
same candidate_dataset_fingerprint
```

## 4. Required Registry Entry Fields

A future registry entry must include:

```text
dataset_id
dataset_kind
registry_entry_version
registry_status
created_at_utc
```

```text
request_id
request_fingerprint
execution_plan_id
execution_plan_fingerprint
```

```text
profile_id
profile_version
profile_contract_hash
```

```text
candidate_dataset_fingerprint
validation_result_fingerprint
registry_entry_fingerprint
```

```text
coverage_start
coverage_end
exchange_scope
instrument_count
session_count
logical_partition_count
```

```text
requested_partition_count
materialized_partition_count
reusable_partition_count
blocked_partition_count
quarantined_partition_count
not_built_partition_count
```

```text
file_manifest_ref
partition_manifest_ref
lineage_manifest_ref
validation_report_ref
validation_evidence_manifest_ref
```

```text
validation_status
reuse_eligibility
promotion_review_eligibility
downstream_eligibility
```

```text
supersedes_dataset_id
superseded_by_dataset_id
quarantine_reference
```

## 5. State Separation

The registry must keep separate:

```text
registry_status
validation_status
reuse_eligibility
promotion_review_eligibility
downstream_eligibility
```

### 5.1 Registry Status

Closed set:

```text
planned
candidate
validated_candidate
quarantined
blocked
failed
superseded
deprecated
```

### 5.2 Validation Status

Closed set:

```text
not_validated
pass
pass_with_restrictions
blocked
quarantined
fail
```

### 5.3 Reuse Eligibility

Closed set:

```text
not_evaluated
eligible
ineligible
pending_determinism
pending_policy_review
```

### 5.4 Promotion Review Eligibility

Closed set:

```text
not_eligible
eligible_with_restrictions
eligible
```

### 5.5 Downstream Eligibility

For v0.1:

```text
downstream_eligibility = false
```

This design does not authorize downstream consumption under any status.

## 6. Coverage Recording

The registry must record both:

```text
requested_coverage
```

and:

```text
effective_materialized_coverage
```

Coverage must not be represented only by:

```text
start_date
end_date
```

It must reference a logical partition manifest.

Required reconciliation:

```text
requested_logical_partitions
    =
materialized_partitions
+ blocked_partitions
+ quarantined_partitions
+ not_built_partitions
```

## 7. Reuse Eligibility Policy

The registry must not declare a dataset reusable merely because it exists.

Future reuse eligibility requires:

```text
matching request_fingerprint
matching execution_plan_fingerprint
matching profile_version
matching source_fingerprints
matching builder_versions
matching schema_hash
validation_status in pass or pass_with_restrictions, subject to policy
determinism_proven
no quarantine
no unresolved blocking findings
```

Therefore:

```text
registry_status = validated_candidate
```

does not automatically imply:

```text
reuse_eligibility = eligible
```

## 8. Supersession

The registry must support supersession without deleting prior entries.

Example:

```text
candidate_dataset_v1
    ↓
new build with corrected sources
    ↓
candidate_dataset_v2
```

Required fields:

```text
supersedes_dataset_id
supersession_reason
supersession_authority
superseded_at_utc
```

No prior registry entry may be rewritten silently.

## 9. Quarantine Reference

A candidate dataset may remain registered even when quarantined.

The registry must preserve:

```text
original_file_refs
validation_findings
hashes
quarantine_reason
quarantine_authority
quarantine_reference
```

Quarantine does not mean deletion. It means the artifact is retained as evidence
but is not safe for reuse, promotion or consumption.

## 10. Registry Entry Fingerprint

The registry must produce:

```text
registry_entry_fingerprint
```

Conceptually:

```text
hash(
    dataset_id
    + candidate_dataset_fingerprint
    + validation_result_fingerprint
    + coverage_manifest_hash
    + lineage_manifest_hash
    + registry_status
)
```

This fingerprint identifies the registry statement, not the dataset content
alone.

## 11. Required Future Registry Artifacts

Future registry execution must be able to emit:

```text
market_state_candidate_dataset_registry_entry.json
market_state_candidate_dataset_registry_entry_fingerprint.txt
market_state_candidate_dataset_registry_readout.md
```

These artifacts are not created by this design gate.

## 12. Blocking Rules

A future registry write must block when:

```text
dataset_id_missing
candidate_dataset_fingerprint_missing
request_fingerprint_missing
execution_plan_fingerprint_missing
profile_contract_hash_missing
validation_result_fingerprint_missing
logical_partition_manifest_missing
file_manifest_ref_missing
lineage_manifest_ref_missing
validation_report_ref_missing
coverage_reconciliation_failure
registry_status_invalid
validation_status_invalid
reuse_eligibility_invalid
promotion_review_eligibility_invalid
downstream_eligibility_not_false_in_v0_1
supersession_cycle_detected
quarantine_reference_missing_for_quarantined_status
```

## 13. Closed Boundaries

This design gate records:

```text
registry_entries_written = 0
registry_runtime_reads = 0
datasets_registered = 0
datasets_promoted = 0
datasets_superseded = 0
quarantine_transitions = 0
official_dataset = false
production = false
downstream = false
```

## 14. Next Gate

```text
next_allowed_gate =
market_state_run_lifecycle_and_manifest_design_v0_1
```

That gate may define how runs are born, monitored, finalized, consumed and
manifested. It must not be treated as already open by this document.
