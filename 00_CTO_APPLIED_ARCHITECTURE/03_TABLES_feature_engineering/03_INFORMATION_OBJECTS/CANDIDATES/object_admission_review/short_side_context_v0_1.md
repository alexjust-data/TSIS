# Short-Side Context - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Short-Side Context`
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
El lado short puede estar presionado, crowded o restringido.
```

### Phenomenon Description

```text
Fuentes short con lag, short volume, days-to-cover,
borrow availability, locate state o SSR pueden alterar
la interpretacion de squeezes, fallos y riesgo operativo.
```

### Observable Information To Preserve

```text
Informacion observable con lag/as-of sobre presion,
crowding o restricciones del lado short.
```

### Primary Informational Uncertainty

```text
Que condicion short-side conocida en t afecta el instrumento:
crowding, presion short, cobertura potencial, restricciones
o disponibilidad operativa para short.
```

### Semantic Capability

```text
Short-Side Context debe representar contexto short as-of
sin confundirse con Trading Activity, Order Flow Pressure
o outcomes posteriores.
```

### Candidate Information Object

```text
Short-Side Context
```

## 3. Minimal Semantic Identity

`Short-Side Context` deja de ser `Short-Side Context` si desaparece:

```text
1. fuente short o borrow/locate/SSR gobernada;
2. lag/as_of explicito;
3. semantica de crowding, presion o restriccion short;
4. separacion frente a actividad intradia general;
5. separacion frente a order flow/agresion intradia.
```

No necesita para conservar su identidad:

```text
volume general;
signed flow;
aggressor imbalance;
price movement;
future squeeze outcome;
borrow/locate no gobernado.
```

## 4. Irreducibility Criterion

```text
Short-Side Context es irreducible si TSIS necesita preservar
condiciones del lado short conocidas as-of,
y esa informacion no queda suficientemente preservada por
Trading Activity, Order Flow Pressure, Fundamental Context,
Liquidity o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Short-Side Context | En dominio vecino |
| --- | --- | --- |
| `short_volume_ratio` | actividad short reportada/con lag | no Trading Activity intradia general |
| `days_to_cover` | crowding/cobertura potencial | no liquidity truth |
| `borrow_availability` | restriccion short si fuente gobernada | execution context |
| `SSR` | restriccion/regla de shorting | no order flow pressure |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Trading Activity` | Short volume es actividad? | No. Fuente, lag y semantica de crowding son distintas. | `not_absorbed` |
| Absorb into `Order Flow Pressure` | Short activity es agresion vendedora? | No necesariamente. Short data no equivale a signed/aggressor flow intradia. | `not_absorbed` |
| Absorb into `Fundamental Context` | Float/capital structure lo cubre? | No. Short-side preserva posicion/restriccion/crowding short. | `not_absorbed` |
| Absorb into `Outcomes` | Squeeze posterior valida short context? | No. Squeeze/failure posterior es outcome. | `outcome_separated` |
| Split `Borrow/Locate` | Borrow merece Objeto propio? | No por defecto; queda bloqueado sin fuente gobernada. | `blocked_extension` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `days_to_cover_model` | core candidate | Requiere as_of/lag. |
| `short_volume_ratio_model` | core/extension | No equivale a activity general. |
| `short_interest_z_model` | extension | Requiere ventana/baseline. |
| `borrow_availability_model` | blocked | Requiere fuente gobernada. |
| `locate_state_model` | blocked | Requiere fuente gobernada. |
| `ssr_state_model` | blocked/pending | Requiere fuente/regla gobernada. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima es representar contexto short conocido as-of,
con lag declarado y semantica separada de activity/order-flow.
```

## 9. Temporal Legality Constraints

```text
1. Lag/as_of obligatorio.
2. No usar revisiones posteriores.
3. Borrow/locate/SSR bloqueados sin fuente gobernada.
4. Short volume no equivale a agresion intradia.
5. Squeeze/failure posterior es outcome.
```

## 10. State Impact If Eventually Accepted

```text
market_state_short_extension:
    days_to_cover, short_volume_ratio, lag/as_of.

blocked_until_source:
    borrow availability, locate state, SSR.

outcomes:
    squeeze response, failure, covering outcomes.
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
1. Exigir lag/as_of.
2. No fusionar con Trading Activity.
3. No tratar short volume como aggressor flow.
4. Bloquear borrow/locate/SSR sin fuente gobernada.
5. Separar squeeze posterior como outcome.
```

## 12. Open Questions For Formal Admission

```text
1. Que fuentes short son gobernadas?
2. Days-to-cover entra en core o extension?
3. Short volume ratio es suficiente sin short interest PIT?
4. Borrow/locate/SSR quedan bloqueados hasta que fuente?
5. Como se declara lag por proveedor?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\short_side_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\short_side_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\short_side_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

