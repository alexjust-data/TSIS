# Data Foundation Outputs Target Contract v0.1

## Estado

Tipo: module contract.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status: `provisional_design_contract`.

Este documento no materializa tablas. Define que outputs deben existir, para que
sirven, de donde debe salir su informacion, como trabajan cuando aparece un
evento y que no deben contener.

La matriz de estado real de estas tablas vive en:

```text
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
```

Lectura obligatoria:

```text
target_contract = que debe existir y por que
status_matrix   = que existe hoy, que esta validado y que sigue bloqueado
```

## Graphify Context Consultado

Este contrato fue preparado despues de consultar tres contextos Graphify del
proyecto:

```text
C:/TSIS_Data/00_CTO/graphify-out/graph.json
C:/TSIS_Data/00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/graphify-out/graph.json
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/graphify-out/_graphify_staging_foundations_authority_20260620/graphify-out/graph.json
```

Lectura usada:

- `00_CTO` fija la arquitectura de laboratorio y la separacion entre datos,
  eventos, outcomes, estrategias, ML, decision y ejecucion.
- `10_DATA_QUALITY_HARNESS` refuerza que todo dataset consumible debe tener
  evidence assets, validator contract, registry entry, visual reading protocol y
  final acceptance criteria.
- `foundations_authority` enlaza dataset contracts, data audit standard,
  completion standard, inspection dossiers, validators, registries y consumption
  policies.

Limitacion conocida:

```text
foundations_authority_20260620 existe y es consultable, pero tiene remediation
Graphify pendiente para chunks 13-16. Por tanto se usa como mapa de orientacion,
no como unica autoridad final.
```

La autoridad final de este contrato debe seguir siendo:

```text
contrato + certificacion + evidencia + profiling fisico + validator
```

## Principio Central

Las tablas objetivo de Data Foundation no son otra copia de toda la raw data.

Son una capa canonicamente organizada para que las capas posteriores puedan
preguntar:

```text
que instrumento era?
que sesion era?
que precio/view corresponde?
que corporate actions aplican?
que contexto diario existia?
que paso intradia?
que microestructura habia?
que calidad tiene este dato?
puedo usar este caso para backtest, ML, ejecucion o solo forense?
```

La informacion completa se conserva en las fuentes raw/auditadas. Las tablas
maestras deben guardar lo necesario para operar y enlazar el resto mediante
keys estables.

## Relacion Con La Data De Mercado Descargada

Si: estas tablas deben venir de la data real descargada del mercado.

No: estas tablas no deben copiar toda la raw data de mercado dentro de una tabla
gigante.

La regla es:

```text
raw market data descargada
-> auditoria/calidad
-> componentes derivados de estado
-> market_state / event_state
-> modelos, decisiones, backtests y evaluadores
```

La raw data descargada sigue siendo la verdad fisica completa:

```text
quotes
trades
daily
1m
halts
reference
short / short_review
financial
news / filings / alerts
```

Los outputs de Data Foundation deben extraer o normalizar de esa raw data solo
lo necesario para reconstruir estado de forma eficiente, auditable y sin
leakage.

Ejemplo:

```text
quotes raw completos
-> spread_median, spread_p95, locked_crossed_ratio, quote_update_rate,
   nbbo_staleness, depth_proxy, liquidity_thinning_score
```

```text
trades raw completos
-> trade_count, trade_intensity, dollar_volume, odd_lot_ratio,
   aggressive_flow_proxy, price_impact_proxy, duplicate_trade_ratio
```

Cuando un consumidor necesite inspeccion profunda, replay o recomputacion, debe
volver al raw/auditado mediante keys, source paths, hashes y manifests.

Regla:

```text
El estado debe estar basado en la data de mercado real descargada.
El estado no debe ser una copia indiscriminada de toda la raw data.
```

## Justificacion Cientifica De Esta Arquitectura

Esta decision no es solo preferencia de ingenieria.

La literatura relevante apunta a una misma conclusion:

```text
los modelos de decision aprenden sobre estados estructurados;
los estados deben venir de datos reales;
la raw data debe conservarse como verdad recomputable;
la tabla de entrenamiento debe ser legal en el tiempo, auditada y evaluable.
```

### 1. Offline RL Convierte Datasets En Decision Engines, Pero Solo Si El Dataset Esta Bien Definido

Levine, Kumar, Tucker y Fu describen Offline RL como aprendizaje de politicas
desde datos previamente recogidos, sin nueva interaccion online, y senalan que
la promesa es convertir grandes datasets en motores de decision.

Referencia:

```text
Levine et al. (2020)
Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems
https://arxiv.org/abs/2005.01643
```

Implicacion TSIS:

```text
No basta tener raw data.
Hay que construir datasets de estado/accion/reward con semantica estable.
```

### 2. Offline RL Falla Con Distribution Shift Si El Dataset No Cubre El Estado/Accion

Kumar, Zhou, Tucker y Levine muestran que los metodos off-policy pueden fallar
en Offline RL por sobreestimacion inducida por distribution shift entre el
dataset y la politica aprendida.

Referencia:

```text
Kumar et al. (2020)
Conservative Q-Learning for Offline Reinforcement Learning
https://arxiv.org/abs/2006.04779
```

Implicacion TSIS:

```text
Antes de entrenar RL hay que declarar cobertura, calidad, ventanas, acciones,
labels/rewards y out-of-distribution guards.
```

### 3. La Microestructura No Se Modela Bien Como OHLCV Plano

DeepLOB modela limit order books capturando estructura espacial del libro con
convoluciones y dependencias temporales con LSTM, usando LOB data real de cash
equities.

Referencia:

```text
Zhang, Zohren, Roberts (2018/2020)
DeepLOB: Deep Convolutional Neural Networks for Limit Order Books
https://arxiv.org/abs/1808.03668
```

Implicacion TSIS:

```text
quotes/trades deben transformarse en representaciones microestructurales,
ventanas, secuencias o embeddings, no simplemente pegarse a una tabla plana.
```

### 4. Alta Accuracy En LOB No Implica Senal Operable

LOBFrame muestra que las caracteristicas microestructurales de las acciones
afectan la eficacia de deep learning y que alta capacidad predictiva no equivale
necesariamente a trading accionable. Tambien argumenta que metricas ML
tradicionales pueden no evaluar bien forecasts de LOB.

Referencia:

```text
Briola, Bartolucci, Aste (2024)
Deep Limit Order Book Forecasting
https://arxiv.org/abs/2403.09267
```

Implicacion TSIS:

```text
Por eso separamos prediccion, decision, ejecucion, costes, calidad y outcomes.
```

### 5. RL De Ejecucion Sobre LOB Requiere Simulacion Y Estado Escalable

JAX-LOB se disena para procesar miles de libros en paralelo y se integra con
paquetes JAX para abordar un problema de optimal execution con RL.

Referencia:

```text
Frey et al. (2023)
JAX-LOB: A GPU-Accelerated limit order book simulator to unlock large scale
reinforcement learning for trading
https://arxiv.org/abs/2308.13289
```

Implicacion TSIS:

```text
Si queremos RL/execution realista, necesitamos estados microestructurales
recomputables y simulables, no solo snapshots sin lineage.
```

### 6. AlphaEvolve/FunSearch Demuestran Que La Busqueda Requiere Evaluadores Bloqueados

AlphaEvolve mejora algoritmos mediante una tuberia evolutiva que recibe feedback
continuo de evaluadores. FunSearch combina LLMs y procedimientos evolutivos para
descubrimiento programatico.

Referencias:

```text
Novikov et al. (2025)
AlphaEvolve: A coding agent for scientific and algorithmic discovery
https://arxiv.org/abs/2506.13131

Romera-Paredes et al. (2024)
Mathematical discoveries from program search with large language models
https://www.nature.com/articles/s41586-023-06924-6
```

Implicacion TSIS:

```text
Antes de permitir busqueda evolutiva sobre eventos, features o policies,
debemos bloquear datasets, estados, evaluadores, fitness y leakage gates.
```

### 7. Causal ML Justifica No Entrenar Solo Sobre Proxies Bonitos

Scholkopf argumenta que problemas duros de ML e IA estan relacionados con
causalidad.

Referencia:

```text
Scholkopf (2019/2022)
Causality for Machine Learning
https://arxiv.org/abs/1911.10500
```

Implicacion TSIS:

```text
El estado debe intentar representar mecanismos: attention, liquidity stress,
inventory stress, catalyst, regime, halts, short pressure y execution context,
no solo indicadores visuales correlacionados.
```

### 8. Matriz Decision-Evidencia Para Agentes

Ningun paper externo demuestra "TSIS" como arquitectura exacta.

Lo que si existe es evidencia directa de cada obligacion tecnica que este
contrato impone. Por tanto, un agente no debe leer esta seccion como
bibliografia decorativa, sino como justificacion de diseno.

| Decision TSIS | Evidencia directa | Obligacion tecnica |
| --- | --- | --- |
| Modelar eventos como estados, no como velas sueltas. | Kaelbling, Littman y Moore (1996) describen RL como decision secuencial fundada en Markov decision theory, delayed reinforcement y hidden state: https://arxiv.org/abs/cs/9605103 | Las tablas deben poder componer `state -> action -> reward/outcome`, no solo describir precio historico. |
| Usar datasets historicos gobernados para decision engines. | Levine et al. (2020) definen Offline RL como uso de datos previamente recogidos para aprender politicas sin nueva interaccion online: https://arxiv.org/abs/2005.01643 | Cada tabla entrenable debe declarar cobertura, periodo, lineage, cutoffs y limitaciones. |
| No entrenar RL sobre cobertura pobre o no declarada. | Kumar et al. (2020) muestran fallo por distribution shift entre dataset y politica aprendida: https://arxiv.org/abs/2006.04779 | Todo output debe exponer universe scope, full-universe claim, OOD risk y promotion status. |
| No reducir microestructura a OHLCV plano. | DeepLOB usa estructura espacial del LOB y dependencias temporales para cash equities: https://arxiv.org/abs/1808.03668 | quotes/trades deben derivar features/secuencias microestructurales con ventana, reloj y contexto. |
| Evaluar si una prediccion LOB es operable, no solo accurate. | LOBFrame muestra que alta forecasting power en LOB no implica senal accionable y propone evaluacion operacional: https://arxiv.org/abs/2403.09267 | Separar features, labels, outcomes, costes, ejecucion y evaluadores. |
| Preparar simulacion/replay para ejecucion y RL. | ABIDES modela mercados con agentes, exchange, latencias y protocolos tipo NASDAQ ITCH/OUCH; JAX-LOB escala simulacion LOB para RL: https://arxiv.org/abs/1904.12066 y https://arxiv.org/abs/2308.13289 | Las tablas no sustituyen al raw; deben permitir replay, simulacion y recomputacion desde raw. |
| Bloquear evaluadores antes de busqueda evolutiva. | FunSearch y AlphaEvolve dependen de evaluadores sistematicos para puntuar programas y evitar confabulacion: https://www.nature.com/articles/s41586-023-06924-6 y https://arxiv.org/abs/2506.13131 | Antes de AlphaEvolve financiero deben estar fijos datasets, validators, fitness, leakage gates y archive schema. |
| Preferir mecanismos sobre correlaciones fragiles. | Scholkopf (2019/2022) conecta los problemas duros de ML con causalidad: https://arxiv.org/abs/1911.10500 | `market_state` debe representar mecanismos plausibles: attention, catalyst, liquidity stress, inventory stress, regime, short pressure y execution context. |

## Regla Para Agentes Nuevos: Tablas Como Componentes De Estado

Estas tablas son `state_components`.

No son, por separado, el `market_state` institucional final.

Interpretacion obligatoria:

```text
raw/audited data
-> Data Foundation state components
-> market_state / event_state reconstruction
-> event_table
-> outcome / strategy / ML / execution / RL
```

Por tanto:

- una tabla puede estar bien materializada y seguir siendo solo un componente;
- ningun consumidor debe llamarla `market_state` si no compone reloj causal,
  lineage, quality gates, leakage boundaries y schema de estado;
- los outputs de Data Foundation deben facilitar reconstruccion de estado, no
  mezclar eventos, outcomes, estrategias, acciones o rewards;
- todo builder nuevo debe declarar si produce `state_component`,
  `event_state_candidate` o `institutional_market_state`.

## Lectura Rapida: Que Data Lleva Cada Tabla

