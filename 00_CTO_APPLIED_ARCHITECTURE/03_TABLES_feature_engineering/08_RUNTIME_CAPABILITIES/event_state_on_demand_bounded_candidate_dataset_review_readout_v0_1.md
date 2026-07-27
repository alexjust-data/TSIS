# Event State On-Demand Bounded Candidate Dataset Review Readout v0.1

Status: `CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION`
Date: `2026-07-27`

```text
review_id = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T000000Z
reviewed_run = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z
reviewed_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
review_decision = approved_as_event_state_on_demand_bounded_candidate_evidence_with_restrictions
requested_contexts = 9
represented_contexts = 8
unavailable_contexts = 1
unaccounted_contexts = 0
event_state_candidate_records = 8
hard_review_failures = 0
candidate_dataset_review_approved = true
reuse_eligibility_after_review = pending_deterministic_rerun
official_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1
```

The candidate is accepted only as bounded Event State on-demand evidence. It is
not an official Event State dataset, not production, and not downstream
consumable. The review does not mutate the candidate registry entry and does
not authorize another materialization.
