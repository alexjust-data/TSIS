# Market State Bounded On-Demand Deterministic Rerun Authorization Readout v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RERUN`
Date: `2026-07-25`

```text
gate = market_state_bounded_on_demand_deterministic_rerun_authorization_v0_1
parent_gate = market_state_bounded_on_demand_candidate_dataset_review_v0_1
authorized_next_gate = market_state_bounded_on_demand_deterministic_rerun_v0_1
actual_next_gate_after_consumption = market_state_bounded_on_demand_determinism_validation_v0_1
baseline_run_id = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
baseline_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
baseline_candidate_rows = 8
baseline_unavailable_contexts = 1
authorized_rerun_requests_max = 1
authorized_rerun_runs_max = 1
reuse_existing_candidate_parquet = false
reuse_eligibility_changes = 0
deterministic_rerun_execution = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS
consumed_by_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z
blocked_prior_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z
comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb
scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
production = false
downstream = false
```

The authorization freezes the first approved bounded candidate dataset as the
baseline for deterministic comparison. The rerun must rebuild rather than reuse,
and must produce a normalized comparison artifact before any later idempotency
or reuse transition can be considered.

If baseline source hashes, profile hashes, builder identity or validator identity
cannot be reproduced exactly, the next gate must block rather than compare a
changed baseline.

## Required Match Set

```text
request_fingerprint
execution_plan_semantics_fingerprint
resolved_profile_fingerprint
resolved_universe_fingerprint
resolved_source_set_fingerprint
partition_coverage_resolution_fingerprint
scientific_dataset_fingerprint
state_id_set
state_output_fingerprint_set
unavailable_context_set
validation_status
```

Physical execution-plan and candidate-dataset fingerprints may differ when the difference is limited to run-local paths, run id or other declared runtime metadata.

## Next Allowed Gate

```text
market_state_bounded_on_demand_determinism_validation_v0_1
```
