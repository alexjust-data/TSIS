# Liquidity - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Liquidity` merece existir
como `Information Object` independiente.

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
Negociar tiene coste y disponibilidad variable.
```

### Phenomenon Description

```text
La facilidad de ejecutar o absorber negociacion cambia segun spread,
profundidad visible, disponibilidad de quotes, actividad operable
e impacto esperado.
```

### Observable Information To Preserve

```text
Facilidad, coste y disponibilidad observable para negociar
un instrumento en una escala temporal declarada.
```

### Primary Informational Uncertainty

```text
Que tan negociable es el instrumento en t:
cuanto cuesta cruzar, cuanta contrapartida observable existe,
si el book es utilizable, y si la actividad disponible sirve
como proxy restringido de tradability.
```

### Semantic Capability

```text
Liquidity debe ser capaz de representar condiciones observables
de coste, disponibilidad y facilidad de negociacion de forma temporalmente legal.
```

### Candidate Information Object

```text
Liquidity
```

## 3. Minimal Semantic Identity

`Liquidity` deja de ser `Liquidity` si desaparece:

```text
1. coste observable de negociar;
2. disponibilidad o profundidad observable;
3. capacidad de distinguir tradability proxy de liquidity truth;
4. escala temporal o ventana declarada;
5. legalidad temporal en decision_timestamp.
```

No necesita para conservar su identidad:

```text
direccion del precio;
participacion negociada como fenomeno principal;
signed flow o aggressor imbalance;
volatilidad/rango;
outcomes de ejecucion futuros;
profundidad L2/MBO sin fuente gobernada.
```

## 4. Irreducibility Criterion

```text
Liquidity es irreducible si TSIS necesita preservar coste,
facilidad y disponibilidad de negociacion,
y esa informacion no queda suficientemente preservada por
Trading Activity, Market Microstructure State, Order Flow Pressure,
Price Movement, Volatility o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Liquidity | En dominio vecino |
| --- | --- | --- |
| `dollar_volume` | proxy restringido de tradability | Trading Activity como cantidad economica negociada |
| `trade_count` | proxy restringido de disponibilidad operable | Trading Activity como intensidad de prints |
| `spread_bps` | coste de cruzar | Microstructure como estado de quote quality/context |
| `top_depth` | disponibilidad visible L1 | no profundidad total del mercado |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Trading Activity` | Dollar volume basta para liquidity? | No. Es proxy de tradability, no coste/disponibilidad completa. | `not_absorbed` |
| Absorb into `Market Microstructure State` | Es solo quote state? | No. Microstructure describe condiciones top-of-book/tape; Liquidity pregunta por negociabilidad. | `not_absorbed` |
| Absorb into `Order Flow Pressure` | Es solo consumo de liquidez? | No. OFP mide presion direccional; Liquidity mide capacidad/coste/disponibilidad. | `not_absorbed` |
| Absorb into `Execution Outcomes` | Realized spread o slippage futuro son liquidity? | No como input. Son research/outcome si usan futuro. | `outcome_separated` |
| Split `Tradability Proxy` | Proxy merece Objeto propio? | No por defecto. Es modelo restringido de Liquidity, no truth. | `proxy_model` |

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
| `quoted_spread_cost_model` | core candidate | Permitido con quote quality gates. |
| `displayed_depth_model` | core/extension candidate | L1 only; no profundidad total. |
| `quote_availability_model` | context/extension | Representa presencia/usabilidad de quotes. |
| `tradability_proxy_model` | proxy model | Dollar volume/trade count no son liquidity truth. |
| `effective_spread_model` | blocked for State | Requiere alignment y side policy. |
| `price_impact_model` | candidate blocked | Requiere formula y boundary con outcomes. |
| `realized_spread_model` | outcome/research only | No input si usa horizonte futuro. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima no es usar spread o depth aislados.

La condicion minima es que exista al menos un modelo aprobado
que preserve coste/disponibilidad de negociacion observable
con fuentes y cutoffs gobernados.
```

## 9. Temporal Legality Constraints

```text
1. Quotes deben ser observables <= decision_timestamp.
2. Ventanas de spread/depth deben estar cerradas.
3. L1 depth no debe presentarse como depth total.
4. Effective spread requiere trade-quote alignment y side classifier.
5. Realized spread/slippage futuro no puede ser input de State.
6. Locked/crossed debe viajar con quality/microstructure context.
```

## 10. State Impact If Eventually Accepted

```text
market_state_core:
    spread/availability minima con quality gates.

market_state_microstructure_extension:
    depth, quote availability, locked/crossed context.

execution_research:
    effective spread, impact, realized spread bajo separacion X/y.
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
1. Mantener separado Liquidity de Trading Activity.
2. Declarar dollar volume/trade count como proxies, no truth.
3. No presentar L1 depth como profundidad total.
4. Bloquear effective/realized spread hasta alignment y side policy.
5. Mover OFI/signed/aggressor a Order Flow Pressure.
```

## 12. Open Questions For Formal Admission

```text
1. Que modelo implementa primero Liquidity core?
2. Que quote quality gates son obligatorios?
3. Depth L1 entra en core o extension?
4. Tradability proxy debe vivir en core, extension o execution context?
5. Que parte de price impact es input observable y que parte outcome?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\liquidity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\liquidity_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

