# DAS 0003 - Investigacion Profunda De Proveedores De Data

Fecha: 2026-07-09  
Experimento: EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003  
Estado: draft_research_v0_1  
**Objetivo**: 
```
identificar proveedores para conseguir toda la data posible que permita construir state tables segundo a segundo y modelar/inferir el primer movimiento DAS.
```

## Addendum 2026-07-09 - DAS API Descartada

Decision vigente:

```text
DAS CMD API no es util para 0003 y no tendremos acceso operativo a ella.
No debe aparecer como proveedor recomendado ni como capa live principal.
La investigacion de proveedores se centra en market data vendors externos: Databento, direct exchange feeds, CTA/UTP, WRDS TAQ, Polygon/Massive y fuentes especializadas.
```

## Decision Central

No hay un proveedor unico que cubra todo con calidad institucional, coste razonable y derechos claros. La solucion realista es un stack por capas:

```text
Capa 0 - TSIS actual: quotes historicas, trades historicos parciales, OHLCV, state tables, imagenes, halts.
Capa 1 - Proveedor externo pragmatico: Databento / Polygon-Massive / WRDS TAQ segun dataset, con T&S + NBBO + L2/L3 si se contrata.
Capa 2 - Direct feeds/SIP si el estudio justifica mas fidelidad: Nasdaq, NYSE, Cboe, IEX, MEMX, CTA/UTP, OPRA.
Capa 3 - Contexto y catalysts: SEC/FDA/ClinicalTrials, Bloomberg/LSEG/Dow Jones/RavenPack/Benzinga, short/borrow, options, social.
Capa 4 - Ejecucion real futura: broker/FIX/IBKR u otro broker con API/drop-copy si se decide operar; DAS API queda fuera por falta de acceso/utilidad.
Capa 5 - Observabilidad/calidad: clock sync, lineage, coverage, latency, licensing y sample audits.
```

## Recomendacion Ejecutiva

Para estudiar DAS ahora:

```text
1. Usar TSIS quotes historicas para construir state table segundo a segundo.
2. Anadir SEC EDGAR + FDA/openFDA + Nasdaq/FINRA/halts para contexto gratuito/as-of.
3. Estandarizar labels humanos.
4. Comprar solo si el estudio quote-driven demuestra que discrimina valid_das_impulse vs bad_chop.
```

Para mejorar historico sin montar infraestructura HF:

```text
1. Databento como primer candidato fuerte para MBO/MBP/trades/status/corporate actions/security master/OPRA segun dataset.
2. WRDS/NYSE TAQ si hay acceso academico/institucional y basta trades+quotes NMS tick-by-tick.
3. Polygon/Massive como API rapida para NBBO quotes, trades, reference, news y cobertura amplia, no como full L3.
```

Para live operativo:

```text
1. DAS CMD API queda descartada; el punto de observacion real debe ser proveedor externo contratado.
2. Guardar raw provider payloads o parquet original + coverage_quality + ingestion lineage.
3. Si hay presupuesto institucional: direct exchange feeds + SIP + OPRA.
```

Para nivel HF/profesional:

```text
1. Direct feeds por exchange: Nasdaq TotalView-ITCH, NYSE Integrated, Cboe PITCH/Depth, MEMX, IEX TOPS/DEEP.
2. SIP CTA/UTP para NBBO regulatorio.
3. OPRA para options.
4. Feed handler propio, timestamping, colocation/connectivity y simulador de ejecucion.
```

---

# Ranking De Proveedores Por Utilidad DAS

## Tier A - Mas Criticos Para El Movimiento

### 1. Databento

**Cubre**: historical/live API, schemas MBO/L3, MBP-10/L2, MBP-1/L1, trades, OHLCV, status, imbalance, OPRA, corporate actions, adjustment factors, security master; datasets listados incluyen Nasdaq TotalView-ITCH, NYSE Integrated, Cboe depth, IEX TOPS, MEMX, OPRA y otros.  
**Uso DAS**: mejor candidato comercial unico para investigar microestructura sin negociar feed por feed desde cero.  
**Ventaja**: unifica schemas, historical + live, Python/API, batch, replay; orientado a microestructura y modelos.  
**Limitacion**: coste y derechos dependen de dataset/uso; hay que confirmar cobertura exacta de small caps, premarket y profundidad por venue.  
**Prioridad**: P0/P1.  
**Decision**: primer proveedor comercial a evaluar para “queremos todo” en modo research/pragmatic.

