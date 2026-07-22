# Intraday Scanner Candidates Table Target Contract v0.1

## Estado

Status:

```text
target_contract_builder_implemented_controlled_replay_not_official
```

Dataset target:

```text
intraday_scanner_candidates_table_v0_1
```

## Rol

Esta tabla es el denominador intradia de candidatos in-play. Su funcion es
responder:

```text
que smallcaps elegibles cruzaron un movimiento fuerte intradia,
cuando lo hicieron,
en que segmento,
y con que actividad acumulada hasta ese momento.
```

No responde si una estrategia debe operar.

## Grain

```text
one row per ticker + session_date evaluated
```

Llave logica:

```text
scanner_run_id
ticker
session_date
```

`as_of_utc` se define como:

```text
first_cross_50_ts_utc when selected or motion-threshold seen
else last observed extended-hours bar for evaluated rows
```

## Sources

Fuentes primarias:

```text
E:/TSIS/data/ohlcv_1m
E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

El builder no lee `quotes` ni `trades`. La microestructura queda para
`microstructure_features_table`, `market_state_table` y `event_state_table`.

## Repair-Aware Successor Requirement

La version v0.1 usa `E:/TSIS/data/ohlcv_1m` raw. Esa decision fue suficiente
para el replay controlado inicial y para demostrar:

```text
grain
lineage
first-cross timing
segment detection
manifest/heartbeat/run evidence
```

No es suficiente para promocion canonical/full-universe si existen mechas o
precios 1m incompatibles con quotes.

El sucesor correcto debe ser:

```text
dataset_id: intraday_scanner_candidates_table_v0_2_quote_guarded_candidate
source_price_view: ohlcv_1m_quote_guarded
storage_model: raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay
```

Contrato upstream:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
```

El reparador quote-guarded:

1. lee raw 1m desde `E:/TSIS/data/ohlcv_1m`;
2. lee quotes desde `D:/quotes` mientras la paridad E-root sigue pendiente;
3. construye un envelope por minuto con `bid_floor = q01(bid)`,
   `ask_cap = q99(ask)`, minimo 3 quotes/minuto y tolerancia
   `0.3% + 0.0001`;
4. escribe solo filas problematicas en shards/manifest;
5. no modifica el raw;
6. no reconstruye VWAP desde quotes.

El artefacto promocionado disponible desde 2026-07-03 es:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
status: PASS
universe_tickers: 4824
completed_tickers: 4824
missing_tickers: 0
manifest_rows: 301278342
```

La lectura oficial para el scanner v0.2 sera:

```text
raw monthly ohlcv_1m parquet
+ matching repair_manifest rows for ticker/range
-> in-memory quote-guarded bars
```

Si el cruce de +50% existe solo en raw y desaparece en quote-guarded, el row
debe conservar evidencia del spike pero quedar no seleccionado:

```text
motion_threshold_seen_raw = true
motion_threshold_seen_qg = false
selected_intraday_in_play_candidate = false
scanner_quality_state = rejected_raw_spike_not_confirmed_by_quotes
```

## Column Families

### Lineage

```text
intraday_scanner_candidate_id
scanner_run_id
created_at_utc
dataset_id
schema_version
quality_policy_version
scanner_policy_version
scanner_definition_id
base_scanner_definition_id
materialization_scope
full_universe_claim
source_ohlcv_1m_root
source_master_daily_root
source_*_manifest
source_price_view
source_quote_guarded_repair_manifest
source_quote_guarded_run_id
requires_rebuild_after_quote_guarded_e_promotion
```

### Identity

```text
instrument_id
ticker
session_date
as_of_utc
as_of_policy
instrument_name
primary_exchange
exchange_acronym
active_in_reference
reference_last_updated_utc
```

### Base Eligibility

```text
common_stock_filter_passed
market_cap_usd
market_cap_filter_passed
family_data_quality_verdict
data_present
backtest_core_row_candidate
base_eligible_smallcap_denominator_passed
```

### Float Context

```text
shares_outstanding_context
float_shares
float_unavailable_reason
```

`float_shares` must remain null until `float_context_table` exists.

### Daily Context

```text
prior_close
daily_open
daily_high
daily_low
daily_close
daily_volume
daily_dollar_volume
rvol_20d
gap_pct
daily_return_pct
```

### Intraday Detection

```text
first_bar_ts_utc
last_bar_ts_utc
extended_bar_count
extended_volume
extended_dollar_volume
max_move_vs_prev_close_pct
max_move_vs_segment_open_pct
premarket_high_vs_prev_close_pct
regular_high_vs_prev_close_pct
afterhours_high_vs_prev_close_pct
max_move_segment
```

### First Cross

```text
first_cross_50_ts_utc
first_cross_50_ts_et
first_cross_50_segment
first_cross_price
first_cross_move_vs_prev_close_pct
first_cross_move_vs_segment_open_pct
volume_to_time_at_first_cross
dollar_volume_to_time_at_first_cross
bars_observed_to_first_cross
first_cross_source_ohlcv_1m_file
first_cross_price_source
raw_first_cross_price
qg_first_cross_price
raw_move_vs_prev_close_pct
qg_move_vs_prev_close_pct
quote_guarded_repair_applied_at_cross
repair_state_at_cross
repair_reason_at_cross
```

### Selection

```text
motion_threshold_passed
tradability_threshold_passed
price_filter_passed_at_first_cross
selected_intraday_in_play_candidate
scanner_selection_state
candidate_reasons
```

## Selection Semantics

`selected_intraday_in_play_candidate = true` iff:

```text
common_stock = true
market_cap_usd < 100M
data quality usable/review
first_cross_move_vs_prev_close_pct >= 50
first_cross_price > 0.5
first_cross_price <= 20
volume_to_time_at_first_cross >= 500000
OR dollar_volume_to_time_at_first_cross >= 250000
```

## Output Locations

Controlled local replay:

```text
C:/TSIS_Data/tests/test_runs/<date>/<run_id>/
```

Official/promoted candidate replay root, when explicitly run by a human:

```text
E:/TSIS/data/data_foundation_outputs/intraday_scanner_candidates_table/candidate_replays/<run_id>/
```

Promoted canonical table, not created yet:

```text
E:/TSIS/data/data_foundation_outputs/intraday_scanner_candidates_table/intraday_scanner_candidates_table_v0_1/
```

## Promotion Barrier

Before promotion to official E-root table:

```text
20y replay completed
runner manifest complete
heartbeat/pid/log evidence complete
duplicate ticker-session keys = 0
full_universe_claim explicitly reviewed
source ohlcv_1m quality/repair policy declared
quote-guarded repair manifest final/promoted or explicit raw-diagnostic scope
raw-only v0.1 runs blocked from canonical/full-universe promotion
raw-spike-not-confirmed-by-quotes rejection semantics validated
float remains non-filter until float_context_table exists
strategy overlays excluded
```

## Consumer Rules

Consumers may use this table for:

```text
candidate denominator
frontside discovery surface
event-window seeding
strategy overlay input
market_state/event_state build input
```

Consumers must not use it as:

```text
entry signal
label
reward
execution truth
complete market state
complete microstructure state
```
