# Experimental Core Four Market State Scale B Builder Resolution Execution Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_b_builder_resolution_execution_scope_v0_1`

This authorization opens only the bounded non-production Scale B builder/resolution execution subgate. It does not execute builders.

It binds the future execution to the frozen Scale B sample and the accepted run-local 014-derived Scale B execution surface.

---

## Cardinality Authority

The frozen Scale B sample has 72 contexts, not 60. Therefore the authorized builder/resolution target is:

```text
requested_contexts = 72
required_objects_per_context = 4
expected_resolution_records = 288
expected_blocked_contexts = 8
expected_integrable_contexts = 64
```

The required object order is:

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
sample_run_id = experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z
sample_manifest_rows = 72
selected_instruments = 8
selected_sessions = 6
calendar_strata = 6
scale_b_sample_fingerprint = 5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972
instrument_selection_fingerprint = df5e15c29024345267e867eae76c78764201325c1478791d3b7c30482a93f375
session_selection_fingerprint = c25cbd5bd9ba683cfe9fa6da028cfa40fe106c6618b66bbbe5302493773a2945
```

The execution must consume:

```text
runs/experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z/scale_b_sample_manifest.jsonl
```

It must fail closed if the observed sample fingerprint differs from `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`. Reselecting or mutating the sample is forbidden.

---

## Surface Authority

```text
surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
surface_run_id = experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z
surface_rows = 8112
surface_parquet_sha256 = 883bc41d089e33671f2d6aac689b79976bd205a0ab979c74ed54bd0856465e7e
scale_b_execution_surface_fingerprint = dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa
surface_source_snapshot_fingerprint = 4a8562a166e8b145b499b6ac813880e67b6fb3e010ad77dbd2e91c7c2c17972b
```

The builder must read only this accepted run-local 014-derived surface for intraday values:

```text
runs/experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z/014_scale_b_execution_surface_candidate_v0_1.parquet
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

Every resolution record must preserve temporal lineage:

```text
calendar_id
calendar_version
calendar_row_fingerprint
session_open_utc
session_close_utc
session_type
is_early_close
```

The execution must fail closed on missing or multiple calendar row bindings.

---

## Source Boundary

Allowed source aliases:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
```

004 daily year boundary:

```text
004_master_daily_table allowed_years = 2024, 2025
2024 rows are authorized only to satisfy prior_20 daily history for frozen 2025-01-21 contexts.
This does not authorize additional sample dates, sample reselection, full-history daily reads or any 013 direct builder input.
```

For this Scale B subgate, `014_master_intraday_bar_table_candidate` is bound to the accepted run-local surface above.

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

## Scale B Temporal Semantics

The future execution must demonstrate:

```text
pre_bar -> current-session bar values blocked
after_last_sampled_bar != session_close
near/session-close contexts bounded by governed session close
early_close -> no bar after governed early close admitted
fixed_utc_fallback_uses = 0
```

The builder must not infer session close from absence of more bars in the surface.

---

## Required Outputs

```text
pre_manifest.json
heartbeat.json
scale_b_sample_manifest.jsonl
builder_request_report.csv
context_resolution_summary.csv
capability_resolution_report.csv
selected_source_rows_report.csv
calendar_binding_report.csv
cutoff_enforcement_report.csv
duplicate_handling_report.csv
formula_validation_report.csv
builder_output_contract_report.csv
determinism_report.csv
builder_restrictions_report.csv
core_four_resolution_records.jsonl
core_four_builder_validation_summary.json
final_manifest.json
readout.md
```

---

## Closure Criteria

```text
sample_fingerprint_match = true
surface_fingerprint_match = true
calendar_source_snapshot_fingerprint_match = true
requested_contexts = 72
required_objects_per_context = 4
resolution_records = 288
missing_object_records = 0
extra_object_records = 0
expected_blocked_contexts = 8
unexpected_blocked_contexts = 0
unexpected_resolved_blocked_contexts = 0
expected_integrable_contexts = 64
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
experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1
```

Still closed:

```text
Market State integration until a separate authorization consumes accepted resolution records
Market State materialization
Market State parquet
official Market State
production builder
downstream State consumption
dataset promotion
full-history execution
full-universe execution
quote-dependent object integration
surface reconstruction from 013
013 direct builder input
Scale C historical bounded execution
```
