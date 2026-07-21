# Fundamental Context - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Fundamental Context`
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
El instrumento tiene estructura economica y societaria conocida as-of.
```

### Phenomenon Description

```text
Filings, estados, estructura de capital, float, shares,
market cap candidates y recencia fundamental pueden cambiar
el significado de precio, liquidez, actividad y eventos.
```

### Observable Information To Preserve

```text
Contexto fundamental point-in-time sobre estructura economica,
financiera o societaria del instrumento.
```

### Primary Informational Uncertainty

```text
Que caracteristicas fundamentales conocidas en t condicionan
la interpretacion del estado observable y que tan fresca o fiable
es esa informacion.
```

### Semantic Capability

```text
Fundamental Context debe representar contexto fundamental PIT/as-of
sin usar revisiones posteriores ni inferir outcomes.
```

### Candidate Information Object

```text
Fundamental Context
```

## 3. Minimal Semantic Identity

`Fundamental Context` deja de ser `Fundamental Context` si desaparece:

```text
1. informacion fundamental o societaria point-in-time;
2. as_of o filing timestamp gobernado;
3. recencia o validez temporal;
4. separacion entre valores conocidos y revisiones posteriores;
5. formula/version para ratios derivados.
```

No necesita para conservar su identidad:

```text
price movement;
liquidity actual;
trading activity intradia;
short-side crowding;
news freshness;
outcomes futuros.
```

## 4. Irreducibility Criterion

```text
Fundamental Context es irreducible si TSIS necesita preservar
estructura economica/societaria conocida as-of,
y esa informacion no queda suficientemente preservada por
News Context, Short-Side Context, Broad Market Context,
Liquidity o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Fundamental Context | En dominio vecino |
| --- | --- | --- |
| `float` | estructura de capital PIT si esta gobernada | input bloqueado para turnover si no hay fuente PIT |
| `market_cap` | contexto economico derivado | puede depender de price, pero no es Price Movement |
| `filing_age_days` | recencia fundamental | data freshness/gobernanza temporal |
| `statement_value_FIELD` | valor fundamental as-of | ratios requieren formula versionada |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `News Context` | Filing/news son catalizadores? | No. News preserva publicacion/catalizador; Fundamentals preserva estructura PIT. | `not_absorbed` |
| Absorb into `Liquidity` | Float/market cap explican liquidez? | Pueden condicionar, pero no miden coste/disponibilidad actual. | `not_absorbed` |
| Absorb into `Short-Side Context` | Float/short crowding son lo mismo? | No. Short-Side usa fuentes short/borrow/lag propio. | `not_absorbed` |
| Absorb into `Outcomes` | Fundamentals predicen resultados? | Su uso como predictor no los convierte en outcome. | `not_absorbed` |
| Split `Float PIT` | Float merece Objeto propio? | No por defecto. Es modelo/capacidad fundamental bloqueada hasta fuente gobernada. | `blocked_representation_model` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `filing_recency_model` | core candidate | Requiere as_of. |
| `statement_value_model` | core/extension | Campo y periodo deben estar gobernados. |
| `fundamental_ratio_model` | extension | Requiere formula versionada. |
| `float_pit_model` | blocked/extension | Bloqueado sin fuente PIT gobernada. |
| `market_cap_model` | candidate | Requiere shares/price/as_of policy. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima es preservar contexto fundamental conocido as-of,
con fuente, periodo, timestamp y politica de revision declarados.
```

## 9. Temporal Legality Constraints

```text
1. PIT/as_of obligatorio.
2. No usar revisiones posteriores.
3. Ratios requieren formula versionada.
4. Float PIT queda bloqueado sin fuente gobernada.
5. Statement values requieren periodo y filing lineage.
```

## 10. State Impact If Eventually Accepted

```text
market_state_fundamental_extension:
    filing age, statement recency, selected statement values.

blocked_until_source:
    float PIT, market cap, shares candidates.

research_only:
    ratios no versionados o formulas no cerradas.
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
1. Exigir PIT/as_of y no usar revisiones posteriores.
2. Bloquear float PIT sin fuente gobernada.
3. Versionar formulas de ratios.
4. Separar Fundamental Context de News y Short-Side Context.
5. Declarar filing/statement lineage.
```

## 12. Open Questions For Formal Admission

```text
1. Que campos fundamentales entran en core extension?
2. Que fuente gobierna float PIT?
3. Market cap se admite como fundamental, derived context o bloqueado?
4. Que formulas de ratios son institucionales?
5. Que recencia minima permite consumo de State?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\fundamental_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\fundamental_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\fundamental_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

