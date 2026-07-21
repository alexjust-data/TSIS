# Price Location / Structure - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta el Information Object admitido
`Price Location / Structure` con modelos de representacion aprobados,
capacidades derivables, variables fisicas candidatas, tablas fuente y perfiles
de State previstos.

No reabre la identidad cientifica de `Price Location / Structure`.
No modifica schemas.
No cambia builders.
No materializa tablas.
No promociona datasets.
No autoriza consumo productivo de `Market State` ni `Event State`.

---

## 1. Governance Input

```text
information_object = Price Location / Structure
formal_admission = accepted_with_restrictions
formal_admission_doc =
  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_location_structure_formal_admission_v0_1.md

ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_a_status = CLOSED
phase_b_status = OPEN

operational_mapping_decision = mapped_with_restrictions
operational_mapping_phase_b_authorized = true
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
physical_materialization_authorized = false
dataset_promotion_authorized = false

builder_validation_required = true
market_state_integration_required = true
event_state_integration_required = true
operational_promotion_authorized = false_until_phase_b_gates
```

Lectura:

```text
Este mapping autoriza disenar la resolucion operativa de
Price Location / Structure.
No autoriza todavia ejecutar builders productivos ni consumir variables como
State oficial.
```

---

## 2. Approved Semantic Capability

Capacidad semantica aprobada:

```text
Price Location / Structure debe ser capaz de representar
la posicion contextual del precio frente a referencias estructurales
legalmente conocidas en decision_timestamp.
```

Condicion operativa minima:

```text
El mapping debe poder resolver al menos un modelo que mida distancia,
proximidad o coordenada relativa del precio observable contra un anchor legal,
sin usar anchors finales futuros ni labels de estrategia.
```

---

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `session_anchor_location_model` | `mapped_as_core_minimum` | Position against session open or governed segment anchor. |
| `prior_close_location_model` | `mapped_as_core_minimum` | Position against prior close known as-of. |
| `vwap_location_model` | `mapped_as_extension_pending_vwap_policy` | Distance to VWAP built only with information <= t. |
| `hod_lod_proximity_model` | `mapped_as_extension_pending_distance_formula_ids` | Proximity to high/low observed so far. |
| `range_position_model` | `blocked_pending_formula_and_volatility_boundary` | Coordinate inside observed range; not range amplitude. |
| `pullback_retrace_location_model` | `restricted_boundary_model` | Recent structural distance; may become pattern research. |
| `anchored_vwap_distance_model` | `blocked_until_anchor_policy` | Requires explicit anchor policy and VWAP construction rule. |
| `final_daily_structure_model` | `mapped_as_prior_or_after_close_context` | Prior-day or after-close context only. |
| `future_extrema_location_model` | `prohibited_as_state_input` | Outcome only. |

---

## 4. Capability To Physical Mapping

### Daily And Session Anchors

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `daily__open_price` | `open` | `004_master_daily_table` | `market_state_opening_context`, source input for session anchor | Current session open legal only after session open. |
| `daily__prior_close` | `prior_close` | `004_master_daily_table` | `market_state_daily_context`, reference input for prior-close location | Prior valid closed session only; legal as-of. |
| `intraday__bar_close_price` | `close` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | source input for location price_ref | Closed bar only. |
| `intraday__return_vs_session_open_ratio` | `return_vs_session_open_ratio` | `014_master_intraday_bar_table_candidate`, future state builder | `market_state_core`, `market_state_intraday` | Interpreted as distance to session open; `price_ref` must be closed bar and session open known by t. |
| `intraday__return_vs_prior_close_ratio` | `return_vs_prior_close_ratio` | `014_master_intraday_bar_table_candidate`, future state builder | `market_state_core`, `market_state_intraday` | Interpreted as distance to prior close; prior close known by t. |
| `intraday__return_vs_segment_open_ratio` | `return_vs_segment_open_ratio` | future state builder | `market_state_intraday_extension`, `event_state_window_context` | Requires governed segment policy; segment open must be known by t. |

