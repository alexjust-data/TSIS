# Event State On-Demand Bounded Idempotency Reuse Test Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REUSE_TEST`
Date: `2026-07-28`

This document authorized exactly one bounded idempotency/reuse test for the
first Event State on-demand candidate dataset. The authorized test submitted
the same normalized Event State request with a reuse policy and proved that
TSIS can return the existing governed Event State candidate dataset without
rebuilding Event State.

Baseline candidate dataset:

```text
baseline_run_id = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z
baseline_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
baseline_event_state_request_fingerprint = f82e424b60a69e2e9edec00e3dcf456c2042d18b334366dab76622286fac6ade
baseline_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33
baseline_normalized_logical_dataset_fingerprint = e2c47083b8dd560e67bcda32b0063cf9f468754e34f76b82e9f839046d375699
```

Accepted determinism evidence:

```text
determinism_validation_id = event_state_on_demand_bounded_determinism_validation_v0_1_20260728T000000Z
determinism_validation_status = CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION
determinism_status = PROVEN_FOR_BOUNDED_SCOPE
comparison_fingerprint = 9580cc5f747ef6c6fd3ec2b3c92460a7ce0eba6e9164248e636ab241dcf55c55
reuse_transition_ready = true
reuse_eligibility_after_validation = pending_idempotency_reuse_test
```

## Authorized Test Policy

```text
reuse_policy = reuse_if_exact_validated_event_state_match
same_normalized_request_required = true
selected_dataset_id_must_equal = event_state_candidate_dataset_v0_1_d5662103e1c45f90
selected_normalized_logical_dataset_fingerprint_must_equal = e2c47083b8dd560e67bcda32b0063cf9f468754e34f76b82e9f839046d375699
event_state_materializer_executions_expected = 0
market_state_materializer_executions_expected = 0
event_instances_created_expected = 0
event_window_bindings_created_expected = 0
instrument_session_projections_created_expected = 0
event_state_candidate_records_read_expected = 0
market_state_candidate_records_read_expected = 0
source_market_data_rows_read_expected = 0
new_candidate_dataset_registry_entries_expected = 0
```

The test was allowed to read governed request, plan, manifest, validation,
determinism and candidate registry metadata. It was not allowed to read source
market data, read Market State candidate content, read Event State candidate
record content, rebuild Event State, rematerialize Market State or create a new
candidate dataset identity.

## Consumed Test Result

```text
consumed_by_run_id = event_state_on_demand_bounded_idempotency_reuse_test_v0_1_20260728T074624Z
consumed_at_utc = 2026-07-28T07:46:24Z
closure_status = CLOSED_PASS_EVENT_STATE_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS
idempotency_status = PROVEN_FOR_BOUNDED_EVENT_STATE_EXACT_MATCH_REUSE
selected_candidate_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90
selected_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33
selected_normalized_logical_dataset_fingerprint = e2c47083b8dd560e67bcda32b0063cf9f468754e34f76b82e9f839046d375699
market_state_dependency_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
report_fingerprint = e52e92da85feb259a93616d9fd8340d0b874d563355b9b3373ca7d61710a358d
evidence_entry_fingerprint = 237f359d69fbc78fb1b00557a5096584ef1d32d8c4a11227f7190684eb4f312e
blocking_failures = 0
```

Observed counters:

```text
candidate_registry_metadata_reads = 1
event_state_candidate_files_read = 0
event_state_candidate_records_read = 0
market_state_candidate_files_read = 0
market_state_candidate_records_read = 0
source_market_data_rows_read = 0
event_state_materializer_executions = 0
market_state_materializer_executions = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_session_projections_created = 0
new_event_state_candidate_files = 0
new_candidate_dataset_registry_entries = 0
idempotency_reuse_evidence_entries_written = 1
reuse_eligibility_after_test = pending_reuse_eligibility_transition_review
reuse_eligibility_changes = 0
official_event_state_dataset = false
production = false
downstream = false
```

Invalid technical attempt preserved:

```text
failed_run_id = event_state_on_demand_bounded_idempotency_reuse_test_v0_1_20260728T074430Z
failure_status = FAILED_TECHNICAL_RUNNER_REQUEST_FIELD_BUG_BEFORE_FINAL_MANIFEST
valid_gate_closure = false
```

## Boundaries Remaining Closed

```text
new_event_state_request_execution = false
event_state_materializer_execution = false
market_state_materializer_execution = false
event_state_candidate_records_read = false
market_state_candidate_files_read = false
source_market_data_rows_read = false
candidate_dataset_registry_entry_write = false
reuse_eligibility_mutation_by_authorization = false
official_event_state_dataset = false
production = false
downstream = false
```

## Contract

```text
contract = event_state_on_demand_bounded_idempotency_reuse_test_contract_v0_1.json
contract_content_sha256_excluding_hash_field = 50ede549474d286c3e1e0f71ff270e3e2baadebd57f328cc9919a9c8b73ab4f6
```

## Next Gate

```text
event_state_on_demand_bounded_reuse_eligibility_transition_review_v0_1
```
