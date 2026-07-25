# Experimental Core Four Market State Scale C Authorization v0.2

Status: `authorized_with_restrictions_v0_2`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_scope_v0_2`
Stage: `core_four_market_state_scale_c_multi_period_historical_bounded`

This revision opens only a bounded Scale C historical sample preflight with
deterministic historical candidate-pool discovery. It supersedes the v0.1
preflight attempt only for sample construction because the v0.1 seed pool was
not historically deep enough.

---

## 1. Superseded Attempt

```text
previous_preflight_run =
experimental_core_four_market_state_scale_c_sample_preflight_v0_1_20260723T152658Z

previous_preflight_status =
BLOCKED_INSTRUMENT_HISTORY_COVERAGE

previous_required_instruments = 10
previous_minimum_instruments = 8
previous_eligible_instruments = 3
previous_sample_manifest_rows = 0
```

The blocked attempt is retained as valid negative evidence. It is not accepted
as closure evidence for Scale C sample preflight because no sample fingerprint
was frozen.

---

## 2. Revision Reason

The Scale A eligible pool was built for the accepted Scale A/Scale B period and
contained only three instruments with complete governed-session coverage across
the authorized 2021-2025 Scale C sessions:

```text
AAME
ABEO
ABUS
```

This is a pool-depth limitation, not a calendar binding defect and not a source
root failure. The governed calendar matched all eight historical sessions and
the v0.1 run preserved the authority boundary.

---

## 3. Authorized Gate

```text
experimental_core_four_market_state_scale_c_authorization_v0_2 = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_c_sample_preflight_v0_2 = NOT_EXECUTED_NEXT
experimental_core_four_market_state_scale_c_execution_surface_construction = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_builder_resolution_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_market_state_integration_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_candidate_materialization_execution = NOT_AUTHORIZED
experimental_core_four_market_state_scale_c_candidate_physical_validation = NOT_AUTHORIZED
official_market_state = NOT_OPEN
```

The next executable unit is still a sample preflight. It may freeze a Scale C
sample only if the historical candidate pool, governed calendar, source
coverage, identity history and prior-20 history all pass.

---

## 4. Revised Candidate Pool Policy

The accepted Scale A eligible pool remains lineage evidence only. It is not a
hard candidate universe for Scale C v0.2.

The preflight may discover a historical candidate pool from:

```text
004_master_daily_table
```

using only:

```text
authorized Scale C session dates
the governed prior 20 trading sessions for each authorized session
price_view = split_normalized
```

The preflight may then verify intraday feasibility through:

```text
013_ohlcv_1m_quote_guarded
```

for no more than:

```text
candidate_tickers_for_intraday_feasibility_cap = 40
```

This is bounded candidate-pool discovery. It is not full-history execution, not
full-universe execution and not builder input authorization.

---

## 5. Sample Shape

```text
target_requested_contexts = 120
required_objects_per_context = 4
target_resolution_records_if_later_executed = 480
selected_instruments_target = 10
selected_instruments_minimum = 8
selected_sessions = 8
selected_period_years = 5
expected_blocked_contexts = 16
target_integrable_contexts = 104
```

The context allocation remains:

```text
instrument_session_core_contexts = 80
pre_bar_expected_blocked_contexts = 10
after_last_sampled_bar_restricted_contexts = 10
historical_period_boundary_stress_contexts = 20
```

---

## 6. Authority Boundary

Still forbidden:

```text
Scale C execution surface construction
builder/resolution execution
Information Object formula execution
Market State integration
Market State materialization
Market State parquet writes
013 direct builder input
014 builder input
raw quotes
downstream consumption
dataset promotion
production
full history
full universe
```

Allowed only for the preflight:

```text
governed calendar binding read
004 bounded historical candidate-pool discovery and prior-20 checks
013 bounded intraday coverage feasibility for capped candidates
eligible Scale A pool lineage read
```

---

## 7. Closure Criteria

```text
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
selected_sessions = 8
selected_period_years = 5
selected_instruments = 10
sample_manifest_rows = 120
expected_resolution_records = 480
expected_blocked_contexts = 16
target_integrable_contexts = 104
source_coverage_failures = 0
historical_source_coverage_failures = 0
formula_history_coverage_failures = 0
identity_history_failures = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
stratification_failures = 0
hard_preflight_failures = 0
scale_c_sample_fingerprint_present = true
```

If any hard criterion fails, the run must close as a blocked preflight and emit
no frozen sample manifest.

