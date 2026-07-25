# Market State Request Contract Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Parent Gate: `market_state_on_demand_capability_design_v0_1`

This document defines the canonical request contract for future Market State
on-demand generation.

It is design-only. It does not create a request, resolve a profile, read data,
create an execution plan, build Market State, write parquet or write registry
entries.

## 1. Contract Principle

```text
Market State Request
    = normalized user or system intent

Execution Plan
    = resolved construction instructions
```

A request declares what representation is required. It must not decide how the
representation will be built.

Therefore a request may name governed identities such as:

```text
profile_id
profile_version_policy
universe_definition_id
explicit_instrument_ids
date_or_session_scope
calendar_authority_id
point_in_time_policy_id
output_mode
validation_level
reuse_policy
```

But a request must not name or select:

```text
physical data paths
source parquet files
builder implementations
temporary output directories
resolved partitions
materializer internals
registry dataset identifiers
machine-specific state
```

Those belong to the future `market_state_execution_plan_contract_v0_1`.

## 2. Required Blocks

### 2.1 Request Identity

```text
request_type
request_contract_version
request_id
requested_at_utc
requested_by
request_purpose
```

Only `request_type = market_state` is valid for this contract.

`requested_at_utc` and `requested_by` are audit fields. They do not participate
in the semantic `request_fingerprint`.

### 2.2 Representation Intent

```text
profile_id
profile_version_policy
profile_version
resolution
grain
```

For v0.1:

```text
profile_version_policy = exact
```

Policies such as `latest_accepted` or `latest_compatible` are explicitly out of
scope until a later compatibility gate defines them.

### 2.3 Scientific Scope

The request must define one temporal scope:

```text
start_date + end_date
```

or:

```text
session_dates
```

The request must also define one universe selection mode:

```text
universe_definition_id
```

or:

```text
explicit_instrument_ids
```

Both may appear together only if the contract marks one as the primary universe
and the other as an explicit filter. Ambiguous coexistence blocks before
execution.

### 2.4 Temporal And Source Policy

```text
calendar_authority_id
exchange_scope
point_in_time_policy_id
as_of_policy_id
source_version_policy
```

The request defines policy intent. The future source and universe resolvers will
decide which exact governed artifacts satisfy that intent.

For v0.1:

```text
source_version_policy = exact_governed_or_block
```

No fallback is permitted.

### 2.5 Output Intent

```text
output_mode
output_format
partition_policy
validation_level
reuse_policy
```

For v0.1:

```text
output_mode = candidate
reuse_policy = reuse_if_exact_validated_match
```

Official output modes remain prohibited until a separate promotion and
consumption authority exists.

## 3. Request Fingerprint

The `request_fingerprint` is a deterministic hash of the normalized request
intent.

It must include:

```text
request_type
request_contract_version
profile_id
profile_version_policy
profile_version
resolution
grain
universe_definition_id or explicit_instrument_ids
date/session scope
calendar_authority_id
exchange_scope
point_in_time_policy_id
as_of_policy_id
source_version_policy
output_mode
output_format
partition_policy
validation_level
reuse_policy
```

It must exclude:

```text
request_id
requested_at_utc
requested_by
run_id
output_path
temporary path
machine id
wall-clock runtime values
```

Rule:

```text
same normalized request intent
    -> same request_fingerprint
```

But:

```text
same request_fingerprint
    != guaranteed same dataset
```

The future execution plan fingerprint will capture exact source versions,
partitions, builders, validators and output registry policy.

## 4. Validation And Blocking

The request contract must block before resolver execution if:

```text
request_type is not market_state
profile_id is missing
profile_version_policy is not exact
profile_version is missing
temporal scope is missing
both date range and session_dates are contradictory
universe selection is missing
universe_definition_id and explicit_instrument_ids conflict
calendar_authority_id is missing
point_in_time_policy_id is missing
as_of_policy_id is missing
source_version_policy permits fallback
output_mode is official or production
validation_level is missing
unknown fields attempt to name physical paths
```

Blocked requests are valid governance outcomes. They must not be repaired by
resolver inference.

## 5. Request Status Model

This contract defines statuses only for request records once a future gate
authorizes request creation.

```text
DRAFT_REQUEST
VALIDATED_INTENT_NO_EXECUTION
BLOCKED_BEFORE_RESOLUTION
RESOLVED_NO_EXECUTION
AUTHORIZED_FOR_BOUNDED_EXECUTION
RUNNING
VALIDATING
CLOSED_PASS_WITH_RESTRICTIONS
FAILED
QUARANTINED
```

This gate creates no request records.

## 6. Boundary To Execution Plan

The next gate must define:

```text
market_state_execution_plan_contract_v0_1
```

The execution plan will consume a validated request and resolve:

```text
exact profile contract
exact universe membership
exact sessions
exact source datasets and versions
exact partitions
builder and validator versions
quantitative limits
expected outputs
execution_plan_fingerprint
```

The materializer must later consume a frozen execution plan, not the raw request.

## 7. Closure

```text
market_state_request_contract_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

request_records_created = 0
requests_executed = 0
execution_plans_created = 0
source_rows_read = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false

next_allowed_gate
    = market_state_execution_plan_contract_design_v0_1
```
