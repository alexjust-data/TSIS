# Trading Activity - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-20`
Scope: `information_object_to_physical_state_bridge`

Este documento conecta el Information Object admitido `Trading Activity`
con modelos de representacion, capacidades derivables, variables fisicas
candidatas, tablas fuente y perfiles de State.

No modifica schemas.
No cambia builders.
No materializa tablas.
No promociona datasets.
No autoriza consumo productivo sin validacion posterior.

## Phase Boundary Update

```text
artifact_role = pilot_vertical_artifact
phase_b_ratification =
  trading_activity_operational_mapping_phase_b_ratification_v0_1.md
TSIS_Market_Ontology_v1 = FROZEN
Phase_B_Engineering = OPEN_FOR_GOVERNED_MAPPING
production_builder_authorized = false
state_consumption_authorized = false
```

Este mapping demostro el proceso para `Trading Activity` como piloto.
La autoridad Phase B vigente vive en la ratificacion indicada arriba.
Sigue sin autorizar consumo productivo, schemas, builders ni materializacion.
## 1. Governance Input

```text
information_object = Trading Activity
formal_admission = accepted_with_restrictions
formal_admission_doc =
  C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
```

Capacidad semantica aprobada:

```text
Representar la intensidad observable de participacion negociada
de forma temporalmente legal.
```

## 2. Mapping Principle

```text
Information Object
    -> approved Representation Model
        -> derivable capability
            -> candidate physical variable
                -> source table
                    -> State profile
                        -> Builder validation
```

Regla:

```text
Una variable compartida puede servir a varios Objetos.
El mapping debe declarar el significado local de esa variable
para Trading Activity.
```

## 3. Approved Operational Models

| Operational model | Mapping status | Primary State role |
| --- | --- | --- |
| `daily_absolute_participation_model` | `mapped_with_temporal_restriction` | `market_state_daily_context` |
| `daily_relative_participation_model` | `mapped_with_prior_only_baseline` | `market_state_daily_context` |
| `intraday_absolute_accumulation_model` | `mapped_for_first_builder_validation` | `market_state_intraday` / first vertical pass |
| `intraday_pace_model` | `mapped_as_conditional_variant` | `market_state_intraday_extension` |
| `trade_window_intensity_model` | `mapped_as_microstructure_extension` | `market_state_microstructure_extension` / `event_state_window_context` |
| `trade_size_distribution_model` | `mapped_as_restricted_extension` | optional microstructure texture only |
| `economic_turnover_model` | `mapped_partially` | dollar participation only; float turnover blocked |

## 4. Capability To Physical Mapping

### Daily Context

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `daily__volume` | `volume` | `004_master_daily_table` | `market_state_daily_context` | Current session final value only after close; prior sessions allowed as-of. |
| `daily__transaction_count` | `transaction_count` | `004_master_daily_table` | `market_state_daily_context` | Current session final value only after close; prior sessions allowed as-of. |
| `daily__dollar_volume` | `dollar_volume` | `004_master_daily_table` | `market_state_daily_context` | Current session final value only after close; prior sessions allowed as-of. |
| `daily__volume_20d_avg` | `volume_20d_avg` | `004_master_daily_table` | `market_state_daily_context` | Prior valid closed sessions only. |
| `daily__rvol_20d` | `rvol_20d` | `004_master_daily_table` | `market_state_daily_context` | Current daily final rvol after close only; intraday use must be prior/as-of context. |

### Intraday Closed-Bar Accumulation

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__bar_volume` | `volume` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Closed bar only. |
| `intraday__bar_transaction_count` | `transaction_count` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Closed bar only; count policy required. |
| `intraday__session_volume_to_time` | `session_volume_to_time` | `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Sum bars with `bar_end <= decision_timestamp`. |
| `intraday__session_dollar_volume_to_time` | `session_dollar_volume_to_time` | `014_master_intraday_bar_table_candidate` | `market_state_intraday` | Sum legal closed bars; requires vwap/close dollar policy. |

### Intraday Pace Variant

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `intraday__volume_pace_W` | `volume_pace_W` | `014_master_intraday_bar_table_candidate` plus prior baseline | `market_state_intraday_extension` | Requires declared window, baseline, min_periods, calendar and as-of policy. |
| `intraday__dollar_volume_pace_W` | `dollar_volume_pace_W` | `014_master_intraday_bar_table_candidate` plus prior baseline | `market_state_intraday_extension` | Requires declared dollar policy and prior-only expectation. |

