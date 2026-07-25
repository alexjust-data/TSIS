# Experimental Core Four Market State Scale C Market State Integration Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_market_state_integration_execution_scope_v0_1`

This authorization opens only the Scale C non-materializing Market State integration execution gate. It consumes accepted Scale C core-four resolution records and may emit non-canonical Market State candidate JSONL records.

It does not authorize source market-data reads, surface reconstruction, parquet materialization, downstream State consumption, production builders, dataset promotion, full-history execution or full-universe execution.

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_scale_c_market_state_integration_execution
authorization = experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_c_market_state_integration_execution_scope_v0_1.json
source_builder_run = experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z
profile_id = market_state_core_four_intraday_experimental_v0_1
```

The gate may test only whether the already accepted Scale C resolution records can be assembled atomically into complete core-four Market State candidate records.

## 2. Frozen Input Authority

```text
resolution_record_count = 480
contexts_seen = 120
integrable_contexts = 104
blocked_contexts = 16
failed_contexts = 0

scale_c_sample_run_id = experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
scale_c_execution_surface_run_id = experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z
scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554
calendar_binding_run_id = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
```

The execution must fail before emitting candidate records if any binding does not match the source builder manifest or resolution records.

## 3. Expected Result

```text
input_resolution_records = 480
contexts_seen = 120
candidate_records_expected = 104
rejected_required_object_blocked_contexts_expected = 16
failed_contexts_expected = 0
blocked_values_admitted_expected = 0
source_market_data_rows_read_expected = 0
parquet_files_written_expected = 0
```

## 4. Authority

```text
source_row_reads_allowed = false
filesystem_market_data_reads_allowed = false
bounded_sample_market_data_read_allowed = false
full_data_read_allowed = false
013_direct_reads_allowed = false
surface_rebuild_allowed = false
sample_reselection_allowed = false
fixed_utc_probe_calendar_fallback_allowed = false
production_builder_authorized = false
state_materialization_allowed = false
parquet_write_allowed = false
downstream_consumption_authorized = false
dataset_promotion_authorized = false
candidate_jsonl_output_allowed = true
rejected_context_report_allowed = true
```

## 5. Next Gate

Only if this gate closes successfully may TSIS open a separate authorization for:

```text
experimental_core_four_market_state_scale_c_candidate_materialization_authorization_v0_1
```

That future gate must still be non-production unless a separate operational promotion authority is issued.
