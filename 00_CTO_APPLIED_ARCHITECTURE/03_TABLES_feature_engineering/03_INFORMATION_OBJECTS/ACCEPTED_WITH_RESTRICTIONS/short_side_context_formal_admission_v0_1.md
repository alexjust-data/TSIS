# Short-Side Context - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Short-Side Context`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Short-Side Context
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
Short-Side Context queda admitido como Information Object de TSIS,
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
Short-Side Context preserva una primary informational uncertainty propia:
que condicion short-side conocida en t afecta el instrumento,
incluyendo crowding, presion, cobertura potencial, restricciones
o disponibilidad operativa para short.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Short-Side Context = contexto short conocido as-of,
                     con fuente, lag y semantica propia.

Trading Activity = intensidad negociada general o por ventana.
Order Flow Pressure = agresion o imbalance intradia inferido.
Fundamental Context = estructura economica/societaria PIT.
Liquidity = coste, disponibilidad y facilidad de negociar.
Outcome Layer = squeeze/failure/covering posterior.
```

## 3. Approved Semantic Capability

```text
Short-Side Context debe representar contexto short as-of
sin confundirse con Trading Activity, Order Flow Pressure
o outcomes posteriores.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
condicion short-side conocida as-of, con fuente declarada, lag declarado,
cutoff legal en decision_timestamp y separacion frente a activity
intradia general, aggressor flow y squeeze/failure posterior.
```

## 4. Minimal Semantic Identity

`Short-Side Context` deja de ser `Short-Side Context` si desaparece:

```text
1. fuente short o borrow/locate/SSR gobernada;
2. lag/as_of explicito;
3. semantica de crowding, presion o restriccion short;
4. separacion frente a actividad intradia general;
5. separacion frente a order flow/agresion intradia.
```

No forman parte de su identidad minima:

```text
volume general;
signed flow;
aggressor imbalance;
price movement;
future squeeze outcome;
borrow/locate no gobernado.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `days_to_cover_model` | `approved_as_core_candidate` | Core short crowding/capacity candidate for future Phase B mapping | Requiere source, lag y as_of policy. No autoriza variable fisica ahora. |
| `short_volume_ratio_model` | `conditionally_approved_context_model` | Short activity context candidate | No equivale a Trading Activity general ni aggressor flow. |
| `short_interest_z_model` | `restricted_extension_only` | Relative short crowding candidate | Requiere ventana, baseline y lag/source governance. |
| `borrow_availability_model` | `blocked_until_governed_source` | Borrow constraint candidate | Requiere fuente borrow gobernada. |
| `locate_state_model` | `blocked_until_governed_source` | Locate constraint candidate | Requiere fuente locate gobernada. |
| `ssr_state_model` | `blocked_until_source_and_rule_policy` | Short sale restriction candidate | Requiere fuente/regla gobernada y as_of policy. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `general_trade_volume_model` | `move_to_trading_activity` | Volumen general no preserva crowding/restriccion short. |
| `aggressor_short_flow_model` | `move_to_order_flow_pressure_when_intraday_signed` | Aggressor/signed flow intradia requiere classifier y pertenece a OFP. |
| `float_structure_model` | `move_to_fundamental_context` | Float/capital structure PIT es Fundamental Context salvo uso short-specific gobernado. |
| `short_squeeze_response_model` | `outcome_only` | Squeeze/failure/covering posterior es outcome. |
| `ungoverned_borrow_locate_model` | `blocked_without_source` | Borrow/locate sin fuente gobernada no puede representar el Objeto. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Lag/as_of sera obligatorio.

3. No se podran usar revisiones posteriores.

4. Short volume no podra tratarse como Trading Activity general
   ni como aggressor flow intradia.

5. Days-to-cover requerira fuente, lag y denominator gobernados.

6. Short interest z-score requerira ventana y baseline.

7. Borrow availability queda bloqueado sin fuente gobernada.

8. Locate state queda bloqueado sin fuente gobernada.

9. SSR queda bloqueado sin fuente/regla gobernada.

10. Squeeze, failure y covering posteriores quedan en Outcomes.

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
1. Operational Mapping de Short-Side Context.

2. Builder Validation de Short-Side Context.

3. Market State Integration de Short-Side Context.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se aprueba fuente short gobernada nueva.
2. Se aprueba fuente borrow gobernada.
3. Se aprueba fuente locate gobernada.
4. Se aprueba SSR source/rule policy.
5. Cambia la frontera con Trading Activity.
6. Cambia la frontera con Order Flow Pressure.
7. Cambia la frontera con Fundamental Context.
8. Se detecta uso de squeeze/failure posterior como input.
9. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
10. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\short_side_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\short_side_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\short_side_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\short_side_context_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
