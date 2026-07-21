# Broad Market Context - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Broad Market Context`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Broad Market Context
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
Broad Market Context queda admitido como Information Object de TSIS,
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
Broad Market Context preserva una primary informational uncertainty propia:
en que entorno general de mercado ocurre el estado del instrumento,
con que proxies observables y con que cobertura as-of.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Broad Market Context = entorno de mercado amplio observable as-of.

Price Movement = movimiento del instrumento individual.
Volatility / Range State = amplitud o dispersion del instrumento.
News / Catalyst Context = publicaciones o catalizadores externos.
Fundamental Context = estructura economica/societaria del instrumento.
Quality State = cobertura/validacion administrativa.
Outcome Layer = comportamiento futuro posterior.
```

## 3. Approved Semantic Capability

```text
Broad Market Context debe representar contexto de mercado amplio
observable as-of sin afirmar verdad macro o regimen no gobernado.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
contexto amplio observable as-of, con simbolo o proxy declarado,
timestamp, coverage policy, fuente declarada, cutoff legal
en decision_timestamp y separacion frente a verdad macro no gobernada.
```

## 4. Minimal Semantic Identity

`Broad Market Context` deja de ser `Broad Market Context` si desaparece:

```text
1. referencia observable de mercado amplio;
2. temporalidad as-of;
3. relacion contextual con el instrumento;
4. separacion entre proxy y verdad macro/regimen;
5. cobertura/calidad declarada.
```

No forman parte de su identidad minima:

```text
precio del instrumento individual;
news/catalyst especifico del instrumento;
fundamentals de la empresa;
outcome futuro;
regimen macro no observado.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `index_return_context_model` | `approved_as_core_candidate` | Core broad-market context candidate for future Phase B mapping | Retornos de mercado amplio as-of; no usar cierres finales antes de disponibilidad. No autoriza variable fisica ahora. |
| `index_range_context_model` | `approved_as_context_model` | Broad range/risk context candidate | Requiere timestamp, source y cutoff legal. |
| `risk_on_off_proxy_model` | `restricted_extension_pending` | Risk-on/off proxy candidate | Proxy, no verdad macro; requiere definicion y validation. |
| `market_regime_model` | `representation_model_pending` | Regime proxy candidate | No Objeto separado sin prueba de identidad en cross-object review. |
| `coverage_state_model` | `quality_context_only` | Coverage/interpretability context | No alpha por defecto; separar de Quality State cuando aplique. |
| `macro_economic_context_model` | `blocked_until_source_asof_policy` | Future macro/economic extension | Requiere fuente, calendario y as_of policy. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `instrument_price_movement_model` | `move_to_price_movement` | Movimiento del instrumento individual no es contexto amplio. |
| `instrument_specific_news_model` | `move_to_news_catalyst_context` | News/catalyst especifico del instrumento pertenece a News Context. |
| `company_fundamental_model` | `move_to_fundamental_context` | Estructura de la empresa pertenece a Fundamental Context. |
| `macro_truth_model_without_source` | `blocked_without_governance` | No afirmar regimen macro sin fuente, calendario y definicion gobernada. |
| `future_market_response_model` | `outcome_only` | Comportamiento futuro de mercado/instrumento es outcome. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. as_of sera obligatorio.

3. No se podran usar cierres finales del dia antes de estar disponibles.

4. Proxies de indice no podran declararse verdad macro.

5. Risk-on/off requerira definicion de proxy y validation.

6. Market Regime queda como modelo/proxy pendiente,
   no Objeto separado por defecto.

7. Coverage state debera separarse como calidad/contexto,
   no alpha por defecto.

8. Macro/economic context queda bloqueado sin fuente
   y calendario as-of gobernados.

9. Toda variable fisica debera pasar por Operational Mapping
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
1. Operational Mapping de Broad Market Context.

2. Builder Validation de Broad Market Context.

3. Market State Integration de Broad Market Context.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se aprueban indices/proxies canonicos de Broad Market Context.
2. Risk-on/off se promueve con definicion gobernada.
3. Market Regime se propone como Information Object independiente.
4. Coverage state cambia de quality/context a modelo causal.
5. Se aprueba fuente macro/economic as-of gobernada.
6. Cambia la frontera con Price Movement.
7. Cambia la frontera con Volatility / Range State.
8. Se detecta uso de cierre final no disponible en t.
9. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
10. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\broad_market_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\broad_market_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\broad_market_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\broad_market_context_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
