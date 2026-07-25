# Python for Algorithmic Trading Cookbook - Jason Strimpel

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido](#mapa-rapido)
- [Datos y almacenamiento](#datos-y-almacenamiento)
- [Backtesting y factor research](#backtesting-y-factor-research)
- [Interactive Brokers y live](#interactive-brokers-y-live)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates](#quality-gates)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Este cookbook es una fuente moderna y practica para Python: adquisicion de datos, pandas, visualizacion, almacenamiento, factores, VectorBT, Zipline Reloaded, Alphalens, Pyfolio, Interactive Brokers, live deployment y gestion avanzada de datos.

Para TSIS no es autoridad cientifica ni arquitectura unica, pero si es muy util como recetario tecnico para:

```text
data ingestion -> local storage -> research -> backtest tools -> performance analytics -> broker API -> live deployment
```

## Rol dentro de TSIS

Encaja en:

```text
PythonRecipes
DataAcquisition
LocalDataStore
FactorPipeline
VectorizedBacktestPrototype
ZiplineReferenceBacktest
PerformanceAnalytics
IBBrokerAdapterReference
LiveTickStorage
RiskAlerts
TradeExecutionLedger
```

## Mapa rapido

| Capitulo | Contenido | Uso TSIS |
|---|---|---|
| 1 | free data: Nasdaq Data Link, OpenBB, options/futures/factors | `ExternalDataAdapter` |
| 2 | pandas transforms, returns, volatility, resampling, missing data | `FeaturePipeline` |
| 3 | Matplotlib/Seaborn/Dash | `ResearchDashboard` |
| 4 | CSV, SQLite, PostgreSQL, HDF5 | `LocalDataStore` |
| 5 | PCA, beta, Fama-French, factor ranking | `FactorResearch` |
| 6 | VectorBT and walk-forward optimization | `VectorizedPrototype` |
| 7 | Zipline Reloaded event-based factor backtests | `ReferenceBacktestEngine` |
| 8 | Alphalens factor analysis | `FactorValidation` |
| 9 | Pyfolio risk/performance | `PerformanceReport` |
| 10-11 | Interactive Brokers contracts, orders, market data, positions, P&L | `BrokerAdapterReference` |
| 12 | live deployment examples | `LiveStrategyRunner` |
| 13 | ThetaData, ArcticDB, risk alerts, SQL execution storage | `TickStore`, `RiskAlertEngine`, `ExecutionLedger` |

## Datos y almacenamiento

Los capitulos 1-4 son utiles para agentes que necesiten crear ingestion y almacenamiento rapido. Para TSIS, hay que adaptar las recetas a la arquitectura existente basada en datos canonicos y Parquet/DuckDB/Polars.

No copiar sin criterio:

```text
CSV/SQLite/HDF5 recipes -> revisar contra TSIS canonical schema
```

Si una receta usa un proveedor externo, debe quedar registrado:

```text
provider
endpoint
download_time
adjustment_policy
schema_version
license/usage constraint
```

## Backtesting y factor research

VectorBT sirve para prototipos vectorizados y exploracion rapida. Zipline Reloaded sirve como referencia event-based para factor portfolios. Alphalens y Pyfolio ayudan a evaluar factores, retornos, turnover, drawdowns, exposure y performance.

Para TSIS:

```text
VectorBT = research speed
Zipline = external reference implementation
Alphalens/Pyfolio = analytics reference
TSIS engine = semantic authority final
```

## Interactive Brokers y live

Los capitulos 10-12 son relevantes por los contratos de API:

- contract objects;
- order objects;
- historical data;
- market data snapshots;
- streaming live market data;
- local tick storage;
- order execution;
- order management;
- positions;
- portfolio P&L;
- live deployment.

Aunque TSIS use DAS/Polygon, estas recetas ayudan a disenar un broker adapter limpio.

## Blueprint TSIS derivado

```text
ExternalDataAdapter
    -> CanonicalDataValidator
    -> LocalDataStore
    -> ResearchNotebook
    -> VectorizedPrototype
    -> EventBacktestReference
    -> PerformanceAnalytics
    -> BrokerAdapter
    -> LiveDataStore
    -> RiskAlert
    -> ExecutionLedger
```

## Quality gates

- Toda receta debe adaptarse a schemas TSIS, no copiase como modulo aislado.
- Separar prototype backtest de authority backtest.
- Registrar versiones de librerias.
- No usar OpenBB/Nasdaq/IB data sin registrar adjustment/source policy.
- Live tick storage debe incluir timestamp, source, symbol identity y schema.
- Execution details deben persistirse en ledger auditable.

## Limitaciones

Es un cookbook reciente, pero depende de librerias y APIs que cambian. Antes de implementar recetas actuales conviene comprobar documentacion oficial o versions locales. No sustituye arquitectura event-driven propia ni validacion cientifica avanzada.

