# Experimental Core Four Market State Scale A Candidate Materialization Execution Readout v0.1

run_id: `experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z`
status: `CLOSED_PASS_WITH_RESTRICTIONS`

## Scope

This gate consumed the accepted Scale A integrated Market State candidate records and emitted one bounded, non-official candidate parquet.
It did not read source market data, did not execute builders, did not integrate additional Information Objects and did not authorize downstream consumption.

## Inputs

```text
source_integration_run_id = experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z
input_candidate_records = 52
rejected_contexts_available = 8
```

## Counts

```text
output_candidate_rows = 52
candidate_parquet_files_written = 1
candidate_parquet_bytes = 66399
physical_column_count = 40
physical_value_column_count = 17
source_market_data_rows_read = 0
rejected_contexts_materialized_as_rows = 0
```

## Validation

```text
schema_match = true
duplicate_primary_keys = 0
duplicate_source_candidate_record_ids = 0
duplicate_materialized_state_candidate_ids = 0
missing_required_columns = 0
extra_columns = 0
semantic_equality_failures = 0
lineage_losses = 0
restriction_losses = 0
fingerprint_mismatches = 0
roundtrip_failures = 0
semantic_rebuild_differences = 0
hard_validation_failures = 0
```

## Artifacts

```text
scope = configs/experimental_core_four_market_state_scale_a_candidate_materialization_scope_v0_1.json
script = scripts/core_four_market_state_materialization_probe.py
run_dir = runs/experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z/
parquet = runs/experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z/core_four_market_state_scale_a_candidate_v0_1.parquet
```

## Next Gate

Allowed next: `experimental_core_four_market_state_scale_a_candidate_physical_validation`.
Still closed: official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale B and Scale C.
