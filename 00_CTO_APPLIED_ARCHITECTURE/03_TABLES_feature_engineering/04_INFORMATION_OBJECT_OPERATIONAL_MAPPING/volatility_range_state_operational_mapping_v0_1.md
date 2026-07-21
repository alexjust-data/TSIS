# Volatility / Range State - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `Volatility / Range State` con modelos aprobados,
capacidades derivables, variables candidatas, tablas fuente y perfiles de
State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = Volatility / Range State
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
Volatility / Range State debe ser capaz de representar amplitud,
dispersion, expansion, compresion o inestabilidad observable del precio
de forma temporalmente legal.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `intraday_range_so_far_model` | `mapped_as_core_minimum` | Observable intraday amplitude through t. |
| `daily_range_model` | `mapped_as_prior_or_after_close_context` | Closed daily range context. |
| `rolling_daily_volatility_model` | `extension_pending_variant_policy` | Prior-only rolling dispersion. |
| `rolling_daily_range_model` | `extension_pending_variant_policy` | Prior-only rolling range context. |
| `closed_window_realized_volatility_model` | `blocked_pending_formula_policy` | Intraday/event dispersion in closed window. |
| `compression_expansion_model` | `restricted_extension_only` | Relative state against governed baseline. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__high_so_far` | `high_so_far` | `014_master_intraday_bar_table_candidate` | `market_state_core`, source input | Closed valid bars through t only. |
| `intraday__low_so_far` | `low_so_far` | `014_master_intraday_bar_table_candidate` | `market_state_core`, source input | Closed valid bars through t only. |
| `intraday__range_so_far_ratio` | `range_so_far_ratio` | `014_master_intraday_bar_table_candidate` | `market_state_core`, `market_state_intraday` | `(high_so_far / low_so_far) - 1`; denominator > 0. |
| `daily__daily_range_pct` | `daily_range_pct` | `004_master_daily_table` | `market_state_daily_historical_context` | Prior sessions as-of; current session only after close. |
| `daily__volatility_Nd` | `daily_volatility_Nd` | future state builder | restricted extension | Prior-only N, return input, statistic and min_periods required. |
| `daily__range_Nd` | `daily_range_Nd` | future state builder | restricted extension | Prior-only N, range input, statistic and min_periods required. |

## 5. Source Tables And Temporal Legality

```text
004_master_daily_table:
    daily range and prior historical range/volatility context.

013_ohlcv_1m_quote_guarded:
    upstream guarded 1m OHLCV source.

014_master_intraday_bar_table_candidate:
    high_so_far, low_so_far and range_so_far candidate surface.
```

## 6. Operational Restrictions

```text
1. Current-day final daily high/low/range cannot be used intraday before close.
2. Intraday range uses only closed bars <= decision_timestamp.
3. Rolling daily volatility/range must be prior-only.
4. Realized volatility requires formula, return input, W and min_periods.
5. Range position belongs to Price Location / Structure when interpreted as coordinate.
6. Future range, future volatility, MFE and MAE are outcomes only.
```

## 7. Required Builder Validation

```text
1. high_so_far and low_so_far include only closed valid bars.
2. range_so_far denominator is positive.
3. Current final daily range is after-close only.
4. Rolling variants are prior-only and versioned.
5. No future range/volatility/outcome fields appear in X.
```

## 8. Authorized And Non-Authorized Consumers

Authorized:

```text
builder_validation_design
market_state_integration_design_after_builder_validation
event_state_integration_design_after_market_state_integration
research_planning
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
1. Realized volatility formula is approved.
2. Compression/expansion baseline becomes canonical.
3. Boundary with Price Location / Structure changes.
4. Builder Validation detects leakage or source ambiguity.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\volatility_range_state_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

