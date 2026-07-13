# DAS 0003 - Catalogo Completo De Data Para State Tables Segundo A Segundo

Fecha: 2026-07-09  
Experimento: EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003  
Estado: draft_operativo_v0_1  

Objetivo:   

```
listar, ordenar y definir toda la data medible que puede ayudar a 
modelar el despertar del primer PUSH / primer impulso en tiempo real. 

No lista solo lo que ya tenemos: 

incluye lo que tenemos, 
lo que podemos capturar live, 
lo que no tenemos y 
lo que usan enfoques HF/profesionales.
```

## Regla De Lectura

Prioridad:

```text
P0 = maxima utilidad para inferir movimiento segundo a segundo
P1 = muy util para confirmar, filtrar o evitar falsos positivos
P2 = util para contexto, labels, evaluacion o riesgo
P3 = aporta, pero no debe dirigir el detector primario
```

Estado:

```text
TENEMOS = existe al menos un ejemplo local verificado
PARCIAL = existe una aproximacion, pero no el dato completo ideal
LIVE_CAPTURABLE = no hay historico auditado, pero puede capturarse live
NO_TENEMOS = no localizado / no contratado / no certificado
DERIVADO = se calcula a partir de otros datos, no es raw
A_CREAR = salida necesaria de 0003
```

```text
Features = solo datos disponibles hasta t.
Labels/outcomes = nunca features.
```

**Resumen corto:**


Para estudiar ahora: 
```
quotes/top-of-book historicas + 
scanner/worklist + 
imagenes/labels + 
state tables retrospectivas + 
halts + 
OHLCV auditoria.
```
Para live/proveedor defendible: 
```
proveedor externo T&S + 
L2/L3/NBBO + 
coverage/runtime logs + 
data quality + 
timestamp/latency metadata.
```
Para HF completo: 
```
L3/MBO + 
direct feeds + 
cross-venue latency + 
execution/fills/routes + 
fee/rebate/tick model + 
simulador de ejecucion.
```


# Catalogo Ordenado De Data
## 01. L3 / Market-By-Order / Order Lifecycle
**Prioridad**: P0  
**Estado TSIS**: NO_TENEMOS  
**Definicion**:  ciclo de vida de orden individual:
   * add,  
   * modify/replace,   
   * cancel, 
   * execute/delete, 
   * con order_id, 
   * lado, 
   * precio, 
   * size, 
   * timestamp y 
   * venue.    

**Representa**: la cola real de oferta/demanda. Permite ver si la liquidez aparece, se retira, se ejecuta o se reposiciona.  
**Ventaja para DAS**: es lo mas potente para distinguir despertar real de ruido. Un primer push limpio deberia mostrar consumo de ask, reposicionamiento de bid y demanda persistente, no solo prints aislados.  
**Asociaciones**: L2, T&S, aggressor side, queue position, spread, microprice, execution fills, latency, venue-specific feeds.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\das_l3_mbo_events.schema.md
```

## 02. L2 / Market-By-Price Depth

**Prioridad**: P0  
**Estado TSIS**: NO_TENEMOS / REQUIERE_PROVEEDOR_EXTERNO  
**Definicion**: profundidad agregada por precio y lado: niveles bid/ask con price, size, rank/level y, si viene, market maker/venue/participant.  
**Representa**: liquidez visible esperando a distintos precios. No identifica orden individual, pero si estructura de profundidad y sus cambios.  
**Ventaja para DAS**: mide depth imbalance, ask depletion, bid replenishment, microprice, presion del book y si el push atraviesa liquidez real o solo libro vacio.  
**Asociaciones**: T&S, top-of-book, L3 si existiera, subscription/runtime logs.  
**Ejemplo/path**:  

```text
Estado: REQUIERE_PROVEEDOR_EXTERNO
Dataset/canal requerido: L2/MBP o L3/MBO de proveedor externo
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\evidence\provider_samples\<provider>\<dataset>
Data family esperada: l2_mbp_or_l3_mbo
Historico auditado: NO_LOCALIZADO
```

## 03. Time And Sales / Raw Prints / Tape

**Prioridad**: P0  
**Estado TSIS**: PARCIAL historico / REQUIERE_PROVEEDOR_EXTERNO  
**Definicion**: secuencia de trades ejecutados: timestamp, price, size, exchange/venue, conditions y raw payload. Para 0003 debe venir de proveedor externo como trades/time-and-sales; DAS tms no se usara.  
**Representa**: transacciones reales. Confirma que alguien cruza liquidez y paga precio, no solo mueve quotes.  
**Ventaja para DAS**: el despertar deberia mostrar aceleracion de prints, aumento de dollar-volume, prints levantando ask, continuidad y ausencia de presion vendedora fuerte.  
**Asociaciones**: L1/L2 para aggressor side, scanner, halts/conditions, outcomes.  
**Ejemplo/path**:  

```text
Estado live: LIVE_CAPTURABLE
Dataset/canal requerido: trades/time-and-sales de proveedor externo
Path objetivo live/historico: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\evidence\provider_samples\<provider>\<dataset>
Data family esperada: trades

