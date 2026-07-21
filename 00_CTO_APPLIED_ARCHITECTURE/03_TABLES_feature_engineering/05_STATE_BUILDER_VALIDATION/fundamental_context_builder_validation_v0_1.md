# Fundamental Context - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Fundamental Context`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Fundamental Context
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = fundamental_context_operational_mapping_v0_1.md
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
builder_validation_profile = fundamental_context_filing_statement_recency_core_v0_1
mapping_profile = market_state_instrument_context
profile_role = market_state_context_minimum
validation_scope = non_production_design_validation
```

Modelos incluidos:

```text
filing_recency_model
statement_recency_model
statement_value_model_as_restricted_extension
fundamental_ratio_model_as_restricted_extension
```

No incluidos:

```text
market_cap_model
float_pit_model
post_revision_truth
future_fundamental_response
```

## 3. Required Resolution Gates

```text
gate_1_object_governance =
  Fundamental Context admitted with restrictions and mapped with restrictions.

gate_2_pit_availability =
  filing and statement availability timestamps are <= decision_timestamp.

gate_3_revision_policy =
  post-decision revisions are not visible at t.

gate_4_field_policy =
  FIELD variants declare field, statement family, source id and revision rule.

gate_5_formula_policy =
  ratio variants declare formula version, input fields and availability policy.

gate_6_blocked_extensions =
  float PIT and market cap remain excluded until governed as_of policy.

gate_7_outcome_separation =
  future fundamental or market response does not enter X.
```

## 4. Expected Source Resolution

```text
009_fundamentals_asof_table:
  filing_age_days
  statement_recency_days
  statement_value_FIELD

future state builder:
  fundamental_ratio_FORMULA as restricted extension
```

Blocked sources:

```text
reference / filings / vendor float PIT source
market_cap_STATE
post-revision final truth
```

## 5. Required Checks

```text
1. Filing availability is legal as-of.
2. Statement availability is legal as-of.
3. Revision policy prevents post-decision leakage.
4. FIELD variants are declared and versioned.
5. FORMULA variants are declared and versioned.
6. Float and market cap fields are absent from core output.
7. Lineage includes source table, version, filing/source id, cutoff and quality flag.
```

## 6. Output Authority

Passing this validation may authorize only:

```text
fundamental_context_market_state_integration_design
```

It does not authorize:

```text
production_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
post_revision_truth
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\fundamental_context_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\fundamental_context_formal_admission_v0_1.md
```
