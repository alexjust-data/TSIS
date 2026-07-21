# Trading Activity - Market State Integration v0.1

Status: `market_state_integration_design_v0_1`
Date: `2026-07-20`
Scope: `pre_materialization_state_profile_integration`

Este documento registra como debe integrarse `Trading Activity` en la
arquitectura de `Market State` una vez superada la validacion del builder.

No modifica el contrato canonico operativo.
No cambia schemas.
No cambia builders.
No materializa `market_state_table`.
No autoriza uso productivo.

## Phase Boundary Update

```text
artifact_role = pilot_vertical_artifact
TSIS_Market_Ontology_Phase = ACTIVE
Phase_B_Engineering = DEFERRED
physical_materialization_authorized = false
```

Esta integracion queda como diseno piloto. No autoriza integrar nuevos Objetos
en Market State operativo hasta completar la Formal Admission de todos los
Information Objects principales y congelar `TSIS Market Ontology v1`.
## 1. Integration Input

```text
information_object = Trading Activity
formal_admission_decision = accepted_with_restrictions
operational_mapping_decision = ready_for_builder_validation_design
builder_validation_status = design_ready_not_executed
```

Decision de integracion:

```text
market_state_integration_decision = proposed_pending_builder_validation
state_consumption_authorized = false
```

## 2. Integration Role

`Trading Activity` aporta a `Market State` esta informacion:

```text
intensidad observable de participacion negociada
```

Pregunta que permite responder dentro de State:

```text
Existe participacion negociada suficiente, normal o anomala
para interpretar el estado observable del mercado en t?
```

No debe aportar:

```text
direccion del precio;
coste de ejecucion;
quoted depth;
order flow direccional;
scanner selection;
outcomes futuros;
short-side delayed context;
float turnover no gobernado.
```

## 3. Market State Profiles

### market_state_core

Rol:

```text
Declarar disponibilidad y calidad del Objeto para el estado.
No absorber todas las variantes de Trading Activity.
```

Campos conceptuales candidatos:

```text
trading_activity__profile_status
trading_activity__quality_flag
trading_activity__as_of_utc
trading_activity__temporal_legality_flag
```

### market_state_daily_context

Rol:

```text
Contextualizar la sesion actual con actividad diaria cerrada
o baselines historicos prior-only.
```

Modelos:

```text
daily_absolute_participation_model
daily_relative_participation_model
```

Restriccion:

```text
No usar volumen final de la sesion actual antes del cierre.
```

### market_state_intraday

Rol:

```text
Representar actividad acumulada y/o por barra cerrada hasta
decision_timestamp.
```

Modelo inicial:

```text
intraday_absolute_accumulation_model
```

Este es el perfil recomendado para la primera validacion vertical.

### market_state_intraday_extension

Rol:

```text
Representar pace contra expectativa intradia declarada.
```

Modelo:

```text
intraday_pace_model
```

Restriccion:

```text
Requiere variant policy antes de uso.
```

### market_state_microstructure_extension

Rol:

```text
Representar intensidad de trades en ventanas cerradas cuando el
consumidor necesita detalle microestructural.
```

Modelo:

```text
trade_window_intensity_model
```

Restriccion:

```text
Perfil separado del core por coste, densidad y sensibilidad al ruido.
```

## 4. Event State Reuse

`Event State` no debe reconstruir otro `Trading Activity`.

Debe:

```text
1. referenciar un Market State valido;
2. conservar state_role;
3. declarar consumption_legality;
4. agregar ventanas event-specific solo si estan cerradas y autorizadas.
```

Regla:

```text
post_event puede ser informacion valida para investigacion,
pero no input decision-safe para una decision anterior o simultanea
al evento.
```

## 5. First Vertical Integration Path

Orden recomendado:

```text
1. Formal Admission
2. Operational Mapping
3. Builder Validation
4. Market State Integration
5. Operational contract promotion outside applied architecture
```

Primer perfil:

```text
profile_id = trading_activity_first_vertical_v0_1
target_state_profile = market_state_intraday
integration_status = pending_builder_validation_execution
```

## 6. Required Evidence Before Promotion

Antes de promover esta integracion a un contrato operativo, TSIS debe tener:

```text
1. Builder validation pass report.
2. Source table version resolution.
3. Temporal legality report.
4. Quality and coverage report.
5. Namespace / schema proposal.
6. Downstream impact note.
7. Changelog entry.
8. Operational authority update in the relevant 01_foundations contract.
```

## 7. Promotion Boundary

Este documento pertenece a:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
```

Por tanto, funciona como:

```text
applied_architecture_integration_design
```

No sustituye la autoridad operativa de:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

Cuando se promueva a ejecucion real, la decision debe reflejarse en
contratos, schemas, validators, manifests o status matrices operativos.

## 8. Preliminary Integration Decision

```text
market_state_integration_status = proposed
builder_validation_required = true
operational_contract_update_required = true
state_consumption_authorized = false
physical_materialization_authorized = false
```

## 9. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\trading_activity_builder_validation_v0_1.md
```
