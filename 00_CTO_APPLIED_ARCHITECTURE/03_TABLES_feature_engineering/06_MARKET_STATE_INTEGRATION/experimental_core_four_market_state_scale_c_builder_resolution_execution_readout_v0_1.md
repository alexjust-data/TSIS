# Experimental Core Four Market State Scale C Builder/Resolution Execution Readout v0.1

run_id: `experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z`
status: `CLOSED_PASS_WITH_RESTRICTIONS`

## Scope

This gate consumed the frozen Scale C sample, the accepted run-local Scale C execution surface, governed calendar binding, and 004 daily rows.
It emitted Information Object resolution records only. It did not read 013 directly, rebuild the surface, execute Market State integration, or write candidate Market State parquet.

## Counts

requested_contexts = 120
resolution_records = 480
integrable_contexts = 104
blocked_contexts = 16
failed_contexts = 0
pass_or_pass_with_restrictions_records = 416
blocked_input_unavailable_records = 64

## Bound Inputs

scale_c_sample_fingerprint = `67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d`
scale_c_execution_surface_fingerprint = `34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554`
calendar_binding_run_id = `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z`
calendar_version = `governed_exchange_session_calendar_xnys_v0_1`
calendar_source_snapshot_fingerprint = `8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967`

## Validation

source_market_data_rows_read = 29049
source_004_rows_read = 15080
source_014_rows_read = 13969
source_013_rows_read = 0
formula_failures = 0
future_bar_leaks = 0
calendar_binding_failures = 0
session_boundary_failures = 0
decision_case_semantic_mismatches = 0
early_close_cutoff_failures = 0
bars_beyond_governed_close_admitted = 0
fixed_utc_fallback_uses = 0
output_contract_failures = 0
nondeterministic_records = 0
semantic_equality_failures = 0
authority_failures = 0
hard_validation_failures = 0

## Restrictions Preserved

- candidate artifacts remain non-canonical
- accepted surface is run-local, not official 014
- core-four profile is not complete TSIS Market State
- fixed UTC probe calendar is not current authority
- 013 may appear only as surface lineage, not builder input
- pre-bar current-session values remain blocked
- after_last_sampled_bar remains not-session-close semantics
- quote-dependent objects remain excluded

## Next Gate

Allowed next: `experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization_v0_1`.
Still closed at that checkpoint: Scale C Market State integration until separate authorization, candidate materialization, official Market State, production builder, downstream consumption, promotion, full-history and full-universe.

## Run Directory

`C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z`
