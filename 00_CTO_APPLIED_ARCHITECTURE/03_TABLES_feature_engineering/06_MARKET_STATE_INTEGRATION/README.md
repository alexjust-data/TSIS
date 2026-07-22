# 06_MARKET_STATE_INTEGRATION

Status: `phase_b_core_four_materialization_execution_closed_v0_1`
Date: `2026-07-22`

Esta carpeta registra disenos y ejecuciones experimentales no productivas de
integracion de Information Objects admitidos en perfiles de `Market State`.

No es autoridad de produccion. No promociona schemas, builders,
materializaciones ni consumo downstream por si misma.

## Current Phase Boundary

```text
TSIS Market Ontology Phase = CLOSED
TSIS Market Ontology v1 = FROZEN
Phase B = OPEN
Market State Integration Expansion = CORE_FOUR_MATERIALIZATION_EXECUTION_BOUNDED
core_four_builder_validation = CLOSED_PASS_WITH_RESTRICTIONS
core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_candidate_parquet_output_allowed = true
production_builder_authorized = false
state_consumption_authorized = false
official_physical_materialization_authorized = false
official_parquet_materialization_authorized = false
downstream_consumption_authorized = false
official_market_state_authorized = false
```

Regla:

```text
No integrar nuevos Objetos en Market State operativo hasta que exista
Operational Mapping gobernado, Builder Validation aprobada, aceptacion de
resolution records, integration execution experimental y autorizacion separada
de materializacion/promocion.
```

## Pilot Artifact

La integracion de `Trading Activity` se conserva como:

```text
market_state_integration_design
proof_of_process
not_operational_authority
```

No autoriza schemas, builders, materializaciones ni consumo downstream.

## Core Four Integration Design

```text
profile_id = market_state_core_four_intraday_experimental_v0_1
core_four_market_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

Artefactos:

```text
core_four_market_state_integration_design_v0_1.md
core_four_market_state_integration_design_contract_v0_1.json
```

Reglas principales:

```text
join experimental = context_id
join semantico = instrument_id + ticker + session_date + decision_timestamp_utc + decision_case
request_id no es clave de join
object_atomicity = required
blocked object records = diagnostic_only_not_admitted
```

## Core Four Integration Execution

```text
execution_authorization = experimental_core_four_market_state_integration_execution_authorization_v0_1.md
execution_scope = configs/core_four_market_state_integration_execution_scope_v0_1.json
script = scripts/core_four_market_state_integration_probe.py
reference_run = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS
```

Resultado:

```text
contexts_seen = 10
input_resolution_records = 40
candidate_records_emitted = 8
rejected_contexts = 2
rejected_required_object_blocked_contexts = 2
failed_context_consistency = 0
failed_contract_or_determinism = 0
future_bar_leaks = 0
blocked_values_admitted = 0
admitted_value_rows = 136
source_market_data_rows_read = 0
parquet_files_written = 0
```

Readout:

```text
experimental_core_four_market_state_integration_execution_readout_v0_1.md
```

Run artifacts:

```text
runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/
```

The emitted `market_state_candidate_records.jsonl` file is diagnostic and
non-canonical. It is not a Market State table.

## Core Four Materialization Design

```text
logical_profile_id = core_four_market_state_profile_v0_1
physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
candidate_records_accepted_for_materialization_design = true
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
```

Artefactos:

```text
core_four_market_state_materialization_design_v0_1.md
core_four_market_state_materialization_design_contract_v0_1.json
```

El diseno separa el perfil logico core-four del schema fisico candidato y
clasifica las restricciones vivas por etapa: blockers de materializacion,
blockers de promocion, blockers de consumo operativo y restricciones
semanticas.

El diseno no ejecuto escrituras parquet. La autorizacion acotada posterior ya
existe y la ejecucion experimental ya cerro con restricciones sobre 8 records
candidatos. El parquet resultante sigue siendo candidato, no oficial y sin
consumo downstream.

## Core Four Materialization Authorization

```text
authorization = experimental_core_four_market_state_materialization_authorization_v0_1.md
scope = configs/experimental_core_four_market_state_materialization_scope_v0_1.json
experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS
experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS
experimental_candidate_parquet_output_allowed = true
candidate_parquet_filename = core_four_market_state_candidate_v0_1.parquet
schema_inference_from_sample = false
physical_value_columns_closed = true
json_field_serialization = canonical_utf8_json_string
state_output_fingerprint_payload = exact_non_circular
semantic_rebuild_determinism = required
byte_identical_parquet_rebuild = not_required
```

La autorizacion fijo la frontera de ejecucion. La ejecucion experimental
posterior consumio solo los 8 candidate JSONL records aceptados, genero un
unico parquet candidato no oficial y emitio evidencia de schema, grain,
lineage, restrictions, fingerprints, roundtrip y rebuild determinism.

## Core Four Materialization Execution

```text
script = scripts/core_four_market_state_materialization_probe.py
reference_run = experimental_core_four_market_state_materialization_v0_1_20260722T081155Z
readout = experimental_core_four_market_state_materialization_execution_readout_v0_1.md
experimental_core_four_market_state_materialization_execution = PASS_WITH_RESTRICTIONS
```

Resultado:

```text
input_candidate_records = 8
output_candidate_rows = 8
rejected_contexts_materialized_as_rows = 0
source_market_data_rows_read = 0
candidate_parquet_files_written = 1
candidate_parquet_bytes = 34097
physical_column_count = 40
physical_value_column_count = 17
schema_match = true
hard_validation_failures = 0
roundtrip_failures = 0
semantic_rebuild_differences = 0
semantic_rebuild_compare_field_count = 37
```

Run artifacts:

```text
runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/
```

The emitted `core_four_market_state_candidate_v0_1.parquet` file is bounded
experimental candidate evidence. It is not an official Market State table and
is not downstream-consumable.

## Preserved Restrictions

```text
governed_exchange_session_calendar_required_before_operational_integration
after_last_sampled_bar_is_not_end_of_session
trading_activity_rvol_20d_name_must_preserve_volume_to_time_over_prior_full_session_mean_semantics
duplicate_counts_are_request_impact_not_physical_group_counts
quote_dependent_objects_remain_blocked
```

## Next Gate

The next gate is not production execution or promotion. The next possible step is a physical validation review of the bounded candidate artifact:

```text
core_four_market_state_candidate_physical_validation = OPEN_NEXT_REVIEW_GATE
```

Still closed:

```text
official Market State parquet materialization = NOT_AUTHORIZED
production builder = NOT_AUTHORIZED
state consumption = NOT_AUTHORIZED
downstream ML/RL consumption = NOT_AUTHORIZED
full-history execution = NOT_AUTHORIZED
full-universe execution = NOT_AUTHORIZED
quote-dependent object integration = NOT_AUTHORIZED
official Market State = NOT_OPEN
operational promotion = NOT_AUTHORIZED
```
