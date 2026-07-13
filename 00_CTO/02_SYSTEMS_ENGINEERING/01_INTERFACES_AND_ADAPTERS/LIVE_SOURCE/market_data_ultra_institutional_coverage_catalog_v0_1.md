# Market Data Ultra-Institutional Coverage Catalog v0.1

Fecha: 2026-07-09
Owner layer: 00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/LIVE_SOURCE
Estado: draft_cto_reference

## Proposito

Este documento complementa el catalogo DAS 0003. El catalogo DAS 0003 estaba optimizado para datos accionables y razonablemente obtenibles para estudiar/capturar el primer impulso. Este documento enumera la capa extrema: datos regulatorios, venue-private, broker-private, participant-private, cross-asset y no observables directamente.

## Por Que No Estaba En El Documento Anterior

No estaba completo en el documento DAS inicial por scope, no porque sea irrelevante.

```text
El documento DAS 0003 buscaba la data necesaria y comprable para modelar first impulse.
Esta capa incluye datos que pueden ser utiles, pero muchos no son comprables, no son publicos, requieren acuerdos institucionales, o solo existen dentro de venues, brokers, reguladores o participantes.
```

Decision:

```text
Para DAS first impulse, el core sigue siendo T&S + L1/NBBO + L2/L3 + timestamps + quality + labels.
La data de este documento mejora explicacion, ejecucion, vigilancia, riesgo y simulacion, pero no siempre es necesaria para el primer estudio offline.
```

## Taxonomia De Observabilidad

```text
A. Observable y comprable: direct feeds, SIP, OPRA, TAQ, MBO/MBP vendors, news, reference.
B. Observable solo por venues/reguladores: audit trail completo, surveillance flags, full order lifecycle consolidado.
C. Broker/internalizer private: client flow, routing decisions, wholesaler behavior, fills internos.
D. Participant private: inventario, intenciones, hidden liquidity, proprietary alpha, risk limits.
E. Inferible: hidden/iceberg, inventory pressure, toxic flow, queue position si no tenemos order id.
```

## Regla De Uso

```text
No disenar un sistema que dependa de data no observable.
Si una data no es comprable, se documenta como no_observable o regulator_only y se sustituye por proxies inferibles.
```

---

# Catalogo De Data Ultra-Institucional

## 01. Consolidated Audit Trail / CAT-Level Order Events

**Prioridad**: P0 para regulador, P2 para DAS investigacion  
**Estado TSIS**: NO_TENEMOS / REGULATOR_ONLY  
**Definicion**: audit trail regulatorio de eventos de orden: recepcion, routing, modification, cancellation, execution, account/customer identifiers y timestamps normalizados.  
**Representa**: historia regulatoria completa de ordenes y rutas a traves del mercado.  
**Ventaja para DAS**: permitiria reconstruir flujo real y routing con una fidelidad imposible desde feeds publicos. Muy util para entender si el impulso nace de participantes concretos, routers o venues.  
**Asociaciones**: broker orders, exchange executions, routing, timestamps, customer/order ids, surveillance.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\cat_order_events_regulator_only.schema.md  

## 02. Venue-Native Full Order Lifecycle Across All Exchanges

**Prioridad**: P0 para HF, P1 para microestructura avanzada  
**Estado TSIS**: NO_TENEMOS / REQUIERE_DIRECT_FEEDS  
**Definicion**: mensajes nativos por venue: add, cancel, replace, execute, trade, imbalance, status, con semantica propia del exchange.  
**Representa**: vida real del order book venue por venue antes de agregacion vendor.  
**Ventaja para DAS**: permite saber donde nace el movimiento y si el push se propaga o solo existe en un venue.  
**Asociaciones**: L3/MBO, SIP, venue latency, cross-venue lead-lag, routing.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\venue_native_order_lifecycle.schema.md  

## 03. Dark Pool / ATS Execution Prints And Venue Attribution

