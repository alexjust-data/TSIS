# Event State On-Demand Bounded Incremental Overlap Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-28`

This document authorizes exactly one future bounded Event State incremental
overlap execution. The authorized execution must reuse the bounded exact-match
eligible Event State candidate evidence for the already represented contexts
and build only the small delta for one additional XNYS session.

It did not itself execute the incremental run. The subsequent run consumed this authorization and did not authorize official Event
State dataset promotion, production use, downstream consumption, unbounded
reuse or generalized Event State on-demand materialization.

```text
parent_gate = event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1
authorized_next_gate = event_state_on_demand_bounded_incremental_overlap_execution_v0_1
baseline_event_state_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
baseline_reuse_eligibility = eligible_for_bounded_event_state_exact_match_reuse
event_type_id = event_type:market_data:session_opened
subject_scope = exchange_session
exchange_scope = XNYS
base_sessions = 2021-01-19, 2021-03-15, 2022-11-25
delta_sessions = 2024-03-11
instrument_projection_count = 3
expected_requested_contexts = 12
expected_reusable_event_state_contexts = 8
expected_delta_event_state_contexts_to_build = 3
expected_unavailable_contexts = 1
expected_combined_represented_contexts = 11
market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability
market_state_dependency_reuse_policy = reuse_existing_validated_candidate_or_block_unless_separate_dependency_generation_authorized
scope_sha256 = 3b4dddda10614bd7b88186d19666aaa63ddf11e6bfde393079b7c5de84466813
```

Authorized limits for the future execution:

```text
maximum_incremental_execution_runs = 1
maximum_requested_event_state_contexts = 12
maximum_reusable_event_state_contexts = 8
maximum_delta_event_state_candidate_records = 3
maximum_unavailable_contexts = 1
maximum_new_candidate_dataset_registry_entries = 1
baseline_registry_entry_mutations = 0
official_event_state_dataset = false
production = false
downstream = false
```

The future run must preserve exact-one binding over Event Instance, Event
Window, Instrument Projection, Market State dependency, state_role and
consumption_legality. Any ambiguity, missing dependency or unauthorized Market
State dependency must block the affected context instead of using fallbacks.

## Closed In This Authorization Gate

```text
incremental_overlap_execution = false
event_state_materializer_execution = false
market_state_materializer_execution = false
event_state_candidate_records_read = false
market_state_candidate_records_read = false
source_market_data_rows_read = false
candidate_dataset_registry_entry_write = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
unbounded_reuse = false
```

## Consumed By

```text
consumed_by_run_id = event_state_on_demand_bounded_incremental_overlap_execution_v0_1_20260728T084733Z
consumed_at_utc = 2026-07-28T08:47:33Z
```

## Next Gate

```text
event_state_on_demand_bounded_incremental_overlap_candidate_dataset_review_v0_1
```
