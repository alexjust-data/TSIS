# Fundamental Context - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Fundamental Context`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Fundamental Context
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
Fundamental Context queda admitido como Information Object de TSIS,
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
Fundamental Context preserva una primary informational uncertainty propia:
que caracteristicas fundamentales conocidas en t condicionan
la interpretacion del estado observable y que tan fresca o fiable
es esa informacion.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Fundamental Context = estructura economica, financiera o societaria
                      conocida point-in-time.

News / Catalyst Context = publicacion/catalizador externo disponible as-of.
Short-Side Context = short interest, borrow, locate o crowding con lag propio.
Liquidity = coste, disponibilidad y facilidad de negociar.
Broad Market Context = entorno externo de mercado.
Outcome Layer = respuesta futura o resultado posterior.
```

## 3. Approved Semantic Capability

```text
Fundamental Context debe representar contexto fundamental PIT/as-of
sin usar revisiones posteriores ni inferir outcomes.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
contexto fundamental conocido as-of, con fuente, periodo, timestamp,
filing lineage, politica de revision declarada y cutoff legal
en decision_timestamp.
```

## 4. Minimal Semantic Identity

`Fundamental Context` deja de ser `Fundamental Context` si desaparece:

```text
1. informacion fundamental o societaria point-in-time;
2. as_of o filing timestamp gobernado;
3. recencia o validez temporal;
4. separacion entre valores conocidos y revisiones posteriores;
5. formula/version para ratios derivados.
```

No forman parte de su identidad minima:

```text
price movement;
liquidity actual;
trading activity intradia;
short-side crowding;
news freshness;
outcomes futuros.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `filing_recency_model` | `approved_as_core_candidate` | Core PIT freshness candidate for future Phase B mapping | Requiere as_of, source y filing lineage. No autoriza variable fisica ahora. |
| `statement_value_model` | `conditionally_approved_context_model` | Fundamental value context candidate | Campo, periodo, source y revision policy deben estar gobernados. |
| `statement_recency_model` | `approved_as_core_candidate` | Statement freshness / recency context | Requiere periodo y filing lineage. |
| `fundamental_ratio_model` | `restricted_extension_only` | Derived fundamental context candidate | Requiere formula versionada y leakage policy. |
| `market_cap_model` | `blocked_until_shares_price_asof_policy` | Derived size context candidate | Requiere shares, price y as_of policy. |
| `float_pit_model` | `blocked_until_governed_PIT_source` | Capital structure candidate | Bloqueado sin fuente float PIT gobernada. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `post_revision_fundamental_model` | `rejected_as_leakage` | No usar revisiones posteriores como conocimiento en t. |
| `news_catalyst_model` | `move_to_news_catalyst_context` | Publicacion/catalizador externo pertenece a News Context. |
| `short_crowding_model` | `move_to_short_side_context` | Short interest/borrow/locate tienen fuente y lag propios. |
| `liquidity_cost_model` | `move_to_liquidity` | Coste/disponibilidad actual de negociar no es fundamental context. |
| `future_fundamental_response_model` | `outcome_only` | Respuesta futura a fundamentals es outcome/research, no input. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. PIT/as_of sera obligatorio.

3. No se podran usar revisiones posteriores.

4. Statement values requeriran periodo, source y filing lineage.

5. Ratios requeriran formula versionada.

6. Float PIT queda bloqueado sin fuente gobernada.

7. Market cap queda bloqueado hasta shares/price/as_of policy.

8. Fundamental Context debera mantenerse separado de
   News / Catalyst Context y Short-Side Context.

9. No se podran inferir outcomes desde revision posterior.

10. Toda variable fisica debera pasar por Operational Mapping
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
1. Operational Mapping de Fundamental Context.

2. Builder Validation de Fundamental Context.

3. Market State Integration de Fundamental Context.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se aprueba fuente float PIT gobernada.
2. Se aprueba shares/as_of policy para market cap.
3. Se aprueba una formula institucional de ratios fundamentales.
4. Cambia la frontera con News / Catalyst Context.
5. Cambia la frontera con Short-Side Context.
6. Cambia la politica de filing lineage o revision handling.
7. Se detecta uso de revisiones posteriores como input.
8. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
9. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\fundamental_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\fundamental_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\fundamental_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\fundamental_context_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