**Prioridad**: P1  
**Estado TSIS**: NO_TENEMOS / PARCIALMENTE_OBSERVABLE  
**Definicion**: ejecuciones fuera de exchanges lit, incluyendo ATS/dark pools, TRF prints y, cuando existe, atribucion de venue/condition.  
**Representa**: volumen ejecutado fuera del libro visible.  
**Ventaja para DAS**: ayuda a detectar acumulacion/distribucion que no aparece en L2. Un impulso puede ser precedido por prints off-exchange o internalizados.  
**Asociaciones**: TRF, T&S, conditions, NBBO, odd lots, institutional blocks.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\ats_trf_dark_prints.schema.md  

## 04. TRF / Off-Exchange Print Detail

**Prioridad**: P1  
**Estado TSIS**: NO_TENEMOS / REQUIERE_PROVEEDOR  
**Definicion**: prints reportados a Trade Reporting Facilities, con timestamp, price, size, sale condition, reporting facility y flags.  
**Representa**: ejecuciones off-exchange reportadas al mercado.  
**Ventaja para DAS**: diferencia volumen lit vs off-exchange y mejora trade signing.  
**Asociaciones**: T&S, NBBO, dark pools, wholesaler/internalizer activity.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\trf_off_exchange_prints.schema.md  

## 05. Odd Lots And Odd-Lot NBBO

**Prioridad**: P1  
**Estado TSIS**: REQUIERE_PROVEEDOR / DEPENDE_DEL_FEED  
**Definicion**: quotes y trades de menos de round lot, y top-of-book incluyendo odd lots si el feed lo permite.  
**Representa**: parte relevante del precio real, especialmente en acciones caras o fragmentadas.  
**Ventaja para DAS**: evita perder micro movimientos y mejora lectura de top-of-book en nombres con lots pequenos.  
**Asociaciones**: NBBO, SIP, direct feeds, T&S, spread, microprice.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\odd_lot_quotes_trades.schema.md  

## 06. Retail Price Improvement / Wholesaler/Internalizer Flow

**Prioridad**: P1/P2  
**Estado TSIS**: NO_TENEMOS / BROKER_PRIVATE_OR_REPORT_PROXY  
**Definicion**: ejecuciones retail internalizadas, price improvement, wholesaler route, fill quality y venue/market maker.  
**Representa**: flujo minorista que no necesariamente interactua con el libro lit.  
**Ventaja para DAS**: small caps pueden tener participacion retail fuerte; esta data ayuda a separar retail chase de institutional flow.  
**Asociaciones**: Rule 605/606 reports, broker fills, TRF prints, T&S, social attention.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\retail_price_improvement_flow.schema.md  

## 07. Broker Smart Order Router Decisions

**Prioridad**: P1 para ejecucion, P2 para investigacion  
**Estado TSIS**: NO_TENEMOS / BROKER_PRIVATE  
**Definicion**: decisiones del router: venues candidatos, route elegido, rechazo, reroute, latency, fee/rebate logic y fill probability.  
**Representa**: como una orden propia llega realmente al mercado.  
**Ventaja para DAS**: una senal puede existir pero no ser ejecutable si el router llega tarde o el venue elegido no tiene liquidez.  
**Asociaciones**: fills, L2/L3, venue fees, latency, broker risk.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\smart_order_router_decisions.schema.md  

## 08. Broker Client Flow Segmentation

**Prioridad**: P1/P2  
**Estado TSIS**: NO_TENEMOS / BROKER_PRIVATE  
**Definicion**: clasificacion interna de flujo por tipo de cliente: retail, institutional, prop, algo, market maker, toxic/non-toxic.  
**Representa**: calidad y origen probable del flujo.  
**Ventaja para DAS**: ayudaria a distinguir impulso retail, institutional accumulation, squeeze o flow toxico.  
**Asociaciones**: broker fills, routing, price improvement, T&S, adverse selection.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\broker_client_flow_segments.schema.md  

## 09. True Queue Position For Our Orders