Esta seccion existe para agentes nuevos sin contexto previo.

Cada tabla lleva una parte distinta del futuro `market_state` / `event_state`.

| Tabla | Que data lleva | Para que sirve en un evento |
|---|---|---|
| `instrument_master` | Identidad temporal del instrumento: `instrument_id`, ticker, nombre, tipo de activo, exchange, activo/inactivo, fechas, remaps y ticker lineage cuando aplique. | Saber que instrumento era realmente en esa fecha y evitar survivorship bias o errores por ticker label. |
| `market_calendar` | Dias abiertos/cerrados, sesiones, premarket, regular session, after-hours, early close, timezone y session clocks. | Saber si ese dia/minuto es comparable y construir ventanas correctas. |
| `expected_data_calendar` | Que data se espera por familia, ticker, fecha o sesion. | Distinguir ausencia esperada de ausencia patologica. |
| `corporate_actions_table` | Splits, dividends, ticker changes, mergers, symbol events y price-view implications. | Evitar leer un split, dividendo o cambio de ticker como evento de trading. |
| `master_daily_table` | Contexto diario por ticker/dia: OHLCV, gaps, volumen, RVOL, price view, daily liquidity, flags basicos y calidad. | Saber el contexto estructural antes y durante el evento. |
| `daily_scanner_candidates_table` | Candidatos in-play por definicion de scanner: filtros, ranking, top-N, denominador, as-of, source lineage y flags de calidad. | Reconstruir que tickers estaban en play y bajo que regla. No es estado completo ni universo completo. |
| `master_intraday_bar_table` | Barras intradia, normalmente 1m: OHLCV, volumen, VWAP si aplica, sesion, minute index, price view y calidad. | Reconstruir evolucion intradia, premarket, opening drive y deteccion inicial del evento. |
| `microstructure_features_table` | Resumen de quotes/trades en una ventana: spread, locked/crossed, tape intensity, odd lots, liquidez, calidad y textura libro/tape. | Saber como estaba la microestructura durante una ventana de evento. v0.1 es solo `seed_event_window_smoke`; no es entrenamiento ML/RL ni full-universe. |
| `halts_table` | Halts, resumes, suspensions, timestamps y tipo/razon de halt cuando exista. | Saber si el evento fue interrumpido o condicionado por halt. |
| `event_windows_table` | Ventanas gobernadas por evento: prior session, pre-event, event-response, same-session y next-session; incluye leakage gates y lineage del evento fuente. | Impedir que microestructura, outcomes, ML/RL o backtests inventen ventanas distintas o mezclen features pre-evento con labels post-evento. v0.1 cubre solo halts intradia LT1B con calendario. |
| `outcomes_table` | Outcomes/labels post-evento por ventana gobernada y `price_view`: retornos next-session desde cierre del evento hacia open/high/low/close de la sesion siguiente, labels discretos y quality gates. | Separar `y` de `X`: permite Outcome Research, Strategy Research y ML labels sin contaminar features pre-evento. v0.1 es diario/halt-derived; no es reward RL ni outcome de ejecucion intradia. |
| `fundamentals_asof_table` | Statement fundamentals conocidos as-of: income statements, balance sheets y cash flows con `filing_date` como disponibilidad; ratios y standalone `financial_v0_1` excluidos en v0.1. | Dar contexto estructural sin mirar informacion futura. Requiere seleccion externa `as_of_date <= event/session cutoff`; no es tabla directa de ML/RL. |
| `short_context_table` | Short interest y short volume source-scoped desde `short` y `short_review`; v0.1 no trae SSR ni borrow/availability. | Medir short pressure, squeeze context y crowding bajo as-of/lag explicito. |
| `short_sale_constraints_table` | SSR, borrow, locate, short availability, HTB/ETB state y borrow fee cuando exista fuente broker/vendor/regulatoria. | Saber si una estrategia short era ejecutable o restringida en ese instante. No puede inferirse desde short interest/volume. |
| `regime_context_table` | Regimen de mercado/ticker/sector: volatilidad, liquidez, momentum, attention regime y condiciones agregadas. | Condicionar ML/RL por regimen y evitar mezclar estados visualmente parecidos pero semanticamente distintos. |
| `news_context_table` | Noticias conocidas hasta el corte temporal: catalyst type, fuente, timestamps, ticker attribution y confidence. | Distinguir evento tecnico de evento con catalyst. |
| `real_time_corporate_event_alerts_table` | Alertas live: offering, warrants, 8-K, 6-K, SEC/newswire/vendor, `received_utc`, event type y lineage. | Detectar eventos corporativos market-moving en tiempo real y generar `corporate_event_risk_state`. |
| `dataset_certification_matrix` | Estado de calidad por familia/dataset: good/review/bad/scoped/blocked y gates de consumo. | Decidir si el caso puede usarse para research, backtest, ML o solo forense. |
| `data_quality_report` | Evidencia humana, visual, estadistica y tecnica de auditoria. | No es feature. Sirve para justificar si los inputs que alimentan el estado son confiables. |

Regla:

```text
una tabla = una pieza del estado
market_state = composicion legal y auditada de piezas
event_state = market_state + contexto/ventana/definicion del evento
```

## Por Que Hacemos Componentes Antes De Entrenar

La fase actual no intenta entrenar modelos todavia.

Intenta construir la cadena de custodia que hara posible entrenarlos despues sin
engano estadistico, sin leakage y sin ambiguedad semantica.

Motivo:

```text
Si una tabla no puede demostrar schema, lineage, calidad, hashes, tests,
as-of semantics y uso permitido en pequeno, escalarla a millones de filas solo
escala el error.
```

Por eso TSIS construye primero componentes pequenos o acotados:

1. demostrar que la forma de la tabla es correcta;
2. demostrar que se puede recomputar desde raw/auditado;
3. demostrar que cada fila conserva lineage y calidad;
4. demostrar que el consumidor sabe que puede y no puede hacer;
5. documentar visualmente ejemplos humanos;
6. solo despues ampliar cobertura.

Esta fase responde:

```text
Podemos construir correctamente la pieza?
Podemos auditarla?
Podemos explicar que representa?
Podemos impedir usos indebidos?
```

La fase futura de entrenamiento respondera:

```text
Con suficiente cobertura y labels separados, este estado ayuda a predecir,
decidir o ejecutar?
```

## Cuando Aparece Un Evento

Supongamos que el Event Engine evalua:

```text
ticker = ABCD
date = 2021-05-14
event_window = 09:30:00-10:15:00 ET
```

El uso correcto de Data Foundation no es leer un parquet gigante unico.

El flujo correcto es:

1. `instrument_master`
   - resuelve identidad temporal;
   - confirma si `ABCD` era common stock, warrant, ETF, ADR, ticker antiguo,
     ticker activo/inactivo o remap;
   - evita survivorship bias y errores por ticker label.

2. `market_calendar`
   - define si `2021-05-14` fue trading day;
   - define premarket, regular session, after-hours, early close y timezone;
   - evita construir eventos en ventanas no comparables.

3. `corporate_actions_table`
   - identifica splits, dividends, ticker events y remaps relevantes;
   - decide que price view usar: `raw`, `split_normalized`, `adjusted` o
     `adjusted_proxy`;
   - evita que un split o dividendo se lea como gap/evento falso.

4. `master_daily_table`
   - entrega el contexto diario del ticker/date;
   - gap, volumen, RVOL, market cap/float cuando existan, flags de noticia,
     halt, calidad y price view;
   - permite decidir si el dia entra en el universo de investigacion.

5. `daily_scanner_candidates_table`
   - reconstruye que tickers estaban en play bajo una definicion de scanner;
   - preserva filtros, ranking, top-N, denominador, as-of y source lineage;
   - no es estado completo ni universo completo; solo seed/candidate set para
     builders posteriores.

6. `master_intraday_bar_table`
   - entrega barras intradia canonicas, normalmente 1m;
   - permite detectar primer push, HOD, pullbacks, VWAP, PM volume,
     opening drive y evolucion del evento;
   - no debe contener todo quotes/trades bruto.

7. `microstructure_features_table`
   - consulta solo la ventana del evento cuando se necesita libro/tape;
   - calcula spread, crossed/locked, bid/ask depth, trade intensity,
     odd-lots, fuera de NBBO y liquidez usable;
   - alimenta execution realism y filtros de viabilidad;
   - v0.1 existe solo como `seed_event_window_smoke`; para ML/RL,
     backtest core o execution simulation debe existir una version posterior
     con ventanas oficiales, E-root gobernado y cobertura declarada.

8. `halts_table`
   - detecta si el evento fue interrumpido por halt, resume quote/trade o SEC
     suspension;
   - ajusta outcomes y simulacion.

9. `event_windows_table`
   - define ventanas comunes para pre-event features, event response,
     same-session context y post-event outcomes;
   - separa ventanas legalmente usables como features de ventanas que contienen
     informacion posterior;
   - v0.1 cubre solo eventos de halt intradia resueltos contra
     `instrument_master` y `market_calendar`.

10. `outcomes_table`
   - materializa labels/outcomes post-evento desde ventanas gobernadas;
   - separa resultados `y` de features pre-evento `X`;
   - v0.1 cubre solo `next_session_regular_daily` para eventos halt-derived y
     no debe usarse como reward RL ni como ejecucion intradia.

11. `fundamentals_asof_table`, `short_context_table`,
   `short_sale_constraints_table`, `regime_context_table`,
   `news_context_table`, `real_time_corporate_event_alerts_table`
   - agregan contexto solo si tienen semantica `as-of`;
   - capturan eventos corporativos market-moving publicados en segundos o
     minutos;
   - no deben contaminar el evento con informacion publicada despues.

12. `dataset_certification_matrix` y `data_quality_report`
   - deciden si el caso es `backtest_core`, `research`, `ml_flagged`,
     `forensic` o `quarantine`;
   - no son fuentes de mercado, son gates y evidencia.

Resultado:

```text
Data Foundation no produce el evento.
Data Foundation produce el estado defendible que permite detectar el evento.
```

El Event Engine consumira estas tablas y escribira `event_table` en una capa
posterior.

## Regla De Diseno: Core Delgado + Sidecars Pesados

El error a evitar es crear una tabla diaria/intradia enorme con todo mezclado.

La forma correcta es:

```text
raw/audited sources
  -> canonical compact master tables
  -> sidecar context/microstructure tables
  -> event-window joins controlados
```

Esto no pierde informacion. La conserva en capas con roles claros:

- master tables: estado canonico y keys;
- sidecars: informacion pesada o especializada;
- raw/audited sources: verdad completa preservada;
- data_quality_report: evidencia de auditoria y gates.

## Outputs Objetivo

### 1. `instrument_master`

Alias historico/arquitectonico:

```text
symbol_master
```

Nombre preferido:

```text
instrument_master
```

Motivo: `symbol` o `ticker` es una etiqueta temporal. La identidad economica
real puede sobrevivir a ticker changes, remaps, splits, mergers o cambios de
listing.

Clase:

```text
reference/context table
```

Grain recomendado:

```text
instrument_id + valid_from + valid_to
```

Keys:

```text
instrument_id
ticker
date/as_of_date
composite_figi
share_class_figi
cik
```

Fuentes candidatas:

```text
E:/TSIS/data/reference/all_tickers/
E:/TSIS/data/reference/overview/
E:/TSIS/data/reference/events/
E:/TSIS/data/reference/ticker_types/
E:/TSIS/data/reference/exchanges/
E:/TSIS/data/additional/ipos/
E:/TSIS/data/financial/
```

Muestra fisica:

```text
file: E:/TSIS/data/reference/all_tickers/snapshot_date=2005-01-02.parquet
rows_in_file: 2632
columns: ticker, name, market, locale, primary_exchange, type, active,
currency_name, cik, composite_figi, share_class_figi, last_updated_utc,
snapshot_date

ticker  name                         market  locale  primary_exchange  type  active
A       AGILENT TECHNOLOGIES, INC    stocks  us      XNYS              CS    True
AA      ALCOA INC                    stocks  us      XNYS              CS    True
```

Materializacion actual:

```text
dataset_id: instrument_master_v0_1
path: E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
rows: 4824
tickers: 4824
build_run_id: instrument_master_v0_1_20260621T145725Z
sha256: 69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
manifest: E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_summary_v0_1.csv
hard_fail_count: 0
duplicate_ticker_count: 0
```

Lectura institucional:

```text
instrument_master_v0_1 existe como primera materializacion compacta.
Su grano actual es ticker del universo lt1b_universe_v0_1.
No resuelve continuidad economica completa ni membership diaria fully PTI.
```

Uso en evento:

- confirma que el ticker era instrumento elegible ese dia;
- evita tratar warrants, preferred, ETFs o ADRs como common stock si la
  estrategia exige common stock;
- resuelve cambios de ticker antes de unir historico.

No debe contener:

- OHLCV;
- features de estrategia;
- resultados forward-looking;
- labels ML.

### 2. `corporate_actions_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
instrument_id/ticker + action_date + action_type + source
```

Fuentes candidatas:

```text
E:/TSIS/data/reference/splits/
E:/TSIS/data/reference/dividends/
E:/TSIS/data/reference/events/
E:/TSIS/data/additional/corporate_actions/
01_foundations/module_contracts/corporate_actions_adjustment_methodology.md
```

Muestra fisica:

```text
file: E:/TSIS/data/reference/splits/ticker=A/splits_A.parquet
rows_in_file: 1
columns: execution_date, id, split_from, split_to, ticker, _dataset,
_ingested_utc

execution_date  split_from  split_to  ticker
2014-11-03      1000        1398      A
```

Muestra fisica adicional:

```text
file: E:/TSIS/data/reference/dividends/ticker=A/dividends_A.parquet
rows_in_file: 1
columns: ticker, _dataset, _ingested_utc

ticker  _dataset
A       dividends
```

Uso en evento:

- decide si un gap es movimiento de mercado o ajuste corporativo;
- alimenta `split_normalized` y `adjusted`;
- evita que ML aprenda splits/dividendos como alpha;
- separa `signal_price_view`, `execution_price_view` y
  `valuation_price_view`.

No debe contener:

- precios OHLCV ya ajustados como unica verdad;
- decisiones de estrategia;
- reparaciones manuales sin lineage.

Estado materializado inicial:

```text
dataset_id: corporate_actions_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/corporate_actions_table/corporate_actions_table_v0_1.parquet
rows: 104757
tickers: 3621
instrument_ids: 3497
action_type_counts:
  dividend: 92033
  split: 6630
  ticker_change: 6094
source_system_counts:
  additional: 52490
  reference: 52267
first_action_date: 1969-12-31
last_action_date: 2027-06-15
build_run_id: corporate_actions_table_v0_1_20260622T144845Z
output_sha256: 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
hard_fail_count: 0
duplicate_corporate_action_id_count: 0
invalid_split_terms_count: 0
negative_dividend_amount_count: 0
within_instrument_valid_window_false_count: 39525
cross_source_overlap_groups: 51336
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_four_tables_v0_1/
```

Lectura institucional:

```text
corporate_actions_table_v0_1 existe como tabla de contexto corporativo y
lineage de ajustes. reference se conserva como fuente primaria y additional
como fuente secundaria/reconciliacion. La tabla no resuelve continuidad
economica completa entre ticker changes ni produce precios ajustados finales.
```

### 3. `market_calendar`

Alias arquitectonico:

```text
calendar_table
```

Clase:

```text
reference/context table
```

Grain recomendado:

```text
date + market + session
```

Fuentes candidatas:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.parquet
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.meta.json
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
exchange_calendars calendar = XNYS
timezone = America/New_York
01_foundations/module_contracts/market_session_scope.md
```

Estado:

```text
TSIS official local calendar candidate, replicable byte-for-byte with the
current builder and dependency version.
```

Verificacion local:

```text
builder: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
dependency: exchange_calendars 4.13.1
command:
python scripts/agent05_build_market_calendar_official.py ^
  --calendar XNYS ^
  --start 2005-01-01 ^
  --end 2025-12-31 ^
  --tz America/New_York ^
  --out-dir <output_dir>

current parquet sha256:
8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228

regenerated parquet sha256:
8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228

match: True
rows: 5283
first_session: 2005-01-03
last_session: 2025-12-31
early_close_sessions: 45
calendar: XNYS
timezone: America/New_York
```

Uso en evento:

- define premarket, regular, after-hours y early close;
- permite calcular `minute_index`, PM volume, opening drive y event windows;
- evita comparar una sesion incompleta con una sesion normal.

No debe contener:

- datos por ticker salvo excepciones de expected coverage;
- halts como si fueran calendario base;
- features de precio.

Fuentes externas para contraste y replicacion:

```text
exchange_calendars project:
https://github.com/gerrymanoim/exchange_calendars

NYSE Holidays & Trading Hours:
https://www.nyse.com/markets/hours-calendars

Nasdaq Stock Market Holiday Schedule:
https://www.nasdaq.com/market-activity/stock-market-holiday-schedule
```

Nota institucional:

```text
El fichero local puede llamarse oficial dentro de TSIS porque tiene builder,
metadata, hashes y reproduccion exacta. No debe describirse como descarga raw
directa de NYSE. Su fuente tecnica directa es exchange_calendars; NYSE/Nasdaq
son fuentes externas de contraste para reglas de holidays, early closes y
regular trading hours.
```

Materializacion actual:

```text
dataset_id: market_calendar_v0_1
path: E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
rows: 5283
calendar: XNYS
timezone: America/New_York
first_session: 2005-01-03
last_session: 2025-12-31
early_close_sessions: 45
build_run_id: market_calendar_v0_1_20260622T072422Z
source_parquet_sha256: 8aac3ea4f7fbcaf6c394320f53acc1524bf5e5e3addbcd48ef31718bc0214228
output_sha256: 96bd60c124e6552d269f8846205ed28bf6e58881453a5bbb4f73ced0657b56d5
hard_fail_count: 0
duplicate_session_count: 0
```

Lectura institucional:

```text
market_calendar_v0_1 existe como tabla limpia de CAPA 1.
El source local conserva el calendario oficial candidato reproducible.
El output materializado normaliza tipos y agrega lineage para consumo downstream.
```

### 4. `expected_data_calendar`

Clase:

```text
certification/quality table
```

Grain recomendado:

```text
dataset_family + ticker/instrument_id + date + expected_session
```

Motivo:

`market_calendar` dice si el mercado existe. `expected_data_calendar` dice si
esperamos que una familia tenga dato para un ticker/date concreto.

Fuentes candidatas:

```text
instrument_master
market_calendar
dataset_registry/
data_consumption_policies/
inspection_dossiers/
data_quality_report/
```

Uso en evento:

- diferencia `missing porque no debia existir` de `missing porque fallo data`;
- gobierna `expected`, `present`, `healthy`, `usable`.

No debe contener:

- precio;
- retornos;
- features de estrategia.

Estado materializado inicial:

```text
dataset_id: expected_data_calendar_v0_1
path: E:/TSIS/data/data_foundation_outputs/expected_data_calendar/expected_data_calendar_v0_1
layout: partitioned parquet dataset by dataset_family/year
rows: 29029152
dataset_families: daily_raw, ohlcv_1m_raw, quotes_raw, trades_raw
rows_per_family: 7257288
tickers: 4824
first_session: 2005-01-03
last_session: 2025-12-31
parquet_file_count: 84
tree_sha256: 1c7571cdcefc1ffd3f0f6cda921d32d64dee33cc41c3676809686c1bc575a57f
build_run_id: expected_data_calendar_v0_1_20260622T141019Z
hard_fail_count: 0
duplicate_key_groups: 0
invalid_window_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_instrument_master_market_calendar_expected_data_calendar_v0_1/
```

Lectura institucional:

```text
expected_data_calendar_v0_1 existe como denominador contractual de cobertura.
Declara expectativas por familia/ticker/sesion; no mide presencia real ni
calidad. Los reports posteriores deben unirlo contra presencia fisica,
validadores de familia y data_quality_report.
```

### 5. `master_daily_table`

Clase:

```text
analytical master table
```

Grain recomendado:

```text
instrument_id/ticker + date + price_view
```

Price views permitidas:

```text
daily_raw
split_normalized
adjusted
adjusted_proxy solo para evidencia forense, no como vista core final
```

Fuentes candidatas:

```text
E:/TSIS/data/ohlcv_daily/
E:/TSIS/data/ohlcv_daily_adjusted/
E:/TSIS/data/reference/
E:/TSIS/data/additional/news/
E:/TSIS/data/additional/ipos/
E:/TSIS/data/financial/
E:/TSIS/data/short/
E:/TSIS/data/Halts/
E:/TSIS/data/regime_indicators/
```

Muestra fisica raw:

```text
file: E:/TSIS/data/ohlcv_daily/ticker=ZZ/year=2006/day_aggs_ZZ_2006.parquet
rows_in_file: 185
columns: ticker, date, year, o, h, l, c, v, vw, n, t

ticker  date        o      h      l      c      v
ZZ      2006-04-07  17.50  18.20  17.30  17.50  23847400.0
ZZ      2006-04-10  17.61  17.62  16.76  16.84   2916300.0
```

Muestra fisica adjusted:

```text
file: E:/TSIS/data/ohlcv_daily_adjusted/ticker=ZZ/year=2006/day_aggs_ZZ_2006_adjusted.parquet
rows_in_file: 185
columns: ticker, date, year, o, h, l, c, v, vw, n, t,
future_split_factor, o_split_normalized, h_split_normalized,
l_split_normalized, c_split_normalized, future_dividend_factor,
future_adjustment_factor, o_adjusted, h_adjusted, l_adjusted, c_adjusted
```

Uso en evento:

- calcula contexto previo: gap, prior close, daily range, dollar volume, RVOL;
- identifica si el dia cumple filtros de universo/evento;
- aporta market cap/float solo si vienen de fuentes `as-of`;
- alimenta Event Engine y Outcome Research diario.

No debe contener:

- todo el libro quotes;
- todo el tape trades;
- fundamentales sin `filing_date`;
- noticias sin `published_utc`;
- labels forward-looking como features.

Estado materializado inicial:

```text
dataset_id: master_daily_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
layout: partitioned parquet dataset by year/price_view
rows: 21771864
expected_daily_rows: 7257288
price_views: daily_raw, split_normalized, adjusted
rows_per_price_view: 7257288
data_present_rows: 19782153
missing_expected_data_rows: 1989711
selected_price_hard_invalid_rows: 0
negative_volume_rows: 0
backtest_core_row_candidate_rows: 19782153
rows_with_corporate_action: 92979
parquet_file_count: 63
tree_sha256: 1c9c39202514e41a879261a62e0dbcae054bb7e503b40e6e0e44138f38894e9e
build_run_id: master_daily_table_v0_1_20260622T161747Z
hard_fail_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_six_tables_v0_1/
```

Lectura institucional:

```text
master_daily_table_v0_1 existe como superficie diaria compacta para eventos,
backtest diario y research. Mantiene grano instrument/ticker/session/price_view
y no mezcla `daily_raw`, `split_normalized` y `adjusted` en una fila opaca.
Conserva filas missing esperadas para coverage accounting y marca
`backtest_core_row_candidate`. v0.1 no une fundamentals, news, short, halts ni
regime context.
```

### 5A. `daily_scanner_candidates_table`

Clase:

```text
candidate generation table
```

Grain recomendado:

```text
scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id
```

Fuentes candidatas:

```text
instrument_master_v0_1
market_calendar_v0_1
master_daily_table_v0_1
master_intraday_bar_table_v0_1 where scoped/legal
fundamentals_asof_table_v0_1 when market-cap/float context is legal
short_context_table_v0_1 when source lag/as-of rules permit
regime_context_table_v0_1 when source lag/as-of rules permit
news_context_table_v0_1 for catalyst-aware variants
```

Contrato especifico:

```text
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
configs/data_foundation_outputs/scanner_definitions/
```

Uso en evento:

- reconstruye que tickers estaban en play bajo un scanner versionado;
- conserva filtros, ranking, top-N, denominador, as-of y lineage;
- separa visibilidad operativa humana de discovery amplio;
- sirve como seed/candidate set para builders de `market_state_table`;
- permite comparar diferentes definiciones de scanner sin contaminar estado,
  labels o estrategia.

Definiciones v0.1:

```text
trade_station_like_scanner_v0_1
  -> replica el scanner operativo humano con `volume_today > 500000` y ranking
     por `% change 1D`.

broad_in_play_discovery_scanner_v0_1
  -> protege research contra sesgo de llegada tardia y permite inclusion por
     volumen acelerado, RVOL-to-time, after-hours breakout, premarket new high,
     prior-day high reclaim, range expansion, news context o halt/reopen
     context.
```

