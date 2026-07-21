# Price Movement - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta el Information Object admitido `Price Movement` con
modelos de representacion aprobados, capacidades derivables, variables fisicas
candidatas, tablas fuente y perfiles de State previstos.

No reabre la identidad cientifica de `Price Movement`.
No modifica schemas.
No cambia builders.
No materializa tablas.
No promociona datasets.
No autoriza consumo productivo de `Market State` ni `Event State`.

---

## 1. Governance Input

```text
information_object = Price Movement
formal_admission = accepted_with_restrictions
formal_admission_doc =
  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_movement_formal_admission_v0_1.md

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
Este mapping autoriza disenar la resolucion operativa de Price Movement.
No autoriza todavia ejecutar builders productivos ni consumir variables como
State oficial.
```

---

## 2. Approved Semantic Capability

Capacidad semantica aprobada:

```text
Price Movement debe ser capaz de representar el cambio observable
del precio entre referencias temporales declaradas,
de forma temporalmente legal.
```

Condicion operativa minima:

```text
El mapping debe poder resolver al menos un modelo que mida cambio observable
del precio contra una referencia legal, usando solo informacion conocida en
decision_timestamp y sin outcomes futuros.
```

---

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `intraday_return_to_reference_model` | `mapped_as_core_minimum` | Core as-of movement against legal reference. |
| `opening_gap_movement_model` | `mapped_with_open_cutoff` | Discontinuous movement from prior close to session open. |
| `daily_closed_return_model` | `mapped_as_prior_or_after_close_context` | Historical daily movement; current session only after close. |
| `bar_to_bar_movement_model` | `blocked_pending_capability_decision` | Requires decision on canonical `intraday__bar_return`. |
| `move_speed_model` | `mapped_as_extension_pending_variant_policy` | Dynamic movement rate over governed window W. |
| `move_acceleration_model` | `restricted_extension_pending_variant_policy` | Second-order movement; noise-sensitive. |
| `momentum_persistence_model` | `not_core_pending_formula_or_subobject_decision` | Directional persistence; not synonym for Price Movement. |
| `reversal_fade_model` | `not_core_boundary_model` | Boundary with pattern research and Price Location / Structure. |
| `future_response_model` | `prohibited_as_state_input` | Outcome only. |

---

## 4. Capability To Physical Mapping

### Daily Reference And Historical Context

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `daily__prior_close` | `prior_close` | `004_master_daily_table` | `market_state_daily_context`, reference input for intraday | Prior valid closed session only; legal as-of. |
| `daily__gap_pct` | `gap_pct` | `004_master_daily_table` | `market_state_opening_context` | Legal only after session open and valid prior close. |
| `daily__daily_return_pct` | `daily_return_pct` | `004_master_daily_table` | `market_state_daily_historical_context` | Prior sessions allowed as-of; current session only after market close. |
| `daily__intraday_return_pct` | `intraday_return_pct` | `004_master_daily_table` | `market_state_daily_historical_context` | Prior sessions allowed as-of; current session only after market close. |

### Intraday Core Movement

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__bar_open_price` | `open` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | source input for closed-bar movement | Closed bar only. |
| `intraday__bar_close_price` | `close` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | source input for `price_ref` | Closed bar only. |
| `intraday__return_vs_prior_close_ratio` | `return_vs_prior_close_ratio` | `014_master_intraday_bar_table_candidate`, future state builder | `market_state_core`, `market_state_intraday` | `price_ref` from closed bar; prior close known by t. |
| `intraday__return_vs_session_open_ratio` | `return_vs_session_open_ratio` | `014_master_intraday_bar_table_candidate`, future state builder | `market_state_core`, `market_state_intraday` | `price_ref` from closed bar; session open known by t. |
| `intraday__return_vs_segment_open_ratio` | `return_vs_segment_open_ratio` | future state builder | `market_state_intraday_extension`, `event_state_window_context` | Requires governed segment policy; segment open must be known by t. |

### Intraday Dynamic Extensions

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__move_speed_W` | `move_speed_W` | candidate derived from `014_master_intraday_bar_table_candidate` | `market_state_intraday_extension`, `event_state_window_context` | Requires declared W, return_ref, price_ref, scope, min_periods and closed bars. |
| `intraday__move_acceleration_W` | `move_acceleration_W` | candidate derived from speed sequence | restricted extension | Requires declared W, speed formula id, elapsed policy, min_periods and noise policy. |

---

## 5. First Phase B Mapping Profile

El primer perfil debe conservar la capacidad semantica minima sin abrir una
matriz grande de horizontes.

```text
profile_id = price_movement_first_mapping_v0_1
profile_role = market_state_core_minimum
profile_status = mapping_ready_pending_builder_validation
```

Modelos incluidos:

```text
intraday_return_to_reference_model
opening_gap_movement_model
daily_closed_return_model_for_prior_history
```

Capacidades minimas:

