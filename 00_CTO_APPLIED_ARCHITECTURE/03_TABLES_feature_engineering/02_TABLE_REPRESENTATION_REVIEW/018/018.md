# 018 - intraday_scanner_candidates_table

## Tipo de documento

Ficha de atributos contractuales. No es una muestra de parquet operativo promovido.

## Documentos fuente usados

Solo se usan estos documentos:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\intraday_scanner_candidates_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\intraday_scanner_candidates_table_target_contract_v0_1.md`

## Estado documentado

| item | valor |
| --- | --- |
| dataset_id | `intraday_scanner_candidates_table_v0_1` |
| status | `schema_contract_candidate_controlled_replay_not_promoted` |
| grano | `one row per scanner_run_id + ticker + session_date` |
| full_universe_claim | `false` para controlled replays |

`intraday_scanner_candidates_table_v0_1` es una superficie de candidatos intradia. No es `market_state_table`, `event_state_table`, label table, reward table ni state completo.

## Atributos obligatorios por contrato

### Identidad y linaje

```text
intraday_scanner_candidate_id string not null
scanner_run_id string not null
created_at_utc string not null
dataset_id string not null
schema_version string not null
quality_policy_version string not null
scanner_policy_version string not null
scanner_definition_id string not null
base_scanner_definition_id string not null
materialization_scope string not null
full_universe_claim boolean not null
instrument_id string nullable
ticker string not null
session_date date not null
as_of_utc timestamp not null
as_of_policy string not null
```

### Elegibilidad y contexto

```text
common_stock_filter_passed boolean not null
market_cap_usd double nullable
market_cap_filter_passed boolean nullable
shares_outstanding_context double nullable
float_shares double nullable
float_unavailable_reason string nullable
prior_close double nullable
daily_open double nullable
daily_high double nullable
daily_low double nullable
daily_close double nullable
daily_volume double nullable
daily_dollar_volume double nullable
rvol_20d double nullable
gap_pct double nullable
daily_return_pct double nullable
family_data_quality_verdict string nullable
data_present boolean not null
backtest_core_row_candidate boolean nullable
```

### Campos intradia

```text
first_bar_ts_utc timestamp nullable
last_bar_ts_utc timestamp nullable
extended_bar_count bigint not null
extended_volume double nullable
extended_dollar_volume double nullable
max_move_vs_prev_close_pct double nullable
max_move_vs_segment_open_pct double nullable
premarket_high_vs_prev_close_pct double nullable
regular_high_vs_prev_close_pct double nullable
afterhours_high_vs_prev_close_pct double nullable
max_move_segment string nullable
first_cross_50_ts_utc timestamp nullable
first_cross_50_ts_et timestamp nullable
first_cross_50_segment string nullable
first_cross_price double nullable
first_cross_move_vs_prev_close_pct double nullable
first_cross_move_vs_segment_open_pct double nullable
volume_to_time_at_first_cross double nullable
dollar_volume_to_time_at_first_cross double nullable
bars_observed_to_first_cross bigint nullable
first_cross_source_ohlcv_1m_file string nullable
```

### Seleccion

```text
motion_threshold_passed boolean not null
tradability_threshold_passed boolean not null
price_filter_passed_at_first_cross boolean nullable
base_eligible_smallcap_denominator_passed boolean not null
selected_intraday_in_play_candidate boolean not null
scanner_selection_state string not null
candidate_reasons string nullable
```

### Linaje de fuente

```text
source_ohlcv_1m_root string not null
source_master_daily_root string not null
source_master_daily_manifest string nullable
source_instrument_master_manifest string nullable
source_market_calendar_manifest string nullable
master_daily_build_run_id string nullable
```

## Columnas prohibidas

```text
label
reward
action
fill
pnl
strategy_decision
entry_signal
exit_signal
```

## Constraints semanticos

```text
selected_intraday_in_play_candidate implies motion_threshold_passed
selected_intraday_in_play_candidate implies tradability_threshold_passed
selected_intraday_in_play_candidate implies price_filter_passed_at_first_cross
selected_intraday_in_play_candidate implies base_eligible_smallcap_denominator_passed
float_shares must remain null until float_context_table exists
full_universe_claim must be false for controlled replays
```
