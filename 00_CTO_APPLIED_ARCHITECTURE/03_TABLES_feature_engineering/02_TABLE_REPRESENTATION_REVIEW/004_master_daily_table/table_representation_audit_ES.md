# 004 master_daily_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `004` |
| `table_name` | `master_daily_table` |
| `dataset_id` | `master_daily_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Contexto diario canonico del instrumento para precio, actividad, rango y calidad diaria.
```

Rol de la tabla:

```text
market_information
daily_context
quality
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Price Dynamics;Trading Activity;Representation Quality |
| `source_domain` | OHLCV |
| `temporal_resolution` | daily |
| `institutional_role` | market_information, daily_context, quality |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 000, 001, 002, OHLCV daily, corporate actions |
| Que produce | daily context for intraday/state/outcome builders |
| Puede alimentar Market State | `yes_after_temporal_gating` |
| Puede alimentar Event State | `yes_after_temporal_gating` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Daily Price State
Overnight Dislocation
Daily Trading Activity
Daily Volatility Range
```

## Modelos De Representacion Candidatos

```text
daily OHLC reference model
gap model
daily participation model
range model
```

## Capacidades Derivables Relacionadas

```text
daily returns
gap percent
range percent
dollar volume
relative volume
```

## Faltantes / Riesgo Principal

```text
Accepted object mapping and intraday temporal cutoff for full-day fields.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\004_master_daily_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
