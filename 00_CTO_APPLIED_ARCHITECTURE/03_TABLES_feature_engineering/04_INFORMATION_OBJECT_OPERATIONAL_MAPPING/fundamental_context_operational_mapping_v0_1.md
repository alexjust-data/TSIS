# Fundamental Context - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Fundamental Context` con modelos aprobados,
capacidades derivables, variables candidatas, tablas fuente y perfiles de
State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Fundamental Context
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
Fundamental Context debe ser capaz de representar informacion estructural,
contable o de filing observable point-in-time del instrumento.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `filing_recency_model` | `mapped_as_core_minimum` | PIT filing freshness. |
| `statement_recency_model` | `mapped_as_core_minimum` | PIT statement freshness. |
| `statement_value_model` | `extension_pending_field_policy` | Field-level fundamental context. |
| `fundamental_ratio_model` | `restricted_extension_pending_formula_policy` | Derived ratio context. |
| `market_cap_model` | `blocked_until_shares_price_asof_policy` | Derived size context. |
| `float_pit_model` | `blocked_until_governed_PIT_source` | Capital structure context. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `fundamentals__filing_age_days` | `filing_age_days` | `009_fundamentals_asof_table`, state builder candidate | `market_state_instrument_context` | Availability date <= t. |
| `fundamentals__statement_recency_days` | `statement_recency_days` | `009_fundamentals_asof_table`, state builder candidate | `market_state_instrument_context` | Statement availability <= t. |
| `fundamentals__statement_value_FIELD` | `statement_value_FIELD` | `009_fundamentals_asof_table` | restricted extension | Requires FIELD, statement family, source id and revision policy. |
| `fundamentals__ratio_FORMULA` | `fundamental_ratio_FORMULA` | future state builder | restricted extension | Requires formula version, fields and availability policy. |
| `reference__float_pit_state` | `float_pit_state` | reference / filings / vendor | blocked extension | No governed PIT float source today. |
| `market_cap_STATE` | `market_cap_STATE` | future state builder | blocked extension | Requires shares, price, source and as_of policy. |

## 5. Source Tables And Temporal Legality

```text
009_fundamentals_asof_table:
    PIT/as-of filing and statement context.

reference / filings / vendor:
    future source for float PIT and shares data.
```

## 6. Operational Restrictions

```text
1. No post-revision values may be used as knowledge in t.
2. Statement fields require declared field/source/period policy.
3. Ratios require formula version and leakage policy.
4. Market cap requires shares and price as-of policy.
5. Float PIT remains blocked without governed source.
6. News catalysts belong to News / Catalyst Context.
7. Short crowding belongs to Short-Side Context.
```

## 7. Required Builder Validation

```text
1. Filing and statement availability timestamps are <= t.
2. Revision policy prevents post-decision leakage.
3. FIELD and FORMULA variants are declared and versioned.
4. Float and market cap do not enter until source/as_of policy exists.
5. Future fundamental response does not enter X.
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
post_revision_truth
```

## 9. Review Triggers

```text
1. Fundamental source/as_of policy changes.
2. Float PIT source becomes governed.
3. Market cap formula/source policy is approved.
4. Builder Validation detects filing or revision leakage.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\fundamental_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