### Trade Window Intensity

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `trades__trade_count_WINDOW` | `trade_count_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_extension`, `event_state_window_context` | Variant required; `window_end <= decision_timestamp`. |
| `trades__trade_rate_WINDOW` | `trade_rate_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_extension`, `event_state_window_context` | Variant required; closed window and min_rows. |
| `trades__total_volume_WINDOW` | `trades_total_volume_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_extension`, `event_state_window_context` | Closed window; valid trade size. |
| `trades__dollar_volume_WINDOW` | `trades_dollar_volume_WINDOW` | `015_microstructure_features_table_candidate` | `market_state_microstructure_extension`, `event_state_window_context` | Closed window; valid price and size. |

### Restricted Microstructure Texture

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `trades__size_median_WINDOW` | `trades_size_median_WINDOW` | `015_microstructure_features_table_candidate` | restricted extension | Closed window; min_rows; not core. |
| `trades__size_p90_WINDOW` | `trades_size_p90_WINDOW` | `015_microstructure_features_table_candidate` | restricted extension | Closed window; min_rows; not core. |

## 5. Blocked Or Excluded Mappings

| Candidate | Mapping decision | Reason |
| --- | --- | --- |
| `reference__float_pit_state` | `blocked` | No governed PIT float source; true float turnover not allowed. |
| `trades__signed_flow_WINDOW` | `excluded_from_trading_activity` | Belongs to `Order Flow Pressure` unless admitted separately. |
| `trades__aggressor_imbalance_WINDOW` | `excluded_from_trading_activity` | Directional/aggressor semantics. |
| `scanner thresholds` | `selection_surface_only` | `018` can explain selection, not core state evidence. |
| future returns / MFE / MAE | `prohibited` | Outcomes are not State inputs. |

## 6. First Vertical Implementation Profile

El primer recorrido vertical debe validar el perfil mas pequeno que conserva
la capacidad semantica sin abrir extensiones pesadas.

```text
profile_id = trading_activity_first_vertical_v0_1
profile_role = market_state_intraday_minimum
profile_status = design_ready_pending_builder_validation
```

Modelos incluidos:

```text
daily_relative_participation_model
intraday_absolute_accumulation_model
```

Capacidades minimas:

```text
daily__volume_20d_avg
daily__rvol_20d
intraday__bar_volume
intraday__session_volume_to_time
```

Capacidades opcionales para la primera validacion:

```text
daily__dollar_volume
intraday__bar_transaction_count
intraday__session_dollar_volume_to_time
```

No incluir en la primera validacion:

```text
trade_window_intensity_model
trade_size_distribution_model
scanner_activity_threshold_model
directional_activity_model
true_float_turnover_model
```

## 7. State Profile Mapping

### market_state_core

```text
Trading Activity no debe convertir el core en una mega-tabla.
El core solo debe declarar que el Objeto existe y si el perfil minimo
esta disponible/legal para `decision_timestamp`.
```

Campos conceptuales candidatos:

```text
trading_activity__profile_status
trading_activity__as_of_utc
trading_activity__quality_flag
```

### market_state_daily_context

```text
Usa contexto diario cerrado o historico previo.
No usa volumen final de la sesion actual antes del cierre.
```

### market_state_intraday

```text
Usa barras 1m cerradas y acumulados hasta decision_timestamp.
Es el perfil principal para la primera validacion vertical.
```

### market_state_microstructure_extension

```text
Usa ventanas de trades cerradas.
Debe permanecer separada del core por coste, densidad y riesgo de ruido.
```

### event_state_window_context

```text
Event State debe reutilizar Market State base y, si corresponde,
agregar contexto de ventana cerrado respecto a un evento.

post_event puede ser valido para investigacion, pero no input
para decisiones anteriores o simultaneas al evento.
```

## 8. Builder Resolution Requirements

El builder debe poder resolver:

```text
1. Objeto admitido:
   Trading Activity.

2. Perfil solicitado:
   first_vertical / daily_context / intraday / microstructure_extension.

3. Modelo aprobado para ese perfil.

4. Capacidades requeridas y opcionales.

5. Variable fisica candidata.

6. Tabla fuente y version/lineage.

7. Regla temporal aplicable.

8. Quality flag y as_of/cutoff.
```

## 9. Operational Blockers

```text
1. Confirmar fuente operativa oficial de 014 y su status frente a 013.
2. Definir convencion exacta de `decision_timestamp` vs cierre de barra.
3. Definir alias fisicos finales en contrato de Market State.
4. Definir quality flags minimos para volumen/cobertura.
5. Definir politica de variantes para pace.
6. Mantener float turnover bloqueado hasta float PIT oficial.
7. Mantener 018 fuera de causal State core.
```

## 10. Output Decision

```text
operational_mapping_decision = ready_for_builder_validation_design
state_consumption_authorized = false
builder_validation_required = true
market_state_integration_required = true
```

## 11. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\trading_activity_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\object_admission_review\trading_activity_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\DOMAIN_DEFINITIONS\trading_activity_representation_landscape_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\004_master_daily_table\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\014\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\015\table_representation_audit_ES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\018\table_representation_audit_ES.md
```
