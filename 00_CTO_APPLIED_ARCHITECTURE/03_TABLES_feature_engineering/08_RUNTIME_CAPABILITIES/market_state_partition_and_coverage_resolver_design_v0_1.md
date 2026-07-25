# Market State Partition And Coverage Resolver Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_source_resolver_design_v0_1`

This document defines the future Market State partition and coverage resolver.

It is design-only. It does not execute a resolver, read source rows, open
parquet files, create manifests, create execution plans, build Market State,
write parquet or write registry entries.

## 1. Resolver Principle

```text
Market State Partition and Coverage Resolver
    = the future component that classifies every requested logical partition
      into one and only one execution disposition.
```

It consumes:

```text
validated request intent
resolved_profile block
resolved_universe_and_scope block
resolved_sources block
reuse_policy
validation_level
output_mode
```

It produces partition and coverage classification only. It must not resolve
profiles, universes, source aliases, builders, validators or output paths.

## 2. Logical Partition vs Physical Storage Partition

The resolver must separate:

```text
logical coverage partition
    = unit TSIS classifies as reusable, buildable, unavailable,
      blocked or quarantined

physical storage partition
    = later materializer output grouping
```

For the first Market State intraday profile, the default logical coverage
partition is:

```text
profile_id
+ profile_version
+ instrument_id
+ exchange_id
+ session_date
```

The materializer may later group logical partitions into physical storage
partitions, but this resolver must classify logical partitions.

## 3. Inputs

Required future inputs:

```text
request_id
request_fingerprint
resolved_profile_id
resolved_profile_version
resolved_profile_fingerprint
resolved_universe_fingerprint
resolved_source_set_fingerprint
resolved_instrument_session_contexts
resolved_source_authorities
reuse_policy
validation_level
output_mode
coverage_policy_id
```

The resolver must not alter resolved profile identity, universe membership or
source versions.

## 4. Source Availability vs Output Disposition

The resolver must distinguish:

```text
source availability evidence
    = whether required source aliases have declared coverage for a logical
      partition

output partition disposition
    = operational classification of the requested Market State partition
```

`available_source_partitions` is not a final output disposition.

Source availability can support a `to_build` classification, but it does not
mean a Market State partition is reusable.

## 5. Output Partition Dispositions

Every requested logical partition must receive exactly one disposition:

```text
reusable_validated
to_build
to_rebuild
unavailable
quarantined
blocked
```

Required invariant:

```text
requested_logical_partitions
    =
    reusable_validated
    + to_build
    + to_rebuild
    + unavailable
    + quarantined
    + blocked
```

The categories are mutually exclusive.

## 6. Disposition Semantics

### reusable_validated

An existing output partition is reusable only if it matches:

```text
profile contract hash
request semantics
source set fingerprint
builder fingerprint
universe membership identity
calendar authority
point-in-time policy
schema hash
validation status
partition content hash
lineage completeness
```

### to_build

No reusable output exists, but:

```text
all required sources exist
source coverage is sufficient
contracts are compatible
execution is legally possible
```

### to_rebuild

An output exists but cannot be reused because of:

```text
source version change
builder version change
validation expiry
profile change
fingerprint mismatch
lineage incompleteness
```

### unavailable

The partition cannot be built because physical coverage is insufficient:

```text
missing_source_partition
outside_source_coverage
instrument_absent_from_required_source
```

### blocked

The partition cannot be legally classified for execution:

```text
ambiguous_resolution
unauthorized_source
identity_failure
contract_incompatibility
schema_mismatch
```

### quarantined

A source or existing output is present but excluded by:

```text
validation failure
corruption
hash mismatch
quality incident
lineage violation
```

Quarantined partitions must not be reused or rebuilt automatically without
explicit policy.

## 7. Coverage Dimensions

Coverage must be evaluated across:

```text
source_alias
instrument_id
exchange_id
session_date
timestamp range
required resolution
schema version
calendar authority
```

For a Market State partition:

```text
coverage(partition)
    =
    intersection(
        coverage of every required source alias
    )
```

If any required source alias lacks sufficient coverage, the partition is not
`to_build`.

## 8. Partial Session Coverage

The resolver must consume profile policy for required session coverage:

```text
full_session_required
regular_session_only
partial_coverage_allowed_with_restriction
```

It must not infer an acceptable coverage window from available source rows.

## 9. Output Block

The resolver must populate the Execution Plan `partition_and_coverage` block:

```text
requested_partitions
reusable_validated_partitions
partitions_to_build
partitions_to_rebuild
blocked_partitions
missing_partitions
quarantined_partitions
```

It must also produce:

```text
partition_policy_id
logical_partition_grain
requested_partition_count
reusable_validated_partition_count
to_build_partition_count
to_rebuild_partition_count
unavailable_partition_count
blocked_partition_count
quarantined_partition_count
coverage_status
partition_coverage_resolution_fingerprint
requested_partition_manifest_ref
reusable_partition_manifest_ref
build_partition_manifest_ref
rebuild_partition_manifest_ref
unavailable_partition_manifest_ref
blocked_partition_manifest_ref
quarantined_partition_manifest_ref
source_availability_manifest_ref
```

The manifest references are future runtime outputs. This design gate creates no
manifests.

## 10. Coverage Status

Global coverage statuses:

```text
FULLY_REUSABLE
FULLY_BUILDABLE
PARTIALLY_BUILDABLE
BLOCKED
```

For v0.1:

```text
partial execution = prohibited unless separately authorized
```

## 11. Fingerprint Contribution

The resolver contributes to `execution_plan_fingerprint` through:

```text
request_fingerprint
resolved_profile_fingerprint
resolved_universe_fingerprint
resolved_source_set_fingerprint
coverage_policy_id
logical_partition_grain
sorted partition dispositions
source availability evidence hashes
partition_coverage_resolution_fingerprint
```

It must not include:

```text
resolver_run_time
machine name
temporary manifest path
log path
```

## 12. Blocking Rules

The resolver must block if:

```text
logical_partition_grain_missing
resolved_universe_fingerprint_missing
resolved_source_set_fingerprint_missing
required_source_alias_coverage_missing
source_availability_ambiguous
existing_output_reuse_identity_ambiguous
existing_output_validation_status_missing
existing_output_lineage_incomplete
partition_disposition_invariant_failure
coverage_policy_missing
partial_session_coverage_policy_missing
quarantined_source_required
unauthorized_source_required
schema_contract_incompatible
partial_execution_requested_without_authorization
```

Blocked partition/coverage resolution must stop before materializer design
claims readiness for execution.

## 13. Boundary To Materializer

The next gate must design:

```text
market_state_materializer_design_v0_1
```

The materializer may consume partition dispositions but must not reclassify
coverage, change source versions or alter logical partition identity.

## 14. Closure

```text
market_state_partition_and_coverage_resolver_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

partition_coverage_resolver_executions = 0
partition_manifests_created = 0
coverage_manifests_created = 0
existing_dataset_registry_runtime_reads = 0
source_manifest_runtime_reads = 0
source_parquet_files_read = 0
source_rows_read = 0
partition_status_transitions = 0
execution_plan_instances_created = 0
execution_plans_created = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_materializer_design_v0_1
```
