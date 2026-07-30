# Market State Core Four Replay Availability Evidence Sidecar Execution and Validation Readout v0.1

Gate: `market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1`
Date: `2026-07-29`
Status: `CLOSED_PASS_SCALE_VALIDATION_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ`

```text
case_count = 16
failed_cases = 0
sidecar_records_written = 104
candidate_dataset_id = market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762
candidate_dataset_fingerprint = 516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
candidate_parquet_sha256 = bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68
sidecar_sha256 = 8e426b09bb1cafac26e49c7a81de31ef4ea60ca3b56ac3aa766ba13a0772c5ac
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
production = false
downstream = false
```

The active sidecar now targets the scale-validation candidate required by physical evidence alignment. Availability timestamps are row-addressable and bounded by `zero_latency_candidate_replay_publication_policy_v0_1`; this remains candidate integration evidence, not production or downstream authority.
