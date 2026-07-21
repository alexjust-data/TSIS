# Volatility / Range State - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Volatility / Range State`
merece existir como `Information Object` independiente.

No constituye admision formal.
No autoriza variables para `Market State` ni `Event State`.
No selecciona implementacion fisica final.
No modifica schemas, builders, validators, manifests, contratos ni datasets.

## Nota De Estado

```text
Domain Definition = define el dominio semantico.
Representation Landscape = revisa modelos posibles.
Candidate Object Definition = fija el candidato trazable.
Object Admission Review = intenta romper el candidato antes de admitirlo.
Accepted Object = decision institucional posterior, no ejecutada aqui.
```

Este documento aplica el criterio refinado de admision:

```text
Un Information Object no necesita evidencia exclusiva.

Necesita preservar una primary informational uncertainty
que no quede suficientemente representada por otros Objetos
sin perder su semantic capability o minimal semantic identity.
```

## 1. Jerarquia Metodologica

```text
Observable market phenomenon
    -> Phenomenon description
        -> Observable information to preserve
            -> Primary informational uncertainty
                -> Semantic capability
                    -> Candidate Information Object
                        -> Minimal semantic identity
                            -> Representation Model
                                -> Physical implementation
```

## 2. Candidate Object

### Observable Market Phenomenon

```text
El precio se dispersa.
```

### Phenomenon Description

```text
El precio ocupa una amplitud observable, con rango,
dispersion o variabilidad en una ventana temporal declarada.
```

### Observable Information To Preserve

```text
Amplitud, dispersion e incertidumbre observable del precio
en ventanas temporales legales.
```

### Primary Informational Uncertainty

```text
Cuanta amplitud o dispersion observable tiene el precio,
si el estado esta comprimido o expandido,
y si la variabilidad actual altera la interpretacion del movimiento,
evento, riesgo u operabilidad.
```

### Semantic Capability

```text
Volatility / Range State debe ser capaz de representar
amplitud y dispersion observable del precio de forma temporalmente legal.
```

### Candidate Information Object

```text
Volatility / Range State
```

## 3. Minimal Semantic Identity

`Volatility / Range State` deja de ser `Volatility / Range State`
si desaparece:

```text
1. amplitud, rango o dispersion observable del precio;
2. ventana temporal declarada;
3. separacion entre rango observado y movimiento direccional;
4. separacion entre rango observado y localizacion del precio;
5. legalidad temporal en decision_timestamp.
```

No necesita para conservar su identidad:

```text
direccion del cambio;
posicion frente a VWAP/HOD/LOD como fenomeno principal;
volumen o participacion negociada;
spread, depth o coste de ejecucion;
order flow direccional;
future range, future volatility, MFE o MAE.
```

## 4. Irreducibility Criterion

```text
An Information Object is irreducible when its primary informational
uncertainty cannot be sufficiently represented by existing admitted
or candidate Objects without losing its semantic capability or
minimal semantic identity.
```

Aplicacion:

```text
Volatility / Range State es irreducible si TSIS necesita preservar
amplitud y dispersion observable del precio,
y esa informacion no queda suficientemente preservada por
Price Movement, Price Location / Structure, Trading Activity,
Liquidity, Order Flow Pressure o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Volatility / Range State | En dominio vecino |
| --- | --- | --- |
| `high_price` / `low_price` | rango y amplitud observada | anchors para Price Location |
| `close_price` | punto de serie para dispersion/realized vol | precio para Price Movement |
| `return series` | insumo para realized volatility | movimiento direccional si se interpreta como cambio |
| `MFE` / `MAE` | outcome de excursion futura | prohibido como input observable |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Price Movement` | Es solo cambio de precio? | No. Movement mide direccion/dinamica; Range/Volatility mide amplitud/dispersion. | `not_absorbed` |
| Absorb into `Price Location / Structure` | Es solo posicion dentro del rango? | No. Location usa coordenadas; Range State mide el tamano/dispersion del espacio observado. | `not_absorbed` |
| Absorb into `Trading Activity` | La volatilidad depende de volumen? | Puede estar condicionada por actividad, pero no mide participacion. | `not_absorbed` |
| Absorb into `Liquidity` | Es solo riesgo de ejecucion? | No. Liquidity mide coste/disponibilidad; Range State mide variabilidad del precio. | `not_absorbed` |
| Absorb into `Outcomes` | Future range es volatility? | No como input. Future range/MFE/MAE son outcomes. | `outcome_separated` |
| Split `Compression / Expansion` | Merece Objeto propio? | No por defecto. Es modelo de estado de rango/volatilidad. | `representation_model` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
Scientific Review:
    Debe existir este Information Object?

Engineering Readiness:
    Esta TSIS preparado para usarlo operativamente?
```

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `daily_range_model` | daily context candidate | Legal tras cierre o como historia previa. |
| `rolling_daily_volatility_model` | historical volatility model | Requiere prior-only variant. |
| `rolling_daily_range_model` | historical range model | Requiere prior-only variant. |
| `intraday_range_so_far_model` | core intraday candidate | Usa high/low observados hasta t. |
| `closed_window_realized_volatility_model` | intraday/event-window candidate | Requiere formula antes de State mapping. |
| `compression_expansion_model` | extension | No core hasta formula definida. |
| `future_range_response_model` | outcome only | Prohibido como input de State. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima no es usar una variable concreta.

La condicion minima es que exista al menos un Representation Model aprobado
capaz de implementar amplitud/dispersion observable con cutoff legal.
```

## 9. Temporal Legality Constraints

```text
1. Daily range final no es decision-safe intradia.

2. Intraday range solo puede usar barras cerradas <= t.

3. Rolling volatility/range debe ser prior-only o ventana cerrada.

4. Realized volatility requiere ventana cerrada, formula y min_periods.

5. Future volatility/range, MFE y MAE son outcomes, no inputs.

6. Toda fuente 1m derivada debe declarar lineage, version y politica
   de reparacion o quote-guarding cuando aplique.
```

## 10. State Impact If Eventually Accepted

```text
market_state_core:
    rango/amplitud observable minima decision-safe.

market_state_intraday:
    range_so_far y realized volatility con formulas gobernadas.

market_state_event_extension:
    compression/expansion en ventanas cerradas.

outcomes:
    future range, future volatility, MFE y MAE separados.
```

## 11. Preliminary Review Decision

```text
peer_review_result = survives_adversarial_review
formal_admission_decision = pending
```

### Scientific Identity

```text
scientific_identity = accepted_by_review
scientific_identity_confidence = high
recommended_scientific_admission_path = accepted
```

### Operational Readiness

```text
operational_readiness = accepted_with_restrictions
state_consumption_authorized = false
physical_variables_authorized = false
operational_mapping_required = true
```

Restricciones operativas recomendadas:

```text
1. Separar estrictamente range/volatility de Price Movement.
2. Separar range position como Location si se interpreta como coordenada.
3. Prohibir future range, future volatility, MFE y MAE como inputs.
4. Exigir formulas versionadas para realized vol y compression/expansion.
5. Exigir ventanas cerradas y min_periods.
```

## 12. Open Questions For Formal Admission

```text
1. Que modelo implementa primero la semantic capability?
2. `intraday_range_so_far_model` entra en core o intraday profile?
3. Como se define realized volatility sin multiplicar variantes?
4. Compression/expansion es extension general o pattern-specific?
5. Que thresholds separan volatility state de quality/noise flags?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\volatility_range_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\volatility_range_state_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