Modelo v0.2 vigente para nuevos builders:

```text
base_in_play_universe_scanner_v0_2
  -> common stock, market cap < 100M, 0.5 < last <= 20, quality usable/review

trade_station_like_profile_v0_2
  -> volume_today >= 500000 + pct_chg_1d top 25

relative_volume_profile_v0_2
percent_change_profile_v0_2
dollar_volume_tradability_profile_v0_2
das_research_profile_v0_2
  -> profiles inside the same base denominator
```

En v0.2, `volume_today >= 500000` y `% change 1D top 25` no son filtros
universales; son perfiles/visibilidades dentro de la base comun.

No debe contener:

- market state completo;
- universo completo salvo denominador probado;
- labels, outcomes, rewards, fills, PnL o estrategia;
- autorizacion directa de ML/RL;
- seleccion manual oculta como si fuera scanner.

### 6. `master_intraday_bar_table`

Alias arquitectonico:

```text
master_intraday_table
```

Nombre preferido:

```text
master_intraday_bar_table
```

Motivo: deja claro que es una tabla de barras intradia, no una tabla que mezcla
quotes, trades y todo microstructure raw.

Clase:

```text
analytical master table
```

Grain recomendado:

```text
instrument_id/ticker + ts_utc + bar_size + price_view
```

Fuentes candidatas:

```text
E:/TSIS/data/ohlcv_1m/
E:/TSIS/data/ohlcv_1m_split_normalized/
E:/TSIS/data/intraday_regime_features/
E:/TSIS/data/Halts/
market_calendar
corporate_actions_table
```

Muestra fisica raw:

```text
file: E:/TSIS/data/ohlcv_1m/ticker=ZZ/year=2013/month=01/minute_aggs_ZZ_2013_01.parquet
rows_in_file: 3631
columns: ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t

ticker  ts_utc                date        o     h     l
ZZ      2013-01-02T14:30:00Z  2013-01-02  2.19  2.19  2.1799
ZZ      2013-01-02T14:32:00Z  2013-01-02  2.18  2.19  2.1800
```

Muestra fisica split-normalized:

```text
file: E:/TSIS/data/ohlcv_1m_split_normalized/ticker=SAVA/year=2023/month=12/minute_aggs_SAVA_2023_12_split_normalized.parquet
rows_in_file: 7760
columns: ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t,
future_split_factor, o_split_normalized, h_split_normalized,
l_split_normalized, c_split_normalized, vw_split_normalized,
materialized_price_view, source_1m_file, source_splits_file
```

Scope de esta fuente:

```text
E:/TSIS/data/ohlcv_1m_split_normalized/ no es una copia normalizada full-universe
de todo 1m. Es una materializacion piloto/proof con casos de split inspeccionados
para demostrar que el codigo y la semantica de normalizacion 1m por split son
correctos. Cuando un evento/backtest necesite otros ticker-meses con splits,
debe ejecutarse ese pipeline ya auditado sobre el scope requerido y registrarse
una nueva materializacion gobernada.
```

Runbook para materializacion amplia/full-universe:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
```

Uso en evento:

- detecta PM volume, first push, HOD, LOD, VWAP reclaim, pullback y event_end;
- sirve para outcomes intradia;
- permite materializar event windows sin escanear todo raw.

No debe contener:

- todos los quotes;
- todos los trades;
- fields de fundamentals;
- labels que solo se conocen despues de la ventana.

Materializacion actual:

```text
dataset_id: master_intraday_bar_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_1
layout: partitioned parquet dataset by year/month/price_view
materialization_scope: scoped_split_normalized_event_cases
full_universe_claim: false
rows: 175252
source_split_normalized_bar_rows: 87626
tickers: 8
ticker_months: 10
price_views: 1m_raw, 1m_split_normalized
first_ts_utc: 2006-03-01 13:02:00+00:00
last_ts_utc: 2025-02-28 22:10:00+00:00
selected_price_hard_invalid_rows: 0
negative_volume_rows: 0
event_research_bar_candidate_rows: 161176
backtest_core_bar_candidate_rows: 0
raw_quality_manifest_missing_rows: 14076
raw_quality_manifest_missing_ticker_months: 1
parquet_file_count: 14
output_tree_sha256: 288b5b296bfec4a629ef5cf841340d8b72ca3f00cbda7f51b9092a34b84bb79e
build_run_id: master_intraday_bar_table_v0_1_20260623T155007Z
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
hard_fail_count: 0
```

Lectura institucional:

```text
master_intraday_bar_table_v0_1 existe como superficie intradia gobernada,
pero scoped. No es una copia full-universe de raw 1m ni la normalizacion fisica
de todos los ticker-meses con split. Su denominador son los ticker-meses piloto
ya materializados en ohlcv_1m_split_normalized para probar el mecanismo de
normalizacion. Por contrato, backtest_core_bar_candidate es false en v0.1 y todo
consumo debe preservar materialization_scope, full_universe_claim, price_view,
raw_allowed_consumption y vwap_consumption_state.
```

Ruta quote-guarded candidate definida:

```text
dataset_id: master_intraday_bar_table_v0_2_candidate_quote_guarded
contract: 01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
config: configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
target_path: E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded
status: candidate_contract_defined_not_materialized
full_universe_claim: false
```

Motivo:

```text
El reparador quote-guarded `ohlcv_1m` esta disenado para corregir OHLC 1m
imposibles contra envelopes de quotes sin modificar los parquets raw. La tabla
intradia debe poder consumir esa vista cuando este completa, pero no debe
promocionarse mientras el repair final y su validacion no existan en E-root.
```

Bridge actual:

```text
repair_run_root: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
minute_root: E:/TSIS/data/ohlcv_1m
quotes_root: D:/quotes
quotes_root_state: provisional_d_legacy_recovery_root_pending_e_parity
future_official_root: E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
```

Modelo de almacenamiento de la ruta quote-guarded:

```text
raw ohlcv_1m + repair_manifest_v0_2.parquet = vista ohlcv_1m_quote_guarded
```

La ruta no presupone un arbol fisico completo corregido. El artefacto
promocionado esperado es el manifest de minutos afectados y los campos
`o_qg/h_qg/l_qg/c_qg` que debe aplicar el loader en memoria.

Regla:

```text
La pieza pendiente aceptada para esta ruta es cambiar de bridge/run-root a un
repair manifest oficial bajo
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded cuando el repair
termine y pase validacion final. Hasta entonces no hay parquet oficial
`master_intraday_bar_table_v0_2_candidate_quote_guarded`.
```

### 7. `microstructure_features_table`

Clase:

```text
execution/microstructure table
```

Grain recomendado:

```text
instrument_id/ticker + ts_utc or event_window_id + feature_window
```

Fuentes conceptuales:

```text
E:/TSIS/data/quotes_/   # target official E-root after D:/quotes clone/audit
E:/TSIS/data/trades_ticks_prod_2005_2026/
inspection_dossiers/quotes/
inspection_dossiers/trades/
data_consumption_policies/quotes_consumption_policy.md
data_consumption_policies/trades_consumption_policy.md
```

Fuentes usadas por la materializacion v0.1:

```text
seed input:
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/microstructure_features_seed_windows_v0_1.csv

quotes source used now:
D:/quotes

target official quotes root:
E:/TSIS/data/quotes_

legacy incomplete E quotes root:
E:/TSIS/data/quotes

trades source used now:
E:/TSIS/data/trades_ticks_prod_2005_2026

identity source:
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet

family gate source:
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
```

Regla de interpretacion:

```text
inspection_dossiers/quotes and inspection_dossiers/trades explain audit quality,
visual evidence, policies and human-readable findings. They are not the raw
source used to compute the table values.

microstructure_features_table_v0_1 computes features from the raw files declared
in source_quotes_file and source_trades_file, then attaches family gates and
identity context from governed CAPA 1 outputs.
```

La raiz `D:/quotes` es provisional para este seed porque la paridad fisica de
quotes hacia `E:/TSIS/data/quotes_` todavia esta abierta. La tabla conserva
`quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity` y debe
reconstruirse/compararse contra el root E gobernado antes de cualquier promocion
de consumo. `E:/TSIS/data/quotes` queda tratado como raiz E incompleta/legacy,
no como raiz oficial objetivo.

Muestra fisica quotes:

```text
file: D:/quotes/ZYXI/year=2025/month=12/day=01/quotes.parquet
rows_in_window: 13288
sha256: 9b73b6bdd3d1e23e65f95b39926b36a4416e82aa9f00ae1fe62544b0e2099245
columns: ask_exchange, ask_price, ask_size, bid_exchange, bid_price, bid_size,
conditions, indicators, participant_timestamp, sequence_number, timestamp,
tape, trf_timestamp, year, month, day

ask_exchange  ask_price  ask_size  bid_exchange  bid_price  bid_size  conditions
20            0.0        0         20            0.0        0         [1]
8             1.4        100       0             0.0        0         [2]
```

Muestra fisica trades:

```text
file: E:/TSIS/data/trades_ticks_prod_2005_2026/ZYXI/year=2025/month=12/day=2025-12-01/market.parquet
rows_in_window: 18182
sha256: d23f0dda5a5f8c65c9785d50675e061cee987b5e509da6007698dc60425d0646
columns: ticker, date, timestamp, price, size, exchange, conditions, year,
month, day

ticker  date        timestamp                   price  size   exchange  conditions
ZYXI    2025-12-01  2025-12-01 14:30:00.772845  1.21   29595  12        [17, 9, 41]
ZYXI    2025-12-01  2025-12-01 14:30:00.772855  1.21   29595  12        [16]
```

Current materialization:

```text
dataset_id: microstructure_features_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_1
manifest: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_summary_v0_1.csv
schema: 01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md
dataset_contract: 01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md
consumption_policy: 01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md
registry: 01_foundations/dataset_registry/outputs/microstructure_features_table_registry_entry.yaml
validators: 01_foundations/validators/outputs/microstructure_features_table_validators.md
materializer: scripts/materialize_microstructure_features_table.py
test: tests/data_foundation_outputs/test_microstructure_features_table_contract.py
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
```

Current candidate visual evidence:

```text
candidate_dataset_id: microstructure_features_table_v0_2_candidate
candidate_scope: 6-row smoke artifact under test-run artifacts only
visual_readout: 01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_visual_readout_v0_1.md
visual_manifest: 01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/microstructure_candidate_visual_manifest_v0_1.json
image_dir: 01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/images/
human_notebook: 01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb
official_dataset_created: false
full_universe_claim: false
```

Current controlled v0.2 candidate materialization:

```text
dataset_id: microstructure_features_table_v0_2_candidate
materialization_scope: halt_event_windows_microstructure_candidate_controlled_25_per_role
path: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate_controlled_25_per_role
manifest: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json
summary: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_summary_v0_2_candidate_controlled_25_per_role.csv
source_windows_csv: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/microstructure_features_table_v0_2_candidate_controlled_25_per_role/microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv
test: tests/data_foundation_outputs/test_microstructure_features_controlled_candidate.py
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_v0_2_controlled_candidate/
visual_readout: 01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
visual_manifest: 01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json
visual_image_dir: 01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/images/
visual_case_count: 50
rows: 50
tickers: 9
windows: 50
quotes_file_present_rows: 50
trades_file_present_rows: 24
review_partial_source_rows: 26
pass_seed_window_rows: 24
hard_fail_count: 0
duplicate_key_groups: 0
full_universe_claim: false
execution_sim_candidate_rows: 0
backtest_core_microstructure_candidate_rows: 0
quotes_root: D:/quotes
quotes_root_state: provisional_d_legacy_recovery_root_pending_e_parity
target_official_quotes_root: E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root: E:/TSIS/data/quotes
trades_root: E:/TSIS/data/trades_ticks_prod_2005_2026
trades_root_state: official_e_raw_root
output_tree_sha256: a3d418b06d8c4bd200d51d8eb9c6d888664c1af86ab3dd37c80d48ff2397d128
```

Interpretacion:

```text
microstructure_features_table_v0_2_candidate_controlled_25_per_role is a
controlled candidate surface for market-state design. It proves event-window
microstructure feature materialization, source lineage, quote/trade hashes,
partial-source states and sampled raw recomputation. It is not the official
production table, not full universe, not a primary ML/RL training corpus, not
core-backtest-ready and not execution-simulation truth.
```

Current v0.1 scope:

```text
build_run_id: microstructure_features_table_v0_1_20260625T155732Z
materialization_scope: seed_event_window_smoke
full_universe_claim: false
seed_window: seed_zyxi_20251201_full_day
row_count: 1
ticker_count: 1
quotes_rows: 13288
trades_rows: 18182
hard_fail_count: 0
execution_sim_candidate_rows: 0
backtest_core_microstructure_candidate_rows: 0
```

Uso en evento:

- calcula spread, quoted liquidity, tape intensity, print size distribution,
  outside-range flags, odd-lot texture y execution feasibility;
- se consulta por ventana de evento, no como join permanente full-history;
- alimenta Execution Models y filtros de realismo.

No debe contener:

- todo quotes/trades bruto duplicado;
- price adjustment economico;
- targets de outcome.
- claims de cobertura full-universe;
- autorizacion de core backtesting o execution simulation mientras el scope sea
  `seed_event_window_smoke`.

### 8. `fundamentals_asof_table`

Clase:

```text
reference/context table
```

Grain materializado v0.1:

```text
source_file_relative_path + source_file_row_number + statement_family
```

Fuente v0.1:

```text
E:/TSIS/data/additional/financials
```

Subfamilias incluidas:

```text
income_statements
balance_sheets
cash_flow_statements
```

Exclusiones v0.1:

```text
additional/financials/ratios = review_sparse_vendor_derived_snapshot_not_statement_asof_core
E:/TSIS/data/financial = blocked_by_financial_consumption_policy_audit_status_FAIL
```

Materializacion actual:

```text
dataset_id: fundamentals_asof_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1
rows: 621756
tickers: 4813
instruments: 4590
parquet_files: 51
build_run_id: fundamentals_asof_table_v0_1_20260626T101617Z
materialization_scope: additional_financials_core_lt1b_statement_asof_v0_1
output_tree_sha256: 07d3d0200e16e020cee79fc2cf6aa873cde0145cf7efa0f07d0e78c8aefe5d58
manifest: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_summary_v0_1.csv
full_universe_claim: false
```

Conteos:

```text
source_files = 14472
business_files = 14436
empty_sentinel_files = 36
business_rows = 621756

