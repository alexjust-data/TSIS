# 014 - master_intraday_bar_table

## Tipo de documento

Ficha de atributos contractuales. No es una muestra de parquet operativo full-universe.

## Documentos fuente usados

Solo se usan estos documentos:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\master_intraday_bar_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md`

## Estado documentado

| item | valor |
| --- | --- |
| dataset_id actual | `master_intraday_bar_table_v0_1` |
| unidad | `instrument intraday bar price-view row` |
| grano | `instrument_id + ticker + ts_utc + bar_size + price_view` |
| root | `E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table` |
| layout | `partitioned parquet dataset by year/month/price_view` |
| scope v0.1 | `scoped_split_normalized_event_cases` |
| full_universe_claim | `false` |

`master_intraday_bar_table_v0_1` es una tabla intradia scoped/pilot. No documenta una copia 1m full-universe promovida.

## Atributos obligatorios por contrato

### Identidad

```text
master_intraday_bar_id
ticker
instrument_id
ts_utc
session_date
year
month
bar_size
price_view
```

### Fuente y precio

```text
quality_gate_family
source_dataset
source_root
source_file
open
high
low
close
volume
vwap
transaction_count
source_t_epoch_ms
```

### Linaje raw y split

```text
source_raw_open
source_raw_high
source_raw_low
source_raw_close
source_raw_vwap
source_raw_volume
source_raw_transaction_count
future_split_factor
o_split_normalized
h_split_normalized
l_split_normalized
c_split_normalized
vw_split_normalized
materialized_source_price_view
source_1m_file_reported
source_splits_file
source_split_normalized_file
```

### Contexto piloto

```text
pilot_role
pilot_event_type
pilot_event_date
session_segment
```

### Calidad raw 1m

```text
raw_quality_manifest_present
raw_quality_manifest_rows
raw_core_quality_state
raw_core_issue_family
raw_combined_quality_state
raw_allowed_consumption
raw_vw_quality_state
raw_vw_issue_family
raw_final_policy_bucket_lt1b
raw_manifest_negative_or_zero_ohlc_rows
raw_manifest_negative_volume_rows
raw_manifest_high_low_inversion_rows
raw_manifest_duplicate_ts_utc_rows
raw_manifest_vw_outside_range_rows
```

### Corporate actions

```text
corporate_action_count
split_action_count
dividend_action_count
ticker_change_action_count
has_split_action
has_dividend_action
has_ticker_change_action
has_any_corporate_action
```

### Calidad y consumo

```text
row_level_price_integrity_state
selected_price_hard_invalid
negative_volume
core_ohlcv_consumption_allowed
vwap_consumption_allowed
vwap_consumption_state
event_research_bar_candidate
backtest_core_bar_candidate
full_universe_claim
materialization_scope
family_data_quality_verdict
family_foundations_completion_status
family_visual_inspection_status
family_production_use_gate
family_event_consumption_gate
gate_quality_policy_version
```

### Linaje y versionado

```text
dataset_certification_matrix_build_run_id
instrument_master_build_run_id
instrument_master_schema_version
quality_policy_version
schema_version
build_run_id
created_at_utc
```

## Price views v0.1 permitidas

Estas son las vistas aceptadas por el contrato `master_intraday_bar_table_v0_1`, no una declaracion de que `1m_raw` sea la mejor data para consumo operativo.

```text
1m_raw
1m_split_normalized
```

Lectura correcta:

```text
1m_raw = barras originales observadas; se conservan para linaje, auditoria, comparacion y reproducibilidad.
1m_split_normalized = barras ajustadas por splits dentro del contrato v0.1.
```

`1m_raw` puede contener precios incorrectos o no reparados. Por eso se creo el universo quote-guarded fisico:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1
```

En ese universo, la vista buena/corregida es:

```text
1m_quote_guarded_raw
```

## Candidate quote-guarded

Candidate previsto:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

Price views esperadas:

```text
1m_raw
1m_quote_guarded_raw
```

La presencia de `1m_raw` en el candidate no significa que sea la data buena. Significa que se conserva como referencia original para comparar contra la version corregida. La vista que representa la correccion quote-guarded es `1m_quote_guarded_raw`.

Atributos adicionales requeridos:

```text
quote_guarded_view
quote_guarded_repair_applied
repair_state
repair_reason
vw_quote_guarded_status
quote_bid_floor
quote_ask_cap
quote_count
source_quote_guarded_repair_manifest
source_quote_guarded_run_id
source_quotes_root
source_quotes_root_state
requires_rebuild_after_quotes_root_approval
requires_rebuild_after_quote_guarded_e_promotion
```

Regla de promocion del candidate:

```text
full_universe_claim debe permanecer false para `master_intraday_bar_table_v0_2_candidate_quote_guarded` hasta que existan denominator manifest, final quote-guarded validation report y promotion review. Esto no niega que exista el universo fisico corregido `ohlcv_1m_quote_guarded_full_universe_v0_1`; significa que falta promocion/institucionalizacion dentro de `master_intraday_bar_table`.
```

## No usar como

```text
full-universe 1m backtest feed
raw execution simulator truth
quote/trade microstructure substitute
unflagged ML or RL state source
```

