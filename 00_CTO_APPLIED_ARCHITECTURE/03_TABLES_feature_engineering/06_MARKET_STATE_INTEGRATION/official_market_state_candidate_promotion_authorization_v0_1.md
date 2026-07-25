# Official Market State Candidate Promotion Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `official_core_four_profile_registry_promotion_only`

This authorization opens the promotion of a logical official profile registry
entry for the bounded core-four intraday Market State profile. It does not
promote complete TSIS Market State, does not write or copy an official parquet
dataset, and does not authorize production or downstream consumption.

## Promotion Target

```text
promoted_profile_id = market_state_core_four_intraday_profile_v0_1
source_physical_profile_id = core_four_market_state_profile_v0_1
source_physical_schema_version = core_four_market_state_candidate_physical_schema_v0_1
profile_classification = official_profile
profile_scope = bounded_core_four_intraday_market_state_profile
complete_tsis_market_state = false
```

The promotion target is a profile contract and evidence registry package under
this applied architecture layer. It is not an operational Data Foundation
dataset registry and it is not a production table.

## Required Prior Gate

```text
official_market_state_candidate_promotion_review = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS
accepted_review_run = official_market_state_candidate_promotion_review_v0_1_20260723T192107Z
accepted_promotion_run = official_market_state_candidate_promotion_v0_1_20260723T193403Z
promotion_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
```

## Authorized Writes

```text
official_profiles/market_state_core_four_intraday_profile_v0_1/README.md
official_profiles/market_state_core_four_intraday_profile_v0_1/PROFILE_MANIFEST.json
official_profiles/market_state_core_four_intraday_profile_v0_1/EVIDENCE_MANIFEST.json
official_profiles/market_state_core_four_intraday_profile_v0_1/PHYSICAL_SCHEMA_CONTRACT.json
runs/<promotion_run_id>/pre_manifest.json
runs/<promotion_run_id>/heartbeat.json
runs/<promotion_run_id>/official_profile_registry_write_report.csv
runs/<promotion_run_id>/promotion_manifest.json
runs/<promotion_run_id>/final_manifest.json
runs/<promotion_run_id>/readout.md
```

## Authority Boundary

```text
official_profile_registry_write_allowed = true
official_market_state_allowed = false
official_dataset_registry_write_allowed = false
official_parquet_write_allowed = false
candidate_parquet_copy_allowed = false
production_builder_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
source_market_data_reads_allowed = false
```

If this promotion passes, the next possible gate is a separate official profile
artifact validation. Consumption policy, production builders and official table
materialization remain closed.