statement rows:
  income_statements = 242886
  balance_sheets = 136661
  cash_flow_statements = 242209

quality:
  good_statement_asof = 500530
  review_no_temporal_identity = 121217
  review_period_after_filing_date = 9
```

Uso en evento:

- aporta statement fundamentals conocidos legalmente por `filing_date`;
- permite enriquecer un evento solo despues de seleccionar la ultima fila
  elegible con `as_of_date <= event/session cutoff`;
- alimenta Pattern Discovery y ML flagged despues de pasar leakage checks y
  conservar `fundamental_quality_state`.

No debe contener:

- datos conocidos despues del evento como si fueran presentes;
- period_end tratado como availability date;
- ratios vendor snapshot de v0.1;
- standalone `financial_v0_1` mientras siga bloqueado;
- market cap/float historico intradia sin fuente as-of propia;
- causalidad por defecto.

### 9. `news_context_table`

Clase:

```text
reference/context table
```

Grain recomendado:

```text
article_id + published_utc + ticker/requested_ticker
```

Fuentes candidatas:

```text
E:/TSIS/data/additional/news/
C:/TSIS_Data/data/additional/news/
```

Uso en evento:

- aporta `news_flag`, catalyst timing y contexto narrativo;
- permite distinguir evento tecnico sin noticia de evento con catalyst;
- debe preservar `published_utc` y ambiguedad multi-ticker.

No debe contener:

- prueba de causalidad por si sola;
- articulo posterior al evento como feature pre-event.

Materializacion v0.1:

```text
dataset_id: news_context_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1/
manifest: E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_summary_v0_1.csv
build_run_id: news_context_table_v0_1_20260626T123436Z
materialization_scope: additional_news_lt1b_published_utc_context_v0_1
rows: 287138
tickers: 3869
instruments: 3699
parquet_files: 9
output_tree_sha256: bff4a26caaab27e1d7974e8947ecea8b26cea09e585fe304206812db8aafdbff
```

Quality:

```text
good_mono_ticker_news_context: 102556
good_review_multi_ticker_news_context: 180051
review_no_temporal_identity: 4531
hard_fail_count: 0
valid_for_event_context_candidate_rows: 282607
valid_for_rl_training_direct_rows: 0
```

Uso correcto:

- consumir solo con `published_utc <= event/decision cutoff`;
- preservar `ticker` solicitado separado de `payload_tickers`;
- tratar multi-ticker como attribution-review aunque pueda ser contexto valido;
- no confundir `published_utc` historico con `received_utc` live.

### 10. `short_context_table`

Clase:

```text
reference/context state component table
```

Grain materializado v0.1:

```text
source_system + observation_family + ticker + observation_date +
source_duplicate_key_ordinal
```

Fuentes v0.1:

```text
E:/TSIS/data/short/
E:/TSIS/data/short_review/finra_short/
instrument_master_v0_1
```

Materializacion actual:

```text
dataset_id: short_context_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1/
manifest: E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_summary_v0_1.csv
build_run_id: short_context_table_v0_1_20260626T215417Z
materialization_scope: short_and_short_review_source_scoped_context_v0_1
rows: 7145337
tickers: 4694
instruments: 4462
first_observation_date: 2017-12-29
last_observation_date: 2026-04-29
parquet_files: 32
output_tree_sha256: 57c0abbdf6a1d4ef4d1ab6bd7ac326e2d57415645d7cd759605334334271652b
full_universe_claim: false
```

Contratos y codigo:

```text
schema: 01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md
dataset contract: 01_foundations/contract_registry/dataset_contracts/short_context_table_dataset_contract_v0_1.md
registry: 01_foundations/dataset_registry/outputs/short_context_table_registry_entry.yaml
policy: 01_foundations/data_consumption_policies/short_context_table_consumption_policy.md
validators: 01_foundations/validators/outputs/short_context_table_validators.md
materializer: scripts/materialize_short_context_table.py
tests: tests/data_foundation_outputs/test_short_context_table_contract.py
```

Evidencia de test:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Conteos por fuente/familia:

```text
finra_official_free:short_interest rows = 505745, tickers = 4687
finra_official_free:short_volume   rows = 4689038, tickers = 4623
local_polygon:short_interest       rows = 520048, tickers = 4693
local_polygon:short_volume         rows = 1430506, tickers = 3381

source_system_counts:
  finra_official_free = 5194783
  local_polygon = 1950554

observation_family_counts:
  short_interest = 1025793
  short_volume = 6119544
```

Quality:

```text
good_finra_official_free_short_interest_context = 306856
good_finra_official_free_short_volume_context = 4528387
good_local_certified_short_interest_context = 130656
good_local_certified_short_volume_context = 114128
review_finra_pre_2021_short_interest_semantics = 160406
review_local_certification_status = 1705770
review_no_temporal_identity = 193060
review_source_duplicate_key = 6074

bad_rows = 0
duplicate_key_excess_rows = 5250
valid_for_event_context_candidate_rows = 5240433
valid_for_ml_feature_candidate_rows = 5080027
valid_for_state_component_candidate_rows = 5240433
valid_for_rl_training_direct_rows = 0
borrow_data_present_rows = 0
ssr_data_present_rows = 0
full_universe_claim_rows = 0
```

Lectura institucional:

```text
short_context_table_v0_1 no elige una fuente unica de verdad opaca para short.
Preserva dos planos fuente: `local_polygon` y `finra_official_free`.

`short_review`/FINRA es baseline oficial/free y provenance. `short` conserva
el plano local operativo. Los consumidores deben seleccionar fuente, familia,
quality gate y lag/as-of de forma explicita.
```

Uso en evento:

- contexto de crowding y squeeze risk;
- short interest como contexto de posicionamiento reportado, no como intraday
  inventory;
- short volume como contexto diario de flujo/crowding, no como sell-short tape
  completo;
- debe consumirse con `observation_date <= event/decision cutoff` y lag/
  availability explicitos;
- puede alimentar Event Engine, Market State Builder, backtest extended y
  `ml_flagged` solo bajo gates de calidad y as-of externo.

No debe contener:

- tape;
- SSR;
- borrow/locate/availability real-time;
- causalidad intradia no demostrada;
- senales de estrategia;
- labels/outcomes;
- reward RL;
- una decision silenciosa entre FINRA y local.

### 10b. `short_sale_constraints_table`

Clase:

```text
execution constraint / reference state component table
```

Status:

```text
target_defined_not_materialized
```

Contrato especifico:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md
```

Runbook de adquisicion y preparacion:

```text
01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md
```

Grain objetivo:

```text
SSR:
source_system + ticker/instrument_id + trading_date + venue_or_listing_market

borrow/locate/availability:
source_system + broker_or_vendor + account_scope + ticker/instrument_id +
as_of_utc + source_event_id
```

Fuentes candidatas:

```text
SSR:
official exchange/listing-market short-sale restriction files
SEC / Regulation SHO rule reference
vendor market data SSR feeds
derived proxy from validated daily + intraday prices
broker/order-route reject logs

borrow/locate/availability:
broker API or broker export
DAS/SageTrader-compatible broker records if exposed by broker/API
vendor securities-lending data
internal OMS/order logs for locate requests and approvals
execution reject logs
```

Fuentes que no bastan:

```text
short_context_table_v0_1
FINRA short volume
FINRA short interest
daily OHLCV alone
quotes/trades alone for borrow
```

Uso en evento:

- determinar si SSR estaba activo en el momento del evento;
- bloquear o ajustar ejecucion short cuando SSR restringe ordenes agresivas;
- saber si habia shares available to short antes del cutoff;
- saber si locate era requerido, solicitado y aprobado;
- conocer broker/vendor/account scope de la disponibilidad;
- alimentar execution realism, short strategy feasibility y live pre-checks.

No debe contener:

- short interest;
- short volume;
- senales de estrategia;
- labels/outcomes;
- claims de borrow universal entre brokers;
- availability posterior al evento;
- reward RL directo.

Bloqueo actual:

```text
materialized = false
known_physical_source_under_E:/TSIS/data = false
short_context_table_replacement = false
backtest_short_execution_ready = false
live_trading_ready = false
```

Regla historica:

```text
20 years of market data
!=
20 years of broker-specific borrow inventory
```

El historico de precios, volumen, quotes, trades y short context permite
estudiar mercado y presion short. No permite afirmar historico de borrow,
locate, availability, HTB/ETB o borrow fee por broker/cuenta. Para eso hace
falta fuente broker/vendor historica o captura live desde el primer dia
operativo.

Lectura institucional:

```text
TSIS puede estudiar short pressure con `short_context_table_v0_1`.
TSIS no puede afirmar short execution feasibility institucional hasta que
`short_sale_constraints_table` exista con fuente SSR/borrow/locate trazable.
```

### 11. `real_time_corporate_event_alerts_table`

Clase:

```text
reference/event table + live alert stream
```

Grain recomendado:

```text
alert_id + source + received_utc + ticker/instrument_id + event_type
```

Motivo:

Las capturas revisadas muestran una clase de dato que hoy no queda cubierta por
las tablas objetivo: alertas en tiempo real de eventos corporativos que pueden
mover precio en segundos.

Ejemplo observado en captura:

```text
source: PR Newswire
headline: IceCure Announces Pricing of $5.5 Million Private Placement...
published/display time: Jun 17 13:14 EDT
ticker: ICCM
event family: offering/private placement/warrants
```

Otro panel observado muestra alertas mezcladas de:

```text
PRN  = PR Newswire
GLB  = GlobeNewswire
SEC  = SEC filing
forms/events: 8-K, 6-K, 424B3, offerings, warrants, reverse split
```

Fuentes actuales en TSIS:

```text
E:/TSIS/data/additional/news/
```

Estado de cobertura actual:

```text
historical/contextual news exists
real-time low-latency alert feed does not exist as governed Data Foundation output
offering-specific alert stream does not exist
SEC filing stream does not exist as live operational feed
```

Muestra fisica actual de `additional/news`:

```text
file: E:/TSIS/data/additional/news/news/ticker=AACT/news_AACT.parquet
rows_in_file: 3
columns: id, title, author, published_utc, article_url, tickers, image_url,
description, keywords, insights, ticker, publisher.name, _dataset,
_ingested_utc

publisher.name examples: Benzinga, MarketWatch
published_utc example: 2025-09-24T20:05:00Z
```

