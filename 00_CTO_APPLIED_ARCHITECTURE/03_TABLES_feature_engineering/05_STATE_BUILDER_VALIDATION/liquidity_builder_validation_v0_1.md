# Liquidity - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `Liquidity`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = Liquidity
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = liquidity_operational_mapping_v0_1.md
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
builder_validation_profile = liquidity_l1_spread_depth_core_v0_1
mapping_profile = market_state_liquidity_core
profile_role = market_state_core_minimum
validation_scope = non_production_design_validation
```

Modelos incluidos:

```text
quoted_spread_cost_model
displayed_depth_model
quote_availability_model_as_restricted_extension
tradability_proxy_model_as_proxy_only
```

No incluidos:

```text
effective_spread_model
price_impact_model
realized_spread_model
L2_depth_model
hidden_liquidity_model
OFI_or_signed_flow
future_fills_or_slippage
```

## 3. Required Resolution Gates

```text
gate_1_object_governance =
  Liquidity admitted with restrictions and mapped with restrictions.

gate_2_profile_selection =
  builder selects L1 spread/depth profile only.

gate_3_quote_window_legality =
  all quote windows are closed before decision_timestamp.

gate_4_spread_validity =
  ask > bid and mid > 0 for spread rows.

gate_5_depth_semantics =
  top depth is labelled L1 displayed availability, not full depth.

gate_6_blocked_extensions =
  effective spread and impact remain excluded until alignment gates.

gate_7_outcome_separation =
  no fills, slippage, realized spread or future response enters X.
```

## 4. Expected Source Resolution

```text
raw quotes:
  bid_price
  ask_price
  bid_size
  ask_size

015_microstructure_features_table_candidate:
  spread_bps
  quotes_spread_bps_median_WINDOW
  quotes_spread_bps_p90_WINDOW
  quotes_top_depth_mean_WINDOW
```

Blocked sources:

```text
future trade-quote aligned surface
future execution outcome tables
ungoverned L2/MBO sources
```

## 5. Required Checks

```text
1. Source timestamps are <= decision_timestamp.
2. Quote windows are closed and use valid quote rows only.
3. Spread formulas reject invalid bid/ask/mid rows.
4. L1 displayed depth is not promoted as full liquidity depth.
5. Tradability proxies are labelled proxy-only if used.
6. Effective spread and impact are absent from core output.
7. No OFP identity leaks into Liquidity.
8. Lineage includes source table, version, window, cutoff and quality flag.
```

## 6. Output Authority

Passing this validation may authorize only:

```text
liquidity_market_state_integration_design
```

It does not authorize:

```text
production_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
execution_truth
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\liquidity_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\liquidity_formal_admission_v0_1.md
```