```text
daily__prior_close
daily__gap_pct
intraday__bar_close_price
intraday__return_vs_prior_close_ratio
intraday__return_vs_session_open_ratio
```

Capacidades opcionales para primera validacion:

```text
daily__daily_return_pct_as_prior_history
daily__intraday_return_pct_as_prior_history
intraday__return_vs_segment_open_ratio_with_segment_policy
```

No incluir en la primera validacion:

```text
intraday__bar_return_as_canonical_atom
intraday__move_speed_W
intraday__move_acceleration_W
momentum_persistence_model
reversal_fade_model
future_response_model
```

---

## 6. Source Tables And Temporal Legality

| Source | Role in Price Movement | Legal use | Restriction |
| --- | --- | --- | --- |
| `004_master_daily_table` | Daily prior close, gap and closed daily returns. | Prior sessions as-of; current session fields only after their observation cutoff. | Current-day `daily_return_pct` and `intraday_return_pct` prohibited intraday before close. |
| `013_ohlcv_1m_quote_guarded` | Upstream guarded 1m OHLCV source for closed-bar price refs. | Closed bars only. | Must preserve repair/quote-guard lineage. |
| `014_master_intraday_bar_table_candidate` | Candidate closed-bar state surface for intraday returns. | `bar_end <= decision_timestamp`. | Builder must enforce closed-bar cutoff and formula policy. |
| `008_outcomes_table` | Future return / MFE / MAE labels. | Outcomes only. | Prohibited as input to `Price Movement` State. |

Temporal legality rules:

```text
1. No current daily final return before market close.
2. No intraday bar before bar close.
3. No segment return without declared segment boundary known by t.
4. No speed/acceleration without fully closed windows and min_periods.
5. No future return, MFE, MAE or post-decision path as State input.
```

---

## 7. Blocked Or Excluded Mappings

| Candidate | Mapping decision | Reason |
| --- | --- | --- |
| `intraday__bar_return` | `blocked_pending_capability_decision` | Not yet approved as canonical atomic capability; can be expressed through declared return-to-reference models until decided. |
| `intraday__pullback_ratio_W` | `excluded_from_core` | Boundary with Price Location / Structure or pattern research. |
| `intraday__retrace_ratio_W` | `excluded_from_core` | Boundary with Price Location / Structure or pattern research. |
| `intraday__vwap_distance_ratio` | `move_to_price_location_structure` | Location against VWAP, not movement identity. |
| `daily__daily_range_pct` | `move_to_volatility_range_state` | Range/amplitude, not movement identity. |
| `daily__volatility_Nd` | `move_to_volatility_range_state` | Dispersion/uncertainty, not movement identity. |
| `volume`, `dollar_volume`, `trade_count` | `move_to_trading_activity` | Participation evidence, not price movement. |
| `signed_flow`, `aggressor_imbalance` | `move_to_order_flow_pressure` | Directional flow pressure, not observed price displacement. |
| `future__future_return_H` | `prohibited_as_feature` | Outcome only. |
| `future__mfe_H` | `prohibited_as_feature` | Outcome only. |
| `future__mae_H` | `prohibited_as_feature` | Outcome only. |

---

## 8. Required Builder Validation

Builder Validation debe comprobar:

```text
1. `prior_close` procede de la sesion valida anterior.
2. `gap_pct` no existe antes de session open.
3. `price_ref` intradia procede de barra cerrada.
4. `return_vs_prior_close_ratio` y `return_vs_session_open_ratio`
   usan referencias conocidas en decision_timestamp.
5. El dia actual no usa `daily_return_pct` ni `intraday_return_pct`
   antes de market close.
6. Las fuentes 1m conservan lineage quote-guarded / repair policy.
7. `intraday__bar_return` no se trata como capacidad canonica hasta
   decision explicita.
8. Speed, acceleration, momentum y reversal/fade no entran en el perfil
   minimo sin variant policy.
9. Outcomes futuros no aparecen en X.
10. Cada variable fisica queda trazada a capability, source, temporal rule
    y State profile previsto.
```

Primer gate recomendado:

```text
builder_validation_profile = price_movement_core_reference_returns_v0_1
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
1. Se aprueba `intraday__bar_return` como capacidad atomica canonica.
2. Se define policy canonica para speed, acceleration o momentum.
3. Momentum se promueve como Information Object independiente.
4. Cambia la frontera con Price Location / Structure.
5. Cambia la frontera con Volatility / Range State.
6. Cambia la politica de prior_close, session_open, segment_open o price_ref.
7. Cambia el lineage de `013_ohlcv_1m_quote_guarded` o `014_master_intraday_bar_table_candidate`.
8. Builder Validation detecta leakage temporal, formula ambiguity o source mismatch.
9. Market State Integration requiere otro perfil minimo.
```

---

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_domain_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\price_movement_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\price_movement_candidate_object_definition_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\price_movement_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_movement_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\013_ohlcv_1m_quote_guarded\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
```
