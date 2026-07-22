# Experimental Core Four Market State Scale A Sample Preflight Rerun Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `experimental_core_four_market_state_scale_a_sample_preflight_rerun_scope_v0_1`

This authorization opens only a rerun of the Scale A sample preflight after the
accepted eligible representation surface construction. It does not authorize
builders, Information Object resolution execution, Market State integration,
Market State materialization, Market State candidate parquet, production,
downstream consumption, promotion, full-history or full-universe execution.

---

## Authorized Gate

```text
gate = experimental_core_four_market_state_scale_a_sample_preflight_rerun
authorization = experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_a_sample_preflight_rerun_scope_v0_1.json
base_scale_a_authorization = experimental_core_four_market_state_scale_a_authorization_v0_1
remediation_run = experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184904Z
```

The rerun exists solely to freeze, or fail closed again on, the exact Scale A
sample requirement:

```text
requested_contexts = 60
required_instruments = 8
required_sessions = 5
required_objects_per_context = 4
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
```

---

## Accepted Remediation Input

```text
eligible_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS
eligible_instrument_pool = ACCEPTED
eligible_instruments_emitted = 13
bounded_014_rows = 91830
source_market_data_rows_read_by_construction = 221183
construction_authority_failures = 0
construction_hard_contract_failures = 0
construction_determinism_failures = 0
```

Accepted fingerprints:

```text
source_snapshot_fingerprint = 401e94fe156ae6161ac93bc528ef848dd7b1f433f003fa963d51a1249b99572b
bounded_014_candidate_surface_fingerprint = 71cb2d7e4f441800cf3fe1a8c8e129d83b93b02b24a8f6ec76732c56d10f98c9
eligible_instrument_pool_fingerprint = 57e22e7eb616c0682db1d094e19dff2b31e35ca23320ec1757acf4e19323853d
eligible_surface_fingerprint = 00fb613881825ac9053be98b0875379d9ee4dff8c784f7b9906061358298b0fa
bounded_014_candidate_surface_parquet_sha256 = e729bceab6bd75e891dcac9f6bbf5eefa9ed78c8b6ecb8c6be79f4bc535f955b
```

---

## Allowed Inputs

Allowed:

```text
004_master_daily_table
accepted run-local 014-derived candidate surface
accepted eligible_instrument_pool.json
source binding registry
column binding registry as governance reference only
Scale A authorization and scope references
```

The accepted run-local 014-derived candidate surface is consumed under the
`014_master_intraday_bar_table_candidate` semantic alias for this preflight
rerun only. This does not promote the derived surface to official 014 and does
not make `013` a direct input to Scale A.

Forbidden:

```text
013_ohlcv_1m_quote_guarded
raw_quotes
quote-dependent object records
builders
Information Object resolution outputs
Market State candidate records
Market State parquet
production State tables
downstream feature stores
00_CTO/99_REFERENCE_LIBRARY
```

---

## Authority Flags

```text
scale_a_sample_preflight_rerun_allowed = true
accepted_eligible_surface_read_allowed = true
accepted_bounded_014_surface_read_allowed = true

builder_execution_allowed_for_scale_a = false
integration_execution_allowed_for_scale_a = false
candidate_materialization_allowed_for_scale_a = false
candidate_parquet_output_allowed_for_scale_a = false
market_state_candidate_parquet_allowed = false
013_upstream_read_allowed = false

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

## Acceptance Criteria

The rerun may close `PASS_WITH_RESTRICTIONS` only if:

```text
sample_manifest_rows = 60
unique_selected_instruments = 8
unique_selected_sessions = 5
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
calendar_compatibility_failures = 0
identity_failures = 0
source_coverage_failures_in_frozen_sample = 0
duplicate_context_ids = 0
duplicate_semantic_contexts = 0
estimated_total_source_rows <= 250000
scale_a_sample_fingerprint_present = true
builders_executed = false
resolution_records_emitted = 0
integration_executed = false
materialization_executed = false
candidate_parquet_files_written = 0
```

If any hard preflight criterion fails, Scale A execution remains
`BLOCKED_NOT_STARTED`.

---

## Next Boundary

If this rerun passes, the only next allowed work is a separate bounded Scale A
execution authorization that consumes the exact emitted sample fingerprint.

Still closed:

```text
Scale A builder execution
Market State integration
Market State materialization
Market State candidate parquet
official Market State
production builder
downstream consumption
dataset promotion
full-history execution
full-universe execution
Scale B
Scale C
```
