# Experimental Core Four Market State Scale B Builder/Resolution Execution Readout v0.1

run_id: `experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z`
status: `CLOSED_PASS_WITH_RESTRICTIONS`

## Scope

This gate consumed the frozen Scale B sample, the accepted run-local Scale B execution surface, governed calendar binding, and 004 daily rows.
It emitted Information Object resolution records only. It did not read 013 directly, rebuild the surface, execute Market State integration, or write candidate Market State parquet.

## Counts

requested_contexts = 72
resolution_records = 288
integrable_contexts = 64
blocked_contexts = 8
failed_contexts = 0
pass_or_pass_with_restrictions_records = 256
blocked_input_unavailable_records = 32

## Bound Inputs

scale_b_sample_fingerprint = `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`
scale_b_execution_surface_fingerprint = `dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa`
calendar_binding_run_id = `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z`
calendar_version = `governed_exchange_session_calendar_xnys_v0_1`
calendar_source_snapshot_fingerprint = `8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967`

## Validation

source_market_data_rows_read = 12126
source_004_rows_read = 4014
source_014_rows_read = 8112
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

Allowed next: `experimental_core_four_market_state_scale_b_market_state_integration_execution_authorization_v0_1`.
Still closed: Market State integration until separate authorization, materialization, official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale C.

## Run Directory

`C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z`
