# Market State Bounded On-Demand Determinism Validation Readout v0.1

Status: `CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION`
Date: `2026-07-25`

Reviewed baseline:

```text
market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
```

Reviewed successful deterministic rerun:

```text
market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z
```

## Decision

```text
determinism_validation_decision = APPROVED_AS_BOUNDED_DETERMINISM_EVIDENCE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION
scientific_determinism = PROVEN_FOR_BOUNDED_SCOPE
requested_contexts = 9
materialized_candidate_rows = 8
unavailable_contexts = 1
comparison_blocking_failures = 0
runtime_only_differences = 2
reuse_transition_ready = true
reuse_eligibility_after_validation = pending_idempotency_reuse_test
reuse_eligibility_changed_by_this_gate = false
official_dataset = false
production = false
downstream = false
```

The successful rerun rebuilt the bounded candidate output from the same
governed request and authorities. It reproduced the same normalized scientific
Market State result: identical normalized execution-plan semantics, identical
scientific dataset fingerprint, identical 8 row identities, identical 8
`state_output_fingerprint` values and the same unavailable context.

## Runtime Differences

```text
physical_execution_plan_fingerprint_match = false
physical_candidate_dataset_fingerprint_match = false
```

These are accepted runtime-only differences because the rerun has a different
run id, output path and physical run-local metadata. They are not scientific
content differences.

The prior blocked attempt is retained:

```text
blocked_prior_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z
reason = comparison_normalization_too_strict_not_content_mismatch
```

## Boundary

```text
new_request_created = false
rerun_execution_by_this_gate = false
source_rows_read = false
materializer_execution = false
candidate_parquet_written = false
candidate_registry_entry_written = false
reuse_eligibility_upgrade = false
official_market_state_dataset = false
official_parquet = false
production = false
downstream_consumption = false
```

## Next Gate

```text
market_state_bounded_on_demand_idempotency_reuse_test_authorization_v0_1
```
