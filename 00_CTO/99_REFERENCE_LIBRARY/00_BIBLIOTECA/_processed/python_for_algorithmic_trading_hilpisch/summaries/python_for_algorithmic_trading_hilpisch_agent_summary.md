# Python for Algorithmic Trading

**book_id:** `python_for_algorithmic_trading_hilpisch`  
**Fuente:** `Python_for_Algorithmic_Trading_-_Yves_Hilpisch.pdf`  
**Autor:** Yves Hilpisch  
**Paginas PDF:** 616  
**Estado:** resumen agent-readable v0.1  
**Uso principal en TSIS:** puente practico entre Python financiero, datos, backtesting vectorizado, backtesting event-based, streaming online y automatizacion live.

## Menu Rapido

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Para Que Sirve En TSIS](#para-que-sirve-en-tsis)
- [Mapa Del Libro](#mapa-del-libro)
- [Capitulo 2 - Python Infrastructure](#capitulo-2---python-infrastructure)
- [Capitulo 3 - Working With Financial Data](#capitulo-3---working-with-financial-data)
- [Capitulo 4 - Mastering Vectorized Backtesting](#capitulo-4---mastering-vectorized-backtesting)
- [Capitulo 5 - Predicting Market Movements With ML](#capitulo-5---predicting-market-movements-with-ml)
- [Capitulo 6 - Building Classes For Event-Based Backtesting](#capitulo-6---building-classes-for-event-based-backtesting)
- [Capitulo 7 - Real-Time Data And Sockets](#capitulo-7---real-time-data-and-sockets)
- [Capitulos 8-9 - Broker APIs](#capitulos-8-9---broker-apis)
- [Capitulo 10 - Automating Trading Operations](#capitulo-10---automating-trading-operations)
- [Arquitectura Extraible Para TSIS](#arquitectura-extraible-para-tsis)
- [Indice Para Agentes](#indice-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen Ejecutivo

Este libro es una guia practica para construir el entorno Python de un sistema de trading, probar ideas con backtesting vectorizado, pasar a clases de backtesting event-based, consumir datos streaming y desplegar una estrategia automatizada. Para TSIS, su funcion no es definir una arquitectura profesional completa de OMS/execution, sino aterrizar en codigo Python varias piezas que rodean al motor:

```text
environment -> data IO/storage -> vectorized research -> event-based classes -> sockets/online algorithm -> deployment/logging
```

El capitulo mas relevante para el motor es el **capitulo 6**, que implementa clases de backtesting event-based (`BacktestBase`, `BacktestLongOnly`, `BacktestLongShort`). El capitulo 7 explica streaming y online algorithms. El capitulo 10 muestra como convertir un modelo offline en una estrategia online con broker API, logging y monitoring. El capitulo 4 es util para research rapido, pero no sustituye el motor event-driven.

## Para Que Sirve En TSIS

Usar este libro para:

- definir entorno Python reproducible
- trabajar con CSV, HDF5, SQLite y APIs de datos
- entender el rol de vectorized backtesting como fase de research
- ver por que event-based backtesting supera a vectorizado para costes fijos, path dependency y online parity
- implementar una base Python sencilla con cash, units, position, trades, fixed/proportional transaction costs
- convertir algoritmos offline en online algorithms
- entender sockets, PUB/SUB, tick server/client y resampling streaming
- crear logging y monitoring para despliegue

No usar este libro como:

- especificacion final de `TSIS_BACKTEST_ENGINE`
- OMS profesional
- modelo realista de fills en small caps
- sustituto de NautilusTrader/LEAN para arquitectura
- sustituto de Harris para ejecucion realista
- sustituto de Lopez de Prado para validacion cientifica avanzada

## Mapa Del Libro

| Capitulo | Paginas PDF | Para que sirve |
|---|---:|---|
| Preface | 16-29 | Alcance, audiencia y estructura |
| 1. Python and Algorithmic Trading | 31-54 | Contexto, Python, estrategias basicas |
| 2. Python Infrastructure | 57-93 | Conda, environments, Docker, cloud instances, Jupyter |
| 3. Working with Financial Data | 95-144 | Lectura, APIs, HDF5/TsTables/SQLite, almacenamiento |
| 4. Mastering Vectorized Backtesting | 147-219 | Research vectorizado, SMA, momentum, mean reversion, overfitting |
| 5. Predicting Market Movements with ML | 223-310 | Regression/classification/deep learning y backtests vectorizados |
| 6. Building Classes for Event-Based Backtesting | 314-345 | Clases event-based, cash, orders, transaction costs, long-only/long-short |
| 7. Working with Real-Time Data and Sockets | 348-374 | ZeroMQ, tick server/client, online signals, streaming visualization |
| 8. CFD Trading with Oanda | 376-417 | API broker, historico, streaming, market orders |
| 9. FX Trading with FXCM | 420-444 | API broker alternativa, tick/candles/orders |
| 10. Automating Trading Operations | 445-514 | capital management, ML online, deployment, logging, monitoring |
| Appendix | 515-578 | Python, NumPy, matplotlib, pandas |

## Capitulo 2 - Python Infrastructure

**Paginas:** 57-93  
**Componentes TSIS relacionados:** `DevEnvironment`, `RunManifest`, `Deployment`, `Monitoring`

Resumen:

El capitulo cubre gestion de paquetes y entornos con conda, uso de Docker, uso de cloud instances y despliegue de Jupyter Lab seguro. La idea central para TSIS es que el entorno de research/backtest debe ser reproducible y aislado.

Ideas accionables para TSIS:

- fijar versiones de Python y librerias en un environment file
- registrar environment hash/version en `run_manifest.json`
- separar entorno research, backtest batch y live/shadow
- considerar Docker solo cuando aporte reproducibilidad/despliegue, no como complejidad inicial

## Capitulo 3 - Working With Financial Data

**Paginas:** 95-144  
**Componentes TSIS relacionados:** `DataFoundation`, `DataCatalog`, `HistoricalDataAdapter`, `DataValidation`

Resumen:

El capitulo organiza datos financieros en historico/real-time y estructurado/no estructurado. Muestra lectura desde CSV/pandas, APIs de datos y almacenamiento eficiente con HDF5, TsTables y SQLite. Su principio clave es "retrieve once, use multiple times" y "write once, read multiple times".

Ideas accionables para TSIS:

- usar este capitulo como apoyo para IO y almacenamiento, no como esquema final
- adaptar el principio a Parquet/DuckDB/Polars
- distinguir datos historicos estructurados, streaming real-time y datos no estructurados
- para tick data, usar storage particionado por tiempo y consultas por rango

## Capitulo 4 - Mastering Vectorized Backtesting

**Paginas:** 147-219  
**Componentes TSIS relacionados:** `ResearchNotebook`, `FeaturePipeline`, `VectorizedPrototype`, `Validation`

Resumen:

El capitulo muestra backtesting vectorizado con NumPy/pandas para SMA, momentum y mean reversion. Sirve para exploracion rapida de ideas y visualizacion. La estrategia genera `position`, calcula `returns`, aplica shift para evitar usar informacion futura y compara estrategia contra benchmark.

Punto importante:

```text
vectorized backtesting es excelente para research rapido,
pero tiene limites para costes fijos, path dependency, execution realism y live parity.
```

Ideas accionables para TSIS:

- usar vectorizado como capa de investigacion preliminar
- todo prototipo vectorizado que sobreviva debe migrar al motor event-driven
- registrar transaction costs desde la etapa de research
- overfitting/data snooping estan explicitamente advertidos en paginas 207-210

## Capitulo 5 - Predicting Market Movements With ML

**Paginas:** 223-310  
**Componentes TSIS relacionados:** `FeaturePipeline`, `ModelTraining`, `DecisionPolicy`, `Validation`

Resumen:

El capitulo usa regression, classification y deep learning para predecir niveles, retornos o direccion de mercado. Muestra backtesting vectorizado de modelos predictivos y clases para generalizar el enfoque.

Uso en TSIS:

- util como ejemplo de pipeline modelo -> prediccion -> posicion
- no usar como validacion ML final
- separar `ModelTraining` de `DecisionPolicy`
- guardar scaler/normalizacion junto con el modelo si se despliega online

## Capitulo 6 - Building Classes For Event-Based Backtesting

**Paginas:** 314-345  
**Componentes TSIS relacionados:** `BacktestBase`, `Order`, `Portfolio`, `Accounting`, `CostModel`

Resumen:

Este capitulo es el nucleo del libro para TSIS. Explica por que el vectorizado falla para ciertas realidades: lookahead, simplificaciones, costes fijos, instrumentos indivisibles y path dependency. Luego implementa clases event-based con loops sobre barras.

Clases:

| Clase | Funcion |
|---|---|
| `BacktestBase` | carga datos, mantiene cash, units, position, trades, costes y ordenes |
| `BacktestLongOnly` | implementa SMA, momentum y mean reversion long-only |
| `BacktestLongShort` | permite long/short, `go_long`, `go_short` y cierre de posiciones |

Conceptos extraibles:

- `initial_amount`
- `amount`
- `ftc` fixed transaction costs
- `ptc` proportional transaction costs
- `units`
- `position`
- `trades`
- `place_buy_order`
- `place_sell_order`
- `close_out`

Adaptacion TSIS:

```text
BacktestBase       -> no copiar como motor final; extraer accounting minimo
place_buy/sell     -> separar en Order + OMS + ExecutionSimulator
amount/units       -> llevar a Accounting/Portfolio
ftc/ptc            -> CostModel versionado
position           -> PositionLedger
loop over bars     -> Clock/EventLoop
```

## Capitulo 7 - Real-Time Data And Sockets

**Paginas:** 348-374  
**Componentes TSIS relacionados:** `LiveDataAdapter`, `OnlineAlgorithm`, `StreamingState`, `Monitoring`

Resumen:

El capitulo usa ZeroMQ para crear un tick server y clientes subscribers. Explica el patron PUB/SUB, recepcion de ticks, online algorithms, resampling a barras y generacion de senales en real time. Esto es valioso para TSIS porque muestra como pasar de datos incrementales a estado online.

Ideas accionables para TSIS:

- un algoritmo online solo conoce estado actual y pasado
- tick stream puede convertirse en bars mediante resampling
- usar la penultima barra completada para evitar operar con barra incompleta
- separar ingestion, state update, signal generation y order action

## Capitulos 8-9 - Broker APIs

**Paginas:** 376-444  
**Componentes TSIS relacionados:** `BrokerAdapter`, `HistoricalDataAdapter`, `StreamingDataAdapter`, `OrderGateway`

Resumen:

Los capitulos muestran integracion con Oanda y FXCM: obtener historico, recibir streaming data, colocar market orders y consultar cuenta. Aunque TSIS usara DAS/Polygon, estos capitulos son utiles como ejemplos de adaptadores externos.

Adaptacion TSIS:

- no copiar APIs Oanda/FXCM
- extraer patron `BrokerAdapter`
- mapear respuestas externas a eventos internos TSIS
- normalizar fills, account updates y order status

## Capitulo 10 - Automating Trading Operations

**Paginas:** 445-514  
**Componentes TSIS relacionados:** `CapitalManagement`, `OnlineAlgorithm`, `Deployment`, `Logging`, `Monitoring`, `Risk`

Resumen:

El capitulo junta varias piezas: capital management con Kelly, backtesting ML con costes, risk analysis, persistencia de modelo, transformacion offline -> online, deployment cloud, logging y monitoring. Para TSIS, lo mas importante no es la estrategia Oanda, sino el patron operativo:

```text
train offline -> persist model + normalization -> stream data -> build features online -> predict -> place orders -> log/monitor
```

Ideas accionables para TSIS:

- persistir modelo, parametros y normalizacion
- asegurar que online usa los mismos features que backtest
- guardar logs de ticks, bars, features, predictions, orders y fills
- implementar monitoring independiente del proceso de trading
- tratar leverage/Kelly como riesgo, no como recomendacion automatica

## Arquitectura Extraible Para TSIS

Flujo Hilpisch:

```text
DataFrame/CSV/API
  -> vectorized prototype
  -> BacktestBase event-based loop
  -> long-only / long-short subclasses
  -> socket streaming
  -> online algorithm
  -> broker API order
  -> logging/monitoring
```

Flujo TSIS recomendado:

```text
Parquet/DuckDB/Polars
  -> ResearchPrototype
  -> HistoricalDataAdapter
  -> Clock/EventLoop
  -> OnlineStateBuilder
  -> DecisionPolicy
  -> Signal
  -> PortfolioConstruction
  -> PreTradeRisk
  -> OMS
  -> ExecutionSimulator / DASBrokerAdapter
  -> Fill
  -> Accounting/Ledger
  -> Monitoring/Reports
```

## Indice Para Agentes

| Si buscas... | Mira | Paginas | Componente TSIS |
|---|---|---:|---|
| Entorno reproducible Python | Ch. 2 | 57-93 | `DevEnvironment` |
| Docker/cloud/Jupyter | Ch. 2 | 74-92 | `Deployment` |
| Leer datos financieros | Ch. 3 | 95-126 | `DataFoundation` |
| Storage eficiente | Ch. 3 | 126-143 | `DataCatalog` |
| Vectorized research | Ch. 4 | 147-207 | `ResearchPrototype` |
| Data snooping/overfitting | Ch. 4 | 207-210 | `Validation` |
| ML prediction pipeline | Ch. 5 | 223-310 | `ModelTraining` |
| Por que event-based | Ch. 6 | 314-317 | `EventLoop` |
| Backtest base class | Ch. 6 | 317-324 | `Accounting`, `CostModel` |
| Buy/sell order methods | Ch. 6 | 320-322 | `Order`, `ExecutionSimulator` |
| Long-only strategy class | Ch. 6 | 325-329 | smoke test |
| Long-short strategy class | Ch. 6 | 329-335 | `Position` |
| Sockets/PUB-SUB | Ch. 7 | 348-357 | `LiveDataAdapter` |
| Online algorithm | Ch. 7 | 358-362 | `OnlineStateBuilder`, `DecisionPolicy` |
| Streaming visualization | Ch. 7 | 362-370 | `Monitoring` |
| Broker API examples | Ch. 8-9 | 376-444 | `BrokerAdapter` |
| Offline -> online ML | Ch. 10 | 484-491 | `OnlineAlgorithm` |
| Logging/monitoring | Ch. 10 | 491-509 | `Monitoring`, `Ledger` |
| Risk analysis | Ch. 10 | 478-483 | `Risk`, `Metrics` |

## Limitaciones

- Usa APIs y librerias que pueden estar obsoletas o no ser aplicables a TSIS.
- El capitulo 6 no implementa una cola de eventos `Market/Signal/Order/Fill` tan clara como QuantStart.
- Los metodos `place_buy_order` y `place_sell_order` ejecutan inmediatamente y mezclan orden, fill y accounting.
- No modela liquidez, bid/ask real, partial fills, halts, borrow ni small caps.
- El backtesting vectorizado es util para research, pero peligroso como evidencia final.
- Kelly/leverage se presentan como herramientas analiticas; TSIS debe tratarlas con limites de riesgo conservadores.
