# Experimental Core Four Market State Scale B Sample Preflight Readout v0.1

run_id = `experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z`
script_version = `experimental_core_four_market_state_scale_b_sample_preflight_v0_1`

## Decision

```text
experimental_core_four_market_state_scale_b_sample_preflight = PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_execution = NOT_EXECUTED_READY_FOR_SEPARATE_GATE
official_market_state = NOT_OPEN
production_builder = NOT_AUTHORIZED
downstream_consumption = NOT_AUTHORIZED
dataset_promotion = NOT_AUTHORIZED
full_history_execution = NOT_AUTHORIZED
full_universe_execution = NOT_AUTHORIZED
```

## Counts

```text
requested_contexts = 72
sample_manifest_rows = 72
selected_sessions = 6
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
required_instruments = 8
seed_pool_instruments = 13
eligible_instruments = 9
selected_instruments = 8
expected_resolution_records = 288
expected_blocked_contexts = 8
expected_integrable_contexts = 64
estimated_daily_rows = 6176
estimated_intraday_rows = 201514
estimated_total_source_rows = 207690
source_coverage_failures = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
identity_failures = 0
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
scale_b_sample_fingerprint = 5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972
instrument_selection_fingerprint = df5e15c29024345267e867eae76c78764201325c1478791d3b7c30482a93f375
session_selection_fingerprint = c25cbd5bd9ba683cfe9fa6da028cfa40fe106c6618b66bbbe5302493773a2945
```

The preflight froze a governed-calendar Scale B sample. It did not authorize Scale B execution; the next gate must separately authorize builder/resolution execution and any run-local 014-derived execution surface needed for those builders.

## Outputs

Run directory: `C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z`

## Next Gate

```text
experimental_core_four_market_state_scale_b_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_SUBSEQUENT_GATE
```


## Continuity Note 2026-07-23

Subsequent gates were emitted after this preflight readout. The current state is:

```text
experimental_core_four_market_state_scale_b_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_execution_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
accepted_surface_run = experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z
next_allowed_gate = experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization_v0_1
```

This readout remains the accepted evidence for the frozen sample only. It must not be read as current evidence that execution authorization is still unopened.
