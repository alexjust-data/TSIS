# Order Flow Pressure - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Order Flow Pressure` con modelos aprobados,
capacidades candidatas, tablas fuente y gates requeridos.

`Order Flow Pressure` queda mapeado conceptualmente, pero bloqueado para
State hasta que existan trade-quote alignment, side classifier y confidence
policy gobernados.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Order Flow Pressure
formal_admission = accepted_with_restrictions
operational_mapping_decision = mapped_but_operationally_blocked_for_state
operational_mapping_phase_b_authorized = true
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
physical_materialization_authorized = false
dataset_promotion_authorized = false
builder_validation_required = true
market_state_integration_required = true_after_unblock
event_state_integration_required = true_after_unblock
operational_promotion_authorized = false_until_phase_b_gates
```

## 2. Approved Semantic Capability

```text
Order Flow Pressure debe ser capaz de representar signo, agresion,
imbalance o presion direccional observable del flujo de ordenes
de forma temporalmente legal y con confianza declarada.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `bid_hit_ask_lift_model` | `blocked_until_alignment_policy` | Scientific core candidate. |
| `signed_flow_model` | `blocked_until_side_classifier` | Core directional flow candidate. |
| `aggressor_imbalance_model` | `blocked_until_classifier_confidence_policy` | Core imbalance candidate. |
| `ofi_l1_model` | `restricted_L1_extension_pending_ordering_policy` | L1 pressure proxy. |
| `alignment_confidence_model` | `mandatory_support_model` | Required support model for any future consumption. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `trades__bid_hit_ask_lift_WINDOW` | `bid_hit_ask_lift_WINDOW` | future trade-quote aligned surface | blocked core candidate | Requires closed window, classifier, alignment and confidence policy. |
| `trades__signed_flow_WINDOW` | `signed_flow_WINDOW` | future trade-quote aligned surface | blocked core candidate | Requires side classification and sign policy. |
| `trades__aggressor_imbalance_WINDOW` | `aggressor_imbalance_WINDOW` | future trade-quote aligned surface | blocked core candidate | Requires classifier confidence and timestamp policy. |
| `trade_quote__alignment_lag_ms` | `alignment_lag_ms` | future trade-quote aligned surface | support / validation | Closed window; alignment policy required. |
| `trade_quote__alignment_confidence` | `alignment_confidence` | future trade-quote aligned surface | support / validation | Classifier/rule version required. |
| `trade_quote__ofi_l1_WINDOW` | `ofi_l1_WINDOW` | future trade-quote aligned surface | restricted extension | L1-only; event ordering and formula policy required. |

## 5. Source Tables And Temporal Legality

```text
raw trades:
    trade timestamps, price and size.

raw quotes / L1 quote surface:
    bid/ask context for alignment and side classification.

future trade-quote aligned surface:
    required before any State use.
```

## 6. Operational Restrictions

```text
1. No State consumption until alignment policy is approved.
2. No signed flow without side classifier and confidence policy.
3. Price movement alone cannot infer order-flow pressure.
4. Total volume/trade count belongs to Trading Activity.
5. Spread/depth belongs to Liquidity when used as cost/availability.
6. Quote state without direction belongs to Market Microstructure State.
```

## 7. Required Builder Validation

```text
1. Trade and quote clocks are aligned under declared policy.
2. Classifier version and confidence threshold are present.
3. Windows are closed and timestamp-legal.
4. Low-confidence signed variables are masked or excluded.
5. No future price response or execution outcome enters X.
```

## 8. Authorized And Non-Authorized Consumers

Authorized:

```text
alignment_policy_design
classifier_validation_design
builder_validation_design_after_unblock
research_planning
```

Not authorized:

```text
state_consumption
production_market_state_builder
production_event_state_builder
canonical_schema_change
physical_state_materialization
dataset_promotion
live_trading_consumption
```

## 9. Review Triggers

```text
1. Trade-quote alignment policy is approved.
2. Side classifier and confidence policy are approved.
3. OFI L1 formula is approved.
4. Builder Validation detects timestamp/order ambiguity.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\order_flow_pressure_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