Estado historico: PARCIAL
Ejemplo historico: E:\TSIS\data\trades_ticks_prod_2005_2026\AACT\year=2023\month=06\day=2023-06-12\market.parquet
Limitacion: en ejemplos DAS inspeccionados, trades historicos empiezan a las 09:30 ET; no certifican premarket.
```

## 04. Aggressor Side / Buy-Sell Trade Classification

**Prioridad**: P0  
**Estado TSIS**: DERIVADO/A_CREAR  
**Definicion**: clasificacion de cada trade como comprador agresor, vendedor agresor o indeterminado. Puede venir del feed o inferirse comparando trade price contra bid/ask vigente.  
**Representa**: direccion de la presion real. Para un long DAS, pregunta si compradores estan levantando asks de forma persistente.  
**Ventaja para DAS**: volumen alto puede ser distribucion; volumen agresor comprador persistente + ask depletion + bid replenishment es senal mas limpia.  
**Asociaciones**: T&S, L1/L2, NBBO, clock sync, quote matching, spread, conditions.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\derived\trade_aggressor_side_v0_1.parquet
Input necesario: provider trades/T&S + topofbook/L2/L3 sincronizados
```

## 05. Top-Of-Book / L1 Quotes

**Prioridad**: P0  
**Estado TSIS**: TENEMOS historico  
**Definicion**: mejor bid y mejor ask visibles con size y timestamp: best_bid_price, best_bid_size, best_ask_price, best_ask_size.  
**Representa**: frontera inmediata entre oferta y demanda: mid, spread, imbalance superficial, presion de quote y velocidad de cambio del precio visible.  
**Ventaja para DAS**: es el mejor dato que ya tenemos para estudio offline sin velas. Permite mid return, best bid rise, spread compression, quote update rate y chop penalty.  
**Asociaciones**: T&S para aggressor side, L2 para profundidad, scanner para ventana, OHLCV para auditoria visual.  
**Ejemplo/path**:  

```text
Estado: TENEMOS
Ejemplo real: E:\TSIS\data\quotes_\MSS\year=2025\month=09\day=29\quotes.parquet
Ejemplo real: E:\TSIS\data\quotes\OPAD\year=2026\month=01\day=09\quotes.parquet
```

## 06. NBBO / SIP Consolidated Quote

**Prioridad**: P0/P1  
**Estado TSIS**: PARCIAL/NO_CERTIFICADO  
**Definicion**: National Best Bid and Offer consolidado entre venues. No equivale automaticamente a una quote local.  
**Representa**: mejor bid/ask nacional y spread consolidado.  
**Ventaja para DAS**: evita senales falsas por quotes aisladas; ayuda a inferir aggressor side contra la mejor oferta nacional.  
**Asociaciones**: T&S, direct exchange feeds, top-of-book local, venue book, execution/routing.  
**Ejemplo/path**:  

```text
Estado: PARCIAL
Aproximacion local: E:\TSIS\data\quotes_\MSS\year=2025\month=09\day=29\quotes.parquet
Path objetivo NBBO certificado: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\nbbo_sip_quotes.schema.md
```

## 07. Clock Sync, Capture Timestamp, Latency And Jitter

**Prioridad**: P0  
**Estado TSIS**: A_CREAR para live  
**Definicion**: source timestamp, receive/capture timestamp, parse timestamp, clock sync state, drift, latency, jitter, out-of-order y gaps.  
**Representa**: calidad temporal real del flujo. En microestructura, un evento mal ordenado puede convertir una senal buena en falsa.  
**Ventaja para DAS**: para state tables segundo a segundo, el orden de quotes/trades importa. Sin captura temporal no se sabe si el detector vio el evento antes o despues.  
**Asociaciones**: todos los feeds live, subscription logs, parser logs, runtime health, execution timestamps.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\evidence\live_capture\<capture_run_id>\capture_quality.jsonl
```

## 08. Subscription, Entitlement And Runtime State

**Prioridad**: P0  
**Estado TSIS**: A_CREAR  
**Definicion**: registro de decisiones y resultados de suscripcion: requested, started, denied, no_response, error, throttled, disconnected, reconnected, stopped.  
**Representa**: si el sistema realmente estaba mirando el simbolo. Tambien representa limites practicos de proveedor/licencia/cobertura, especialmente con L2/L3.  
**Ventaja para DAS**: evita sesgo silencioso. Un ticker sin evento puede ser no-patron o no-data.  
**Asociaciones**: scanner/worklist, T&S, Lv2, quality, denominator, runtime logs.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\evidence\live_capture\<capture_run_id>\subscriptions.jsonl
```