**Prioridad**: P1 para ejecucion  
**Estado TSIS**: NO_TENEMOS / REQUIERE_ORDER_ACK_AND_BOOK  
**Definicion**: posicion estimada o real de una orden propia dentro de la cola a un precio/venue.  
**Representa**: probabilidad de fill antes de que el precio se mueva.  
**Ventaja para DAS**: esencial para saber si una entrada limit en first impulse es ejecutable.  
**Asociaciones**: order ack, MBO/L3, fills, cancels, venue priority rules, latency.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\own_order_queue_position.schema.md  

## 10. Hidden / Iceberg Liquidity Inference

**Prioridad**: P1  
**Estado TSIS**: INFERIBLE / NO_DIRECTAMENTE_OBSERVABLE  
**Definicion**: liquidez no visible en el libro lit, inferida por ejecuciones repetidas sin decremento visible equivalente o replenishment anomalo.  
**Representa**: oferta/demanda oculta.  
**Ventaja para DAS**: puede explicar por que un push se frena aunque L2 parezca limpio, o por que absorbe mucho volumen sin romper.  
**Asociaciones**: T&S, L2/L3, executions, replenishment, spread, venue rules.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\hidden_iceberg_inference.schema.md  
## 11. Cross-Feed Latency / Lead-Lag Timing

**Prioridad**: P0 para HF, P1 para live avanzado  
**Estado TSIS**: NO_TENEMOS / REQUIERE_INFRA_Y_FEEDS  
**Definicion**: medicion precisa de diferencias temporales entre direct feeds, SIP, vendor feed, broker feed y sistema propio.  
**Representa**: quien ve primero el cambio de precio y con cuanto retraso.  
**Ventaja para DAS**: evita confundir senal con lag; permite saber si un proveedor es demasiado lento para first impulse.  
**Asociaciones**: direct feeds, SIP, capture timestamps, PTP/NTP, event ordering, execution.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\cross_feed_latency_lead_lag.schema.md  

## 12. Market Maker Inventory / Risk State

**Prioridad**: P1 teorica, P3 practica  
**Estado TSIS**: NO_TENEMOS / PARTICIPANT_PRIVATE  
**Definicion**: inventario, risk limits, hedge state y quoting pressure de market makers o liquidity providers.  
**Representa**: presion interna no publica que puede cambiar quotes y spreads.  
**Ventaja para DAS**: explicaria fades, spreads anchos, pullbacks y cambios bruscos de liquidez.  
**Asociaciones**: quotes, depth, options hedging, inventory models, volatility.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\market_maker_inventory_private.schema.md  

## 13. Venue-Specific Auction Order Book

**Prioridad**: P1  
**Estado TSIS**: REQUIERE_PROVEEDOR_DIRECT_FEED  
**Definicion**: detalle granular de subastas: opening/closing/IPO/halt-resume imbalance, indicative price, paired shares, unpaired shares, side, updates por venue.  
**Representa**: presion acumulada en subasta y precio indicativo.  
**Ventaja para DAS**: util cerca de open, resume tras halt y continuidad/destruccion despues del premarket.  
**Asociaciones**: NOII, LULD, halts, regular open, T&S, outcomes.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\venue_auction_order_book.schema.md  

## 14. Full Options Order Book And Greeks Cross-Asset State

**Prioridad**: P1/P2  
**Estado TSIS**: NO_TENEMOS / REQUIERE_OPRA_OR_OPTIONS_VENDOR  
**Definicion**: options quotes/trades/order book, IV surface, greeks, OI, dealer gamma proxies y underlying link.  
**Representa**: presion derivada y hedging potencial.  
**Ventaja para DAS**: en tickers optionable, options flow puede anticipar o amplificar underlying impulse.  
**Asociaciones**: OPRA, underlying T&S/L2, gamma exposure, volatility, market maker inventory.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\full_options_cross_asset_state.schema.md  

## 15. Futures / ETF / Basket Lead-Lag Books

**Prioridad**: P2  
**Estado TSIS**: NO_TENEMOS / REQUIERE_CROSS_ASSET_FEEDS  
**Definicion**: order books y prints de futures, ETFs, sector baskets y correlated instruments.  
**Representa**: presion macro/sectorial y lead-lag cross-asset.  
**Ventaja para DAS**: menos critico en micro/small caps, pero util para distinguir idiosyncratic impulse de market-wide move.  
**Asociaciones**: SPY/QQQ/IWM, sector ETFs, futures, options, market regime.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\cross_asset_lead_lag_books.schema.md  