Fuentes: https://databento.com/docs/schemas-and-data-formats/mbo y https://databento.com/docs/api-reference-historical/basics/datasets

### 2. Direct Exchange Feeds

**Cubre**: feeds oficiales por venue: Nasdaq TotalView-ITCH, NYSE Integrated/OpenBook, Cboe PITCH/Depth, IEX TOPS/DEEP, MEMX, etc.  
**Uso DAS**: maxima fidelidad para order book, depth, trades, imbalances y status.  
**Ventaja**: fuente primaria; necesario si el objetivo final es competir a nivel HF/profesional.  
**Limitacion**: contratos, fees, infraestructura, feed handlers, timestamping, colocation/connectivity; no es la primera compra para un laboratorio.  
**Prioridad**: P0 para HF, P1 para TSIS ahora.  
**Decision**: no comprar todo inicialmente; evaluar solo si el detector offline tiene edge.

Fuentes: NYSE Integrated Feed describe order-by-order, depth, trades, imbalances y status: https://www.nyse.com/data-products/catalog/integrated-feed

### 3. CTA/UTP SIP + NBBO

**Cubre**: trades y protected quotes consolidados, NBBO, LULD, SSR, regulatory halts. CTA cubre Network A/B; UTP cubre Tape C/Nasdaq-listed.  
**Uso DAS**: baseline regulatorio y consolidado para NBBO, quote/trade matching y compliance.  
**Ventaja**: referencia nacional; evita depender de una sola venue.  
**Limitacion**: menos profundo y potencialmente mas lento que direct feeds; no da full L2/L3.  
**Prioridad**: P0/P1.  
**Decision**: necesario para benchmark serio si se compran direct feeds o se quiere NBBO oficial.

Fuente CTA: https://www.ctaplan.com/index
Fuente UTP: https://www.utpplan.com/

### 4. WRDS / NYSE TAQ

**Cubre**: tick-by-tick trade and quote data del U.S. National Market System, intraday, microsecond, miles de issues.  
**Uso DAS**: excelente para investigacion academica de trades/quotes/NBBO historico.  
**Ventaja**: muy usado en investigacion; buen historico.  
**Limitacion**: no full L3; acceso normalmente institucional/academico; puede no ser ideal para live.  
**Prioridad**: P1.  
**Decision**: candidato fuerte si hay acceso via universidad/WRDS o presupuesto institucional.

Fuente: https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/nyse-trade-and-quote-taq/

---

# Matriz Por Familia De Datos

## 01. L3 / MBO / Order Lifecycle

**Proveedor ideal**: direct exchange feeds; Databento si dataset ofrece MBO para el venue; LOBSTER para historico academico Nasdaq; Bloomberg/LSEG/QuantHouse/dxFeed como candidatos institucionales a confirmar.  
**Valor DAS**: maximo para detectar consumo real de ask, cancelaciones, reposicionamiento de bid y liquidez falsa.  
**Estado TSIS**: no tenemos.  
**Compra recomendada**: Databento primero; direct feeds solo despues de validar edge.  
**Nota**: L3 sin timestamps y quality metadata no sirve para modelar segundo a segundo.

## 02. L2 / MBP / Depth

**Proveedor ideal**: Databento MBP-10/MBP-1/MBO, direct feeds NYSE/Nasdaq/Cboe/IEX/MEMX, dxFeed/IQFeed como candidatos a evaluar.  
**Valor DAS**: imbalance, depth, microprice, ask depletion, bid replenishment.  
**Estado TSIS**: no tenemos live propio; requiere proveedor externo para L2/L3 historico/live.  
**Compra recomendada**: pedir sample/cotizacion a Databento primero; direct feeds solo si el edge lo justifica.  
**Nota**: L2 agregado no distingue cancelacion vs ejecucion; hay que asociarlo con T&S.

## 03. T&S / Prints / Tape

**Proveedor ideal**: Databento trades, CTA/UTP SIP, Polygon/Massive trades, WRDS TAQ, direct exchange trades.  
**Valor DAS**: volumen agresor, velocidad de prints, dollar-volume, continuidad del impulso.  
**Estado TSIS**: historico parcial desde 09:30 en ejemplos; no hay live DAS util; requiere proveedor externo para T&S completo/premarket.  
**Compra recomendada**: DAS live + Databento/Polygon para cubrir gaps; WRDS TAQ si acceso.  
**Nota**: para premarket, confirmar cobertura hora a hora y condiciones de trades.

