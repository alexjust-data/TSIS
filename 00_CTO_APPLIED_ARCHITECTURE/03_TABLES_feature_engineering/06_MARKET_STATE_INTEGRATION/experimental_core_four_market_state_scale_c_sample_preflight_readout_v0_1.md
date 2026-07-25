# Experimental Core Four Market State Scale C Sample Preflight Readout v0.1

run_id = `experimental_core_four_market_state_scale_c_sample_preflight_v0_1_20260723T152658Z`
script_version = `experimental_core_four_market_state_scale_c_sample_preflight_v0_1`

## Decision

```text
experimental_core_four_market_state_scale_c_sample_preflight = BLOCKED_INSTRUMENT_HISTORY_COVERAGE
experimental_core_four_market_state_scale_c_execution = BLOCKED_NOT_STARTED
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
sample_manifest_rows = 0
selected_sessions = 8
selected_period_years = 5
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
required_instruments = 10
minimum_instruments = 8
seed_pool_instruments = 13
eligible_instruments = 3
selected_instruments = 0
expected_resolution_records = 480
expected_blocked_contexts = 16
expected_integrable_contexts = 104
observed_expected_blocked_contexts = 0
observed_expected_integrable_contexts = 0
estimated_daily_rows = 13388
estimated_intraday_rows = 213792
estimated_total_source_rows = 227180
source_coverage_failures = 0
historical_source_coverage_failures = 0
formula_history_coverage_failures = 0
identity_history_failures = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
stratification_failures = 1
hard_preflight_failures = 1
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

## Blocked

The preflight did not freeze a Scale C sample. Surface construction, builders, integration and materialization remain not started.

## Outputs

Run directory: `C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_c_sample_preflight_v0_1_20260723T152658Z`

## Next Gate

```text
experimental_core_four_market_state_scale_c_execution_surface_construction_authorization = NOT_OPEN_NEXT_IF_PASS
```
