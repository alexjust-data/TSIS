# TSIS Market Ontology v1 - Cross-Object Ontology Review

Status: `cross_object_ontology_review_v0_1`
Date: `2026-07-21`
Decision: `passes_with_restrictions`
Scope: `phase_a_scientific_transversal_review_pre_freeze`

Este documento ejecuta la revision cientifica transversal de los 12
Information Objects principales de `TSIS Market Ontology v1`.

No crea nuevos Objetos.
No reabre los Object Admission Reviews.
No congela todavia `TSIS Market Ontology v1`.
No autoriza Operational Mapping.
No autoriza Builder Validation.
No autoriza Market State Integration.
No autoriza cambios de schema.
No autoriza variables fisicas.
No autoriza consumo operativo de State.

## 1. Review Decision

```text
ontology_under_review = TSIS Market Ontology v1
review_type = cross_object_scientific_review
review_result = passes_with_restrictions
freeze_recommendation = proceed_to_freeze_artifact
formal_admissions_reviewed = 12
formal_admissions_missing = 0
objects_requiring_merge_before_freeze = 0
objects_requiring_split_before_freeze = 0
new_information_objects_required_before_freeze = 0
phase_b_engineering_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
builder_change_authorized = false
operational_mapping_authorized_now = false
```

Lectura:

```text
La ontologia principal de mercado es cientificamente coherente
como sistema v1 y puede pasar al artefacto de freeze.

El freeze aun debe documentarse en un artefacto separado.
La ingenieria sigue diferida.
```

## 2. Inputs Reviewed

| Information Object | Formal Admission | Scientific identity | Operational readiness |
| --- | --- | --- | --- |
| `Trading Activity` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Price Movement` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Price Location / Structure` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Volatility / Range State` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Liquidity` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Market Microstructure State` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Order Flow Pressure` | `accepted_with_restrictions` | `accepted` | `blocked_for_state_until_alignment_and_classifier` |
| `News / Catalyst Context` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Fundamental Context` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Short-Side Context` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Broad Market Context` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |
| `Halt Context` | `accepted_with_restrictions` | `accepted` | `accepted_with_restrictions` |

Decision:

```text
all_primary_objects_have_formal_admission = true
all_scientific_identities_accepted = true
all_operational_authority_withheld = true
```

## 3. Coverage Review

La cobertura v1 queda organizada en tres capas cientificas.

### Instrument Observable State

```text
Price Movement
Price Location / Structure
Volatility / Range State
Trading Activity
```

Estas piezas preservan:

```text
como cambia el precio;
donde esta situado el precio;
cuanta amplitud/dispersion existe;
cuanta participacion negociada observable existe.
```

Resultado:

```text
instrument_observable_state_coverage = sufficient_for_v1
```

### Tradability / Microstructure / Flow

```text
Liquidity
Market Microstructure State
Order Flow Pressure
```

Estas piezas preservan:

```text
coste/disponibilidad de negociar;
condicion observable de quote/tape;
presion direccional inferida del flujo.
```

Resultado:

```text
tradability_microstructure_flow_coverage = sufficient_for_v1_with_restrictions
```

Restriccion principal:

```text
Order Flow Pressure queda bloqueado para State hasta alignment,
side classifier y confidence policy gobernados.
```

### External / As-Of Context

```text
News / Catalyst Context
Fundamental Context
Short-Side Context
Broad Market Context
Halt Context
```

Estas piezas preservan:

```text
contexto externo publicado as-of;
estructura fundamental PIT;
condicion short-side con lag/as-of;
entorno amplio de mercado;
interrupciones observables de mercado.
```

Resultado:

```text
external_context_coverage = sufficient_for_v1_with_asof_restrictions
```

### Out Of Scope For Ontology v1

No bloquean el freeze:

```text
Execution Outcomes;
future returns;
MFE / MAE;
future range / future volatility;
future news response;
post-resumption response not decision-safe;
Event Window Context as generic temporal infrastructure;
Quality/Governance as administrative authority;
production builders;
physical State schemas;
materialized datasets.
```

Decision:

```text
coverage_gaps_blocking_v1_freeze = none
future_candidate_spaces_exist = true
```

## 4. Irreducibility Audit

| Object | Primary informational uncertainty | Irreducibility decision |
| --- | --- | --- |
| `Trading Activity` | Cuanta participacion negociada observable existe. | Not absorbed by Liquidity, Price Movement or Order Flow Pressure. |
| `Price Movement` | Como cambia el precio hasta t. | Not absorbed by Location, Volatility or Activity. |
| `Price Location / Structure` | Donde esta situado el precio frente a anchors legales. | Not absorbed by Movement or Volatility. |
| `Volatility / Range State` | Cuanta amplitud o dispersion observable existe. | Not absorbed by Movement or Location. |
| `Liquidity` | Que tan negociable es el instrumento en t. | Not absorbed by Trading Activity, Microstructure or Execution. |
| `Market Microstructure State` | En que condicion observable de quote/tape esta el mercado. | Not absorbed by Liquidity, Order Flow Pressure or Quality. |
| `Order Flow Pressure` | Si el flujo ejerce presion compradora o vendedora. | Not absorbed by Activity, Liquidity, Microstructure or Price Movement. |
| `News / Catalyst Context` | Que informacion externa esta disponible as-of. | Not absorbed by Event State, Fundamentals or Outcomes. |
| `Fundamental Context` | Que estructura fundamental PIT condiciona el instrumento. | Not absorbed by News, Short-Side, Liquidity or Outcomes. |
| `Short-Side Context` | Que condicion short-side conocida en t afecta el instrumento. | Not absorbed by Activity, Order Flow Pressure or Fundamentals. |
| `Broad Market Context` | En que entorno amplio observable ocurre el estado. | Not absorbed by instrument Price Movement, News or Fundamentals. |
| `Halt Context` | Si existe interrupcion observable as-of y con que recencia/tipo. | Not absorbed by Microstructure, Event State or Event Window Context. |

Resultado:

```text
all_objects_irreducible_for_v1 = true
irreducibility_confidence = high
```

## 5. Shared Evidence Audit

Shared evidence queda permitido. Shared identity no se asume.

| Shared evidence | Objects involved | V1 decision |
| --- | --- | --- |
| `close`, `open`, `prior_close` | `Price Movement`, `Price Location / Structure` | Movement mide cambio; Location mide posicion frente a referencia. |
| `high_so_far`, `low_so_far` | `Price Location / Structure`, `Volatility / Range State` | Location usa coordenada/proximidad; Volatility usa amplitud/dispersion. |
| `volume`, `trade_count`, `dollar_volume` | `Trading Activity`, `Liquidity` | Activity mide participacion; Liquidity solo puede usarlos como tradability proxy. |
| `VWAP` | `Price Location / Structure`, `Trading Activity` | VWAP puede depender de participacion para construccion, pero distance-to-VWAP es location. |
| `spread`, `depth`, `two_sided_rows` | `Liquidity`, `Market Microstructure State` | Liquidity pregunta coste/disponibilidad; Microstructure pregunta interpretabilidad quote/tape. |
| `trades + quotes` | `Market Microstructure State`, `Order Flow Pressure`, `Liquidity` | OFP requiere direccion/classifier; Liquidity coste; Microstructure context. |
| `float`, `shares`, `market_cap` | `Fundamental Context`, `Trading Activity`, `Liquidity` | Fundamental preserva PIT structure; turnover/liquidity uses remain restricted by PIT source. |
| `published_utc`, `as_of_utc` | `News / Catalyst Context`, `Event State` | News preserva fuente externa; Event State contextualiza timing. |
| `halt_start`, `halt_end`, `minutes_since_resume` | `Halt Context`, `Event State`, `Event Window Context` | Halt Context preserva interrupcion; Event Window is infrastructure. |

Resultado:

```text
shared_evidence_rule_holds = true
shared_identity_confusions_blocking_freeze = none
```

## 6. Boundary Adjudications

### Price Dynamics Boundary

```text
Price Movement
    = cambio / direccion / intensidad / persistencia.

