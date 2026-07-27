# Market State On-Demand Incremental Overlap Candidate Dataset Review Readout v0.1

Status: `CLOSED_PASS_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION`
Date: `2026-07-25`

Reviewed incremental run:

```text
market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z
```

Reviewed candidate dataset:

```text
market_state_candidate_dataset_incremental_v0_1_f2cfd5cf55d0c1be
```

## Decision

```text
review_decision = APPROVED_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION
requested_contexts = 12
represented_contexts = 11
baseline_reused_rows = 8
delta_materialized_rows = 3
unavailable_contexts = 1
unaccounted_contexts = 0
hard_review_failures = 0
dataset_completeness = partial
candidate_dataset_validated = true
official_dataset = false
production = false
downstream = false
```

The candidate is accepted only as bounded incremental Market State on-demand
evidence. It is not an official physical dataset, not production and not
downstream-consumable.

## Scope Ledger

```text
requested_contexts = 12
reused_validated_from_baseline = 8
delta_materialized = 3
unavailable = 1
unaccounted = 0

12 = 8 + 3 + 1
11 represented = 8 baseline + 3 delta
```

The unavailable context remains explicit:

```text
instrument_id = figi_share_class:BBG001S5N8T1
ticker_label_non_authoritative = AAME
session_date = 2022-11-25
decision_timestamp_utc = 2022-11-25T14:30:00Z
reason = missing_exact_decision_timestamp_source_candidate_record
fallback_used = false
```

## Evidence Reviewed

```text
request_fingerprint = 884830b081a2e9b8e5ea5130262600a20b01385a019a66ce3ad2240aac5b9b08
execution_plan_fingerprint = c9ee1a63f9dd8780f16193adf43d35bb8db2271778a64afae2132e052931e746
resolved_profile_fingerprint = bf2b6ff3eb7e4d09a0ee55a7acec214c19f4a3a05111bb9916b19ef930ce4ac7
resolved_universe_fingerprint = 2d557ddc26ee65dfbf83671be02fa33324b2b4c40a11f3c1a43d5e8ec512012d
resolved_source_set_fingerprint = 3393e2eeaca1ce261e3e936fc35355c61cb664477ff79200ce5b99cf2ebddaaa
partition_coverage_resolution_fingerprint = 4befc05e6817394c4f4b28ff2c26c9cc971bd7b6a4a78917fb8cb1963236d285
candidate_dataset_fingerprint = f2cfd5cf55d0c1be1722693cc0216ffd425bbb869e19c17745976c030f2c7a2a
scientific_dataset_fingerprint = 7103e4fdbae205e4bccbeb0c436508f62b016107b4b2756c549073dae971bb5f
validation_result_fingerprint = 9aafd142203872647a8be3668d0aca7c4f95630be4a405e00fd64f5cd111f336
registry_entry_fingerprint = 9d39bfd88a752d99afc7709950a0ea8c1116d7a2c79daef8bd4c79a993637376
review_matrix_sha256 = 7d2ca11f7e429f35518f15aa0ab70cd54f2a60cb80e66a7a6520ca11eb6e13fc
```

## Review Findings

```text
request_scope_ledger = PASS
baseline_delta_contract_compatibility = PASS
canonical_identity_uniqueness = PASS
row_origin_lineage = PASS_WITH_RESTRICTION
baseline_immutability = PASS
fingerprint_separation = PASS_WITH_RESTRICTION
logical_order_independence = PASS
restriction_propagation = PASS
validation_result_consistency = PASS
promotion_and_consumption_boundary = PASS
```

Important restriction: the reviewed combined candidate is a governed logical
composition of baseline rows plus delta rows. The delta parquet contains only
the three newly materialized rows; the baseline rows are referenced, not
rewritten.

## Boundary

```text
registry_entry_mutations = 0
baseline_registry_entry_mutations = 0
new_materialization = false
reuse_eligibility_transition = false
official_market_state_dataset = false
production = false
downstream_consumption = false
```

## Next Gate

```text
market_state_on_demand_incremental_overlap_idempotency_reuse_test_authorization_v0_1
```
