# Event State Profile Artifact Validation Readout v0.1

run_id = `event_state_profile_artifact_validation_v0_1_20260724T204410Z`
script_version = `event_state_profile_artifact_validation_v0_1`

```text
event_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS
profile_id = event_state_core_four_intraday_profile_v0_1
registry_artifacts_checked = 4
registry_sha256_mismatches = 0
registry_invariant_failures = 0
hard_validation_failures = 0
official_event_state_dataset_promotion = false
official_event_state_parquet_files_written = 0
candidate_event_state_records_copied = false
event_detection_authorized = false
source_market_data_rows_read = 0
production = false
downstream_consumption = false
next_allowed_gate = event_state_operational_registry_or_consumption_policy_design_only_after_explicit_authorization
```

The profile registry package is validated only if this gate closes pass with
restrictions. Operational dataset promotion, production, official parquet and
full-history/full-universe execution remain closed.