Price Location / Structure
    = posicion frente a anchors legales.

Volatility / Range State
    = amplitud / rango / dispersion.
```

Decision:

```text
price_dynamics_boundary = clean_for_v1
```

### Activity / Liquidity / Microstructure / Flow Boundary

```text
Trading Activity
    = participacion negociada observable.

Liquidity
    = coste, disponibilidad y facilidad de negociar.

Market Microstructure State
    = condicion observable de quote/tape que afecta interpretabilidad.

Order Flow Pressure
    = direccion, agresion e imbalance inferidos del flujo.
```

Decision:

```text
activity_liquidity_microstructure_flow_boundary = clean_for_v1_with_restrictions
```

Restricciones:

```text
1. Dollar volume/trade count are Trading Activity evidence,
   and only Liquidity proxies when explicitly declared.

2. Spread/depth are Liquidity when interpreted as cost/availability,
   and Microstructure when interpreted as quote/tape state.

3. OFP remains blocked for State until alignment/classifier/confidence.
```

### External Context Boundary

```text
News / Catalyst Context
    = external publication/catalyst as-of.

Fundamental Context
    = financial/economic/corporate structure PIT.

Short-Side Context
    = short-side pressure/crowding/restriction with lag/as-of.

Broad Market Context
    = broad market observable context.

Halt Context
    = observable market interruption context.
