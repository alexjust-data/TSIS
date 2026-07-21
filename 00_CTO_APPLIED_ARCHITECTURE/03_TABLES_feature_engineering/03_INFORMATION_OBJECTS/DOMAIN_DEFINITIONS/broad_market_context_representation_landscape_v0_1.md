# Broad Market Context - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Broad Market Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Estado | Riesgo principal |
| --- | --- | --- | --- |
| `availability_asof_model` | Si el contexto era observable en t. | `required` | leakage o timestamp mal definido. |
| `presence_state_model` | Si el contexto/interrupcion esta activo. | `formula_defined_or_existing` | confundir ausencia de registro con ausencia real. |
| `recency_model` | Tiempo desde el contexto/interrupcion. | `formula_defined` | usar resume/post-event de forma ilegal. |
| `classification_model` | Tipo, regimen, halt reason o categoria. | `existing_or_candidate` | taxonomia incompleta. |
| `quality_context_model` | Cobertura del contexto. | `context_only` | convertir calidad en senal. |

## Modelos Bloqueados O No Listos

```text
as_of obligatorio; no confundir Market Regime con objeto separado sin prueba; proxies de indice no son verdad macro; coverage state es calidad/contexto, no alpha.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

## Evidencia TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\012_regime_context_table\table_representation_audit_ES.md
```