Interpretacion:

```text
additional/news puede servir para research historico y contexto narrativo.
No prueba que TSIS tenga un feed de alertas sub-segundo o de pocos segundos.
No debe tratarse como sustituto de un sistema live de offerings/filings.
```

Campos minimos:

```text
alert_id
event_id_vendor
source
source_channel
ticker
instrument_id
cik
headline
event_type
event_subtype
form_type
published_utc
accepted_utc
received_utc
first_seen_utc
latency_ms_from_source_if_available
url
raw_text
parsed_terms
offering_amount
offering_price
warrant_flag
warrant_terms
discount_or_premium_to_last_close
shares_or_units
underwriter_or_placement_agent
is_amendment
is_correction
confidence
severity
trading_action_hint
raw_payload_path
source_terms
```

Event types iniciales:

```text
offering_pricing
registered_direct
private_placement
atm_offering
shelf_registration
424B_filing
S1_or_S3_registration
F1_or_F3_registration
8K_material_event
6K_foreign_issuer_event
warrant_issuance
reverse_split
delisting_notice
going_concern
clinical_regulatory_update
merger_spac_business_combination
halt_related_news
```

Uso en evento:

- veto o degradacion inmediata de long momentum cuando aparece offering
  dilutivo;
- explicacion causal de collapses intradia;
- generacion de `corporate_event_risk_state` para Event Engine, Strategy
  Research, Execution Models y live trading;
- separacion entre evento tecnico de mercado y evento informacional externo;
- labeling historico de reacciones post-offering.

No debe contener:

- precio como fuente primaria;
- decision automatica de trading sin risk policy;
- inferencias no trazables de LLM sin raw text y confidence;
- noticias historicas sin timestamp de publicacion/recepcion.

Fuentes para conseguirlo en tiempo real:

1. SEC EDGAR APIs / SEC submissions stream.

   Fuente oficial:

   ```text
   https://www.sec.gov/search-filings/edgar-application-programming-interfaces
   ```

   Uso:

   - polling de `data.sec.gov/submissions/CIK##########.json`;
   - forms relevantes: `8-K`, `6-K`, `424B3`, `424B5`, `S-1`, `S-3`,
     `F-1`, `F-3`, `POS AM`, `FWP`;
   - SEC indica que submissions API se actualiza en real time as filings are
     disseminated, con typical processing delay menor a un segundo para
     submissions, aunque puede ser mayor en picos.

   Limitacion:

   - EDGAR llega cuando se presenta el filing;
   - muchas offerings impactantes salen primero por PR Newswire/GlobeNewswire
     y el filing puede llegar despues;
   - por tanto SEC solo no basta para alerta de segundos.

2. Newswire / financial news vendor low-latency.

   Fuentes candidatas:

   ```text
   PR Newswire / Cision
   GlobeNewswire
   Business Wire
   Benzinga Pro / Benzinga news feed
   Dow Jones / FactSet / Refinitiv / MT Newswires / similares institucionales
   ```

   Uso:

   - capturar headlines como las de las capturas;
   - filtrar keywords: `offering`, `registered direct`, `private placement`,
     `warrants`, `ATM`, `priced`, `securities purchase agreement`,
     `gross proceeds`, `shelf`, `424B`;
   - normalizar ticker, source, timestamp y raw text.

   Limitacion:

   - feeds verdaderamente low-latency suelen ser de pago;
   - hay que medir latencia real `published_utc -> received_utc`;
   - no basta con APIs historicas actualizadas por lotes.

3. DAS Trader / NewsWare investigation note.

   Fuentes publicas revisadas:

   ```text
   https://dastrader.com/
   https://dastrader.com/das-api-services/
   https://newsware.com/
   https://newsware.com/newswatch/
   ```

   Lectura tecnica:

   - DAS anuncia servicios de real-time market data y real-time streaming news
     from Newsware dentro de su servicio Market Data Vendor.
   - NewsWare anuncia delivery en tiempo real directamente desde publishers,
     alertas por portfolio/eventos y NewsWare API para entregar noticias de
     cientos de fuentes en un formato.
   - La pagina publica de DAS API no confirma que el API de DAS Trader Pro
     exponga el stream de noticias de NewsWare.
   - La pagina publica de DAS API indica que el uso requiere certificacion, que
     sus documentos/source code estan protegidos, que FIX API es order entry
     only y que sus API services no estan disenados para redistribucion de
     market data o aplicaciones comerciales.

   Decision institucional:

   ```text
   DAS/NewsWare = candidate live alert source.
   DAS Trader Pro API public docs = not enough evidence for governed ingestion.
   NewsWare API direct feed = preferred route to evaluate for TSIS ingestion.
   ```

   Regla:

   ```text
   No asumir que DAS Trader Pro API entrega offerings/news en tiempo real hasta
   obtener documentacion certificada de DAS o contrato directo con NewsWare.
   ```

4. Polygon/Massive News API como historical/context feed.

   Fuente:

   ```text
   https://polygon.io/docs/rest/stocks/news
   ```

   Uso:

   - research historico;
   - contexto narrativo;
   - backfill de news.

   Limitacion:

   - la documentacion muestra endpoint de noticias con metadata, tickers,
     publisher, sentiment y `published_utc`;
   - en los planes visibles la recencia se muestra como `Updated hourly`;
   - no debe asumirse apto para alertas de segundos.

Arquitectura live recomendada:

```text
SEC EDGAR poller
Newswire/vendor websocket or polling feed
  -> raw_alert_log append-only
  -> event classifier deterministic + LLM optional with audit
  -> real_time_corporate_event_alerts_table
  -> live risk/event bus
  -> historical replay dataset
```

Regla institucional:

```text
Para backtest puede bastar `published_utc`.
Para live trading hace falta tambien `received_utc` y medicion de latencia.
Sin `received_utc`, no se puede simular honestamente una alerta en segundos.
```

### 12. `halts_table`

Clase:

```text
reference/event table
```

Grain recomendado:

```text
ticker/instrument_id + halt_start + source
```

Fuentes candidatas:

```text
E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
D:/Halts/processed/halts_master_multisource.parquet
```

Muestra fisica:

```text
file: E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
rows_in_file: 133116
columns: source, source_priority, ticker, issuer_name, listing_exchange,
halt_date, halt_start_et, resume_quote_et, resume_trade_et, halt_code,
halt_type, raw_reason, release_no, item_link, url_source, is_sec_suspension

source  source_priority  ticker  issuer_name                          halt_date
sec     1                <NA>    Garcis U.S.A., Inc.                  1995-10-13
sec     1                <NA>    Environmental Chemicals Group, Inc.   1995-12-12
```

Materializacion actual:

```text
dataset_id: halts_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/halts_table/halts_table_v0_1.parquet
rows: 133116
build_run_id: halts_table_v0_1_20260625T191305Z
sha256: b7a2be01e8af852b9c00a7509648f8554e796ad04867fbc67879596a074084a8
manifest: E:/TSIS/data/data_foundation_outputs/halts_table/_halts_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/halts_table/_halts_table_summary_v0_1.csv
source_master: E:/TSIS/data/Halts/processed/halts_master_multisource.parquet
source_master_sha256: f7b72c298434529788e5ca65fee775e1869c04e02c69c1730ac77509ca899213
source_summary_sha256: 8b2a8eda463b04dd2a1802a9f79061b565a67e292d823302beb3249cb89ae387
```

Contratos y codigo:

```text
schema: 01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md
dataset contract: 01_foundations/contract_registry/dataset_contracts/halts_table_dataset_contract_v0_1.md
registry: 01_foundations/dataset_registry/outputs/halts_table_registry_entry.yaml
policy: 01_foundations/data_consumption_policies/halts_table_consumption_policy.md
validators: 01_foundations/validators/outputs/halts_table_validators.md
materializer: scripts/materialize_halts_table.py
tests: tests/data_foundation_outputs/test_halts_table_contract.py
```

Evidencia de test:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Conteos materializados:

```text
source_counts:
  nasdaq = 118592
  nyse = 13178
  sec = 1346

event_state_counts:
  good_full_intraday_event = 131671
  regulatory_context_only = 1346
  review_partial_identity = 88
  bad_unusable_event = 11

quality_state_counts:
  good = 133017
  review = 88
  bad = 11

valid_for_intraday_mask_count = 131671
valid_for_date_context_count = 133017
valid_for_backtest_event_mask_candidate_count = 131671
```

Anomalias preservadas:

```text
missing_halt_date_count = 11
future_date_flag_count = 8
timestamp_order_review_flag_count = 87
parse_suspect_flag_count = 88
duplicate_source_event_key_row_count = 1709
```

Lectura institucional:

```text
halts_table_v0_1 existe como output gobernado de CAPA 1 para contexto de
interrupciones de mercado. No repara silenciosamente anomalias del source:
las clasifica como good/review/bad y conserva lineage por fila.

Es apta para event context, halt masks y restricciones de outcome/backtest
cuando los gates lo permitan. No es fuente de precio, no es verdad de
ejecucion, no prueba disponibilidad decision-time y no sustituye un contrato
live con received_utc/latency.
```

Uso en evento:

- interrumpe event windows;
- ajusta outcome horizons;
- alimenta execution risk y continuation/failure research.

No debe contener:

- OHLCV;
- inferencias de estrategia;
- timestamps inventados cuando solo existe fecha.

### 12b. `event_windows_table`

Clase:

```text
event-window/state-boundary table
```

Grain materializado v0.1:

```text
source_event_id + window_role
```

Fuente v0.1:

```text
halts_table_v0_1
instrument_master_v0_1
market_calendar_v0_1
```

Materializacion actual:

```text
dataset_id: event_windows_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
rows: 214112
source_events: 42829
tickers: 3710
instruments: 3567
build_run_id: event_windows_table_v0_1_20260625T231016Z
sha256: cee3675487d13353f409813b24f44565aeb0187312dea860bbba13c977b1643e
manifest: E:/TSIS/data/data_foundation_outputs/event_windows_table/_event_windows_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/event_windows_table/_event_windows_table_summary_v0_1.csv
materialization_scope: halts_intraday_lt1b_calendar_covered
full_universe_claim: false
```

Contratos y codigo:

```text
schema: 01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
dataset contract: 01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md
registry: 01_foundations/dataset_registry/outputs/event_windows_table_registry_entry.yaml
policy: 01_foundations/data_consumption_policies/event_windows_table_consumption_policy.md
validators: 01_foundations/validators/outputs/event_windows_table_validators.md
materializer: scripts/materialize_event_windows_table.py
tests: tests/data_foundation_outputs/test_event_windows_table_contract.py
```

Evidencia de test:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Conteos materializados:

```text
source_valid_intraday_event_count = 131671
identity_temporal_match_event_count = 44976
calendar_covered_event_count = 42829
excluded_no_temporal_identity_event_count = 86695
excluded_no_market_calendar_session_event_count = 2147

window_role_counts:
  prior_session_regular = 42829
  pre_event_30m = 42829
  event_to_resume_or_30m = 42829
  same_session_regular = 42829
  next_session_regular = 42796

event_session_phase_counts:
  regular = 38672
  afterhours = 2537
  premarket = 1620

event_window_quality_state_counts:
  good = 213651
  review_resume_fallback = 461
```

Lectura institucional:

```text
event_windows_table_v0_1 existe para fijar fronteras temporales, no para
crear features, labels, estrategias o rewards.

La tabla separa ventanas pre-evento legalmente usables como features de
ventanas que contienen informacion posterior y solo deben alimentar outcomes,
labels o analisis de respuesta.
```

Uso en evento:

- define `prior_session_regular`, `pre_event_30m`,
  `event_to_resume_or_30m`, `same_session_regular` y
  `next_session_regular`;
- permite que microstructure/outcomes/ML/backtest usen la misma frontera de
  evento;
- bloquea leakage mediante `leakage_safe_as_pre_event_feature` y
  `valid_for_ml_feature_candidate`.

No debe contener:

- OHLCV;
- quotes/trades bruto;
- returns/outcomes calculados;
- estrategia;
- reward RL;
- event families no materializadas.

### 12c. `outcomes_table`

Clase:

```text
outcome/label component table
```

Grain materializado v0.1:

```text
event_window_id + outcome_horizon + price_view
```

Fuente v0.1:

```text
event_windows_table_v0_1
master_daily_table_v0_1
```

