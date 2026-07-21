# 015 microstructure_features_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `015` |
| `table_name` | `microstructure_features_table` |
| `dataset_id` | `microstructure_features_table_v0_1` |
| `maturity_level` | `candidate_materialized` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Representacion microestructural desde trades, quotes y ventanas/timestamps gobernados.
```

Rol de la tabla:

```text
microstructure
liquidity
trading_activity
quality
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Liquidity;Trading Activity;Market Microstructure |
| `source_domain` | Trades;Quotes |
| `temporal_resolution` | second;event_window |
| `institutional_role` | microstructure, liquidity, trading_activity, quality |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | raw trades, raw quotes, eligibility policies, 007 when event profile applies |
| Que produce | microstructure feature/context surface |
| Puede alimentar Market State | `yes_as_microstructure_extension` |
| Puede alimentar Event State | `yes_as_event_window_profile` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Liquidity
Trading Activity
Market Microstructure State
Order Flow Pressure
```

## Modelos De Representacion Candidatos

```text
spread/depth model
trade intensity model
quote condition model
signed flow model
```

## Capacidades Derivables Relacionadas

```text
spread
depth
quote rate
trade rate
size distribution
OFI candidates
```

## Faltantes / Riesgo Principal

```text
Split full/general profile vs event-window materialization profile.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\015.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
