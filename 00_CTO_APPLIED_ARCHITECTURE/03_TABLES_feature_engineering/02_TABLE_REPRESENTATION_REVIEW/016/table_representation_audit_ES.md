# 016 market_state_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `016` |
| `table_name` | `market_state_table` |
| `dataset_id` | `market_state_table_v0_1 / market_state_table_v0_1_candidate` |
| `maturity_level` | `candidate_materialized` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Estado observable del mercado en decision_timestamp construido desde Objetos admitidos.
```

Rol de la tabla:

```text
canonical_state
integration_layer
quality
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Multiple admitted Information Object Families |
| `source_domain` | multiple governed sources |
| `temporal_resolution` | decision_timestamp |
| `institutional_role` | canonical_state, integration_layer, quality |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 000-015, 018 optional, accepted mappings |
| Que produce | Market State rows/profiles for downstream consumption |
| Puede alimentar Market State | `target_table_itself_pending_mapping` |
| Puede alimentar Event State | `feeds_event_state_after_gating` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Market State
State Quality
```

## Modelos De Representacion Candidatos

```text
profiled state integration model
core plus extension model
```

## Capacidades Derivables Relacionadas

```text
legal as-of integration
profile selection
quality propagation
```

## Faltantes / Riesgo Principal

```text
Accepted Objects, representation models and profile mapping before official build.
```

## Decision De Primera Pasada

```text
redesign_required
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\016\016.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