## 09. Scanner Trigger, Worklist And Denominator Universe

**Prioridad**: P0/P1  
**Estado TSIS**: TENEMOS  
**Definicion**: lista de candidatos y eventos de scanner: cuando aparece el ticker, a que precio, con que criterios y dentro de que universo.  
**Representa**: mecanismo de descubrimiento. No es el patron en si, pero define que simbolos entran en vigilancia.  
**Ventaja para DAS**: permite estudiar todos los candidatos, incluidos malos/no-punch. Evita elegir solo ganadores visuales y permite medir lead/lag entre scanner y awakening real.  
**Asociaciones**: quotes, T&S, Lv2, state table, labels, runtime subscriptions, outcomes.  
**Ejemplo/path**:  

```text
Estado: TENEMOS
Ejemplo real: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_full_v0_2_20260707T164416Z\anchor_worklist\anchor_worklist_from_denominator_v0_1.parquet
```

## 10. Per-Second Realtime State Table

**Prioridad**: P0  
**Estado TSIS**: A_CREAR  
**Definicion**: tabla derivada con una fila por simbolo/segundo y features calculadas solo con datos disponibles hasta ese segundo.  
**Representa**: memoria del detector. Convierte eventos irregulares de book/trades en estado modelable: dead_base, awakening, impulse, chop, liquidity, quality.  
**Ventaja para DAS**: es el objeto central de 0003. Permite entrenar, auditar y comparar modelos sin depender de PNGs ni de velas 1m.  
**Asociaciones**: T&S, Lv2, L1, scanner, labels, halts, outcomes, quality.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\outputs\das_realtime_impulse_event_state_v0_1.parquet
```

## 11. Order Flow Imbalance / OFI

**Prioridad**: P0  
**Estado TSIS**: DERIVADO/A_CREAR  
**Definicion**: desequilibrio entre oferta y demanda a partir de eventos del libro: cambios en best bid/ask price y size, market orders y cancelaciones.  
**Representa**: presion neta de compra/venta a corto plazo.  
**Ventaja para DAS**: debe ser feature central del despertar. Si OFI positivo persiste mientras mid y best bid suben, hay mayor probabilidad de push real.  
**Asociaciones**: L1, L2, L3, T&S, spread, depth, volatility, microprice.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\derived\order_flow_imbalance_1s_v0_1.parquet
Input minimo actual: E:\TSIS\data\quotes_\MSS\year=2025\month=09\day=29\quotes.parquet
```

## 12. Microprice / Depth Weighted Mid

**Prioridad**: P0/P1  
**Estado TSIS**: DERIVADO/A_CREAR  
**Definicion**: precio teorico que pondera bid/ask por tamanos relativos o profundidad. A diferencia del mid simple, incorpora presion de cola.  
**Representa**: hacia donde empuja el libro visible si las colas actuales se consumen de forma asimetrica.  
**Ventaja para DAS**: si microprice lidera al mid antes del punch, puede anticipar awakening. Con Lv2 es mas robusto; con L1 es aproximado.  
**Asociaciones**: L1, L2, spread, OFI, trade aggressor side.  
**Ejemplo/path**:  

```text
Estado: A_CREAR
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\derived\microprice_1s_v0_1.parquet
Input minimo: quotes L1 historicas
```

## 13. Quote Update Rate And Quote Velocity

**Prioridad**: P1  
**Estado TSIS**: DERIVADO posible con quotes historicas  
**Definicion**: numero de actualizaciones de quote por segundo, cambios direccionales de best bid/ask, frecuencia de spread changes y velocidad de subida/bajada del top-of-book.  
**Representa**: actividad del libro antes de que una vela se vea grande. Un ticker muerto que despierta suele pasar de pocos updates a muchos updates con direccion.  
**Ventaja para DAS**: detecta transicion dead -> awakening. Penaliza casos erraticos donde hay muchos updates pero sin avance neto.  
**Asociaciones**: L1, L2, OFI, spread, scanner trigger, chop penalty.  
**Ejemplo/path**:  

```text
Estado: DERIVADO posible
Input real: E:\TSIS\data\quotes_\MSS\year=2025\month=09\day=29\quotes.parquet
Output objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\derived\quote_velocity_1s_v0_1.parquet
```

## 14. Spread, Spread Stability And Spread Risk

**Prioridad**: P1  
**Estado TSIS**: DERIVADO posible con quotes historicas  
**Definicion**: diferencia entre ask y bid, en absoluto y bps, mas su estabilidad temporal.  
**Representa**: tradeability y calidad de precio. Un push con spread explosivo puede no ser operable aunque el chart parezca fuerte.  
**Ventaja para DAS**: filtra falsos despertares en tickers iliquidos. Ayuda a distinguir movimiento limpio de saltos por libro vacio.  
**Asociaciones**: L1, L2, T&S, slippage, execution fills, risk sizing.  
**Ejemplo/path**:  

