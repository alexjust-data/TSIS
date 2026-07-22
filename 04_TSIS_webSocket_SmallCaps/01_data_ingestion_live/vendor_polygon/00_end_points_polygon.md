A fecha de 13 de marzo de 2026, y revisando la documentación oficial de Polygon/Massive, esto es lo que
tienes para stocks si quieres localizar todo lo descargable/consultable de forma rigurosa.

Si por “descargar” entiendes histórico o bulk:

- REST te sirve para consultas puntuales e históricas.
- Flat Files es la vía realmente masiva para descargar datasets enteros.
- WebSocket no es “descarga” en bloque, sino streaming en vivo.

1. REST API de Stocks
Precios, trades, quotes, barras

- /v3/trades/{stockTicker} (https://polygon.io/docs/rest/stocks/trades-quotes/trades/) — trades tick-by-ti
ck históricos.
- /v3/quotes/{stockTicker} (https://polygon.io/docs/rest/stocks/trades-quotes/quotes) — NBBO quotes histór
icas.
- /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}
(https://polygon.io/docs/rest/stocks/aggregates/custom-bars) — barras históricas custom.
- /v1/open-close/{stocksTicker}/{date}
(https://polygon.io/docs/rest/stocks/aggregates/daily-ticker-summary) — open/close diario.
- /v2/aggs/ticker/{stocksTicker}/prev (https://polygon.io/docs/rest/stocks/aggregates/previous-day-bar) —
barra del día anterior.
- /v2/aggs/grouped/locale/us/market/stocks/{date}
(https://polygon.io/docs/rest/stocks/aggregates/daily-market-summary) — OHLC diario para todo el mercado
USA.
- /v2/last/trade/{stocksTicker} (https://polygon.io/docs/rest/stocks/trades-quotes/last-trade) — último tr
ade.
- /v2/last/nbbo/{stocksTicker} (https://polygon.io/docs/rest/stocks/trades-quotes/last-quote) — última quo
te NBBO.

Snapshots / estado actual

- /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}
(https://polygon.io/docs/rest/stocks/snapshots/single-ticker-snapshot) — snapshot de un ticker.
- /v2/snapshot/locale/us/markets/stocks/tickers
(https://polygon.io/docs/rest/stocks/snapshots/full-market-snapshot) — snapshot full market o lista de t
ickers.
- /v2/snapshot/locale/us/markets/stocks/{direction}
(https://polygon.io/docs/rest/stocks/snapshots/top-market-movers) — top gainers/losers.
- /v3/snapshot (https://polygon.io/docs/rest/stocks/snapshots/unified-snapshot) — snapshot unificado multi-
activo; sirve para stocks con type=stocks.

Tickers y referencia

- /v3/reference/tickers (https://polygon.io/docs/rest/stocks/tickers/all-tickers) — master list de tickers.
- /v3/reference/tickers/{ticker} (https://polygon.io/docs/rest/stocks/tickers/ticker-overview/) — detalle
point-in-time de ticker.
- /v3/reference/tickers/types (https://polygon.io/docs/rest/stocks/tickers/ticker-types) — tipos de ticker.
- /v1/related-companies/{ticker} (https://polygon.io/docs/rest/stocks/tickers/related-tickers) — related t
ickers.
- /vX/reference/tickers/{id}/events (https://polygon.io/docs/rest/stocks/corporate-actions/ticker-events) —
eventos del ticker, experimental.
- /v3/reference/exchanges (https://polygon.io/docs/stocks/get_v3_reference_exchanges) — exchanges.
- /v3/reference/conditions (https://polygon.io/docs/rest/stocks/market-operations/condition-codes) — condi
tion codes.

Corporate actions

- /v3/reference/splits (https://polygon.io/docs/rest/stocks/corporate-actions/splits) — splits.
- /v3/reference/dividends (https://polygon.io/docs/rest/stocks/corporate-actions/dividends) — dividendos.
- /vX/reference/ipos (https://polygon.io/docs/rest/stocks/corporate-actions/ipos) — IPOs.

Fundamentales, news y sentimiento

- /stocks/financials/v1/balance-sheets (https://polygon.io/docs/rest/stocks/fundamentals/balance-sheets) —
balances.
- /stocks/financials/v1/income-statements
(https://polygon.io/docs/rest/stocks/fundamentals/income-statements) — income statements.
- /stocks/financials/v1/cash-flow-statements
(https://polygon.io/docs/rest/stocks/fundamentals/cash-flow-statements) — cash flows.
- /stocks/financials/v1/ratios (https://polygon.io/docs/rest/stocks/fundamentals/ratios) — ratios.
- /stocks/v1/short-interest (https://polygon.io/docs/rest/stocks/fundamentals/short-interest) — short inte
rest.
- /v2/reference/news (https://polygon.io/docs/rest/stocks/news/) — news por ticker/fecha.
- /vX/reference/financials (https://polygon.io/docs/rest/stocks/fundamentals/financials) — financials anti
guo, deprecated.

Market operations

- /v1/marketstatus/now (https://polygon.io/docs/rest/stocks/market-operations/market-status) — market stat
us actual.
- /v1/marketstatus/upcoming (https://polygon.io/docs/rest/stocks/market-operations/market-holidays) — próx
imos holidays.

Indicadores técnicos

- /v1/indicators/sma/{stockTicker}
(https://polygon.io/docs/rest/stocks/technical-indicators/simple-moving-average) — SMA.
- /v1/indicators/ema/{stockTicker}
(https://polygon.io/docs/rest/stocks/technical-indicators/exponential-moving-average) — EMA.
- /v1/indicators/rsi/{stockTicker}
(https://polygon.io/docs/rest/stocks/technical-indicators/relative-strength-index) — RSI.
- /v1/indicators/macd/{stockTicker}
(https://polygon.io/docs/rest/stocks/technical-indicators/moving-average-convergence-divergence) — MACD.

2. WebSocket de Stocks
Esto no es bulk download, pero sí son todos los feeds core de streaming que vi en la documentación oficial:

- Trades (https://polygon.io/docs/websocket/stocks/trades)
- Quotes (https://polygon.io/docs/websocket/stocks/quotes)
- Aggregates per second (https://polygon.io/docs/websocket/stocks/aggregates-per-second)
- Aggregates per minute (https://polygon.io/docs/websocket/stocks/aggregates-per-minute)
- LULD (https://polygon.io/docs/websocket/stocks/luld)
- NOI / Imbalances (https://polygon.io/docs/websocket/stocks/imbalances)
- FMV (https://polygon.io/docs/websocket/stocks/fair-market-value)
- Overview WS (https://polygon.io/docs/stocks/ws_getting-started)

3. Flat Files de Stocks
Si quieres descargar “absolutamente todo” de verdad, aquí está la parte más importante:

- us_stocks_sip/trades_v1 (https://polygon.io/docs/flat-files/stocks/trades) — trades históricos diarios en
CSV.gz.
- us_stocks_sip/quotes_v1 (https://polygon.io/docs/flat-files/stocks/quotes) — quotes históricas diarias en
CSV.gz.
- us_stocks_sip/minute_aggs_v1 (https://polygon.io/docs/flat-files/stocks/minute-aggregates) — minute aggr
egates.
- us_stocks_sip/day_aggs_v1 (https://polygon.io/docs/flat-files/stocks/day-aggregates) — day aggregates.
- Overview Flat Files Stocks (https://polygon.io/docs/flat-files/stocks/overview)

Conclusión práctica
Si tu objetivo es cobertura completa de stocks en Polygon, el inventario core es:

- 33 endpoints/feeds útiles si cuentas REST + WebSocket + Flat Files.
- Para descarga masiva real, quédate con los 4 Flat Files.
- Para histórico selectivo, usa sobre todo:
    - trades
    - quotes
    - aggs/range
    - grouped daily
    - splits
    - dividends
    - financials
    - news

No he incluido productos partner separados tipo Benzinga/analyst ratings porque no forman parte del núcleo
de la documentación base de Stocks; si quieres, te hago una segunda pasada igual de exhaustiva pero
incluyendo add-ons y datasets partner de Polygon para equities.


---


A fecha de 17 de marzo de 2026, ampliando la búsqueda a add-ons y partner datasets oficiales de Polygon para equities/
stocks, el mapa riguroso queda así.

Core de Stocks en Polygon
Estos son los endpoints/feeds nativos de stocks que sí encontré en la documentación oficial:

- GET /v3/trades/{stockTicker}: trades históricos tick-by-tick.
https://polygon.io/docs/rest/stocks/trades-quotes/trades/
- GET /v3/quotes/{stockTicker}: quotes históricas NBBO.
https://polygon.io/docs/rest/stocks/trades-quotes/quotes
- GET /v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{from}/{to}: barras históricas.
https://polygon.io/docs/rest/stocks/aggregates/custom-bars
- GET /v1/open-close/{stocksTicker}/{date}: open/close diario.
https://polygon.io/docs/rest/stocks/aggregates/daily-ticker-summary
- GET /v2/aggs/ticker/{stocksTicker}/prev: barra previa.
https://polygon.io/docs/rest/stocks/aggregates/previous-day-bar
- GET /v2/aggs/grouped/locale/us/market/stocks/{date}: grouped daily para todo el mercado.
https://polygon.io/docs/rest/stocks/aggregates/daily-market-summary
- GET /v2/last/trade/{stocksTicker}: último trade.
https://polygon.io/docs/rest/stocks/trades-quotes/last-trade
- GET /v2/last/nbbo/{stocksTicker}: última quote.
https://polygon.io/docs/rest/stocks/trades-quotes/last-quote
- GET /v2/snapshot/locale/us/markets/stocks/tickers/{stocksTicker}: snapshot individual.
https://polygon.io/docs/rest/stocks/snapshots/single-ticker-snapshot
- GET /v2/snapshot/locale/us/markets/stocks/tickers: snapshot full market.
https://polygon.io/docs/rest/stocks/snapshots/full-market-snapshot
- GET /v2/snapshot/locale/us/markets/stocks/{direction}: top gainers/losers.
https://polygon.io/docs/rest/stocks/snapshots/top-market-movers
- GET /v3/snapshot: snapshot unificado, usable para type=stocks.
https://polygon.io/docs/rest/stocks/snapshots/unified-snapshot
- GET /v3/reference/tickers: listado maestro de tickers.
https://polygon.io/docs/rest/stocks/tickers/all-tickers
- GET /v3/reference/tickers/{ticker}: overview/reference del ticker.
https://polygon.io/docs/rest/stocks/tickers/ticker-overview/
- GET /v3/reference/tickers/types: tipos de ticker.
https://polygon.io/docs/rest/stocks/tickers/ticker-types
- GET /v1/related-companies/{ticker}: related tickers.
https://polygon.io/docs/rest/stocks/tickers/related-tickers
- GET /v3/reference/exchanges: exchanges.
https://polygon.io/docs/stocks/get_v3_reference_exchanges
- GET /v3/reference/conditions: códigos de condición.
https://polygon.io/docs/rest/stocks/market-operations/condition-codes
- GET /v3/reference/splits: splits.
https://polygon.io/docs/rest/stocks/corporate-actions/splits
- GET /v3/reference/dividends: dividendos.
https://polygon.io/docs/rest/stocks/corporate-actions/dividends
- GET /vX/reference/ipos: IPOs.
https://polygon.io/docs/rest/stocks/corporate-actions/ipos
- GET /stocks/financials/v1/balance-sheets: balance sheets.
https://polygon.io/docs/rest/stocks/fundamentals/balance-sheets
- GET /stocks/financials/v1/income-statements: income statements.
https://polygon.io/docs/rest/stocks/fundamentals/income-statements
- GET /stocks/financials/v1/cash-flow-statements: cash flow statements.
https://polygon.io/docs/rest/stocks/fundamentals/cash-flow-statements
- GET /stocks/financials/v1/ratios: ratios.
https://polygon.io/docs/rest/stocks/fundamentals/ratios
- GET /stocks/v1/short-interest: short interest.
https://polygon.io/docs/rest/stocks/fundamentals/short-interest
- GET /stocks/v1/short-volume: short volume.
https://polygon.io/docs/rest/stocks/fundamentals/short-volume
- GET /v2/reference/news: ticker news general de Polygon.
https://polygon.io/docs/rest/stocks/news/
- GET /v1/marketstatus/now: market status.
https://polygon.io/docs/rest/stocks/market-operations/market-status
- GET /v1/marketstatus/upcoming: holidays/upcoming market status.
https://polygon.io/docs/rest/stocks/market-operations/market-holidays
- GET /v1/indicators/sma/{stockTicker}
https://polygon.io/docs/rest/stocks/technical-indicators/simple-moving-average
- GET /v1/indicators/ema/{stockTicker}
https://polygon.io/docs/rest/stocks/technical-indicators/exponential-moving-average
- GET /v1/indicators/rsi/{stockTicker}
https://polygon.io/docs/rest/stocks/technical-indicators/relative-strength-index
- GET /v1/indicators/macd/{stockTicker}
https://polygon.io/docs/rest/stocks/technical-indicators/moving-average-convergence-divergence

Streaming oficial de Stocks

- Trades WS: https://polygon.io/docs/websocket/stocks/trades
- Quotes WS: https://polygon.io/docs/websocket/stocks/quotes
- Per-second aggregates WS: https://polygon.io/docs/websocket/stocks/aggregates-per-second
- Per-minute aggregates WS: https://polygon.io/docs/websocket/stocks/aggregates-per-minute
- LULD WS: https://polygon.io/docs/websocket/stocks/luld
- Imbalances/NOI WS: https://polygon.io/docs/websocket/stocks/imbalances
- FMV WS: https://polygon.io/docs/websocket/stocks/fair-market-value

Flat Files oficiales de Stocks
Esto es lo realmente “descargable en masa”:

- us_stocks_sip/trades_v1
https://polygon.io/docs/flat-files/stocks/trades
- us_stocks_sip/quotes_v1
https://polygon.io/docs/flat-files/stocks/quotes
- us_stocks_sip/minute_aggs_v1
https://polygon.io/docs/flat-files/stocks/minute-aggregates
- us_stocks_sip/day_aggs_v1
https://polygon.io/docs/flat-files/stocks/day-aggregates
- overview flat files stocks
https://polygon.io/docs/flat-files/stocks/overview

Add-ons / Partner datasets de equities en Polygon
Aquí está la ampliación que me pediste.

Benzinga
Polygon documenta estos endpoints partner para equities:

- GET /benzinga/v1/ratings: analyst ratings.
https://polygon.io/docs/rest/partners/benzinga/analyst-ratings
- GET /benzinga/v1/consensus-ratings/{ticker}: consensus ratings.
https://polygon.io/docs/rest/partners/benzinga/consensus-ratings
- GET /benzinga/v1/analyst-insights: rationale/comentario del analista.
https://polygon.io/docs/rest/partners/benzinga/analyst-insights
- GET /benzinga/v1/analysts: analyst details.
https://polygon.io/docs/rest/partners/benzinga/analyst-details
- GET /benzinga/v1/firms: firm details.
https://polygon.io/docs/rest/partners/benzinga/firm-details
- GET /benzinga/v1/earnings: earnings calendar + reported/estimated data.
https://polygon.io/docs/rest/partners/benzinga/earnings
- GET /benzinga/v1/guidance: corporate guidance.
https://polygon.io/docs/rest/partners/benzinga/corporate-guidance
- GET /benzinga/v2/news: Benzinga real-time news.
https://polygon.io/docs/rest/partners/benzinga/news
- GET /benzinga/v1/news: versión antigua, deprecated.
https://polygon.io/docs/rest/partners/benzinga/news-v1

Polygon además anunció oficialmente este paquete partner en mayo-junio de 2025:

- anuncio: https://polygon.io/blog/benzingadata-partnership//
- changelog: https://polygon.io/changelog

TMX / Wall Street Horizon
Partner dataset orientado a eventos corporativos de equities:

- GET /tmx/v1/corporate-events: corporate events globales.
https://polygon.io/docs/rest/partners/tmx/corporate-events
- página partner: https://polygon.io/partners/tmx

Esto cubre earnings announcement dates, dividend dates, shareholder meetings, stock splits, analyst days, conferences y más.

Conclusión rigurosa
Si cuentas todo lo oficial que encontré para equities/stocks en Polygon:

- REST core de stocks: 34 endpoints aprox.
- WebSocket stocks: 7 feeds.
- Flat Files stocks: 4 datasets S3.
- Partner REST para equities:
    - Benzinga: 9 endpoints documentados, de los cuales 1 está deprecated.
    - TMX: 1 endpoint documentado.

En total, para equities/stocks, Polygon te ofrece de forma oficial y documentada alrededor de 55 superficies de acceso entre  REST, WS, flat files y partner APIs.

No he encontrado en la documentación oficial actual de Polygon endpoints separados de SEC filings, insider transactions o  ownership bajo stocks/partners. Eso no demuestra que no existan internamente o en beta, pero no los he visto documentados oficialmente en la pasada que acabo de hacer.