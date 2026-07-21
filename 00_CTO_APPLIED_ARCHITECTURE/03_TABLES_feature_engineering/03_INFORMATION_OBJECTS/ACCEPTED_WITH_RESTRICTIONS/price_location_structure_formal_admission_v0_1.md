# Price Location / Structure - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Price Location / Structure`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Price Location / Structure
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
Price Location / Structure queda admitido como Information Object de TSIS,
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
Price Location / Structure preserva una primary informational uncertainty
propia: donde esta situado el precio frente a referencias estructurales
legalmente conocidas en t.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Price Location / Structure = localizacion contextual del precio
                             frente a anchors legales.

Price Movement = cambio, direccion, intensidad o persistencia del precio.
Volatility / Range = amplitud, dispersion o inestabilidad del precio.
Trading Activity = intensidad observable de participacion negociada.
Liquidity = facilidad, coste, disponibilidad o impacto de negociar.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
Outcome Layer = future extrema, future returns, MFE y MAE.
```

## 3. Approved Semantic Capability

```text
Price Location / Structure debe ser capaz de representar
la posicion contextual del precio frente a referencias estructurales
legalmente conocidas en decision_timestamp.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que mida
posicion del precio observable en t contra una referencia estructural
declarada, con fuente observable declarada, cutoff legal en
decision_timestamp y sin depender de anchors finales futuros
ni labels de estrategia.
```

## 4. Minimal Semantic Identity

`Price Location / Structure` deja de ser `Price Location / Structure`
si desaparece:

```text
1. precio observable en t;
2. referencia estructural o anchor legalmente conocido;
3. distancia, proximidad o coordenada relativa contra esa referencia;
4. separacion entre localizacion actual y movimiento temporal;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
direccion del cambio;
velocidad o aceleracion;
persistencia direccional;
amplitud o dispersion como fenomeno principal;
volumen;
participacion negociada;
spread;
depth;
coste de ejecucion;
agresion compradora o vendedora;
scanner selection;
pattern labels;
future HOD / LOD;
future extrema;
future returns;
MFE;
MAE.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `session_anchor_location_model` | `approved_as_core_candidate` | Core semantic capability candidate for future Phase B mapping | Solo contra session open o segment anchors legalmente conocidos. No autoriza variable fisica ahora. |
| `prior_close_location_model` | `approved_with_asof_restriction` | Core / daily-intraday bridge candidate | `prior_close` debe proceder de sesion previa conocida as-of. |
| `vwap_location_model` | `conditionally_approved_intraday_model` | Intraday location candidate | Requiere VWAP policy; VWAP construido solo con informacion <= t. |
| `hod_lod_proximity_model` | `conditionally_approved_intraday_model` | Intraday structure candidate | Solo high_so_far / low_so_far hasta t; prohibido HOD/LOD final futuro. |
| `range_position_model` | `restricted_extension_only` | Coordinate-within-observed-range candidate | Requiere formula explicita y separacion frente a Volatility / Range State. |
| `pullback_retrace_location_model` | `restricted_boundary_model` | Recent-structure location candidate | Extension o pattern-research boundary hasta resolver frontera. |
| `anchored_vwap_distance_model` | `blocked_until_anchor_policy` | Possible extension candidate | Requiere politica de anchor y construccion de VWAP antes de mapping. |
| `final_daily_structure_model` | `after_close_or_prior_day_only` | Daily historical context | Prohibido intradia para dia actual antes del cierre. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `opening_gap_movement_model` | `move_to_price_movement_when_change` | Si mide cambio discontinuo de apertura, pertenece a Price Movement. |
| `future_extrema_location_model` | `outcome_only` | Future HOD/LOD, future extrema, MFE y MAE son outcomes; no inputs de State. |
| `range_amplitude_model` | `move_to_volatility_range_state` | Describe amplitud o dispersion, no localizacion contextual. |
| `activity_weighted_reference_model` | `dependency_not_identity` | VWAP puede depender de participacion, pero la distancia a VWAP no mide Trading Activity. |
| `execution_zone_model` | `move_to_liquidity_when_execution_cost` | Si pregunta coste, disponibilidad o impacto de negociar, pertenece a Liquidity. |
| `scanner_pattern_label_model` | `research_or_selection_surface_only` | No prueba localizacion como feature causal neutral. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Toda barra intradia solo sera consumible despues de su cierre.

3. `high_so_far` y `low_so_far` solo podran incluir informacion <= t.

4. HOD/LOD final del dia solo sera legal tras market close
   o como contexto historico de sesiones previas.

5. VWAP debera construirse solo con barras o trades disponibles <= t.

6. `prior_close` debera proceder de una sesion previa conocida as-of.

7. Anchored VWAP queda bloqueado hasta tener anchor policy explicita.

8. Pullback/retrace requerira ventana cerrada, anchor declarado
   y separacion frente a pattern labels.

9. `distance_to_session_hod`, `distance_to_session_lod`
   y `session_range_position` deberan registrarse o formularse
   explicitamente antes de mapping.

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
1. Operational Mapping de Price Location / Structure.

2. Builder Validation de Price Location / Structure.

3. Market State Integration de Price Location / Structure.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Cambia la frontera con Price Movement.
2. Cambia la frontera con Volatility / Range State.
3. VWAP location se redefine como core, profile o extension.
4. Se aprueba una VWAP policy canonica nueva.
5. Se aprueban capacidades atomicas `distance_to_session_hod`,
   `distance_to_session_lod` o `session_range_position`.
6. Pullback/retrace se promueve como pattern discovery,
   strategy research o Information Object independiente.
7. Se detecta uso intradia ilegal de HOD/LOD final del dia.
8. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
9. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_location_structure_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\price_location_structure_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
