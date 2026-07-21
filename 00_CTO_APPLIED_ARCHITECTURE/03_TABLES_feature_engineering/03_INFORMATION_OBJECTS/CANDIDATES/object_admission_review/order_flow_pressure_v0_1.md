# Order Flow Pressure - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Order Flow Pressure`
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
El flujo negociado puede ejercer presion direccional.
```

### Phenomenon Description

```text
Trades y quotes gobernadas pueden inferir signo, agresion,
imbalance y consumo direccional de liquidez en una ventana cerrada.
```

### Observable Information To Preserve

```text
Presion direccional inferida desde flujo de trades y quotes,
incluyendo signo, agresion, imbalance y confidence del alignment.
```

### Primary Informational Uncertainty

```text
Si el flujo observable ejerce presion compradora o vendedora,
con que imbalance y confianza, y si esa presion altera
la interpretacion de movimiento, liquidez y continuacion/fallo.
```

### Semantic Capability

```text
Order Flow Pressure debe representar presion direccional del flujo
solo cuando existan alignment, classifier y confidence policy gobernados.
```

### Candidate Information Object

```text
Order Flow Pressure
```

## 3. Minimal Semantic Identity

`Order Flow Pressure` deja de ser `Order Flow Pressure` si desaparece:

```text
1. direccion o signo inferido del flujo;
2. agresion, imbalance o consumo direccional;
3. trade-quote alignment o source policy;
4. confidence policy;
5. ventana cerrada legal en decision_timestamp.
```

No necesita para conservar su identidad:

```text
actividad no direccional;
liquidez como coste/disponibilidad;
microstructure state sin direccion;
movimiento de precio sin atribucion de flujo;
outcome posterior;
classifier no versionado.
```

## 4. Irreducibility Criterion

```text
Order Flow Pressure es irreducible si TSIS necesita preservar
presion direccional del flujo observable,
y esa informacion no queda suficientemente preservada por
Trading Activity, Liquidity, Market Microstructure State,
Price Movement o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Order Flow Pressure | En dominio vecino |
| --- | --- | --- |
| `trades` | signo/agresion/imbalance inferido | Trading Activity como intensidad |
| `quotes` | alignment y bid/ask context | Liquidity/Microstructure como cost/state |
| `OFI L1` | pressure extension L1-limited | Liquidity/microstructure context si no direccional |
| `price movement` | resultado observable asociado | no prueba agresion por si solo |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Trading Activity` | Es solo actividad alta? | No. Activity es no direccional por defecto; OFP requiere signo/agresion/imbalance. | `not_absorbed` |
| Absorb into `Liquidity` | Es solo consumo de liquidez? | No. Puede medir consumo direccional, pero Liquidity pregunta por disponibilidad/coste. | `not_absorbed` |
| Absorb into `Microstructure` | Es solo quote/tape state? | No. Microstructure soporta el contexto; OFP introduce direccion. | `not_absorbed` |
| Absorb into `Price Movement` | Precio sube, entonces buy pressure? | No. Movimiento no prueba agresion sin classifier/alignment. | `not_absorbed` |
| Split `OFI L1` | OFI merece Objeto propio? | No por defecto. Es modelo/extension L1-limited de pressure. | `representation_model` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `bid_hit_ask_lift_model` | scientific core candidate | Bloqueado para State hasta alignment. |
| `signed_flow_model` | core candidate | Bloqueado hasta classifier. |
| `aggressor_imbalance_model` | core candidate | Bloqueado hasta classifier/confidence. |
| `ofi_l1_model` | extension | L1-limited hasta policy. |
| `alignment_confidence_model` | mandatory support model | Necesario para consumo responsable. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima no es tener trades.

La condicion minima es poder inferir presion direccional
con alignment, classifier y confidence policy gobernados.
```

## 9. Temporal Legality Constraints

```text
1. Trades y quotes deben estar disponibles <= decision_timestamp.
2. Ventanas deben estar cerradas.
3. Requiere trade-quote alignment gobernado.
4. Requiere side classifier versionado.
5. Requiere confidence policy y timestamp/sequence validation.
6. OFI debe declararse L1-limited.
```

## 10. State Impact If Eventually Accepted

```text
market_state_microstructure_extension:
    signed flow, aggressor imbalance, OFI L1 cuando esten gobernados.

research_only_until_ready:
    modelos con classifier/alignment no cerrados.

support_quality:
    alignment confidence obligatorio.
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
operational_readiness = blocked_for_state_until_alignment_and_classifier
state_consumption_authorized = false
physical_variables_authorized = false
operational_mapping_required = true
```

Restricciones operativas recomendadas:

```text
1. Bloquear State hasta trade-quote alignment gobernado.
2. Bloquear State hasta side classifier y confidence policy.
3. Separar OFP de Trading Activity no direccional.
4. Separar OFP de Liquidity y Microstructure State.
5. Declarar OFI como L1-limited.
```

## 12. Open Questions For Formal Admission

```text
1. Que classifier es institucionalmente aceptable?
2. Que confidence threshold permite State consumption?
3. Que alignment policy aplica a trades/quotes irregulares?
4. OFI L1 entra como pressure, microstructure o extension separada?
5. Que parte queda research-only hasta disponer de quote alignment robusto?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\order_flow_pressure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\order_flow_pressure_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

