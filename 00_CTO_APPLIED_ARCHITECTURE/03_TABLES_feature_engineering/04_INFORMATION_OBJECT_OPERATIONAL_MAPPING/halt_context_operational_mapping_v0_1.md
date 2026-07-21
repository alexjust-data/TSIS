# Halt Context - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Halt Context` con modelos aprobados, capacidades
derivables, variables candidatas, tablas fuente y perfiles de State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Halt Context
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
Halt Context debe ser capaz de representar interrupcion, tipo, recencia
y contexto observable de halt/resume de forma legal as-of.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `halt_state_model` | `mapped_as_core_minimum` | Is halted at t. |
| `halt_type_model` | `mapped_with_taxonomy_restriction` | Halt type/source context. |
| `halt_recency_model` | `mapped_as_core_minimum` | Recency since halt or resume. |
| `resume_context_model` | `restricted_extension_only` | Resume context by timestamp legality. |
| `halt_clustering_model` | `research_only_until_validated` | Not core State. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `halts__halt_type` | `halt_type` | `006_halts_table` | `market_state_halt_context`, `event_state_context` | Taxonomy/source availability required. |
| `halts__is_halted_at_t` | `is_halted_at_t` | `006_halts_table`, state builder candidate | `market_state_halt_context`, `event_state_context` | `halt_start <= t` and resume null or resume > t, using known timestamps. |
| `halts__minutes_since_halt_start` | `minutes_since_halt_start` | `006_halts_table`, state builder candidate | `market_state_halt_context`, `event_state_context` | Halt start known by t. |
| `halts__minutes_since_resume` | `minutes_since_resume` | `006_halts_table`, state builder candidate | `market_state_halt_context`, `event_state_context` | Resume timestamp known by t. |
| `halt_clustering_STATE` | `halt_clustering_STATE` | future state builder | research only | Requires validation; not core. |

## 5. Source Tables And Temporal Legality

```text
006_halts_table:
    halt / resume timestamps, type and source context.
```

## 6. Operational Restrictions

```text
1. Halt/resume timestamps must be available as-of.
2. Halt type requires source and taxonomy policy.
3. Resume context depends on decision_timestamp.
4. Halt clustering is research-only until validated.
5. Post-resumption price/liquidity response is outcome or timestamp-dependent context.
6. Event Window Context remains infrastructure, not an Information Object.
```

## 7. Required Builder Validation

```text
1. Halt and resume timestamps are legal as-of.
2. is_halted_at_t handles open-ended halts correctly.
3. minutes_since_halt_start/resume do not use unknown timestamps.
4. Halt type taxonomy/source is declared.
5. Post-resumption outcomes do not enter X before observable.
```

## 8. Authorized And Non-Authorized Consumers

Authorized:

```text
builder_validation_design
market_state_integration_design_after_builder_validation
event_state_integration_design_after_market_state_integration
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
post_resumption_outcome_truth
```

## 9. Review Triggers

```text
1. Halt source or taxonomy policy changes.
2. Resume timestamp availability policy changes.
3. Halt clustering is validated for State.
4. Builder Validation detects timestamp leakage.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\halt_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

