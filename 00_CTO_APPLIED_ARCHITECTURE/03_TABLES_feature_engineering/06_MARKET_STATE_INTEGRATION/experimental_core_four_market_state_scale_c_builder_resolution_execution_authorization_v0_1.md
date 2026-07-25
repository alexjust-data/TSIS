# Experimental Core Four Market State Scale C Builder/Resolution Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_builder_resolution_execution_scope_v0_1`

This authorization opens only the bounded non-production Scale C builder/resolution execution subgate. It does not execute Market State integration, candidate materialization, physical validation, production, promotion or downstream consumption.

It binds the future execution to the frozen Scale C sample and the accepted run-local 014-derived Scale C execution surface.

---

## Cardinality Authority

```text
requested_contexts = 120
required_objects_per_context = 4
expected_resolution_records = 480
expected_blocked_contexts = 16
expected_integrable_contexts = 104
selected_instruments = 10
selected_sessions = 8
calendar_strata = 8
decision_case_families = 5
```

Required object order:

```text
price_location_structure
price_movement
trading_activity
volatility_range_state
```

---

## Frozen Sample Authority

```text
sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS
sample_run_id = experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z
sample_manifest_rows = 120
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
instrument_selection_fingerprint = 7e5cc85288b12e917fd1386a25d939e0be6b27562f38015efc79d0c2fa34ebc3
session_selection_fingerprint = 21bf9643f6a60baabd7c64b55e812c7c729ba32f601eed96f8e151a4d218192a
```

Execution must consume exactly:

```text
runs/experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z/scale_c_sample_manifest.jsonl
```

It must fail closed if the observed sample fingerprint differs from `67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d`. Reselecting or mutating the sample is forbidden.

---

## Surface Authority

```text
surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
surface_run_id = experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z
surface_rows = 13969
surface_parquet_sha256 = 9eab0eb107db561a6ac6caa80d73de7402ca3ac54a3b4999773b583b3998a846
scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554
surface_source_snapshot_fingerprint = b2888d6736641d26705cab11c35c1b6c516dd719bfe7c32b6da130695863e69e
```

The builder must read only this accepted run-local 014-derived surface for intraday values:

```text
runs/experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z/014_scale_c_execution_surface_candidate_v0_1.parquet
```

This surface is not official 014, not production, not promoted and not downstream consumable.

---

## Calendar Authority

```text
calendar_binding_run_id = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_calendar_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
exchange = XNYS
timezone = America/New_York
```

Every resolution record must preserve temporal lineage: `calendar_id`, `calendar_version`, `calendar_row_fingerprint`, `session_open_utc`, `session_close_utc`, `session_type`, and `is_early_close`.

---

## Source Boundary

Allowed source aliases:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
```

004 daily years allowed:

```text
2020, 2021, 2022, 2023, 2024, 2025
```

The 2020 and prior-year rows are authorized only to satisfy `prior_20` daily history for frozen Scale C contexts. This does not authorize additional sample dates, sample reselection, full-history daily reads or any 013 direct builder input.

Forbidden:

```text
013_ohlcv_1m_quote_guarded direct builder reads
surface reconstruction from 013
fixed_utc_probe_calendar_v0_1 fallback
raw_quotes
quote-dependent object records
Market State integration
Market State materialization
Market State parquet
production
state consumption
downstream consumption
dataset promotion
full-history/full-universe execution
```

Hard rule:

```text
013_direct_builder_reads_allowed = false
surface_rebuild_allowed = false
accepted_surface_only = true
```

---

## Scale C Temporal Semantics

The execution must demonstrate:

```text
before_first_observable_bar_governed_session -> current-session bar values blocked
historical_period_pre_open_boundary_blocked -> current-session bar values blocked
after_last_sampled_bar_not_session_close != session_close
governed_historical_session_close_boundary -> decision timestamp equals governed close
near/session-close contexts bounded by governed session close
early_close -> no bar after governed early close admitted
fixed_utc_fallback_uses = 0
```

The builder must not infer session close from absence of more bars in the surface.

---

## Closure Criteria

```text
sample_fingerprint_match = true
surface_fingerprint_match = true
calendar_source_snapshot_fingerprint_match = true
requested_contexts = 120
required_objects_per_context = 4
resolution_records = 480
missing_object_records = 0
extra_object_records = 0
expected_blocked_contexts = 16
unexpected_blocked_contexts = 0
unexpected_resolved_blocked_contexts = 0
expected_integrable_contexts = 104
failed_contexts = 0
future_leaks = 0
calendar_binding_failures = 0
calendar_row_bindings_missing = 0
calendar_row_bindings_multiple = 0
session_boundary_failures = 0
decision_case_semantic_mismatches = 0
early_close_failures = 0
early_close_cutoff_failures = 0
bars_beyond_governed_close_admitted = 0
fixed_utc_fallback_uses = 0
formula_failures = 0
semantic_equality_failures = 0
output_contract_failures = 0
fingerprint_failures = 0
nondeterministic_records = 0
source_013_rows_read = 0
surface_rebuilt = false
sample_reselected = false
sample_manifest_mutated = false
market_state_integration_executed = false
candidate_market_state_records_emitted = 0
candidate_parquet_files_written = 0
authority_failures = 0
hard_validation_failures = 0
```

---

## Next Boundary

The next executable subgate is:

```text
experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1
```

If it passes, the next gate must be a separate authorization for:

```text
experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization_v0_1
```

Still closed: Market State integration, materialization, official Market State, production, downstream consumption, dataset promotion, full-history/full-universe execution, quote-dependent object integration, surface reconstruction from 013, and 013 direct builder input.
