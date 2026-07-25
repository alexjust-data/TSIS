# Experimental Core Four Market State Scale C Sample Preflight Readout v0.2

run_id = `experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z`
script_version = `experimental_core_four_market_state_scale_c_sample_preflight_v0_2`

## Decision

```text
experimental_core_four_market_state_scale_c_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_c_execution = NOT_EXECUTED_READY_FOR_SEPARATE_GATE
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

## Counts

```text
requested_contexts = 120
sample_manifest_rows = 120
selected_sessions = 8
selected_period_years = 5
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
required_instruments = 10
minimum_instruments = 8
seed_pool_instruments = 40
eligible_instruments = 40
selected_instruments = 10
expected_resolution_records = 480
expected_blocked_contexts = 16
expected_integrable_contexts = 104
observed_expected_blocked_contexts = 16
observed_expected_integrable_contexts = 104
estimated_daily_rows = 472754
estimated_intraday_rows = 1385127
estimated_total_source_rows = 1857881
source_coverage_failures = 0
historical_source_coverage_failures = 0
formula_history_coverage_failures = 0
identity_history_failures = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
stratification_failures = 0
hard_preflight_failures = 0
```

## Boundary

```text
builders_executed = false
resolution_records_emitted = 0
market_state_integration_executed = false
market_state_materialization_executed = false
market_state_parquet_files_written = 0
run_local_014_surface_construction = false
013_direct_builder_input = false
013_use = bounded_source_coverage_feasibility_only
```

## Frozen Sample

```text
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
instrument_selection_fingerprint = 7e5cc85288b12e917fd1386a25d939e0be6b27562f38015efc79d0c2fa34ebc3
session_selection_fingerprint = 21bf9643f6a60baabd7c64b55e812c7c729ba32f601eed96f8e151a4d218192a
```

The preflight froze a governed-calendar Scale C sample. It did not authorize Scale C surface construction, builder/resolution execution, integration, materialization or downstream consumption.

## Outputs

Run directory: `C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z`

## Next Gate

```text
experimental_core_four_market_state_scale_c_execution_surface_construction_authorization = NOT_OPEN_NEXT_IF_PASS
```
