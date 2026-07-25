# Event State Profile Promotion Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-24`
Scope: `official_event_state_profile_registry_promotion_only`

This authorization opens the promotion of a logical official profile registry
entry for the bounded Event State profile:

```text
event_state_core_four_intraday_profile_v0_1
```

It does not promote complete TSIS Event State, does not create an official Event
State dataset, does not write or copy parquet, and does not authorize production
or downstream consumption.

## Promotion Target

```text
promoted_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
profile_classification = official_event_state_semantic_profile
profile_scope = bounded_validated_core_four_event_state_profile_for_session_opened
complete_tsis_event_state = false
```

The promoted profile is semantic and contractual. It records that a bounded,
calendar-aware `session_opened` Event State profile has passed design, bounded
execution, physical validation, candidate dataset review and promotion review.

It is not a Data Foundation operational dataset registry entry and it is not a
production table.

## Required Prior Gate

```text
event_state_profile_promotion_review =
    APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS

accepted_review_run =
    event_state_profile_promotion_review_v0_1_20260724T201046Z

accepted_promotion_run =
    event_state_profile_promotion_v0_1_20260724T203016Z

promotion_status =
    OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
```

The accepted review found:

```text
candidate_records_reviewed = 8
event_instances_created = 3
event_window_bindings_created = 3
instrument_session_projections_created = 9
market_state_bindings_found = 8
blocked_contexts = 1
hard_review_failures = 0
```

## Authorized Writes

```text
official_profiles/event_state_core_four_intraday_profile_v0_1/README.md
official_profiles/event_state_core_four_intraday_profile_v0_1/PROFILE_MANIFEST.json
official_profiles/event_state_core_four_intraday_profile_v0_1/EVIDENCE_MANIFEST.json
official_profiles/event_state_core_four_intraday_profile_v0_1/EVENT_STATE_SCHEMA_CONTRACT.json
runs/<promotion_run_id>/pre_manifest.json
runs/<promotion_run_id>/heartbeat.json
runs/<promotion_run_id>/official_profile_registry_write_report.csv
runs/<promotion_run_id>/promotion_manifest.json
runs/<promotion_run_id>/final_manifest.json
runs/<promotion_run_id>/readout.md
event_state_profile_promotion_readout_v0_1.md
```

## Authority Boundary

```text
official_event_state_profile_registry_write_allowed = true
official_event_state_profile_promotion_allowed = true

official_event_state_dataset_registry_write_allowed = false
official_event_state_dataset_promotion_allowed = false
official_event_state_parquet_write_allowed = false
candidate_event_state_records_copy_allowed = false
event_state_materialization_allowed = false
event_detection_allowed = false
new_event_type_creation_allowed = false
production_allowed = false
downstream_consumption_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
source_market_data_reads_allowed = false
```

If this promotion passes, the next possible gate is a separate official Event
State profile artifact validation. Dataset promotion, production builders,
materialization and downstream consumption remain closed.
