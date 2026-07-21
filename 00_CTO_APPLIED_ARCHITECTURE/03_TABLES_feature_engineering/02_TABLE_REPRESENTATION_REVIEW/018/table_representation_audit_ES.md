# 018 intraday_scanner_candidates_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `018` |
| `table_name` | `intraday_scanner_candidates_table` |
| `dataset_id` | `intraday_scanner_candidates_table_v0_1` |
| `maturity_level` | `specification_only` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Superficie de candidatos intradia/scanner para seleccionar donde mirar.
```

Rol de la tabla:

```text
candidate_surface
selection_governance
intraday_context
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context;Trading Activity |
| `source_domain` | OHLCV;Scanner |
| `temporal_resolution` | intraday_bar;session |
| `institutional_role` | candidate_surface, selection_governance, intraday_context |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 014/013 intraday bars, 004 daily context, scanner config |
| Que produce | candidate surface for inspection/event/state windows |
| Puede alimentar Market State | `optional_candidate_context_only` |
| Puede alimentar Event State | `candidate_surface_not_validated_event` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Intraday In-Play Candidate
Attention Activity Candidate
```

## Modelos De Representacion Candidatos

```text
scanner selection model
threshold/gate model
```

## Capacidades Derivables Relacionadas

```text
candidate selection
motion threshold
tradability threshold
scanner lineage
```

## Faltantes / Riesgo Principal

```text
Controlled build/materialization evidence and object admission for scanner-derived context.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\018.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