## 04. NBBO / Top Of Book

**Proveedor ideal**: CTA/UTP SIP, Polygon/Massive quotes, Databento MBP-1/BBO/TBBO, TSIS quotes actuales.  
**Valor DAS**: spread, mid, quote imbalance, trade signing, state table segundo a segundo.  
**Estado TSIS**: tenemos quotes historicas en 150/152 casos del denominador 0002.  
**Compra recomendada**: no comprar antes de explotar TSIS quotes; usar Polygon/Massive/Databento si falta cobertura.  
**Nota**: NBBO oficial y quotes locales no son equivalentes.

## 05. Auction Imbalance / NOII / Opening Imbalance

**Proveedor ideal**: Nasdaq NOII/TotalView, NYSE imbalance feeds, Databento imbalance schema/datasets si contratado.  
**Valor DAS**: continuidad hacia open, presion acumulada, riesgo de gap/open drive.  
**Estado TSIS**: no tenemos.  
**Compra recomendada**: P1, despues del detector core; no es necesario para primer estudio.  
**Nota**: importante para 09:28-09:30 y open, menos para despertar 04:00.

## 06. Halts / LULD / SSR / Status

**Proveedor ideal**: Nasdaq Trade Halts, CTA SIP status/LULD/SSR, SEC suspensions, Databento status, TSIS Halts actual.  
**Valor DAS**: filtrar gaps artificiales, resumption, risk state.  
**Estado TSIS**: tenemos halts master multisource.  
**Compra recomendada**: no comprar; completar con fuentes oficiales gratuitas y/o Databento status si ya se contrata.  
**Nota**: debe entrar como feature de calidad/riesgo, no como alpha principal.

Fuentes: https://www.nasdaqtrader.com/Trader.aspx?id=TradeHalts y https://www.ctaplan.com/index

## 07. Execution / Orders / Fills / Routing

**Proveedor ideal**: IBKR TWS/API, broker FIX/drop-copy, Lightspeed/CenterPoint/Cobra/TradeStation/Alpaca u otro broker elegido; DAS API descartada.  
**Valor DAS**: saber si la senal se puede ejecutar con slippage y riesgo aceptable.  
**Estado TSIS**: no tenemos para 0003.  
**Compra recomendada**: no antes de validar evento; despues, IBKR/FIX u otro broker con fills crudos. No DAS API.  
**Nota**: sin fills no hay profit real, solo estudio de evento.

Fuente IBKR API: https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/

## 08. OHLCV Intraday / Bars / Aggregates

**Proveedor ideal**: TSIS actual, Polygon/Massive aggregates, Databento OHLCV schemas, Tiingo, Intrinio, EODHD/FirstRate/Kibot para coste bajo.  
**Valor DAS**: auditoria visual y baseline, no senal primaria.  
**Estado TSIS**: tenemos OHLCV 1m y quote-guarded outputs.  
**Compra recomendada**: no comprar como prioridad; ya tenemos suficiente para 0003.  
**Nota**: bars pierden microestructura; no sirven para cazar el primer segundo del movimiento.

## 09. Corporate Actions / Security Master / Symbology

**Proveedor ideal**: Databento security master/corporate actions, Polygon/Massive reference, SEC EDGAR, OpenFIGI, Bloomberg/FactSet/LSEG/S&P Capital IQ para institucional.  
**Valor DAS**: evitar errores de prior close, splits, ticker continuity y survivorship.  
**Estado TSIS**: parcial con reference snapshots y state tables.  
**Compra recomendada**: usar TSIS/SEC/OpenFIGI primero; Databento/Polygon si se compra market data; FactSet/Bloomberg solo si hay presupuesto institucional.  
**Nota**: todo debe ser as-of.

Fuentes: Databento reference APIs/datasets: https://databento.com/docs/api-reference-reference/basics/overview
OpenFIGI: https://www.openfigi.com/api
SEC companyfacts/submissions APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## 10. Float / Shares / Market Cap / Dilution

**Proveedor ideal**: SEC EDGAR raw filings, FactSet, Bloomberg, LSEG/Refinitiv, S&P Capital IQ, Intrinio/FMP como candidatos de coste menor.  
**Valor DAS**: explica capacidad de squeeze/impulse y destruccion posterior.  
**Estado TSIS**: no certificado para 0003.  
**Compra recomendada**: empezar con SEC EDGAR + parser propio de shares/offering; comprar FactSet/Bloomberg/LSEG si se requiere calidad institucional.  
**Nota**: float es dificil; muchas APIs ofrecen shares/market cap, no float intradia exacto.

