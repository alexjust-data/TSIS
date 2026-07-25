# Experimental Core Four Market State Scale B Execution Surface Construction Readout v0.1

Status: `CLOSED_PASS_WITH_RESTRICTIONS`
Date: `2026-07-23`

This readout records the accepted non-production Scale B run-local 014-derived execution surface construction.

```text
accepted_run = experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z
script = scripts/experimental_core_four_market_state_scale_b_execution_surface_construction.py
scope = configs/experimental_core_four_market_state_scale_b_execution_surface_construction_scope_v0_1.json
final_manifest = runs/experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z/scale_b_execution_surface_final_manifest.json
surface_parquet = runs/experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z/014_scale_b_execution_surface_candidate_v0_1.parquet
```

## Accepted Evidence

```text
surface_construction_status = CLOSED_PASS_WITH_RESTRICTIONS
sample_manifest_rows = 72
scale_b_sample_fingerprint = 5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972
sample_fingerprint_match = true
selected_instruments = 8
selected_sessions = 6
selected_instrument_sessions = 48
source_013_files_read = 32
source_013_rows_read = 149237
maximum_013_rows_read_for_execution_surface = 250000
surface_rows_written = 8112
maximum_run_local_014_execution_surface_rows = 25000
candidate_surface_parquet_files_written = 1
surface_parquet_sha256 = 883bc41d089e33671f2d6aac689b79976bd205a0ab979c74ed54bd0856465e7e
scale_b_execution_surface_fingerprint = dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa
source_snapshot_fingerprint = 4a8562a166e8b145b499b6ac813880e67b6fb3e010ad77dbd2e91c7c2c17972b
calendar_selection_fingerprint = 4830907a028db2a75a4eeca91e64ff88b701d15aa1625eeac0c62b47f37676e2
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
```

## Calendar And Boundary Checks

```text
calendar_binding_failures = 0
calendar_version_match = true
fixed_utc_probe_calendar_as_current_authority = 0
distinct_governed_open_utc_clocks = 13:30:00, 14:30:00
distinct_governed_close_utc_clocks = 17:00:00, 18:00:00, 20:00:00, 21:00:00
selected_instruments_missing = 0
selected_sessions_missing = 0
unexpected_instruments = 0
unexpected_sessions = 0
source_coverage_failures = 0
selected_instrument_sessions_missing = 0
session_boundary_mismatches = 0
early_close_boundary_failures = 0
cutoff_failures = 0
pre_bar_admitted_bar_failures = 0
integrable_contexts_without_prior_or_current_bar = 0
```

## Duplicate And Authority Checks

```text
duplicate_groups = 0
identical_duplicate_groups = 0
conflicting_duplicate_groups = 0
builder_records_emitted = 0
information_object_formulas_executed = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
original_014_modified = false
013_direct_builder_input = false
authority_failures = 0
determinism_failures = 0
hard_validation_failures = 0
```

## Superseded Attempts

```text
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T105511Z = superseded_partial_run_missing_final_manifest_due_windows_long_path_temp_write_failure_not_data_defect
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T110307Z = superseded_empty_run_after_incorrect_long_path_prefix_before_pre_manifest_not_data_defect
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T110716Z = superseded_failed_contract_due_python_output_enumeration_long_path_limit_not_data_defect
```

## Boundary

The accepted surface is a run-local 014-derived execution surface candidate only. It is not official 014, not Market State, not production, not downstream consumable and not a promoted dataset.

`013_ohlcv_1m_quote_guarded` was read only to construct this run-local surface and remains forbidden as direct input to builders, Market State integration, materialization or downstream consumers.

Subsequent authorization emitted after this surface closure:

```text
experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
next_executable_gate = experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1
```


## Continuity Note 2026-07-23

Subsequent authorization was emitted after this surface readout:

```text
experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
scope = configs/experimental_core_four_market_state_scale_b_builder_resolution_execution_scope_v0_1.json
next_executable_gate = experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1
```

This readout remains the accepted evidence for the run-local Scale B execution surface. It must not be read as current evidence that builder/resolution authorization is still unopened.
