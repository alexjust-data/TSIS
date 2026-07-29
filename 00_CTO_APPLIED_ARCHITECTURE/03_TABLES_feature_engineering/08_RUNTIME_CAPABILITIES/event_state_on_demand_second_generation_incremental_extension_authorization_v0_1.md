# Event State On-Demand Second-Generation Incremental Extension Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-28`

This document authorized exactly one bounded Event State second-generation
incremental extension. The authorization has been consumed by the accepted run
listed below.

```text
parent_gate = event_state_on_demand_bounded_incremental_overlap_idempotency_reuse_test_v0_1
authorized_next_gate = event_state_on_demand_second_generation_incremental_extension_v0_1
parent_generation_1_candidate_dataset_id = event_state_incremental_overlap_candidate_dataset_v0_1_f88cc0a0a39117f3
parent_generation_1_candidate_dataset_fingerprint = f88cc0a0a39117f315baf4312dc13533baae8b8574c6966ca91582ca98406c4f
parent_generation_1_logical_event_state_dataset_fingerprint = 73b2f81b76697eb67b55faffecd36c8e77ecf926c1c1f9e56cf6ee0e0ecb10f6
parent_generation_1_reuse_evidence_fingerprint = 60965781a0bf42674c5521cb0e27f7643574ceb2e2bfbd46501da69be869507d
event_type_id = event_type:market_data:session_opened
subject_scope = exchange_session
exchange_scope = XNYS
prior_generation_sessions = 2021-01-19, 2021-03-15, 2022-11-25, 2024-03-11
delta_2_session = 2023-03-20
instrument_projection_count = 3
expected_requested_contexts = 15
expected_reused_prior_generation_event_state_contexts = 11
expected_delta_2_event_state_contexts_to_build = 3
expected_preserved_unavailable_contexts = 1
expected_combined_represented_contexts = 14
market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability
market_state_dependency_reuse_policy = reuse_existing_validated_candidate_or_block_unless_separate_dependency_generation_authorized
market_state_dependency_generation_authorized = false
authorized_scope_sha256_before_consumption = 3ecb9297d1f4446c594306954e022792c5fa85456b775cddb3aaaae32d2fb42a
consumed_scope_sha256 = d8a47b109c75213dca2823562fd80ee6ef636ac58f1106f2b2ab19dd8ccc33cc
contract_sha256 = 192dd6b45911df72d970c3c614d17b7e566804d4973a322c0afbc49b104415f2
```

The future execution must reuse the complete validated generation-1 Event State
candidate for already represented contexts, materialize only the `2023-03-20`
delta2 contexts, preserve the known unavailable context and emit one new
combined candidate identity only if all exact-one bindings remain governed.

The Market State dependency for delta2 is restricted to the governed runtime
capability. The future run may use only exact fingerprint-matched validated
candidate evidence for the three delta2 Market State dependency contexts. It may
not rematerialize Market State or read source market data under this gate.

Closed by this authorization gate before consumption:

```text
second_generation_incremental_execution = false
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

## Required Future Reconciliation

```text
requested_contexts = reused_prior_generation_event_state_contexts + delta_2_materialized_event_state_contexts + unavailable_contexts + blocked_contexts + quarantined_contexts
represented_contexts = reused_prior_generation_event_state_contexts + delta_2_materialized_event_state_contexts
unaccounted_contexts = 0
duplicate_canonical_contexts = 0
unexpected_parent_mutations = 0
```

## Consumed By

```text
run_id = event_state_on_demand_second_generation_incremental_extension_v0_1_20260728T103016Z
run_status = CLOSED_PASS_EVENT_STATE_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED
requested_contexts = 15
represented_contexts = 14
reused_prior_generation_event_state_contexts = 11
delta_2_materialized_event_state_contexts = 3
unavailable_contexts = 1
hard_validation_failures = 0
candidate_dataset_fingerprint = 9a31d9b8bf3af01c1c4a5cd18a37309eec7b3cb41011501ab85e0ef4a4831746
logical_event_state_dataset_fingerprint = b4774100b8ab27794e8d9a9205227c6e694442e8287b92bf5d899ec3a0b66f33
registry_entry_fingerprint = 5b8e4c39ff330aba4a335709e0fd2beb5bc3f72e715f32c8040b9355a75cf458
official_event_state_dataset = false
production = false
downstream = false
```

## Next Gate

```text
event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1
```
