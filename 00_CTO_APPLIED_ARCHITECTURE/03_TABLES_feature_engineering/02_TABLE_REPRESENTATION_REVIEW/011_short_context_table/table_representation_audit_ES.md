# 011 short_context_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `011` |
| `table_name` | `short_context_table` |
| `dataset_id` | `short_context_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Contexto short interest/short volume por fuente, scope y lag.
```

Rol de la tabla:

```text
external_context
short_context
lagged_observable
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context;Trading Activity |
| `source_domain` | Short |
| `temporal_resolution` | as_of;daily |
| `institutional_role` | external_context, short_context, lagged_observable |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | short raw/review sources, identity/date references |
| Que produce | short-side context rows with lag/source semantics |
| Puede alimentar Market State | `yes_with_lag_policy` |
| Puede alimentar Event State | `yes_for_squeeze_context_with_lag` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Short-Side Context
Short Activity
Crowding Context
```

## Modelos De Representacion Candidatos

```text
short interest/activity model
source-lag model
```

## Capacidades Derivables Relacionadas

```text
short volume ratio
days to cover
short activity anomaly
```

## Faltantes / Riesgo Principal

```text
Borrow availability blocked unless real source exists; decide profile/core eligibility.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\011_short_context_table\011_short_context_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
