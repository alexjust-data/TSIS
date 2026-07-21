# 005 corporate_actions_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `005` |
| `table_name` | `corporate_actions_table` |
| `dataset_id` | `corporate_actions_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Eventos corporativos y ajustes estructurales: splits, dividendos y ticker changes.
```

Rol de la tabla:

```text
instrument_context
corporate_event
lineage
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Instrument Context |
| `source_domain` | Reference |
| `temporal_resolution` | as_of;daily |
| `institutional_role` | instrument_context, corporate_event, lineage |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | reference/additional corporate action sources |
| Que produce | corporate action context and price adjustment lineage |
| Puede alimentar Market State | `yes_as_instrument_context` |
| Puede alimentar Event State | `yes_as_event_context_when_governed` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Corporate Action Context
Price Adjustment Context
Identity Lifecycle Change
```

## Modelos De Representacion Candidatos

```text
corporate event model
price comparability model
```

## Capacidades Derivables Relacionadas

```text
split context
dividend context
ticker-change lookup
```

## Faltantes / Riesgo Principal

```text
As-of availability policy for declared/effective action dates.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\005_corporate_actions_table\005_corporate_actions_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
