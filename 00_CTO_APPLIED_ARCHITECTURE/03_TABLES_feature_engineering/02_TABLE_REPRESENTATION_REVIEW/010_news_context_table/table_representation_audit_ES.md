# 010 news_context_table - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `010` |
| `table_name` | `news_context_table` |
| `dataset_id` | `news_context_table_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Noticias, catalizadores y contexto informacional disponible por instrumento.
```

Rol de la tabla:

```text
external_context
event_source
as_of
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | External Context |
| `source_domain` | News |
| `temporal_resolution` | as_of;event_window |
| `institutional_role` | external_context, event_source, as_of |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | news/additional raw sources, identity matching |
| Que produce | PIT news/catalyst context and possible event sources |
| Puede alimentar Market State | `yes_as_news_context_profile` |
| Puede alimentar Event State | `yes_when_governed` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
News Context
Catalyst Context
News Recency
```

## Modelos De Representacion Candidatos

```text
news availability model
catalyst classification model
news recency model
```

## Capacidades Derivables Relacionadas

```text
news presence
news age
source type
topic/category
```

## Faltantes / Riesgo Principal

```text
Availability/as-of proof and event-source policy per vendor.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\010_news_context_table\010_news_context_table.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
