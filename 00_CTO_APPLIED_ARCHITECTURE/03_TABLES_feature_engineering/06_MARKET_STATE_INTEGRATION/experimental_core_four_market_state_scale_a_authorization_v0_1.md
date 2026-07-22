# Experimental Core Four Market State Scale A Authorization v0.1

Status: `authorized_with_restrictions_v0_1`
Date: `2026-07-22`
Scope: `scale_a_multi_context_bounded_only`

This authorization opens the next bounded Scale A gate for the core-four Market
State candidate chain.

It authorizes only a future bounded multi-context execution. It does not
execute builders now, write parquet now, authorize production, create an
official Market State table, authorize downstream State consumption, run full
history, run full universe or promote any dataset.

---

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_scale_a_execution
authorization = experimental_core_four_market_state_scale_a_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_a_scope_v0_1.json
design = core_four_market_state_bounded_scaling_design_v0_1
design_contract = core_four_market_state_bounded_scaling_design_contract_v0_1
logical_profile_id = core_four_market_state_profile_v0_1
physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1
stage_id = core_four_market_state_scale_a_multi_context_bounded
```

Scale A tests whether the validated core-four architecture remains correct
when the number of contexts increases while the execution remains bounded and
non-production.

---

## 2. Exact Scale A Limits

```text
target_requested_contexts = 60
maximum_requested_contexts = 80
required_objects_per_context = 4

target_resolution_records = 240
maximum_resolution_records = 320

target_expected_blocked_contexts = 8
maximum_blocked_contexts = 16

target_integrated_candidate_records = 52
maximum_integrated_candidate_records = 80
maximum_physical_candidate_rows = 80

instrument_count = 8
session_count = 5
decision_case_family_count = 4

maximum_source_market_data_rows_read = 250000
maximum_candidate_parquet_files = 1
maximum_output_bytes = 5000000
```

The execution must maintain these identities:

```text
resolution_records = requested_contexts * 4
resolved_contexts + blocked_contexts + failed_contexts = requested_contexts
integrated_candidate_records = resolved_contexts
materialized_candidate_rows = integrated_candidate_records
failed_contexts = 0
```

The target count assumes:

```text
requested_contexts = 60
blocked_contexts = 8
integrated_candidate_records = 52
```

The maximum caps allow deterministic fallback replacement during sample
selection, but they do not authorize unbounded expansion.

---

## 3. Sample Strategy

Scale A must use a stratified bounded sample. It must not select contexts by
pure random draw.

Required strata:

```text
instrument_diversity
session_diversity
decision_case_diversity
duplicate_status_diversity
volume_diversity
range_diversity
early_intraday_vs_later_intraday_timestamps
accepted_contexts_and_expected_rejected_pre_bar_contexts
```

Decision case families:

```text
pre_first_observable_bar_expected_blocked
first_closed_bar_or_early_regular_intraday
mid_session_regular_intraday
after_last_sampled_bar_not_session_close
```

The `after_last_sampled_bar` case remains a sample-boundary stress case. It
must not be labeled as:

```text
after_session_close
market_close_state
final_session_state
```

---

## 4. Calendar Safety

Scale A is not a calendar-aware validation gate. However, it must not select
sessions where the fixed UTC probe calendar is known to be wrong.

Required guard:

```text
scale_a_calendar_policy = fixed_utc_probe_calendar_compatibility_guarded
scale_a_session_selection_excludes_calendar_mismatch_dates = true
```

The future execution may proceed only if every selected session satisfies:

```text
regular_open_utc = 13:30:00
regular_close_utc = 20:00:00
session_type = regular
early_close_indicator = false
holiday_or_closed_indicator = false
```

If a governed exchange session calendar exists before Scale A execution, it
must be used for the compatibility check. If it does not exist, the execution
must emit a `scale_a_calendar_compatibility_report` and fail closed for any
selected date whose compatibility cannot be demonstrated.

Scale A must not claim calendar-aware evidence. Scale B remains blocked until a
governed exchange session calendar is available and used as temporal authority.

---

## 5. Allowed Inputs

Allowed source aliases:

```text
004_master_daily_table
014_master_intraday_bar_table_candidate
```

Allowed governance/config references:

```text
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_source_binding_registry_v0_1.json
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_column_binding_registry_v0_1.json
05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_core_four_builder_validation_scope_v0_1.json
06_MARKET_STATE_INTEGRATION/configs/core_four_market_state_integration_execution_scope_v0_1.json
06_MARKET_STATE_INTEGRATION/configs/experimental_core_four_market_state_materialization_scope_v0_1.json
```

Forbidden inputs:

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

The future execution may read bounded source rows from `004` and `014` only as
needed to construct the authorized Scale A sample. It must not use Scale A as a
general source audit or full-history scan.

---

## 6. Authority

```text
experimental_core_four_market_state_scale_a_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_scale_a_execution = NOT_EXECUTED

builder_execution_allowed_for_scale_a = true
integration_execution_allowed_for_scale_a = true
candidate_materialization_allowed_for_scale_a = true
candidate_parquet_output_allowed_for_scale_a = true

official_market_state_allowed = false
official_state_table_write_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
quote_dependent_object_integration_allowed = false
```

The authorization is limited to one future bounded Scale A chain:

```text
builder/resolution
    -> integration
    -> candidate materialization
    -> independent physical validation
```

Each step must produce separate run IDs, manifests and readouts.

---

## 7. Required Future Outputs

The future Scale A execution must emit at least:

```text
pre_manifest.json
heartbeat.json
scale_a_sample_manifest.json
scale_a_calendar_compatibility_report.csv
builder_request_report.csv
resolution_record_manifest.json
integration_context_report.csv
market_state_candidate_records.jsonl
rejected_context_report.csv
materialization_manifest.json
core_four_market_state_scale_a_candidate_v0_1.parquet
schema_report.json
grain_report.csv
value_reconciliation_report.csv
lineage_content_report.json
restriction_report.csv
fingerprint_report.csv
roundtrip_report.csv
semantic_rebuild_report.json
authority_report.json
final_manifest.json
readout.md
```

The parquet filename must remain experimental candidate evidence:

```text
core_four_market_state_scale_a_candidate_v0_1.parquet
```

It must not be named or placed as an official `016` Market State table.

---

## 8. Acceptance Criteria

Scale A may close only if:

```text
requested_contexts >= 60
requested_contexts <= 80
resolution_records = requested_contexts * 4
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
authority_failures = 0
calendar_compatibility_failures = 0
hard_validation_failures = 0
```

The validation layer must preserve the proven independent checks from the
eight-row run, including source-to-physical value reconciliation and content
comparison for lineage JSON fields.

---

## 9. Preserved Restrictions

```text
candidate artifacts remain non-canonical
candidate artifacts remain not downstream-consumable
core-four profile is not complete TSIS Market State
quote-dependent objects remain excluded
Scale A is not calendar-aware validation
fixed UTC probe calendar requires compatibility guard
after_last_sampled_bar is not end_of_session
RVOL semantic naming must remain explicit
duplicate request impact must not be confused with physical duplicate groups
```

---

## 10. Next Boundary

After this authorization, the next allowed work is implementation/execution
planning for:

```text
experimental_core_four_market_state_scale_a_execution
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
