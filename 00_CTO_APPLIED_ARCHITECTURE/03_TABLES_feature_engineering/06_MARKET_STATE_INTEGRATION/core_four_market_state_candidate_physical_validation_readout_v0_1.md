# Core Four Market State Candidate Physical Validation Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-22`
Run: `core_four_market_state_candidate_physical_validation_v0_1_20260722T093828Z`
Source Materialization Run: `experimental_core_four_market_state_materialization_v0_1_20260722T081155Z`
Logical Profile: `core_four_market_state_profile_v0_1`
Physical Schema: `core_four_market_state_candidate_physical_schema_v0_1`

This readout records the independent physical validation of the bounded
core-four candidate parquet artifact. The validation did not rewrite parquet,
did not reread market source data and did not promote the candidate artifact.

It closes only the physical acceptance review for the eight-row candidate
artifact. It does not authorize official Market State, production builders,
downstream State consumption, full-history/full-universe execution or dataset
promotion.

## 1. Inputs

```text
scope = configs/experimental_core_four_market_state_materialization_scope_v0_1.json
validation_script = scripts/core_four_market_state_candidate_physical_validation.py
source_candidate_records = runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/market_state_candidate_records.jsonl
candidate_parquet = runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/core_four_market_state_candidate_v0_1.parquet
source_materialization_manifest = runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/materialization_manifest.json
source_materialization_final_manifest = runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/final_manifest.json
rejected_context_report = runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/rejected_context_report.csv
```

The source JSONL remained the only source of expected row values. The parquet
was read only for physical validation.

## 2. Result

```text
core_four_market_state_candidate_physical_validation = PASS_WITH_RESTRICTIONS
overall_status = passed_core_four_market_state_candidate_physical_validation_with_restrictions
input_candidate_records = 8
output_physical_rows = 8
candidate_parquet_files = 1
candidate_parquet_bytes = 34097
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

The validator rebuilt the expected Arrow schema from the closed physical scope
and compared it against the parquet schema. The schema was not inferred from the
observed parquet rows.

## 4. Value Reconciliation

```text
value_mappings_checked = 136
expected_value_mappings = 136
source_to_physical_value_mismatches = 0
missing_source_value_fields = 0
extra_source_value_fields = 0
rvol_rename_checks = 8
rvol_rename_mismatches = 0
rvol_rename_passed = true
```

The review explicitly checked all `8 x 17` source-to-physical value mappings,
including:

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
state_output_fingerprint_matches = 8
state_output_fingerprint_mismatches = 0
materialized_state_candidate_id_matches = 8
materialized_state_candidate_id_mismatches = 0
```

Lineage validation compared canonical JSON content, not mere field presence:

```text
source_lineage_json = canonical(shared_source_evidence, object_record_ids)
policy_versions_json = canonical(input policy_versions)
formula_versions_json = canonical(closed physical formula mapping)
restriction_codes_json = canonical(sorted deduped input restrictions)
context_input_fingerprint = exact input fingerprint
```

## 6. Roundtrip And Rebuild

```text
roundtrip_rows_checked = 8
roundtrip_row_mismatches = 0
roundtrip_field_mismatches = 0
semantic_rebuild_compare_field_count = 37
semantic_rebuild_field_comparisons = 296
semantic_rebuild_differences = 0
byte_identical_parquet_rebuild_required = false
```

Roundtrip validation compared reconstructed pre-write physical rows with rows
read back from parquet. Semantic rebuild validation rebuilt the logical physical
rows with a different run id and compared only the 37 authorized semantic
fields.

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

The zero source-market-data read count is verified by static input boundary and
script behavior, not by operating-system filesystem telemetry.

## 8. Superseded Attempt

A first validation attempt exists at:

```text
runs/core_four_market_state_candidate_physical_validation_v0_1_20260722T093513Z/
```

It is superseded. That attempt failed because the validator incorrectly
required two non-existent candidate-record authority keys to be explicitly
false. The parquet, schema, values, lineage, fingerprints and roundtrip checks
were already passing in that attempt. A local `supersession_manifest.json`
inside the superseded run marks `accepted_as_closure_evidence = false` and
points to the accepted run. The accepted validation run is:

```text
runs/core_four_market_state_candidate_physical_validation_v0_1_20260722T093828Z/
```

## 9. Correct Interpretation

The candidate parquet is now independently validated as a faithful physical
representation of the eight accepted core-four Market State candidate records.

It remains bounded experimental evidence. It is not an official TSIS Market
State table, not production data and not downstream-consumable.

## 10. Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
bounded_eight_record_evidence_only
core_four_profile_is_not_complete_tsis_market_state
```

## 11. Next Boundary

No promotion or production gate is opened by this validation.

Any next step requires a separate design/authorization decision for bounded
scaling or another explicitly scoped review. Still not open:

```text
official Market State parquet materialization
production builder
downstream State consumption
full-history execution
full-universe execution
quote-dependent object integration
operational promotion
dataset promotion
```