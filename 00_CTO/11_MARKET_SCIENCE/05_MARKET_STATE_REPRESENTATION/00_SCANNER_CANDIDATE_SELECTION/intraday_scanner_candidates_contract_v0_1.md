# Intraday Scanner Candidates Contract v0.1

Fecha: 2026-06-30
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION`
Authority type: CTO architecture companion

## Decision

El scanner diario v0.3 queda como proxy coarse. Para estrategias intradia,
DAS/frontside y estados ML/RL, el denominador correcto debe construirse desde
1m:

```text
ohlcv_1m
-> intraday_scanner_candidates_table_v0_1
-> strategy overlays
-> market_state/event_state candidates
```

## Por Que No Basta El Daily Scanner

Un ticker puede:

```text
subir +100% en premarket
colapsar antes del cierre
no quedar correctamente representado por pct_chg_1d
```

Tambien puede activar un frontside en:

```text
premarket
regular session
afterhours
```

Por tanto, la pregunta cientifica no es solo:

```text
subio mucho durante el dia?
```

La pregunta correcta es:

```text
cuando cruzo el umbral,
en que segmento,
con cuanto volumen/dollar volume acumulado,
y que contexto tenia hasta ese timestamp?
```

## Scanner Intradia

Definicion activa:

```text
base_eligible_smallcap_denominator_v0_3
+ first 1m cross of +50% vs prior close
+ tradability gate at first cross
= selected_intraday_in_play_candidate
```

Segmentos:

```text
premarket 04:00-09:30 New York
regular 09:30-16:00 New York
afterhours 16:00-20:00 New York
```

## Dependencia Del Reparador Quote-Guarded

El replay v0.1 se construyo desde `E:/TSIS/data/ohlcv_1m` raw. Eso permite
detectar movimientos intradia que el daily scanner no ve, pero no resuelve
mechas imposibles ni barras 1m incompatibles con quotes.

Por tanto, la secuencia correcta no es:

```text
v0.1 raw -> full universe canonico
```

La secuencia correcta es:

```text
v0.1 raw controlled replay
-> quote-guarded repair manifest finalizado y validado
-> v0.2 quote-guarded intraday scanner candidate
-> broader/20y candidate materialization
```

Estado del reparador LT1B a 2026-07-03:

```text
script: build_ohlcv_1m_quote_guarded_repairs_v0_2.py
minute_root: E:/TSIS/data/ohlcv_1m
quotes_root: D:/quotes
source_runs:
  - quote_guarded_v0_2_20260627_091838
  - quote_guarded_v0_2_lt1b_missing180_20260703_092956
  - quote_guarded_v0_2_lt1b_licn_repair_20260703
promoted_manifest: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
manifest_status: PASS
manifest_rows: 301278342
```

Semantica:

```text
raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet = ohlcv_1m_quote_guarded view
```

El repair manifest no es una copia completa del mercado corregido. Es un
overlay institucional con los minutos afectados y las columnas reparadas:

```text
o_raw/h_raw/l_raw/c_raw
o_qg/h_qg/l_qg/c_qg
repair_state
repair_reason
quote_bid_floor
quote_ask_cap
quote_count
source_ohlcv_path
source_quotes_path
```

La version v0.2 del scanner debe comparar raw vs quote-guarded en el cruce:

```text
raw_first_cross_price
qg_first_cross_price
raw_move_vs_prev_close_pct
qg_move_vs_prev_close_pct
quote_guarded_repair_applied_at_cross
repair_state_at_cross
repair_reason_at_cross
scanner_quality_state
```

Regla critica:

```text
si raw cruza +50% pero quote-guarded no lo confirma,
se conserva evidencia del spike,
pero el ticker no queda seleccionado como in-play candidate.
```

## Separacion De Responsabilidades

Scanner intradia:

```text
detecta candidatos in-play y timing del primer push
```

Overlay de estrategia:

```text
decide si ese candidato encaja con una hipotesis concreta
```

Market/event state:

```text
agrega microestructura, noticias, halts, short context, fundamentals,
regime, daily context y calidad
```

ML/RL:

```text
consume estados gobernados, no filas crudas de scanner como estado final
```

## Evidencia Inicial

Replay controlado:

```text
run_id: intraday_scanner_candidates_v0_1_20260630T175311Z
root: C:/TSIS_Data/tests/test_runs/2026-06-30/intraday_scanner_candidates_replay_20250102_20250110_v0_1/
rows: 33413
tickers: 5690
session_dates: 6
selected_intraday_in_play_candidate_rows: 102
first_cross_premarket_rows: 114
first_cross_regular_rows: 82
first_cross_afterhours_rows: 39
```

Esto demuestra que la deteccion intradia captura eventos que el proxy diario
no puede explicar temporalmente.

## Referencias Operativas

```text
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/configs/data_foundation_outputs/scanner_definitions/intraday_in_play_momentum_candidate_denominator_v0_1.yaml
01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_scanner_candidates_table_v0_1.py
01_TSIS_DATA_FOUNDATION/scripts/run_intraday_scanner_candidates_materialization_v0_1.ps1
01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_scanner_candidates_table_builder_v0_1.py
```

## Regla Final

El scanner intradia dice:

```text
este ticker estuvo in-play en este timestamp/segmento bajo esta politica
```

No dice:

```text
entra long
entra short
esto es edge
esto es reward
esto es estado ML/RL completo
```
