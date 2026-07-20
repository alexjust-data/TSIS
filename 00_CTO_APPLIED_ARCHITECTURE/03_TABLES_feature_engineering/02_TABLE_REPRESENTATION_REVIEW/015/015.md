# 015 - microstructure_features_table

## Tipo de documento

Ficha de atributos contractuales. No es una muestra de parquet operativo full-universe.

## Documentos fuente usados

Solo se usan estos documentos:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\microstructure_features_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md`

## Estado documentado

| item | valor |
| --- | --- |
| dataset_id actual | `microstructure_features_table_v0_1` |
| unidad | `instrument event-window microstructure row` |
| grano | `event_window_id + ticker + window_start_utc + window_end_utc` |
| root | `E:/TSIS/data/data_foundation_outputs/microstructure_features_table` |
| layout | `partitioned parquet dataset by year/month` |
| scope v0.1 | `seed_event_window_smoke` |
| full_universe_claim | `false` |

`microstructure_features_table_v0_1` es una superficie scoped/candidate para ventanas de evento. No documenta una tabla full-universe promovida.

## Atributos obligatorios por contrato

### Identidad

```text
microstructure_feature_id
event_window_id
ticker
instrument_id
instrument_identity_temporal_match
session_date
year
month
window_start_utc
window_end_utc
window_label
```

### Linaje de fuente

```text
source_scope_note
quotes_root_used
quotes_root_state
target_official_quotes_root
legacy_incomplete_e_quotes_root
trades_root_used
trades_root_state
source_quotes_file
source_trades_file
source_quotes_file_present
source_trades_file_present
source_quotes_file_sha256
source_trades_file_sha256
```

### Contexto de instrumento

```text
is_common_stock
is_lt1b_operational
lt1b_classification_1b
instrument_master_build_run_id
instrument_master_schema_version
```

### Features de quotes

```text
quotes_rows
quotes_window_rows
quotes_first_ts_utc
quotes_last_ts_utc
quotes_ask_zero_pct
quotes_bid_zero_pct
quotes_ask_size_zero_pct
quotes_bid_size_zero_pct
quotes_two_sided_rows
quotes_crossed_rows
quotes_locked_rows
quotes_crossed_ratio_pct_all_rows
quotes_crossed_ratio_pct_two_sided
quotes_locked_ratio_pct_two_sided
quotes_spread_bps_median
quotes_spread_bps_p90
quotes_top_depth_mean
```

### Features de trades

```text
trades_rows
trades_window_rows
trades_first_ts_utc
trades_last_ts_utc
trades_invalid_price_rows
trades_invalid_size_rows
trades_odd_lot_ratio_pct
trades_duplicate_exact_ratio_pct
trades_off_regular_session_ratio_pct
trades_total_volume
trades_dollar_volume
trades_price_min
trades_price_max
trades_price_last
trades_size_median
trades_size_p90
```

### Gates de familia

```text
quotes_family_data_quality_verdict
quotes_family_event_consumption_gate
quotes_family_production_use_gate
trades_family_data_quality_verdict
trades_family_event_consumption_gate
trades_family_production_use_gate
dataset_certification_matrix_build_run_id
```

### Flags de consumo

```text
microstructure_quality_state
event_research_microstructure_candidate
execution_sim_candidate
backtest_core_microstructure_candidate
full_universe_claim
materialization_scope
```

### Versionado

```text
quality_policy_version
schema_version
build_run_id
created_at_utc
```

## Estado v0.1 documentado

```text
materialization_scope = seed_event_window_smoke
rows = 1
tickers = 1
windows = 1
execution_sim_candidate_rows = 0
backtest_core_microstructure_candidate_rows = 0
```

## No usar como

```text
core backtesting
execution simulation
full-universe ML/RL training
D:/quotes as final official root
proof that all quotes/trades windows have been materialized
```
