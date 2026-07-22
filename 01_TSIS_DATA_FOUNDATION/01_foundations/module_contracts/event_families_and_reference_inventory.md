# Event Families and Reference Inventory - Modulo 01

## 1. Rol del documento

Este documento inventaria las familias de datos, eventos y referencia ya confirmadas en el proyecto.

No sustituye un data catalog completo.

Su funcion es establecer, con ejemplos concretos, que semanticas existen realmente y que pueden afectar:

- precio
- continuidad
- causalidad
- disponibilidad
- backtest
- ML
- y reconciliacion externa

## 2. Regla metodologica

Este inventario no se construye a partir de nombres de carpeta solamente.

Se construye a partir de:

- inspeccion de estructura;
- lectura de ejemplos representativos;
- y comprobacion de columnas y atributos de cada familia.

## 3. Familias confirmadas

### 3.1 Market data

#### `quotes`

Ejemplo:

- [quotes.parquet](</C:/TSIS_Data/data/quotes/AMC/year=2021/month=03/day=29/quotes.parquet>)

Columnas observadas:

- `ask_exchange`
- `ask_price`
- `ask_size`
- `bid_exchange`
- `bid_price`
- `bid_size`
- `conditions`
- `indicators`
- `participant_timestamp`
- `sequence_number`
- `timestamp`
- `tape`
- `trf_timestamp`
- `year`
- `month`
- `day`

Semantica:

- libro observado `bid/ask`
- metadata de condiciones y tape
- timestamps microestructurales

#### `trades_raw`

Ejemplo:

- [market.parquet](</C:/TSIS_Data/data/trades_ticks_prod_2005_2026/SELF/year=2016/month=01/day=2016-01-19/market.parquet>)

Columnas observadas:

- `ticker`
- `date`
- `timestamp`
- `price`
- `size`
- `exchange`
- `conditions`
- `year`
- `month`
- `day`

Semantica:

- prints observados
- ejecucion
- actividad intradia

#### `daily`

Ejemplo operacional usado en el modulo:

- `D:\ohlcv_daily\...`

Semantica ya fijada en el contrato `daily`:

- `OHLCV` diario
- integridad fisica de barra
- coverage
- y distincion entre `raw`, `split_normalized`, `adjusted` cuando aplique

### 3.2 Corporate actions

#### `dividends`

Ejemplo:

- [dividends_SELF.parquet](</C:/TSIS_Data/data/additional/corporate_actions/dividends/ticker=SELF/dividends_SELF.parquet>)

Columnas observadas:

- `cash_amount`
- `currency`
- `declaration_date`
- `dividend_type`
- `ex_dividend_date`
- `frequency`
- `pay_date`
- `record_date`
- `ticker`

Semantica observada:

- dividendos ordinarios y especiales
- frecuencias no triviales

Valores observados en muestreo:

- `dividend_type`: `CD`, `SC`
- `frequency`: `4`, `12`, `2`, `1`, `0`

#### `splits`

Ejemplo:

- [splits_SGC.parquet](</C:/TSIS_Data/data/additional/corporate_actions/splits/ticker=SGC/splits_SGC.parquet>)

Columnas observadas:

- `execution_date`
- `split_from`
- `split_to`
- `ticker`

Semantica observada:

- forward splits
- reverse splits
- ratios fraccionales o no enteros

Ejemplos confirmados:

- `SGC`: `1 -> 2`
- `AAIC`: `20 -> 1`
- `ABEO`: `25 -> 1`
- `ABVC`: ratios como `1 -> 3.141`

#### `ticker_events`

Ejemplo:

- [ticker_events_SELF.parquet](</C:/TSIS_Data/data/additional/corporate_actions/ticker_events/ticker=SELF/ticker_events_SELF.parquet>)

Columnas observadas:

- `type`
- `date`
- `ticker`
- `name`
- `ticker_change.ticker`

Semantica observada:

- `ticker_change`

### 3.3 Reference and identity

#### `overview`

Ejemplo:

- [overview_SELF_2026-03-09.parquet](</D:/reference/overview/ticker=SELF/overview_SELF_2026-03-09.parquet>)

Columnas observadas:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `cik`
- `composite_figi`
- `share_class_figi`
- `market_cap`
- `description`
- `sic_code`
- `sic_description`
- `ticker_root`
- `homepage_url`
- `list_date`
- `share_class_shares_outstanding`
- `weighted_shares_outstanding`
- `round_lot`
- branding y direccion

Semantica:

- identidad corporativa y de listing
- tipo de instrumento
- metadatos fundamentales de reconciliacion

#### `events`

Ejemplo:

- [events_SELF.parquet](</D:/reference/events/ticker=SELF/events_SELF.parquet>)

Columnas observadas:

- `name`
- `composite_figi`
- `cik`
- `events`
- `ticker`

Semantica:

- timeline compacta de eventos de referencia por ticker

#### `ticker_types`

Ejemplo:

- [ticker_types.parquet](</D:/reference/ticker_types/ticker_types.parquet>)

Valores observados:

- `CS`
- `PFD`
- `WARRANT`
- `RIGHT`
- `BOND`
- `ETF`
- `ETN`
- `ADRC`

Semantica:

- tipo de instrumento
- restriccion crucial para comparabilidad de precio y retorno

#### `exchanges`

Ejemplo:

- [exchanges.parquet](</D:/reference/exchanges/exchanges.parquet>)

Columnas observadas:

- `id`
- `type`
- `asset_class`
- `locale`
- `name`
- `acronym`
- `mic`
- `operating_mic`
- `participant_id`
- `url`

Semantica:

- venue
- MIC
- rol exchange / TRF / SIP

#### `all_tickers snapshots`

