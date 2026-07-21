# Short-Side Context - Representation Landscape v0.1

Status: `representation_landscape_v0_1`
Date: `2026-07-20`
Scope: `post_domain_definition_pre_object_admission`

Este documento revisa modelos posibles para `Short-Side Context`.

No admite todavia ningun `Objeto de Informacion`.
No selecciona el modelo final.
No autoriza variables para `Market State` ni `Event State`.

## Paisaje De Modelos De Representacion 

| Modelo candidato | Que intenta medir | Estado | Riesgo principal |
| --- | --- | --- | --- |
| `availability_asof_model` | Si la informacion existe y era observable en t. | `required` | leakage por disponibilidad posterior. |
| `recency_model` | Edad o lag del contexto disponible. | `formula_defined_or_candidate` | lag mal interpretado. |
| `presence_intensity_model` | Presencia, frecuencia, magnitud o valor observable. | `existing_or_requires_variant` | convertir presencia en significado sin evidencia. |
| `classification_model` | Tipo, categoria o relevancia. | `candidate` | taxonomia/modelo no gobernado. |
| `derived_score_model` | score, z-score, sentiment, novelty, anomaly o ratio. | `requires_variant` | sobreajuste, versionado y leakage. |

## Modelos Bloqueados O No Listos

```text
lag/as_of obligatorio; no fusionar con Trading Activity; borrow/locate/SSR bloqueados sin fuente gobernada; short volume no equivale a agresion intradia; no usar como outcome.
```

## Decision Del Landscape

```text
decision = ready_to_define_candidate_object
```

Motivo:

```text
El dominio es coherente como contexto observable, pero requiere restricciones fuertes de as-of, lag, fuente y modelo.
```
