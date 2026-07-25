# Market State Validator Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_materializer_design_v0_1`

This document defines the future Market State validator.

It is design-only. It does not execute validators, read candidate files, open
parquet, create validation reports, change partition statuses, quarantine
artifacts, write dataset registry entries, emit Market State records, write
datasets, promote outputs or authorize downstream consumption.

## 1. Validator Principle

```text
Market State Validator
    = the future component that evaluates whether one candidate
      materialization faithfully satisfies its frozen Execution Plan,
      profile contract, schema, lineage and temporal legality rules.
```

The validator must not:

```text
modify rows
fill nulls
repair data
re-resolve profiles
re-resolve universe membership
re-resolve source aliases
reclassify partition coverage
choose replacement builders
rebuild partitions
rewrite parquet
write dataset registry entries
promote datasets
authorize downstream consumption
```

If it finds a problem, it reports, classifies, blocks or recommends quarantine.
It never repairs silently.

## 2. Required Future Inputs

A future validator may execute only when a later authorization provides:

```text
frozen_execution_plan
execution_plan_fingerprint
materializer_run_manifest
candidate_output_manifest
candidate_output_files
lineage_manifest
partition_manifest
builder_execution_report
source_fingerprints
profile_contract
expected_schema
grain_policy
identity_policy
temporal_legality_policy
validation_policy
```

The validator consumes these artifacts. It does not rediscover them.

## 3. Validation Blocks

The future validator must support these validation blocks.

### 3.1 Scope Compliance

It must verify that every candidate output is inside the frozen execution plan:

```text
authorized profile
authorized source set
authorized builders
requested instruments
requested sessions
requested logical partitions
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

It must verify that each candidate row is exactly at the profile grain.

For an intraday Market State profile, the canonical key is expected to include
the profile-defined state identity fields, such as:

```text
profile_id
instrument_id
decision_timestamp_utc
```

The validator must block:

```text
duplicate canonical keys
missing key fields
multiple rows for one canonical state
```

### 3.4 Identity Validation

It must verify:

```text
materialized_state_candidate_id
state_output_fingerprint
partition_fingerprint
dataset_fingerprint
```

These identifiers and fingerprints must be present, deterministic, unique where
required and consistent with the represented content.

### 3.5 Temporal Legality

It must verify that output variables comply with temporal policy:

```text
source_timestamp <= decision_timestamp
builder cutoff respected
as_of policy respected
calendar legality respected
session boundaries respected
future-information exclusion preserved
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

### 3.6 Source Lineage

Each candidate output must demonstrate:

```text
source_alias
source_dataset_id
source_dataset_version
source_contract_id
source_schema_id
source_physical_authority
source_content_fingerprint
builder_id
builder_version
temporal_cutoff_policy_id
```

Incomplete lineage blocks reuse eligibility.

### 3.7 Partition Completeness

For each logical partition:

```text
requested_contexts
    =
emitted_contexts
+ blocked_contexts
+ quarantined_contexts
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

### 3.8 Content Validation

The validator must support profile-specific content checks, including:

```text
required variables present
allowed null rates
range constraints
cross-field consistency
monotonic timestamps
session alignment
exchange consistency
```

Not all content anomalies are hard failures. Severity must be explicit.

### 3.9 Fingerprint Validation

It must verify:

```text
file hashes
partition hashes
dataset fingerprint
state_output_fingerprints
manifest hashes
```

The future validator must detect post-materialization mutation.

### 3.10 Determinism Readiness

The validator must emit enough evidence for a later rerun comparison:

```text
record ids
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

Free text may explain a finding, but it must not define the machine-readable
state.

## 5. Candidate Eligibility Recommendations

The validator may emit recommendations:

```text
eligible_for_candidate_registry
eligible_for_reuse
eligible_for_promotion_review
reuse_eligibility_reason
promotion_review_eligibility_reason
```

These are recommendations only. The Dataset Registry and later promotion gates
remain separate authorities.

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
stable profile version
stable builder version
matching source fingerprints
no quarantined partitions
no unresolved blocking findings
determinism proven
```

For v0.1 design, the validator may emit:

```text
reuse_eligibility = pending_determinism_validation
```

## 7. Quarantine Policy

A partition or output artifact should be recommended for quarantine when it
exists physically but cannot be considered safe or reusable.

Examples:

```text
hash_mismatch
corrupt_candidate_file
lineage_inconsistency
temporal_leakage_detected
duplicate_canonical_identities
schema_contract_violation
```

The validator does not delete quarantined artifacts. It preserves them as
evidence and emits a quarantine recommendation for a later authority.

## 8. Required Future Reports

Future validator execution must be able to emit:

```text
market_state_validation_report.json
market_state_partition_validation_report.json
market_state_lineage_validation_report.json
market_state_temporal_legality_report.json
validation_evidence_manifest.json
market_state_validation_readout.md
```

These reports are not created by this design gate.

## 9. Validation Fingerprint

The future validator must produce:

```text
validation_result_fingerprint
```

Conceptually:

```text
hash(
    execution_plan_fingerprint
    + candidate_dataset_fingerprint
    + validator versions
    + validation policy version
    + normalized findings
)
```

This allows TSIS to know when a validation result is obsolete because the
dataset, validator, policy, profile or plan changed.

## 10. Blocking Rules

The future validator must block or fail validation when:

```text
execution_plan_missing
execution_plan_fingerprint_missing
materializer_run_manifest_missing
candidate_output_manifest_missing
lineage_manifest_missing
profile_contract_missing
expected_schema_missing
validation_policy_missing
out_of_scope_output_detected
schema_contract_violation
duplicate_canonical_identity
missing_required_identity
state_output_fingerprint_missing
state_output_fingerprint_mismatch
temporal_leakage_detected
source_lineage_incomplete
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
```

It validates that Market State represents what its contracts declare.

## 12. Closed Boundaries

This design gate records:

```text
validator_executions = 0
candidate_files_read = 0
parquet_files_read = 0
validation_reports_created = 0
partition_status_changes = 0
quarantine_actions = 0
dataset_registry_entries_written = 0
market_state_records_emitted = 0
datasets_written = 0
production = false
downstream_consumption = false
```

## 13. Next Gate

```text
next_allowed_gate =
market_state_candidate_dataset_registry_design_v0_1
```

That gate may define how validation outcomes are recorded. It must not be
treated as already open by this document.
