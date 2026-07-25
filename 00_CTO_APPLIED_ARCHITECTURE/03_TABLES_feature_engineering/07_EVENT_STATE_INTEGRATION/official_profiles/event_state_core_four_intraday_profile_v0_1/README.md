# event_state_core_four_intraday_profile_v0_1

Status: `OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS`
Date: `2026-07-24`

This directory registers the bounded Event State profile as an official semantic
profile contract under Applied Architecture.

It is not complete TSIS Event State, not an operational Data Foundation dataset
registry, not production, and not downstream-consumable by itself.

```text
promotion_run_id = event_state_profile_promotion_v0_1_20260724T203016Z
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
accepted_event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
candidate_records_reviewed = 8
blocked_contexts = 1
hard_validation_failures = 0
official_event_state_dataset_promotion = false
official_event_state_parquet_written = false
event_detection_authorized = false
downstream_consumption_authorized = false
```

Live restrictions:

```text
complete_tsis_event_state = false
event_type_scope = session_opened_only
halt_resumed_excluded = true
source_market_state_physical_dataset_official = false
full_history = false
full_universe = false
production = false
downstream_consumable = false
```