Fuente SEC APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## 11. News / Press Releases / Catalysts

**Proveedor ideal**: Bloomberg News/Terminal/B-PIPE, LSEG/Reuters News, Dow Jones Newswires, RavenPack, Benzinga News API, Polygon/Massive news, SEC EDGAR, GlobeNewswire/PRNewswire/BusinessWire, FDA/openFDA/ClinicalTrials.gov para biotech.  
**Valor DAS**: identificar causa del despertar; priorizar suscripciones TMS/Lv2; separar random chop de catalyst-driven move.  
**Estado TSIS**: no contrato 0003.  
**Compra recomendada**: empezar gratuito con SEC/FDA/ClinicalTrials + press release feeds; evaluar Benzinga/Polygon para small-cap real-time; RavenPack/Bloomberg/LSEG si se requiere NLP institucional.  
**Nota**: timestamp de ingestion y source timestamp son criticos; headline tardio no puede usarse como feature anterior.

Fuentes: SEC APIs https://www.sec.gov/search-filings/edgar-application-programming-interfaces; ClinicalTrials.gov API https://clinicaltrials.gov/data-api/about-api; openFDA https://open.fda.gov/apis/

## 12. Social Attention / Retail Flow Proxies

**Proveedor ideal**: X API, Reddit API, Stocktwits API/enterprise, Dataminr, Quiver Quant, Google Trends.  
**Valor DAS**: crowding/retail attention; explica continuidad y blow-off.  
**Estado TSIS**: no tenemos.  
**Compra recomendada**: P3; no comprar antes de resolver core microstructure.  
**Nota**: alto riesgo de ruido/leakage; timestamps y rate limits importan.

Fuentes: Reddit API https://www.reddit.com/dev/api/; X API https://developer.x.com/en/docs

## 13. Short Interest / Borrow / Locate / SSR / Fails-To-Deliver

**Proveedor ideal**: FINRA short sale volume, Nasdaq/NYSE short interest, SEC fails-to-deliver, S3 Partners, ORTEX, EquiLend DataLend, S&P Global Securities Finance, IBKR shortable shares/borrow as proxy.  
**Valor DAS**: squeeze potential, sell-pressure constraints, borrow stress.  
**Estado TSIS**: no contrato 0003 certificado.  
**Compra recomendada**: usar FINRA/SEC gratuitas primero; IBKR si se tiene cuenta; S3/ORTEX/EquiLend si el modelo demuestra necesidad.  
**Nota**: short interest oficial es lento; borrow/locate live es mas util para operativa.

Fuentes: FINRA short sale volume https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data; SEC FTD https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data

## 14. Options Chain / Options Flow / OPRA

**Proveedor ideal**: OPRA official, Databento OPRA, Cboe LiveVol, ORATS, OptionMetrics IvyDB, ThetaData, Polygon/Massive options, Tradier.  
**Valor DAS**: confirmacion o crowding si ticker tiene opciones liquidas; IV/volume/OI para contexto.  
**Estado TSIS**: no tenemos.  
**Compra recomendada**: P2/P3 para DAS small-caps; no core salvo tickers con options liquidas.  
**Nota**: OPRA es muy voluminoso y caro; para small-cap DAS muchas acciones ni tendran opciones relevantes.

Fuentes: OPRA plan https://www.opraplan.com/; Databento OPRA datasets https://databento.com/docs/api-reference-historical/basics/datasets

## 15. Market Regime / ETFs / Futures / VIX / Macro

**Proveedor ideal**: Cboe VIX, CME futures, Polygon/Massive/Databento for ETF/index proxies, FRED for macro slow data.  
**Valor DAS**: regime/risk; no dispara el primer impulso, pero afecta follow-through y sizing.  
**Estado TSIS**: no contrato 0003.  
**Compra recomendada**: bajo coste; usar ETF OHLCV/quotes y VIX.  
**Nota**: no dejar que regime tape un patron microestructural claro.

Fuentes: Cboe VIX https://www.cboe.com/tradable_products/vix/; FRED API https://fred.stlouisfed.org/docs/api/fred/

## 16. Broker Account / Risk State

**Proveedor ideal**: broker API elegido: DAS, IBKR, TradeStation, Alpaca, Lightspeed/CenterPoint/FIX segun cuenta.  
**Valor DAS**: buying power, restrictions, max loss, open positions, order limits.  
**Estado TSIS**: no 0003.  
**Compra recomendada**: despues de validar evento y antes de paper/live execution.  
**Nota**: no es alpha, es safety.

