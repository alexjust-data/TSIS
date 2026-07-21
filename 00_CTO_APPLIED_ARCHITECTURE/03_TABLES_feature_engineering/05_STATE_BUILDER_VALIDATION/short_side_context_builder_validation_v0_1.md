# Short-Side Context - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Short-Side Context`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Short-Side Context
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = short_side_context_operational_mapping_v0_1.md
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
builder_validation_profile = short_side_days_to_cover_core_v0_1
mapping_profile = market_state_short_context
profile_role = market_state_context_minimum
validation_scope = non_production_design_validation
```

Modelos incluidos:

```text
days_to_cover_model
short_volume_ratio_model
short_interest_z_model_as_restricted_extension
```

No incluidos:

```text
borrow_availability_model
locate_state_model
ssr_state_model
intraday_signed_short_flow
short_squeeze_outcome
```

## 3. Required Resolution Gates

```text
gate_1_object_governance =
  Short-Side Context admitted with restrictions and mapped with restrictions.

gate_2_source_lag_policy =
  short source lag and as_of availability are explicit.

gate_3_days_to_cover_denominator =
  denominator/source policy is declared.

gate_4_short_volume_denominator =
  short_volume_ratio denominator validity is checked.

gate_5_prior_baseline_policy =
  short_interest_z uses prior-only baseline if enabled.

gate_6_blocked_extensions =
  borrow, locate and SSR remain excluded until governed source/rule policy.

gate_7_outcome_separation =
  future squeeze, covering and response outcomes do not enter X.
```

## 4. Expected Source Resolution

```text
011_short_context_table:
  days_to_cover
  short_volume_ratio

future state builder:
  short_interest_z_WINDOW as restricted extension
```

Blocked sources:

```text
future borrow/vendor source
future locate/broker source
future SSR source
future squeeze or covering outcome tables
```

## 5. Required Checks

```text
1. Source lag is declared and legal as-of.
2. days_to_cover denominator/source is traceable.
3. short_volume_ratio denominator is valid.
4. short_interest_z baseline is prior-only if used.
5. Borrow, locate and SSR fields are absent from core output.
6. General volume is not re-owned from Trading Activity.
7. Lineage includes source table, source lag, as_of, version and quality flag.
```

## 6. Output Authority

Passing this validation may authorize only:

```text
short_side_context_market_state_integration_design
```

It does not authorize:

```text
production_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
ungoverned_borrow_truth
ungoverned_locate_truth
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\short_side_context_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\short_side_context_formal_admission_v0_1.md
```
