# Massive / Polygon: endpoints de stocks para U.S. common stocks (`type=CS`) con permisos altos

Fecha de verificacion: 2026-03-20

## Resumen ejecutivo

Massive / Polygon no publica "endpoints separados para common stock" como URLs distintas. La segmentacion de acciones ordinarias de EE. UU. se hace sobre endpoints generales de `stocks`, filtrando normalmente con:

- `market=stocks`
- `type=CS`
- `locale=us`

Cuando necesitas reconstruir el universo historico, conviene anadir tambien:

- `date=YYYY-MM-DD`
- `active=true|false`

Conclusion operativa:

- Para descargar U.S. common stocks, el endpoint maestro de universo es `GET /v3/reference/tickers`.
- Para historico de precios y microestructura, los endpoints clave son `aggs`, `trades`, `quotes`, `open-close`, `prev`, `last trade`, `last nbbo` y `snapshots`.
- Para descarga masiva, la via mas completa son los flat files `us_stocks_sip/*`.
- Para acceso mas elevado, la referencia practica es `Stocks Business + Full Market` para tiempo real comercial; para historico/flat files amplios, `Stocks Advanced` o `Stocks Business` segun el producto concreto.

## Alcance de "permisos mas elevados"

Esta es la lectura practica basada en la documentacion oficial de Massive / Polygon revisada el 2026-03-20:

- `Stocks Advanced`
  - Acceso alto para historico, quotes, trades, snapshots, fundamentals y flat files.
  - Suele cubrir todo el historico relevante y descarga masiva EOD.
- `Stocks Business`
  - Nivel comercial alto.
  - Incluye acceso ampliado a tiempo real y streaming avanzado.
- `Stocks Business + Full Market` expansion
  - Es la combinacion mas cercana a "maximos permisos" para stocks en uso comercial con cobertura de mercado completa en tiempo real.
- `Enterprise`
  - Nivel superior contractual, fuera del autoservicio estandar.

Nota importante:

- Inferencia a partir de pricing y docs: no todos los datasets tick-level en tiempo real quedan implicitos con `Business` base; la propia documentacion comercial distingue expansiones como `Full Market`.

## Regla correcta para Common Stocks (CS)

No existe una familia de endpoints separada "solo CS". El patron correcto es:

1. Usar endpoints de `stocks`.
2. Filtrar el universo en reference con `market=stocks&type=CS&locale=us`.
3. Consumir market data historica o realtime para los tickers resultantes.

Ejemplo conceptual:

```http
GET /v3/reference/tickers?market=stocks&type=CS&locale=us&active=true&limit=1000
```

## Inventario completo de endpoints utiles para descargar U.S. common stocks

### 1. Reference / Universe

`GET /v3/reference/tickers`

Uso:

- Endpoint maestro para construir el universo de tickers.
- Aqui aplicas `market=stocks&type=CS&locale=us`.
- Permite universo actual o historico con `date`.

Filtros clave:

- `market=stocks`
- `type=CS`
- `locale=us`
- `active=true|false`
- `date=YYYY-MM-DD`
- `limit`, `cursor`, `sort`, `order`

`GET /v3/reference/tickers/{ticker}`

Uso:

- Detalle de un ticker individual.
- Sirve para metadatos y campos como market cap, weighted shares outstanding, nombre, descripcion, branding, SIC/NAICS cuando existan.

`GET /v3/reference/tickers/types`

Uso:

- Catalogo oficial de tipos de ticker.
- Importante para confirmar que `CS` corresponde a common stock.

`GET /v3/reference/exchanges`

Uso:

- Lista de exchanges y codigos relacionados.
- Util para mapear venues, MICs o codigos de intercambio.

`GET /vX/reference/tickers/{id}/events`

Uso:

- Endpoint experimental de eventos asociados a tickers.
- No debe tratarse como contrato estable salvo necesidad especifica.

`GET /v1/related-companies/{ticker}`

Uso:

- Tickers relacionados.
- No es esencial para descarga de precios, pero forma parte del universo de referencia de stocks.

### 2. Corporate Actions / Eventos corporativos

`GET /v3/reference/dividends`

Uso:

- Dividendos historicos.
- Necesario para ajustes, total return y control de corporate actions.

