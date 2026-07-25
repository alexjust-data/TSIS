# Experimental Core Four Market State Scale C Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_scope_v0_1`
Stage: `core_four_market_state_scale_c_multi_period_historical_bounded`

This authorization opens only the bounded Scale C historical sample preflight
gate. It does not execute builders, emit Information Object resolution
records, integrate Market State, materialize Market State, write Market State
parquet, authorize production, authorize downstream consumption, run full
history, run full universe or promote any dataset.

---

## 1. Prerequisites

```text
experimental_core_four_market_state_scale_b_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_execution_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
governed_exchange_session_calendar_binding_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

Accepted Scale B closure evidence:

```text
sample_preflight_run =
experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z

execution_surface_run =
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z

builder_resolution_run =
experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z

integration_run =
experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z

candidate_materialization_run =
experimental_scale_b_ms_candidate_materialization_v0_1_20260723T144955Z

candidate_physical_validation_run =
core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z
```

Accepted fingerprints and counts:

```text
scale_b_sample_fingerprint =
5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972

scale_b_execution_surface_fingerprint =
dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa

calendar_version =
governed_exchange_session_calendar_xnys_v0_1

calendar_source_snapshot_fingerprint =
8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967

scale_b_candidate_parquet_sha256 =
33469c968812da7f6459ca2f6e13e973521d5075fe9db0285e1d89d1d80a80c1

