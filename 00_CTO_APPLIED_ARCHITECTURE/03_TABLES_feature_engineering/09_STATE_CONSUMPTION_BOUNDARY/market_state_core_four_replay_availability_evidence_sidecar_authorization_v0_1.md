# Market State Core Four Replay Availability Evidence Sidecar Authorization v0.1

Gate: `market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1`
Date: `2026-07-29`
Status: `CLOSED_AUTHORIZED_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_EXECUTION_AND_VALIDATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ`

## Purpose

Authorize the next bounded execution-and-validation gate to create row-addressable replay availability evidence for the already validated Market State core-four physical candidate.

This authorization exists because the prior runtime interface regression correctly blocked before v0.1.2 reissue:

```text
physical row identity
↔
state_as_of_utc / state_available_at_utc
=
not yet bound one-to-one
```

## Authorized Next Gate

```text
market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1
```

The next gate may create and validate the sidecar. This authorization gate itself creates no sidecar records and opens no physical data.

## Required Sidecar Fields

```text
materialized_state_candidate_id
state_output_fingerprint
candidate_dataset_id
candidate_dataset_fingerprint
instrument_id
profile_id
physical_profile_id
decision_timestamp_utc
state_as_of_utc
state_available_at_utc
state_availability_policy_id
state_publication_latency_policy_id
state_publication_latency
component_availability_evidence
state_replay_consumption_legality
restriction_codes
```

## Boundaries

```text
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```
