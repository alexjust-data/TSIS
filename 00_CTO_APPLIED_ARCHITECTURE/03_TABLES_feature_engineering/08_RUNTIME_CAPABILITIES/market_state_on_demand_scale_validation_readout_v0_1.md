# Market State On-Demand Scale Validation Readout v0.1

Status: `CLOSED_PASS_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED`
Date: `2026-07-27`

```text
run_id = market_state_on_demand_scale_validation_v0_1_20260727T133641Z
requested_contexts = 120
represented_contexts = 104
reusable_validated_contexts = 14
scale_delta_materialized_contexts = 90
unavailable_contexts = 16
unaccounted_contexts = 0
source_candidate_records_read = 104
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_registry_entries_written = 1
hard_validation_failures = 0
candidate_dataset_fingerprint = 516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
scientific_dataset_fingerprint = 0cc901750cabe9fef67a2ee3ebcd6a30c4a807a7b35cda8d29dbd8baa9ddad6e
official_dataset = false
production = false
downstream = false
next_allowed_gate = market_state_on_demand_capability_promotion_review_v0_1
```

The scale validation remains bounded to Scale C runtime evidence. It proves a
larger controlled request can reuse validated lineage-chain contexts and build
only the remaining scale delta. It does not promote an official dataset and does
not authorize downstream use.