### VWAP Location

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__bar_vwap` | `vwap` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | source input for VWAP reference | Closed bar VWAP or governed fallback only. |
| `intraday__vwap_distance_ratio` | `vwap_distance_ratio` | candidate derived from `014_master_intraday_bar_table_candidate` | `market_state_intraday_extension` | Requires `vwap_ref`, window, denominator and fallback policy; VWAP built from bars/trades <= t. |

### Observed High / Low Structure

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__high_so_far` | `high_so_far` | `014_master_intraday_bar_table_candidate` | source input for HOD proximity and range coordinate | Max high over closed valid bars through t. |
| `intraday__low_so_far` | `low_so_far` | `014_master_intraday_bar_table_candidate` | source input for LOD proximity and range coordinate | Min low over closed valid bars through t. |
| `distance_to_session_hod` | `distance_to_session_hod` | future state builder | restricted extension | Requires capability/formula id, denominator, price_ref and cutoff policy. |
| `distance_to_session_lod` | `distance_to_session_lod` | future state builder | restricted extension | Requires capability/formula id, denominator, price_ref and cutoff policy. |
| `session_range_position` | `session_range_position` | future state builder | restricted extension | Requires formula id and explicit boundary with Volatility / Range State. |

### Boundary Extensions

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__pullback_ratio_W` | `pullback_ratio_W` | candidate derived from OHLCV 1m | restricted extension / pattern boundary | Requires W, high_ref, current_price_ref, closed bars and non-pattern use. |
| `intraday__retrace_ratio_W` | `retrace_ratio_W` | candidate derived from OHLCV 1m | restricted extension / pattern boundary | Requires W, anchor policy, current price_ref, closed bars and non-pattern use. |
| `anchored_vwap_distance` | `anchored_vwap_distance` | future state builder | blocked extension | Requires anchor definition, VWAP construction policy and cutoff policy. |

---

## 5. First Phase B Mapping Profile

El primer perfil debe conservar la capacidad semantica minima sin abrir
distancias HOD/LOD no registradas ni variantes VWAP ambiguas.

```text
profile_id = price_location_structure_first_mapping_v0_1
profile_role = market_state_core_minimum
profile_status = mapping_ready_pending_builder_validation
```

Modelos incluidos:

```text
session_anchor_location_model
prior_close_location_model
final_daily_structure_model_for_prior_history_only
```

Capacidades minimas:

```text
daily__open_price
daily__prior_close
intraday__bar_close_price
intraday__return_vs_session_open_ratio_as_location
intraday__return_vs_prior_close_ratio_as_location
```

Capacidades opcionales para primera validacion:

```text
intraday__return_vs_segment_open_ratio_with_segment_policy
intraday__bar_vwap_as_source_only
```

No incluir en la primera validacion:

```text
intraday__vwap_distance_ratio
distance_to_session_hod
distance_to_session_lod
session_range_position
intraday__pullback_ratio_W
intraday__retrace_ratio_W
anchored_vwap_distance
final_daily_high_low_current_day_before_close
future_extrema_location_model
```

---

## 6. Source Tables And Temporal Legality

| Source | Role in Price Location / Structure | Legal use | Restriction |
| --- | --- | --- | --- |
| `004_master_daily_table` | Daily open, prior close and after-close daily structure. | Prior sessions as-of; current open only after session open; current final daily structure only after close. | No current-day final HOD/LOD intraday before close. |
| `013_ohlcv_1m_quote_guarded` | Upstream guarded 1m OHLCV source for closed-bar price refs and VWAP inputs. | Closed bars only. | Must preserve repair/quote-guard lineage and VWAP fallback policy. |
| `014_master_intraday_bar_table_candidate` | Candidate closed-bar state surface for anchors, high_so_far, low_so_far and distance formulas. | `bar_end <= decision_timestamp`. | Builder must enforce closed-bar cutoff and source lineage. |
| `008_outcomes_table` | Future extrema, future HOD/LOD, future returns, MFE, MAE. | Outcomes only. | Prohibited as input to `Price Location / Structure` State. |

Temporal legality rules:

```text
1. No intraday bar before bar close.
2. No current final daily high/low before market close.
3. `high_so_far` and `low_so_far` only include closed bars <= t.
4. VWAP references only include bars or trades <= t.
5. Segment anchors require declared boundary known by t.
6. Pullback/retrace anchors require closed windows and non-pattern use.
7. No future extrema, future HOD/LOD, future return, MFE or MAE as State input.
```

---

## 7. Blocked Or Excluded Mappings

| Candidate | Mapping decision | Reason |
| --- | --- | --- |
| `distance_to_session_hod` | `blocked_pending_capability_or_formula_id` | Not registered as atomic capability; requires denominator, price_ref and cutoff policy. |
| `distance_to_session_lod` | `blocked_pending_capability_or_formula_id` | Not registered as atomic capability; requires denominator, price_ref and cutoff policy. |
| `session_range_position` | `blocked_pending_formula_and_boundary` | Must be coordinate-within-range, not Volatility / Range amplitude. |
| `anchored_vwap_distance` | `blocked_until_anchor_policy` | Requires anchor definition and VWAP construction policy. |
| `intraday__vwap_distance_ratio` | `extension_pending_policy` | Requires VWAP window, denominator and fallback policy before builder validation. |
| `intraday__pullback_ratio_W` | `restricted_boundary_model` | May become pattern research; not core location. |
| `intraday__retrace_ratio_W` | `restricted_boundary_model` | May become pattern research; not core location. |
| `opening_gap_movement_model` | `move_to_price_movement_when_change` | Change from prior close to open belongs to Price Movement if interpreted as displacement. |
| `range_amplitude_model` | `move_to_volatility_range_state` | Range size or dispersion is Volatility / Range State, not location. |
| `future_extrema_location_model` | `prohibited_as_feature` | Future extrema are outcomes. |

---

## 8. Required Builder Validation

Builder Validation debe comprobar:

```text
1. `prior_close` procede de la sesion valida anterior.
2. `daily__open_price` de sesion actual no se consume antes de session open.
3. `price_ref` intradia procede de barra cerrada.
4. `return_vs_session_open_ratio` se interpreta como location solo cuando
   el consumer declara `Price Location / Structure`.
