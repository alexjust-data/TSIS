# Event State On-Demand Bounded Incremental Overlap Candidate Dataset Review Readout v0.1

Status: `CLOSED_PASS_EVENT_STATE_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION`
Date: `2026-07-28`

```text
review_id = event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1_20260728T000000Z
review_run_id = event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1_20260728T091026Z
reviewed_run = event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z
reviewed_candidate_dataset_id = event_state_incremental_overlap_candidate_dataset_v0_1_f88cc0a0a39117f3
review_decision = approved_as_event_state_incremental_overlap_candidate_evidence_with_restrictions
requested_contexts = 12
represented_contexts = 11
reused_validated_event_state_contexts = 8
delta_materialized_event_state_contexts = 3
unavailable_contexts = 1
unaccounted_contexts = 0
combined_event_state_records = 11
hard_review_failures = 0
candidate_dataset_review_approved = true
reuse_eligibility_after_review = pending_incremental_overlap_idempotency_reuse_test
official_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_authorization_v0_1
```

The incremental candidate is accepted only as bounded Event State on-demand
candidate evidence. It is not an official Event State dataset, not production,
and not downstream consumable. The review does not mutate the baseline or
combined registry entries and does not authorize another materialization.
