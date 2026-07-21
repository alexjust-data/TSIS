# 003 dataset_certification_matrix - Auditoria Rapida De Representacion

Status: `pass_01_discovery_review`
Date: `2026-07-20`

Primera pasada de descubrimiento. No certifica, no admite Objetos de Informacion, no promueve tablas y no autoriza consumo nuevo.

## Identidad

| Campo | Valor |
| --- | --- |
| `table_id` | `003` |
| `table_name` | `dataset_certification_matrix` |
| `dataset_id` | `dataset_certification_matrix_v0_1` |
| `maturity_level` | `validated_candidate` |
| `review_scope` | `pass_01_discovery_only` |

## Que Materializa

```text
Estado institucional de calidad, certificacion, scope y permiso de consumo de datasets.
```

Rol de la tabla:

```text
governance
quality
consumption_policy
```

## Ejes Detectados

| Eje | Lectura pass 01 |
| --- | --- |
| `information_object_family` | Representation Quality |
| `source_domain` | all governed sources |
| `temporal_resolution` | as_of |
| `institutional_role` | governance, quality, consumption_policy |

## Flujo Operativo

| Pregunta | Respuesta pass 01 |
| --- | --- |
| Que consume | status matrices, audit dossiers, quality reports |
| Que produce | dataset consumption gates and institutional status |
| Puede alimentar Market State | `yes_as_quality_gate_not_signal` |
| Puede alimentar Event State | `yes_as_quality_gate_not_signal` |

## Objetos De Informacion Candidatos

No estan admitidos. Solo quedan detectados para consolidacion posterior.

```text
Dataset Consumption Eligibility
Representation Quality State
```

## Modelos De Representacion Candidatos

```text
gate/verdict model
status matrix model
```

## Capacidades Derivables Relacionadas

```text
dataset gate lookup
root status lookup
quality verdict propagation
```

## Faltantes / Riesgo Principal

```text
Update when 013 v0_2 candidate promotion is decided.
```

## Decision De Primera Pasada

```text
keep_with_restrictions
```

## Evidencia Consultada

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\003_dataset_certification_matrix\003_dataset_certification_matrix.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