Materializacion actual:

```text
dataset_id: outcomes_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/outcomes_table/outcomes_table_v0_1.parquet
rows: 128388
event_windows: 42796
source_events: 42796
tickers: 3709
instruments: 3566
price_views: daily_raw, split_normalized, adjusted
outcome_horizon: next_session_regular_daily
materialization_scope: halt_next_session_daily_outcomes_v0_1
build_run_id: outcomes_table_v0_1_20260626T073950Z
sha256: ce793a75d747d50c053f44433d5e3e59ebb3616db7056c3e5087a005fb6db09e
manifest: E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/outcomes_table/_outcomes_table_summary_v0_1.csv
full_universe_claim: false
```

Contratos y codigo:

```text
schema: 01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md
dataset contract: 01_foundations/contract_registry/dataset_contracts/outcomes_table_dataset_contract_v0_1.md
registry: 01_foundations/dataset_registry/outputs/outcomes_table_registry_entry.yaml
policy: 01_foundations/data_consumption_policies/outcomes_table_consumption_policy.md
validators: 01_foundations/validators/outputs/outcomes_table_validators.md
materializer: scripts/materialize_outcomes_table.py
tests: tests/data_foundation_outputs/test_outcomes_table_contract.py
```

Evidencia de test:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Conteos materializados:

```text
outcome_quality_state_counts:
  good_daily_outcome = 121761
  review_outcome_daily_missing = 3858
  review_event_and_outcome_daily_missing = 1980
  review_event_daily_missing = 789

rows_by_price_view:
  daily_raw = 42796
  split_normalized = 42796
  adjusted = 42796

valid_for_ml_label_candidate_rows = 121761
valid_for_strategy_label_candidate_rows = 121761
valid_for_backtest_outcome_candidate_rows = 121761
valid_for_rl_reward_candidate_rows = 0
outcome_daily_join_missing_rows = 1389
```

Lectura institucional:

```text
outcomes_table_v0_1 existe para materializar la parte `y` post-evento de una
ventana gobernada. No puede consumirse como feature pre-evento.

La tabla separa labels y outcomes diarios de los componentes de estado. Las
filas review se preservan para explicar cobertura y evitar fabricar labels
cuando falta data diaria esperada o no existe fila outcome enlazable.
```

Uso en evento:

- calcula retornos desde `event_close` hacia `outcome_open/high/low/close` de
  la siguiente sesion regular;
- emite labels discretos por umbrales diarios;
- habilita Outcome Research, Strategy Research y ML labels bajo
  `valid_for_ml_label_candidate=true`;
- preserva `price_view` para no mezclar raw, split-normalized y adjusted.

No debe contener:

- features pre-evento;
- estrategia;
- accion o policy;
- reward RL;
- slippage/fills;
- outcome intradia halt-resume;
- quotes/trades bruto.

### 12. `regime_context_table`

Clase:

```text
reference/context table
```

Grain materializado v0.1:

```text
regime_symbol + trading_date + source_granularity
```

Fuente materializada:

```text
E:/TSIS/data/regime_indicators/**/minute.parquet
E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet
```

Fuentes explicitamente excluidas en v0.1:

```text
E:/TSIS/data/regime_indicators/**/day.parquet
E:/TSIS/data/intraday_regime_features/
E:/TSIS/data/additional/economic/
```

Nota:

```text
regime_indicators day.parquet queda bloqueado porque la auditoria previa mostro
date/datetime sospechosos 1970-01-01. regime_context_table_v0_1 se construye
desde minute.parquet y conserva el bloqueo en manifest, schema, policy y tests.
```

Materializacion v0.1:

```text
dataset_id: regime_context_table_v0_1
path: E:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1/
manifest: E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_summary_v0_1.csv
build_run_id: regime_context_table_v0_1_20260627T084649Z
rows: 154692
regime_symbols: 33
parquet_files: 25
source_minute_files: 33
source_minute_rows_aggregated: 64348953
blocked_day_files: 34
output_tree_sha256: 6cb774257e72ec1fa0e0c4fd514141b684f21e262de0a82206362bdbfbcba48c
```

Quality:

```text
good_minute_aggregated_regime_context: 143840
review_no_market_calendar_session: 9214
review_source_bar_integrity: 107
review_sparse_minute_coverage: 1531
bad_rows: 0
```

Consumer gates:

```text
valid_for_event_context_candidate_rows: 143840
valid_for_ml_feature_candidate_rows: 143834
valid_for_state_component_candidate_rows: 143840
valid_for_backtest_core_direct_rows: 0
valid_for_rl_training_direct_rows: 0
requires_asof_filter: true
contains_future_information_without_event_filter: true
same_session_intraday_causal_claim_allowed: false
execution_truth: false
full_universe_claim: false
```

Contract stack:

```text
schema: 01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md
dataset contract: 01_foundations/contract_registry/dataset_contracts/regime_context_table_dataset_contract_v0_1.md
registry: 01_foundations/dataset_registry/outputs/regime_context_table_registry_entry.yaml
policy: 01_foundations/data_consumption_policies/regime_context_table_consumption_policy.md
validators: 01_foundations/validators/outputs/regime_context_table_validators.md
materializer: scripts/materialize_regime_context_table.py
tests: tests/data_foundation_outputs/test_regime_context_table_contract.py
```

Test evidence:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
```

Uso en evento:

- marca contexto de mercado: risk-on/risk-off, volatility, index trend,
  liquidity regime;
- permite Pattern Discovery y ML condicionado por regimen despues de un as-of
  join externo;
- aporta un componente de estado para `market_state_builder`, no el estado
  final completo.

No debe contener:

- ticker-level causality por defecto;
- fechas erroneas sin correction contract;
- labels forward-looking.
- same-session intraday causal state;
- execution truth;
- direct RL training rows.

### 13. `dataset_certification_matrix`

Clase:

```text
certification/quality table
```

Grain recomendado:

```text
dataset_family + scope + ticker/date optional + quality_version
```

Materializacion v0.1:

```text
dataset_family + family_level + dataset_certification_matrix_policy_v0_1
```

Fuentes candidatas:

```text
01_foundations/data_quality_report/
01_foundations/inspection_dossiers/
01_foundations/dataset_registry/
01_foundations/data_consumption_policies/
01_foundations/validators/
01_foundations/FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md
01_foundations/DATA_AUDIT_QUALITY_STANDARD.md
```

Uso en evento:

- decide si cada input del evento es `good`, `review`, `bad`,
  `recoverable_with_flag` o `quarantine`;
- permite excluir casos del backtest core sin borrar evidencia;
- permite ML con flags de calidad cuando aplique.

No debe contener:

- precios;
- book/tape;
- fundamentales;
- estrategia.

Estado materializado inicial:

```text
dataset_id: dataset_certification_matrix_v0_1
path: E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
rows: 13
family_count: 13
human_inspector_ready_count: 13
visual_casepack_complete_count: 13
blocked_from_backtest_core_count: 2
scoped_only_count: 5
data_quality_verdict_counts:
  blocked_by_data_defect: 2
  complete_scoped: 5
  usable_for_declared_scope: 6
build_run_id: dataset_certification_matrix_v0_1_20260622T154116Z
output_sha256: e7803e3ec58cfb92c1313efc09bdd3a015800c4680437e4567a0174b257f1fb0
source_family_status_matrix_sha256: c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35
hard_fail_count: 0
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-22/data_foundation_outputs_five_tables_v0_1/
```

Lectura institucional:

```text
dataset_certification_matrix_v0_1 existe como gate familiar de calidad y
evidencia. Convierte `family_status_matrix_v0_1.md` en tabla gobernada y
verifica que cada familia tenga root fisico, report, dossier, schema,
contract, registry, policy, validator y evidencia visual. No valida filas de
mercado y no repara familias bloqueadas.
```

### 14. `data_quality_report`

Clase:

```text
forensic evidence / human inspection package
```

No es una tabla de mercado.

Contenido esperado:

```text
family_status_matrix
visual inspection dossiers
good/review/bad case packs
schema validation results
missing data analysis
outlier analysis
format analysis
coverage analysis
known limitations
promotion status
links to evidence assets
```

Fuentes candidatas:

```text
01_foundations/data_quality_report/
01_foundations/inspection_dossiers/
01_foundations/validators/
01_foundations/contract_registry/
01_foundations/canonical_schemas/
```

Uso en evento:

- no se une al evento como feature;
- se consulta para saber si las fuentes que alimentan ese evento son
  defendibles;
- sirve para auditor humano e institucional promotion gates.

No debe contener:

- informacion completa del mercado;
- una copia de raw parquet;
- decisiones operativas de estrategia.

## Mapa De Dependencias Por Evento

```text
instrument_master
  -> valida identidad y universo

market_calendar
  -> valida sesion y ventanas

corporate_actions_table
  -> define price views y evita falsos gaps

master_daily_table
  -> contexto diario pre-evento y dia del evento

master_intraday_bar_table
  -> evolucion intradia y deteccion del evento

microstructure_features_table
  -> solo si hace falta realismo de ejecucion o diagnostico tape/book

halts_table
  -> interrumpe o clasifica el evento

event_windows_table
  -> fija fronteras temporales pre-evento, respuesta y outcome

real_time_corporate_event_alerts_table
  -> captura catalysts corporativos publicados en segundos/minutos

fundamentals/news/short/regime context
  -> explica contexto con as-of semantics

short_sale_constraints_table
  -> valida SSR, borrow, locate y shortability antes de asumir ejecucion short

dataset_certification_matrix + data_quality_report
  -> decide si el caso se puede usar y bajo que restricciones

Event Engine
  -> escribe event_table downstream
```

## Root Comun De Outputs CAPA 1

Los outputs gobernados por este contrato deben vivir bajo:

```text
E:/TSIS/data/data_foundation_outputs/
```

Layout objetivo:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/
E:/TSIS/data/data_foundation_outputs/market_calendar/
E:/TSIS/data/data_foundation_outputs/corporate_actions_table/
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/
E:/TSIS/data/data_foundation_outputs/master_daily_table/
E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/
E:/TSIS/data/data_foundation_outputs/real_time_corporate_event_alerts_table/
E:/TSIS/data/data_foundation_outputs/halts_table/
E:/TSIS/data/data_foundation_outputs/event_windows_table/
E:/TSIS/data/data_foundation_outputs/outcomes_table/
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/
E:/TSIS/data/data_foundation_outputs/news_context_table/
E:/TSIS/data/data_foundation_outputs/short_context_table/
E:/TSIS/data/data_foundation_outputs/short_sale_constraints_table/
E:/TSIS/data/data_foundation_outputs/regime_context_table/
E:/TSIS/data/data_foundation_outputs/data_quality_report/
```

Regla:

```text
Estas tablas no deben materializarse como carpetas sueltas al mismo nivel que
raw/source folders (`reference`, `ohlcv_daily`, `quotes`, `trades`, etc.).
```

Excepcion live-ingestion:

```text
raw_alert_log append-only no es una tabla limpia de CAPA 1. Debe vivir separado:

E:/TSIS/data/live_ingestion/raw_alert_log/
```

## Politica De Tamano Y Optimizacion

Data actual observada por el humano:

```text
raw/audited data actual ~= 1 TB
```

El objetivo no es duplicar ese terabyte.

### Escenarios

```text
Malo: copiar raw completo en master tables
  incremento esperado: +1.0 TB a +2.0 TB

Institucional recomendado: core compacto + sidecars + lineage
  incremento esperado: +150 GB a +450 GB

Muy eficiente: materializacion por ventanas/eventos + sidecars bajo demanda
  incremento esperado: +80 GB a +250 GB
```

### Target

```text
target recomendado CAPA 1 materializada adicional: +150 GB a +450 GB
limite de alerta: >700 GB
mala senal: acercarse a +1 TB salvo justificacion explicita
```

### Reglas Para No Perder Informacion

1. No borrar raw/audited sources.
2. No copiar quotes/trades completos en master tables.
3. Guardar lineage hacia source files, dataset version y run_id.
4. Materializar microstructure por ventanas o agregados.
5. Mantener sidecars especializados.
6. Usar Parquet + ZSTD + tipos estrictos.
7. Particionar por `date/year/month/ticker` segun patron de consumo.
8. Separar features de labels.
9. Separar signal, execution, valuation y benchmark price views.
10. Mantener `data_quality_report` como evidencia, no como base de datos.

## Politica De Materializacion

Formato recomendado:

