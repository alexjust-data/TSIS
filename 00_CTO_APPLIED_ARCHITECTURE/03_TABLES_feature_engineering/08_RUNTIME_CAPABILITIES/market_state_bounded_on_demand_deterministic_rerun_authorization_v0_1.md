# Market State Bounded On-Demand Deterministic Rerun Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_RERUN`
Date: `2026-07-25`

This document authorizes exactly one deterministic rerun gate for the first
bounded Market State on-demand candidate dataset. The rerun must rebuild the
bounded candidate output from the same governed request, authorities, source
fingerprints, builder and validator versions. It must not reuse the existing
candidate parquet as a cache hit.

Baseline run:

```text
baseline_run_id = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
baseline_candidate_dataset_id = market_state_candidate_dataset_v0_1_433288b634924676
baseline_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
baseline_validation_result_fingerprint = 38064d86af50c4a2df2ec0d2561b25390421df7acad4679e957faceaf1791fdb
baseline_registry_entry_fingerprint = 82d551c8f8da00bbb3d8f1cb69bc5952fb9dc25fe3e1560bb497d686ffc2611c
```

Baseline approved review:

```text
review_gate = market_state_bounded_on_demand_candidate_dataset_review_v0_1
review_id = market_state_bounded_on_demand_candidate_dataset_review_v0_1_20260725T000000Z
review_status = CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION
```

## Frozen Baseline Fingerprints

```text
request_fingerprint = 584d07a1874ceceab077101bbc2de0ec37236db1a1a284956a81cb76674145ec
execution_plan_fingerprint = 5555fed758d30b6c8f281517eb747523d3dfaf9bbae1713b4e9f1c28c6fdd733
resolved_profile_fingerprint = bf2b6ff3eb7e4d09a0ee55a7acec214c19f4a3a05111bb9916b19ef930ce4ac7
resolved_universe_fingerprint = 81c2bf5791dd5f05b6a4c112fbda0ca94fde5509c2808820e0bd5882c864d958
resolved_source_set_fingerprint = 3393e2eeaca1ce261e3e936fc35355c61cb664477ff79200ce5b99cf2ebddaaa
partition_coverage_resolution_fingerprint = 3bc8d806de76ff062949d3d4cba6630d005159a619a25f566c825f86fe778b51
candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b
validation_result_fingerprint = 38064d86af50c4a2df2ec0d2561b25390421df7acad4679e957faceaf1791fdb
```

## Frozen Baseline Content

```text
baseline_candidate_rows = 8
baseline_unavailable_contexts = 1
baseline_state_ids = 8
baseline_state_output_fingerprints = 8
```

The rerun must reproduce the same normalized scientific/content result. Runtime
identity may differ only for run-local metadata such as run id, timestamps,
heartbeat timestamps and physical output folder.

## Rerun Policy

```text
reuse_policy = force_rebuild_for_determinism_test
reuse_existing_candidate_parquet = false
return_registry_match_without_materializer = false
skip_materializer = false
fresh_materializer_execution_required = true
```

## Required Comparison Artifact

```text
market_state_deterministic_rerun_comparison_v0_1.json
```

The comparison must evaluate request, plan, profile, universe, source,
partition/coverage, schema, row identities, state output fingerprints,
unavailable context preservation, lineage semantics and validation status.

## Authorization-Issue Boundaries

```text
deterministic_rerun_execution_at_authorization_issue = NOT_EXECUTED
new_requests_created = 0
source_rows_read = 0
materializer_executions = 0
candidate_files_written = 0
determinism_comparisons_created = 0
reuse_eligibility_changes = 0
official_dataset = false
production = false
downstream = false
```


## Consumption Record

```text
consumed_by_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z
consumed_status = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS
blocked_prior_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z
comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb
scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
reuse_eligibility_changes = 0
official_dataset = false
production = false
downstream = false
```

## Next Gate

```text
market_state_bounded_on_demand_determinism_validation_v0_1
```
