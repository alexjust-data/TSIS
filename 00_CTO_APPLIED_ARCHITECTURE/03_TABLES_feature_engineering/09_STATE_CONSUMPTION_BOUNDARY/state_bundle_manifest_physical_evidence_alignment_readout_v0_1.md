# StateBundle Manifest Physical Evidence Alignment Readout v0.1

Gate: `state_bundle_manifest_physical_evidence_alignment_v0_1`
Date: `2026-07-29`
Status: `CLOSED_BLOCKED_REQUIRES_V0_1_2_BUNDLE_REISSUE_AND_REPLAY_TIMESTAMP_EVIDENCE_NO_PHYSICAL_READ`

## Result

The current physical-read evidence remains blocked. Provider v0.1.2 can express the required evidence, but the existing `case_01` response and bundle were emitted before v0.1.2 and cannot be promoted as physical consumption authority.

```text
case_count = 13
blocking_findings = 5
restricted_findings = 3
physical_read_authorization_ready = false
authorization_to_read_issued = false
```

## Blocking Findings

- `ALIGN_CONTROL_PLANE_ARTIFACT_VERSION_001`: control_plane_artifact_version
- `ALIGN_RESPONSE_HASH_001`: bundle_to_response_hash
- `ALIGN_DATASET_IDENTITY_001`: dataset_identity
- `ALIGN_ARTIFACT_HASH_CHAIN_001`: artifact_hash_chain
- `ALIGN_REPLAY_TIMESTAMPS_SCHEMA_001`: replay_timestamp_contract

## Critical Observations

```text
old StateBundleManifest v0.1 case_01 = control-plane evidence only
old bundle does not match physical candidate dataset fingerprint
old bundle does not freeze observed response hash
old bundle does not directly freeze candidate_output_manifest, parquet hash and schema hash
Market State physical schema lacks state_as_of_utc
Market State physical schema lacks state_available_at_utc
```

## Boundaries Preserved

```text
parquet_opened = false
parquet_hash_recomputed = false
state_rows_read = 0
physical_artifacts_opened = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
official_dataset = false
```

## Required Next Gates

- `market_state_core_four_replay_availability_timestamp_contract_v0_1`
- `runtime_user_invocation_bounded_interface_execution_regression_v0_1_2`

Do not reopen `bounded_state_bundle_read_and_replay_authorization_v0_1` until both prerequisites are closed.
