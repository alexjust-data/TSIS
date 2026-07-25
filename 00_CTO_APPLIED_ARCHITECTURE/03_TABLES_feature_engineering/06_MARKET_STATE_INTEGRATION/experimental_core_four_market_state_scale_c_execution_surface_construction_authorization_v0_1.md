# Experimental Core Four Market State Scale C Execution Surface Construction Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_execution_surface_construction_scope_v0_1`

This authorization opens only the Scale C run-local intraday execution surface construction subgate. It consumes the frozen Scale C sample from `experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z` and does not authorize builder/resolution execution, Market State integration, materialization, production, promotion or downstream consumption.

---

## Frozen Sample Authority

```text
scale_c_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS
sample_preflight_run = experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z
sample_manifest_rows = 120
selected_instruments = 10
selected_sessions = 8
selected_period_years = 5
expected_resolution_records = 480
expected_blocked_contexts = 16
expected_integrable_contexts = 104
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
source_coverage_failures = 0
historical_source_coverage_failures = 0
formula_history_coverage_failures = 0
identity_history_failures = 0
stratification_failures = 0
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
instrument_selection_fingerprint = 7e5cc85288b12e917fd1386a25d939e0be6b27562f38015efc79d0c2fa34ebc3
session_selection_fingerprint = 21bf9643f6a60baabd7c64b55e812c7c729ba32f601eed96f8e151a4d218192a
```

The surface constructor must consume exactly:

```text
runs/experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z/scale_c_sample_manifest.jsonl
```

It must fail closed if the observed sample fingerprint differs from `67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d`. Reselecting or mutating the sample is forbidden.

---

## Governed Calendar Authority

```text
accepted_calendar_binding_run = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_calendar_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
fixed_utc_probe_calendar_as_current_authority = false
```

Scale C may use `fixed_utc_probe_calendar_v0_1` only as historical lineage for older evidence. It is not current temporal authority for this execution surface.

---

## Source Boundary

Allowed source aliases for this subgate:

```text
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

`013_ohlcv_1m_quote_guarded` is authorized only as bounded upstream input for constructing one run-local 014-derived Scale C execution surface candidate. It is not authorized as a direct builder input, Market State input, materialization input or downstream input.

Forbidden:

```text
004_master_daily_table
raw_quotes
quote-dependent object records
015 microstructure features
full-history market data scans
full-universe market data scans
production State tables
official Market State tables
downstream feature stores
00_CTO/99_REFERENCE_LIBRARY
```

---

## Exact Limits

```text
requested_contexts = 120
selected_instruments = 10
selected_sessions = 8
expected_blocked_contexts = 16
expected_integrable_contexts = 104
maximum_013_rows_read_for_execution_surface = 600000
maximum_run_local_014_execution_surface_rows = 50000
maximum_candidate_parquet_files = 1
maximum_output_bytes_per_stage = 12000000
```

---

## Authority Flags

```text
scale_c_execution_surface_construction_allowed = true
013_upstream_read_allowed_for_execution_surface = true
run_local_014_surface_creation_allowed = true
original_014_hash_integrity_check_allowed = true

sample_reselection_allowed = false
sample_manifest_mutation_allowed = false
013_direct_builder_input_allowed = false
builder_resolution_execution_allowed = false
information_object_formula_execution_allowed = false
market_state_integration_allowed = false
market_state_materialization_allowed = false
market_state_parquet_allowed = false
raw_quotes_read_allowed = false
quote_dependent_object_integration_allowed = false
run_local_014_surface_promotion_allowed = false
original_014_modification_allowed = false
official_market_state_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
```

---

## Closure Criteria

```text
sample_fingerprint_match = true
calendar_version_match = true
selected_instruments_missing = 0
selected_sessions_missing = 0
unexpected_instruments = 0
unexpected_sessions = 0
calendar_binding_failures = 0
session_boundary_mismatches = 0
early_close_boundary_failures = 0
fixed_utc_probe_calendar_as_current_authority = 0
source_coverage_failures = 0
conflicting_duplicate_groups = 0
candidate_surface_parquet_files_written = 1
builder_records_emitted = 0
information_object_formulas_executed = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
original_014_modified = false
determinism_failures = 0
authority_failures = 0
hard_validation_failures = 0
```

---

## Next Boundary

The next executable subgate, if this closes with restrictions, is:

```text
experimental_core_four_market_state_scale_c_builder_resolution_execution_authorization_v0_1
```

Still closed:

```text
builder/resolution execution until separate authorization consumes the surface manifest
Market State integration
Market State materialization
official Market State
production builder
downstream State consumption
dataset promotion
full-history execution
full-universe execution
quote-dependent object integration
operational promotion
```