`GET /v3/reference/splits`

Uso:

- Splits historicos.
- Imprescindible para series ajustadas y reconstruccion de historicos consistentes.

`GET /vX/reference/ipos`

Uso:

- Calendario o historico de IPOs segun la version/documentacion vigente.
- Relevante si trabajas small caps y quieres detectar altas al universo.

### 3. Market Data historico / REST

`GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}`

Uso:

- OHLCV historico en barras custom.
- Endpoint principal para descargar velas por ticker.

Casos tipicos:

- Diario
- Minuto
- Multi-minuto
- Ajustado o no ajustado

`GET /v2/aggs/grouped/locale/us/market/stocks/{date}`

Uso:

- Resumen diario agrupado de todo el mercado U.S. stocks para una fecha.
- Muy util para ingestas diarias amplias y backfills compactos.

`GET /v1/open-close/{stocksTicker}/{date}`

Uso:

- Open, close y datos intradia resumidos para una fecha concreta.

`GET /v2/aggs/ticker/{stocksTicker}/prev`

Uso:

- Barra del dia previo.
- Util para validaciones, pipelines y comparativas rapidas.

`GET /v3/trades/{stockTicker}`

Uso:

- Trades historicos tick-level.
- Fundamental si quieres microestructura, tape, condiciones, secuencias y timestamps finos.

`GET /v3/quotes/{stockTicker}`

Uso:

- Quotes historicos top-of-book / NBBO historico.
- Necesario para spreads, libro top-of-book y analisis de liquidez.

`GET /v2/last/trade/{stocksTicker}`

Uso:

- Ultimo trade conocido.
- Endpoint de consulta puntual, no de descarga masiva historica.

`GET /v2/last/nbbo/{stocksTicker}`

Uso:

- Ultima NBBO / quote conocida.
- Util para estado de mercado actual por ticker.

### 4. Snapshots

`GET /v2/snapshot/locale/us/markets/stocks/tickers`

Uso:

- Snapshot amplio del mercado de acciones U.S.
- Combina campos de ultimo trade, ultima quote, daily bar, prev day bar, etc.

`GET /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}`

Uso:

- Snapshot de un solo ticker.
- Muy util para monitorizacion o enriquecimiento ligero.

`GET /v2/snapshot/locale/us/markets/stocks/{direction}`

Uso:

- Top market movers.
- `direction` tipicamente `gainers` o `losers`.

`GET /v3/snapshot`

Uso:

- Snapshot unificado multi-activo.
- Para stocks, se usa `type=stocks`.
- No sustituye necesariamente todos los snapshots especializados, pero conviene tenerlo en inventario.

### 5. Fundamentals

`GET /stocks/financials/v1/income-statements`

Uso:

- Estados de resultados.

`GET /stocks/financials/v1/balance-sheets`

Uso:

- Balances.

`GET /stocks/financials/v1/cash-flow-statements`

Uso:

- Flujos de caja.

`GET /stocks/financials/v1/ratios`

Uso:

- Ratios fundamentales normalizados.

`GET /stocks/v1/short-interest`

Uso:

- Short interest.
- Muy relevante en small caps.

`GET /stocks/v1/short-volume`

Uso:

- Short volume.
- Complementa el short interest con otra dimension de actividad short.

Nota de versionado:

- La familia moderna de financials reemplaza endpoints experimentales antiguos. La documentacion y el changelog reflejan migraciones y deprecaciones a partir de 2025.

### 6. News

`GET /v2/reference/news`

Uso:

- Noticias asociadas a tickers.
- Util para eventos, catalysts y enrichments.

### 7. Technical Indicators

Estos endpoints no son la fuente base de precios, pero forman parte del catalogo oficial de stocks y pueden ser utiles si quieres descargar indicadores calculados por el proveedor:

`GET /v1/indicators/sma/{stockTicker}`
`GET /v1/indicators/ema/{stockTicker}`
`GET /v1/indicators/macd/{stockTicker}`
`GET /v1/indicators/rsi/{stockTicker}`

Observacion:

- Para pipelines cuantitativos serios, normalmente se descargan `aggs` y se recalculan internamente.

### 8. WebSocket stocks

Canales principales documentados para stocks:

- Trades
- Quotes
- Aggregates per second
- Aggregates per minute
- LULD
- NOI / imbalances
- FMV

Lectura operativa:

- Si buscas ingest realtime de maximo nivel, estos canales completan la cobertura REST.
- Para casos puramente batch / descarga historica, no sustituyen a `aggs`, `trades`, `quotes` ni a flat files.

### 9. Flat Files / descarga masiva

Estos son los datasets mas importantes para descarga bulk de U.S. equities:

`us_stocks_sip/day_aggs_v1`

Contenido:

- Barras diarias OHLCV de U.S. equities.

`us_stocks_sip/minute_aggs_v1`

Contenido:

- Barras por minuto OHLCV de U.S. equities.

`us_stocks_sip/trades_v1`

Contenido:

- Trades tick-level con timestamps de alta precision.

`us_stocks_sip/quotes_v1`

Contenido:

- Quotes top-of-book con timestamps de alta precision.

Lectura de cobertura:

- Si tu objetivo es "descargar todo" a escala, los flat files son la via mas eficiente.
- Para common stocks, el filtrado a `CS` se hace downstream usando el universo de reference.

## Tabla practica

| Categoria | Endpoint / Dataset | Sirve para U.S. common stocks | Uso principal | Nota de acceso alto |
|---|---|---:|---|---|
| Reference | `/v3/reference/tickers` | Si | Universo maestro | Filtrar `market=stocks&type=CS&locale=us` |
| Reference | `/v3/reference/tickers/{ticker}` | Si | Metadata por ticker | Muy util para enrichment |
| Reference | `/v3/reference/tickers/types` | Si | Catalogo de tipos | Confirma `CS` |
| Reference | `/v3/reference/exchanges` | Si | Catalogo de exchanges | Mapping de venues |
| Reference | `/vX/reference/tickers/{id}/events` | Parcial | Eventos | Experimental |
| Reference | `/v1/related-companies/{ticker}` | Parcial | Pares/relacionados | No esencial para descarga |
| Corporate actions | `/v3/reference/dividends` | Si | Dividendos | Relevante para ajustes |
| Corporate actions | `/v3/reference/splits` | Si | Splits | Relevante para ajustes |
| Corporate actions | `/vX/reference/ipos` | Si | IPOs | Relevante para small caps |
| Historical | `/v2/aggs/ticker/{ticker}/range/...` | Si | OHLCV por ticker | Base de historicos |
| Historical | `/v2/aggs/grouped/locale/us/market/stocks/{date}` | Si | Mercado completo diario | Muy eficiente para batch |
| Historical | `/v1/open-close/{ticker}/{date}` | Si | Open/close diario | Consulta compacta |
| Historical | `/v2/aggs/ticker/{ticker}/prev` | Si | Barra previa | Consulta puntual |
| Historical | `/v3/trades/{ticker}` | Si | Trades tick-level | Requiere acceso alto |
| Historical | `/v3/quotes/{ticker}` | Si | Quotes tick-level | Requiere acceso alto |
| Realtime point | `/v2/last/trade/{ticker}` | Si | Ultimo trade | Consulta puntual |
| Realtime point | `/v2/last/nbbo/{ticker}` | Si | Ultima quote/NBBO | Consulta puntual |
| Snapshot | `/v2/snapshot/locale/us/markets/stocks/tickers` | Si | Snapshot de mercado | Muy util para monitorizacion |
| Snapshot | `/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}` | Si | Snapshot individual | Ligero y practico |
| Snapshot | `/v2/snapshot/locale/us/markets/stocks/{direction}` | Si | Gainers/losers | Ranking intradia |
| Snapshot | `/v3/snapshot` | Si | Snapshot unificado | Requiere filtrar `type=stocks` |
| Fundamentals | `/stocks/financials/v1/income-statements` | Si | Income statements | Familia moderna |
| Fundamentals | `/stocks/financials/v1/balance-sheets` | Si | Balance sheets | Familia moderna |
| Fundamentals | `/stocks/financials/v1/cash-flow-statements` | Si | Cash flow | Familia moderna |
| Fundamentals | `/stocks/financials/v1/ratios` | Si | Ratios | Familia moderna |
| Fundamentals | `/stocks/v1/short-interest` | Si | Short interest | Muy util en small caps |
| Fundamentals | `/stocks/v1/short-volume` | Si | Short volume | Muy util en small caps |
| News | `/v2/reference/news` | Si | Noticias | Enrichment / catalysts |
| Technicals | `/v1/indicators/sma/{ticker}` | Si | SMA | Derivado de precios |
| Technicals | `/v1/indicators/ema/{ticker}` | Si | EMA | Derivado de precios |
| Technicals | `/v1/indicators/macd/{ticker}` | Si | MACD | Derivado de precios |
| Technicals | `/v1/indicators/rsi/{ticker}` | Si | RSI | Derivado de precios |
| WebSocket | Trades | Si | Realtime trades | Acceso alto |
| WebSocket | Quotes | Si | Realtime quotes | Acceso alto |
| WebSocket | Aggs second | Si | Realtime barras | Acceso alto |
| WebSocket | Aggs minute | Si | Realtime barras | Acceso alto |
| WebSocket | LULD | Si | Bandas de limit up/down | Acceso alto |
| WebSocket | NOI / Imbalances | Si | Auction imbalance | Acceso alto |
| WebSocket | FMV | Si | Fair market value | Tipicamente comercial alto |
| Flat files | `us_stocks_sip/day_aggs_v1` | Si | Bulk daily OHLCV | Descarga masiva |
| Flat files | `us_stocks_sip/minute_aggs_v1` | Si | Bulk minute OHLCV | Descarga masiva |
| Flat files | `us_stocks_sip/trades_v1` | Si | Bulk trades | Descarga masiva avanzada |
| Flat files | `us_stocks_sip/quotes_v1` | Si | Bulk quotes | Descarga masiva avanzada |