```text
Estado: DERIVADO posible
Input real: E:\TSIS\data\quotes\OPAD\year=2026\month=01\day=09\quotes.parquet
```

## 15. Auction Imbalance / Opening Imbalance / NOII

**Prioridad**: P1  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: indicadores de desequilibrio de ordenes en subastas de apertura/cierre: paired shares, imbalance side, imbalance shares, indicative price, reference price.  
**Representa**: presion acumulada en subasta, especialmente cerca de la apertura regular.  
**Ventaja para DAS**: puede explicar si el premarket push tiene soporte hacia open o si es aislado. Ayuda a estudiar continuidad/destruccion.  
**Asociaciones**: T&S, L2, regular open, VWAP, outcomes.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\opening_imbalance_noii.schema.md
```

## 16. Venue-Specific Direct Feeds And Cross-Venue Lead/Lag

**Prioridad**: P1 para HF, P2 para TSIS v0  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: feeds directos por exchange/venue con quotes, trades y order book, separados del consolidado.  
**Representa**: donde nace primero el movimiento y como se propaga entre venues. En HF esto es critico para arbitraje/latencia.  
**Ventaja para DAS**: ayuda a saber si un awakening aparece primero en una venue, si el SIP llega tarde, o si el movimiento es fragmentado.  
**Asociaciones**: NBBO, L2/L3, routing, latency, execution fills.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\venue_direct_feeds.schema.md
```

## 17. Halts, LULD, Trading Pauses And Resumption State

**Prioridad**: P1  
**Estado TSIS**: TENEMOS  
**Definicion**: eventos de interrupcion o pausa: regulatory halts, LULD pauses, volatility halts, resumption times y motivos.  
**Representa**: disponibilidad real de trading. Un movimiento puede ser deformado por halt/resume o por riesgo inminente de pausa.  
**Ventaja para DAS**: evita interpretar gaps de trading como falta de impulso o como impulso. Tambien ayuda a clasificar destrucciones/post-halt patterns.  
**Asociaciones**: T&S gaps, quotes gaps, scanner state, risk, outcomes.  
**Ejemplo/path**:  

```text
Estado: TENEMOS
Ejemplo real: E:\TSIS\data\Halts\processed\halts_master_multisource.parquet
Contrato: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\halts\halts_master_multisource_schema_contract.md
```

## 18. Execution, Orders, Fills And Routing

**Prioridad**: P1 para operabilidad, P2 para estudio del patron  
**Estado TSIS**: NO_TENEMOS para 0003  
**Definicion**: ordenes enviadas, ack/reject, route, price, size, fill, partial fill, cancel, replace, fees/rebates, slippage y timestamps.  
**Representa**: diferencia entre senal teorica y trade real.  
**Ventaja para DAS**: el primer impulso puede ser real pero no ejecutable por spread/slippage. Fills permiten saber si la edge sobrevive.  
**Asociaciones**: T&S, L2, spread, route, latency, risk engine, broker state.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\execution_orders_fills.schema.md
```

## 19. Fee/Rebate, Tick Size And Venue Rule State

**Prioridad**: P1/P2  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: costes de ejecucion, maker/taker fees, rebates, tick size, lot constraints y reglas de venue.  
**Representa**: coste real y restricciones del micro-mercado.  
**Ventaja para DAS**: movimiento pequeno con spread/fees altos puede no tener edge. Ayuda a decidir si una entrada impulse es operable o solo visual.  
**Asociaciones**: execution fills, venue, NBBO, spread, slippage, sizing.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\venue_fee_tick_rules.schema.md
```

## 20. OHLCV Intraday 1m

**Prioridad**: P2  
**Estado TSIS**: TENEMOS  
**Definicion**: barras agregadas por minuto: open, high, low, close, volume.  
**Representa**: vista comprimida del comportamiento intradia.  
**Ventaja para DAS**: no debe ser senal primaria de 0003, pero ayuda a revisar casos, crear charts, alinear eventos y comparar si el detector quote-driven anticipa la vela.  
**Asociaciones**: quotes, state tables, images, EMA/VWAP, first_push_high labels.  
**Ejemplo/path**:  

