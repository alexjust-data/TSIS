# Price Movement - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Price Movement`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Price Movement
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
Price Movement queda admitido como Information Object de TSIS,
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
Price Movement preserva una primary informational uncertainty propia:
como cambia el precio hasta t.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Price Movement = cambio, direccion, intensidad, continuidad
                 o persistencia observable del precio.

Price Location = donde esta el precio respecto a referencias.
Volatility / Range = amplitud, dispersion o inestabilidad del precio.
Trading Activity = intensidad observable de participacion negociada.
Liquidity = facilidad, coste, disponibilidad o impacto de negociar.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
```

## 3. Approved Semantic Capability

```text
Price Movement debe ser capaz de representar el cambio observable
del precio entre referencias temporales declaradas,
de forma temporalmente legal.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que mida
cambio observable del precio, con fuente observable declarada,
referencias temporales declaradas, cutoff legal en decision_timestamp
y separacion estricta frente a outcomes futuros.
```

## 4. Minimal Semantic Identity

`Price Movement` deja de ser `Price Movement` si desaparece:

```text
1. cambio observable del precio;
2. referencia temporal declarada;
3. direccion, magnitud, intensidad, continuidad o persistencia
   del cambio;
4. separacion entre movimiento observado hasta t y outcome futuro;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
posicion respecto a VWAP, HOD, LOD, open o prior close;
spread;
depth;
turnover;
volumen;
trade count;
signed flow;
aggressor imbalance;
rango como fenomeno principal;
volatilidad como dispersion;
scanner selection;
pattern labels;
future returns;
MFE;
MAE.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `intraday_return_to_reference_model` | `approved_as_core_candidate` | Core semantic capability candidate for future Phase B mapping | Solo contra referencias observadas y legales hasta t. No autoriza variable fisica ahora. |
| `opening_gap_movement_model` | `approved_with_temporal_restriction` | Discontinuous movement context | Legal despues de conocer apertura y prior close. |
| `daily_closed_return_model` | `approved_with_after_close_restriction` | Daily historical context | Dia actual solo tras market close; historia previa permitida as-of. |
| `bar_to_bar_movement_model` | `conditionally_approved` | Closed-bar movement candidate | Requiere decidir si `intraday__bar_return` existe como capacidad atomica canonica. |
| `move_speed_model` | `conditionally_approved_extension` | Intraday dynamic extension | Requiere ventana W, horizonte, min_periods y politica de variantes. |
| `move_acceleration_model` | `restricted_extension_only` | Second-order movement extension | Sensible a ruido; requiere controles de horizonte y estabilidad. |
| `momentum_persistence_model` | `representation_model_or_subobject_pending` | Directional persistence candidate | No es sinonimo de Price Movement core; frontera pendiente para review transversal. |
| `reversal_fade_model` | `restricted_boundary_model` | Loss-of-continuity candidate | No puede convertirse en pattern research ni label de estrategia dentro de State. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `future_response_model` | `outcome_only` | Future returns, MFE y MAE son outcomes; no inputs de State. |
| `price_location_reference_model` | `move_to_price_location_structure` | Describe donde esta el precio, no como cambia. |
| `range_dispersion_model` | `move_to_volatility_range_state` | Describe amplitud o dispersion, no identidad primaria de movimiento. |
| `activity_or_turnover_model` | `move_to_trading_activity` | Describe participacion negociada, no movimiento del precio. |
| `signed_flow_or_aggression_model` | `move_to_order_flow_pressure` | Introduce signo, agresion, imbalance o presion direccional. |
| `scanner_pattern_label_model` | `research_or_selection_surface_only` | No prueba movimiento como feature causal neutral. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Toda barra intradia solo sera consumible despues de su cierre.

3. `gap_pct` solo sera legal despues de conocer apertura y prior_close.

4. `daily_return_pct` e `intraday_return_pct` del dia actual
   solo seran legales tras market close si representan el dia completo.

5. `return_vs_prior_close` y `return_vs_session_open`
   solo seran legales intradia con precio observado hasta t.

6. Speed, acceleration, persistence y reversal/fade requeriran
   ventanas cerradas, horizonte declarado, min_periods y versionado
   de variantes.

7. Future returns, MFE y MAE quedan prohibidos como inputs.

8. Momentum queda pendiente como Representation Model o subobject;
   no puede absorber automaticamente Price Movement.

9. `intraday__bar_return` queda pendiente de decision como
   capacidad atomica canonica o expresion derivada de returns
   contra referencia.

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
1. Operational Mapping de Price Movement.

2. Builder Validation de Price Movement.

3. Market State Integration de Price Movement.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Momentum se promueve como Information Object independiente.
2. Se aprueba una capacidad atomica canonica `intraday__bar_return`.
3. Cambian las fronteras de Price Location / Structure.
4. Cambian las fronteras de Volatility / Range State.
5. Se redefine la politica de referencias temporales canonicas.
6. Se autoriza un nuevo modelo de reversal/fade con identidad propia.
7. Se detecta leakage temporal en cualquier modelo aprobado.
8. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
9. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_movement_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\price_movement_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