## Lo que faltaba o estaba incompleto en los apuntes originales

Tu lista era razonablemente buena, pero estaba incompleta en estos puntos:

- Faltaba `GET /v2/aggs/ticker/{stocksTicker}/prev`
- Faltaba `GET /v2/last/trade/{stocksTicker}`
- Faltaba `GET /v2/last/nbbo/{stocksTicker}`
- Faltaba `GET /v2/snapshot/locale/us/markets/stocks/{direction}`
- Faltaba `GET /v3/snapshot` con `type=stocks`
- Faltaba `GET /v1/related-companies/{ticker}`
- Faltaba `GET /vX/reference/ipos`
- Faltaban los indicadores `SMA`, `EMA`, `MACD`, `RSI`
- Faltaban canales WebSocket adicionales: `aggregates per second`, `aggregates per minute`, `LULD`, `NOI`, `FMV`
- En fundamentals faltaba reflejar la familia moderna posterior a la deprecacion de endpoints experimentales antiguos

## Recomendacion practica para un pipeline de small caps U.S. common stocks

Si el objetivo es descargar y mantener una base de datos completa de small caps U.S. common stocks, la arquitectura sensata con Massive / Polygon es:

1. Construir el universo con `GET /v3/reference/tickers` usando:
   - `market=stocks`
   - `type=CS`
   - `locale=us`
   - `active=true|false`
   - `date=` cuando necesites punto en el tiempo
2. Enriquecer con:
   - `GET /v3/reference/tickers/{ticker}`
   - `GET /v3/reference/splits`
   - `GET /v3/reference/dividends`
   - `GET /vX/reference/ipos`
3. Descargar precios base con:
   - `GET /v2/aggs/ticker/{stocksTicker}/range/...`
   - o flat files `day_aggs_v1` / `minute_aggs_v1`
4. Si necesitas microestructura:
   - `GET /v3/trades/{stockTicker}`
   - `GET /v3/quotes/{stockTicker}`
   - o flat files `trades_v1` / `quotes_v1`
5. Si necesitas fundamentales/event-driven:
   - income statements
   - balance sheets
   - cash flow statements
   - ratios
   - short interest
   - short volume
   - news

## Enlaces oficiales

Massive

- Stocks Overview: https://massive.com/docs/stocks/
- Changelog: https://www.massive.com/changelog
- Massive pricing for stocks: https://massive.com/pricing?product=stocks
- Massive SIP / business page: https://massive.com/sip
- Massive flat files day aggregates example: https://massive.com/docs/flat-files/stocks/day-aggregates/2025/05

