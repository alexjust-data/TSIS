# Broad Market Context - Object Admission Review v0.1

Status: `object_admission_review_v0_1`
Date: `2026-07-20`
Scope: `candidate_adversarial_review_pre_formal_admission`

Este documento revisa si el Objeto candidato `Broad Market Context`
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
El entorno general de mercado cambia.
```

### Phenomenon Description

```text
Indices, proxies de regimen, retornos de mercado,
rango intradia, risk-on/off candidates y contexto macro/economico
pueden condicionar la interpretacion de un instrumento.
```

### Observable Information To Preserve

```text
Entorno general de mercado observable as-of que contextualiza
el instrumento, evento o sesion.
```

### Primary Informational Uncertainty

```text
En que contexto general ocurre el estado:
mercado amplio favorable, adverso, volatil, comprimido,
risk-on/risk-off proxy o con cobertura insuficiente.
```

### Semantic Capability

```text
Broad Market Context debe representar contexto de mercado amplio
observable as-of sin afirmar verdad macro o regimen no gobernado.
```

### Candidate Information Object

```text
Broad Market Context
```

## 3. Minimal Semantic Identity

`Broad Market Context` deja de ser `Broad Market Context` si desaparece:

```text
1. referencia observable de mercado amplio;
2. temporalidad as-of;
3. relacion contextual con el instrumento;
4. separacion entre proxy y verdad macro/regimen;
5. cobertura/calidad declarada.
```

No necesita para conservar su identidad:

```text
precio del instrumento individual;
news/catalyst especifico del instrumento;
fundamentals de la empresa;
outcome futuro;
regimen macro no observado.
```

## 4. Irreducibility Criterion

```text
Broad Market Context es irreducible si TSIS necesita preservar
entorno de mercado amplio observable as-of,
y esa informacion no queda suficientemente preservada por
Price Movement del instrumento, News Context, Fundamental Context
o Outcomes.
```

## 5. Shared Evidence Rule

```text
Shared evidence is allowed.
Shared identity is not assumed.
```

| Evidence | En Broad Market Context | En dominio vecino |
| --- | --- | --- |
| `index_return` | contexto amplio | no movimiento del instrumento individual |
| `regime_intraday_range_pct` | rango de mercado amplio | volatility proxy si se modela como dispersion |
| `risk_on_off_state` | proxy candidato | no verdad macro sin definicion gobernada |
| `bar_coverage_state` | cobertura/contexto | quality, no alpha por defecto |

## 6. Boundary / Absorption Tests

| Attack | Question | Review result | Decision |
| --- | --- | --- | --- |
| Absorb into `Price Movement` | Es movimiento del precio? | No. Es movimiento/contexto de mercado amplio, no del instrumento. | `not_absorbed` |
| Absorb into `Volatility / Range` | Es solo range de indice? | No. Range puede ser una dimension, pero el Objeto preserva contexto amplio. | `not_absorbed` |
| Absorb into `News Context` | Macro/news lo cubre? | No. News preserva publicaciones; Broad Market preserva observables de mercado amplio. | `not_absorbed` |
| Absorb into `Quality State` | Coverage state es calidad? | Si, coverage es quality/context, no alpha; pero no absorbe todo el Objeto. | `boundary_confirmed` |
| Split `Market Regime` | Regime merece Objeto separado? | No sin prueba; queda como modelo/proxy candidato. | `representation_model_pending` |

## 6.1 Scientific Review Versus Engineering Readiness

```text
scientific_identity = accepted
operational_readiness = blocked_or_restricted
```

## 7. Representation Models Under Review

| Model | Admission role | Review |
| --- | --- | --- |
| `index_return_context_model` | core candidate | Retornos de mercado amplio as-of. |
| `index_range_context_model` | context model | Rango/riesgo amplio observable. |
| `risk_on_off_proxy_model` | extension/pending | Proxy, no verdad macro. |
| `market_regime_model` | pending | No Objeto separado sin prueba. |
| `coverage_state_model` | quality/context | No alpha por defecto. |
| `macro_economic_context_model` | future extension | Requiere source/as_of policy. |

## 8. Semantic Capability Versus Minimum Model

```text
La condicion minima es preservar contexto amplio observable as-of,
con simbolo/proxy, timestamp, cobertura y significado declarado.
```

## 9. Temporal Legality Constraints

```text
1. as_of obligatorio.
2. No usar cierres finales del dia antes de estar disponibles.
3. Proxies de indice no son verdad macro.
4. Coverage state debe separarse como calidad/contexto.
5. Macro/economic context requiere fuente y calendario as-of.
```

## 10. State Impact If Eventually Accepted

```text
market_state_broad_context_extension:
    index returns, range, proxy risk-on/off, coverage context.

research_only_until_ready:
    macro/economic context, regime states no gobernados.
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
1. Declarar proxies y no tratarlos como verdad macro.
2. Exigir as_of y coverage policy.
3. Separar coverage state como calidad/contexto.
4. No crear Market Regime separado sin prueba de identidad.
5. Bloquear macro/economic context sin fuente gobernada.
```

## 12. Open Questions For Formal Admission

```text
1. Que indices/proxies gobiernan Broad Market Context?
2. Risk-on/off entra como modelo o queda research-only?
3. Coverage state viaja con Broad Market o Quality State?
4. Market Regime debe ser modelo o Objeto futuro?
5. Que fuentes macro/economic son as-of confiables?
```

## 13. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\broad_market_context_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\broad_market_context_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\broad_market_context_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

