# 016 - market_state_table

## Tipo de documento

Ficha de atributos contractuales. No es una muestra de parquet operativo.

## Documentos fuente usados

Solo se usan estos documentos:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`

## Estado documentado

| item | valor |
| --- | --- |
| dataset_id previsto | `market_state_table_v0_1` |
| unidad | `one instrument state snapshot at one decision timestamp and horizon` |
| grano | `instrument_id + decision_timestamp_utc + state_horizon + state_scope + state_schema_version` |
| primary key | `market_state_id` |
| future root | `E:/TSIS/data/data_foundation_outputs/market_state_table` |
| future layout | `market_state_table_v0_1/decision_year=<YYYY>/decision_month=<MM>/` |
| materialized v0.1 | `false` |

`market_state_table_v0_1` es una tabla objetivo. La tabla oficial no esta materializada en v0.1.

## Atributos obligatorios por contrato

### Identidad

```text
market_state_id
instrument_id
ticker
decision_timestamp_utc
decision_date
decision_session_date
state_horizon
state_scope
state_schema_version
state_builder_version
state_quality_state
```

### Linaje

```text
build_run_id
created_at_utc
source_cutoff_policy_version
leakage_policy_version
feature_namespace_version
component_manifest_hash_bundle
component_build_run_id_bundle
component_quality_bundle
component_availability_bundle
```

### Gates de consumidor

```text
valid_for_event_context_candidate
valid_for_ml_feature_candidate
valid_for_backtest_context_candidate
valid_for_rl_state_candidate
valid_for_rl_training_direct
valid_for_execution_simulator_direct
contains_future_information_without_event_filter
requires_asof_filter
full_universe_claim
execution_truth
```

Valores objetivo por defecto:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
execution_truth = false
requires_asof_filter = true
```

### Disponibilidad de componentes

```text
identity_component_state
calendar_component_state
scanner_component_state
daily_component_state
intraday_component_state
microstructure_component_state
halt_component_state
fundamentals_component_state
news_component_state
short_context_component_state
short_constraints_component_state
regime_component_state
quality_component_state
```

Estados permitidos para componentes:

```text
included_good
included_review
missing_optional
missing_required
blocked_by_policy
not_requested
not_available
```

### Campos as-of requeridos

```text
identity_as_of_utc
calendar_as_of_utc
scanner_as_of_utc
daily_as_of_utc
intraday_as_of_utc
microstructure_as_of_utc
halt_as_of_utc
fundamentals_as_of_utc
news_as_of_utc
short_context_as_of_utc
short_constraints_as_of_utc
regime_as_of_utc
```

Regla obligatoria:

```text
component_as_of_utc <= decision_timestamp_utc
```

## Namespaces de features obligatorios

Toda feature debe empezar por uno de estos prefijos:

```text
identity__
calendar__
scanner__
daily__
intraday__
microstructure__
halt__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
```

No se permite feature sin namespace.

## Columnas prohibidas

```text
outcome__*
label__*
reward__*
action__*
policy__*
fill__*
pnl__*
future__*
strategy__*
signal__*
```

Solo se permiten estas llaves de referencia, sin valores inline de outcome/label/reward:

```text
outcome_join_key
label_join_key
```

## Estados de calidad iniciales

```text
state_good_for_declared_cutoff
state_review_missing_optional_component
state_review_scoped_intraday_component
state_review_microstructure_seed_only
state_review_short_constraints_missing
state_blocked_future_information_detected
state_blocked_required_component_missing
state_blocked_invalid_component_quality
state_bad_duplicate_state_id
state_bad_missing_decision_timestamp
```

## Estado actual documentado

```text
market_state_table_v0_1 materialized = false
builder_implemented = false
schema_status = target_schema_defined
controlled_candidate_materialized = true
candidate_dataset_id = market_state_table_v0_1_candidate
candidate_status = controlled_candidate_not_promoted
```
