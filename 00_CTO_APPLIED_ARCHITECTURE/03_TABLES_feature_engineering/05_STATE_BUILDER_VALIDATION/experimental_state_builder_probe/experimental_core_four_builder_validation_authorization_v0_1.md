# Experimental Core Four Builder Validation Authorization v0.1

status: `authorized_for_experimental_probe_only`
phase: `Phase B - experimental builder validation`
effective_scope: `experimental_builder_validation_execution_core_four`

## Purpose

This artifact authorizes the first experimental execution of Information Object
builders for the four core Objects only:

```text
Trading Activity
Price Movement
Price Location / Structure
Volatility / Range State
```

The gate checks whether each Object can produce an experimental deterministic
Information Object resolution record from governed bounded inputs.

It does not build a Market State table, join Objects into State, write parquet
State outputs, authorize quote-dependent builders, promote datasets or authorize
production consumption.

## Authority

```text
bounded_sample_data_read_allowed = true
experimental_formula_execution_allowed = true
experimental_resolution_records_allowed = true
full_data_read_allowed = false
production_builder_authorized = false
state_materialization_allowed = false
state_consumption_authorized = false
market_state_integration_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
quote_dependent_builder_execution_authorized = false
writes_to_source_allowed = false
```

The authorization is valid only when the executable scope is provided by:

```text
configs/experimental_core_four_builder_validation_scope_v0_1.json
```

## Hard Limits

```text
maximum_objects = 4
maximum_instruments = 3
maximum_sessions_per_instrument = 2
maximum_decision_timestamps_per_session = 5
maximum_resolution_requests = 120
maximum_total_input_rows = 30000
full_scan_allowed = false
```

## Authorized Operations

The probe may:

```text
read only allowed columns declared in scope
select bounded source rows inside the run
apply closed-bar cutoff rules
apply selected price_view policy for 004
apply identical duplicate collapse policy for 014
execute formula rules declared in the scope
emit experimental Information Object resolution records inside the run directory
compute deterministic fingerprints
write validation reports inside the run directory
```

The probe may not:

```text
write to source datasets
repair or rewrite rows
perform full scans
execute quote-dependent builders
join Object records into a Market State row
materialize Market State or Event State
promote outputs or datasets
authorize production builder development
```

## Required Outputs

```text
core_four_builder_execution_manifest.json
builder_request_report.csv
capability_resolution_report.csv
selected_source_rows_report.csv
cutoff_enforcement_report.csv
duplicate_handling_report.csv
formula_validation_report.csv
builder_output_contract_report.csv
determinism_report.csv
builder_restrictions_report.csv
core_four_builder_validation_summary.json
core_four_builder_validation_findings.md
```

## Non-Claims

A passing gate does not claim full-universe correctness, full-history temporal
legality, production readiness, State materialization readiness or Market State
Integration readiness.
