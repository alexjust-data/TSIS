# 002 expected_data_calendar - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `002` |
| `table_name` | `expected_data_calendar` |
| `dataset_id` | `expected_data_calendar_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Denominador esperado de existencia de datos por instrumento, sesion y dataset.
```

Rol de la tabla:

```text
coverage_infrastructure
quality
governance
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Market Context |
| `source_domain` | Reference;OHLCV |
| `temporal_resolution` | daily |
| `institutional_role` | coverage_infrastructure, quality, governance |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | 000 instrument identity, 001 market calendar, dataset policies |
| Que produce | expectedness rows for coverage and certification |
| Puede alimentar Market State | `yes_as_quality_context_only` |
| Puede alimentar Event State | `yes_as_quality_context_only` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Dataset Expectedness
Observability Coverage
```

## Modelos De Representacion Candidatos

```text
coverage denominator model
expected-vs-present model
```

## Capacidades Derivables Relacionadas

```text
expected data lookup
missingness interpretation
```

## Faltantes / Riesgo Principal

```text
Align expectedness with 013 v0_2 after promotion decision.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\002_expected_data_calendar\002_expected_data_calendar.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
