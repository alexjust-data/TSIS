# Market State On-Demand Incremental Overlap Execution Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`

## Decision

The incremental overlap execution gate is authorized with restrictions.

```text
authorized_next_gate =
market_state_on_demand_incremental_overlap_execution_v0_1

execution_performed =
false
```

## Authorized Incremental Scope

```text
baseline_dataset =
market_state_candidate_dataset_v0_1_433288b634924676

profile =
market_state_core_four_intraday_profile_v0_1

exchange =
XNYS

instruments =
AAME
ABEO
ABUS

baseline_sessions =
2021-01-19
2021-03-15
2022-11-25

delta_session =
2023-03-20

requested_contexts =
12
```

## Expected Runtime Proof

The next run must prove:

```text
12 requested contexts
=
8 reusable_validated baseline contexts
+
1 known unavailable baseline context
+
3 delta contexts to build
```

It must not rebuild the eight reusable contexts.

## Evidence Used For Delta Selection

The governed candidate source contains records for the three authorized
instruments on the selected delta session:

```text
source =
market_state_candidate_records.jsonl

source_sha256 =
e166ad63a571327455047ed166e347e0c9c4d18dd233bf0986bc6980b1f1d7f6

delta_session =
2023-03-20

delta_decision_timestamp_utc =
2023-03-20T13:30:00Z

delta_records_found =
3
```

This was a bounded scope inspection of the already-governed candidate source,
not a Market State materialization and not a market-data source read.

## Restrictions

```text
official_dataset =
false

production =
false

downstream =
false

event_state_on_demand =
false

unbounded_incremental_execution =
false

baseline_registry_entry_mutation =
false
```

## Boundary Counters

```text
new_requests_created = 0
execution_plans_created = 0
resolver_executions = 0
materializer_executions = 0
validator_executions = 0
candidate_files_written = 0
candidate_dataset_registry_entries_written = 0
registry_entry_mutations = 0
```

## Close

```text
authorization_status =
AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

next_gate =
market_state_on_demand_incremental_overlap_execution_v0_1
```