Fuentes: IBKR API docs https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/; Alpaca docs https://docs.alpaca.markets/docs/trading-api

## 17. Infrastructure Telemetry / Clock / Observability

**Proveedor ideal**: self-hosted OpenTelemetry, Prometheus/Grafana, chrony/NTP, Meinberg/PTP si se quiere alta precision.  
**Valor DAS**: demostrar que el sistema ve eventos en orden y sin lag; necesario para live defensible.  
**Estado TSIS**: no 0003.  
**Compra recomendada**: implementar barato desde el principio para live; no esperar a produccion.  
**Nota**: si capture_quality falla, el evento debe quedar `quality__state=not_trustworthy`.

Fuentes: OpenTelemetry https://opentelemetry.io/docs/; Prometheus https://prometheus.io/docs/introduction/overview/; chrony https://chrony-project.org/

## 18. Data Quality / Lineage / Lake Governance

**Proveedor ideal**: TSIS contracts, Great Expectations/Soda/dbt tests, DVC/lakeFS, parquet manifests, custom lineage.  
**Valor DAS**: reproducibilidad, anti-leakage, as-of correctness, versionado de labels/features.  
**Estado TSIS**: parcial con 01_foundations y manifests.  
**Compra recomendada**: no hace falta proveedor caro; reforzar proceso interno.  
**Nota**: cada provider nuevo debe entrar con schema, policy y sample audit.

Fuentes: Great Expectations https://docs.greatexpectations.io/; lakeFS https://docs.lakefs.io/

## 19. LOB Simulation / Replay / RL Execution

**Proveedor ideal**: self-built replay con Databento/L2/L3, JAX-LOB, ABIDES, queue-reactive models; vendors de TCA si institucional.  
**Valor DAS**: despues de validar evento, permite probar entry/stop/sizing bajo slippage y latencia.  
**Estado TSIS**: no tenemos.  
**Compra recomendada**: no comprar ahora; construir replay simple primero.  
**Nota**: simulador sin datos L2/L3 reales puede dar falsa seguridad.

Fuentes: JAX-LOB https://arxiv.org/abs/2308.13289; queue-reactive model https://arxiv.org/abs/1312.0563

---

# Stack Recomendado Por Fase

## Fase 0 - Sin Compra Nueva

```text
TSIS quotes historicas
TSIS OHLCV 1m
TSIS state tables + images
TSIS Halts
SEC EDGAR APIs
openFDA / ClinicalTrials.gov
FINRA short sale volume
SEC FTD
Nasdaq halts/public status where applicable
```

Objetivo: demostrar si top-of-book historico separa valid_das_impulse de bad_chop/no_punch.

## Fase 1 - Compra Pragmatica Para Research

```text
Databento: MBO/MBP/trades/status/security master/OPRA segun presupuesto
Polygon/Massive: API breadth, trades/quotes/reference/news si se necesita API rapida
WRDS TAQ: si hay acceso institucional/academico
Benzinga o similar: small-cap catalyst news real-time si los labels muestran importancia de news
```

Objetivo: cubrir gaps de historico y mejorar features microestructurales sin montar direct feeds.

## Fase 2 - Proveedor Externo Live/Historico Profundo

```text
provider trades/T&S -> raw provider payload/parquet
provider L2/MBP or L3/MBO -> raw provider payload/parquet
coverage_quality.jsonl
capture_quality.jsonl
runtime telemetry
clock sync
provider raw payload/schema preservation
```

Objetivo: detector live real con el dato que TSIS realmente ve.

## Fase 3 - Institucional/HF

```text
Nasdaq TotalView-ITCH
NYSE Integrated/OpenBook
Cboe PITCH/Depth
IEX TOPS/DEEP
MEMX feed
CTA/UTP SIP
OPRA
FIX/drop-copy/execution feeds
colo/timestamping if needed
```

Objetivo: competir con data profesional y minimizar ambiguedad de venue/latency.

---

# Proveedores Que NO Deben Ser Core Para El Primer Estudio

```text
Social-only providers: demasiado ruido, P3.
Options-only providers: no todos los DAS small caps tienen options liquidas.
Macro-only providers: util para regime, no para detectar primer punch.
OHLCV-only vendors: ya tenemos bars; no resuelven microestructura.
News-only vendors: utiles, pero no sustituyen book/trades.
Execution-only brokers: necesarios despues, no antes de validar evento.
```

