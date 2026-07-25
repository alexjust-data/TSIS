# Market State Bounded On-Demand Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-25`

```text
gate = market_state_bounded_on_demand_execution_authorization_v0_1
parent_gate = market_state_on_demand_execution_chain_joint_review_v0_1
authorization_scope = bounded_market_state_on_demand_execution_only
authorized_next_gate = market_state_bounded_on_demand_execution_v0_1
request_records_created = 0
execution_plans_created = 0
resolver_executions = 0
run_records_created = 0
source_rows_read = 0
materializer_executions = 0
validator_executions = 0
registry_entries_written = 0
datasets_written = 0
official_dataset = false
production = false
downstream = false
```

This authorization consumes the Market State on-demand execution-chain joint
review and authorizes opening one bounded execution gate.

It does not execute that gate.

## Authorized Bounded Scope

The future bounded execution may create exactly one candidate Market State
on-demand run for:

```text
request_type = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
profile_version_policy = exact
output_mode = candidate
exchange_scope = XNYS
session_dates = 2021-01-19, 2021-03-15, 2022-11-25
instrument_ids =
    figi_share_class:BBG001S5N8T1  # AAME
    figi_share_class:BBG001S8T7K0  # ABEO
    figi_share_class:BBG001S6RSK0  # ABUS
maximum_instruments = 3
maximum_sessions = 3
maximum_instrument_session_contexts = 9
```

This scope mirrors the bounded Event State evidence run:

```text
event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z
```

That prior run is evidence for scope selection only. It is not an on-demand
Market State output and must not be copied as the result of this future run.

## Authorized Future Actions

The next gate may, only inside the bounded scope above:

```text
create one normalized Market State request record
execute the Profile Resolver
execute the Universe Resolver
execute the Source Resolver
execute the Partition / Coverage Resolver
create one frozen Execution Plan
consume one explicit execution authorization
create one run record
create pre-run, heartbeat, final or failure manifests
execute the Market State materializer
write candidate Market State output files
execute the Market State validator
write validation reports
write one candidate dataset registry entry
emit a bounded execution readout
```

## Required Restrictions

The future execution must:

```text
use output_mode = candidate
use profile_version_policy = exact
use source_version_policy = exact_governed_or_block
use no fallback source substitution
materialize fresh candidate output from the frozen Execution Plan
not copy the previous Scale C parquet as the on-demand output
preserve the refined partition disposition model
record every requested context as emitted, blocked or quarantined
```

The refined partition disposition model for this authorized execution is:

```text
reusable_validated
to_build
to_rebuild
unavailable
quarantined
blocked
```

`missing` is not an independent disposition in this authorization. Missing
source coverage must be recorded as a cause of `unavailable`, not as an
overlapping state.

## Explicit Prohibitions

This authorization does not allow:

```text
unbounded Market State execution
full-history execution
full-universe execution
Event State execution
Event Instance creation
Event Window creation
new Event Types
new Market State profiles
profile promotion
official Market State dataset promotion
official parquet writes
production
downstream consumption
backtesting
ML/RL consumption
strategy evaluation
```

## Closure

This document records authorization only. The authorization is consumed by
being recorded for the next bounded execution gate and cannot be reused for a
different scope.

The next allowed gate is:

```text
market_state_bounded_on_demand_execution_v0_1
```
