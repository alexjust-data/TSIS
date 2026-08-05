# BT-GATE-015 V0.3 Consumed Failure Readout

```text
BT-GATE-015 = OPEN_POSTEXECUTION_FAILURE_REVIEW_REQUIRED
V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3 = PROHIBITED
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION = NOT_AUTHORIZED
```

The externally approved R2 pre-execution package had SHA-256
`52aab61b0f6343448d47ae988bc575df1ae86d485c4c4d3ab854bfdd554c47fe`.
The command executed once at `2026-08-05T11:08:31Z`.

```text
physical_data_files_opened = 1
physical_state_records_scanned = 8
physical_state_rows_selected = 1
market_state_dependency_events = 1
event_state_events_emitted = 0
event_state_store_inserts = 0
bounded_probe_observations = 0
failure_code = FAIL_EVENT_STATE_IDENTITY_MISMATCH
validation_phase_reached = PHYSICAL_ROW_VALIDATION
```

The subsequent external postexecution review confirmed the exact cause from
existing provider and consumer evidence without reopening the candidate:

```text
physical.source_market_state_candidate_dataset_fingerprint
was incorrectly compared with
sidecar.market_state_availability_evidence_dataset_fingerprint

correct comparison =
sidecar.market_state_dependency_dataset_fingerprint
```

The external report SHA-256 is
`faf069958509ee07d87db02e3e6bf9cc594758524d9eac77465b62e86d50e590`.
Provider data was not modified and V0.3 must never be rerun.
