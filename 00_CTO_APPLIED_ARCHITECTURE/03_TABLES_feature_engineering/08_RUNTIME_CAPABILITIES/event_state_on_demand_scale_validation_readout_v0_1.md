# Event State On-Demand Scale Validation Readout v0.1

Status: `CLOSED_PASS_EVENT_STATE_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED`
Date: `2026-07-28`

```text
run_id = event_state_on_demand_scale_validation_v0_1_20260728T120123Z
requested_contexts = 80
represented_contexts = 74
reused_lineage_chain_contexts = 14
scale_delta_materialized_contexts = 60
unavailable_contexts = 6
unaccounted_contexts = 0
combined_event_state_records = 74
event_state_materializer_executions = 1
market_state_materializer_executions = 0
market_state_candidate_records_read = 104
source_market_data_rows_read = 0
candidate_dataset_registry_entries_written = 1
hard_validation_failures = 0
candidate_dataset_fingerprint = 363f9188c6cce6d41e3a414831bdc8d57b59e2b4b4a934b827acfab11a99b907
logical_event_state_dataset_fingerprint = 04f2ffb5b4a4b6865529aaecc189b0b22c7e76976dc8344b714e08f9f5649e64
validation_result_fingerprint = 8cd71a709ca1ca37f958a8b12ee551f87e7c53f754860159a8097a27ea48acb8
official_event_state_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_on_demand_capability_promotion_review_v0_1
```

The scale validation remains candidate/runtime evidence. It proves Event State
on-demand can scale beyond the incremental chain while reusing validated Event
State evidence, materializing only new at-anchor delta records and resolving
Market State exclusively through the promoted runtime capability.