Ejemplo:

- [snapshot_date=2013-11-04.parquet](</D:/reference/all_tickers/snapshot_date=2013-11-04.parquet>)

Columnas observadas:

- `ticker`
- `name`
- `market`
- `locale`
- `primary_exchange`
- `type`
- `active`
- `currency_name`
- `cik`
- `composite_figi`
- `share_class_figi`
- `snapshot_date`

Semantica:

- universo por fecha
- identidad temporalizada

### 3.4 Market events and external context

#### `halts`

Ejemplo:

- [halts_master_multisource.parquet](</D:/Halts/processed/halts_master_multisource.parquet>)

Columnas observadas:

- `source`
- `source_priority`
- `ticker`
- `issuer_name`
- `listing_exchange`
- `halt_date`
- `halt_start_et`
- `resume_quote_et`
- `resume_trade_et`
- `halt_code`
- `halt_type`
- `raw_reason`
- `release_no`
- `item_link`
- `url_source`
- `is_sec_suspension`

Semantica:

- LULD pauses
- volatility halts
- SEC suspensions
- resume timestamps

#### `ipos`

Ejemplo:

- [ipos_AARD.parquet](</C:/TSIS_Data/data/additional/ipos/ipos/ticker=AARD/ipos_AARD.parquet>)

Columnas observadas:

- `announced_date`
- `listing_date`
- `issuer_name`
- `currency_code`
- `final_issue_price`
- `offer_price_range`
- `total_offer_size`
- `primary_exchange`
- `shares_outstanding`
- `security_type`
- `lot_size`
- `ipo_status`

Semantica:

- nacimiento/listing
- precio de oferta
- estado del IPO

#### `news`

Ejemplo:

- [news_AACT.parquet](</C:/TSIS_Data/data/additional/news/news/ticker=AACT/news_AACT.parquet>)

Columnas observadas:

- `title`
- `author`
- `published_utc`
- `article_url`
- `tickers`
- `description`
- `keywords`
- `insights`
- `publisher.*`

Semantica:

- narrativa causal externa
- sentimiento y contexto noticioso

### 3.5 Feature layers

#### `financial`

Ejemplo:

- [balance_sheets_A.parquet](</D:/financial/balance_sheets/ticker=A/balance_sheets_A.parquet>)

Semantica:

- balances con `period_end`, `filing_date`, `fiscal_quarter`, `fiscal_year`, `timeframe`
- capa de fundamentales

#### `economic`

Ejemplo:

- [inflation.parquet](</C:/TSIS_Data/data/additional/economic/inflation.parquet>)

Columnas observadas:

- `date`
- `cpi`
- `cpi_year_over_year`
- `cpi_core`
- `pce`
- `pce_core`
- `pce_spending`

Semantica:

- macroeconomia exogena

#### `regime_indicators`

Ejemplo:

- [day.parquet](</D:/regime_indicators/etfs/DIA/day.parquet>)

Columnas observadas:

- `volume`
- `vwap`
- `open`
- `close`
- `high`
- `low`
- `trades`
- `datetime`
- `date`

Semantica:

- capa de proxies de mercado o ETF para regimen

Nota:

- el `datetime` del ejemplo observado requiere auditoria adicional antes de consumo institucional.

### 3.6 Short side data

#### `short_interest`

Ejemplo:

- [AMC.parquet](</C:/TSIS_Data/data/short/short_interest/AMC.parquet>)

Columnas observadas:

- `settlement_date`
- `ticker`
- `short_interest`
- `avg_daily_volume`
- `days_to_cover`

Semantica:

- crowding lenta
- presion de corto
- `days_to_cover`

#### `short_volume`

Ejemplo:

- [AMC.parquet](</C:/TSIS_Data/data/short/short_volume/AMC.parquet>)

Columnas observadas:

- `date`
- `total_volume`
- `short_volume`
- `exempt_volume`
- `non_exempt_volume`
- `short_volume_ratio`
- breakdown por venue:
  - `nyse_short_volume`
  - `nasdaq_carteret_short_volume`
  - `nasdaq_chicago_short_volume`
  - `adf_short_volume`

Semantica:

- shorting diario
- composicion por venue
- potencial explicativo de squeezes y crowding

## 4. Familias auxiliares o no primarias

### `images`

Ejemplo:

- `C:\TSIS_Data\data\images\...`

Lectura:

- capa de soporte visual o documental
- no debe tratarse como dataset economico primario

### `short_review`

Lectura:

- capa documental y de mantenimiento sobre short data
- no dataset primario

### `trades_ticks_2019_2025`

Lectura provisional:

- requiere inspeccion especifica antes de promoverse como capa institucional
- no debe presumirse equivalente al arbol `trades_ticks_prod_2005_2026`

## 5. Conclusiones operativas

1. El proyecto no solo contiene market data.
   Contiene tambien:
   - corporate actions
   - market events
   - identity
   - instrument typing
   - exogenous macro and news
   - fundamentals
   - short data

2. No todas las carpetas pobladas implican contenido real.
   Existen muchos parquets `_empty` en `dividends`, `splits`, `ticker_events` e `ipos`.

3. La arquitectura institucional debe separar:

- `price views`
- `event views`
- `identity views`
- `feature views`

4. Ningun agente deberia asumir que:

- ticker = common stock
- daily raw = adjusted
- quotes raw = misma escala que daily
- o que una capa noticiosa o de halt es solo "contexto opcional"

## 6. Relacion con otros documentos

Este inventario debe leerse junto con:

- `data_storage_topology_and_target_state.md`
- `price_semantics_and_adjustment_policy.md`
- `price_views_registry.md`
- `corporate_actions_adjustment_methodology.md`
