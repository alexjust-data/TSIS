# Experimental Core Four Market State Scale B Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_b_scope_v0_1`
Stage: `core_four_market_state_scale_b_multi_session_calendar_aware`

This authorization opens only the bounded Scale B calendar-aware sample preflight gate. It does not execute builders, emit Information Object resolution records, integrate Market State, materialize Market State, write Market State parquet, authorize production, authorize downstream consumption, run full history, run full universe or promote any dataset.

---

## 1. Prerequisites

```text
experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS
governed_exchange_session_calendar_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
governed_exchange_session_calendar_binding_authorization = AUTHORIZED_WITH_RESTRICTIONS
governed_exchange_session_calendar_binding_validation = CLOSED_PASS_WITH_RESTRICTIONS
accepted_calendar_binding_run = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
```

Accepted calendar binding evidence:

```text
calendar_profile_id = governed_exchange_session_calendar_v0_1
calendar_version = governed_exchange_session_calendar_xnys_v0_1
source_rows = 5328
bound_rows = 5328
early_close_sessions = 45
source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
hard_validation_failures = 0
```

---

## 2. Authorized Gate

```text
experimental_core_four_market_state_scale_b_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_b_sample_preflight = NOT_EXECUTED_NEXT
experimental_core_four_market_state_scale_b_execution_authorization = NOT_OPEN
experimental_core_four_market_state_scale_b_builder_resolution_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_b_market_state_integration_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_b_candidate_materialization_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_b_candidate_physical_validation = NOT_AUTHORIZED
experimental_core_four_market_state_scale_b_execution = NOT_AUTHORIZED
```

The next executable unit is a sample preflight. It may freeze a calendar-aware sample only if calendar, identity and source coverage all pass. If coverage is insufficient, it must close as a blocked preflight and emit no frozen sample manifest.

---

## 3. Scale B Objective

Scale B tests whether the accepted core-four architecture remains temporally legal when the session boundary comes from a governed exchange calendar instead of the fixed UTC probe guard.

Scale B must demonstrate coverage across:

```text
winter regular session
summer regular session
US DST transition neighborhood
Europe/US DST desynchronization neighborhood
early-close session
pre-bar expected-blocked context
regular intraday context
after_last_sampled_bar context not promoted to market close
```

Scale B must retire `fixed_utc_probe_calendar_v0_1` as current temporal authority. It may only appear as historical lineage for earlier Scale A/probe evidence.

---

## 4. Authorized Calendar Session Plan

The preflight must test these governed XNYS sessions:

```text
2025-01-21 | winter_regular_standard_time | open_utc=14:30 | close_utc=21:00 | regular
2025-03-10 | us_dst_transition_neighborhood | open_utc=13:30 | close_utc=20:00 | regular
2025-03-24 | europe_us_dst_desynchronization | open_utc=13:30 | close_utc=20:00 | regular
2025-07-02 | summer_regular_dst | open_utc=13:30 | close_utc=20:00 | regular
2025-07-03 | summer_early_close | open_utc=13:30 | close_utc=17:00 | early_close
2025-11-28 | winter_early_close | open_utc=14:30 | close_utc=18:00 | early_close
```

No holiday or closed-day row is authorized. Absence-based holiday inference remains closed.

---

## 5. Sample Shape Authorized For Preflight

```text
target_requested_contexts = 72
maximum_requested_contexts = 96
required_objects_per_context = 4
target_resolution_records_if_later_executed = 288
maximum_resolution_records_if_later_executed = 384
selected_instruments = 8
candidate_instrument_pool_minimum = 8
selected_sessions = 6
expected_blocked_contexts = 8
maximum_blocked_contexts = 16
target_integrable_contexts = 64
maximum_integrated_candidate_records_if_later_executed = 88
maximum_physical_candidate_rows_if_later_executed = 88
```

Context allocation target:

```text
instrument_session_core_contexts = 48
pre_bar_expected_blocked_contexts = 8
after_last_sampled_bar_restricted_contexts = 8
calendar_boundary_stress_contexts = 8
```

The preflight must produce a deterministic sample fingerprint if and only if all hard preflight criteria pass.

---

## 6. Allowed Inputs For The Preflight

Allowed evidence and bounded source aliases:

```text
governed_exchange_session_calendar_bound_v0_1 from accepted calendar binding run
eligible_instrument_pool.json from accepted Scale A eligible representation surface
004_master_daily_table for bounded source coverage checks only
014_master_intraday_bar_table_candidate for bounded source coverage checks only
013_ohlcv_1m_quote_guarded for bounded source coverage feasibility only
```

`013` remains forbidden as a direct builder, Market State, materialization or downstream input. Any future run-local 014-derived surface for Scale B requires a separate remediation or construction authorization unless explicitly added by a later gate.

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
maximum_daily_rows_read_for_preflight = 50000
maximum_intraday_rows_read_for_preflight = 500000
maximum_total_source_rows_read_for_preflight = 550000
required_output_files = 13
maximum_output_files = 14
unexpected_output_files = 0
maximum_output_bytes = 5000000
candidate_market_state_parquet_files_allowed = 0
```

No builder or formula execution is authorized by these row-read limits.

---

## 8. Required Preflight Outputs

```text
pre_manifest.json
heartbeat.json
scale_b_calendar_session_plan.json
scale_b_calendar_coverage_report.csv
scale_b_instrument_selection_report.csv
scale_b_source_coverage_preflight_report.csv
scale_b_context_plan_report.csv
scale_b_duplicate_context_report.csv
scale_b_sample_manifest.jsonl
scale_b_sample_summary.json
scale_b_authority_report.json
final_manifest.json
experimental_core_four_market_state_scale_b_sample_preflight_readout_v0_1.md
```

If the preflight blocks before sample freeze, `scale_b_sample_manifest.jsonl` must be empty or absent and `sample_freeze_status` must not equal `FROZEN`.

---

## 9. Preflight Closure Criteria

PASS_WITH_RESTRICTIONS requires:

```text
accepted_calendar_binding_run_consumed = true
calendar_version = governed_exchange_session_calendar_xnys_v0_1
selected_sessions = 6
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
selected_instruments = 8
requested_contexts = 72
expected_resolution_records = 288
expected_blocked_contexts = 8
expected_integrable_contexts = 64
source_coverage_failures = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
identity_failures = 0
stratification_failures = 0
hard_preflight_failures = 0
scale_b_sample_fingerprint_present = true
```

Allowed blocked outcomes:

```text
BLOCKED_SOURCE_SESSION_COVERAGE
BLOCKED_INSTRUMENT_COVERAGE
BLOCKED_CALENDAR_SESSION_PLAN
BLOCKED_SAMPLE_CARDINALITY
FAILED_AUTHORITY_BOUNDARY
FAILED_CONTRACT
```

---

## 10. Preserved Restrictions

```text
Scale B execution is not authorized
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
next_allowed_gate = experimental_core_four_market_state_scale_b_sample_preflight_v0_1
```

Only after the preflight freezes a valid Scale B sample may a separate Scale B execution authorization be opened.

