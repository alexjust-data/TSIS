# Experimental Core Four Market State Scale B Candidate Materialization Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS`
Date: `2026-07-23`
Scope: `scale_b_market_state_candidate_jsonl_to_candidate_parquet_only`

This authorization opens only the bounded non-production Scale B candidate
materialization execution gate. It consumes the accepted Scale B Market State
candidate JSONL records from the integration run and may write one run-local
candidate parquet.

It does not authorize official Market State, production builders, source
market-data rereads, downstream State consumption, dataset promotion,
full-history execution or full-universe execution.

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_scale_b_candidate_materialization_execution
authorization = experimental_core_four_market_state_scale_b_candidate_materialization_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_b_candidate_materialization_scope_v0_1.json
source_integration_run = experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z
source_builder_run = experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z
```

## 2. Frozen Input Authority

```text
input_candidate_records = 64
input_rejected_contexts = 8
source_market_data_rows_read = 0
parquet_input_files = 0

scale_b_sample_fingerprint = 5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972
scale_b_execution_surface_fingerprint = dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
calendar_version = governed_exchange_session_calendar_xnys_v0_1
```

The materializer must fail if the integration summary, final manifest or JSONL
records do not match this authority.

## 3. Allowed Inputs

```text
market_state_candidate_records.jsonl
integration_context_report.csv
integration_value_manifest.csv
rejected_context_report.csv
scale_b_integration_summary.json
final_manifest.json
core_four_market_state_materialization_design_contract_v0_1.json
```

Allowed input root:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z
```

No physical market source root is authorized as input for this gate.

## 4. Authority

```text
experimental_candidate_parquet_output_allowed = true
candidate_parquet_filename = core_four_market_state_scale_b_candidate_v0_1.parquet
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

## 5. Expected Result

```text
input_candidate_records = 64
output_candidate_rows = 64
input_rejected_context_records = 8
candidate_parquet_files = 1
source_market_data_rows_read = 0
hard_validation_failures = 0
```

## 6. Next Gate

Only if this gate closes successfully may TSIS open:

```text
experimental_core_four_market_state_scale_b_candidate_physical_validation_authorization_v0_1
```

That future gate must independently validate the physical parquet and must not
authorize official Market State, downstream consumption or promotion.
