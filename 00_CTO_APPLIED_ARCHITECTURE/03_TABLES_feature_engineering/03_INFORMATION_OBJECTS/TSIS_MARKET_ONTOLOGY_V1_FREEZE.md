# TSIS Market Ontology v1 - Freeze Act

Status: `ontology_v1_frozen`
Date: `2026-07-21`
Scope: `phase_a_closure_phase_b_opening`

Este documento es el acta institucional de congelacion de `TSIS Market
Ontology v1`.

No es un documento metodologico adicional.
No reabre la admision cientifica de los Information Objects.
No define Operational Mapping.
No autoriza builders de produccion, consumo de State, schemas fisicos ni
materializaciones operativas.

---

## 1. Decision Institucional

```text
ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
effective_date = 2026-07-21

objects_admitted = 12
cross_object_review = passed_with_restrictions
freeze_criteria_status = satisfied_with_restrictions

phase_a_status = CLOSED
phase_b_status = OPEN
phase_b_scope = governed_engineering

new_information_objects_allowed_in_v1 = false

operational_mapping_phase_b_authorized = true
builder_validation_authorized = after_operational_mapping
market_state_integration_authorized = after_builder_validation
event_state_integration_authorized = after_market_state_integration
operational_promotion_authorized = false_until_phase_b_gates

production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
physical_materialization_authorized = false
dataset_promotion_authorized = false
```

La ontologia queda congelada como dependencia cientifica estable para la
ingenieria posterior.

Phase B queda abierta exclusivamente como fase de implementacion gobernada:

```text
Operational Mapping
    -> Builder Validation
        -> Market State Integration
            -> Event State Integration
                -> Operational Promotion
```

---

## 2. Evidencia De Freeze

La decision se apoya en los siguientes artefactos:

```text
cross_review:
    03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

formal_admissions:
    03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/

object_admission_reviews:
    03_INFORMATION_OBJECTS/CANDIDATES/object_admission_review/
```

Resultado de la revision transversal:

```text
formal_admissions_reviewed = 12
objects_requiring_merge_before_freeze = 0
objects_requiring_split_before_freeze = 0
new_information_objects_required_before_freeze = 0
review_result = passes_with_restrictions
freeze_recommendation = proceed_to_freeze_artifact
```

---

## 3. Objetos Admitidos En v1

Los Information Objects admitidos en `TSIS Market Ontology v1` son:

```text
1. Trading Activity
2. Price Movement
3. Price Location Structure
4. Volatility Range State
5. Liquidity
6. Market Microstructure State
7. Order Flow Pressure
8. News Catalyst Context
9. Fundamental Context
10. Short Side Context
11. Broad Market Context
12. Halt Context
```

Estos objetos forman la frontera cientifica de `TSIS Market Ontology v1`.

---

## 4. Regla De Lock

Ningun nuevo Information Object entra en `TSIS Market Ontology v1` salvo una
de estas condiciones extraordinarias:

```text
1. evidencia extraordinaria de una primary informational uncertainty ausente;
2. contradiccion estructural demostrada entre identidades admitidas;
3. descubrimiento en Phase B de que un objeto admitido no puede representarse
   operativamente sin perdida de identidad;
4. decision explicita de gobierno para abrir TSIS Market Ontology v1.1 o v2.
```

Cualquier concepto nuevo que no cumpla esas condiciones debe ir a un backlog de
`vNext candidate`, no a `v1`.

---

## 5. Restricciones Conocidas

Estas restricciones no bloquean el freeze porque no invalidan la identidad
cientifica de los objetos. Si bloquean o limitan su uso operativo hasta que
Phase B las resuelva mediante mappings, policies, validators o fuentes
gobernadas.

```text
Trading Activity:
    true_float_turnover requiere float point-in-time;
    economic turnover requiere politica de precio y fuente aprobada.

Price Movement:
    debe excluir variables de resultado futuro;
    MFE, MAE, future return y future range no son State inputs.

Price Location Structure:
    VWAP y anchored levels requieren politica temporal explicita;
    niveles derivados no pueden usar informacion posterior a decision_timestamp.

Volatility Range State:
    realized volatility requiere ventanas legalmente cerradas;
    implied volatility no entra sin fuente y timestamp gobernados.

Liquidity:
    L2, MBO, hidden depth y depth curve quedan bloqueados sin fuente gobernada;
    spread efectivo e impacto requieren trade-quote alignment y policy.

Market Microstructure State:
    quote staleness, queue lifetime y event sequencing requieren timestamp
    policy;
    L2/MBO queda bloqueado hasta fuente gobernada.

Order Flow Pressure:
    queda operativamente bloqueado hasta trade-quote alignment, side
    classification y confidence policy aprobadas.

News Catalyst Context:
    sentiment, novelty y catalyst taxonomy requieren modelos/fuentes
    versionados y as-of policy.

Fundamental Context:
    float, market cap, ratios y fundamentals derivados requieren fuente,
    formulas y point-in-time policy aprobadas.

Short Side Context:
    borrow, locate, short interest y SSR requieren fuentes gobernadas y reglas
    temporales explicitas.

Broad Market Context:
    risk-on/off, market regime y macro truth quedan restringidos hasta fuentes,
    calendario y definiciones aprobadas.

Halt Context:
    halt clustering y post-resumption states quedan research-only salvo
    timestamp legality y fuente oficial gobernada.
```

Restriccion transversal:

```text
future outcomes, labels, MFE, MAE, post-decision response y cualquier variable
que observe informacion posterior a decision_timestamp no pueden entrar como
State input.
```

---

## 6. Autoridad De Phase B

El freeze autoriza iniciar Phase B como ingenieria gobernada, no como
produccion.

Phase B debe implementar la ontologia congelada sin redefinir silenciosamente
sus identidades cientificas.

Orden autorizado:

```text
1. Operational Mapping
2. Builder Validation
3. Market State Integration
4. Event State Integration
5. Operational Promotion
```

La validacion vertical de `Trading Activity` se conserva como:

```text
pilot_vertical_artifact
proof_of_process
not_operational_authority
```

Puede usarse como patron de trabajo, pero no como autorizacion productiva.

---

## 7. Cierre

Con esta acta:

```text
TSIS Market Ontology Phase = CLOSED
TSIS Market Ontology v1 = FROZEN
TSIS Market Ontology v1 Lock = ACTIVE
TSIS Phase B = OPEN
```

El siguiente trabajo institucional ya no es crear mas metodologia ni admitir
mas objetos en `v1`.

El siguiente trabajo institucional es implementar fielmente la ontologia
congelada mediante Operational Mapping, Builder Validation e integracion
gobernada en Market State y Event State.
