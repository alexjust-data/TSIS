# News / Catalyst Context - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `News / Catalyst Context`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = News / Catalyst Context
formal_admission_decision = accepted_with_restrictions
scientific_identity = accepted
scientific_identity_confidence = high
operational_readiness = accepted_with_restrictions
ontology_phase_status = active
phase_a_scope = formal_admission_only
phase_b_engineering_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
operational_mapping_required = true
operational_mapping_authorized_now = false
builder_validation_required = true
market_state_integration_required = true
```

Lectura:

```text
News / Catalyst Context queda admitido como Information Object de TSIS,
pero su consumo operativo queda bloqueado hasta congelar
TSIS Market Ontology v1 y reabrir Phase B.
```

Esta admision concede autoridad ontologica.
No concede autoridad operativa.

## 2. Scientific Identity

```text
scientific_identity = accepted
scientific_identity_confidence = high
```

Justificacion:

```text
News / Catalyst Context preserva una primary informational uncertainty
propia: si existe informacion externa disponible en t, cuan reciente es
y que contexto aporta sin introducir futuro.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
News / Catalyst Context = informacion externa publicada o disponible as-of
                          con fuente, attribution y temporalidad gobernada.

Event State = relacion temporal del contexto con un evento.
Fundamental Context = estructura PIT del instrumento.
Trading Activity = respuesta observable en participacion negociada.
Scanner Selection = superficie de seleccion, no verdad causal.
Outcome Layer = respuesta futura posterior a la noticia.
```

## 3. Approved Semantic Capability

```text
News / Catalyst Context debe representar contexto externo publicado
o disponible as-of con attribution policy y temporalidad gobernada.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
informacion externa disponible as-of, con fuente declarada,
timestamp de publicacion o disponibilidad, attribution policy,
cutoff legal en decision_timestamp y separacion frente a response futura.
```

## 4. Minimal Semantic Identity

`News / Catalyst Context` deja de ser `News / Catalyst Context`
si desaparece:

```text
1. informacion externa publicada o disponible;
2. timestamp de publicacion y/o disponibilidad as-of;
3. relacion con instrumento, evento o sesion;
4. attribution/source policy;
5. separacion entre observacion disponible e interpretacion futura.
```

No forman parte de su identidad minima:

```text
sentiment score no versionado;
novelty score no versionado;
categoria de catalizador no gobernada;
movimiento de precio posterior;
outcome de respuesta;
seleccion de scanner.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `news_presence_model` | `approved_as_core_candidate` | Core as-of context candidate for future Phase B mapping | Requiere source, attribution y as_of policy. No autoriza variable fisica ahora. |
| `news_freshness_model` | `approved_as_core_candidate` | Recency / lag context candidate | Requiere `published_utc` y/o `as_of_utc`; no usar disponibilidad posterior a t. |
| `article_count_model` | `conditionally_approved_context_model` | Coverage/intensity context | Ventana legal cerrada; no convertir presencia en causalidad sin evidencia. |
| `keyword_flag_model` | `restricted_extension_only` | Provisional catalyst/type proxy | Requiere keyword policy versionada. |
| `sentiment_model` | `blocked_until_versioned_model` | Research/extension candidate | Requiere modelo versionado, validation y leakage policy. |
| `novelty_model` | `blocked_until_versioned_model_and_baseline` | Research/extension candidate | Requiere modelo versionado, baseline y as-of governance. |
| `catalyst_category_model` | `blocked_until_governed_taxonomy` | Catalyst taxonomy candidate | No truth institucional sin taxonomia gobernada. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `future_news_response_model` | `outcome_only` | Respuesta futura del mercado a la noticia no puede ser input. |
| `scanner_news_selection_model` | `selection_surface_only` | Selecciona candidatos; no prueba contexto causal neutral. |
| `ungoverned_sentiment_model` | `rejected_until_versioned` | Sentiment sin modelo versionado no es evidencia gobernada. |
| `ungoverned_catalyst_label_model` | `rejected_until_taxonomy` | Categoria sin taxonomia no es verdad institucional. |
| `fundamental_event_model` | `move_to_fundamental_context_when_structural` | Si preserva estructura PIT del instrumento, pertenece a Fundamental Context. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. `published_utc` y `as_of_utc` seran obligatorios cuando apliquen.

3. No se podran usar noticias publicadas o disponibles despues de t.

4. Attribution policy sera obligatoria.

5. Source governance sera obligatoria antes de mapping.

6. Sentiment y novelty quedan bloqueados sin modelo versionado.

7. Catalyst category queda bloqueado sin taxonomia gobernada.

8. Article count debera usar ventana legal cerrada.

9. Scanner selection no puede entrar como variable causal neutral.

10. Response futura a la noticia queda en Outcomes.

11. Toda variable fisica debera pasar por Operational Mapping
    despues de congelar TSIS Market Ontology v1.
```

## 8. Authorized Consumers

Autorizados en esta decision:

```text
ontology_phase_formal_admission
cross_object_ontology_review
future_operational_mapping_design_after_ontology_freeze
research_planning
```

No autorizados todavia:

```text
production_market_state_builder
production_event_state_builder
canonical_schema_change
physical_state_materialization
feature_contract_promotion
dataset_promotion
operational_mapping_execution
builder_validation_execution
market_state_integration_execution
```

## 9. Required Next Artifacts

Requeridos durante Phase A:

```text
1. Formal Admissions de los demas Information Objects principales.

2. Cross-Object Ontology Review:
   TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

3. TSIS Market Ontology v1 Freeze.
```

Diferidos hasta Phase B:

```text
1. Operational Mapping de News / Catalyst Context.

2. Builder Validation de News / Catalyst Context.

3. Market State Integration de News / Catalyst Context.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se aprueba una nueva fuente news gobernada.
2. Se aprueba attribution policy canonica.
3. Sentiment se promueve con modelo versionado.
4. Novelty se promueve con modelo versionado y baseline.
5. Catalyst category obtiene taxonomia gobernada.
6. Cambia la frontera con Event State.
7. Cambia la frontera con Fundamental Context.
8. Se detecta uso de noticias posteriores a t.
9. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
10. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\news_catalyst_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\news_catalyst_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\news_catalyst_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\news_catalyst_context_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
