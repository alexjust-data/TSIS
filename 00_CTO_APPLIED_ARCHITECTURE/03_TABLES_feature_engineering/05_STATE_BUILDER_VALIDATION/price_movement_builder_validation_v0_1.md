# Price Movement - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Price Movement`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Price Movement
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = price_movement_operational_mapping_v0_1.md
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
builder_validation_profile = price_movement_core_reference_returns_v0_1
mapping_profile = price_movement_first_mapping_v0_1
profile_role = market_state_core_minimum
validation_scope = non_production_design_validation
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

No incluir:

```text
intraday__bar_return_as_canonical_atom
intraday__move_speed_W
intraday__move_acceleration_W
momentum_persistence_model
reversal_fade_model
future_response_model
```

## 3. Required Gates

| Gate | Pass condition | Fail condition |
| --- | --- | --- |
| `governance` | Object admitted, ontology frozen, operational mapping exists. | Builder treats mapping as production authority. |
| `profile_selection` | Only core reference-return models are selected. | Speed, acceleration, momentum or reversal enter the minimum profile. |
| `prior_close_resolution` | `prior_close` resolves from prior valid session. | Prior close uses current or unknown session value. |
| `gap_cutoff` | `gap_pct` appears only after session open. | Gap exists before open is observable. |
| `closed_bar_price_ref` | Intraday price_ref comes from closed bar. | Open/incomplete bar enters X. |
| `daily_after_close` | Current `daily_return_pct` and `intraday_return_pct` are after-close only. | Current daily final return is used intraday. |
| `outcome_separation` | Future return, MFE, MAE and post-decision path are absent from X. | Any future outcome enters State input. |

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
2. `gap_pct` is not available before session open.
3. `price_ref` intraday proceeds from closed bar.
4. `return_vs_prior_close_ratio` and `return_vs_session_open_ratio`
   use references known at decision_timestamp.
5. Current daily final returns are not used before market close.
6. 1m sources preserve quote-guarded / repair lineage.
7. `intraday__bar_return` is not treated as canonical until approved.
8. Speed, acceleration, momentum and reversal/fade remain out of the minimum profile.
9. Future outcomes do not appear in X.
10. Every candidate variable traces to capability, source, temporal rule and State profile.
```

## 6. Output Authority

If executed and passed, this validation may authorize:

```text
price_movement_market_state_integration_design
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
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\price_movement_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\price_movement_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

