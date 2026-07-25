# Market State Profile Resolver Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_execution_plan_contract_design_v0_1`

This document defines the future Market State profile resolver.

It is design-only. It does not execute a resolver, read profile registries at
runtime, create execution plans, read data, build Market State, write parquet or
write registry entries.

## 1. Resolver Principle

```text
Market State Profile Resolver
    = the future component that resolves profile intent
      into an exact profile contract and the `resolved_profile`
      block of a Market State Execution Plan.
```

It consumes validated request intent:

```text
profile_id
profile_version_policy
profile_version
output_mode
validation_level
```

It produces only profile-resolution fields. It must not resolve universe,
calendar, physical sources, partitions, builders, validators or output paths.

## 2. Input Contract

Required future inputs:

```text
request_id
request_fingerprint
profile_id
profile_version_policy
profile_version
output_mode
validation_level
```

For v0.1:

```text
profile_version_policy = exact
output_mode = candidate
```

No `latest`, `compatible`, `default` or implicit profile version selection is
allowed.

## 3. Registry Authority

The resolver may use only governed profile registry artifacts authorized by a
later execution gate.

For the first supported target:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
profile_status_required = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
profile_classification = official_semantic_profile_not_physical_dataset
profile_artifact_validation_required = true
```

The resolver must preserve this distinction:

```text
official semantic profile
    != official physical dataset
```

Therefore resolving the profile does not imply:

```text
official_market_state_dataset = true
official_market_state_parquet = true
downstream_consumption = true
```

## 4. Resolved Profile Output

The resolver must populate the Execution Plan `resolved_profile` block:

```text
resolved_profile_id
resolved_profile_version
profile_contract_id
profile_contract_hash
profile_artifact_validation_run
expected_grain
expected_schema_id
expected_schema_hash
required_information_object_ids
required_state_variable_ids
profile_restriction_ids
profile_allowed_output_modes
profile_forbidden_output_modes
profile_required_source_aliases
profile_required_builder_roles
profile_required_validator_roles
```

Only the first ten fields are required by the current execution plan contract;
the restriction/source/builder/validator role fields are resolver outputs that
future resolver gates may consume.

## 5. Eligibility Rules

The profile resolver must block if:

```text
profile_id missing
profile_version missing
profile_version_policy != exact
profile registry entry missing
profile version not found
multiple profile versions match
profile status not official semantic profile
profile artifact validation missing
profile contract hash missing
schema contract missing
requested output_mode incompatible with profile restrictions
request tries to treat semantic profile as official physical dataset
required Information Objects missing
required State Variables missing
```

Blocked profile resolution must stop before universe and source resolution.

## 6. Restriction Propagation

The resolver must propagate profile restrictions into the execution plan and
future authorization checks.

For `market_state_core_four_intraday_profile_v0_1`, restrictions include:

```text
complete_tsis_market_state = false
official_market_state_dataset = false
official_market_state_parquet = false
production = false
downstream_consumption = false
quote_dependent_objects_excluded = true
profile_scope = core_four_intraday
```

These restrictions do not block candidate planning, but they block official
dataset claims and downstream consumption.

## 7. Profile Resolution Status

The resolver status must remain separate from blocking findings:

```text
profile_resolution_status =
    resolved
    blocked
    superseded
    quarantined
```

Example:

```text
profile_resolution_status = blocked
blocking_findings = [profile_artifact_validation_missing]
```

## 8. Fingerprint Contribution

The resolver contributes to `execution_plan_fingerprint` through:

```text
resolved_profile_id
resolved_profile_version
profile_contract_hash
expected_schema_hash
required_information_object_ids
required_state_variable_ids
profile_restriction_ids
profile_artifact_validation_run
```

It must not include:

```text
resolver_run_time
machine name
temporary registry lookup path
log path
```

## 9. Boundary To Future Resolvers

After profile resolution, future gates must design:

```text
market_state_universe_resolver_design_v0_1
market_state_source_resolver_design_v0_1
market_state_partition_and_coverage_resolver_design_v0_1
```

Those resolvers consume the resolved profile requirements but must not alter the
resolved profile identity or version.

## 10. Closure

```text
market_state_profile_resolver_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

profile_resolver_executions = 0
profile_registry_runtime_reads = 0
execution_plans_created = 0
request_records_created = 0
requests_executed = 0
source_rows_read = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_universe_resolver_design_v0_1
```
