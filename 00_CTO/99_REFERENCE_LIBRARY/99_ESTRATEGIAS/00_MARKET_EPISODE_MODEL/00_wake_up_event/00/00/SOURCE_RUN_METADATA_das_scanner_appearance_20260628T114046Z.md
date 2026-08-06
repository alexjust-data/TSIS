# DAS Run Metadata - das_scanner_appearance_20260628T114046Z

- status: `completed`
- strategy_id: `das`
- query_name: `das_scanner_appearance`
- run_datetime_utc: `2026-06-28 11:40:46 UTC`
- total_files: `72058`
- files_scanned: `72058`
- raw_candidate_count: `679`
- candidate_count: `679`
- partial_output: `candidate_events_partial.csv`

## Terminal launcher

```powershell
Set-Location 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS'
python 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\scripts\das_widgets.py' `
  --data-root 'E:\TSIS\data\ohlcv_1m' `
  --reference-overview-root 'E:\TSIS\data\reference\overview' `
  --output-root 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs' `
  --universe-path 'C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet' `
  --session-scope premarket `
  --push-label-pct 20.0 `
  --dip-label-pct 3.0 `
  --min-session-volume 500000.0 `
  --min-price 0.5 `
  --max-price 20.0 `
  --max-market-cap 100000000.0 `
  --missing-market-cap-policy flag `
  --price-view raw `
  --vwap-source calculated `
  --progress-every 250 `
  --partial-flush-every 1 `
  --years '2024,2025,2026'
```

## Field definitions

- `1m root`: Carpeta operativa de velas 1m usada para buscar candidatos.
- `Reference`: Carpeta de referencia usada para leer exchange, market cap y compania.
- `Universe`: Source of truth LT1B que limita los tickers elegibles.
- `Tickers`: Lista manual de tickers; vacio significa usar universo LT1B.
- `Years`: Anios a escanear; acepta 2025 o 2022-2025.
- `Session`: Segmentos donde simular aparicion en screener.
- `Session Vol >`: Volumen acumulado desde el inicio de premarket; debe alcanzarse mientras se construye el primer push.
- `Price >=`: Precio minimo observado en la vela de aparicion.
- `Price <=`: Precio maximo observado en la vela de aparicion.
- `MCap <`: Market cap maximo permitido cuando existe dato de referencia.
- `No MCap`: Politica cuando falta market cap: include, exclude o flag.
- `DAS state`: Clasificacion posterior: scanner_only, push_detected, push_and_dip, rebreak_confirmed o failed_before_rebreak.
- `Green wick dip`: Dip intrabar en vela verde de continuacion: barre bajo el cierre previo y recupera con momentum.
- `Price`: Vista de precio usada: raw o split_normalized.
- `VWAP`: Linea VWAP del chart: calculated usa VWAP acumulada calculada; raw usa la columna vw del parquet.
- `Y padding`: Aire visual arriba y abajo del chart interactivo.
- `Progress`: Cada cuantos archivos escaneados se imprime progreso en terminal.
- `Flush hits`: Cada cuantos candidatos nuevos se actualiza candidate_events_partial.csv.

## Outputs

- `candidate_events_partial.csv`: candidatos parciales durante el run.
- `candidate_events.csv`: candidatos finales en CSV.
- `candidate_events.parquet`: candidatos finales en Parquet cuando existen filas.

## Delete command

```powershell
Remove-Item -LiteralPath 'C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z' -Recurse -Force
```
