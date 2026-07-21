# Trading Activity - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-20`
Decision: `accepted_with_restrictions`
Scope: `information_object_governance_decision`

Este documento registra la decision institucional aplicada sobre el
Information Object `Trading Activity`.

No reabre la revision cientifica.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Trading Activity
formal_admission_decision = accepted_with_restrictions
scientific_identity = accepted
operational_readiness = accepted_with_restrictions
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
operational_mapping_required = true
builder_validation_required = true
market_state_integration_required = true
```

Lectura:

```text
Trading Activity queda admitido como Information Object de TSIS,
pero su consumo operativo queda bloqueado hasta que existan mapping,
validacion de builder y decision de integracion en Market State.
```

## 2. Scientific Identity

```text
scientific_identity = accepted
scientific_identity_confidence = high
```

Justificacion:

```text
Trading Activity preserva una primary informational uncertainty propia:
cuanta participacion negociada observable existe en el instrumento,
en una escala temporal declarada y bajo legalidad temporal.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Trading Activity = intensidad observable de participacion negociada.
Liquidity = facilidad, coste, disponibilidad o impacto de negociar.
Price Movement = cambio, direccion, intensidad o persistencia del precio.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
Volatility / Range = amplitud, dispersion o inestabilidad del precio.
```

## 3. Approved Semantic Capability

```text
Trading Activity debe ser capaz de representar la intensidad observable
de participacion negociada de forma temporalmente legal.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que mida
participacion negociada realizada dentro de una ventana, escala
o resolucion temporal explicita, con fuente observable declarada
y cutoff legal en decision_timestamp.
```

## 4. Minimal Semantic Identity

`Trading Activity` deja de ser `Trading Activity` si desaparece:

```text
1. participacion negociada observable;
2. intensidad de participacion;
3. escala temporal, ventana o ritmo explicito;
4. negociacion realizada, no solo interes teorico o quote state;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
spread;
quoted depth;
direccion del precio;
retorno;
VWAP;
HOD / LOD;
agresor comprador o vendedor;
signed flow;
scanner selection;
outcomes futuros;
short activity con fuente y lag propios.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `daily_absolute_participation_model` | `approved_with_temporal_restriction` | daily context | Solo sesiones cerradas o contexto historico previo. |
| `daily_relative_participation_model` | `approved_with_prior_only_baseline` | daily baseline / anomaly context | Baseline prior-only; volumen final del dia no decision-safe intradia. |
| `intraday_absolute_accumulation_model` | `approved_for_first_operational_mapping` | first intraday state candidate | Barras cerradas; depende de politica de 014/013 quote-guarded. |
| `intraday_pace_model` | `conditionally_approved` | intraday extension | Requiere variante declarada: ventana, baseline, calendario, min_periods. |
| `trade_window_intensity_model` | `approved_as_extension` | microstructure / event-window profile | Ventana cerrada; min_rows; no usar post-event como input predictivo. |
| `trade_size_distribution_model` | `restricted_extension_only` | microstructure texture candidate | No entra en core sin justificacion adicional. |
| `economic_turnover_model` | `partially_approved` | dollar turnover allowed | True float turnover bloqueado sin float PIT gobernado. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `scanner_activity_threshold_model` | `selection_surface_only` | Selecciona candidatos; no prueba actividad como feature causal neutral. |
| `directional_activity_model` | `move_to_order_flow_pressure` | Introduce signo, agresion e imbalance. |
| `short_activity_model` | `move_to_short_side_context` | Fuente, lag y semantica distintos. |
| `true_float_turnover_model` | `blocked` | Requiere float point-in-time gobernado. |

## 7. Operational Restrictions

```text
1. No usar volumen diario final antes del cierre.

2. Todo baseline debe ser prior-only o as-of.

3. Toda barra intradia debe estar cerrada antes de consumo.

4. Toda ventana de trades debe cumplir:
   window_end <= decision_timestamp.

5. Scanner selection no puede entrar como variable causal neutral.

6. Signed flow, aggressor imbalance y OFI no pertenecen al core
   de Trading Activity.

7. True float turnover queda bloqueado hasta fuente float PIT oficial.

8. Toda variable fisica debe pasar por Operational Mapping antes
   de entrar en un perfil de State.
```

## 8. Authorized Consumers

Autorizados en esta decision:

```text
architecture_applied_mapping
operational_mapping_design
builder_validation_design
market_state_profile_design
event_state_profile_design
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
```

## 9. Required Next Artifacts

```text
1. Operational Mapping:
   C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md

2. Builder Validation:
   C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\trading_activity_builder_validation_v0_1.md

3. Market State Integration:
   C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\trading_activity_market_state_integration_v0_1.md
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Se promueve una fuente float PIT oficial.
2. Cambia la semantica de 004, 013, 014, 015 o 018.
3. Se aprueba un modelo de Order Flow Pressure que absorba signed activity.
4. Se decide que trade size distribution tiene identidad propia.
5. Se autoriza materializacion fisica de Market State.
6. Se detecta leakage temporal en un modelo aprobado.
7. Se promueve un nuevo contrato operativo en 01_foundations.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\trading_activity_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\trading_activity_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
