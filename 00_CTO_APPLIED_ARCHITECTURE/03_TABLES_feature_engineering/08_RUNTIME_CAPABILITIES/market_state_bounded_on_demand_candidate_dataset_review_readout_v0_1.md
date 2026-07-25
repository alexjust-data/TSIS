# Market State Bounded On-Demand Candidate Dataset Review Readout v0.1

Status: `CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION`
Date: `2026-07-25`

Reviewed execution run:

```text
market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
```

Reviewed candidate dataset:

```text
market_state_candidate_dataset_v0_1_433288b634924676
```

## Decision

```text
review_decision = APPROVED_AS_BOUNDED_CANDIDATE_DATASET_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION
candidate_records_reviewed = 8
requested_contexts = 9
unavailable_contexts = 1
candidate_parquet_files_reviewed = 1
candidate_registry_entries_reviewed = 1
review_failures = 0
hard_review_failures = 0
reuse_eligibility_after_review = pending_determinism_validation
```

The reviewed output is suitable only as bounded candidate Market State
on-demand evidence. It is not an official Market State dataset, not a reusable
cache entry yet, not production and not downstream-consumable.

## Scope Reconciliation

```text
requested_contexts = 9
materialized_candidate_rows = 8
unavailable_contexts = 1

9 = 8 + 1
```

The unavailable context remains explicit and was not emitted as a partial row:

```text
instrument_id = figi_share_class:BBG001S5N8T1
ticker_label_non_authoritative = AAME
session_date = 2022-11-25
decision_timestamp_utc = 2022-11-25T14:30:00Z
reason = missing_exact_decision_timestamp_source_candidate_record
available_same_instrument_session_timestamp = 2022-11-25T16:58:00Z
fallback_used = false
```

## Evidence Reviewed

```text
request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
execution_plan_fingerprint = 5555fed758d30b6c8f281517eb747523d3dfaf9bbae1713b4e9f1c28c6fdd733
resolved_universe_fingerprint = 81c2bf5791dd5f05b6a4c112fbda0ca94fde5509c2808820e0bd5882c864d958
resolved_source_set_fingerprint = 3393e2eeaca1ce261e3e936fc35355c61cb664477ff79200ce5b99cf2ebddaaa
partition_coverage_resolution_fingerprint = 3bc8d806de76ff062949d3d4cba6630d005159a619a25f566c825f86fe778b51
candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
validation_result_fingerprint = 38064d86af50c4a2df2ec0d2561b25390421df7acad4679e957faceaf1791fdb
registry_entry_fingerprint = 82d551c8f8da00bbb3d8f1cb69bc5952fb9dc25fe3e1560bb497d686ffc2611c
```

## Review Findings

```text
scope_accounting = PASS
unavailable_context_preservation = PASS_WITH_RESTRICTION
request_output_scope = PASS_WITH_RESTRICTION
grain_and_identity = PASS
temporal_legality_evidence = PASS
lineage_completeness = PASS_WITH_RESTRICTION
registry_entry_consistency = PASS
validation_result_consistency = PASS
reuse_boundary = PASS_WITH_RESTRICTION
promotion_and_consumption_boundary = PASS
```

Important restriction: the candidate parquet does not contain an `exchange_id`
column. The XNYS scope is proven by the frozen request, resolved universe and
Execution Plan lineage, not by a row-level physical exchange field.

## Boundary

```text
candidate_dataset_accepted_as_evidence = true
reuse_eligibility = pending_determinism_validation
official_market_state_dataset = false
official_parquet = false
production = false
downstream_consumption = false
new_materialization = false
```

## Next Gate

```text
market_state_bounded_on_demand_deterministic_rerun_authorization_v0_1
```
