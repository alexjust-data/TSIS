# Data Resume actualizado

Fecha de verificacion: 2026-03-20
Ruta analizada: `D:\`

## Nota metodologica

Este resumen reemplaza al anterior porque ya no describe la realidad actual del storage.

Para no encallarme con millones de ficheros, el analisis se ha hecho como lo haria un ingeniero de datos serio:

- conteos exactos de primer nivel por dataset
- verificacion exacta de particiones y convenciones de path
- muestreo de esquemas reales sobre ficheros Parquet concretos
- inspeccion dirigida de subarboles pequenos y medianos

No se ha intentado hacer un conteo exhaustivo de todos los ficheros del lago completo porque ese coste no aporta valor proporcional y, con este volumen, penaliza mucho el tiempo de inspeccion. Por tanto:

- los conteos de carpetas de primer nivel que se reportan aqui son exactos
- las convenciones de particionado y nombres de fichero estan verificadas
- las coberturas temporales marcadas como "observadas" vienen de verificaciones reales sobre particiones y muestras, no de suposiciones

## `D:\` y la estructura base es esta:

- `D:\financial`
- `D:\Halts`
- `D:\ohlcv_1m`
- `D:\ohlcv_1m_missing`
- `D:\ohlcv_daily`
- `D:\quotes`
- `D:\reference`
- `D:\regime_indicators`
- `D:\trades_ticks_prod_2005_2026`

## Estructura principal actual

### `D:\quotes`

Hecho verificado:

- 1698 carpetas de primer nivel
- particionado por ticker sin prefijo `ticker=`
- patron de path verificado: `D:\quotes\{TICKER}\year=YYYY\month=MM\day=DD\quotes.parquet`

Convenciones verificadas:

- el dia en `quotes` usa `day=DD`
- por dia hay un fichero `quotes.parquet`

Cobertura temporal observada:

- `AAT`: `2011` a `2026`
- `AABA`: `2017` a `2019`
- existe al menos `year=2026` en el dataset

Lectura correcta:

- no es un universo full-market de 12k+ tickers
- es un universo curado mucho mas pequeno y con cobertura temporal heterogenea por ticker

Esquema real de muestra:

- fichero: `D:\quotes\AABA\year=2017\month=06\day=19\quotes.parquet`
- columnas: `ask_exchange`, `ask_price`, `ask_size`, `bid_exchange`, `bid_price`, `bid_size`, `conditions`, `indicators`, `participant_timestamp`, `sequence_number`, `timestamp`, `tape`, `trf_timestamp`, `year`, `month`, `day`

### `D:\trades_ticks_prod_2005_2026`

Hecho verificado:

- 888 carpetas de primer nivel
- particionado por ticker sin prefijo `ticker=`
- patron de path verificado: `D:\trades_ticks_prod_2005_2026\{TICKER}\year=YYYY\month=MM\day=YYYY-MM-DD\market.parquet`

Convenciones verificadas:

- el dia en `trades` usa `day=YYYY-MM-DD`
- se ha verificado al menos `market.parquet` como fichero por dia

Cobertura temporal observada:

- `AAT`: `2011` a `2026`
- `AABA`: `2017` a `2019`
- por ejemplo, en `AAT/year=2026/month=03` hay dias `2026-03-02` a `2026-03-13`

Lectura correcta:

- tambien es un universo curado y mas pequeno que OHLCV/fundamentals/reference
- la cobertura no debe inferirse solo por el nombre de carpeta; hay que mirar las particiones reales por ticker

Esquema real de muestra:

- fichero: `D:\trades_ticks_prod_2005_2026\AABA\year=2017\month=06\day=2017-06-19\market.parquet`
- columnas: `ticker`, `date`, `timestamp`, `price`, `size`, `exchange`, `conditions`, `year`, `month`, `day`

### `D:\ohlcv_1m`

Hecho verificado:

- 12109 carpetas de primer nivel
- 12106 son particiones `ticker=*`
- 3 son auxiliares: `_run`, `_staging_commit_1m`, `_staging_flatfiles_1m`
- patron de path verificado: `D:\ohlcv_1m\ticker={TICKER}\year=YYYY\month=MM\minute_aggs_{TICKER}_{YYYY}_{MM}.parquet`

Cobertura temporal observada:

- `AAA`: existe `year=2005`
- `AAT`: `2011` a `2026`
- por construccion observada del lago, este arbol cubre al menos desde `2005` hasta `2026`

Lectura correcta:

- este es uno de los datasets core y mucho mas amplio que `quotes` o `trades_ticks_prod_2005_2026`
- el layout es mensual por ticker y anio

Esquema real de muestra:

- fichero: `D:\ohlcv_1m\ticker=AAA\year=2005\month=01\minute_aggs_AAA_2005_01.parquet`
- columnas: `ticker`, `ts_utc`, `date`, `year`, `month`, `o`, `h`, `l`, `c`, `v`, `vw`, `n`, `t`

### `D:\ohlcv_daily`

Hecho verificado:

- 12470 carpetas de primer nivel
- 12468 son particiones `ticker=*`
- 2 son auxiliares: `_run`, `_staging_commit`
- patron de path verificado: `D:\ohlcv_daily\ticker={TICKER}\year=YYYY\day_aggs_{TICKER}_{YYYY}.parquet`

Cobertura temporal exacta medida en el arbol de particiones:

- minimo: `2005`
- maximo: `2026`
- total de directorios `year=*`: `125400`

Lectura correcta:

- es el universo mas amplio y estable entre los precios agregados inspeccionados
- el layout es anual por ticker

### `D:\ohlcv_1m_missing`

Hecho verificado:

- 29 carpetas de primer nivel
- 27 son particiones `ticker=*`
- 2 son auxiliares: `_run`, `_staging_flatfiles_1m`

Lectura correcta:

- esto no es un dataset core equivalente a `ohlcv_1m`
- es un parche / bucket de faltantes para un conjunto pequeno de tickers

Cobertura temporal observada en muestra real:

- `DAL`: `2005`, `2007` a `2026`

Esquema real de muestra:

- fichero: `D:\ohlcv_1m_missing\ticker=DAL\year=2005\month=01\minute_aggs_DAL_2005_01.parquet`
- columnas: `ticker`, `ts_utc`, `date`, `year`, `month`, `o`, `h`, `l`, `c`, `v`, `vw`, `n`, `t`

### `D:\financial`

Hecho verificado:

Subdirectorios de primer nivel:

- `balance_sheets`
- `cash_flow_statements`
- `income_statements`
- `ratios`
- `_audit`
- `_run`

Conteos exactos verificados:

- `balance_sheets`: 12468 particiones `ticker=*`
- `cash_flow_statements`: 12468 particiones `ticker=*`
- `income_statements`: 12468 particiones `ticker=*`
- `ratios`: 12468 particiones `ticker=*`

Lectura correcta:

- los fundamentals ya no estan organizados como en el resumen viejo
- ahora estan normalizados por familia contable y ticker
- `financial` esta alineado en cobertura de universo con `ohlcv_daily` y `reference/overview`

Esquema real de muestra en `ratios`:

- fichero: `D:\financial\ratios\ticker=A\ratios_A.parquet`
- columnas: `ticker`, `cik`, `date`, `price`, `average_volume`, `market_cap`, `earnings_per_share`, `price_to_earnings`, `price_to_book`, `price_to_sales`, `price_to_cash_flow`, `price_to_free_cash_flow`, `dividend_yield`, `return_on_assets`, `return_on_equity`, `debt_to_equity`, `current`, `quick`, `cash`, `ev_to_sales`, `ev_to_ebitda`, `enterprise_value`, `free_cash_flow`, `_dataset`, `_ingested_utc`

### `D:\reference`

Hecho verificado:

Subdirectorios de primer nivel:

- `all_tickers`
- `dividends`
- `events`
- `exchanges`
- `overview`
- `splits`
- `ticker_types`
- `_run`

#### `reference/all_tickers`

Hecho verificado:

- 3109 snapshots parquet
- primer snapshot observado: `snapshot_date=2005-01-02.parquet`
- ultimo snapshot observado: `snapshot_date=2026-03-09.parquet`

Esquema real de muestra:

- columnas: `ticker`, `name`, `market`, `locale`, `primary_exchange`, `type`, `active`, `currency_name`, `cik`, `composite_figi`, `share_class_figi`, `last_updated_utc`, `snapshot_date`, `_exchange_filter`, `_dataset`, `_ingested_utc`
- muestra leida: 2632 filas en `snapshot_date=2005-01-02.parquet`

#### `reference/overview`

Hecho verificado:

- 12468 particiones `ticker=*`

Esquema real de muestra:

- fichero: `D:\reference\overview\ticker=A\overview_A_2022-02-08.parquet`
- columnas: `ticker`, `name`, `market`, `locale`, `primary_exchange`, `type`, `active`, `currency_name`, `cik`, `composite_figi`, `share_class_figi`, `market_cap`, `phone_number`, `description`, `sic_code`, `sic_description`, `ticker_root`, `homepage_url`, `total_employees`, `list_date`, `share_class_shares_outstanding`, `weighted_shares_outstanding`, `round_lot`, `address.address1`, `address.city`, `address.state`, `address.postal_code`, `request_date`, `_dataset`, `_ingested_utc`

#### `reference/dividends`, `reference/splits`, `reference/events`

Hecho verificado:

- `dividends`: 12468 particiones `ticker=*`
- `splits`: 12468 particiones `ticker=*`
- `events`: 12468 particiones `ticker=*`

Muestras reales:

- `splits_AAPL.parquet`: columnas `execution_date`, `id`, `split_from`, `split_to`, `ticker`, `_dataset`, `_ingested_utc`; 3 filas
- `events_AAPL.parquet`: columnas `name`, `composite_figi`, `cik`, `events`, `ticker`, `_dataset`, `_ingested_utc`; 1 fila
- `dividends_AAPL.parquet`: en la muestra leida solo aparecen `ticker`, `_dataset`, `_ingested_utc`; 1 fila

Lectura correcta:

- `reference` ahora es un store serio y amplio de snapshots y entidades por ticker
- el resumen viejo no refleja este layout ni su escala actual

### `D:\regime_indicators`

Hecho verificado:

Subdirectorios de primer nivel:

- `etfs`
- `indices`

Contenido observado:

- `indices` contiene al menos `I_COMP`, `I_NDX`, `I_SOX`
- `etfs` contiene al menos `DIA`, `EEM`, `EFA`, `FXE`, `GLD`, `HYG`, `IWM`, `LQD`, `QQQ`, `SLV`, `SPSM`, `SPY`, `TLT`, `UNG`, `USO`, `UUP`, `UVXY`, `VB`, `VIXY`, `VXX`, `XLB`, `XLC`, `XLE`, `XLF`, `XLI`, `XLK`, `XLP`, `XLRE`, `XLU`, `XLV`, `XLY`

Esquema real de muestra:

- fichero: `D:\regime_indicators\etfs\DIA\day.parquet`
- columnas: `volume`, `vwap`, `open`, `close`, `high`, `low`, `trades`, `datetime`, `date`

### `D:\Halts`

Hecho verificado:

Subdirectorios de primer nivel:

- `processed`
- `raw`

#### `Halts/processed`

Contenido observado:

- `halts_master.csv`
- `halts_master.parquet`
- `halts_master_multisource.csv`
- `halts_master_multisource.parquet`
- `halts_master_multisource_summary.csv`
- `halts_master_nasdaq_for_run_dates.csv`
- `halts_master_nasdaq_for_run_dates.parquet`
- `halts_master_nyse_1y.csv`
- `halts_master_nyse_1y.parquet`
- `halts_master_sec.csv`
- `halts_master_sec.parquet`
- `nasdaq_halts_raw.csv`
- `nasdaq_tradehalts_for_run_dates_raw.csv`
- `sec_suspensions_raw.csv`
- `universe_tickers_without_halts.csv`
- `universe_tickers_without_halts_multisource.csv`
- `universe_tickers_with_halts.csv`
- `universe_tickers_with_halts_multisource.csv`
- `universe_vs_halts_coverage.csv`
- `universe_vs_halts_coverage_multisource.csv`

Lectura correcta:

- aqui no hay solo raw descargado; ya hay outputs consolidados y comparativas de cobertura

#### `Halts/raw`

Subdirectorios observados:

- `nasdaq`
- `nasdaq_rss_by_date`
- `nyse`
- `sec`

Muestras observadas:

- en `raw/nasdaq`: `https_www_nasdaqtrader_com_trader_aspx_id_TradeHalts.html`, `TradingHaltHistory.html`
- en `raw/nasdaq_rss_by_date`: XMLs por fecha como `01022004.xml`, `01022008.xml`, `01022014.xml`, `01022024.xml`

## Resumen operativo real

Si el objetivo es backtestear small caps con la data actual, la lectura correcta del lago es esta:

- `quotes` y `trades_ticks_prod_2005_2026` no son el universo completo; son universos curados y mas pequenos
- `ohlcv_1m`, `ohlcv_daily`, `financial/*` y `reference/*` tienen una cobertura mucho mas amplia, del orden de ~12.4k tickers
- `ohlcv_daily` tiene cobertura temporal global verificada de `2005` a `2026`
- `reference/all_tickers` funciona como store historico de snapshots diarios y llega hasta `2026-03-09`
- `ohlcv_1m_missing` es un parche puntual y no debe confundirse con el dataset principal
- `Halts` ya contiene tanto fuentes raw como salidas procesadas listas para uso

## Riesgos y notas de ingenieria

- No se debe inferir cobertura temporal global solo por el nombre de una carpeta raiz; hay heterogeneidad real por ticker
- `quotes` y `trades` usan convenciones distintas para la particion `day`
  - `quotes`: `day=DD`
  - `trades`: `day=YYYY-MM-DD`
- En varios datasets las columnas de particion (`year`, `month`, `day`, `ticker`) tambien estan escritas dentro del propio fichero Parquet
  - esto puede hacer fallar lecturas tipo `pyarrow.read_table()` si se mezclan columnas internas y particionado Hive automatico
  - para inspeccion fiable conviene usar `pyarrow.parquet.ParquetFile(...)` o desactivar la inferencia de particiones

## Conclusion

El resumen viejo ya no sirve como fotografia del storage actual.

La realidad operativa a 2026-03-20 es que `D:\` contiene un lago mas maduro y mas amplio, con:

- core de precios agregados muy amplio en `ohlcv_1m` y `ohlcv_daily`
- universos mas curados para `quotes` y `trades`
- fundamentals y reference alineados alrededor de ~12468 tickers
- snapshots historicos diarios en `reference/all_tickers`
- bucket especifico de faltantes en `ohlcv_1m_missing`
- raw + processed para halts

Este es el estado que deberia usarse como base para cualquier backtest o auditoria de cobertura actual.