Polygon / Massive docs espejo por endpoint

- All Tickers: https://polygon.io/docs/rest/stocks/tickers/all-tickers
- Ticker Overview: https://polygon.io/docs/rest/stocks/tickers/ticker-overview/
- Exchanges: https://polygon.io/docs/rest/stocks/market-operations/exchanges
- Related Tickers: https://polygon.io/docs/rest/stocks/tickers/related-tickers
- Dividends: https://polygon.io/docs/rest/stocks/corporate-actions/dividends
- Splits: https://polygon.io/docs/rest/stocks/corporate-actions/splits
- IPOs: https://polygon.io/docs/rest/stocks/corporate-actions/ipos
- Custom Bars: https://polygon.io/docs/rest/stocks/aggregates/custom-bars
- Daily Market Summary: https://polygon.io/docs/rest/stocks/aggregates/daily-market-summary
- Daily Ticker Summary / Open-Close: https://polygon.io/docs/rest/stocks/aggregates/daily-ticker-summary
- Previous Day Bar: https://polygon.io/docs/rest/stocks/aggregates/previous-day-bar
- Trades: https://polygon.io/docs/rest/stocks/trades-quotes/trades/
- Quotes: https://polygon.io/docs/rest/stocks/trades-quotes/quotes
- Last Trade: https://polygon.io/docs/rest/stocks/trades-quotes/last-trade
- Last Quote / NBBO: https://polygon.io/docs/rest/stocks/trades-quotes/last-quote
- Full Market Snapshot: https://polygon.io/docs/rest/stocks/snapshots/full-market-snapshot
- Single Ticker Snapshot: https://polygon.io/docs/rest/stocks/snapshots/single-ticker-snapshot
- Top Market Movers: https://polygon.io/docs/rest/stocks/snapshots/top-market-movers
- Unified Snapshot: https://polygon.io/docs/rest/stocks/snapshots/unified-snapshot
- News: https://polygon.io/docs/rest/stocks/news
- Income Statements: https://polygon.io/docs/rest/stocks/fundamentals/income-statements
- Balance Sheets: https://polygon.io/docs/rest/stocks/fundamentals/balance-sheets
- Cash Flow Statements: https://polygon.io/docs/rest/stocks/fundamentals/cash-flow-statements
- Ratios: https://polygon.io/docs/rest/stocks/fundamentals/ratios
- Short Interest: https://polygon.io/docs/rest/stocks/fundamentals/short-interest
- Short Volume: https://polygon.io/docs/rest/stocks/fundamentals/short-volume
- Stocks WebSocket Overview: https://polygon.io/docs/stocks/ws_getting-started
- Stocks WebSocket Trades: https://polygon.io/docs/websocket/stocks/trades
- Stocks WebSocket Quotes: https://polygon.io/docs/websocket/stocks/quotes
- Stocks WebSocket Aggregates Per Minute: https://polygon.io/docs/websocket/stocks/aggregates-per-minute
- Stocks WebSocket LULD: https://polygon.io/docs/websocket/stocks/luld
- Stocks WebSocket Imbalances: https://polygon.io/docs/websocket/stocks/imbalances
- Stocks WebSocket Fair Market Value: https://polygon.io/docs/websocket/stocks/fair-market-value
- Stocks Flat Files Trades: https://polygon.io/docs/flat-files/stocks/trades
- Stocks Flat Files Quotes: https://polygon.io/docs/flat-files/stocks/quotes
- Stocks Flat Files Minute Aggregates: https://polygon.io/docs/flat-files/stocks/minute-aggregates
- Stocks Flat Files Day Aggregates: https://polygon.io/docs/flat-files/stocks/day-aggregates

## Nota final

Si el criterio exacto es "todos los endpoints de stocks que puedo usar para descargar U.S. common stocks con el acceso mas alto posible", el conjunto anterior cubre el catalogo practico relevante de Massive / Polygon para stocks al 2026-03-20, incluyendo REST, WebSocket y flat files.

La regla correcta no es buscar "endpoints distintos para CS", sino:

- usar endpoints de stocks,
- construir el universo `CS` desde reference,
- y luego descargar precios, eventos, fundamentales, news o microestructura sobre ese universo.



