# Experimental Core Four Market State Scale C Execution Surface Construction Readout v0.1

run_id = `experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z`
script_version = `experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1`

## Decision

```text
experimental_core_four_market_state_scale_c_execution_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
scale_c_builder_resolution_execution = NOT_EXECUTED_REQUIRES_SEPARATE_GATE
market_state_integration = NOT_EXECUTED
market_state_materialization = NOT_EXECUTED
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
```

## Counts

```text
sample_manifest_rows = 120
selected_instruments = 10
selected_sessions = 8
selected_instrument_sessions = 80
source_013_rows_read = 360409
surface_rows_written = 13969
candidate_surface_parquet_files_written = 1
calendar_binding_failures = 0
session_boundary_mismatches = 0
early_close_boundary_failures = 0
source_coverage_failures = 0
conflicting_duplicate_groups = 0
cutoff_failures = 0
authority_failures = 0
determinism_failures = 0
hard_validation_failures = 0
```

## Fingerprints

```text
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
calendar_selection_fingerprint = 81915b4f62b212ea2f3a23479aa16a0ec588925b29602686ec345838f71a24c2
source_snapshot_fingerprint = b2888d6736641d26705cab11c35c1b6c516dd719bfe7c32b6da130695863e69e
scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554
surface_parquet_sha256 = 9eab0eb107db561a6ac6caa80d73de7402ca3ac54a3b4999773b583b3998a846
```

## Boundary

```text
013_direct_builder_input = false
builder_records_emitted = 0
information_object_formulas_executed = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
original_014_modified = false
```

Run directory: `C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z`
