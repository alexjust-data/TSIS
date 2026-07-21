# Short-Side Context - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Short-Side Context` con modelos aprobados, capacidades
derivables, variables candidatas, tablas fuente y perfiles de State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Short-Side Context
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
Short-Side Context debe ser capaz de representar crowding, restriccion,
capacidad o disponibilidad observable del lado short de forma legal as-of.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `days_to_cover_model` | `mapped_as_core_minimum` | Short crowding/capacity context. |
| `short_volume_ratio_model` | `mapped_as_context_model` | Short activity context. |
| `short_interest_z_model` | `restricted_extension_pending_baseline_policy` | Relative short crowding. |
| `borrow_availability_model` | `blocked_until_governed_source` | Borrow constraint context. |
| `locate_state_model` | `blocked_until_governed_source` | Locate constraint context. |
| `ssr_state_model` | `blocked_until_source_and_rule_policy` | Short-sale restriction context. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `short__days_to_cover` | `days_to_cover` | `011_short_context_table` | `market_state_short_context` | Source lag/as_of policy required. |
| `short__short_volume_ratio` | `short_volume_ratio` | `011_short_context_table` | `market_state_short_context` | Source lag/as_of policy and denominator validity required. |
| `short__short_interest_z_WINDOW` | `short_interest_z_WINDOW` | future state builder | restricted extension | Prior-only baseline, window and min_periods required. |
| `short__borrow_availability_state` | `borrow_availability_state` | future borrow/vendor source | blocked extension | No governed source today. |
| `short__locate_state` | `locate_state` | future locate/broker source | blocked extension | No governed source today. |
| `short__ssr_state` | `ssr_state` | future SSR source | blocked extension | Requires source, trigger rule and as_of policy. |

## 5. Source Tables And Temporal Legality

```text
011_short_context_table:
    short interest / days-to-cover / short-volume context with source lag.

future borrow / locate / SSR sources:
    blocked until governed.
```

## 6. Operational Restrictions

```text
1. Source lag and as_of policy are mandatory.
2. Borrow and locate are blocked without governed source.
3. SSR is blocked without source and rule policy.
4. General volume belongs to Trading Activity.
5. Intraday signed short flow belongs to Order Flow Pressure when classified.
6. Float/capital structure belongs to Fundamental Context unless short-specific use is governed.
7. Short squeeze/failure response is outcome only.
```

## 7. Required Builder Validation

```text
1. Short source lag is explicit and legal as-of.
2. days_to_cover denominator/source policy is declared.
3. short_volume_ratio denominator is valid.
4. Borrow/locate/SSR blocked fields do not enter X.
5. Future squeeze/covering outcomes do not enter X.
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
ungoverned_borrow_truth
ungoverned_locate_truth
```

## 9. Review Triggers

```text
1. Borrow or locate source becomes governed.
2. SSR source/rule policy is approved.
3. Short interest lag policy changes.
4. Builder Validation detects source lag leakage.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\short_side_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

