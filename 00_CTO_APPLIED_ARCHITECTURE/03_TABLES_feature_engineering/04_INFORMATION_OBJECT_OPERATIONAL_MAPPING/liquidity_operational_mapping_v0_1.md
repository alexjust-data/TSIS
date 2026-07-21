# Liquidity - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Liquidity` con modelos aprobados, capacidades
derivables, variables candidatas, tablas fuente y perfiles de State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Liquidity
formal_admission = accepted_with_restrictions
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

## 2. Approved Semantic Capability

```text
Liquidity debe ser capaz de representar condiciones observables de facilidad,
coste, disponibilidad o impacto esperado de negociar de forma temporalmente
legal.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `quoted_spread_cost_model` | `mapped_as_core_minimum` | Observable L1 crossing cost context. |
| `displayed_depth_model` | `mapped_with_L1_restriction` | Visible top-of-book availability. |
| `quote_availability_model` | `mapped_as_extension_pending_window_policy` | Quote usability/availability context. |
| `tradability_proxy_model` | `restricted_proxy_only` | Activity-based proxy, not liquidity truth. |
| `effective_spread_model` | `blocked_until_alignment_and_side_policy` | Advanced cost from trades+quotes. |
| `price_impact_model` | `blocked_until_formula_and_boundary` | Impact proxy requiring causal formula and boundary. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `quotes__bid_price` | `bid_price` | raw quotes, `015_microstructure_features_table_candidate` | source input | Source timestamp <= t; valid price. |
| `quotes__ask_price` | `ask_price` | raw quotes, `015_microstructure_features_table_candidate` | source input | Source timestamp <= t; valid price. |
| `quotes__bid_size` | `bid_size` | raw quotes, `015_microstructure_features_table_candidate` | source input | Source timestamp <= t; valid displayed size. |
| `quotes__ask_size` | `ask_size` | raw quotes, `015_microstructure_features_table_candidate` | source input | Source timestamp <= t; valid displayed size. |
| `quotes__spread_bps_row` | `spread_bps` | `015_microstructure_features_table_candidate` | `market_state_liquidity_core` | Valid ask > bid and mid > 0. |
| `quotes__spread_bps_median_WINDOW` | `quotes_spread_bps_median_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_liquidity_core` | Closed window, min_rows and valid spread rows. |
| `quotes__spread_bps_p90_WINDOW` | `quotes_spread_bps_p90_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_liquidity_extension` | Closed window, min_rows and valid spread rows. |
| `quotes__top_depth_mean_WINDOW` | `quotes_top_depth_mean_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_liquidity_core` | L1 only; closed window and valid depth rows. |
| `trade_quote__effective_spread_bps_WINDOW` | `effective_spread_bps_WINDOW` | future trade-quote aligned surface | blocked extension | Requires alignment, side classifier and confidence policy. |
| `trade_quote__price_impact_proxy_WINDOW` | `price_impact_proxy_WINDOW` | future trade-quote aligned surface | blocked extension | Requires formula version and boundary with outcomes/OFP. |

## 5. Source Tables And Temporal Legality

```text
015_microstructure_features_table_candidate:
    current candidate for L1 quote-derived spread/depth windows.

raw quotes:
    upstream source for bid/ask price and displayed size.

future trade-quote aligned surface:
    required for effective spread and impact models.
```

## 6. Operational Restrictions

```text
1. L1 displayed depth is not full market depth.
2. L2/MBO and hidden liquidity remain blocked without governed source.
3. Effective spread requires trade-quote alignment and side classifier.
4. Realized spread uses future midpoint and is outcome/research only.
5. Dollar volume/trade count are tradability proxies only.
6. OFI and signed flow belong to Order Flow Pressure.
```

## 7. Required Builder Validation

```text
1. Quote windows are closed and timestamp-legal.
2. Spread rows enforce ask > bid and mid > 0.
3. Depth rows are L1-only and labelled as displayed availability.
4. Effective spread and impact do not enter core before alignment gates.
5. No future fills, slippage or outcome fields enter X.
```

## 8. Authorized And Non-Authorized Consumers

Authorized:

```text
builder_validation_design
market_state_integration_design_after_builder_validation
research_planning
feature_contract_planning
```

Not authorized:

```text
production_market_state_builder
state_consumption
canonical_schema_change
physical_state_materialization
dataset_promotion
execution_truth
```

## 9. Review Triggers

```text
1. Governed L2/MBO source appears.
2. Trade-quote alignment and side classifier are approved.
3. Effective spread or impact formula is approved.
4. Builder Validation detects quote-quality leakage or timestamp ambiguity.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\liquidity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

