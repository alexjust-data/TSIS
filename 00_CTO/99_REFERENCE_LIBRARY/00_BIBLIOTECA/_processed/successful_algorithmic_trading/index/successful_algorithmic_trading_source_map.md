# Source Map - Successful Algorithmic Trading

**book_id:** `successful_algorithmic_trading`  
**Funcion real:** fuente pedagogica para construir el primer motor event-driven Python de TSIS.

| Componente TSIS | Que aporta este libro | Seccion/Paginas | Prioridad |
|---|---|---:|---|
| `ResearchSpec` | Necesidad de hipotesis, parametros y evaluacion disciplinada | Ch. 3, Ch. 16 / 24-29, 190-203 | Alta |
| `RunManifest` | Implicito en optimizacion y reproducibilidad de variantes | Ch. 16 / 190-203 | Alta |
| `DataFoundation` | Securities master, vendors, symbols, exchanges, prices | Ch. 7 / 56-69 | Alta |
| `SymbolIdentity` | Problemas de tickers, vendor mappings y bankruptcies | Ch. 7 / 59 | Alta |
| `CorporateActions` | Necesidad de almacenar splits/dividends | Ch. 7 / 59 | Alta |
| `HistoricalDataAdapter` | Data handler historico con drip-feed | Ch. 14 / 144-149 | Critica |
| `ReplayDataAdapter` | Derivado del mismo patron `DataHandler` | Ch. 14 / 144-149 | Alta |
| `LiveDASAdapter` | Sustituir live feed sin cambiar strategy/portfolio | Ch. 14 / 144, 170 | Alta |
| `Clock` | Heartbeat temporal del backtest/live | Ch. 14 / 161-164 | Critica |
| `EventLoop` | Loop externo e interno que procesa cola | Ch. 14 / 161-164 | Critica |
| `EventQueue` | Cola de comunicacion `Market/Signal/Order/Fill` | Ch. 14 / 140-164 | Critica |
| `EventBus` | No formalizado, pero inferible de cola de eventos | Ch. 14 / 140-164 | Alta |
| `MarketDataEvent` | `MarketEvent` como nueva barra/dato | Ch. 14 / 140-141 | Critica |
| `QuoteEvent` | No cubierto; extender desde data frequency/order book | Ch. 8 / 72-73 | Media |
| `TradeEvent` | No cubierto; extender desde tick data | Ch. 8 / 72-73 | Media |
| `OnlineStateBuilder` | No formalizado; debe derivarse del drip-feed sin lookahead | Ch. 3, Ch. 14 / 25-26, 144-149 | Alta |
| `MarketStateSnapshot` | No cubierto; extension TSIS necesaria | Ch. 14 / 144-149 | Alta |
| `EventStateSnapshot` | No cubierto; extension TSIS necesaria | Ch. 14 / 149-151 | Alta |
| `EventDetection` | No separado; se mezcla dentro de Strategy | Ch. 15 / 172-188 | Media |
| `Strategy` | Interfaz abstracta y ejemplos concretos | Ch. 14-15 / 149-188 | Critica |
| `DecisionPolicy` | Inferible desde `calculate_signals` | Ch. 14-15 / 149-188 | Alta |
| `Signal` | `SignalEvent` con strategy_id, symbol, datetime, direction, strength | Ch. 14 / 141 | Critica |
| `PortfolioConstruction` | Portfolio convierte signal en order, aunque de forma naive | Ch. 14 / 151-158 | Alta |
| `PreTradeRisk` | Mencionado como mejora pendiente; no implementado | Ch. 13-14 / 128-133, 151 | Media |
| `OMS` | Parcialmente mezclado en Portfolio | Ch. 14 / 151-158 | Alta |
| `Order` | `OrderEvent` basico con symbol, type, quantity, direction | Ch. 14 / 142 | Critica |
| `OrderEvent` | Evento de orden teorica | Ch. 14 / 142 | Critica |
| `ExecutionSimulator` | `SimulatedExecutionHandler`, baseline simple | Ch. 14 / 159-160 | Critica |
| `BrokerAdapter` | `IBExecutionHandler` como ejemplo live | Ch. 14 / 164-170 | Alta |
| `Fill` | `FillEvent` con timestamp, symbol, exchange, qty, direction, cost, commission | Ch. 14 / 142-143 | Critica |
| `Accounting` | Actualizacion de cash, commission, holdings, total | Ch. 14 / 153-158 | Alta |
| `Portfolio` | Positions/holdings/equity curve | Ch. 14 / 151-158 | Alta |
| `PostTradeRisk` | No separado; desarrollar para TSIS | Ch. 13 / 128-133 | Media |
| `Ledger` | Impl. basica como lists/dataframes/equity.csv | Ch. 14 / 151-164 | Alta |
| `Metrics` | Sharpe, drawdown, returns, trade analysis | Ch. 12 / 118-127 | Alta |
| `Validation` | Biases, cross-validation, overfitting, grid search | Ch. 3, Ch. 16 / 24-29, 190-203 | Alta |
| `Report` | Performance plots and summary stats | Ch. 12, Ch. 15 / 118-127, 188-189 | Media |

## Adaptacion Recomendada Para TSIS

Copiar el patron, no el codigo literal:

```text
Event classes       -> dataclasses/pydantic models versionados
Queue               -> deterministic event queue con prioridad temporal
DataHandler         -> Parquet/DuckDB/Polars adapters
Strategy            -> DecisionPolicy + EventDetection separados
Portfolio           -> PortfolioConstruction + Risk + OMS + Accounting separados
ExecutionHandler    -> SimulatedVenue + DASBrokerAdapter
equity.csv          -> Parquet ledgers + run_manifest.json
```

## Prioridad De Lectura

Para construir `BACKTEST_VERTICAL_SLICE_V0_1`, leer en este orden:

```text
1. Ch. 14, paginas 138-164 - motor event-driven
2. Ch. 3, paginas 24-29 - sesgos y costes
3. Ch. 7-8, paginas 56-84 - datos
4. Ch. 12-13, paginas 118-133 - metrics y risk
5. Ch. 15, paginas 172-176 - estrategia simple smoke test
6. Ch. 16, paginas 190-203 - experimentos y optimizacion
```
