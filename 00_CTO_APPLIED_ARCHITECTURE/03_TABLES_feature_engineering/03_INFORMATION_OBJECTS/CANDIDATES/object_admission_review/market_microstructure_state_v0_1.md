# Market Microstructure State - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Market Microstructure State`
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
La estructura observable del tape y top-of-book cambia.
```

### Phenomenon Description

```text
Las condiciones microestructurales observables, como two-sided quotes,
locked/crossed state, quote activity, staleness y tape integrity,
condicionan la interpretabilidad de observaciones intradia.
```

### Observable Information To Preserve

```text
Estado observable del top-of-book y tape que afecta la calidad,
interpretabilidad y contexto de precio, liquidez y actividad.
```

### Primary Informational Uncertainty

```text
En que condicion microestructural observable se encuentra el mercado:
si hay quotes two-sided, si el book esta locked/crossed,
si las quotes son activas o stale,
y si el tape/quote context permite interpretar otros Objetos.
```

### Semantic Capability

```text
Market Microstructure State debe representar condiciones observables
del top-of-book y tape sin absorber Liquidity, Trading Activity
ni Order Flow Pressure.
```

### Candidate Information Object

```text
Market Microstructure State
```

## 3. Minimal Semantic Identity

`Market Microstructure State` deja de ser `Market Microstructure State`
si desaparece:

```text
1. estado observable de quotes o tape;
2. condicion microestructural del top-of-book;
3. rol de interpretabilidad/contexto;
4. separacion frente a liquidez, actividad y order flow;
5. legalidad temporal en decision_timestamp.
```

No necesita para conservar su identidad:

```text
coste/facilidad de negociar como pregunta primaria;
volumen negociado como intensidad;
signo/agresion/imbalance;
halts como source event;
L2/MBO sin fuente gobernada;
alpha o outcome.
```

## 4. Irreducibility Criterion

```text
Market Microstructure State es irreducible si TSIS necesita preservar
condiciones observables de tape/top-of-book que afectan interpretabilidad,
y esa informacion no queda suficientemente preservada por Liquidity,
Trading Activity, Order Flow Pressure, Halt Context o Quality State.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Market Microstructure State | En dominio vecino |
| --- | --- | --- |
| `spread_bps` | microstructure/quote state context | Liquidity como coste de cruce |
| `two_sided_rows` | quote availability/interpretable book | Liquidity availability gate |
| `locked/crossed ratios` | microstructure quality/context | calidad/gate de consumo |
| `quote_update_rate` | quote activity state | posible liquidity context |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Liquidity` | Microstructure es liquidity? | No. Liquidity pregunta por negociabilidad; Microstructure por estado/contexto top-of-book/tape. | `not_absorbed` |
| Absorb into `Trading Activity` | Quote/tape state es actividad? | No. Activity mide participacion negociada; microstructure mide condiciones de observacion. | `not_absorbed` |
| Absorb into `Order Flow Pressure` | Microstructure es order flow? | No. OFP introduce signo/agresion; microstructure puede soportar alignment pero no lo reemplaza. | `not_absorbed` |
| Absorb into `Representation Quality State` | Es solo quality? | Parcial. Locked/crossed/tape integrity pueden ser quality context, pero el estado microestructural observable tiene identidad propia. | `boundary_confirmed` |
| Move `Interruption Context` | Halts pertenecen aqui? | No. Interruption/halt context debe vivir en Halt Context. | `move_to_halt_context` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `two_sided_quote_state_model` | core candidate | Permitido con quote quality gates. |
| `locked_crossed_state_model` | microstructure quality context | Context/gate, no alpha por defecto. |
| `quote_activity_state_model` | extension | Mide actividad/actualizacion de quotes. |
| `quote_staleness_lifetime_model` | blocked/pending | Requiere timestamp sequence policy. |
| `tape_integrity_context_model` | quality context only | No debe confundirse con signal. |
| `interruption_context_model` | move out | Pertenece a Halt Context. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima es disponer de al menos un modelo aprobado
que preserve estado observable de quote/tape con gates temporales
y de calidad suficientes.
```

## 9. Temporal Legality Constraints

```text
1. Quotes/trades deben estar disponibles <= decision_timestamp.
2. Ventanas microestructurales deben estar cerradas.
3. Staleness requiere timestamp sequence policy.
4. L2/MBO queda bloqueado sin fuente gobernada.
5. Locked/crossed y tape integrity son context/gates, no outcomes.
```

## 10. State Impact If Eventually Accepted

```text
market_state_microstructure_extension:
    two-sided quote state, locked/crossed context, quote activity.

quality/context:
    tape integrity and staleness gates.

halt_context:
    interruptions moved out.
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
1. No absorber Liquidity, Trading Activity ni Order Flow Pressure.
2. Tratar locked/crossed y tape integrity como context/gate.
3. Bloquear L2/MBO hasta fuente gobernada.
4. Mover interruption context a Halt Context.
5. Exigir timestamp sequence policy para staleness/lifetime.
```

## 12. Open Questions For Formal Admission

```text
1. Que microstructure context entra en core o extension?
2. Locked/crossed viaja como state, quality o ambos?
3. Que gates hacen interpretable una ventana microestructural?
4. Como se separa quote state de liquidity cost?
5. Que source policy habilitaria L2/MBO en el futuro?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\market_microstructure_state_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\market_microstructure_state_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

