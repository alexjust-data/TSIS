# Market Microstructure State - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Market Microstructure State` con modelos aprobados,
capacidades derivables, variables candidatas, tablas fuente y perfiles de
State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Market Microstructure State
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
Market Microstructure State debe ser capaz de representar condiciones
observables de estructura y calidad economica del mercado de cotizacion
de forma temporalmente legal.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `two_sided_quote_state_model` | `mapped_as_core_minimum` | L1 two-sided quote interpretability. |
| `locked_crossed_state_model` | `mapped_as_context_gate` | Quote state context / anomaly gate. |
| `quote_activity_state_model` | `extension_pending_window_policy` | Quote update/activity context. |
| `quote_staleness_lifetime_model` | `blocked_until_timestamp_sequence_policy` | Staleness/lifetime extension. |
| `tape_integrity_context_model` | `quality_context_only` | Interpretability context only. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `quotes__two_sided_rows_WINDOW` | `two_sided_rows_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_core` | Closed window; ask > 0 and bid > 0 policy. |
| `quotes__crossed_rows_WINDOW` | `crossed_rows_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_context` | Closed window; quote quality policy. |
| `quotes__locked_rows_WINDOW` | `locked_rows_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_context` | Closed window; quote quality policy. |
| `quotes__crossed_ratio_pct_two_sided_WINDOW` | `crossed_ratio_pct_two_sided_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_context` | Closed window; denominator policy. |
| `quotes__locked_ratio_pct_two_sided_WINDOW` | `locked_ratio_pct_two_sided_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_context` | Closed window; denominator policy. |
| `quotes__quote_count_WINDOW` | `quote_count_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_extension` | Closed window, min_rows. |
| `quotes__quote_update_rate_WINDOW` | `quote_update_rate_WINDOW` | candidate | restricted extension | Requires window, min_rows and timestamp policy. |
| `quotes__staleness_WINDOW` | `quote_staleness_WINDOW` | candidate | blocked extension | Requires timestamp units and gap policy. |
| `quotes__lifetime_WINDOW` | `quote_lifetime_WINDOW` | candidate | blocked extension | Requires quote sequence/lifetime policy. |

## 5. Source Tables And Temporal Legality

```text
raw quotes:
    upstream L1 bid/ask events.

015_microstructure_features_table_candidate:
    candidate windowed quote-state surface.
```

## 6. Operational Restrictions

```text
1. Spread as execution cost belongs to Liquidity.
2. Depth as availability belongs to Liquidity.
3. OFI/signed/aggressor models belong to Order Flow Pressure.
4. Halts/interruption belong to Halt Context.
5. Staleness/lifetime remain blocked until timestamp/sequence policy.
6. L2/MBO remains blocked without governed source.
```

## 7. Required Builder Validation

```text
1. Quote windows are closed.
2. Two-sided quote policy is explicit.
3. Locked/crossed ratios declare denominator.
4. Quote activity is not confused with Trading Activity.
5. Staleness/lifetime do not enter before timestamp policy.
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
```

## 9. Review Triggers

```text
1. Timestamp/sequence policy is approved.
2. Governed L2/MBO source appears.
3. Boundary with Liquidity or Order Flow Pressure changes.
4. Builder Validation detects quote-source ambiguity.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\market_microstructure_state_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

