# Experimental Core Four Market State Scale A Builder/Resolution Execution Readout v0.1

run_id: `experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z`
status: `CLOSED_PASS_WITH_RESTRICTIONS`

## Scope

This gate consumed the frozen Scale A sample and emitted Information Object resolution records only.
It did not execute Market State integration, did not write candidate Market State parquet, and did not read 013 or raw quotes.

## Counts

requested_contexts = 60
resolution_records = 240
integrable_contexts = 52
blocked_contexts = 8
failed_contexts = 0
pass_or_pass_with_restrictions_records = 208
blocked_input_unavailable_records = 32

## Validation

source_market_data_rows_read = 5761
formula_failures = 0
future_bar_leaks = 0
output_contract_failures = 0
nondeterministic_records = 0
semantic_equality_failures = 0
hard_validation_failures = 0

## Restrictions Preserved

- candidate artifacts remain non-canonical
- core-four profile is not complete TSIS Market State
- Scale A is not calendar-aware validation
- fixed UTC probe calendar remains guarded
- after_last_sampled_bar remains not-session-close semantics
- quote-dependent objects remain excluded

## Superseded Attempts

`20260722T202216Z`, `20260722T202243Z` and `20260722T202407Z` are not accepted closure evidence. They were superseded by `20260722T202557Z` due wrapper/output-order and source-read-boundary reporting issues, not candidate-record formula defects.

## Next Gate

Allowed next: `experimental_core_four_market_state_scale_a_market_state_integration_execution`.
Still closed: official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale B, Scale C.

## Run Directory

`C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z`
