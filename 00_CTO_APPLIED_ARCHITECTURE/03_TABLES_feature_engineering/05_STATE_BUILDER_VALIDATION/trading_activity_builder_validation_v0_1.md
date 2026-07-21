# Trading Activity - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-20`
Scope: `pre_implementation_validation_plan`

Este documento define la validacion necesaria para comprobar si el
Information Object `Trading Activity` puede recorrer el pipeline:

```text
Formal Admission
    -> Operational Mapping
        -> Builder Resolution
            -> Market State profile
```

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## Phase Boundary Update

```text
artifact_role = pilot_vertical_artifact
phase_b_ratification =
  trading_activity_builder_validation_phase_b_ratification_v0_1.md
TSIS_Market_Ontology_v1 = FROZEN
Phase_B_Engineering = OPEN_FOR_GOVERNED_BUILDER_VALIDATION
production_builder_development_authorized = false
state_consumption_authorized = false
```

Esta validacion queda como diseno piloto ratificado por el artefacto indicado
arriba. Sigue sin autorizar desarrollar ni ejecutar builders de produccion,
schemas, materializaciones ni consumo de State.

## 1. Validation Target

```text
information_object = Trading Activity
formal_admission = accepted_with_restrictions
operational_mapping = ready_for_builder_validation_design
validation_target = first_vertical_profile
```

Perfil a validar primero:

```text
profile_id = trading_activity_first_vertical_v0_1
profile_role = market_state_intraday_minimum
```

Modelos incluidos:

```text
daily_relative_participation_model
intraday_absolute_accumulation_model
```

## 2. Pass / Fail Principle

La validacion no debe preguntar:

```text
hay columnas de volumen disponibles?
```

Debe preguntar:

```text
puede el builder resolver legalmente la semantic capability
de Trading Activity para un decision_timestamp concreto?
```

Condicion de exito:

```text
Para un instrumento y decision_timestamp, el builder puede resolver
un perfil minimo de intensidad de participacion negociada usando
solo evidencia observable, temporalmente legal y trazable.
```

## 3. Required Resolution Gates

### Gate 1 - Object Governance

```text
input:
  Trading Activity

expected:
  formal_admission_decision = accepted_with_restrictions
  scientific_identity = accepted
  operational_mapping_exists = true
  state_consumption_authorized = false
```

Pass condition:

```text
El builder reconoce el Objeto como admitido con restricciones,
pero no lo trata como consumible sin perfil validado.
```

### Gate 2 - Profile Selection

```text
requested_profile = trading_activity_first_vertical_v0_1
```

Pass condition:

```text
El builder selecciona solo los modelos aprobados para el perfil:
daily_relative_participation_model
intraday_absolute_accumulation_model
```

Fail condition:

```text
El builder incorpora por defecto scanner thresholds,
signed flow, aggressor imbalance, trade size distribution
o true float turnover.
```

### Gate 3 - Capability Resolution

Capacidades requeridas:

```text
daily__volume_20d_avg
daily__rvol_20d
intraday__bar_volume
intraday__session_volume_to_time
```

Capacidades opcionales:

```text
daily__dollar_volume
intraday__bar_transaction_count
intraday__session_dollar_volume_to_time
```

Pass condition:

```text
Todas las capacidades requeridas resuelven a una variable candidata,
una tabla fuente y una regla temporal.
```

### Gate 4 - Source Table Resolution

Fuentes esperadas:

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

Fuentes no permitidas en el primer perfil:

```text
015_microstructure_features_table_candidate
018_intraday_scanner_candidates_table
future outcome tables
short-side delayed sources
float PIT sources no gobernadas
```

Pass condition:

```text
El builder puede explicar por que cada fuente se usa o se excluye.
```

### Gate 5 - Temporal Legality

Reglas obligatorias:

```text
1. `daily__rvol_20d` de la sesion actual solo despues del cierre.
2. Baselines diarios usan sesiones previas validas.
3. Barras intradia usan solo barras cerradas.
4. `session_volume_to_time` usa solo barras con cierre legal.
5. No hay outcomes futuros.
6. No hay selection surface causal neutral desde 018.
```

Pass condition:

```text
Cada valor puede demostrar `as_of`, source/cutoff y disponibilidad
legal en decision_timestamp.
```

### Gate 6 - Output Namespace

Los aliases fisicos finales no quedan autorizados aqui, pero cualquier
salida de validacion debe mantener namespace semanticamente estable:

```text
trading_activity__*
```

Pass condition:

```text
Ningun campo de Trading Activity queda nombrado como generic volume
sin ownership semantico.
```

### Gate 7 - Quality And Lineage

El perfil debe transportar:

```text
source_table_id
source_dataset_version
representation_profile_version
component_as_of_utc
component_quality_flag
temporal_legality_flag
```

Pass condition:

```text
La fila de State puede ser auditada hasta fuente, modelo,
perfil y regla temporal.
```

## 4. Negative Tests

La validacion debe fallar si:

```text
1. Usa volumen final diario de la misma sesion antes del cierre.
2. Usa scanner selection como actividad causal.
3. Usa signed/aggressor variables bajo Trading Activity core.
4. Usa post-event window como input decision-safe.
5. Usa float turnover sin float PIT gobernado.
6. Une 014 por timestamp ambiguo sin regla de cierre de barra.
7. Pierde lineage de fuente o version.
8. No puede distinguir required vs optional capabilities.
```

## 5. Validation Evidence To Produce Later

Cuando se ejecute esta validacion, debe producir como minimo:

```text
validation_run_id
validation_timestamp_utc
code_commit
mapping_doc_version
input_profile_id
source_table_versions
sample_instruments
sample_decision_timestamps
pass_fail_matrix
temporal_legality_report
quality_flag_report
missing_capabilities_report
final_decision
```

Si la ejecucion es larga, debe cumplir:

```text
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
```

## 6. Preliminary Builder Decision

```text
builder_validation_status = design_ready_not_executed
builder_change_authorized = false
state_consumption_authorized = false
market_state_integration_decision = pending_validation
```

Lectura:

```text
El recorrido vertical esta suficientemente especificado para disenar
una validacion, pero todavia no hay evidencia de ejecucion.
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
