# Price Location / Structure - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Price Location / Structure`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Price Location / Structure
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = price_location_structure_operational_mapping_v0_1.md
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
market_state_integration_authorized = false_until_builder_validation_execution
```

## 2. Validation Target

```text
builder_validation_profile = price_location_core_anchor_distances_v0_1
mapping_profile = price_location_structure_first_mapping_v0_1
profile_role = market_state_core_minimum
validation_scope = non_production_design_validation
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

No incluir:

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

## 3. Required Gates

| Gate | Pass condition | Fail condition |
| --- | --- | --- |
| `governance` | Object admitted, ontology frozen, operational mapping exists. | Builder treats mapping as production authority. |
| `profile_selection` | Only session/prior-close anchor models are selected. | VWAP, HOD/LOD, range position or pullback/retrace enter minimum profile. |
| `session_open_cutoff` | Current session open is known before use. | Session open is consumed before availability. |
| `prior_close_resolution` | Prior close resolves from prior valid closed session. | Prior close uses current or unknown value. |
| `closed_bar_price_ref` | Intraday price_ref comes from closed bar. | Open/incomplete bar enters X. |
| `semantic_context` | Return ratios are interpreted as location only under this Object. | Builder conflates Location with Price Movement. |
| `future_extrema_separation` | Future HOD/LOD, MFE, MAE and future return are absent from X. | Any future extrema/outcome enters State input. |

## 4. Expected Sources

```text
004_master_daily_table
013_ohlcv_1m_quote_guarded
014_master_intraday_bar_table_candidate
```

Prohibited source for X:

```text
008_outcomes_table
```

## 5. Required Builder Checks

```text
1. `prior_close` proceeds from the previous valid closed session.
2. `daily__open_price` for current session is not consumed before session open.
3. `price_ref` intraday proceeds from closed bar.
4. `return_vs_session_open_ratio` is interpreted as location only when
   the consumer declares `Price Location / Structure`.
5. `return_vs_prior_close_ratio` is interpreted as location only when
   the consumer declares `Price Location / Structure`.
6. HOD/LOD final of current day does not appear before market close.
7. VWAP distance does not enter without policy.
8. distance_to_session_hod/lod and session_range_position do not enter without formula/capability id.
9. Pullback/retrace does not encode strategy labels.
10. Future extrema and outcomes do not appear in X.
11. Every candidate variable traces to capability, source, temporal rule and State profile.
```

## 6. Output Authority

If executed and passed, this validation may authorize:

```text
price_location_structure_market_state_integration_design
```

It still does not authorize:

```text
production_market_state_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_location_structure_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\price_location_structure_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

