# Market Microstructure State - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Market Microstructure State`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Market Microstructure State
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
Market Microstructure State queda admitido como Information Object de TSIS,
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
Market Microstructure State preserva una primary informational uncertainty
propia: en que condicion observable de top-of-book y tape se encuentra
el mercado, y si esa condicion permite interpretar otros Objetos.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Market Microstructure State = condiciones observables de quote/tape
                              que afectan interpretabilidad.

Liquidity = coste, disponibilidad y facilidad de negociar.
Trading Activity = intensidad observable de participacion negociada.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
Halt Context = interrupciones regulatorias o de mercado.
Quality/Governance = cobertura, validacion y permisos administrativos.
```

## 3. Approved Semantic Capability

```text
Market Microstructure State debe representar condiciones observables
del top-of-book y tape sin absorber Liquidity, Trading Activity
ni Order Flow Pressure.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
estado observable de quotes o tape, con ventana temporal cerrada,
fuente observable declarada, cutoff legal en decision_timestamp
y gates de calidad suficientes para interpretar la observacion.
```

## 4. Minimal Semantic Identity

`Market Microstructure State` deja de ser `Market Microstructure State`
si desaparece:

```text
1. estado observable de quotes o tape;
2. condicion microestructural del top-of-book;
3. rol de interpretabilidad o contexto;
4. separacion frente a Liquidity, Trading Activity y Order Flow Pressure;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
coste/facilidad de negociar como pregunta primaria;
volumen negociado como intensidad;
signo;
agresion;
imbalance;
halts como source event;
L2/MBO sin fuente gobernada;
alpha;
outcome.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `two_sided_quote_state_model` | `approved_as_core_candidate` | Core microstructure interpretability candidate for future Phase B mapping | Requiere quote quality gates y ventanas cerradas. No autoriza variable fisica ahora. |
| `locked_crossed_state_model` | `approved_as_context_gate` | Microstructure quality/context candidate | Context/gate, no alpha por defecto. |
| `quote_activity_state_model` | `approved_as_extension` | Quote update / activity context | Requiere variante declarada; no confundir con Trading Activity. |
| `quote_staleness_lifetime_model` | `blocked_until_timestamp_sequence_policy` | Staleness/lifetime candidate | Requiere timestamp/sequence behavior gobernado. |
| `tape_integrity_context_model` | `quality_context_only` | Tape interpretability context | No convertir calidad en senal sin justificacion posterior. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `interruption_context_model` | `move_to_halt_context` | Halts/interruption son contexto de interrupcion, no microestructura continua core. |
| `spread_cost_model` | `move_to_liquidity_when_cost` | Spread como coste de cruce pertenece a Liquidity. |
| `depth_liquidity_model` | `move_to_liquidity_when_availability` | Depth como disponibilidad para negociar pertenece a Liquidity. |
| `ofi_or_aggressor_model` | `move_to_order_flow_pressure` | OFI, signed flow y aggressor imbalance introducen direccion/presion. |
| `L2_MBO_microstructure_model` | `blocked_without_governed_source` | No existe fuente L2/MBO gobernada. |
| `coverage_quality_model` | `move_to_quality_governance_when_administrative` | Coverage/validacion son gates, no estado microestructural economico por si solos. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Quotes y trades deberan estar disponibles <= decision_timestamp.

3. Ventanas microestructurales deberan estar cerradas.

4. Two-sided quote state requerira quote quality gates.

5. Locked/crossed y tape integrity viajaran como context/gate,
   no como alpha por defecto.

6. Staleness/lifetime queda bloqueado hasta timestamp sequence policy.

7. L2/MBO queda bloqueado hasta fuente gobernada.

8. Interruption context pertenece a Halt Context.

9. Spread/depth como coste/disponibilidad pertenecen a Liquidity.

10. OFI, signed flow y aggressor imbalance pertenecen a
    Order Flow Pressure.

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
1. Operational Mapping de Market Microstructure State.

2. Builder Validation de Market Microstructure State.

3. Market State Integration de Market Microstructure State.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Cambia la frontera con Liquidity.
2. Cambia la frontera con Trading Activity.
3. Cambia la frontera con Order Flow Pressure.
4. Cambia la frontera con Halt Context.
5. Locked/crossed pasa de context/gate a variable causal propuesta.
6. Se aprueba timestamp sequence policy para staleness/lifetime.
7. Se aprueba fuente L2/MBO gobernada.
8. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
9. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\market_microstructure_state_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\market_microstructure_state_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