## 16. Intraday Securities Lending / Locate / Borrow Book

**Prioridad**: P1/P2  
**Estado TSIS**: NO_TENEMOS / REQUIERE_BROKER_OR_SECURITIES_FINANCE_PROVIDER  
**Definicion**: availability, borrow rate, locate fills, hard-to-borrow state, recall risk y securities lending supply intradia.  
**Representa**: restriccion real de shorting y squeeze potential.  
**Ventaja para DAS**: ayuda a explicar movimientos explosivos y dificultad de fade/short.  
**Asociaciones**: short interest, FTD, broker locate, float, SSR, outcomes.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\intraday_securities_lending_locate.schema.md  

## 17. Settlement / Clearing / Margin Constraint State

**Prioridad**: P2/P3  
**Estado TSIS**: NO_TENEMOS / BROKER_CLEARING_PRIVATE  
**Definicion**: clearing constraints, margin changes, settlement risk, concentration limits y broker risk controls.  
**Representa**: restricciones post-trade que pueden bloquear sizing o routing.  
**Ventaja para DAS**: no detecta el push, pero define si una estrategia puede escalar sin riesgo operativo.  
**Asociaciones**: broker account state, execution, borrow, risk engine, compliance.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\clearing_margin_constraint_state.schema.md  

## 18. Regulatory Surveillance Flags

**Prioridad**: P2  
**Estado TSIS**: REGULATOR_ONLY / PARTIALLY_INFERABLE  
**Definicion**: flags o scores internos de surveillance: spoofing, layering, wash trading, momentum ignition, manipulation alerts.  
**Representa**: patrones sospechosos detectados por reguladores/venues.  
**Ventaja para DAS**: evitar confundir impulso real con actividad manipulativa o no tradeable.  
**Asociaciones**: L3, order lifecycle, cancellations, trade prints, participant ids, CAT.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\regulatory_surveillance_flags.schema.md  

## 19. Participant Identity / MPID / Attribution

**Prioridad**: P1/P2  
**Estado TSIS**: PARCIAL_SEGUN_FEED / MUCHAS_VECES_NO_PUBLICO  
**Definicion**: identificadores de market participant, broker, market maker, MPID o venue participant attribution.  
**Representa**: quien esta proporcionando o tomando liquidez, cuando el feed lo expone.  
**Ventaja para DAS**: ayuda a distinguir actividad de market maker, retail wholesaler, institutional broker o venue-specific liquidity.  
**Asociaciones**: L2/L3, direct feeds, T&S, dark/ATS, broker routing.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\participant_identity_attribution.schema.md  

## 20. Indicative Interest / IOI / Block Liquidity

**Prioridad**: P2  
**Estado TSIS**: NO_TENEMOS / INSTITUTIONAL_PRIVATE  
**Definicion**: indications of interest, block crossing interest, conditional orders, RFQ/negotiated liquidity.  
**Representa**: liquidez institucional no siempre visible en lit book.  
**Ventaja para DAS**: puede explicar prints grandes o absorcion sin L2 visible. Menos accionable para small-cap impulse si no hay acceso institucional.  
**Asociaciones**: dark pools, ATS, block trades, broker flow, TRF prints.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\ioi_block_liquidity.schema.md  

## 21. Payment For Order Flow / Rule 605-606 Reports

**Prioridad**: P2  
**Estado TSIS**: PUBLIC_REPORTS / LOW_FREQUENCY  
**Definicion**: informes de routing, execution quality, payment for order flow, venues usados y fill quality por broker/market center.  
**Representa**: estructura de ejecucion retail agregada, no evento intradia exacto.  
**Ventaja para DAS**: contexto sobre donde se internaliza flujo retail y calidad de fills esperada.  
**Asociaciones**: retail flow, wholesalers, broker routing, execution quality.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\rule_605_606_execution_quality.schema.md  

