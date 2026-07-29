# Event State On-Demand Bounded Incremental Overlap Execution Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-28`

```text
gate = event_state_on_demand_bounded_incremental_overlap_execution_authorization_v0_1
parent_gate = event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1
authorized_next_gate = event_state_on_demand_bounded_incremental_overlap_execution_v0_1
baseline_event_state_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
baseline_reuse_eligibility = eligible_for_bounded_event_state_exact_match_reuse
expected_requested_contexts = 12
expected_reusable_event_state_contexts = 8
expected_delta_event_state_contexts_to_build = 3
expected_unavailable_contexts = 1
expected_combined_represented_contexts = 11
scope_sha256 = 3b4dddda10614bd7b88186d19666aaa63ddf11e6bfde393079b7c5de84466813
```

The authorization is bounded to one partially overlapping request for
`event_type:market_data:session_opened`, XNYS, the same three instrument
projections and one additional session (`2024-03-11`). It authorizes only the
future execution gate. This authorization was consumed by accepted run
`event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z`, which created candidate runtime evidence only.

Consumed by:

```text
event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z
```

Next gate:

```text
event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1
```
