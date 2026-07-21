# 012 regime_context_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `012` |
| `table_name` | `regime_context_table` |
| `dataset_id` | `regime_context_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Contexto de regimen/mercado observable o as-of.
```

Rol de la tabla:

```text
market_context
external_context
regime
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context |
| `source_domain` | Market / Economic Context |
| `temporal_resolution` | as_of;daily;intraday |
| `institutional_role` | market_context, external_context, regime |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | market/economic sources, calendar/as-of policies |
| Que produce | regime context surface |
| Puede alimentar Market State | `pending_state_gate` |
| Puede alimentar Event State | `pending_event_gate` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Market Regime
Broad Market Context
```

## Modelos De Representacion Candidatos

```text
regime context model
broad market proxy model
```

## Capacidades Derivables Relacionadas

```text
index return
volatility proxy
risk-on/off state
```

## Faltantes / Riesgo Principal

```text
Current valid_for_state/ml flags need review before consumption.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\012_regime_context_table\012_regime_context_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
