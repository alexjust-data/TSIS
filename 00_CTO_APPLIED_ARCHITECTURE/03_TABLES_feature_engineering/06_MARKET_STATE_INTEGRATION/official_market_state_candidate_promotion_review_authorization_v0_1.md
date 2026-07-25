# Official Market State Candidate Promotion Review Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `official_profile_candidate_review_only`

This authorization opens a review gate only. It does not authorize official table
promotion, parquet copying, production builders, downstream consumption or
full-history/full-universe execution.

## Reviewed Object

```text
profile_id = market_state_core_four_intraday_profile_v0_1
profile_classification = official_profile_candidate
profile_scope = bounded_validated_core_four_intraday_market_state_profile
complete_tsis_market_state = false
```

The reviewed object is not complete TSIS Market State. It is a bounded
core-four intraday profile candidate built from the admitted Information Objects
validated through Scale A, Scale B and Scale C.

## Authorized Review

```text
gate = official_market_state_candidate_promotion_review_v0_1
scope = configs/official_market_state_candidate_promotion_review_scope_v0_1.json
authorized_actions = evidence_inventory, restriction_classification, sufficiency_review, promotion_review_decision
authorized_decision_values = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS, BLOCKED_PENDING_EVIDENCE, REJECTED_FOR_OFFICIAL_PROFILE_PROMOTION
accepted_review_run = official_market_state_candidate_promotion_review_v0_1_20260723T192107Z
review_decision = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS
```

## Required Evidence

The review must consume evidence from the bounded proof chain, Scale A, Scale B
and Scale C. Scale C is the primary physical evidence for the review.

Required Scale C anchors:

```text
sample_preflight_run = experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z
execution_surface_run = experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z
builder_resolution_run = experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z
market_state_integration_run = experimental_core_four_market_state_scale_c_market_state_integration_execution_v0_1_20260723T184533Z
candidate_materialization_run = experimental_scale_c_ms_candidate_materialization_v0_1_20260723T184752Z
candidate_physical_validation_run = core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554
candidate_parquet_sha256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
resolution_records = 480
integrated_candidate_records = 104
physical_candidate_rows = 104
value_mappings_checked = 1768
hard_validation_failures = 0
```

## Blocking Criteria

The review must block promotion readiness if any of these are observed:

```text
schema_contract_mismatch
unresolved_source_to_physical_mismatch
fingerprint_mismatch
temporal_leakage
calendar_authority_mismatch
nondeterministic_semantic_rebuild
unclassified_breaking_change_in_common_materializer_or_validator
missing_accepted_run_artifact
unclear_canonical_grain_or_primary_key
```

## Non-Blocking Scope Restrictions

These restrictions describe the candidate profile scope and must be preserved,
but do not by themselves block a core-four official-profile promotion review:

```text
quote_dependent_objects_excluded = true
required_information_objects = 4
complete_tsis_market_state = false
full_history = false
full_universe = false
production = false
downstream_consumable = false
```

## Authority Boundary

```text
official_profile_promotion_allowed = false
official_market_state_allowed = false
official_parquet_write_allowed = false
candidate_parquet_copy_allowed = false
production_builder_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
source_market_data_reads_allowed = false
```

If the review approves the candidate, the only next gate is a separate
`official_market_state_candidate_promotion_authorization_v0_1`.