5. `return_vs_prior_close_ratio` se interpreta como location solo cuando
   el consumer declara `Price Location / Structure`.
6. `high_so_far` y `low_so_far` usan solo barras cerradas <= t.
7. HOD/LOD final del dia actual no aparece en X antes de market close.
8. VWAP distance no entra sin vwap_ref, denominator, window y fallback policy.
9. distance_to_session_hod/lod y session_range_position no entran sin
   formula/capability id aprobado.
10. Pullback/retrace no codifica labels de estrategia ni setups especificos.
11. Future extrema, future returns, MFE y MAE no aparecen en X.
12. Cada variable fisica queda trazada a capability, source, temporal rule
    y State profile previsto.
```

Primer gate recomendado:

```text
builder_validation_profile = price_location_core_anchor_distances_v0_1
validation_scope = non_production_design_validation
```

---

## 9. Authorized And Non-Authorized Consumers

Autorizados por este mapping:

```text
builder_validation_design
market_state_integration_design_after_builder_validation
event_state_integration_design_after_market_state_integration
research_planning
feature_contract_planning
```

No autorizados por este mapping:

```text
production_market_state_builder
production_event_state_builder
canonical_schema_change
physical_state_materialization
state_consumption
dataset_promotion
live_trading_consumption
feature_contract_promotion
```

---

## 10. Review Triggers

Revisar este mapping si ocurre cualquiera de estos eventos:

```text
1. Se aprueba una VWAP policy canonica.
2. Se aprueban `distance_to_session_hod`, `distance_to_session_lod`
   o `session_range_position` como capacidades atomicas canonicas.
3. Cambia la frontera con Price Movement.
4. Cambia la frontera con Volatility / Range State.
5. Pullback/retrace se promueve como pattern discovery, strategy research
   o Information Object independiente.
6. Se detecta uso intradia ilegal de HOD/LOD final del dia.
7. Cambia la politica de session_open, prior_close, segment_open o price_ref.
8. Cambia el lineage de `013_ohlcv_1m_quote_guarded` o
   `014_master_intraday_bar_table_candidate`.
9. Builder Validation detecta formula ambiguity, source mismatch o leakage.
10. Market State Integration requiere otro perfil minimo.
```

---

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_location_structure_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_location_structure_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\price_location_structure_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_location_structure_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
