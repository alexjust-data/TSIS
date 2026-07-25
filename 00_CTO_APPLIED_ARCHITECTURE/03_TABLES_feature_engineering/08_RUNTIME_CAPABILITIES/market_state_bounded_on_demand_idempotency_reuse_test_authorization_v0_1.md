# Market State Bounded On-Demand Idempotency Reuse Test Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REUSE_TEST`
Date: `2026-07-25`

This document authorizes exactly one bounded idempotency/reuse test for the
first Market State on-demand candidate dataset. The authorized test must submit
the same normalized Market State request with a reuse policy and prove that TSIS
returns the existing governed candidate dataset without rebuilding it.

Baseline candidate dataset:

```text
baseline_run_id = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
baseline_candidate_dataset_id = market_state_candidate_dataset_v0_1_433288b634924676
baseline_request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
baseline_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
```

Accepted determinism evidence:

```text
determinism_validation_id = market_state_bounded_on_demand_determinism_validation_v0_1_20260725T000000Z
determinism_validation_status = CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION
scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb
reuse_transition_ready = true
reuse_eligibility_after_validation = pending_idempotency_reuse_test
```

## Authorized Test Policy

```text
reuse_policy = reuse_if_exact_validated_match
same_normalized_request_required = true
selected_dataset_id_must_equal = market_state_candidate_dataset_v0_1_433288b634924676
materializer_executions_expected = 0
source_market_data_rows_read_expected = 0
source_candidate_records_read_expected = 0
new_candidate_parquet_files_expected = 0
new_candidate_dataset_registry_entries_expected = 0
```

The test may read governed request, plan, manifest, validation and candidate
registry metadata. It must not read source market data or rebuild Market State.

## Closed Boundaries

```text
idempotency_reuse_test_execution = CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS
accepted_run = market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z
consumed_at_utc = 2026-07-25T06:03:18Z
new_request_execution = false
source_rows_read = 0
materializer_executions = 0
candidate_parquet_written = 0
candidate_dataset_registry_entries_written = 0
reuse_eligibility_mutation_by_authorization = false
official_dataset = false
production = false
downstream = false
```

## Contract

```text
contract = market_state_bounded_on_demand_idempotency_reuse_test_contract_v0_1.json
contract_content_sha256_excluding_hash_field = c836f3ae2d5821a0d2d7b66ee1c2db1c1866fe83b36a2d1fbb27f31bf678b98d
```

## Next Gate

```text
market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z
```

Next institutional gate:

```text
market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1
```
