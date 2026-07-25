# Market State Bounded On-Demand Execution Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`

```text
gate = market_state_bounded_on_demand_execution_authorization_v0_1
parent_gate = market_state_on_demand_execution_chain_joint_review_v0_1
authorized_next_gate = market_state_bounded_on_demand_execution_v0_1
authorized_requests_max = 1
authorized_execution_plans_max = 1
authorized_runs_max = 1
authorized_instruments_max = 3
authorized_sessions_max = 3
authorized_instrument_session_contexts_max = 9
request_records_created = 0
execution_plans_created = 0
resolver_executions = 0
run_records_created = 0
source_rows_read = 0
materializer_executions = 0
validator_executions = 0
registry_entries_written = 0
datasets_written = 0
production = false
downstream = false
```

The first bounded Market State on-demand execution authorization is recorded.
It freezes the next gate to a single small candidate run:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
exchange_scope = XNYS
session_dates = 2021-01-19, 2021-03-15, 2022-11-25
instrument_ids = AAME, ABEO, ABUS stable FIGI share-class identifiers
maximum_contexts = 9
output_mode = candidate
```

The execution must create a fresh candidate on-demand output from one frozen
Execution Plan. It may not copy or relabel the prior Scale C parquet as an
on-demand result.

The authorization preserves the joint-review restriction:

```text
partition_dispositions =
    reusable_validated
    to_build
    to_rebuild
    unavailable
    quarantined
    blocked
```

Missing physical coverage must be represented as an `unavailable` cause, not
as a separate overlapping disposition.

This gate created no requests, no execution plans, no resolver outputs, no run
records, no source reads, no candidate files, no validation reports, no
registry entries and no datasets.

The next allowed gate is:

```text
market_state_bounded_on_demand_execution_v0_1
```
