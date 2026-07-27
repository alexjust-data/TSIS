# Market State On-Demand Incremental Overlap Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Authorization ID: `market_state_on_demand_incremental_overlap_execution_authorization_v0_1`

## Purpose

This authorization opens the next bounded execution gate for Market State
on-demand incremental overlap behavior.

It does not execute the run. It authorizes only one future execution gate:

```text
market_state_on_demand_incremental_overlap_execution_v0_1
```

The future execution must prove that a partially overlapping Market State
request can reuse already validated bounded exact-match partitions and build
only the new delta partitions.

## Parent Evidence

```text
baseline_run_id =
market_state_bounded_on_demand_execution_v0_1_20260724T232123Z

baseline_candidate_dataset_id =
market_state_candidate_dataset_v0_1_433288b634924676

baseline_candidate_dataset_fingerprint =
433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

baseline_scientific_dataset_fingerprint =
a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7

bounded_exact_match_reuse_status =
eligible_for_bounded_exact_match_reuse

reuse_transition_review_run =
market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z
```

## Authorized Scope

The authorized incremental request must preserve the original bounded scope and
add exactly one delta session:

```text
profile_id =
market_state_core_four_intraday_profile_v0_1

exchange_scope =
XNYS

instruments =
figi_share_class:BBG001S5N8T1  AAME
figi_share_class:BBG001S8T7K0  ABEO
figi_share_class:BBG001S6RSK0  ABUS

baseline_sessions =
2021-01-19
2021-03-15
2022-11-25

delta_session =
2023-03-20

requested_contexts =
12
```

The delta session was selected because the governed candidate source contains
records for all three instruments at the XNYS governed session-open timestamp:

```text
2023-03-20T13:30:00Z
```

## Expected Partition Disposition

The future execution plan must classify requested logical partitions as:

```text
requested_logical_partitions = 12

expected_reusable_validated = 8
expected_known_unavailable = 1
expected_to_build_delta = 3
```

The known unavailable baseline context is:

```text
instrument_id = figi_share_class:BBG001S5N8T1
ticker = AAME
session_date = 2022-11-25
decision_timestamp_utc = 2022-11-25T14:30:00Z
reason = missing_exact_decision_timestamp_source_candidate_record
available_candidate_timestamp = 2022-11-25T16:58:00Z
```

The execution must not silently convert this known unavailable context into a
materialized row unless a governed source or policy change is explicitly
recorded. No such change is authorized here.

## Authorized Future Actions

The next execution gate may:

```text
create one new Market State request record for the overlap scope
execute Profile Resolver
execute Universe Resolver
execute Source Resolver
execute Partition / Coverage Resolver
freeze one execution plan
consume this authorization once
open one run lifecycle
reuse eligible baseline partitions without rebuilding them
build only the delta partitions classified as to_build
validate the combined candidate result
record candidate dataset evolution evidence
emit an incremental overlap readout
```

## Prohibited Actions

This authorization does not allow:

```text
unbounded requests
new profiles
new instruments beyond the authorized three
sessions beyond the authorized four
rebuilding reusable_validated baseline partitions
fallback to non-authorized sources
source market-data row reads outside the governed candidate source contract
official dataset promotion
production use
downstream consumption
ML / RL / backtest consumption
Event State on-demand execution
registry mutation of the baseline entry in place
```

## Incremental Invariants

The future run must prove:

```text
Request B != Request A

Request B =
baseline scope
+
one delta session

Execution Plan B must contain:
reusable_validated
+
to_build_delta
+
known_unavailable
```

The materializer must execute only for the delta build set. If it rebuilds the
eight reusable baseline records, the incremental test fails.

## Boundary Counters

At this authorization gate:

```text
incremental_overlap_execution = NOT_EXECUTED
new_requests_created = 0
execution_plans_created = 0
resolver_executions = 0
materializer_executions = 0
validator_executions = 0
candidate_files_written = 0
candidate_dataset_registry_entries_written = 0
registry_entry_mutations = 0
official_dataset = false
production = false
downstream = false
```

## Closing Status

```text
authorization_status =
AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

next_gate =
market_state_on_demand_incremental_overlap_execution_v0_1
```
