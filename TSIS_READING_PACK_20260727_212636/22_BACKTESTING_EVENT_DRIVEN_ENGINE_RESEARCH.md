# Backtesting Event-Driven Profesional En Python

Investigacion y nota de arquitectura para TSIS. Fecha: 22 de julio de 2026.

## Referencias Mejores Para Motor Event-Driven

1. **NautilusTrader**  
   Probablemente la referencia open-source mas seria hoy para estudiar arquitectura moderna: motor event-driven, backtest/live con la misma semantica, catalogo Parquet, ejecucion, portfolio, risk y adapters. Aunque el core es Rust, Python se usa como plano de control.  
   Fuente: [NautilusTrader docs](https://nautilustrader.io/docs/latest/)

2. **QuantConnect LEAN**  
   La referencia institucional open-source mas madura. Core en C#, pero permite algoritmos Python. Estudia su arquitectura: `AlgorithmManager`, `DataFeed`, `TimeSlice`, `TransactionHandler`, `Portfolio`, `Security`, `Brokerage`, scheduled events, live/backtest.  
   Fuente: [LEAN Algorithm Engine](https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/algorithm-engine)

3. **Zipline / zipline-reloaded**  
   Buen modelo Python puro para entender backtesting stream-based: `initialize`, `handle_data`, bundles, slippage, transaction costs, order delay. No lo tomaria como arquitectura final para small caps profesional, pero si como API pedagogica.  
   Fuente: [Zipline docs](https://zipline.ml4trading.io/beginner-tutorial.html)

4. **Backtrader**  
   Excelente para aprender ciclo de estrategia, broker simulado, lifecycle de ordenes y eventos. Limitacion importante: su broker de backtesting por defecto no modela volumen de forma realista, lo que es peligroso para small caps.  
   Fuente: [Backtrader orders](https://www.backtrader.com/docu/order-creation-execution/order-creation-execution/)

5. **HftBacktest**  
   Muy util si quieres bajar a tick/L2: replay de order book, latencias, queue position y fills. Ojo: documenta explicitamente que no modela market impact en replay, asi que tus ordenes deben ser pequenas frente al mercado.  
   Fuente: [HftBacktest docs](https://hft.readthedocs.io/en/latest/)

6. **ABIDES / ABIDES-Markets**  
   No es un backtester historico clasico, sino un simulador discreto multiagente de mercado. Sirve para entender exchange simulation, message passing, latencias y limit order book.  
   Fuente: [ABIDES GitHub](https://github.com/abides-sim/abides), [JPMorgan ABIDES](https://github.com/jpmorganchase/abides-jpmc-public)

## Libros De Arquitectura Que Si Aplican

7. **Harry Percival & Bob Gregory, _Architecture Patterns with Python_**  
   Para implementar bien en Python: domain model, repository, unit of work, message bus, domain events, ports/adapters. Muy relevante para disenar tu motor sin convertirlo en un script gigante.  
   Fuente: [Cosmic Python](https://www.cosmicpython.com/)

8. **Martin Kleppmann, _Designing Data-Intensive Applications_**  
   Para almacenamiento, replay determinista, logs de eventos, tolerancia a fallos, sistemas de datos, reproducibilidad y pipelines.  
   Fuente: [DDIA](https://martin.kleppmann.com/2017/03/27/designing-data-intensive-applications.html)

9. **Martin Fowler, _Patterns of Enterprise Application Architecture_**  
   Repository, Unit of Work, Domain Model, Service Layer. Estos patrones encajan muy bien con `DataCatalog`, `OrderRepository`, `PortfolioService`, `ExecutionService`.  
   Fuente: [Fowler P of EAA](https://martinfowler.com/books/eaa.html)

10. **Hohpe & Woolf, _Enterprise Integration Patterns_**  
    Para message bus, event channels, routing, queues y patrones de integracion. Muy util si separas data replay, OMS, risk, broker y reporting.  
    Fuente: [Enterprise Integration Patterns](https://martinfowler.com/books/eip.html)

## Blueprint Minimo Del Motor

Un motor event-driven serio deberia tener estos modulos:

```text
DataCatalog -> Clock/EventLoop -> EventBus -> Strategy
                                  |
                                  v
                           Risk / OMS / BrokerSim
                                  |
                                  v
                         Portfolio / Accounting
                                  |
                                  v
                         EventLog / Metrics / Reports
```

Eventos minimos:

```text
MarketDataEvent
QuoteEvent
BarEvent
CorporateActionEvent
SignalEvent
OrderIntent
OrderSubmitted
OrderAccepted
OrderRejected
OrderCancelled
FillEvent
PositionEvent
PortfolioValuationEvent
TimerEvent
```

Para small caps, el motor no puede limitarse a OHLCV. Necesitas:

- bid/ask o proxy de spread
- halts y suspensiones
- partial fills
- participacion maxima sobre volumen
- ADV y dollar volume
- no-trade days
- delistings
- splits/dividends point-in-time
- borrow availability/cost si haces shorts
- ordenes que no se ejecutan magicamente en el close
- event log reproducible con IDs deterministas

## Conclusion Tecnica

La biblioteca de validacion estadistica responde a:

```text
Como evito creer que una estrategia funciona cuando en realidad esta sobreajustada?
```

Esta segunda lista responde a:

```text
Como construyo el sistema?
```

Para TSIS, el camino recomendado es usar **LEAN y NautilusTrader como planos de arquitectura**, **Architecture Patterns with Python** como guia de implementacion Python, y construir un motor propio estrecho para small caps con Parquet/DuckDB/Polars, no un clon generico de Backtrader.

## Addendum TSIS: Camino B

La idea operativa es:

```text
Camino B - Backtester propio en Python
```

Ventajas:

- control total
- integracion natural con TSIS
- snapshots del estado
- trazabilidad
- adaptacion a datos Polygon/DAS
- misma semantica historica y online

Inconvenientes:

- debes implementar y verificar muchas piezas
- mayor riesgo de errores
- mas tests y tiempo

## Guia Principal Para Empezar

Si hay que escoger una guia practica para comenzar a aterrizar el motor en el PC, la fuente mas directa es:

**Michael Halls-Moore / QuantStart, "Event-Driven Backtesting with Python"**  
Fuente: [QuantStart Part I](https://www.quantstart.com/articles/Event-Driven-Backtesting-with-Python-Part-I/)

Por que:

- define los componentes correctos: `Event`, `EventQueue`, `DataHandler`, `Strategy`, `Portfolio`, `ExecutionHandler`, `Loop`
- separa historico y live mediante interfaces comunes
- evita lookahead bias mediante drip-feed de datos
- muestra el flujo `MARKET -> SIGNAL -> ORDER -> FILL`
- es pequeno suficiente para convertirse en un vertical slice TSIS v0.1

Limitacion:

- es una arquitectura pedagogica, no small-caps-grade
- hay que sustituir CSV/pandas por Parquet/DuckDB/Polars
- hay que separar `Portfolio`, `OMS`, `Risk`, `BrokerSim`, `Ledger` y snapshots con mas rigor
- hay que endurecer fill model, corporate actions, halts y trazabilidad

## Libro Principal Complementario

**Yves Hilpisch, _Python for Algorithmic Trading_**, especialmente el capitulo 6, "Building Classes for Event-Based Backtesting".  
Fuente: [O'Reilly](https://www.oreilly.com/library/view/python-for-algorithmic/9781492053347/)

Uso recomendado:

- tomarlo como puente practico entre Python financiero y backtesting event-based
- no tomarlo como arquitectura final de TSIS
- adaptar solo las ideas utiles: clases, event loop, separacion estrategia/backtest, streaming basico

## Manual De Arquitectura Python

**Harry Percival & Bob Gregory, _Architecture Patterns with Python_**  
Fuente: [Cosmic Python](https://www.cosmicpython.com/)

Uso recomendado:

- aplicar `domain model`
- aplicar `message bus`
- aplicar `repository`
- aplicar `unit of work` cuando haya persistencia
- aplicar `ports/adapters` para separar Polygon, DAS, Parquet y BrokerSim

## Orden De Trabajo Recomendado

```text
1. Leer QuantStart Event-Driven Backtesting with Python.
2. Implementar un vertical slice TSIS_BACKTEST_ENGINE_V0_1.
3. Leer Hilpisch capitulo 6 para comparar una implementacion alternativa.
4. Leer NautilusTrader Architecture para endurecer componentes.
5. Usar LEAN como referencia de motor maduro.
6. Solo despues incorporar Lopez de Prado, PBO, DSR y validacion avanzada.
```

## Vertical Slice TSIS_BACKTEST_ENGINE_V0_1

Objetivo de aceptacion:

```text
Una estrategia clasica debe producir decisiones reproducibles sobre datos historicos,
guardar la representacion del mercado en cada decision y ejecutarse posteriormente
mediante replay usando el mismo nucleo decisional.
```

Componentes minimos:

```text
HistoricalDataFeed
Clock / EventLoop
EventBus
Strategy
Signal
Order
ExecutionSimulator
Position
Portfolio
Risk
Ledger
Metrics
MarketStateSnapshot
EventStateSnapshot
DecisionRecord
RunManifest
```

Artefactos minimos:

```text
signals.parquet
orders.parquet
fills.parquet
positions.parquet
trades.parquet
decision_snapshots.parquet
equity_curve.parquet
run_manifest.json
```

La decision practica es empezar a implementar ya con una guia pequena y verificable, no esperar a dominar toda la literatura academica.
