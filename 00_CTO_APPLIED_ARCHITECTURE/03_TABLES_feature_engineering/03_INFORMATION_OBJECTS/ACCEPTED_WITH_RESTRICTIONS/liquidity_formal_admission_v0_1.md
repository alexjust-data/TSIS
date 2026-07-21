# Liquidity - Formal Admission v0.1

Status: `formal_admission_v0_1`
Date: `2026-07-21`
Decision: `accepted_with_restrictions`
Scope: `tsis_market_ontology_phase_formal_admission`

Este documento registra la decision institucional aplicada sobre el
Information Object `Liquidity`.

No reabre la revision cientifica.
No modifica la metodologia de admision.
No autoriza Operational Mapping durante Phase A.
No autoriza cambios de schema.
No autoriza cambios de builder.
No materializa variables para `Market State` ni `Event State`.
No promociona datasets ni contratos operativos.

## 1. Decision

```text
information_object = Liquidity
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
Liquidity queda admitido como Information Object de TSIS,
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
Liquidity preserva una primary informational uncertainty propia:
que tan negociable es el instrumento en t, cuanto cuesta cruzar,
cuanta contrapartida observable existe y si el book es utilizable.
```

No requiere evidencia exclusiva.

Si requiere identidad informacional propia:

```text
Liquidity = facilidad, coste, disponibilidad y tradability
            observable de negociacion.

Trading Activity = intensidad observable de participacion negociada.
Market Microstructure State = estado operativo del book/tape.
Order Flow Pressure = signo, agresion, imbalance o presion direccional.
Volatility / Range State = amplitud o dispersion del precio.
Execution Outcomes = fills, slippage realizado o realized spread futuro.
```

## 3. Approved Semantic Capability

```text
Liquidity debe ser capaz de representar condiciones observables
de coste, disponibilidad y facilidad de negociacion
de forma temporalmente legal.
```

Condicion minima:

```text
Debe existir al menos un Representation Model aprobado que preserve
coste o disponibilidad observable de negociacion, con fuente declarada,
ventana temporal cerrada, cutoff legal en decision_timestamp
y separacion frente a outcomes de ejecucion futuros.
```

## 4. Minimal Semantic Identity

`Liquidity` deja de ser `Liquidity` si desaparece:

```text
1. coste observable de negociar;
2. disponibilidad o profundidad observable;
3. distincion entre tradability proxy y liquidity truth;
4. escala temporal o ventana declarada;
5. legalidad temporal en decision_timestamp.
```

No forman parte de su identidad minima:

```text
direccion del precio;
participacion negociada como fenomeno principal;
signed flow;
aggressor imbalance;
volatilidad o rango;
outcomes de ejecucion futuros;
realized spread futuro;
slippage futuro;
profundidad L2/MBO sin fuente gobernada.
```

## 5. Approved Representation Models

| Model | Formal status | Authorized role | Restrictions |
| --- | --- | --- | --- |
| `quoted_spread_cost_model` | `approved_as_core_candidate` | Core observable cost candidate for future Phase B mapping | Requiere quote quality gates; ventanas cerradas. No autoriza variable fisica ahora. |
| `displayed_depth_model` | `approved_with_L1_restriction` | Visible availability candidate | L1 only; no presentar como profundidad total del mercado. |
| `quote_availability_model` | `approved_as_context_or_extension` | Quote usability / availability candidate | Requiere ventanas cerradas y politica de variantes. |
| `tradability_proxy_model` | `restricted_proxy_only` | Tradability proxy context | Dollar volume/trade count son proxies, no liquidity truth. |
| `effective_spread_model` | `blocked_until_alignment_and_side_policy` | Advanced cost candidate | Requiere trade-quote alignment y side classifier gobernados. |
| `price_impact_model` | `blocked_until_formula_and_boundary` | Impact candidate | Requiere formula causal y frontera con outcomes / Order Flow Pressure. |

## 6. Rejected Or Non-Core Models

| Model | Decision | Reason |
| --- | --- | --- |
| `realized_spread_model` | `outcome_or_research_only` | Usa horizonte futuro; no puede ser input de State. |
| `ofi_l1_model` | `move_to_order_flow_pressure` | OFI, signed flow y aggressor imbalance miden presion direccional. |
| `pure_dollar_volume_liquidity_model` | `proxy_only_not_truth` | Dollar volume es evidencia compartida; no prueba coste ni disponibilidad completa. |
| `borrow_availability_liquidity_model` | `blocked_without_governed_source` | No existe fuente borrow/locate gobernada. |
| `L2_depth_model` | `blocked_without_governed_source` | No existe fuente L2/MBO gobernada. |
| `execution_outcome_model` | `move_to_execution_or_outcomes` | Fills, slippage y PnL son ejecucion/outcomes, no Liquidity observable en t. |

## 7. Operational Restrictions

```text
1. Ningun consumo operativo queda autorizado durante Phase A.

2. Quotes deberan ser observables <= decision_timestamp.

3. Ventanas de spread, depth y availability deberan estar cerradas.

4. Quote quality gates seran obligatorios antes de mapping.

5. L1 depth no podra presentarse como profundidad total.

6. Dollar volume y trade count deberan declararse proxies
   de tradability, no liquidity truth.

7. Effective spread queda bloqueado hasta trade-quote alignment
   y side classifier gobernados.

8. Realized spread, slippage futuro y realized execution quality
   quedan prohibidos como inputs.

9. OFI, signed flow y aggressor imbalance pertenecen a
   Order Flow Pressure.

10. Locked/crossed context debera viajar con quality o
    microstructure context, sin confundirse con alpha.

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
1. Operational Mapping de Liquidity.

2. Builder Validation de Liquidity.

3. Market State Integration de Liquidity.

4. Operational Promotion, solo si supera gates posteriores.
```

## 10. Review Triggers

Revisar esta admision si ocurre cualquiera de estos eventos:

```text
1. Cambia la frontera con Trading Activity.
2. Cambia la frontera con Market Microstructure State.
3. Cambia la frontera con Order Flow Pressure.
4. Se aprueba trade-quote alignment y side classifier gobernados.
5. Se aprueba fuente L2/MBO gobernada.
6. Se aprueba fuente borrow/locate gobernada.
7. Price impact se redefine como input observable u outcome.
8. Se detecta uso de realized spread o slippage futuro como input.
9. La Cross-Object Ontology Review detecta redundancia,
   hueco o absorcion parcial no resuelta.
10. Se reabre Phase B tras congelar TSIS Market Ontology v1.
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\liquidity_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\liquidity_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```
