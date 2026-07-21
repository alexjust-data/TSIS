# 009 fundamentals_asof_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `009` |
| `table_name` | `fundamentals_asof_table` |
| `dataset_id` | `fundamentals_asof_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Contexto fundamental point-in-time/as-of del instrumento.
```

Rol de la tabla:

```text
external_context
instrument_context
as_of
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Instrument Context |
| `source_domain` | Fundamentals;SEC |
| `temporal_resolution` | as_of |
| `institutional_role` | external_context, instrument_context, as_of |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | fundamentals/SEC/additional sources, identity |
| Que produce | PIT fundamental context |
| Puede alimentar Market State | `yes_as_external_context_profile` |
| Puede alimentar Event State | `yes_when_as_of_safe` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Fundamental Context
Capital Structure Context
```

## Modelos De Representacion Candidatos

```text
PIT fundamental model
capital structure model
```

## Capacidades Derivables Relacionadas

```text
float lookup
shares/market cap context
filing age
```

## Faltantes / Riesgo Principal

```text
Verify physical fields vs candidates and prove PIT availability.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\009_fundamentals_asof_table\009_fundamentals_asof_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
