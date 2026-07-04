# OHLCV 1m Quote-Guarded Repair Runbook v0.1

## 1. Rol

Este runbook define como ejecutar la reparacion manifest-first de barras
`ohlcv_1m` semanticamente imposibles frente al envelope de `quotes`.

No modifica `E:/TSIS/data/ohlcv_1m`.

El resultado oficial de esta fase es:

- un `repair_manifest_v0_1.parquet`;
- un resumen reproducible de la auditoria;
- shards por ticker-month para poder reanudar ejecuciones largas;
- un loader `quote_guarded` capaz de aplicar el overlay en memoria.

## 2. Comando full-universe

Desde PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -Workers 12 -Overwrite
```

Parametros por defecto:

- `MinuteRoot = E:\TSIS\data\ohlcv_1m`
- `QuotesRoot = D:\quotes`
- `OutputRoot = E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded`
- `SessionStart = 04:00`
- `SessionEnd = 20:00`
- `BidQuantile = 0.01`
- `AskQuantile = 0.99`
- `TolerancePct = 0.003`
- `AbsTolerance = 0.0001`
- `MinQuoteCount = 3`

## 3. Smoke test recomendado

Antes de lanzar 20 anos completos:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -SmokeOnly -Workers 4 -Overwrite
```

`-SmokeOnly` limita la ejecucion a 12 parquets mensuales salvo que se pase
`-MaxFiles`.

## 4. Piloto sobre los cuatro casos motivadores

Para reproducir TWG, TIRX, RVYL y SHPH en 2026 sin promover output oficial:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -Tickers "TWG,TIRX,RVYL,SHPH" -MinYear 2026 -MaxYear 2026 -NoPromoteManifest -Workers 4 -Overwrite
```

## 5. Reanudar ejecuciones

El runner escribe:

- `runs/data_foundation/ohlcv_1m_quote_guarded/<run_id>/repair_shards/`
- `runs/data_foundation/ohlcv_1m_quote_guarded/<run_id>/file_summaries/`
- `runs/data_foundation/ohlcv_1m_quote_guarded/<run_id>/repair_manifest.parquet`
- `runs/data_foundation/ohlcv_1m_quote_guarded/<run_id>/repair_summary.json`

Si se relanza el mismo `RunRoot` sin `-Overwrite`, los ticker-month ya
procesados se saltan usando su summary JSON.

Ejemplo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_YYYYMMDD_HHMMSS" -Workers 12
```

## 6. Output promovido

Por defecto, el runner promueve el manifest consolidado a:

```text
E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_v0_1.parquet
```

Tambien escribe:

```text
E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_summary_v0_1.json
E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_v0_1_sample.csv
```

Para evitar promocion y dejar solo artefactos de run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -NoPromoteManifest
```

## 6.1 LT1B Promoted Manifest Closeout

The 2026-07-03 LT1B closeout promotes the scoped manifest:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_sample.csv
```

Summary gates:

```text
status = PASS
universe_dataset = lt1b_universe_v0_1
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
selected_repair_shards = 421533
written_shards = 421533
manifest_rows = 301278342
```

The promoted filename is `repair_manifest_lt1b_v0_1.parquet`, not the older
placeholder `repair_manifest_v0_1.parquet` or `repair_manifest_v0_2.parquet`.
The broad all-directory run is not promoted directly; the accepted manifest was
consolidated from the broad LT1B subset, the missing-180 supplement and the LICN
repair supplement.
## 7. Semantica de reparacion

Para cada ticker-minute con quotes suficientes:

- `quote_bid_floor = quantile(bid_price, 0.01)`
- `quote_ask_cap = quantile(ask_price, 0.99)`
- `o`, `h`, `l`, `c` se recortan al envelope si salen de rango;
- despues se fuerza consistencia OHLC:
  - `h_qg >= max(o_qg, c_qg)`
  - `l_qg <= min(o_qg, c_qg)`
- `v` se preserva;
- `n` se preserva;
- `vw` no se reconstruye desde quotes.

Si `vw` es imposible frente al envelope o frente al OHLC raw, queda marcado como:

```text
invalid_not_repaired_from_quotes
```

## 8. Uso por loaders

El modulo reusable es:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\src\data\ohlcv_1m_quote_guarded.py
```

Funciones principales:

- `build_quote_minute_envelope`
- `detect_quote_guarded_repairs`
- `apply_quote_guarded_repairs`
- `load_quote_guarded_ohlcv_month`

Los consumidores no deben leer el manifest a mano si pueden usar estas
funciones.

## 9. Regla institucional

Este proceso no declara trade truth.

Declara una vista quote-guarded para impedir que backtests, eventos y charts
usen barras OHLC de un minuto que contradicen de forma material el contexto
bid/ask disponible.

Cuando exista presupuesto para data de trades completa, esta capa podra ser
superada por una reconstruccion trade-based.

## 10. Supervision y validacion de runs largos

El protocolo operativo vivo para runs full-universe v0_2 esta documentado en:

```text
01_foundations/module_contracts/ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1.md
```

Ese documento es obligatorio para ejecuciones largas porque fija:

- proceso monitor humano;
- proceso supervisor con auto-restart seguro;
- proceso validador independiente;
- regla de no usar `-Overwrite` para reanudar;
- validaciones sobre shards y summaries persistidos;
- comando final de validacion completa.
