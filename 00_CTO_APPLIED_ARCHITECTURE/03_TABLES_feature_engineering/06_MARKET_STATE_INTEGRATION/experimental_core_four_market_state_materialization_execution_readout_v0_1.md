# Experimental Core Four Market State Materialization Execution Readout v0.1

Status: `closed_pass_with_restrictions_v0_1`
Date: `2026-07-22`
Run: `experimental_core_four_market_state_materialization_v0_1_20260722T081155Z`
Logical Profile: `core_four_market_state_profile_v0_1`
Physical Schema: `core_four_market_state_candidate_physical_schema_v0_1`

This readout records the first bounded experimental physical materialization of
accepted core-four Market State candidate records into one non-official parquet
candidate artifact.

It does not authorize official Market State, production builders, downstream
State consumption, full-history/full-universe execution or dataset promotion.

## 1. Inputs

```text
source_integration_run = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
materialization_design = core_four_market_state_materialization_design_v0_1
materialization_contract = core_four_market_state_materialization_design_contract_v0_1
authorization = experimental_core_four_market_state_materialization_authorization_v0_1
execution_scope = experimental_core_four_market_state_materialization_scope_v0_1
script = scripts/core_four_market_state_materialization_probe.py
```

The only source of physical rows and values was:

```text
market_state_candidate_records.jsonl
```

The integration context, value manifest, rejected-context report, integration
summary and final manifest were used only for reconciliation and authority
checks. The materializer did not reread physical market source tables.

## 2. Result

```text
experimental_core_four_market_state_materialization_execution = PASS_WITH_RESTRICTIONS
overall_status = passed_core_four_market_state_materialization_with_restrictions
input_candidate_records = 8
output_candidate_rows = 8
rejected_contexts_materialized_as_rows = 0
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_parquet_bytes = 34097
physical_column_count = 40
physical_value_column_count = 17
hard_validation_failures = 0
```

## 3. Physical Representation

```text
candidate_parquet = 06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/core_four_market_state_candidate_v0_1.parquet
pyarrow_version = 21.0.0
compression = snappy
use_dictionary = false
timestamp_unit = us
timezone = UTC
row_group_size = 8
schema_inference_from_sample = false
```

The schema was built explicitly from the closed scope. It was not inferred from
the eight input records.

## 4. Validation Evidence

```text
schema_match = true
duplicate_primary_keys = 0
duplicate_source_candidate_record_ids = 0
duplicate_materialized_state_candidate_ids = 0
missing_required_columns = 0
extra_columns = 0
namespace_collisions = 0
non_nullable_nulls = 0
type_coercion_failures = 0
semantic_equality_failures = 0
lineage_losses = 0
restriction_losses = 0
fingerprint_mismatches = 0
roundtrip_failures = 0
semantic_rebuild_differences = 0
semantic_rebuild_compare_field_count = 37
byte_identical_parquet_rebuild_required = false
```

Roundtrip validation compared normalized pre-write rows with rows reread from
the same parquet file. Semantic rebuild determinism compared the authorized 37
fields and ignored only run-specific or parquet metadata fields.

## 5. Output Artifacts

```text
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/pre_manifest.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/heartbeat.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/core_four_market_state_candidate_v0_1.parquet
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/materialization_manifest.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/schema_report.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/grain_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/lineage_report.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/restriction_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/fingerprint_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/roundtrip_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/reconciliation_report.csv
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/rebuild_determinism_report.json
06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/final_manifest.json
```

## 6. Correct Interpretation

The parquet contains eight bounded experimental candidate rows for the core-four
profile. It is a physical representation of already accepted integration
candidate records.

It is not an official TSIS Market State table. It is not a production dataset
and is not authorized for downstream consumption.

## 7. Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
bounded_eight_record_evidence_only
core_four_profile_is_not_complete_tsis_market_state
```

## 8. Next Gate

The next gate is review/validation, not promotion:

```text
core_four_market_state_candidate_physical_validation = OPEN_NEXT_REVIEW_GATE
```

Still not open:

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