scale_b_physical_rows = 64
scale_b_value_mappings_checked = 1088
scale_b_hard_validation_failures = 0
```

---

## 2. Authorized Gate

```text
experimental_core_four_market_state_scale_c_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_c_sample_preflight = NOT_EXECUTED_NEXT
experimental_core_four_market_state_scale_c_execution_authorization = NOT_OPEN
experimental_core_four_market_state_scale_c_execution_surface_construction = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_builder_resolution_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_market_state_integration_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_candidate_materialization_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_candidate_physical_validation = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_execution = NOT_AUTHORIZED
```

The next executable unit is a sample preflight. It may freeze a multi-period
historical bounded sample only if calendar, identity, historical source
coverage and formula-history coverage all pass. If coverage is insufficient,
it must close as a blocked preflight and emit no frozen sample manifest.

---

## 3. Scale C Objective

Scale C tests whether the accepted core-four architecture remains reproducible
across a larger bounded historical period without acquiring production,
official Market State, downstream or full-history authority.

Scale C must test:

```text
schema drift across periods
identity history across periods
historical source coverage
prior-20 daily formula history coverage
governed calendar boundary stability
early-close and DST behavior across years
deterministic sample freeze
```

Scale C is not:

```text
full-history execution
full-universe execution
official 016 Market State
production State Builder
downstream-consumable State
dataset promotion
```

---

## 4. Authorized Historical Session Plan

The preflight must evaluate only these governed XNYS sessions:

```text
2021-01-19 | 2021_winter_regular_standard_time | open_utc=14:30 | close_utc=21:00 | regular
2021-03-15 | 2021_us_dst_transition_neighborhood | open_utc=13:30 | close_utc=20:00 | regular
2022-07-05 | 2022_summer_regular_dst | open_utc=13:30 | close_utc=20:00 | regular
2022-11-25 | 2022_winter_early_close | open_utc=14:30 | close_utc=18:00 | early_close
2023-03-20 | 2023_europe_us_dst_desynchronization | open_utc=13:30 | close_utc=20:00 | regular
2023-07-03 | 2023_summer_early_close | open_utc=13:30 | close_utc=17:00 | early_close
2024-03-11 | 2024_us_dst_transition_neighborhood | open_utc=13:30 | close_utc=20:00 | regular
2025-07-03 | 2025_summer_early_close | open_utc=13:30 | close_utc=17:00 | early_close
```

No holiday or closed-day row is authorized. Absence-based holiday inference
remains closed.

---

## 5. Sample Shape Authorized For Preflight

```text
target_requested_contexts = 120
maximum_requested_contexts = 160
required_objects_per_context = 4
target_resolution_records_if_later_executed = 480
maximum_resolution_records_if_later_executed = 640
candidate_instrument_pool_cap = 40
selected_instruments_target = 10
selected_instruments_minimum = 8
selected_sessions = 8
selected_period_years = 5
expected_blocked_contexts = 16
maximum_blocked_contexts = 32
target_integrable_contexts = 104
maximum_integrated_candidate_records_if_later_executed = 140
maximum_physical_candidate_rows_if_later_executed = 140
```

Context allocation target:

```text
instrument_session_core_contexts = 80
pre_bar_expected_blocked_contexts = 10
after_last_sampled_bar_restricted_contexts = 10
historical_period_boundary_stress_contexts = 20
```

The preflight must produce a deterministic Scale C sample fingerprint if and
only if all hard preflight criteria pass.

---

## 6. Allowed Inputs For The Preflight

Allowed evidence and bounded source aliases:

```text
governed_exchange_session_calendar_bound_v0_1 from accepted calendar binding run
eligible_instrument_pool.json from accepted Scale A eligible representation surface
eligible_surface_source_snapshot_manifest.json from accepted Scale A eligible representation surface
004_master_daily_table for bounded source coverage and prior-20 daily history checks only
013_ohlcv_1m_quote_guarded for bounded historical intraday coverage feasibility only
```

`013` remains forbidden as a direct builder, Market State, materialization or
downstream input. Any future Scale C run-local 014-derived execution surface
requires a separate execution authorization after the sample preflight passes.

Forbidden inputs:

```text
raw_quotes
quote-dependent objects
015 microstructure features
production State tables
official Market State tables
downstream feature stores
full-history market data scans
full-universe market data scans
00_CTO/99_REFERENCE_LIBRARY
```

---

## 7. Source Read Limits

```text
maximum_calendar_rows_read = 5328
maximum_daily_rows_read_for_preflight = 150000
maximum_intraday_rows_read_for_preflight = 1000000
maximum_total_source_rows_read_for_preflight = 1200000
required_output_files = 14
maximum_output_files = 15
unexpected_output_files = 0
maximum_output_bytes = 8000000
candidate_market_state_parquet_files_allowed = 0
```

No builder or formula execution is authorized by these row-read limits.

---

## 8. Required Preflight Outputs

```text
pre_manifest.json
heartbeat.json
scale_c_calendar_period_plan.json
scale_c_calendar_coverage_report.csv
scale_c_instrument_selection_report.csv
scale_c_source_coverage_preflight_report.csv
scale_c_historical_coverage_report.csv
scale_c_context_plan_report.csv
scale_c_duplicate_context_report.csv
scale_c_sample_manifest.jsonl
scale_c_sample_summary.json
scale_c_authority_report.json
final_manifest.json
experimental_core_four_market_state_scale_c_sample_preflight_readout_v0_1.md
```

If the preflight blocks before sample freeze, `scale_c_sample_manifest.jsonl`
must be empty or absent and `sample_freeze_status` must not equal `FROZEN`.

---

## 9. Preflight Closure Criteria

PASS_WITH_RESTRICTIONS requires:

```text
accepted_scale_b_physical_validation_run_consumed = true
accepted_calendar_binding_run_consumed = true
calendar_version = governed_exchange_session_calendar_xnys_v0_1
selected_sessions = 8
selected_period_years = 5
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
selected_instruments >= 8
requested_contexts = 120
expected_resolution_records = 480
expected_blocked_contexts = 16
target_integrable_contexts = 104
source_coverage_failures = 0
historical_source_coverage_failures = 0
formula_history_coverage_failures = 0
identity_history_failures = 0
schema_drift_blockers = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
stratification_failures = 0
hard_preflight_failures = 0
scale_c_sample_fingerprint_present = true
```

Allowed blocked outcomes:

```text
BLOCKED_SOURCE_PERIOD_COVERAGE
BLOCKED_INSTRUMENT_HISTORY_COVERAGE
BLOCKED_CALENDAR_PERIOD_PLAN
BLOCKED_SAMPLE_CARDINALITY
BLOCKED_FORMULA_HISTORY_COVERAGE
FAILED_AUTHORITY_BOUNDARY
FAILED_CONTRACT
```

---

## 10. Preserved Restrictions

```text
Scale C execution is not authorized
Scale C run-local 014 surface construction is not authorized
builder/resolution execution is not authorized
Market State integration is not authorized
Market State materialization is not authorized
Market State parquet is not authorized
production builder is not authorized
official Market State is not authorized
downstream consumption is not authorized
full-history/full-universe execution is not authorized
quote-dependent objects remain excluded
closed-day and holiday inference remain excluded
```

---

## 11. Next Gate

```text
next_allowed_gate = experimental_core_four_market_state_scale_c_sample_preflight_v0_1
```

Only after the preflight freezes a valid Scale C sample may a separate Scale C
execution authorization be opened.
