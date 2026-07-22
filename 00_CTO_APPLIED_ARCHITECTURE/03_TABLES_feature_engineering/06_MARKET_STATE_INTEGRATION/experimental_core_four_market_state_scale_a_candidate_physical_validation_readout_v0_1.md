# Experimental Core Four Market State Scale A Candidate Physical Validation Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-22`
Run: `experimental_core_four_market_state_scale_a_candidate_physical_validation_v0_1_20260722T204600Z`
Source Materialization Run: `experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z`
Source Integration Run: `experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z`
Logical Profile: `core_four_market_state_profile_v0_1`
Physical Schema: `core_four_market_state_candidate_physical_schema_v0_1`

This readout records the independent physical validation of the bounded Scale A candidate parquet artifact. The validation did not rewrite parquet, did not reread market source data and did not promote the candidate artifact.

It closes only the physical acceptance review for the 52-row Scale A candidate artifact. It does not authorize official Market State, production builders, downstream State consumption, full-history/full-universe execution, Scale B, Scale C or dataset promotion.

## 1. Inputs

```text
scope = configs/experimental_core_four_market_state_scale_a_candidate_materialization_scope_v0_1.json
validation_script = scripts/core_four_market_state_candidate_physical_validation.py
source_candidate_records = runs/experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z/market_state_candidate_records.jsonl
candidate_parquet = runs/experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z/core_four_market_state_scale_a_candidate_v0_1.parquet
source_materialization_manifest = runs/experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z/materialization_manifest.json
source_materialization_final_manifest = runs/experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z/final_manifest.json
rejected_context_report = runs/experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z/rejected_context_report.csv
```

The source JSONL remained the only source of expected row values. The parquet was read only for physical validation.

## 2. Result

```text
experimental_core_four_market_state_scale_a_candidate_physical_validation = PASS_WITH_RESTRICTIONS
overall_status = passed_core_four_market_state_candidate_physical_validation_with_restrictions
input_candidate_records = 52
output_physical_rows = 52
candidate_parquet_files = 1
candidate_parquet_bytes = 66399
physical_column_count = 40
physical_value_column_count = 17
hard_validation_failures = 0
```

## 3. Artifact And Schema Validation

```text
parquet_exists = true
parquet_sha256_matches_manifest = true
parquet_bytes_match_manifest = true
schema_match = true
column_order_exact = true
timestamp_timezone_utc = true
duplicate_primary_keys = 0
duplicate_source_candidate_record_ids = 0
duplicate_materialized_state_candidate_ids = 0
rejected_contexts_in_parquet = 0
```

## 4. Value Reconciliation

```text
value_mappings_checked = 884
expected_value_mappings = 884
source_to_physical_value_mismatches = 0
missing_source_value_fields = 0
extra_source_value_fields = 0
rvol_rename_checks = 52
rvol_rename_mismatches = 0
rvol_rename_passed = true
```

The review explicitly checked all `52 x 17` source-to-physical value mappings, including:

```text
trading_activity__daily_rvol_20d
  -> trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
```

## 5. Lineage, Restrictions And Fingerprints

```text
source_lineage_content_mismatches = 0
policy_version_mismatches = 0
formula_version_mismatches = 0
restriction_mismatches = 0
context_fingerprint_mismatches = 0
state_output_fingerprint_matches = 52
state_output_fingerprint_mismatches = 0
materialized_state_candidate_id_matches = 52
materialized_state_candidate_id_mismatches = 0
```

## 6. Roundtrip And Rebuild

```text
roundtrip_rows_checked = 52
roundtrip_row_mismatches = 0
roundtrip_field_mismatches = 0
semantic_rebuild_compare_field_count = 37
semantic_rebuild_field_comparisons = 1924
semantic_rebuild_differences = 0
byte_identical_parquet_rebuild_required = false
```

## 7. Authority Boundary

```text
source_market_data_rows_read = 0
source_market_data_read_verification = verified_by_static_input_boundary_not_os_filesystem_audit
authority_failures = 0
candidate_rows_are_canonical_market_state = false
candidate_rows_are_downstream_consumable = false
official_market_state_allowed = false
production_builder_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
```

## 8. Next Work

Scale A is closed through independent candidate physical validation. The next technical work should be a separately authorized design/review step, most likely `governed_exchange_session_calendar_design`, before any Scale B authorization or calendar-aware execution.
