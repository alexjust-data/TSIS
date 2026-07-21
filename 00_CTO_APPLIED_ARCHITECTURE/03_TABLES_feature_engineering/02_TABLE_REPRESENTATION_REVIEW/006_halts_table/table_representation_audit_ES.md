# 006 halts_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `006` |
| `table_name` | `halts_table` |
| `dataset_id` | `halts_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Eventos de halt, suspension y resumption observados y gobernados.
```

Rol de la tabla:

```text
event
halt_context
microstructure_interruption
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Microstructure |
| `source_domain` | Halts |
| `temporal_resolution` | event_window;as_of |
| `institutional_role` | event, halt_context, microstructure_interruption |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | halts raw/source datasets, reference identity |
| Que produce | governed halt event/context rows |
| Puede alimentar Market State | `yes_when_decision_safe` |
| Puede alimentar Event State | `yes_as_event_source_context` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Halt Context
Regulatory Venue Interruption
```

## Modelos De Representacion Candidatos

```text
trading interruption model
halt classification model
```

## Capacidades Derivables Relacionadas

```text
halt presence
time since halt/resume
halt type
halt clustering candidate
```

## Faltantes / Riesgo Principal

```text
Split event source, event window use and outcome adjacency.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\006_halts_table\006_halts_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
