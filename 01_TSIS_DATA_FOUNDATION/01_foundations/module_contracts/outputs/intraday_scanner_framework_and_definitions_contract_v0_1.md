# Intraday Scanner Framework And Definitions Contract v0.1

## Estado

Tipo: module contract.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Status:

```text
builder_implemented_controlled_replay_not_official
```

## Problema Que Resuelve

`daily_scanner_candidates_table_v0_3` usa proxies EOD/diarios. Puede detectar
que un ticker tuvo movimiento fuerte durante la sesion, pero no puede probar:

```text
primer timestamp del push
segmento del push
si el push ocurrio en premarket, regular o afterhours
volumen/dollar volume acumulado hasta ese timestamp
```

Para estrategias intradia, DAS/frontside, ML/RL por estados y event-state
builders, esa ceguera es inaceptable. El scanner intradia v0.1 cubre esa
brecha leyendo `ohlcv_1m`.

## Definicion Activa

```text
base_eligible_smallcap_denominator_v0_3
  -> intraday_in_play_momentum_candidate_denominator_v0_1
  -> strategy overlays
  -> market_state/event_state builders
```

La config activa vive en:

```text
configs/data_foundation_outputs/scanner_definitions/intraday_in_play_momentum_candidate_denominator_v0_1.yaml
```

## Sesiones Y Segmentos

La deteccion intradia trabaja sobre extended hours New York:

```text
04:00 <= t < 09:30  -> premarket
09:30 <= t < 16:00  -> regular
16:00 <= t <= 20:00 -> afterhours
```

Cada fila de salida representa un `ticker + session_date` evaluado y conserva
el primer cruce real del umbral:

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
```

## Umbral In-Play

Umbral inicial:

```text
minimum_push_move_pct = 50%
```

Regla:

```text
first 1m bar where high >= prior_close * 1.50
```

Tambien se conserva `move_vs_segment_open_pct` para estudiar movimientos que
nacen dentro de premarket, regular o afterhours.

## Tradability Gate

El gate inicial es:

```text
volume_to_time_at_first_cross >= 500000
OR dollar_volume_to_time_at_first_cross >= 250000
```

Interpretacion obligatoria:

```text
tradability != alpha
```

El gate solo indica que el candidato tenia actividad minima para estudio,
contrapartida y viabilidad inicial. La estrategia posterior debe estudiar
calidad del frontside, liquidez, microestructura, spread, halts, catalyst,
outcomes y ejecucion.

## Dependencia Quote-Guarded Y Sucesor v0.2

`intraday_scanner_candidates_table_v0_1` lee `E:/TSIS/data/ohlcv_1m`
directamente. Eso sirve para probar forma, timing, manifests y notebook de
inspeccion, pero no debe escalarse a canon 20y sin declarar la politica de
reparacion quote-guarded.

La ruta correcta de promocion es:

```text
raw ohlcv_1m
+ repair_manifest_lt1b_v0_1.parquet
= ohlcv_1m_quote_guarded view
-> intraday_scanner_candidates_table_v0_2_quote_guarded_candidate
```

La semantica del overlay quote-guarded esta gobernada por:

```text
01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
```

Estado operativo conocido del reparador:

```text
script: build_ohlcv_1m_quote_guarded_repairs_v0_2.py
minute_root: E:/TSIS/data/ohlcv_1m
quotes_root: D:/quotes
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
repair_shards: <run_root>/repair_shards/
promoted_manifest: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
promoted_manifest_state: PASS
promoted_manifest_rows: 301278342
```

El reparador no modifica los parquets raw y no crea un arbol fisico completo
corregido. Escribe solo filas afectadas como overlay/delta. La vista oficial
se obtiene cargando raw 1m y aplicando en memoria `o_qg/h_qg/l_qg/c_qg` solo
en los minutos afectados.

La version v0.2 del scanner intradia debe anadir, como minimo:

```text
first_cross_price_source
quote_guarded_repair_applied_at_cross
repair_state_at_cross
repair_reason_at_cross
raw_first_cross_price
qg_first_cross_price
raw_move_vs_prev_close_pct
qg_move_vs_prev_close_pct
scanner_quality_state
```

Regla de seleccion v0.2:

```text
si existe reparacion quote-guarded para el minuto de cruce,
la seleccion debe basarse en la vista quote-guarded.
```

Un spike raw no confirmado por quotes debe quedar preservado como evidencia,
pero no seleccionado como candidato in-play:

```text
motion_threshold_seen_raw = true
motion_threshold_seen_qg = false
selected_intraday_in_play_candidate = false
scanner_quality_state = rejected_raw_spike_not_confirmed_by_quotes
```

Por tanto, v0.1 no debe llamarse canonical/full-universe si se ejecuta a 20
anos sobre raw. El siguiente paso institucional correcto es construir/validar v0.2
quote-guarded contra el manifest promovido, o conservar cualquier run v0.1
como diagnostico raw explicitamente marcado.

## Float

Float no se usa como filtro global en v0.1.

Motivo:

```text
float_context_table no existe aun con source/as-of/coverage point-in-time.
```

La salida puede contener:

```text
shares_outstanding_context
float_shares = null
float_unavailable_reason
```

`shares_outstanding_context` no es `float_shares`.

## Prohibited Uses

Queda prohibido:

- tratar rows de scanner como `market_state`;
- tratar rows de scanner como `event_state`;
- entrenar ML/RL directamente sobre scanner rows;
- usar el scanner como senal de entrada;
- meter labels, outcomes, reward, PnL, fills o decision de estrategia;
- usar float como filtro hasta que exista `float_context_table`;
- llamar full-universe a un replay controlado local.

## Builder, Runner Y Tests

```text
builder: scripts/materialize_intraday_scanner_candidates_table_v0_1.py
runner: scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
test: tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py
```

El runner chunkifica por ventanas mensuales y escribe:

```text
pre_manifest
heartbeat
heartbeat.jsonl
pids
logs por ventana
_run_summary.json
```

## Evidencia Controlada

```text
run_id: intraday_scanner_candidates_v0_1_20260630T175311Z
root: C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
start_date: 2025-01-02
end_date: 2025-01-10
window_count: 1
rows: 33413
tickers: 5690
session_dates: 6
base_eligible_rows: 7498
motion_threshold_rows: 235
tradability_pass_rows: 176
selected_intraday_in_play_candidate_rows: 102
first_cross_premarket_rows: 114
first_cross_regular_rows: 82
first_cross_afterhours_rows: 39
duplicate_ticker_session_keys: 0
source_ohlcv_1m_file_count: 5775
full_universe_claim: false
```

Validacion:

```text
python -m pytest C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py -q
```

Resultado:

```text
1 passed
```

## Relacion Con Daily v0.3

`daily_scanner_candidates_table_v0_3` queda como:

```text
daily_eod_proxy / coarse context
```

No debe usarse como detector oficial para estrategias intradia que dependan de:

```text
primer push
premarket
afterhours
time-to-cross
volume-to-time
frontside timing
```

La autoridad para esos casos pasa a:

```text
intraday_scanner_candidates_table_v0_1
```

con el scope declarado de cada run.

## Regla Final

```text
intraday_scanner_candidates_table_v0_1 tells TSIS when a smallcap became
intraday in-play under a declared 1m momentum/tradability policy. It is not
market_state, event_state, label, reward, execution truth or strategy signal.
```
