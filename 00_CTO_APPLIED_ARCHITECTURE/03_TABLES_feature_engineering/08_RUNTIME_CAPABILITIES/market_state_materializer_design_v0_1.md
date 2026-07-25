# Market State Materializer Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_partition_and_coverage_resolver_design_v0_1`

This document defines the future Market State materializer.

It is design-only. It does not execute builders, read source rows, open source
parquet, create staging directories, write candidate data, compute hashes,
create manifests, validate outputs or write dataset registry entries.

## 1. Materializer Principle

```text
Market State Materializer
    = the future component that consumes one authorized frozen execution plan
      and writes candidate Market State output artifacts.
```

The materializer must not:

```text
resolve profiles
resolve universe membership
resolve source aliases
resolve partition coverage
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
execution_plan_id
execution_plan_fingerprint
execution_plan_status = authorized_for_execution
request_fingerprint
resolved_profile block
resolved_universe_and_scope block
resolved_sources block
partition_and_coverage block
resolved_builders block
output_plan block
quantitative_limits block
```

If any required plan block is missing, materialization must block before source
rows are read.

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

Partial execution remains prohibited unless a later execution authorization
explicitly permits a subset of logical partitions.

## 4. Build Responsibility

The future materializer orchestrates builder execution exactly as frozen in the
execution plan:

```text
builder_id
builder_version
builder_contract_hash
input_source_aliases
output_variable_ids
temporal_cutoff_policy_id
temporal_cutoff_policy_hash
```

It must not substitute builder versions or infer missing builder definitions.

## 5. Output Staging And Atomic Commit

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
complete all planned candidate outputs
compute output hashes
write manifests
run validators in later validator gate
commit only after validation policy allows
```

This design does not authorize staging directory creation or output writes.

## 6. Candidate Output Status

The materializer may only create future outputs with:

```text
output_status = candidate_unvalidated
```

A validator gate may later move the output to:

```text
validated_candidate
```

The materializer must not create:

```text
official_dataset
production_dataset
downstream_consumable_dataset
```

## 7. Required Future Artifacts

Future materializer execution must be able to emit:

```text
candidate_data_files
candidate_output_manifest.json
lineage_manifest.json
partition_build_report.json
builder_execution_report.json
blocked_partition_report.json
materializer_run_readout.md
```

These artifacts are not created by this design gate.

## 8. Manifest Requirements

The future output manifest must preserve:

```text
request_fingerprint
execution_plan_fingerprint
resolved_profile_fingerprint
resolved_universe_fingerprint
resolved_source_set_fingerprint
partition_coverage_resolution_fingerprint
builder_contract_hashes
output_schema_hash
candidate_file_hashes
logical_partition_counts
materialized_partition_counts
blocked_or_skipped_partition_counts
```

## 9. Lineage Requirements

For each candidate output partition, lineage must preserve:

```text
logical_partition_id
partition_disposition_consumed
source_aliases_used
source_dataset_versions
source_content_fingerprints
builder_id
builder_version
temporal_cutoff_policy_id
profile_contract_hash
calendar_authority_id
point_in_time_policy_id
```

## 10. Blocking Rules

The future materializer must block before reading source rows if:

```text
execution_plan_status_not_authorized
execution_plan_fingerprint_missing
execution_plan_contains_unresolved_blocks
resolved_builders_missing
output_schema_missing
output_plan_missing
quantitative_limits_missing
partition_disposition_not_materializable
partial_execution_not_authorized
source_authority_missing_from_plan
builder_contract_missing
temporal_cutoff_policy_missing
candidate_output_root_authority_missing
atomic_commit_policy_missing
```

## 11. Boundary To Validator

The next gate must design:

```text
market_state_validator_design_v0_1
```

The validator may inspect candidate outputs and decide validation status in a
future execution gate. The materializer must not self-certify its outputs.

## 12. Closure

```text
market_state_materializer_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

materializer_executions = 0
builder_executions = 0
source_rows_read = 0
source_parquet_files_read = 0
staging_directories_created = 0
candidate_data_files_written = 0
candidate_parquet_files_written = 0
output_manifests_created = 0
lineage_manifests_created = 0
content_hashes_computed = 0
validation_reports_created = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_validator_design_v0_1
```