```text
Estado: TENEMOS
Ejemplo real: E:\TSIS\data\ohlcv_1m\_staging_flatfiles_1m\ticker=BNCN\year=2005\month=3\0ee3be9e818a49a2911471d47547fbc7-0.parquet
Quote-guarded manifest: E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

## 21. VWAP, EMA, Donchian, Wilder Bands And Derived Visual Indicators

**Prioridad**: P2  
**Estado TSIS**: DERIVADO/PARCIAL  
**Definicion**: indicadores calculados a partir de bars o event streams: VWAP, EMA8, Wilder8, Donchian high/low, distance to moving averages.  
**Representa**: resumen visual/agregado del estado del precio. No mide por si solo la causa microestructural.  
**Ventaja para DAS**: sirve para interpretar patron humano: precio sobre EMA8, primer dip a EMA8, break de rango. En 0003 debe ser feature secundaria o label-audit.  
**Asociaciones**: OHLCV, quotes, first dip labels, images.  
**Ejemplo/path**:  

```text
Estado: PARCIAL/DERIVADO
Ejemplo visual: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_VISUAL_CASEBOOK\img\human_notes_cases\0004_MSS_2025-09-29_push464.70_rebreak_03_event_day_premarket_detail.png
```

## 22. Human Labels From Images / Manual Pattern Labels

**Prioridad**: P2 pero imprescindible para aprendizaje supervisado  
**Estado TSIS**: PARCIAL  
**Definicion**: etiquetas humanas: valid_das_impulse, bad_chop, no_punch, first_push_start, first_push_high, first_dip_low, rebreak, confidence y notas.  
**Representa**: criterio humano que queremos formalizar. No es dato de mercado, es target/label.  
**Ventaja para DAS**: permite entrenar clasificador/ranker que discrimine patron limpio contra basura choppy sin eliminar malos del denominador.  
**Asociaciones**: images, state tables, quote features, T&S/L2 features, outcomes.  
**Ejemplo/path**:  

```text
Estado: PARCIAL
Ejemplo real: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\DAS_VISUAL_CASEBOOK\img\human_notes_cases\0004_MSS_2025-09-29_push464.70_rebreak_03_event_day_premarket_detail.png
Path objetivo labels estructurados: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\labels\das_impulse_human_labels_v0_1.parquet
```

## 23. Existing DAS Candidate State Table

**Prioridad**: P2  
**Estado TSIS**: TENEMOS  
**Definicion**: tabla retrospectiva con columnas de scanner, premarket, frontside, DAS, EMA/VWAP, quality, labels y outcomes.  
**Representa**: mapa historico del detector anterior y anchors visuales ya calculados. No es raw market data.  
**Ventaja para DAS**: sirve como source de labels retrospectivos y disciplina de nombres. No debe usarse como feature live si contiene futuro.  
**Asociaciones**: images, OHLCV, quotes, worklist, labels, outcomes.  
**Ejemplo/path**:  

```text
Estado: TENEMOS
Ejemplo real: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\state_tables\das_candidate_state_table_experimental_v0_1.parquet
Resumen: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\state_tables\das_candidate_state_table_experimental_v0_1_summary.md
```

## 24. Forward Outcomes / MFE / MAE / Failure State

**Prioridad**: P2  
**Estado TSIS**: PARCIAL/DERIVADO  
**Definicion**: resultados posteriores al evento: maximum favorable excursion, maximum adverse excursion, time-to-fail, rebreak, destruction, continuation.  
**Representa**: utilidad ex-post del evento. No es informacion disponible en el momento de decision.  
**Ventaja para DAS**: mide si detectar `DAS_IMPULSE_START_CONFIRMED` tiene valor. Tambien ayuda a separar impulso bueno de impulso que muere rapido.  
**Asociaciones**: event state, labels, OHLCV/quotes forward windows, execution si existe.  
**Ejemplo/path**:  

```text
Estado: PARCIAL
Ejemplo real con columnas outcome__: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\state_tables\das_candidate_state_table_experimental_v0_1.parquet
Regla: outcome__* nunca es feature.
```

## 25. Prior Close, Daily Reference, Gap And Daily Context

**Prioridad**: P2  
**Estado TSIS**: PARCIAL/TENEMOS en state tables y OHLCV  
**Definicion**: cierre anterior, open premarket, gap %, daily range, prior day volume, ATR/volatility diaria.  
**Representa**: contexto de escala. Un +20% en un ticker de $0.30 no es igual que en $20; prior close define denominadores.  
**Ventaja para DAS**: normaliza movimiento y ayuda a detectar acciones que despiertan desde base muerta. Evita errores por split o close incorrecto.  
**Asociaciones**: scanner, OHLCV daily/intraday, reference data, corporate actions.  
**Ejemplo/path**:  

```text
Estado: PARCIAL
Ejemplo con daily__/scanner__: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\state_tables\das_candidate_state_table_experimental_v0_1.parquet
```

## 26. Corporate Actions, Splits And Ticker Identity

**Prioridad**: P2  
**Estado TSIS**: PARCIAL/TENEMOS referencia general  
**Definicion**: splits, reverse splits, symbol changes, listing status, active/inactive state, exchange e instrument identity.  
**Representa**: continuidad correcta del activo. En small caps, splits y cambios de ticker pueden contaminar % moves y prior close.  
**Ventaja para DAS**: evita falsos push por ajuste mal aplicado. Necesario para as-of correctness.  
**Asociaciones**: prior close, OHLCV, scanner, reference snapshots, corporate actions.  
**Ejemplo/path**:  

```text
Estado: PARCIAL
Ejemplo real: E:\TSIS\data\reference\all_tickers\snapshot_date=2005-01-02.parquet
```

## 27. Float, Shares Outstanding, Market Cap And Dilution Structure

**Prioridad**: P2  
**Estado TSIS**: NO_TENEMOS/PARCIAL no verificado para 0003  
**Definicion**: float, shares outstanding, market cap, free float, warrants, offerings, ATM programs, dilution risk.  
**Representa**: capacidad del ticker para moverse y sostener squeeze/impulse. Small float + catalyst + flow puede amplificar movimiento.  
**Ventaja para DAS**: no detecta el primer segundo del push, pero ayuda a explicar por que unos impulses siguen y otros mueren.  
**Asociaciones**: news, SEC filings, prior close, volume, borrow/short interest, outcomes.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS como contrato 0003 certificado
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\float_share_structure_asof.schema.md
```

