# Market State Source Resolver Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_universe_resolver_design_v0_1`

This document defines the future Market State source resolver.

It is design-only. It does not execute a resolver, read source registries at
runtime, inspect parquet, read market data, create source sets, create execution
plans, build Market State, write parquet or write registry entries.

## 1. Resolver Principle

```text
Market State Source Resolver
    = the future component that resolves profile-required source aliases
      into exact governed dataset/view authorities.
```

It consumes:

```text
validated request intent
resolved_profile block
resolved_universe_and_scope block
source_version_policy
output_mode
validation_level
```

It produces only source-resolution fields. It must not resolve partition
availability, row coverage, builders, validators or output paths.

## 2. Input Contract

Required future inputs:

```text
request_id
request_fingerprint
resolved_profile_id
resolved_profile_version
profile_required_source_aliases
resolved_universe_fingerprint
universe_manifest_hash
resolved_calendar_authority_id
resolved_calendar_version
resolved_exchange_scope
source_version_policy
output_mode
validation_level
```

For v0.1:

```text
source_version_policy = exact_governed_or_block
output_mode = candidate
```

No fallback is allowed.

## 3. Source Alias Resolution

Rule:

```text
one profile-required source alias
    = exactly one authorized governed source resolution
```

If an alias resolves to zero or multiple candidates, source resolution blocks
before partition and coverage resolution.

The resolver must preserve the distinction between:

```text
source alias
    = semantic source role required by profile

dataset/view authority
    = governed physical or logical source that satisfies that role
```

## 4. Governed Source Evidence

Each resolved source must reference:

```text
source_alias
dataset_id
dataset_version
view_id
source_authority_status
contract_id
contract_hash
schema_id
schema_hash
physical_location_authority
content_fingerprint
declared_coverage_manifest_hash
consumption_policy_id
consumption_policy_hash
source_restriction_ids
allowed_use
forbidden_use
```

The `declared_coverage_manifest_hash` is not a partition coverage proof. It is
only the governed source-level coverage declaration consumed later by
`market_state_partition_and_coverage_resolver_design_v0_1`.

## 5. Authority Status Model

The resolver must classify each source:

```text
official_dataset
proven_restricted_dataset
validated_candidate
scoped_candidate
semantic_only_not_physical
blocked
```

For v0.1 candidate output, source authority may be restricted or candidate only
if the profile and consumption policies allow it explicitly. The resolver must
carry those restrictions into the execution plan and future authorization
checks.

## 6. Resolved Sources Output

The resolver must populate the Execution Plan `resolved_sources` block:

```text
source_alias
dataset_id
dataset_version
view_id
contract_id
contract_hash
schema_id
schema_hash
physical_location_authority
content_fingerprint
coverage_manifest_hash
consumption_policy_id
consumption_policy_hash
```

Additional resolver outputs for later gates:

```text
resolved_source_set_id
resolved_source_set_fingerprint
source_resolution_status
required_source_alias_count
resolved_source_alias_count
blocked_source_alias_count
source_resolution_manifest_ref
source_resolution_manifest_hash
source_authority_status
source_restriction_ids
allowed_use
forbidden_use
blocking_findings
```

## 7. Blocking Rules

The source resolver must block if:

```text
required_source_alias_missing
source_alias_not_declared_by_profile
source_version_policy_not_exact_governed_or_block
source_registry_entry_missing
source_version_missing_or_ambiguous
multiple_sources_resolve_for_alias
no_authorized_source_for_alias
dataset_contract_missing
schema_contract_missing
consumption_policy_missing
physical_location_authority_missing
content_fingerprint_missing
declared_coverage_manifest_missing
source_not_authorized_for_output_mode
source_restrictions_conflict_with_profile
semantic_only_source_used_as_physical_dataset
silent_fallback_attempted
raw_source_substituted_for_guarded_view
current_or_unversioned_source_requested
```

Blocked source resolution must stop before partition and coverage resolution.

## 8. No Fallback Policy

The resolver must not substitute:

```text
raw OHLCV for quote-guarded view
current source version for exact governed version
candidate dataset for official dataset when official output is requested
semantic profile registry for physical source
alternate dataset with similar columns
```

Fallbacks require a separate explicit policy and authorization.

## 9. Fingerprint Contribution

The resolver contributes to `execution_plan_fingerprint` through:

```text
resolved_source_set_fingerprint
source_alias
dataset_id
dataset_version
view_id
contract_hash
schema_hash
physical_location_authority
content_fingerprint
declared_coverage_manifest_hash
consumption_policy_hash
source_restriction_ids
```

It must not include:

```text
resolver_run_time
machine name
temporary registry lookup path
log path
```

## 10. Boundary To Future Resolver

After source resolution, the next gate must design:

```text
market_state_partition_and_coverage_resolver_design_v0_1
```

That resolver may consume resolved source authorities and resolved universe
scope, but must not alter source alias identity or source versions.

## 11. Closure

```text
market_state_source_resolver_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

source_resolver_executions = 0
source_registry_runtime_reads = 0
source_contract_runtime_reads = 0
source_schema_runtime_reads = 0
source_consumption_policy_runtime_reads = 0
source_rows_read = 0
source_parquet_files_read = 0
resolved_source_sets_created = 0
execution_plans_created = 0
request_records_created = 0
requests_executed = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_partition_and_coverage_resolver_design_v0_1
```
