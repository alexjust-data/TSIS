# Official Market State Candidate Promotion Review Readout v0.1

run_id = `official_market_state_candidate_promotion_review_v0_1_20260723T192107Z`
script_version = `official_market_state_candidate_promotion_review_v0_1`

```text
official_market_state_candidate_promotion_review = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS
reviewed_profile_id = market_state_core_four_intraday_profile_v0_1
evidence_artifacts_checked = 8
resolution_records = 480
integrated_candidate_records = 104
physical_candidate_rows = 104
value_mappings_checked = 1768
semantic_rebuild_field_comparisons = 3848
hash_mismatches = 0
count_mismatches = 0
hard_validation_failures = 0
official_profile_promotion_executed = false
official_market_state_authorized = false
official_parquet_files_written = 0
source_market_data_rows_read = 0
next_allowed_gate = official_market_state_candidate_promotion_authorization_v0_1
```

The review approves the bounded core-four intraday profile candidate for a
separate promotion authorization only if the decision is
`APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS`. It does not promote
an official table, copy parquet, authorize production, authorize downstream
consumption or open full-history/full-universe execution.
