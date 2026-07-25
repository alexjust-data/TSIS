# Experimental Core Four Market State Scale C Candidate Materialization Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1`

This authorization opens only the bounded non-production Scale C candidate materialization execution gate. It consumes the accepted Scale C Market State candidate JSONL records from the integration run and may write one run-local candidate parquet.

It does not authorize official Market State, production builders, source market-data rereads, downstream State consumption, dataset promotion, full-history execution or full-universe execution.

## 1. Authorized Gate

```text
gate = experimental_scale_c_ms_candidate_materialization_v0_1
authorization = experimental_core_four_market_state_scale_c_candidate_materialization_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_c_candidate_materialization_scope_v0_1.json
source_integration_run = experimental_core_four_market_state_scale_c_market_state_integration_execution_v0_1_20260723T184533Z
source_builder_run = experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z
```

## 2. Frozen Input Authority

```text
input_candidate_records = 104
input_rejected_contexts = 16
source_market_data_rows_read = 0
parquet_input_files = 0
scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d
scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
calendar_version = governed_exchange_session_calendar_xnys_v0_1
```

The materializer must fail if the integration summary, final manifest or JSONL records do not match this authority.

## 3. Authority

```text
experimental_candidate_parquet_output_allowed = true
candidate_parquet_filename = core_four_market_state_scale_c_candidate_v0_1.parquet
source_market_data_reread_allowed = false
filesystem_market_data_reads_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
production_builder_allowed = false
state_consumption_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
official_market_state_allowed = false
official_state_table_write_allowed = false
```

## 4. Expected Result

```text
input_candidate_records = 104
output_candidate_rows = 104
input_rejected_context_records = 16
candidate_parquet_files = 1
source_market_data_rows_read = 0
hard_validation_failures = 0
```

## 5. Next Gate

Only if this gate closes successfully may TSIS open:

```text
experimental_core_four_market_state_scale_c_candidate_physical_validation_authorization_v0_1
```

That future gate must independently validate the physical parquet and must not authorize official Market State, downstream consumption or promotion.
