# Market State Execution Plan Contract Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Parent Gate: `market_state_request_contract_design_v0_1`

This document defines the canonical execution plan contract for future Market
State on-demand generation.

It is design-only. It does not create a plan, execute resolvers, read data,
build Market State, write parquet or write registry entries.

## 1. Contract Principle

```text
Market State Request
    = what representation is required

Market State Execution Plan
    = complete, immutable and reproducible resolution of that request
```

A future materializer must consume a frozen execution plan. It must not
re-resolve:

```text
profile
profile version
universe
instruments
sessions
calendar
sources
source versions
partitions
builders
validators
output policy
quantitative limits
```

## 2. Plan Genealogy

Every execution plan must derive from exactly one normalized request.

Required identity fields:

```text
execution_plan_id
execution_plan_contract_version
request_id
request_fingerprint
created_at_utc
planner_id
planner_version
planner_contract_hash
```

The `created_at_utc` field is audit lineage. It does not participate in the
execution plan semantic fingerprint.

## 3. Resolved Profile Block

The plan must resolve all profile ambiguity before execution.

Required fields:

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
```

No unresolved policy such as `latest`, `compatible`, `default` or implicit
version selection may remain in the plan.

## 4. Resolved Universe And Scope Block

Required fields:

```text
resolved_universe_definition_id
resolved_universe_version
universe_manifest_path
universe_manifest_hash
instrument_count
resolved_instrument_ids_or_manifest_ref
resolved_session_dates_or_manifest_ref
resolved_exchange_scope
resolved_calendar_authority_id
resolved_calendar_version
instrument_session_context_count
```

For large scopes, the plan may reference manifests instead of embedding full
lists, but the manifest hash must be part of the plan fingerprint.

## 5. Resolved Source Block

For each required source alias:

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

Rule:

```text
one required source alias
    = exactly one authorized physical resolution
```

If there are zero or multiple authorized resolutions, the plan status must be
`blocked`.

## 6. Partition And Coverage Block

The plan must classify all requested work:

```text
requested_partitions
reusable_validated_partitions
partitions_to_build
blocked_partitions
missing_partitions
quarantined_partitions
```

Required invariant:

```text
requested_partitions
    =
    reusable_validated_partitions
    + partitions_to_build
    + blocked_partitions
    + missing_partitions
    + quarantined_partitions
```

For v0.1, partial execution is not automatically authorized. A later bounded
execution authorization must decide whether a partially resolved plan can be
consumed.

## 7. Resolved Builder Block

For every builder required by the profile:

```text
builder_id
builder_version
builder_contract_id
builder_contract_hash
input_source_aliases
output_variable_ids
temporal_cutoff_policy_id
temporal_cutoff_policy_hash
```

A different builder version may produce a different dataset and must change the
execution plan fingerprint.

## 8. Resolved Validator Block

The plan must know the validation obligations before execution.

Required fields:

```text
validator_id
validator_version
validator_contract_hash
validation_scope
blocking_severity
expected_validation_reports
```

The future materializer cannot choose validators after output creation.

## 9. Output Plan Block

Required fields:

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

The plan may define output root authority, but runtime-specific paths that
depend on `execution_run_id` must not be included in the plan fingerprint.

## 10. Quantitative Limits

The plan must freeze:

```text
maximum_instruments
maximum_sessions
maximum_contexts
maximum_source_rows
maximum_output_rows
maximum_output_bytes
maximum_partitions
```

If estimated work exceeds authorized limits, the plan must be blocked before
execution.

## 11. Fingerprint Policy

Two fingerprints remain distinct:

```text
request_fingerprint
    = meaning of the request

execution_plan_fingerprint
    = concrete resolution of the request
```

The `execution_plan_fingerprint` must include:

```text
request_fingerprint
resolved profile identity and hash
resolved universe manifest hash
resolved calendar identity and version
resolved source identities and fingerprints
coverage and partition manifests
builder identities and contract hashes
validator identities and contract hashes
output schema and policy
quantitative limits
```

It must exclude:

```text
run start time
machine name
temporary output paths
heartbeat state
log paths
wall-clock runtime values
```

Rule:

```text
same request_fingerprint
same resolved authorities
same plan contract
    -> same execution_plan_fingerprint
```

## 12. Plan Status Model

```text
draft
resolved
blocked
authorized_for_execution
consumed
superseded
quarantined
```

The plan status must remain separate from `blocking_findings`.

Example:

```text
plan_status = blocked
blocking_findings = [missing_source_partition, ambiguous_profile_version]
```

## 13. Resolution Classes

The contract distinguishes:

```text
invalid_request
    = request violates request contract

unresolvable_request
    = valid request cannot be resolved with available authorities

partially_resolvable_request
    = some requested scope can be resolved and some blocks

fully_resolved_request
    = all requested scope has a complete plan
```

For v0.1:

```text
partial execution
    = not automatically authorized
```

## 14. Boundary To Future Gates

The next resolver gates must produce fields that conform to this plan contract:

```text
market_state_profile_resolver_design_v0_1
market_state_universe_resolver_design_v0_1
market_state_source_resolver_design_v0_1
market_state_partition_and_coverage_resolver_design_v0_1
```

Resolvers should not invent output structures incompatible with the frozen plan
contract.

## 15. Closure

```text
market_state_execution_plan_contract_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

execution_plans_created = 0
request_records_created = 0
requests_executed = 0
profile_resolver_executions = 0
universe_resolver_executions = 0
source_resolver_executions = 0
source_rows_read = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_profile_resolver_design_v0_1
```
