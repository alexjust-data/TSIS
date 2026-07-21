# 007 event_windows_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `007` |
| `table_name` | `event_windows_table` |
| `dataset_id` | `event_windows_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Ventanas temporales gobernadas alrededor de eventos o candidatos.
```

Rol de la tabla:

```text
event_window_infrastructure
temporal_context
governance
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context |
| `source_domain` | Halts;News;Scanner |
| `temporal_resolution` | event_window |
| `institutional_role` | event_window_infrastructure, temporal_context, governance |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | source events, calendar, time policies |
| Que produce | event-relative windows for features, outcomes and state |
| Puede alimentar Market State | `conditional_event_proximity_only` |
| Puede alimentar Event State | `yes_primary_window_input` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Event Window Context
Event Relative Time
```

## Modelos De Representacion Candidatos

```text
event-relative window model
window eligibility model
```

## Capacidades Derivables Relacionadas

```text
pre-at-post windows
window eligibility
event-relative slicing
```

## Faltantes / Riesgo Principal

```text
Map window_role to state_role and consumption_legality downstream.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\007_event_windows_table\007_event_windows_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
