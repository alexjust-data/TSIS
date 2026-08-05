# Event State `session_opened` Replay Availability Sidecar Readout v0.1

```text
event_state_session_opened_replay_availability_evidence_sidecar_v0_1 =
CLOSED_PASS_ROW_ADDRESSABLE_EVENT_STATE_REPLAY_AVAILABILITY_EVIDENCE_WITH_RESTRICTIONS_NO_CONSUMER_AUTHORIZATION
case_count = 52
failed_cases = 0
physical Event State candidate files opened = 1
candidate rows scanned = 8
candidate rows selected = 1
Market State Parquet opened = false
backtester files modified = 0
BT-GATE-015 implementation = NOT_AUTHORIZED
Event State physical consumer read = NOT_AUTHORIZED
```

The row-addressable sidecar proves `event_state_available_at_utc`
for the exact on-demand AAME record. It does not itself authorize
consumer implementation or physical replay.
