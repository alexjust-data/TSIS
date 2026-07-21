# 001 market_calendar - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `001` |
| `table_name` | `market_calendar` |
| `dataset_id` | `market_calendar_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Infraestructura temporal canonica de sesiones, aperturas, cierres, festivos y early closes.
```

Rol de la tabla:

```text
temporal_infrastructure
market_context
governance
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context |
| `source_domain` | Reference |
| `temporal_resolution` | daily;intraday_session |
| `institutional_role` | temporal_infrastructure, market_context, governance |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | exchange calendar artifacts |
| Que produce | canonical session schedule and timestamp boundaries |
| Puede alimentar Market State | `yes_as_temporal_context` |
| Puede alimentar Event State | `yes_as_window_context` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Trading Session Context
Temporal Observability Boundary
```

## Modelos De Representacion Candidatos

```text
session availability model
calendar cutoff model
```

## Capacidades Derivables Relacionadas

```text
session lookup
timestamp-in-session classification
expected session denominator
```

## Faltantes / Riesgo Principal

```text
Mapping to session-context objects for 014/016.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\001_market_calendar\001_market_calendar.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