```

Decision:

```text
external_context_boundary = clean_for_v1_with_source_lag_restrictions
```

### Event Boundary

```text
Event Window Context = temporal infrastructure.
Event State = event-relative state context.
Halt Context = observable interruption Information Object.
News Context = external source/catalyst Information Object.
```

Decision:

```text
event_boundary = clean_for_v1
```

## 7. Critical Pending Concepts

| Concept | V1 ruling | Reason | Review trigger |
| --- | --- | --- | --- |
| `Momentum` | `representation_model_or_subobject_pending` | Directional persistence is not all Price Movement. | Reopen if it proves independent primary uncertainty. |
| `Relative Activity` | `representation_model` | It scales participation; it does not create new identity by default. | Reopen if relative participation becomes irreducible across objects. |
| `Economic Turnover` | `model_with_split_roles` | Dollar turnover can represent activity; true float turnover blocked without float PIT. | Reopen when float PIT source is governed. |
| `Trade Size Distribution` | `restricted_extension_only` | It may be Trading Activity texture or Microstructure texture, but not v1 Object. | Reopen if microstructure texture proves distinct primary uncertainty. |
| `Hidden Liquidity` | `future_candidate_not_v1_object` | Scientifically plausible, but no admitted candidate/review and no governed L2/MBO/hidden source. | Reopen when source and object review exist. |
| `Market Regime` | `broad_market_representation_model_pending` | Proxy/model for Broad Market Context, not separate Object by default. | Reopen if regime identity is irreducible. |
| `Risk-On/Off` | `restricted_proxy_model` | Proxy, not macro truth. | Reopen with governed definition and validation. |
| `Sentiment / Novelty` | `blocked_extension_models` | Require versioned model, baseline and leakage policy. | Reopen when governed models exist. |
| `Borrow / Locate / SSR` | `blocked_short_side_extensions` | Require governed sources and lag/as-of policy. | Reopen when source governance exists. |
| `Halt Clustering` | `research_only` | No core identity without validation. | Reopen if promoted as knowledge object. |

Decision:

```text
critical_pending_concepts_block_freeze = false
all_pending_concepts_have_v1_ruling = true
```

## 8. Minimal Semantic Identity Compatibility

Each object defines what makes it stop being itself.

Compatibility result:

```text
minimal_semantic_identity_coverage = complete
minimal_semantic_identity_conflicts = none
```

Identity anchors:

| Object | Minimal identity anchor |
| --- | --- |
| `Trading Activity` | observable traded participation and intensity in a legal window |
| `Price Movement` | observable price change between declared temporal references |
| `Price Location / Structure` | observable price position against legal structural anchors |
| `Volatility / Range State` | observable amplitude/range/dispersion in declared window |
| `Liquidity` | observable cost/availability/tradability conditions |
| `Market Microstructure State` | observable quote/tape condition and interpretability context |
| `Order Flow Pressure` | inferred directional flow with alignment/classifier/confidence |
| `News / Catalyst Context` | external information available as-of with attribution |
| `Fundamental Context` | fundamental/corporate PIT structure with revision control |
| `Short-Side Context` | short-side condition with source and lag/as-of |
| `Broad Market Context` | broad market reference/proxy observable as-of |
| `Halt Context` | observable halt/resume/suspension state and timing |

## 9. Operational Readiness Separation

The ontology is scientifically coherent before engineering execution.

Current operational state:

```text
Phase A = active_until_freeze
Phase B = deferred
Operational Mapping = not_authorized_now
Builder Validation = not_authorized_now
Market State Integration = not_authorized_now
State consumption = false
Physical variables = false
Schema changes = false
Production builders = false
```

Important asymmetry:

```text
Order Flow Pressure is scientifically accepted,
but operationally blocked for State until alignment,
side classifier and confidence policy are governed.
```

This is not a contradiction.

It confirms that:

```text
scientific_identity != operational_readiness
```

## 10. Freeze Criteria Audit

| Freeze criterion | Result |
| --- | --- |
| 12 main Information Objects have Formal Admission | `pass` |
| Each decision is accepted / accepted_with_restrictions / rejected | `pass` |
| Each Object has approved semantic capability | `pass` |
| Each Object has minimal semantic identity | `pass` |
| Critical boundaries resolved or marked as restriction | `pass_with_restrictions` |
| Cross-object review documented | `pass_by_this_document` |
| No open doubt changes another Object identity before freeze | `pass_with_review_triggers` |
| State consumption remains false | `pass` |
| Phase B remains closed | `pass` |

Decision:

```text
freeze_criteria_status = satisfied_with_restrictions
freeze_artifact_required_next = true
```

## 11. Cross-Object Review Conclusion

The 12 admitted Information Objects form a coherent v1 ontology:

```text
Market Ontology v1
    -> instrument observable state
    -> tradability / microstructure / flow context
    -> external / as-of context
```

No Object requires merge before freeze.
No Object requires split before freeze.
No missing domain blocks freeze.
No shared evidence conflict blocks freeze.
No unresolved boundary changes the identity of another Object.

Final decision:

```text
TSIS Market Ontology v1
    cross_object_review = passed_with_restrictions
    next_required_artifact = TSIS Market Ontology v1 Freeze
    phase_b_engineering = still_deferred
```

## 12. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\AGENT.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_movement_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_location_structure_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\volatility_range_state_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\liquidity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\market_microstructure_state_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\order_flow_pressure_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\news_catalyst_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\fundamental_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\short_side_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\broad_market_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\halt_context_formal_admission_v0_1.md
```
