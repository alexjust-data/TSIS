# Market State On-Demand Incremental Overlap Idempotency Reuse Test Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`

This document authorizes exactly one idempotency/reuse test for the validated
partially overlapping Market State on-demand request. The authorized test must
submit the same normalized overlap request with a reuse policy and prove that
TSIS returns the existing governed combined candidate without rebuilding
baseline evidence, delta evidence or creating a new dataset identity.

Parent review:

```text
review_gate = market_state_on_demand_incremental_overlap_candidate_dataset_review_v0_1
review_id = market_state_on_demand_incremental_overlap_candidate_dataset_review_v0_1_20260725T000000Z
review_status = CLOSED_PASS_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION
review_matrix_sha256 = 7d2ca11f7e429f35518f15aa0ab70cd54f2a60cb80e66a7a6520ca11eb6e13fc
```

Baseline candidate dataset:

```text
baseline_run_id = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
baseline_candidate_dataset_id = market_state_candidate_dataset_v0_1_433288b634924676
baseline_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
baseline_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
baseline_artifact_availability = available
```

Incremental combined candidate:

```text
incremental_run_id = market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z
combined_candidate_dataset_id = market_state_candidate_dataset_incremental_v0_1_f2cfd5cf55d0c1be
combined_candidate_dataset_fingerprint = f2cfd5cf55d0c1be1722693cc0216ffd425bbb869e19c17745976c030f2c7a2a
combined_scientific_dataset_fingerprint = 7103e4fdbae205e4bccbeb0c436508f62b016107b4b2756c549073dae971bb5f
combined_context_ledger_sha256 = 9e117ea5a82bbeeba0e36f24e13d2db124c260aabac1a5bc088a61cdcdb8a9b1
fingerprint_comparison_sha256 = e8f30356dcf648343cc9e6097fe5b9231a62b86580757022e5f1d3f459a8271d
requested_contexts = 12
represented_contexts = 11
unavailable_contexts = 1
```

## Authorized Test Policy

```text
reuse_policy = reuse_if_exact_validated_overlap_match
same_normalized_overlap_request_required = true
selected_dataset_id_must_equal = market_state_candidate_dataset_incremental_v0_1_f2cfd5cf55d0c1be
selected_scientific_dataset_fingerprint_must_equal = 7103e4fdbae205e4bccbeb0c436508f62b016107b4b2756c549073dae971bb5f
materializer_executions_expected = 0
delta_materializer_executions_expected = 0
source_market_data_rows_read_expected = 0
source_candidate_records_read_expected = 0
new_candidate_parquet_files_expected = 0
new_candidate_dataset_registry_entries_expected = 0
baseline_registry_entry_mutations_expected = 0
combined_candidate_registry_entry_mutations_expected = 0
```

The future test may read governed registry metadata, request/plan records,
manifests, the combined context ledger and fingerprint comparison evidence. It
must not read source market data, rebuild Market State, rebuild the delta, write
new candidate parquet files or register a second scientific dataset identity.

## Required Pre-Reuse Checks

```text
baseline dataset fingerprint unchanged
baseline validation still valid
baseline reuse eligibility still active
baseline physical evidence available
delta dataset fingerprint unchanged
delta validation still valid
delta output available
same context ledger
same composition policy
same schema compatibility
same lineage policy
same restriction propagation
artifact availability = available
```

## Closed Boundaries

```text
idempotency_reuse_test_execution = false
new_market_state_request_execution = false
source_rows_read = false
materializer_execution = false
delta_materializer_execution = false
candidate_parquet_write = false
candidate_dataset_registry_entry_write = false
official_dataset_promotion = false
incremental_capability_promotion = false
unbounded_reuse = false
production = false
downstream_consumption = false
registry_reuse_eligibility_mutation_by_authorization = false
```

## Contract

```text
contract = market_state_on_demand_incremental_overlap_idempotency_reuse_test_contract_v0_1.json
contract_content_sha256_excluding_hash_field = 00108c6c9ad5114c731357c29f5239199ecea91c07c3bbde95d9521c2c7a3cf5
```

## Next Gate

```text
market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1
```
