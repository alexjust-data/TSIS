# Volatility / Range State - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Volatility / Range State`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Volatility / Range State
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
Volatility / Range State queda admitido como Information Object de TSIS,
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
Volatility / Range State preserva una primary informational uncertainty
propia: cuanta amplitud o dispersion observable tiene el precio
en una ventana temporal legal.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Volatility / Range State = amplitud, rango, dispersion
                           o variabilidad observable del precio.

Price Movement = cambio, direccion, intensidad o persistencia del precio.
Price Location / Structure = posicion frente a anchors legales.
Trading Activity = intensidad observable de participacion negociada.
Liquidity = facilidad, coste, disponibilidad o impacto de negociar.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
Outcome Layer = future range, future volatility, MFE y MAE.
```

## 3. Approved Semantic Capability

```text
Volatility / Range State debe ser capaz de representar
amplitud y dispersion observable del precio de forma temporalmente legal.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado capaz de medir
rango, amplitud o dispersion observada del precio, con ventana temporal
declarada, fuente observable declarada, cutoff legal en decision_timestamp
y separacion estricta frente a outcomes futuros.
```

## 4. Minimal Semantic Identity

`Volatility / Range State` deja de ser `Volatility / Range State`
si desaparece:

```text
1. amplitud, rango o dispersion observable del precio;
2. ventana temporal declarada;
3. separacion entre rango observado y movimiento direccional;
4. separacion entre rango observado y localizacion del precio;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
direccion del cambio;
velocidad;
aceleracion;
posicion frente a VWAP, HOD o LOD como fenomeno principal;
volumen;
participacion negociada;
spread;
depth;
coste de ejecucion;
order flow direccional;
future range;
future volatility;
MFE;
MAE.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `intraday_range_so_far_model` | `approved_as_core_candidate` | Core observable amplitude candidate for future Phase B mapping | Solo barras cerradas <= t; high/low observados hasta t. No autoriza variable fisica ahora. |
| `daily_range_model` | `approved_with_after_close_restriction` | Daily historical context | Daily range final no es decision-safe intradia para el dia actual. |
| `rolling_daily_volatility_model` | `conditionally_approved_historical_model` | Historical volatility context | Requiere variante prior-only, ventana, estimator y min_periods. |
| `rolling_daily_range_model` | `conditionally_approved_historical_model` | Historical range context | Requiere variante prior-only, estadistico y min_periods. |
| `closed_window_realized_volatility_model` | `conditionally_approved_intraday_model` | Intraday / event-window dispersion candidate | Requiere formula canonica, ventana W, return input y min_periods antes de mapping. |
| `compression_expansion_model` | `restricted_extension_only` | Relative range/volatility state candidate | No core hasta formula, baseline y variante versionada. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `future_range_response_model` | `outcome_only` | Future range, future volatility, MFE y MAE son outcomes; no inputs de State. |
| `movement_speed_model` | `move_to_price_movement` | Speed y acceleration describen dinamica direccional, no identidad primaria de range/volatility. |
| `range_position_model` | `move_to_price_location_structure_when_coordinate` | Si se interpreta como coordenada dentro del rango, pertenece a Price Location / Structure. |
| `activity_conditioned_volatility_model` | `dependency_not_identity` | La volatilidad puede estar condicionada por actividad, pero no mide participacion. |
| `execution_risk_model` | `move_to_liquidity_when_execution_cost` | Si pregunta coste o disponibilidad de negociar, pertenece a Liquidity. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Daily range final no sera decision-safe intradia.

3. Intraday range solo podra usar barras cerradas <= t.

4. Rolling volatility/range debera ser prior-only o ventana cerrada.

5. Realized volatility requerira ventana cerrada, formula,
   estimator, return input y min_periods.

6. Compression/expansion requerira baseline, denominator,
   ventana y version de formula.

7. Future range, future volatility, MFE y MAE quedan prohibidos
   como inputs.

8. Range position sera Price Location / Structure si se interpreta
   como coordenada.

9. Speed y acceleration perteneceran a Price Movement salvo decision
   transversal contraria.

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
1. Operational Mapping de Volatility / Range State.

2. Builder Validation de Volatility / Range State.

3. Market State Integration de Volatility / Range State.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Cambia la frontera con Price Movement.
2. Cambia la frontera con Price Location / Structure.
3. Se aprueba una formula canonica de realized volatility intradia.
4. Se aprueba una formula canonica de compression/expansion.
5. Se redefine range position como coordenada o como rango.
6. Se detecta uso ilegal de future range, future volatility, MFE o MAE.
7. Se detecta contaminacion entre volatility state y quality/noise flags.
8. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
9. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\volatility_range_state_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\volatility_range_state_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
