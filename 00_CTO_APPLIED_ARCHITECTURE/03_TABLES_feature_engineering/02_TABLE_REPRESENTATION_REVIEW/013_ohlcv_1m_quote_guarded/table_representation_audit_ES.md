# 013 ohlcv_1m_quote_guarded - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `013` |
| `table_name` | `ohlcv_1m_quote_guarded` |
| `dataset_id` | `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Quote-guarded overlay y arbol candidato fisico para barras OHLCV 1m.
```

Rol de la tabla:

```text
intraday_observable
repair_overlay
quality_lineage
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Price Dynamics;Representation Quality |
| `source_domain` | OHLCV;Quotes |
| `temporal_resolution` | intraday_bar |
| `institutional_role` | intraday_observable, repair_overlay, quality_lineage |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | raw OHLCV 1m, quotes, repair manifests |
| Que produce | validated technical candidate tree for guarded 1m consumption |
| Puede alimentar Market State | `yes_indirect_after_014` |
| Puede alimentar Event State | `yes_indirect_after_014` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Intraday Bar Observability
Price Integrity State
```

## Modelos De Representacion Candidatos

```text
quote-guarded bar model
repair lineage model
```

## Capacidades Derivables Relacionadas

```text
guarded 1m OHLCV
repair delta replacement
validation lineage
```

## Faltantes / Riesgo Principal

```text
Promotion review/registry/policy finalization for v0_2_candidate.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\013_ohlcv_1m_quote_guarded_operational_reading.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