---

# Due Diligence Antes De Comprar

Para cada proveedor hay que exigir:

```text
1. Cobertura por ticker/date/hora, incluyendo premarket 04:00-09:30 ET.
2. Timestamps: exchange/source/capture, timezone, precision, ordering guarantees.
3. Tipo real de book: L1, MBP/L2, MBO/L3.
4. Trades: condiciones, corrections/cancels, odd lots, TRF, off-exchange.
5. NBBO: SIP oficial o vendor-computed.
6. Licencia: research, redistribution, derived data, live display/non-display.
7. Coste por dataset, exchange fees, non-display fees, user/device fees.
8. API replay/batch/export a parquet.
9. Raw payload o schema suficientemente fiel.
10. Sample para nuestros casos DAS: MSS 2025-09-29, SONN 2025-07-14, OPAD 2026-01-09, AMOD 2026-01-07.
```

---

# Proveedor Preferido Por Familia Critica

```text
MBO/L3 historico/live: Databento primero; direct feeds si institucional.
L2/Depth: Databento/direct feeds como candidatos principales; no DAS Lv2.
T&S: Databento/Polygon/CTA-UTP/TAQ/direct feeds; no DAS tms.
NBBO: TSIS quotes para estudio; CTA/UTP o Databento/Polygon para oficial/comercial.
Halts/status: TSIS + Nasdaq/SEC/CTA; Databento status si ya contratado.
News/catalyst: SEC/FDA gratis; Benzinga/Polygon; Bloomberg/LSEG/RavenPack institucional.
Short/borrow: FINRA/SEC gratis; IBKR proxy; S3/ORTEX/EquiLend institucional.
Options: OPRA/Databento/ORATS/OptionMetrics/ThetaData, solo si hace falta.
Execution: IBKR/FIX/u otro broker con API/drop-copy, despues de validar evento. No DAS API.
Telemetry: OpenTelemetry/Prometheus/chrony, construir interno.
```

---

# Fuentes Consultadas

- Databento schemas MBO/MBP/trades: https://databento.com/docs/schemas-and-data-formats/mbo
- Databento datasets: https://databento.com/docs/api-reference-historical/basics/datasets
- Databento reference APIs: https://databento.com/docs/api-reference-reference/basics/overview
- NYSE Integrated Feed: https://www.nyse.com/data-products/catalog/integrated-feed
- CTA Plan: https://www.ctaplan.com/index
- UTP Plan: https://www.utpplan.com/
- OPRA Plan: https://www.opraplan.com/
- WRDS / NYSE TAQ: https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/nyse-trade-and-quote-taq/
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC Fails-to-Deliver: https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data
- FINRA short sale volume: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data
- ClinicalTrials.gov API: https://clinicaltrials.gov/data-api/about-api
- openFDA APIs: https://open.fda.gov/apis/
- IBKR API docs: https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-doc/
- Alpaca Trading API: https://docs.alpaca.markets/docs/trading-api
- Cboe VIX: https://www.cboe.com/tradable_products/vix/
- FRED API: https://fred.stlouisfed.org/docs/api/fred/
- OpenFIGI API: https://www.openfigi.com/api
- OpenTelemetry: https://opentelemetry.io/docs/
- Prometheus: https://prometheus.io/docs/introduction/overview/
- chrony: https://chrony-project.org/
- Great Expectations: https://docs.greatexpectations.io/
- lakeFS: https://docs.lakefs.io/
- JAX-LOB: https://arxiv.org/abs/2308.13289
- Queue-reactive model: https://arxiv.org/abs/1312.0563

---

# Decision Para 0003

La compra inmediata mas racional no es “todo”. Es:

```text
1. Exprimir TSIS quotes historicas y construir das_realtime_impulse_event_state_v0_1.
2. Diseñar contrato de proveedor externo T&S/L2/L3/NBBO ya.
3. Pedir samples/cotizacion a Databento para MBO/MBP/trades/status en los casos DAS.
4. Evaluar Polygon/Massive solo como API breadth/reference/news, no como L3.
5. Mantener direct feeds institucionales como Fase 3, no Fase 1.
```

Si una compra unica debe priorizarse para investigacion profunda de microestructura, el primer candidato es Databento. Si el objetivo cambia a operativa/HF institucional, el camino correcto son direct exchange feeds + SIP + OPRA + execution/drop-copy.


