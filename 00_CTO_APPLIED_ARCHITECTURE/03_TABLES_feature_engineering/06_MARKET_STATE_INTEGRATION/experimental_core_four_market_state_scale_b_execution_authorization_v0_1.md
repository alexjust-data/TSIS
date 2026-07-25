# Experimental Core Four Market State Scale B Execution Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_b_execution_scope_v0_1`

This authorization binds the bounded Scale B execution chain to the frozen governed-calendar sample emitted by `experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z`.

It authorizes only a non-production Scale B chain against that exact sample:

```text
run-local Scale B 014-derived execution surface construction
    -> builder/resolution
    -> integration
    -> candidate materialization
    -> independent physical validation
```

Each stage must use a separate run ID and consume the previous stage manifest. This document does not execute the chain.

---

## Frozen Sample Authority

```text
scale_b_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS
sample_preflight_run = experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z
sample_manifest_rows = 72
selected_instruments = 8
selected_sessions = 6
expected_resolution_records = 288
expected_blocked_contexts = 8
expected_integrable_contexts = 64
calendar_session_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
source_coverage_failures = 0
identity_failures = 0
stratification_failures = 0
scale_b_sample_fingerprint = 5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972
instrument_selection_fingerprint = df5e15c29024345267e867eae76c78764201325c1478791d3b7c30482a93f375
session_selection_fingerprint = c25cbd5bd9ba683cfe9fa6da028cfa40fe106c6618b66bbbe5302493773a2945
```

The execution must consume:

```text
runs/experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z/scale_b_sample_manifest.jsonl
```

The execution must fail closed if the observed sample fingerprint differs from `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`. Reselecting or mutating the sample is forbidden.

---

## Governed Calendar Authority

```text
accepted_calendar_binding_run = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
fixed_utc_probe_calendar_as_current_authority = false
```

Scale B may use `fixed_utc_probe_calendar_v0_1` only as historical lineage for older Scale A/probe evidence. It is not current temporal authority for this execution.

---

## Source Boundary

Allowed source aliases for the complete bounded chain:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
013_ohlcv_1m_quote_guarded
```

`013_ohlcv_1m_quote_guarded` is authorized only for the first subgate, a bounded run-local construction of a Scale B 014-derived execution surface. It is not authorized as a direct builder input, Market State input, materialization input or downstream input.

The future builder/resolution stage must consume `014_master_intraday_bar_table_candidate` via the run-local Scale B 014-derived execution surface emitted by the first subgate. The original 014 must not be modified or promoted.

Forbidden:

```text
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
requested_contexts = 72
maximum_requested_contexts = 96
required_objects_per_context = 4
expected_resolution_records = 288
maximum_resolution_records = 384
expected_blocked_contexts = 8
maximum_blocked_contexts = 16
expected_integrable_contexts = 64
maximum_integrated_candidate_records = 88
expected_physical_candidate_rows = 64
maximum_physical_candidate_rows = 88
selected_instruments = 8
selected_sessions = 6
maximum_source_market_data_rows_read_total_chain = 550000
maximum_013_rows_read_for_execution_surface = 250000
maximum_run_local_014_execution_surface_rows = 25000
maximum_candidate_parquet_files = 1
maximum_output_bytes_per_stage = 10000000
```

---

## Authority Flags

```text
scale_b_execution_authorized = true
scale_b_execution_surface_construction_allowed = true
builder_resolution_execution_allowed_for_scale_b = true
integration_execution_allowed_for_scale_b = true
candidate_materialization_allowed_for_scale_b = true
candidate_physical_validation_allowed_for_scale_b = true
candidate_parquet_output_allowed_for_scale_b = true

sample_reselection_allowed = false
sample_manifest_mutation_allowed = false
013_upstream_read_allowed_for_execution_surface = true
013_direct_builder_input_allowed = false
raw_quotes_read_allowed = false
quote_dependent_object_integration_allowed = false
run_local_014_surface_promotion_allowed = false
original_014_modification_allowed = false

official_market_state_allowed = false
official_state_table_write_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
```

---

## Closure Criteria

Scale B may close only if:

```text
sample_fingerprint_match = true
calendar_version_match = true
calendar_boundary_mismatches = 0
fixed_utc_probe_calendar_as_current_authority = 0
run_local_014_execution_surface_created = true
original_014_modified = false
013_direct_builder_input = false
resolution_records = 288
failed_contexts = 0
blocked_contexts_expected = 8
blocked_contexts_maximum = 16
integrated_candidate_records_expected = 64
materialized_candidate_rows_expected = 64
materialized_candidate_rows_maximum = 88
rejected_contexts_materialized_as_rows = 0
blocked_required_object_values_admitted = 0
duplicate_primary_keys = 0
duplicate_source_candidate_record_ids = 0
duplicate_materialized_state_candidate_ids = 0
missing_physical_columns = 0
extra_physical_columns = 0
schema_inference_from_sample = false
source_to_physical_value_mismatches = 0
lineage_content_mismatches = 0
restriction_mismatches = 0
fingerprint_mismatches = 0
roundtrip_mismatches = 0
semantic_rebuild_differences = 0
authority_failures = 0
hard_validation_failures = 0
```

---

## Next Boundary

The next executable subgate is:

```text
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1
```

Still closed:

```text
official Market State
production builder
downstream State consumption
dataset promotion
full-history execution
full-universe execution
quote-dependent object integration
operational promotion
Scale C historical bounded execution
```
