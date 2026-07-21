# 017 event_state_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `017` |
| `table_name` | `event_state_table` |
| `dataset_id` | `event_state_table_v0_1 / event_state_table_v0_1_candidate` |
| `maturity_level` | `candidate_materialized` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Market State contextualizado respecto a evento/ventana con state_role y consumption_legality separados.
```

Rol de la tabla:

```text
canonical_event_state
event_relative_state
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context;Canonical Core Representation |
| `source_domain` | Events;Windows;State |
| `temporal_resolution` | event_window |
| `institutional_role` | canonical_event_state, event_relative_state |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 016 Market State, 007 windows, source events |
| Que produce | event-relative state rows |
| Puede alimentar Market State | `not_market_state_source` |
| Puede alimentar Event State | `target_table_itself_pending_gates` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Event State
Event Relative Context
```

## Modelos De Representacion Candidatos

```text
event-relative state model
state_role plus consumption_legality model
```

## Capacidades Derivables Relacionadas

```text
pre/at/post state role
consumption legality
relative timing
```

## Faltantes / Riesgo Principal

```text
Builders must emit consumption_legality; events need governed source/registry.
```

## Decision De Primera Pasada

```text
redesign_required
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\017\017.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