## 28. News, Press Releases, SEC Filings And Catalyst Stream

**Prioridad**: P2  
**Estado TSIS**: NO_TENEMOS en contrato 0003  
**Definicion**: eventos textuales timestamped: headlines, press releases, SEC filings, FDA/contract/news catalysts, sentiment y tags.  
**Representa**: causa informativa potencial del despertar. Muchos DAS moves small-cap nacen por catalyst.  
**Ventaja para DAS**: mejora discriminacion entre punch real por informacion y random chop. Ayuda a priorizar suscripciones Lv2/TMS cuando hay limite.  
**Asociaciones**: scanner trigger, social attention, volume acceleration, outcomes, float.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\news_catalyst_events_asof.schema.md
```

## 29. Social Attention, Retail Flow Proxies And Search Interest

**Prioridad**: P2/P3  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: menciones en redes/chats, watchlist retail, Google Trends, Reddit/StockTwits/X, broker popularity si disponible.  
**Representa**: atencion y crowding. En small caps, atencion retail puede amplificar el primer impulso.  
**Ventaja para DAS**: no debe disparar entradas por si solo, pero puede explicar continuidad o fallos por crowded/chase behavior.  
**Asociaciones**: news, scanner, volume, outcomes, float.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\social_attention_asof.schema.md
```

## 30. Short Interest, Borrow, Locate, SSR And Fails-To-Deliver

**Prioridad**: P2  
**Estado TSIS**: NO_TENEMOS/PARCIAL no verificado  
**Definicion**: short interest, borrow availability, borrow cost, locate state, short sale restriction, fails-to-deliver.  
**Representa**: potencial de squeeze y restricciones de venta corta.  
**Ventaja para DAS**: ayuda a explicar pushes violentos y destrucciones posteriores. Tambien afecta operabilidad si la estrategia necesita short/hedge.  
**Asociaciones**: float, news, volume, SSR, outcomes.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS como contrato 0003
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\short_borrow_ssr_asof.schema.md
```

## 31. Options Chain, Options Flow And Implied Volatility

**Prioridad**: P2/P3 para small-cap DAS  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: cadena de opciones, greeks, IV, volume/open interest, unusual options flow, put/call imbalance.  
**Representa**: derivados y posicionamiento. En algunos tickers, options activity puede liderar o confirmar movimiento.  
**Ventaja para DAS**: aporta cuando el ticker tiene opciones liquidas. En muchos micro/small caps puede ser irrelevante.  
**Asociaciones**: underlying T&S/L2, news, float, market regime.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\options_flow_asof.schema.md
```

## 32. ETF, Index, Futures And Market Regime

**Prioridad**: P2/P3  
**Estado TSIS**: NO_TENEMOS como contrato 0003  
**Definicion**: SPY/QQQ/IWM, sector ETF, futures, VIX/vol regime, market breadth y macro/open regime.  
**Representa**: viento de mercado. No causa normalmente un microcap DAS awakening, pero puede afectar follow-through y riesgo.  
**Ventaja para DAS**: filtra entornos donde los impulses tienden a fallar o donde el mercado entero favorece momentum.  
**Asociaciones**: outcomes, sizing, risk, sector/news.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS como contrato 0003
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\market_regime_asof.schema.md
```

## 33. Broker Account State, Buying Power And Risk Limits

**Prioridad**: P2 para operabilidad  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: buying power, margin, max position, daily loss, symbol restrictions, PDT/risk limits y order size caps.  
**Representa**: capacidad real de actuar sobre la senal.  
**Ventaja para DAS**: no ayuda a detectar el patron, pero evita disenar una entrada que no puede ejecutarse o que viola riesgo.  
**Asociaciones**: execution, sizing, slippage, risk engine.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\broker_risk_state.schema.md
```

