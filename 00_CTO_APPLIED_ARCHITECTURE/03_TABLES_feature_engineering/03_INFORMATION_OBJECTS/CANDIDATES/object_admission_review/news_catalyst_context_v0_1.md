# News / Catalyst Context - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `News / Catalyst Context`
merece existir como `Information Object` independiente.

No constituye admision formal.
No autoriza variables para `Market State` ni `Event State`.
No selecciona implementacion fisica final.
No modifica schemas, builders, validators, manifests, contratos ni datasets.

## Nota De Estado

```text
Domain Definition = define el dominio semantico.
Representation Landscape = revisa modelos posibles.
Candidate Object Definition = fija el candidato trazable.
Object Admission Review = intenta romper el candidato antes de admitirlo.
Accepted Object = decision institucional posterior, no ejecutada aqui.
```

## Nota De Estado

```text
Domain Definition = define el dominio semantico.
Representation Landscape = revisa modelos posibles.
Candidate Object Definition = fija el candidato trazable.
Object Admission Review = intenta romper el candidato antes de admitirlo.
Accepted Object = decision institucional posterior, no ejecutada aqui.
```

Este documento aplica el criterio refinado de admision:

```text
Un Information Object no necesita evidencia exclusiva.

Necesita preservar una primary informational uncertainty
que no quede suficientemente representada por otros Objetos
sin perder su semantic capability o minimal semantic identity.
```

## 1. Jerarquia Metodologica

```text
Observable market phenomenon
    -> Phenomenon description
        -> Observable information to preserve
            -> Primary informational uncertainty
                -> Semantic capability
                    -> Candidate Information Object
                        -> Minimal semantic identity
                            -> Representation Model
                                -> Physical implementation
```

## 2. Candidate Object

### Observable Market Phenomenon

```text
Informacion externa se publica o queda disponible.
```

### Phenomenon Description

```text
Noticias, articulos, comunicados o catalizadores externos
pueden estar disponibles as-of y alterar la interpretacion
del instrumento, evento o sesion.
```

### Observable Information To Preserve

```text
Presencia, edad, disponibilidad as-of, cantidad, tipo provisional,
novedad o relevancia gobernada de noticias/catalizadores.
```

### Primary Informational Uncertainty

```text
Si existe informacion externa disponible en t,
cuan reciente es, que tipo de contexto aporta,
y si cambia la lectura del estado observable sin introducir futuro.
```

### Semantic Capability

```text
News / Catalyst Context debe representar contexto externo publicado
o disponible as-of con attribution policy y temporalidad gobernada.
```

### Candidate Information Object

```text
News / Catalyst Context
```

## 3. Minimal Semantic Identity

`News / Catalyst Context` deja de ser `News / Catalyst Context`
si desaparece:

```text
1. informacion externa publicada o disponible;
2. timestamp de publicacion y/o disponibilidad as-of;
3. relacion con instrumento, evento o sesion;
4. attribution/source policy;
5. separacion entre observacion disponible y interpretacion futura.
```

No necesita para conservar su identidad:

```text
sentiment score no versionado;
novelty score no versionado;
categoria de catalizador no gobernada;
movimiento de precio posterior;
outcome de respuesta;
seleccion de scanner.
```

## 4. Irreducibility Criterion

```text
News / Catalyst Context es irreducible si TSIS necesita preservar
contexto externo disponible as-of,
y esa informacion no queda suficientemente preservada por
Price Movement, Trading Activity, Fundamental Context,
Broad Market Context o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En News / Catalyst Context | En dominio vecino |
| --- | --- | --- |
| `published_utc` | temporalidad del catalizador | Event State como relacion temporal con evento |
| `article_count` | intensidad de cobertura externa | scanner/attention context si se usa para seleccion |
| `keywords` | proxy de tipo de noticia | catalyst taxonomy solo si esta gobernada |
| `sentiment_score` | extension model versionada | no verdad institucional sin modelo versionado |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Event State` | La noticia es evento, no objeto? | No. Event State contextualiza; News Context preserva informacion externa disponible. | `not_absorbed` |
| Absorb into `Fundamental Context` | Noticias son fundamentals? | No. Fundamentals son estructura PIT; news es publicacion/catalizador externo. | `not_absorbed` |
| Absorb into `Trading Activity` | Atencion se ve en volumen? | No. Actividad puede responder, pero no preserva la fuente externa. | `not_absorbed` |
| Absorb into `Outcome Layer` | La respuesta futura valida la noticia? | No como input. Respuesta posterior es outcome. | `outcome_separated` |
| Split `Sentiment` | Sentiment merece Objeto propio? | No por defecto. Es modelo versionado de representacion. | `representation_model` |
| Split `Catalyst Category` | Categoria merece Objeto propio? | No sin taxonomia gobernada y prueba de identidad. | `blocked_until_taxonomy` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `news_presence_model` | core candidate | Preserva si existe noticia disponible as-of. |
| `news_freshness_model` | core candidate | Edad desde publicacion/disponibilidad. |
| `article_count_model` | coverage/intensity candidate | Cuenta articulos en ventana legal. |
| `keyword_flag_model` | extension | Requiere keyword policy. |
| `sentiment_model` | blocked/extension | Requiere modelo versionado. |
| `novelty_model` | blocked/extension | Requiere modelo versionado y baseline. |
| `catalyst_category_model` | blocked until taxonomy | No truth sin taxonomia gobernada. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima es representar informacion externa disponible as-of,
con fuente, timestamp, attribution y cutoff legal.
```

## 9. Temporal Legality Constraints

```text
1. `published_utc` y `as_of_utc` son obligatorios.
2. No usar noticias publicadas o disponibles despues de t.
3. Attribution policy obligatoria.
4. Sentiment/novelty requieren modelo versionado.
5. Catalyst category requiere taxonomia gobernada.
6. Respuesta futura a la noticia es outcome, no input.
```

## 10. State Impact If Eventually Accepted

```text
market_state_news_extension:
    presence, freshness, article count, attribution.

research_only_until_ready:
    sentiment, novelty, catalyst category.

event_state_context:
    relacion temporal con eventos cuando este gobernada.
```

## 11. Preliminary Review Decision

```text
peer_review_result = survives_adversarial_review
formal_admission_decision = pending
```

### Scientific Identity

```text
scientific_identity = accepted_by_review
scientific_identity_confidence = high
recommended_scientific_admission_path = accepted
```

### Operational Readiness

```text
operational_readiness = accepted_with_restrictions
state_consumption_authorized = false
physical_variables_authorized = false
operational_mapping_required = true
```

Restricciones operativas recomendadas:

```text
1. Exigir as_of y attribution policy.
2. Bloquear sentiment/novelty sin modelo versionado.
3. Bloquear catalyst category sin taxonomia gobernada.
4. Separar news context de event outcome y scanner selection.
5. Mantener response futura como outcome.
```

## 12. Open Questions For Formal Admission

```text
1. Que fuentes news quedan gobernadas?
2. Que attribution policy es minima?
3. Article count entra en core o extension?
4. Catalyst category requiere taxonomia antes de State?
5. Sentiment/novelty quedan research-only hasta que version?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\news_catalyst_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\news_catalyst_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\news_catalyst_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

