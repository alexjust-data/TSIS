# Event State Profile Promotion Readout v0.1

run_id = `event_state_profile_promotion_v0_1_20260724T203016Z`
script_version = `event_state_profile_promotion_v0_1`

```text
event_state_profile_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
promoted_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
accepted_event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
registry_artifacts_written = 4
candidate_records_reviewed = 8
blocked_contexts = 1
hard_validation_failures = 0
official_event_state_profile_promotion_executed = true
official_event_state_dataset_promotion = false
official_event_state_parquet_files_written = 0
candidate_event_state_records_copied = false
event_detection_authorized = false
source_market_data_rows_read = 0
production = false
downstream_consumption = false
next_allowed_gate = event_state_profile_artifact_validation_v0_1
```

The promoted artifact is an official Event State semantic profile registry
package only. It does not promote complete TSIS Event State, write or copy
parquet, authorize event detection, authorize production, authorize downstream
consumption or open full-history/full-universe execution.