## 34. Infrastructure Telemetry

**Prioridad**: P2/P3  
**Estado TSIS**: NO_TENEMOS para 0003  
**Definicion**: CPU, memory, queue sizes, event lag, socket lag, disk write latency, parser backlog y dropped messages.  
**Representa**: salud tecnica del sistema. En live, una mala senal puede ser simplemente lag.  
**Ventaja para DAS**: permite excluir o degradar periodos donde el detector no tenia capacidad de ver correctamente el mercado.  
**Asociaciones**: capture quality, runtime state, live events, clock sync.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\evidence\live_capture\<capture_run_id>\infra_telemetry.jsonl
```

## 35. Data Quality, Lineage And Policy Contracts

**Prioridad**: P2  
**Estado TSIS**: TENEMOS parcialmente  
**Definicion**: contratos, policies, manifests, schema versions, row quality, source lineage y validation reports.  
**Representa**: confianza en la data. Sin esto no se puede comparar runs ni reproducir resultados.  
**Ventaja para DAS**: permite saber si un caso fallido es fallo de patron, fallo de data o cambio de contrato.  
**Asociaciones**: todos los datasets, outputs, labels, state tables.  
**Ejemplo/path**:  

```text
Estado: TENEMOS parcialmente
Ejemplo state manifest: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS\03_STRATEGY_LIBRARY\LONG\DAS\runs\das_scanner_appearance_20260628T114046Z\state_tables\das_candidate_state_table_experimental_v0_1_manifest.json
Ejemplo policy: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\quotes_consumption_policy.md
```

## 36. Synthetic LOB Replay / Market Simulator

**Prioridad**: P3 ahora, P1 para ejecucion futura  
**Estado TSIS**: NO_TENEMOS  
**Definicion**: simulador de libro que reproduce dinamica de LOB a partir de historico o agentes. Puede usarse para stress tests y RL.  
**Representa**: entorno controlado para probar decision/execution. No reemplaza historico, pero permite evaluar politicas bajo escenarios.  
**Ventaja para DAS**: despues de validar el evento, seria util para probar entradas impulse/dip/rebreak y slippage bajo incertidumbre.  
**Asociaciones**: L2/L3, T&S, fills, latency, risk, RL/execution.  
**Ejemplo/path**:  

```text
Estado: NO_TENEMOS
Path objetivo: C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FIRST_IMPULSE_REALTIME_DETECTION_0003\data_contracts\expected\lob_simulator_config.schema.md
```

---

# Minimo Para Estudio Offline Vs Minimo Para Live

## Para Estudiarlo Ahora

Suficiente para empezar:

```text
quotes historicas L1/top-of-book
scanner/worklist/denominator
state tables retrospectivas como labels/contexto
imagenes anotadas
halts
OHLCV 1m como auditoria visual
```

Salida minima de estudio:

```text
das_realtime_impulse_event_state_v0_1.parquet
```

Features as-of por segundo:

```text
mid_return_5s_15s_30s_60s
best_bid_rise_rate
best_ask_rise_rate
spread_bps
spread_stability
bid_ask_size_imbalance
quote_update_rate
quote_direction_flip_rate
dead_base_score
awakening_score
impulse_score
chop_penalty
spread_risk_penalty
quality_state
```

## Para Live Defendible

Falta capturar:

```text
provider trades/T&S raw feed
provider L2/MBP or L3/MBO raw feed
subscriptions.jsonl
capture_quality.jsonl
runtime/infra telemetry
clock sync metadata
parser schemas y raw payloads
```

## Para HF/Profesional Completo

Faltaria:

```text
L3/MBO
full direct venue feeds
certified NBBO/SIP history
cross-venue lead-lag and latency
execution/fill/routing data
fee/rebate/tick model
queue-position model
market simulator / transaction cost simulator
```

---

# Respuesta Anterior Clonada, Mejorada Y Actualizada

Para solo estudiar el patron, si: TSIS tiene suficiente para empezar bien.

No hace falta proveedor live T&S/L2/L3 para estudiar el patron offline inicial. Eso hace falta para convertirlo despues en un sistema real-time fuerte. Para investigacion, lo minimo viable ya existe:

```text
1. quotes/top-of-book historicas en 150/152 casos del denominador 0002
2. datos desde aproximadamente 04:00 ET, suficientes para estudiar casi todo el premarket DAS disponible
3. OHLCV 1m para auditoria visual y comparacion, no como senal primaria
4. imagenes buenas/malas para labels humanos
5. tabla de estado antigua con anchors retrospectivos: first_push_start, first_push_high, first_dip_low, rebreak
6. casos choppy/no-punch como OPAD/AMOD para aprender que NO queremos
7. halts/reference data para evitar errores de interpretacion
```

Con eso podemos hacer un estudio serio:

```text
quote replay historico
-> construir state table segundo a segundo
-> calcular features solo con datos hasta t
-> detectar dead_base / awakening / impulse_candidate
-> comparar contra labels humanos
-> clasificar valid_das_impulse vs bad_chop/no_punch/too_slow/no_data
```

Lo que falta para estudiarlo mejor:

```text
1. convertir imagenes anotadas en labels estructurados
2. tener negativos explicitos, no solo casos bonitos
3. definir exactamente DAS_IMPULSE_START_CONFIRMED
4. crear das_realtime_impulse_event_state_v0_1.parquet
5. poner quality flags: quotes missing, late start, gaps, broken spread, halt, no_data
6. no usar first_push_high como feature; solo como label/outcome retrospectivo
7. guardar todos los candidatos, aunque sean malos, para no sesgar el estudio
```

Frase correcta:

```text
Para estudiar el patron: si tenemos data suficiente.
Para demostrar un sistema real-time operable/profesional: falta contratar/capturar proveedor externo T&S/L2/L3/NBBO.
Para competir a nivel HF completo: faltaria L3/MBO, direct feeds, latencia, routing y ejecucion.
```

El siguiente paso logico no es profit ni puntitos visuales. Es construir el estudio offline con quotes, labels y negativos, y demostrar si podemos separar patron DAS limpio de basura choppy antes de pensar en entrada, stop o sizing.

---

# Referencias Profesionales Y Cientificas

## Order Flow Imbalance Y Price Impact

- Rama Cont, Arseniy Kukanov, Sasha Stoikov, "The Price Impact of Order Book Events".
  URL: https://arxiv.org/abs/1011.6402
  Uso para TSIS: justifica que en horizontes cortos el order flow imbalance en best bid/ask es mas informativo que volumen agregado.

## Deep Learning Sobre Limit Order Book

- Zihao Zhang, Stefan Zohren, Stephen Roberts, "DeepLOB: Deep Convolutional Neural Networks for Limit Order Books".
  URL: https://arxiv.org/abs/1808.03668
  Uso para TSIS: evidencia que modelos modernos de prediccion de movimiento usan estructura del libro de ordenes, no velas 1m como input principal.

## Queue-Reactive Model Y Simulacion De Libro

- Weibing Huang, Charles-Albert Lehalle, Mathieu Rosenbaum, "Simulating and analyzing order book data: The queue-reactive model".
  URL: https://arxiv.org/abs/1312.0563
  Uso para TSIS: modelar intensidades del flujo de ordenes condicionadas al estado actual del libro y usarlo para simulacion/TCA.

## LOB Simulators Y Reinforcement Learning

- Sascha Frey et al., "JAX-LOB: A GPU-Accelerated limit order book simulator to unlock large scale reinforcement learning for trading".
  URL: https://arxiv.org/abs/2308.13289
  Uso para TSIS: referencia para futuros simuladores LOB y entrenamiento de politicas de ejecucion cuando ya tengamos evento validado.

## Algorithmic Trading Y Liquidez

- Terrence Hendershott, Charles Jones, Albert Menkveld, "Does Algorithmic Trading Improve Liquidity?".
  URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1100635
  Uso para TSIS: evidencia empirica de que trading algoritmico y quotes informatizados afectan liquidez, spreads e informacion de quotes.

## HFT, Latencia Y Diseno De Mercado

- Eric Budish, Peter Cramton, John Shim, "The High-Frequency Trading Arms Race: Frequent Batch Auctions as a Market Design Response".
  URL: https://academic.oup.com/qje/article/130/4/1547/1916146
  Uso para TSIS: explica que en HF la ventaja no es solo la senal, sino velocidad, estructura de mercado y latencia.

## Riesgo Regulatorio: Momentum Ignition, Spoofing, Layering

- FINRA, "Algorithmic Trading".
  URL: https://www.finra.org/rules-guidance/key-topics/algorithmic-trading
  Uso para TSIS: separa deteccion pasiva legitima de impulso de practicas manipulativas; 0003 debe detectar, no inducir movimiento.

---

# Decision Del Documento

0003 debe construir primero una state table de investigacion offline basada en quotes historicas. En paralelo debe preparar el contrato de proveedor externo T&S/L2/L3/NBBO, porque ese sera el minimo para convertir el estudio en detector real-time defendible.

Prioridad inmediata:

```text
1. estructurar labels humanos buenos/malos
2. construir features quote-driven segundo a segundo
3. crear das_realtime_impulse_event_state_v0_1.parquet
4. evaluar discriminacion valid_das_impulse vs bad_chop/no_punch
5. definir contrato de proveedor externo T&S/L2/L3/NBBO para futuras capturas/compras
```




