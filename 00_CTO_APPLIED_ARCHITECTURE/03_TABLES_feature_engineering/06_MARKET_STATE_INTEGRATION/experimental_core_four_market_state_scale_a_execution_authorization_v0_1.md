# Experimental Core Four Market State Scale A Execution Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `experimental_core_four_market_state_scale_a_execution_scope_v0_1`

This authorization binds the bounded Scale A execution to the frozen sample
emitted by `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z`.

It authorizes only the non-production Scale A chain against that exact sample:

```text
builder/resolution
    -> integration
    -> candidate materialization
    -> independent physical validation
```

Each stage must use a separate run ID and consume the previous stage manifest.
This document does not execute the chain.

---

## Frozen Sample Authority

```text
sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS
sample_manifest_rows = 60
selected_instruments = 8
selected_sessions = 5
expected_resolution_records = 240
expected_blocked_contexts = 8
expected_integrable_contexts = 52
duplicate_status_diversity_frozen_contexts = 5
scale_a_sample_fingerprint = 65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1
```

The execution must consume:

```text
runs/experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z/scale_a_sample_manifest.jsonl
```

The execution must fail closed if the observed sample fingerprint differs from
`65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1`. Reselecting or mutating the sample is forbidden.

---

## Source Boundary

Allowed source aliases:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
```

For this Scale A execution, the `014_master_intraday_bar_table_candidate` alias
is bound to the accepted run-local derived surface:

```text
runs/experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1_20260722T184904Z/014_scale_a_eligible_surface_candidate_v0_1.parquet
sha256 = e729bceab6bd75e891dcac9f6bbf5eefa9ed78c8b6ecb8c6be79f4bc535f955b
```

This does not promote the derived surface to official 014. `013` remains
forbidden as direct builder, integration, materialization or Market State input.

Forbidden:

```text
013_ohlcv_1m_quote_guarded
raw_quotes
quote-dependent object records
full-history market data
full-universe market data
production State tables
downstream feature stores
00_CTO/99_REFERENCE_LIBRARY
```

---

## Exact Limits

```text
requested_contexts = 60
maximum_requested_contexts = 80
required_objects_per_context = 4
expected_resolution_records = 240
maximum_resolution_records = 320
expected_blocked_contexts = 8
maximum_blocked_contexts = 16
expected_integrable_contexts = 52
maximum_integrated_candidate_records = 80
expected_physical_candidate_rows = 52
maximum_physical_candidate_rows = 80
maximum_source_market_data_rows_read = 250000
maximum_candidate_parquet_files = 1
maximum_output_bytes = 5000000
```

---

## Authority Flags

```text
scale_a_execution_authorized = true
builder_resolution_execution_allowed_for_scale_a = true
integration_execution_allowed_for_scale_a = true
candidate_materialization_allowed_for_scale_a = true
candidate_physical_validation_allowed_for_scale_a = true
candidate_parquet_output_allowed_for_scale_a = true

sample_reselection_allowed = false
sample_manifest_mutation_allowed = false
013_upstream_read_allowed = false
raw_quotes_read_allowed = false
quote_dependent_object_integration_allowed = false

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

Scale A may close only if:

```text
sample_fingerprint_match = true
resolution_records = 240
failed_contexts = 0
blocked_contexts <= 16
integrated_candidate_records = resolved_contexts
materialized_candidate_rows = integrated_candidate_records
materialized_candidate_rows <= 80
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
calendar_compatibility_failures = 0
authority_failures = 0
hard_validation_failures = 0
```

---

## Next Boundary

The next executable subgate is:

```text
experimental_core_four_market_state_scale_a_builder_resolution_execution
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
Scale B calendar-aware execution
Scale C historical bounded execution
```
