# Experimental Core Four Market State Scale A Market State Integration Execution Readout v0.1

run_id: `experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z`
status: `CLOSED_PASS_WITH_RESTRICTIONS`

## Scope

This gate consumed the accepted Scale A builder/resolution records and emitted integrated Market State candidate records only.
It did not read market data, did not execute builders, did not materialize parquet and did not authorize downstream consumption.

## Counts

input_resolution_records = 240
contexts_seen = 60
candidate_records_emitted = 52
rejected_contexts = 8
rejected_required_object_blocked_contexts = 8
admitted_value_rows = 884

## Validation

failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
hard_validation_failures = 0

## Next Gate

Allowed next: `experimental_core_four_market_state_scale_a_candidate_materialization_execution`.
Still closed: official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale B, Scale C.

## Run Directory

`C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z`
