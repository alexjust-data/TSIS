# Market State Core Four Replay Availability Timestamp Contract v0.1 Readout

Gate: `market_state_core_four_replay_availability_timestamp_contract_v0_1`
Date: `2026-07-29`
Status: `CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ`

## Result

The replay timestamp contract for `market_state_core_four_intraday_profile_v0_1` is closed as validation-hardened, contract-ready with restrictions and no physical read.

```text
case_count = 30
failed_cases = 0
missing_required_case_ids = 0
duplicate_case_ids = 0
unexpected_case_ids = 0
```

## Validation Hardening

The runner now validates every fixture through both layers:

```text
JSON Schema validation
+
semantic validation
```

It also closes the external semantic-enforcement findings:

```text
required core-four Information Object coverage
component status -> row legality coherence
state_availability_status -> replay legality coherence
publication latency included in state_available_at_utc
PT0S bound to zero-latency policy
timestamp ordering across source/component/state
restriction propagation from components to row
canonical UTC Z timestamp representation
ordered ISO-8601 duration parsing
```

## Closed Timestamp Semantics

```text
decision_timestamp_utc = market instant represented by the row
state_as_of_utc = max source-information timestamp incorporated into the complete emitted row
state_available_at_utc = first historical instant the complete row could legally be delivered
```

Replay eligibility remains:

```text
event_loop.clock >= state_available_at_utc
```

## Boundaries Preserved

```text
physical_artifacts_opened = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```

## Next Required Gate

```text
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

After that gate reissues a v0.1.2 response/bundle with the required timestamp evidence, repeat `state_bundle_manifest_physical_evidence_alignment_v0_1` before reopening any bounded read-and-replay authorization.
