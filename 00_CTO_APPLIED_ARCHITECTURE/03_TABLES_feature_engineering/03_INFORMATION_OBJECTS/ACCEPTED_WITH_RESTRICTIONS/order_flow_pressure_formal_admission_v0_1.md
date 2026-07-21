# Order Flow Pressure - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Order Flow Pressure`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Order Flow Pressure
formal_admission_decision = accepted_with_restrictions
scientific_identity = accepted
scientific_identity_confidence = high
operational_readiness = blocked_for_state_until_alignment_and_classifier
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
Order Flow Pressure queda admitido como Information Object de TSIS,
pero su consumo operativo queda bloqueado hasta congelar
TSIS Market Ontology v1, reabrir Phase B y disponer de
alignment, classifier y confidence policy gobernados.
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
Order Flow Pressure preserva una primary informational uncertainty propia:
si el flujo observable ejerce presion compradora o vendedora,
con que imbalance y con que confianza.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Order Flow Pressure = signo, agresion, imbalance
                      y consumo direccional inferido del flujo.

Trading Activity = intensidad observable no direccional por defecto.
Liquidity = coste, disponibilidad y facilidad de negociar.
Market Microstructure State = quote/tape state sin direccion por si mismo.
Price Movement = desplazamiento observable del precio.
Execution Outcomes = fills, slippage o impactos realizados posteriores.
```

## 3. Approved Semantic Capability

```text
Order Flow Pressure debe representar presion direccional del flujo
solo cuando existan alignment, classifier y confidence policy gobernados.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado capaz de inferir
signo, agresion, imbalance o consumo direccional desde trades y quotes,
con trade-quote alignment gobernado, side classifier versionado,
confidence policy, ventana cerrada y cutoff legal en decision_timestamp.
```

## 4. Minimal Semantic Identity

`Order Flow Pressure` deja de ser `Order Flow Pressure` si desaparece:

```text
1. direccion o signo inferido del flujo;
2. agresion, imbalance o consumo direccional;
3. trade-quote alignment o source policy;
4. confidence policy;
5. ventana cerrada legal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
actividad no direccional;
liquidez como coste o disponibilidad;
microstructure state sin direccion;
movimiento de precio sin atribucion de flujo;
outcome posterior;
classifier no versionado.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `bid_hit_ask_lift_model` | `accepted_conceptually_blocked_for_state` | Scientific core candidate | Bloqueado para State hasta trade-quote alignment gobernado. |
| `signed_flow_model` | `accepted_conceptually_blocked_for_state` | Core directional flow candidate | Bloqueado hasta side classifier versionado y confidence policy. |
| `aggressor_imbalance_model` | `accepted_conceptually_blocked_for_state` | Core imbalance candidate | Bloqueado hasta classifier, confidence y timestamp policy. |
| `ofi_l1_model` | `restricted_L1_extension_only` | Pressure extension candidate | Declarar L1-limited; requiere ordering policy. |
| `alignment_confidence_model` | `mandatory_support_model` | Required support model | Obligatorio para cualquier consumo responsable futuro. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `trade_count_activity_model` | `move_to_trading_activity` | Trade count mide intensidad, no presion direccional. |
| `total_volume_activity_model` | `move_to_trading_activity` | Volumen total no prueba signo/agresion. |
| `spread_depth_model` | `move_to_liquidity_when_cost_or_availability` | Spread/depth miden coste o disponibilidad, no presion. |
| `quote_state_model` | `move_to_market_microstructure_state_when_non_directional` | Quote state sin direccion pertenece a Microstructure. |
| `price_movement_inference_model` | `rejected_as_pressure_without_classifier` | Movimiento de precio no prueba agresion sin classifier/alignment. |
| `execution_outcome_model` | `move_to_execution_or_outcomes` | Fill, slippage o impacto realizado son ejecucion/outcome. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Trades y quotes deberan estar disponibles <= decision_timestamp.

3. Ventanas deberan estar cerradas.

4. State consumption queda bloqueado hasta trade-quote alignment gobernado.

5. State consumption queda bloqueado hasta side classifier versionado.

6. State consumption queda bloqueado hasta confidence policy.

7. Requiere timestamp/sequence validation.

8. OFI debera declararse L1-limited.

9. Order Flow Pressure no podra absorber Trading Activity
   no direccional.

10. Order Flow Pressure no podra absorber Liquidity
    ni Market Microstructure State.

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
state_consumption_before_alignment_and_classifier
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
1. Operational Mapping de Order Flow Pressure.

2. Builder Validation de Order Flow Pressure.

3. Market State Integration de Order Flow Pressure.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se aprueba trade-quote alignment gobernado.
2. Se aprueba side classifier versionado.
3. Se aprueba confidence threshold para State consumption.
4. Cambia la frontera con Trading Activity.
5. Cambia la frontera con Liquidity.
6. Cambia la frontera con Market Microstructure State.
7. OFI L1 se redefine como pressure, microstructure o extension separada.
8. Se detecta inferencia de pressure desde price movement sin classifier.
9. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
10. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\order_flow_pressure_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\order_flow_pressure_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
