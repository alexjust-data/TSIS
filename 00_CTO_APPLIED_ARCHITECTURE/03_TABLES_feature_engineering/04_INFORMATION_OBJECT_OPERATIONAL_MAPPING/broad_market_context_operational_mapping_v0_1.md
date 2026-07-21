# Broad Market Context - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Broad Market Context` con modelos aprobados,
capacidades derivables, variables candidatas, tablas fuente y perfiles de
State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Broad Market Context
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
Broad Market Context debe ser capaz de representar condiciones observables
del mercado amplio o regimen externo disponibles legalmente as-of.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `index_return_context_model` | `mapped_as_core_minimum` | Broad market movement context. |
| `index_range_context_model` | `mapped_as_context_model` | Broad range/risk context. |
| `risk_on_off_proxy_model` | `restricted_extension_pending_definition` | Proxy only. |
| `market_regime_model` | `restricted_representation_pending_validation` | Regime proxy candidate. |
| `coverage_state_model` | `quality_context_only` | Interpretability context. |
| `macro_economic_context_model` | `blocked_until_source_asof_policy` | Macro extension. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `regime__intraday_return` | `regime_intraday_return` | `012_regime_context_table` / regime pilot | `market_state_broad_context` | Source timestamp and cutoff legal. |
| `regime__close_to_previous_close_return` | `regime_close_to_previous_close_return` | `012_regime_context_table` / regime pilot | `market_state_broad_context` | Prior close/source policy required. |
| `regime__high_to_open_return` | `regime_high_to_open_return` | `012_regime_context_table` / regime pilot | `market_state_broad_context_extension` | Source cutoff legal. |
| `regime__low_to_open_return` | `regime_low_to_open_return` | `012_regime_context_table` / regime pilot | `market_state_broad_context_extension` | Source cutoff legal. |
| `regime__intraday_range_pct` | `regime_intraday_range_pct` | `012_regime_context_table` / regime pilot | `market_state_broad_context_extension` | Source cutoff legal. |
| `macro__event_context` | `macro_event_context` | future macro/economic source | blocked extension | Requires calendar, source and as_of policy. |
| `risk_on_off_proxy_STATE` | `risk_on_off_proxy_STATE` | future state builder | restricted extension | Requires definition and validation. |

## 5. Source Tables And Temporal Legality

```text
012_regime_context_table / regime pilot:
    broad/index/regime context candidate source.

future macro/economic source:
    blocked until governed calendar/source/as_of policy exists.
```

## 6. Operational Restrictions

```text
1. Broad market context is not instrument Price Movement.
2. Risk-on/off is proxy only until defined and validated.
3. Market regime is representation candidate, not new Object in v1.
4. Macro truth is blocked without source, calendar and as_of policy.
5. Coverage state is quality context only.
6. Future market/instrument response is outcome only.
```

## 7. Required Builder Validation

```text
1. Regime/index source timestamps are legal as-of.
2. Current final index values are not used before availability.
3. Proxy definitions are versioned.
4. Macro fields remain blocked until source policy exists.
5. Future response does not enter X.
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
ungoverned_macro_truth
```

## 9. Review Triggers

```text
1. Regime source or timestamp policy changes.
2. Risk-on/off proxy is validated or rejected.
3. Macro source/calendar/as_of policy is approved.
4. Builder Validation detects market-source leakage.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\broad_market_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

