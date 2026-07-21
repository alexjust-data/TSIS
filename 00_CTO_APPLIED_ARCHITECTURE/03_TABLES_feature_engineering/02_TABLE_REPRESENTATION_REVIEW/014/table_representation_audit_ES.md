# 014 master_intraday_bar_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `014` |
| `table_name` | `master_intraday_bar_table` |
| `dataset_id` | `master_intraday_bar_table_v0_1 / v0_2_candidate_quote_guarded` |
| `maturity_level` | `candidate_materialized` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Representacion intradia basada en barras cerradas, price views, calidad y contexto de sesion.
```

Rol de la tabla:

```text
market_information
intraday_bar
quality
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Price Dynamics;Trading Activity;Representation Quality |
| `source_domain` | OHLCV |
| `temporal_resolution` | intraday_bar |
| `institutional_role` | market_information, intraday_bar, quality |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 013, 001, 004, 005, quality policies |
| Que produce | intraday bar representation surface for state/scanner/research |
| Puede alimentar Market State | `yes_as_intraday_profile_after_mapping` |
| Puede alimentar Event State | `yes_for_event_windows_after_gating` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Intraday Price Dynamics
Intraday Position
Intraday Trading Activity
Intraday Volatility
```

## Modelos De Representacion Candidatos

```text
bar return/slope model
session reference model
volume pace model
range model
```

## Capacidades Derivables Relacionadas

```text
bar return
range
VWAP
distance to references
volume pace
```

## Faltantes / Riesgo Principal

```text
Full post-013 v0_2 build/rebuild decision and accepted object mapping.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\014.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
