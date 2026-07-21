# Trading Activity - Phase B Operational Mapping Ratification v0.1

Status: `phase_b_mapping_ratification_v0_1`
Date: `2026-07-21`
Scope: `pilot_vertical_to_governed_phase_b_mapping`

Este documento ratifica el mapping piloto de `Trading Activity` como artefacto
usable dentro de Phase B gobernada, con restricciones.

No sustituye el mapping piloto.
No reabre la identidad cientifica de `Trading Activity`.
No modifica schemas.
No cambia builders.
No materializa tablas.
No promociona datasets.
No autoriza consumo productivo de `Market State` ni `Event State`.

## 1. Governance Input

```text
information_object = Trading Activity
formal_admission = accepted_with_restrictions
pilot_mapping_doc =
  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md

ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_a_status = CLOSED
phase_b_status = OPEN

ratification_decision = ratified_as_governed_phase_b_mapping_with_restrictions
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
Trading Activity debe ser capaz de representar la intensidad observable
de participacion negociada de forma temporalmente legal.
```

## 3. Approved Representation Models

| Representation model | Ratification status | Operational role |
| --- | --- | --- |
| `daily_absolute_participation_model` | `ratified_with_temporal_restriction` | Prior/closed daily participation context. |
| `daily_relative_participation_model` | `ratified_with_prior_only_baseline` | Historical baseline / abnormal participation context. |
| `intraday_absolute_accumulation_model` | `ratified_as_core_minimum` | First governed intraday participation profile. |
| `intraday_pace_model` | `extension_pending_variant_policy` | Pace against governed prior/as-of baseline. |
| `trade_window_intensity_model` | `extension_pending_window_policy` | Event/window trade intensity. |
| `trade_size_distribution_model` | `restricted_extension_only` | Microstructure texture only. |
| `economic_turnover_model` | `mapped_partially` | Dollar participation only; true float turnover blocked. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `daily__volume` | `volume` | `004_master_daily_table` | `market_state_daily_context` | Current final only after close; prior sessions as-of. |
| `daily__transaction_count` | `transaction_count` | `004_master_daily_table` | `market_state_daily_context` | Current final only after close; prior sessions as-of. |
| `daily__dollar_volume` | `dollar_volume` | `004_master_daily_table` | `market_state_daily_context` | Current final only after close; price/volume valid. |
| `daily__volume_20d_avg` | `volume_20d_avg` | `004_master_daily_table` | `market_state_daily_context` | Prior valid closed sessions only. |
| `daily__rvol_20d` | `rvol_20d` | `004_master_daily_table` | `market_state_daily_context` | Current final only after close; intraday baseline use must be prior/as-of. |
| `intraday__bar_volume` | `volume` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Closed bar only. |
| `intraday__bar_transaction_count` | `transaction_count` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Closed bar only; count policy required. |
| `intraday__session_volume_to_time` | `session_volume_to_time` | `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Sum legal closed bars with `bar_end <= decision_timestamp`. |
| `intraday__session_dollar_volume_to_time` | `session_dollar_volume_to_time` | `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Closed bars only; vwap/close dollar policy required. |

## 5. Source Tables And Temporal Legality

```text
004_master_daily_table:
    daily closed / prior participation context.

013_ohlcv_1m_quote_guarded:
    guarded closed-bar OHLCV source.

014_master_intraday_bar_table_candidate:
    intraday accumulation candidate.

015_microstructure_features_table_candidate:
    trade-window extensions only, not core minimum.
```

## 6. Operational Restrictions

```text
1. True float turnover remains blocked without governed float PIT.
2. Intraday pace requires variant policy, baseline, calendar and min_periods.
3. Trade-window intensity requires closed windows and min_rows.
4. Directional activity belongs to Order Flow Pressure.
5. Short activity belongs to Short-Side Context.
6. Scanner thresholds are selection surfaces only.
```

## 7. Required Builder Validation

```text
1. Daily final values are not used intraday before close.
2. Prior baselines use prior valid sessions only.
3. Intraday accumulation uses only closed bars.
4. Dollar volume policy declares vwap/close fallback.
5. No directional/sign/aggressor fields enter Trading Activity.
6. True float turnover remains blocked.
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
production_event_state_builder
state_consumption
canonical_schema_change
physical_state_materialization
dataset_promotion
live_trading_consumption
```

## 9. Review Triggers

```text
1. Governed float PIT source appears.
2. Intraday pace policy changes.
3. Trade-window intensity becomes core requirement.
4. Builder Validation detects leakage or formula ambiguity.
5. Market State Integration requires another minimal profile.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

