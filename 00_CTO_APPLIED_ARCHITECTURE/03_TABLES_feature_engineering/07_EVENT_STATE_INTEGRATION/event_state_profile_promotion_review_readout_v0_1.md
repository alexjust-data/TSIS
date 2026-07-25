# Event State Profile Promotion Review Readout v0.1

run_id = `event_state_profile_promotion_review_v0_1_20260724T201046Z`
script_version = `event_state_profile_promotion_review_v0_1`

```text
event_state_profile_promotion_review = APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS
reviewed_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
event_type_scope = event_type:market_data:session_opened
evidence_artifacts_checked = 15
candidate_records_reviewed = 8
event_instances_created = 3
event_window_bindings_created = 3
instrument_session_projections_created = 9
market_state_bindings_found = 8
blocked_contexts = 1
fallback_uses = 0
physical_validation_hard_failures = 0
candidate_dataset_review_hard_failures = 0
hard_review_failures = 0
official_event_state_profile_promotion_executed = false
official_event_state_dataset_promotion = false
official_parquet_files_written = 0
event_state_materialization = false
production = false
downstream_consumption = false
next_allowed_gate = event_state_profile_promotion_authorization_v0_1
```

The review approves a separate semantic profile promotion authorization only if
the decision is `APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS`.
It does not promote an Event State profile, promote a dataset, write parquet,
materialize Event State, authorize production, or authorize downstream
consumption.
