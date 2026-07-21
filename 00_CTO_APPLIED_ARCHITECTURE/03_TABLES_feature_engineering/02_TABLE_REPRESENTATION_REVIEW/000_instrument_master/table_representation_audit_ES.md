# 000 instrument_master - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `000` |
| `table_name` | `instrument_master` |
| `dataset_id` | `instrument_master_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Identidad canonica, universo y vigencia institucional de instrumentos.
```

Rol de la tabla:

```text
infraestructura
instrument_context
lineage
governance
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Instrument Context |
| `source_domain` | Reference |
| `temporal_resolution` | as_of |
| `institutional_role` | infraestructura, instrument_context, lineage, governance |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | reference raw,  identity sources |
| Que produce | instrument identity for all downstream joins |
| Puede alimentar Market State | `yes_as_identity_context` |
| Puede alimentar Event State | `yes_as_identity_context` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Instrument Identity
Universe Membership
Listing Status
```

## Modelos De Representacion Candidatos

```text
identity/lifecycle model
universe membership model
```

## Capacidades Derivables Relacionadas

```text
symbol resolution
identity as-of lookup
exchange/security classification
```

## Faltantes / Riesgo Principal

```text
Explicit object mapping for identity/universe; confirm registry promotion.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\000_instrument_master\000_instrument_master.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
