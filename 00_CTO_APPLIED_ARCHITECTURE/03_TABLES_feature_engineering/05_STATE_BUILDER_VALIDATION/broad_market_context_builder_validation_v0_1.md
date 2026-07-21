# Broad Market Context - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Broad Market Context`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Broad Market Context
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = broad_market_context_operational_mapping_v0_1.md
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
builder_validation_profile = broad_market_index_context_core_v0_1
mapping_profile = market_state_broad_context
profile_role = market_state_context_minimum
validation_scope = non_production_design_validation
```

Modelos incluidos:

```text
index_return_context_model
index_range_context_model_as_context
risk_on_off_proxy_model_as_restricted_extension
market_regime_model_as_restricted_representation
coverage_state_model_as_quality_context
```

No incluidos:

```text
macro_economic_context_model
ungoverned_market_regime_truth
future_market_response
future_instrument_response
```

## 3. Required Resolution Gates

```text
gate_1_object_governance =
  Broad Market Context admitted with restrictions and mapped with restrictions.

gate_2_source_timestamp_legality =
  regime/index source timestamps and cutoffs are legal as-of.

gate_3_prior_close_policy =
  previous close references are governed and available.

gate_4_proxy_definition =
  risk-on/off proxy has versioned definition if enabled.

gate_5_regime_boundary =
  market regime remains representation candidate, not new Object in v1.

gate_6_macro_block =
  macro fields remain excluded until source/calendar/as_of policy.

gate_7_outcome_separation =
  future broad or instrument response does not enter X.
```

## 4. Expected Source Resolution

```text
012_regime_context_table / regime pilot:
  regime_intraday_return
  regime_close_to_previous_close_return
  regime_high_to_open_return
  regime_low_to_open_return
  regime_intraday_range_pct
```

Blocked sources:

```text
future macro/economic source
ungoverned macro calendar
future response or outcome tables
```

## 5. Required Checks

```text
1. Regime/index source timestamps are legal as-of.
2. Current final index values are not used before availability.
3. Prior close policy is explicit.
4. Proxy definitions are versioned.
5. Macro fields are absent from core output.
6. Instrument Price Movement is not re-owned by Broad Market Context.
7. Lineage includes source table, index universe, cutoff, version and quality flag.
```

## 6. Output Authority

Passing this validation may authorize only:

```text
broad_market_context_market_state_integration_design
```

It does not authorize:

```text
production_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
ungoverned_macro_truth
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\broad_market_context_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\broad_market_context_formal_admission_v0_1.md
```
