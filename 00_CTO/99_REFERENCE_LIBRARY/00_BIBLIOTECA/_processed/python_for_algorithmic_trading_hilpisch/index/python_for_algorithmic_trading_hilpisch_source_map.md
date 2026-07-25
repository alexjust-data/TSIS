# Source Map - Python for Algorithmic Trading

**book_id:** `python_for_algorithmic_trading_hilpisch`  
**Funcion real:** puente practico Python entre research, event-based backtesting, streaming y automatizacion.

| Componente TSIS | Que aporta este libro | Seccion/Paginas | Prioridad |
|---|---|---:|---|
| `DevEnvironment` | conda, environments, Docker, cloud/Jupyter | Ch. 2 / 57-93 | Alta |
| `RunManifest` | registrar entorno, parametros, librerias, modelo persistido | Ch. 2, Ch. 10 / 57-93, 483-491 | Alta |
| `DataFoundation` | clasificacion de datos y lectura con pandas/APIs | Ch. 3 / 95-126 | Alta |
| `DataCatalog` | HDF5/TsTables/SQLite, write once read many | Ch. 3 / 126-143 | Alta |
| `HistoricalDataAdapter` | lectura de historico desde CSV/API | Ch. 3-4 / 95-207 | Media |
| `ResearchPrototype` | vectorized backtesting con pandas | Ch. 4 / 147-207 | Alta |
| `FeaturePipeline` | returns, rolling features, lagged features, normalization | Ch. 4-5, Ch. 10 / 147-310, 467-471 | Alta |
| `Validation` | data snooping, overfitting, train/test split | Ch. 4-5 / 207-310 | Alta |
| `EventLoop` | loops event-based sobre barras | Ch. 6 / 314-345 | Alta |
| `CostModel` | fixed/proportional transaction costs | Ch. 6 / 318-328 | Alta |
| `Order` | buy/sell order methods, although simplified | Ch. 6 / 320-322 | Media |
| `ExecutionSimulator` | immediate execution baseline | Ch. 6 / 320-322 | Media |
| `Accounting` | cash, units, net wealth, close out | Ch. 6 / 318-323 | Alta |
| `Portfolio` | position, units, long-only/long-short transitions | Ch. 6 / 325-335 | Alta |
| `LiveDataAdapter` | ZeroMQ PUB/SUB tick stream | Ch. 7 / 348-357 | Alta |
| `OnlineStateBuilder` | collect ticks, resample bars, compute returns/momentum | Ch. 7 / 358-362 | Critica |
| `DecisionPolicy` | online signal generation from resampled bars | Ch. 7 / 358-362 | Alta |
| `BrokerAdapter` | Oanda/FXCM examples | Ch. 8-9 / 376-444 | Media |
| `ModelRegistry` | persist model + normalization parameters | Ch. 10 / 483-486 | Alta |
| `Deployment` | remote server/cloud setup | Ch. 10 / 491-504 | Media |
| `Logging` | persistent runtime information | Ch. 10 / 491-495 | Alta |
| `Monitoring` | real-time local monitoring from remote process | Ch. 7, Ch. 10 / 362-370, 491-509 | Alta |
| `Risk` | Kelly, drawdown, VaR, leverage warnings | Ch. 10 / 446-483 | Alta |

## Adaptacion Recomendada Para TSIS

No copiar el motor del capitulo 6 como arquitectura final. Extraer:

```text
BacktestBase.cash/units/trades     -> AccountingLedger
ftc/ptc                            -> CostModel
for bar in range(...)              -> Clock/EventLoop
place_buy_order/place_sell_order   -> OrderIntent -> OMS -> Fill
online algorithm                   -> same DecisionPolicy under streaming adapter
logging/monitoring                 -> mandatory audit/observability
```

## Prioridad De Lectura

```text
1. Ch. 6, paginas 314-345 - clases event-based
2. Ch. 7, paginas 348-374 - streaming y online algorithms
3. Ch. 10, paginas 463-509 - offline -> online, logging, monitoring
4. Ch. 4, paginas 147-210 - vectorized research y overfitting
5. Ch. 3, paginas 95-143 - datos y storage
6. Ch. 2, paginas 57-93 - entorno reproducible
```
