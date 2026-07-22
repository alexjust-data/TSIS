# Experimental Core Four Market State Integration Execution Authorization v0.1

Status: `authorized_for_bounded_artifact_execution_v0_1`
Date: `2026-07-21`
Scope: `core_four_resolution_records_only`

This authorization opens the first experimental execution gate for integrating
accepted core-four Information Object resolution records into non-materialized
Market State candidate records.

It does not authorize production builders, source data reads, parquet
materialization, downstream State consumption or dataset promotion.

## 1. Authorized Gate

```text
gate = experimental_core_four_market_state_integration_execution
input_review = experimental_core_four_resolution_record_acceptance_review_v0_1
input_run = experimental_state_builder_probe_v0_10_20260721T193918Z
design_contract = core_four_market_state_integration_design_contract_v0_1
profile_id = market_state_core_four_intraday_experimental_v0_1
```

The only purpose of this gate is to test whether the already accepted
resolution records can be assembled into complete core-four Market State
candidate records under the integration design.

## 2. Allowed Inputs

Allowed input artifacts:

```text
core_four_resolution_records.jsonl
builder_output_contract_report.csv
cutoff_enforcement_report.csv
determinism_report.csv
selected_source_rows_report.csv
final_manifest.json
experimental_core_four_resolution_record_acceptance_summary_v0_1.json
experimental_core_four_resolution_record_acceptance_context_report_v0_1.csv
core_four_market_state_integration_design_contract_v0_1.json
```

Allowed input roots:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION
```

No physical market source root is authorized as input for this gate.

## 3. Authority

```text
source_row_reads_allowed = false
filesystem_market_data_reads_allowed = false
bounded_sample_market_data_read_allowed = false
full_data_read_allowed = false
production_builder_authorized = false
state_materialization_allowed = false
parquet_write_allowed = false
downstream_consumption_authorized = false
dataset_promotion_authorized = false
candidate_jsonl_output_allowed = true
rejected_context_report_allowed = true
```

## 4. Execution Limits

```text
maximum_contexts = 10
maximum_input_resolution_records = 40
maximum_candidate_records = 10
maximum_rejected_context_records = 10
maximum_output_value_rows = 1000
```

The probe must fail if these limits are exceeded.

## 5. Required Acceptance Rules

For each `context_id`, the probe must enforce:

```text
exactly 4 records per context
exactly the required core-four object ids
same semantic join key across records
same 004 daily evidence across records
same 014 selected bar evidence across records
no future_bar_leak
output contract already passed
determinism already passed
object atomicity required
blocked object values not admitted
```

Required object ids:

```text
trading_activity
price_movement
price_location_structure
volatility_range_state
```

## 6. Allowed Outputs

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
core_four_market_state_integration_execution_summary.json
core_four_market_state_integration_execution_findings.md
final_manifest.json
```

The candidate JSONL records are diagnostic integration outputs only. They are
not canonical Market State rows.

## 7. Expected Reference Result

For the reference v0.10 input run, expected shape is:

```text
contexts_seen = 10
candidate_records_expected = 8
rejected_required_object_blocked_contexts_expected = 2
market_state_rows_materialized = 0
```

## 8. Non-Authority

This authorization does not open:

```text
Market State parquet materialization
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

Only if this gate closes successfully may TSIS open a design gate for:

```text
core_four_market_state_materialization_design
```

That future gate must still be non-production unless a separate operational
promotion authority is issued.