## 22. News Embargo / Primary Source Release Timestamps

**Prioridad**: P1/P2  
**Estado TSIS**: REQUIERE_NEWS_VENDOR_OR_PRIMARY_SOURCE  
**Definicion**: timestamps exactos de publicacion, embargo release, wire ingestion, headline dissemination y first-seen por proveedor.  
**Representa**: cuando la informacion se hizo disponible de verdad.  
**Ventaja para DAS**: muchos impulses small-cap nacen de catalysts; source timestamp evita leakage.  
**Asociaciones**: SEC/FDA/news wires, scanner trigger, T&S acceleration, social attention.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\primary_source_news_release_timestamps.schema.md  

## 23. Data Vendor Entitlement / License State

**Prioridad**: P1 operacional  
**Estado TSIS**: A_CREAR  
**Definicion**: permisos, exchange fees, non-display rights, redistribution rights, delayed/live status y dataset entitlements por proveedor.  
**Representa**: que podemos usar legal y tecnicamente.  
**Ventaja para DAS**: evita construir un sistema sobre data que no se puede usar en live o redistribution.  
**Asociaciones**: provider contracts, ingestion, compliance, data quality, procurement.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\market_data_entitlement_state.schema.md  

## 24. Inferred Toxic Flow / Adverse Selection Score

**Prioridad**: P1/P2  
**Estado TSIS**: INFERIBLE / A_CREAR  
**Definicion**: score derivado de order flow, spread response, short-horizon price impact y fill outcomes que estima toxicidad del flujo.  
**Representa**: si tomar/proveer liquidez contra ese flujo es peligroso.  
**Ventaja para DAS**: distingue impulso explotable de flujo que ya llega tarde y revierte.  
**Asociaciones**: T&S, L2/L3, OFI, execution fills, MFE/MAE, spread.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\inferred_toxic_flow_score.schema.md  

## 25. Counterfactual Execution / Venue Fill Probability

**Prioridad**: P1 para estrategia  
**Estado TSIS**: A_CREAR / REQUIERE_SIMULADOR  
**Definicion**: estimacion de si una orden hipotetica se habria llenado por venue, precio y timestamp.  
**Representa**: diferencia entre senal visual y fill posible.  
**Ventaja para DAS**: crucial para validar entradas impulse/dip/rebreak sin sobreestimar edge.  
**Asociaciones**: L3/L2, queue position, trades, fills reales, simulator, latency.  
**Ejemplo/path**: C:\TSIS_Data\00_CTO\02_SYSTEMS_ENGINEERING\01_INTERFACES_AND_ADAPTERS\LIVE_SOURCE\expected_contracts\counterfactual_execution_fill_probability.schema.md  

---

# Existe Mas Data?

Si, si ampliamos la definicion a informacion privada o no observable. En la practica el limite es este:

```text
1. Todo lo que el mercado publica: comprable o descargable.
2. Todo lo que venues y reguladores ven: no siempre comprable.
3. Todo lo que brokers/internalizers ven: privado/contractual.
4. Todo lo que participantes saben: inventario, intencion, alpha, riesgo, no publico.
5. Todo lo oculto: hidden liquidity, iceberg, motives, solo inferible.
```

Conclusion:

```text
No existe un catalogo finito de "toda la data posible" si incluimos informacion privada e intenciones.
Si hablamos de data de mercado usable por TSIS, este documento + el catalogo DAS 0003 cubren el mapa completo razonable: raw market data, provider data, regulatory/private layers, execution, context, quality e inferred signals.
```

# Relacion Con DAS 0003

Para DAS first impulse:

```text
Core obligatorio: T&S + L1/NBBO + L2/L3 + timestamps + quality + labels.
Capa avanzada util: dark/TRF, odd lots, auction, venue-native, cross-feed latency, short/borrow.
Capa no dependible: CAT, broker client flow, market maker inventory, regulatory flags, participant intent.
```

Regla final:

```text
Si una data no se puede comprar, capturar o inferir de forma defendible, no puede ser feature obligatoria.
Puede existir como explicacion teorica, proxy o riesgo residual.
```