```text
parquet
compression = zstd
dictionary_encoding = true para categoricas
```

Tipos recomendados:

```text
ticker/instrument_id: dictionary/string controlado
date: date32
timestamp: timestamp[us/ns, UTC declarado]
flags: bool/int8
categorias: dictionary
price: float32 o decimal segun precision requerida por policy
volume/size: int64
quality_state: dictionary
```

Particionado recomendado:

```text
master_daily_table/year=YYYY/
master_intraday_bar_table/year=YYYY/month=MM/
microstructure_features_table/year=YYYY/month=MM/date=YYYY-MM-DD/
dataset_certification_matrix/family=.../version=.../
```

No usar una particion que produzca millones de ficheros minusculos sin plan de
compaction.

## Campos Minimos Transversales

Toda tabla materializada de CAPA 1 debe incluir o poder enlazar:

```text
dataset_version
source_dataset
source_root
build_run_id
quality_policy_version
schema_version
price_view si aplica
as_of_semantics si aplica
created_at/build_timestamp
```

## Reglas De Consumo Downstream

### Event Engine

Consume:

```text
instrument_master
market_calendar
corporate_actions_table
master_daily_table
daily_scanner_candidates_table
master_intraday_bar_table
real_time_corporate_event_alerts_table
halts_table
event_windows_table
dataset_certification_matrix
```

Consulta bajo demanda:

```text
microstructure_features_table
news_context_table
short_context_table
short_sale_constraints_table
regime_context_table
fundamentals_asof_table
```

### Outcome Research

Consume:

```text
event_table
event_windows_table
outcomes_table
master_daily_table
master_intraday_bar_table
corporate_actions_table
halts_table
```

Regla:

```text
outcome no debe usar informacion posterior como feature pre-evento.
```

### Strategy Research

Consume:

```text
event_table
outcome_table
outcomes_table
event_windows_table
master_intraday_bar_table
microstructure_features_table
real_time_corporate_event_alerts_table
short_sale_constraints_table
halts_table
```

Regla:

```text
senal puede vivir en adjusted/split-normalized; ejecucion debe mirar raw
quotes/trades o features derivadas de raw.
```

### ML / Offline RL

Consume:

```text
features as-of
labels/outcomes separados
quality flags
instrument identity
regime context
execution feasibility
short-sale constraints when legally as-of
```

Regla:

```text
labels no pueden mezclarse con features.
```

## State Composition Contract

La composicion de `market_state_table` y `event_state_table` queda gobernada
por:

```text
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
```

Runbook de continuidad y build-loop skeleton:

```text
01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
```

Politica obligatoria de cobertura, scanner diario y lookbacks:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

Contrato objetivo del scanner diario/candidate set:

```text
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

Lectura institucional:

```text
context tables != final state
```

Un estado solo existe institucionalmente cuando un builder declara:

- `decision_timestamp_utc`;
- as-of policy por componente;
- source/manifest lineage;
- component quality gates;
- feature namespace version;
- separacion explicita entre features y labels;
- prohibicion de outcomes/rewards inline;
- leakage/adversarial validation.

Por tanto, los outputs ya materializados pueden ser componentes, pero no son
por si solos `market_state_table` ni `event_state_table`.

Estado actual del stack skeleton:

```text
schema contracts: defined
dataset contracts: defined
consumption policies: defined
validator contracts: defined
registry target entries: defined_not_materialized
official builder status: not implemented
candidate builder status: controlled_candidate implemented
fixture builder status: deterministic_fixture_only implemented
fixture configs: defined
test status: contract consistency + adversarial leakage fixtures + controlled candidate materialization passed
market_state_table_v0_1 materialized: false
event_state_table_v0_1 materialized: false
market_state_table_v0_1_candidate materialized: true
event_state_table_v0_1_candidate materialized: true
```

Evidencia fixture loop:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
tests = 14
passed = 14
failed = 0
skipped = 0
```

Lectura obligatoria:

```text
Los builders actuales conservan el modo fixture JSONL bajo
C:/TSIS_Data/tests/test_runs/.
Tambien pueden escribir controlled candidates bajo
E:/TSIS/data/data_foundation_outputs/.
No escriben ni promocionan el parquet oficial market_state_table_v0_1 ni
event_state_table_v0_1.
No habilitan ML/RL/backtest/execution directos.
```

Evidencia controlled candidate loop:

```text
market_state_candidate:
  dataset: E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
  manifest: E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
  rows: 50
  tickers: 9
  event_windows: 50
  valid_for_event_context_candidate_rows: 50
  valid_for_ml_feature_candidate_rows: 0
  valid_for_rl_state_candidate_rows: 0
  full_universe_claim_rows: 0

event_state_candidate:
  dataset: E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
  manifest: E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
  rows: 50
  tickers: 9
  event_windows: 50
  pre_event_rows: 25
  post_event_review_rows: 25
  valid_for_pattern_discovery_rows: 50
  valid_for_ml_feature_candidate_rows: 0
  valid_for_rl_state_candidate_rows: 0
  full_universe_claim_rows: 0

tests:
  python -m pytest tests/data_foundation_outputs/test_market_state_table_contract.py tests/data_foundation_outputs/test_event_state_table_contract.py -q
  passed = 16
  failed = 0
```

El fixture loop prueba que se bloquean:

- `*_as_of_utc > decision_timestamp_utc`;
- prefijos de labels/outcomes/rewards/future/signal/strategy/action/policy/
  fill/pnl dentro del estado;
- `post_event_review` usado como feature candidata ML.

## Promotion Barrier

Ningun output de este documento queda materializado o institucional solo por
estar descrito aqui.

Para pasar a `validated` o `institutional`, cada output necesita:

```text
canonical schema
dataset registry entry
data consumption policy
validator
profiling fisico
quality report
manifest/run_id
changelog
Graphify refresh queue si altera el mapa semantico
```

## Work Order Recomendado

1. `instrument_master`
2. `corporate_actions_table`
3. `market_calendar` + `expected_data_calendar`
4. `dataset_certification_matrix`
5. `master_daily_table`
6. `daily_scanner_candidates_table`
7. `master_intraday_bar_table`
8. `microstructure_features_table`
9. `halts_table`
10. `event_windows_table`
11. `outcomes_table`
12. `real_time_corporate_event_alerts_table`
13. `fundamentals_asof_table`
14. `news_context_table`
15. `short_context_table`
16. `short_sale_constraints_table`
17. `regime_context_table`

Estado actual de esta lista:

```text
All listed outputs except `daily_scanner_candidates_table`,
`real_time_corporate_event_alerts_table` and `short_sale_constraints_table` are
materialized for their declared v0.1 scopes.
```

## Next Materialization Priority After Current v0.1 Stack

La siguiente prioridad no es materializar `market_state_table` y
`event_state_table` directamente.

Orden operativo recomendado:

```text
1. daily_scanner_candidates_table controlled historical replay
2. master_intraday_bar_table wider/full-scope materialization plan
3. microstructure_features_table multi-window/multi-event materialization plan
4. market_state_table controlled real sample
5. event_state_table controlled real sample
6. short_sale_constraints_table after SSR/borrow/locate source acquisition
7. real_time_corporate_event_alerts_table after live/vendor latency contract
```

Motivo:

```text
market_state_table y event_state_table son composiciones de estado.
No deben promocionarse sobre una base intradia/microestructural debil.
Tampoco deben promocionarse como ticker-dia aislado: deben declarar scanner,
denominador, lookback policy y memoria historica as-of cuando la estrategia lo
requiera.
```

Regla para comenzar una materializacion amplia/full-universe:

```text
No se lanza full-universe ciego.
```

Cada tabla debe tener antes:

- source root oficial o paridad documentada;
- scope/denominador declarados;
- manifest policy;
- recomputation test desde raw/source;
- quality gates;
- `full_universe_claim` explicito;
- evidencia de tests;
- changelog, registry y Graphify queue actualizados.

Lectura por tabla:

- `daily_scanner_candidates_table`: primera candidata de este loop porque
  define el candidate set/in-play discovery que usaran los builders de estado.
  No requiere copiar quotes/trades completos ni esperar la promocion final de
  microestructura. Debe empezar con replay historico controlado, scanner
  definition config, manifest, summary, validators y `full_universe_claim=false`
  salvo denominador probado. El primer replay debe ejecutar como minimo
  `trade_station_like_scanner_v0_1` y
  `broad_in_play_discovery_scanner_v0_1`, preservando candidatos vistos por el
  scanner operativo, candidatos solo vistos por discovery amplio, razones de
  inclusion y evidencia de casos que el filtro `volume_today > 500000` o el
  ranking `% change 1D` habrian detectado tarde. El contrato objetivo vive en
  `01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md`.
  El contrato de definiciones vive en
  `01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md`.
- `master_intraday_bar_table`: siguiente candidata para ampliar cobertura porque
  ya existe pipeline piloto y runbook de normalizacion 1m. El loop operativo
  queda definido en
  `01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md`.
  Ese plan exige primero smoke split-safe, denominador, manifest, candidate
  output, builder parametrizado, tests y gates de promocion. El smoke
  split-safe ya paso en
  `runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_153012/`
  con `scan_strategy = split_tickers_then_partition_direct`; no autoriza
  reutilizar `master_intraday_bar_table_v0_1` como full-universe.
  Decision operativa `2026-06-29`: se anade la subruta
  `master_intraday_bar_table_v0_2_candidate_quote_guarded` para la vista
  quote-guarded. Esta subruta queda bloqueada hasta que el output final
  `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/` tenga repair
  manifest y validacion final. El bridge actual usa `D:/quotes` solo como
  lineage provisional candidate-only.
- `microstructure_features_table`: no debe ampliarse como tick-by-tick ciego
  para todo minuto/ticker; primero debe materializar ventanas gobernadas de
  eventos y decision timestamps. El loop operativo queda definido en
  `01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md`.
  Ese plan exige denominador de `event_windows_table`, estado explicito de la
  raiz quotes (`E:/TSIS/data/quotes_` oficial objetivo o `D:/quotes` candidato
  provisional), output candidate-only, builder parametrizado, recomputacion
  desde raw quotes/trades y evidencia visual/forense antes de promocionar. El
  primer subpaso ya existe como manifest builder:
  `scripts/build_microstructure_candidate_window_manifest.py`; ademas
  `scripts/materialize_microstructure_features_table.py` ya soporta un path
  candidato parametrizado probado bajo `C:/TSIS_Data/tests/test_runs/...`. La
  primera evidencia visual/forense de 6 filas vive en
  `01_foundations/inspection_dossiers/microstructure_features/` y el notebook
  humano companion vive en
  `01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb`.
  No escribe parquet oficial ni autoriza promocion. Decision operativa
  `2026-06-29`: para no bloquear el loop controlado de estados, `D:/quotes`
  queda aceptado como raiz provisional candidate-only mientras continua la
  clonacion/auditoria hacia la raiz oficial objetivo `E:/TSIS/data/quotes_`.
  `E:/TSIS/data/quotes` queda como raiz E incompleta/legacy. Cualquier
  candidato que herede esa raiz debe declarar
  `quotes_root_state=provisional_d_legacy_recovery_root_pending_e_parity` y
  `requires_rebuild_after_e_quotes_parity=true`.
- `market_state_table` / `event_state_table`: deben esperar a tener componentes
  intradia/microestructura mas defendibles.
- `short_sale_constraints_table`: bloqueada por falta de fuente SSR/borrow/
  locate/availability oficial, broker o vendor.
- `real_time_corporate_event_alerts_table`: bloqueada por contrato live/vendor,
  latency semantics y received-time lineage.

Motivo:

```text
primero identidad, calendario, actions y calidad;
despues precio diario/intradia;
despues microestructura, alertas corporativas live y contexto;
despues consumo por eventos, outcomes, strategy, ML/RL.
```

## Regla Final

Estas tablas existen para que un evento tenga un estado defendible.

No existen para duplicar toda la historia.
No existen para esconder informacion.
No existen para mezclar eventos, estrategias y outcomes.

La arquitectura correcta es:

```text
raw/audited truth
  -> governed compact outputs
  -> event-state reconstruction
  -> market_state_table / event_state_table under composition contract
  -> event_table downstream
  -> outcome/strategy/ML/execution/RL
```

Si un futuro agente no puede explicar que hace una tabla cuando aparece un
evento concreto, esa tabla todavia no esta suficientemente bien definida.
