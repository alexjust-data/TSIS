# Market State Universe Resolver Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_profile_resolver_design_v0_1`

This document defines the future Market State universe resolver.

It is design-only. It does not execute a resolver, read identity/calendar
sources at runtime, create universe manifests, create execution plans, read
market data, build Market State, write parquet or write registry entries.

## 1. Resolver Principle

```text
Market State Universe Resolver
    = the future component that resolves universe intent and temporal scope
      into exact point-in-time instrument-session membership.
```

It consumes:

```text
validated request intent
resolved_profile block
universe selection mode
date or session scope
calendar authority intent
point-in-time policy intent
as-of policy intent
```

It produces only universe and session-resolution fields. It must not resolve
physical market-data sources, partitions, builders, validators or output paths.

## 2. Input Contract

Required future inputs:

```text
request_id
request_fingerprint
resolved_profile_id
resolved_profile_version
universe_selection_mode
universe_definition_id
explicit_instrument_ids
instrument_filter_mode
start_date
end_date
session_dates
calendar_authority_id
exchange_scope
point_in_time_policy_id
as_of_policy_id
```

For v0.1:

```text
universe_definition_id xor explicit_instrument_ids
```

Both may be present only if one is explicitly marked as the primary universe and
the other as a filter. Ambiguity blocks before source resolution.

## 3. Point-In-Time Membership

The resolver must preserve:

```text
instrument identity
symbol history
listing lifecycle
delisting lifecycle
exchange membership
security type eligibility
session-date eligibility
point-in-time universe membership
```

It must not use current ticker state to infer historical membership.

Prohibited shortcuts:

```text
current listing leakage
survivorship leakage
retroactive exchange assignment
symbol-only identity joins
unversioned universe definitions
silent calendar fallback
```

## 4. Temporal Scope Resolution

The resolver must normalize one temporal scope into governed sessions:

```text
date_range -> resolved_session_dates
```

or:

```text
session_dates -> resolved_session_dates
```

It must preserve:

```text
resolved_calendar_authority_id
resolved_calendar_version
calendar_source_snapshot_fingerprint
exchange_scope
session_date
session_open_utc
session_close_utc
session_type
is_early_close
calendar_row_fingerprint
```

The resolver must not infer sessions from observed bars or source coverage.

## 5. Resolved Universe Output

The resolver must produce one deterministic `resolved_universe` result and
populate the Execution Plan `resolved_universe_and_scope` block.

Primary resolved-universe fields:

```text
resolved_universe_id
resolved_universe_version
resolution_method
universe_definition_id
universe_definition_version
point_in_time_policy_id
calendar_authority_id
exchange_scope
resolved_session_dates
resolved_instrument_count
resolved_instrument_session_context_count
universe_manifest_reference
universe_manifest_fingerprint
resolved_universe_fingerprint
coverage_status
blocking_findings
```

Execution Plan block fields:

```text
resolved_universe_definition_id
resolved_universe_version
universe_manifest_path
universe_manifest_hash
resolved_universe_fingerprint
instrument_count
resolved_instrument_ids_or_manifest_ref
resolved_session_dates_or_manifest_ref
resolved_exchange_scope
resolved_calendar_authority_id
resolved_calendar_version
instrument_session_context_count
```

Additional resolver outputs for later gates:

```text
instrument_identity_authority_id
instrument_identity_authority_hash
universe_policy_id
universe_policy_hash
point_in_time_policy_hash
as_of_policy_hash
calendar_source_snapshot_fingerprint
session_manifest_hash
blocked_membership_report_hash
resolved_universe_fingerprint
coverage_status
blocking_findings
excluded_contexts_count
blocked_contexts_count
resolved_contexts_count
```

For large scopes, the execution plan may reference a manifest rather than embed
all instrument and session rows. The manifest hash must be part of the plan
fingerprint.

## 6. Membership Manifest Requirement

A future universe manifest must be deterministic and include at minimum:

```text
instrument_id
symbol_as_of_session
exchange_id
session_date
session_open_utc
session_close_utc
calendar_version
calendar_row_fingerprint
membership_status
membership_reason
membership_as_of_utc
identity_lineage_ref
universe_definition_ref
```

The manifest represents resolved scope. It is not a Market State dataset.

The resolver must distinguish:

```text
excluded
    = context did not satisfy the governed universe rule

blocked
    = TSIS cannot prove whether the context satisfies the rule
```

Required context accounting:

```text
requested_instrument_session_contexts
    = resolved_contexts
    + blocked_contexts
    + excluded_contexts
```

## 7. Blocking Rules

The universe resolver must block if:

```text
universe selection missing
universe_definition_id and explicit_instrument_ids conflict
universe_definition_id missing version
universe definition not governed
explicit_instrument_ids not canonical instrument IDs
point_in_time_policy_id missing
as_of_policy_id missing
instrument identity authority missing
calendar authority missing
calendar version missing
exchange scope ambiguous
date range and session_dates conflict
session date not found in governed calendar
multiple calendar rows for exchange + session_date
instrument membership ambiguous for session date
current symbol/listing state required to resolve history
membership manifest hash cannot be produced
instrument_session_context_count exceeds authorization
```

Blocked universe resolution must stop before source resolution.

## 8. Resolution Status

The resolver status must remain separate from blocking findings:

```text
universe_resolution_status =
    resolved
    blocked
    partially_resolved
    superseded
    quarantined
```

For v0.1:

```text
partial execution = not automatically authorized
```

Partially resolved scopes may be recorded, but a later execution authorization
must explicitly decide whether they can be consumed.

## 9. Fingerprint Contribution

The resolver contributes to `execution_plan_fingerprint` through:

```text
resolved_universe_definition_id
resolved_universe_version
universe_manifest_hash
resolved_universe_fingerprint
instrument_count
resolved_session_dates_or_manifest_ref
resolved_exchange_scope
resolved_calendar_authority_id
resolved_calendar_version
calendar_source_snapshot_fingerprint
session_manifest_hash
instrument_session_context_count
point_in_time_policy_hash
as_of_policy_hash
```

It must not include:

```text
resolver_run_time
machine name
temporary manifest path
log path
```

## 10. Boundary To Future Resolvers

After universe resolution, future gates must design:

```text
market_state_source_resolver_design_v0_1
market_state_partition_and_coverage_resolver_design_v0_1
```

Those resolvers may consume resolved instruments and sessions, but must not
alter the universe identity, membership or calendar binding.

## 11. Closure

```text
market_state_universe_resolver_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

universe_resolver_executions = 0
universe_manifests_created = 0
instrument_session_contexts_created = 0
calendar_runtime_reads = 0
instrument_master_runtime_reads = 0
instrument_identity_runtime_reads = 0
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
    = market_state_source_resolver_design_v0_1
```
