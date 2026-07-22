# Experimental State Builder Probe

Status: `experimental_core_four_integration_execution_passed_with_restrictions_v0_1`
Date: `2026-07-21`
Scope: `phase_b_non_production_resolution_probe`

Este directorio contiene el primer builder experimental de `TSIS Market
Ontology v1`.

No es un builder de produccion. No materializa `Market State`. No autoriza
consumo de State, cambios de schema, promocion de datasets ni lectura completa
de datos.

## Purpose

El probe comprueba si los 12 `Information Objects` congelados pueden recorrer
un circuito ejecutable no productivo de resolucion:

```text
Formal Admission
    -> Operational Mapping
        -> Builder Validation Design
            -> experimental resolution probe
```

Hasta ahora ha descubierto y cerrado con restricciones los gates de source
binding, schema, column binding, identidad, tiempo, grano, calidad, lineage,
core-four builder execution y aceptacion de resolution records.

## Files

```text
configs/experimental_state_builder_probe_v0_1.json
configs/experimental_source_binding_registry_v0_1.json
configs/experimental_column_binding_registry_v0_1.json
configs/experimental_bounded_sample_scope_v0_1.json
configs/experimental_bounded_grain_scope_v0_1.json
configs/experimental_bounded_quality_lineage_scope_v0_1.json
configs/experimental_core_four_builder_validation_scope_v0_1.json
experimental_bounded_sample_validation_authorization_v0_1.md
experimental_bounded_grain_validation_authorization_v0_1.md
experimental_bounded_quality_lineage_validation_authorization_v0_1.md
experimental_core_four_builder_validation_authorization_v0_1.md
experimental_state_builder_probe_core_four_builder_validation_readout_v0_1.md
experimental_core_four_resolution_record_acceptance_review_v0_1.md
experimental_core_four_resolution_record_acceptance_summary_v0_1.json
experimental_core_four_resolution_record_acceptance_context_report_v0_1.csv
experimental_core_four_resolution_record_acceptance_semantic_report_v0_1.csv
policies/
scripts/experimental_state_builder_probe.py
runs/
```

## Current Gate State

```text
contract_check = CLOSED_PASS
experimental_physical_source_binding = CLOSED_PASS
path_validation = PASS
experimental_physical_schema_validation = REEXECUTED_WITH_COLUMN_BINDINGS
experimental_logical_to_physical_binding = PASS_WITH_RESTRICTIONS
logical_column_resolution = PASS_WITH_RESTRICTIONS
schema_validation = PASS_WITH_RESTRICTIONS
bounded_identity_and_temporal_validation = CLOSED_PASS_WITH_RESTRICTIONS
bounded_grain_validation = CLOSED_PASS_WITH_RESTRICTIONS
bounded_quality_and_lineage_validation = CLOSED_PASS_WITH_RESTRICTIONS
quality_semantics_validation = CLOSED_PASS_WITH_RESTRICTIONS
lineage_validation = CLOSED_PASS_WITH_RESTRICTIONS
experimental_builder_validation_execution_core_four = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
quote_dependent_builder_execution = BLOCKED_PENDING_QUOTE_ORDERING_OR_ASOF
state_materialization = NOT_AUTHORIZED
production_builder = NOT_AUTHORIZED
```

## Reference Core-Four Builder Validation Run

```text
run_id = experimental_state_builder_probe_v0_10_20260721T193918Z
script_version = experimental_state_builder_probe_v0_10
mode = experimental_builder_validation_execution_core_four
overall_status = passed_core_four_builder_validation_with_restrictions
resolution_requests = 40
formula_rows = 170
formula_failures = 0
future_bar_leaks = 0
output_contract_failures = 0
nondeterministic_records = 0
```

Readout:

```text
experimental_state_builder_probe_core_four_builder_validation_readout_v0_1.md
```

## Reference Resolution Record Acceptance Review

```text
review_id = experimental_core_four_resolution_record_acceptance_review_v0_1
reference_run = experimental_state_builder_probe_v0_10_20260721T193918Z
review_status = CLOSED_PASS_WITH_RESTRICTIONS
records_reviewed = 40
contexts_reviewed = 10
context_consistency_failures = 0
semantic_equality_failures = 0
output_contract_failures = 0
determinism_failures = 0
cutoff_future_leaks = 0
blocked_records_with_diagnostic_partial_values = 6
```

## Downstream Core-Four Integration Execution

The accepted records were integrated in:

```text
../../06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/
```

Result:

```text
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
contexts_seen = 10
input_resolution_records = 40
candidate_records_emitted = 8
rejected_contexts = 2
rejected_required_object_blocked_contexts = 2
failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
source_market_data_rows_read = 0
parquet_files_written = 0
```

Readout:

```text
../../06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_readout_v0_1.md
```

## Active Findings

```text
004_master_daily_table:
    selected_price_view = split_normalized observed in bounded sample;
    promotion remains restricted until full-history price-view consistency validation.

014_master_intraday_bar_table_candidate:
    identical duplicate rows can be deterministically collapsed experimentally;
    conflicting duplicate rows would block core-four builder execution.

core_four_builder_validation:
    40 bounded resolution requests executed across the four core objects;
    8 expected pre-bar requests block unavailable inputs instead of inventing state.

core_four_integration_execution:
    candidate JSONL records are diagnostic only, not canonical Market State rows;
    object_atomicity rejected blocked pre-bar contexts and admitted no blocked values.

raw_quotes:
    as_of_utc remains unavailable pending governed quote availability contract;
    quote_ordering_key remains blocked because same-timestamp distinct quote states exist;
    blockers are quote-dependent, not core-four blockers.
```

## Authority

```text
experimental_builder_allowed = true_as_non_production_resolution_probe
core_four_builder_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
schema_metadata_read_allowed = true_metadata_only
bounded_sample_data_read_allowed = true_only_under_explicit_scope
full_data_read_allowed = false
state_materialization_allowed = false
```

Next possible gate:

```text
core_four_market_state_materialization_design
```

Not open:

```text
Liquidity builder execution
Market Microstructure builder execution
Order Flow Pressure builder execution
Market State parquet materialization
State consumption
production builder development
downstream State consumption
operational promotion
```
