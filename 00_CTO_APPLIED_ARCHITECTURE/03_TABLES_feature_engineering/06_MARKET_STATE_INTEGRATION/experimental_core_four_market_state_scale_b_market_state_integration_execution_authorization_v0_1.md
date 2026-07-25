# Experimental Core Four Market State Scale B Market State Integration Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS`
Date: `2026-07-23`
Scope: `scale_b_resolution_records_only`

This authorization opens only the Scale B non-materializing Market State
integration execution gate. It consumes accepted Scale B core-four resolution
records and may emit non-canonical Market State candidate JSONL records.

It does not authorize source market-data reads, surface reconstruction, parquet
materialization, downstream State consumption, production builders, dataset
promotion, full-history execution or full-universe execution.

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_scale_b_market_state_integration_execution
authorization = experimental_core_four_market_state_scale_b_market_state_integration_execution_authorization_v0_1
scope = configs/experimental_core_four_market_state_scale_b_market_state_integration_execution_scope_v0_1.json
source_builder_run = experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z
profile_id = market_state_core_four_intraday_experimental_v0_1
```

The gate may test only whether the already accepted Scale B resolution records
can be assembled atomically into complete core-four Market State candidate
records.

## 2. Frozen Input Authority

```text
resolution_record_count = 288
contexts_seen = 72
integrable_contexts = 64
blocked_contexts = 8
failed_contexts = 0

scale_b_sample_run_id =
experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z

scale_b_sample_fingerprint =
5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972

scale_b_execution_surface_run_id =
experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z

scale_b_execution_surface_fingerprint =
dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa

calendar_binding_run_id =
governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z

calendar_version =
governed_exchange_session_calendar_xnys_v0_1

calendar_source_snapshot_fingerprint =
8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
```

The execution must fail before emitting candidate records if any of these
bindings do not match the source builder manifest or resolution records.

## 3. Allowed Inputs

Allowed input artifacts from the accepted Scale B builder run:

```text
core_four_resolution_records.jsonl
context_resolution_summary.csv
builder_output_contract_report.csv
cutoff_enforcement_report.csv
determinism_report.csv
selected_source_rows_report.csv
core_four_builder_validation_summary.json
final_manifest.json
core_four_market_state_integration_design_contract_v0_1.json
```

Allowed input root:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION
```

No physical market source root is authorized as input for this gate.

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

## 5. Required Integration Rules

For each `context_id`, the execution must enforce:

```text
exactly 4 records per context
exactly the required core-four object ids
same semantic join key across records
same 004 daily evidence across records
same 014 selected bar evidence across records
same governed calendar binding across records
no future_bar_leak
output contract already passed
determinism already passed
object atomicity required
blocked object values not admitted
no partial candidate emitted
no substituted object emitted
```

Required object ids:

```text
trading_activity
price_movement
price_location_structure
volatility_range_state
```

## 6. Expected Result

```text
input_resolution_records = 288
contexts_seen = 72
candidate_records_expected = 64
rejected_required_object_blocked_contexts_expected = 8
failed_contexts_expected = 0
blocked_values_admitted_expected = 0
source_market_data_rows_read_expected = 0
parquet_files_written_expected = 0
```

## 7. Allowed Outputs

The execution may write only small experimental run artifacts under:

```text
06_MARKET_STATE_INTEGRATION\runs\
```

Allowed outputs:

```text
pre_manifest.json
heartbeat.json
market_state_candidate_records.jsonl
rejected_context_report.csv
integration_context_report.csv
integration_value_manifest.csv
scale_b_integration_summary.json
scale_b_integration_findings.md
final_manifest.json
readout.md
```

The candidate JSONL records are diagnostic integration outputs only. They are
not canonical Market State rows and are not downstream consumable.

## 8. Non-Authority

This authorization does not open:

```text
candidate parquet materialization
official Market State materialization
canonical schema creation
full-history execution
full-universe execution
production scheduling
downstream ML/RL consumption
event detection consumption
quote-dependent object integration
operational promotion
```

## 9. Next Gate

Only if this gate closes successfully may TSIS open a separate authorization
for:

```text
experimental_core_four_market_state_scale_b_candidate_materialization_authorization_v0_1
```

That future gate must still be non-production unless a separate operational
promotion authority is issued.
