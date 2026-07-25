# Concept Index - Python for Algorithmic Trading Cookbook - Jason Strimpel

## Menu

- [Datos](#datos)
- [Research y backtesting](#research-y-backtesting)
- [Broker/live](#brokerlive)
- [Uso TSIS](#uso-tsis)

## Datos

| Concepto | Capitulo | Uso TSIS |
|---|---:|---|
| Nasdaq Data Link | 1 | `ExternalDataAdapter` |
| OpenBB stocks/futures/options | 1 | `MarketDataAdapterPrototype` |
| pandas returns/vol/resampling/missing data | 2 | `FeaturePipeline` |
| dashboards | 3 | `ResearchDashboard` |
| CSV/SQLite/PostgreSQL/HDF5 | 4 | `LocalDataStoreReference` |
| ArcticDB tick storage | 13 | `TickStoreReference` |

## Research y backtesting

| Concepto | Capitulo | Uso TSIS |
|---|---:|---|
| PCA | 5 | `FactorResearch` |
| Beta hedging | 5 | `FactorExposureModel` |
| Fama-French | 5 | `FactorValidation` |
| Zipline Pipeline | 5 | `PipelineReference` |
| VectorBT | 6 | `VectorizedPrototype` |
| Walk-forward optimization | 6 | `ParameterSearchPrototype` |
| Zipline Reloaded | 7 | `ReferenceEventBacktest` |
| Alphalens | 8 | `FactorPerformanceAnalytics` |
| Pyfolio | 9 | `RiskPerformanceAnalytics` |

## Broker/live

| Concepto | Capitulo | Uso TSIS |
|---|---:|---|
| IB API app | 10 | `BrokerAdapterReference` |
| Contract object | 10 | `InstrumentContractMapping` |
| Order object | 10 | `OrderModelReference` |
| Historical/market data snapshots | 10 | `BrokerMarketDataAdapter` |
| Streaming live market data | 10 | `LiveDataAdapter` |
| Live tick SQL storage | 10 | `LiveTickLedger` |
| Order execution/management | 11 | `OrderLifecycleReference` |
| Portfolio/positions/P&L | 11 | `PortfolioStateReference` |
| Live deployment | 12 | `LiveStrategyRunner` |
| Risk limit alerts | 13 | `RiskAlertEngine` |
| Execution details SQL storage | 13 | `ExecutionLedger` |

## Uso TSIS

| Tarea | Consultar |
|---|---|
| Prototipo rapido de datos | Ch. 1-4 |
| Factor research | Ch. 5, 8 |
| Vectorized prototype | Ch. 6 |
| Backtest de referencia externo | Ch. 7 |
| Analytics de performance | Ch. 9 |
| Broker adapter design | Ch. 10-12 |
| Tick/execution storage | Ch. 10, 13 |

