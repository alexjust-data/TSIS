# 01 Source Crosswalk

Mapa fuente -> uso dentro de la arquitectura TSIS.

## Successful Algorithmic Trading

**book_id:** `successful_algorithmic_trading`  
**Fuente:** Michael Halls-Moore / QuantStart  
**Rol:** guia practica para el primer backtester event-driven en Python.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Flujo `MarketEvent -> SignalEvent -> OrderEvent -> FillEvent` | `EventLoop`, `EventQueue`, `EventBus` | Ch. 14 / 140-164 | Critica |
| Interfaz `DataHandler` historico/live | `HistoricalDataAdapter`, `ReplayDataAdapter`, `LiveDASAdapter` | Ch. 14 / 144-149, 170 | Critica |
| `Strategy.calculate_signals` | `Strategy`, `DecisionPolicy` | Ch. 14-15 / 149-188 | Critica |
| Portfolio basico | `PortfolioConstruction`, `Portfolio`, `Accounting` | Ch. 14 / 151-158 | Alta |
| Simulated/live execution handler | `ExecutionSimulator`, `BrokerAdapter` | Ch. 14 / 159-170 | Alta |
| Heartbeat/backtest loop | `Clock`, `EventLoop` | Ch. 14 / 161-164 | Critica |
| Backtesting biases y costes | `Validation`, `CostModel`, `FillModel` | Ch. 3 / 24-29 | Alta |
| Securities master y datos | `DataFoundation`, `SymbolIdentity`, `CorporateActions` | Ch. 7-8 / 56-84 | Alta |
| Performance/risk metrics | `Metrics`, `Risk`, `Report` | Ch. 12-13 / 118-133 | Alta |
| Parameter sweeps y overfitting | `ExperimentRunner`, `RunManifest`, `Validation` | Ch. 16 / 190-203 | Alta |

## Python for Algorithmic Trading

**book_id:** `python_for_algorithmic_trading_hilpisch`  
**Fuente:** Yves Hilpisch  
**Rol:** puente practico Python para entorno, datos, vectorized research, event-based classes, streaming y automation.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Entorno Python reproducible | `DevEnvironment`, `RunManifest` | Ch. 2 / 57-93 | Alta |
| Data IO y almacenamiento eficiente | `DataFoundation`, `DataCatalog` | Ch. 3 / 95-143 | Alta |
| Vectorized prototyping | `ResearchPrototype`, `FeaturePipeline` | Ch. 4 / 147-207 | Alta |
| Data snooping y overfitting | `Validation` | Ch. 4 / 207-210 | Alta |
| Event-based class design | `EventLoop`, `Accounting`, `CostModel` | Ch. 6 / 314-345 | Alta |
| Buy/sell/cash/units model | `Order`, `Portfolio`, `Accounting` | Ch. 6 / 318-335 | Alta |
| Sockets/PUB-SUB streaming | `LiveDataAdapter`, `OnlineStateBuilder` | Ch. 7 / 348-374 | Alta |
| Offline -> online algorithm | `DecisionPolicy`, `ModelRegistry` | Ch. 10 / 483-491 | Alta |
| Logging and monitoring | `Logging`, `Monitoring`, `Ledger` | Ch. 10 / 491-509 | Alta |
| Risk/leverage analysis | `Risk`, `Metrics` | Ch. 10 / 446-483 | Media |

## The Evaluation and Optimization of Trading Strategies

**book_id:** `evaluation_optimization_trading_strategies_pardo`  
**Fuente:** Robert Pardo  
**Rol:** protocolo practico para desarrollo, evaluacion, optimizacion, walk-forward, control de sobreajuste y monitorizacion real-time.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Proceso idea -> trading -> monitorizacion | `StrategyLifecycle`, `ResearchGovernance` | Ch. 3 / 85-100 | Critica |
| Plataforma con diagnosticos, reporting, batch testing y WFA | `BacktestPlatform`, `ExperimentRunner`, `DiagnosticsReport` | Ch. 4 / 101-117 | Alta |
| Entrada, salida, risk management y sizing | `StrategySpec`, `RiskModel`, `SizingModel` | Ch. 5 / 118-142 | Alta |
| Simulacion historica y reportes minimos | `HistoricalSimulation`, `TradeList`, `EquityCurve`, `IntervalPerformance` | Ch. 6 / 143-203 | Critica |
| Costes, slippage, limit fills y ambiguedad same-bar | `ExecutionSimulator`, `FillModel`, `CostModel` | Ch. 6 / 143-170 | Alta |
| Especificacion exacta de reglas | `StrategySpecification`, `ParameterSchema` | Ch. 7 / 204-216 | Critica |
| Test preliminar, inspeccion manual y multimarket/multiperiod | `GoldenCaseTests`, `TradeReconciliation`, `PreliminaryTestReport` | Ch. 8 / 217-242 | Critica |
| Search methods y objective function | `ParameterSearch`, `ObjectiveFunctionLibrary` | Ch. 9 / 243-281 | Alta |
| Optimization framework y search space | `OptimizationRun`, `SearchSpace`, `RunManifest` | Ch. 10 / 282-300 | Alta |
| Optimization profile y robustez parametrica | `OptimizationProfile`, `RobustnessAnalyzer` | Ch. 10 / 300-312 | Critica |
| Walk-forward analysis y WFE | `WalkForwardRunner`, `WindowPolicy`, `WalkForwardEfficiencyMetric` | Ch. 11 / 314-345 | Critica |
| Riesgo, capital, MDD, RAR, consistency | `RiskReport`, `CapitalModel`, `StabilityReport` | Ch. 12 / 346-368 | Alta |
| Overfitting, overscanning, overparameterization | `OverfittingGuard`, `ModelComplexityBudget`, `SampleSizeGate` | Ch. 13 / 369-393 | Critica |
| Evaluation profile vs trade profile | `LivePerformanceMonitor`, `ShadowTradingMonitor` | Ch. 14 / 394-413 | Critica |

## Quantitative Trading

**book_id:** `quantitative_trading_chan`  
**Fuente:** Ernest P. Chan  
**Rol:** puente operativo para seleccion de ideas, backtesting practico, costes, ejecucion, paper trading, riesgo, regimenes y capacidad.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Filtro de estrategias por capital, tiempo, datos y capacidad | `StrategyIntakeChecklist` | Ch. 2 / 28-50 | Alta |
| Small caps, iliquidez, capacidad y competencia institucional | `SmallCapLiquidityGate`, `CapacityModel` | Ch. 2/8 / 28-50, 238-243 | Critica |
| Backtest como replicacion propia | `ReproducibilityGate` | Ch. 3 / 51-52 | Alta |
| Datos ajustados, survivorship-free y point-in-time | `DataQualityGate`, `CorporateActions`, `PointInTimeUniverse` | Ch. 3 / 59-68 | Critica |
| Sharpe, MDD, MDD duration, MAR | `MetricsEngine`, `DrawdownProfiler` | Ch. 3 / 68-82 | Alta |
| Look-ahead y test de truncamiento | `TemporalIntegrityGate`, `TruncatedDataInvarianceTest` | Ch. 3 / 82-83, 93-94 | Critica |
| Data-snooping, sample size, train/test y DSR | `OverfittingGuard`, `ExperimentRegistry` | Ch. 3 / 83-88 | Critica |
| Sensitivity analysis y simplificacion | `SensitivityAnalysis`, `RefinementGovernance` | Ch. 3 / 97-107 | Alta |
| Transaction costs y turnover cost | `TransactionCostModel`, `CostAccounting` | Ch. 2-3 / 43-44, 98-103 | Critica |
| Broker API, paper account y simulator | `BrokerCapabilityMatrix`, `PaperTradingEnvironment` | Ch. 4 / 113-115 | Alta |
| ATS semi/full automation | `AutomatedTradingSystem`, `DASBrokerAdapter` | Ch. 5 / 120-128 | Alta |
| Order size vs ADV/market cap | `ParticipationCap`, `AverageVolumeGate`, `DollarVolumeGate` | Ch. 5 / 130-132 | Critica |
| Paper trading y reconciliacion | `ShadowTradingHarness`, `BacktestVsPaperReconciler` | Ch. 5 / 132-133 | Critica |
| Divergencia live vs backtest | `LiveDivergenceMonitor` | Ch. 5 / 133-137 | Critica |
| Hard-to-borrow y short-sale rules | `ShortAvailabilityModel`, `ShortSaleConstraintModel` | Ch. 5 / 135 | Critica para shorts |
| Kelly, half-Kelly, allocation y leverage | `RiskSizingModel`, `CapitalAllocator`, `LeveragePolicy` | Ch. 6 / 138-154 | Alta |
| Model/software/operational risk | `RiskRegister`, `ModelRiskMonitor`, `OperationalRunbook` | Ch. 6 / 156-157 | Alta |
| Mean reversion vs momentum | `StrategyType`, `RegimeMonitor`, `ExitPolicy` | Ch. 7 / 166-170, 210-215 | Alta |
| CPO/regime conditional parameters | `RegimeConditionalParameterPolicy`, `ModelRegistry` | Ch. 7 / 170-181 | Media/Futura |
| Cointegration/pairs | `PairResearch`, `CointegrationTest`, `SpreadState` | Ch. 7 / 182-200 | Media/Futura |
| Factor models/PCA | `FactorExposureModel` | Ch. 7 / 200-210 | Media/Futura |
| HFT/intraday realism | `QuoteEvent`, `SpreadModel`, `LatencyModel`, `HFTReadinessGate` | Ch. 7 / 230-235 | Alta para intraday avanzado |

## Machine Trading

**book_id:** `machine_trading_chan`  
**Fuente:** Ernest P. Chan  
**Rol:** puente practico para factores, time-series, ML, opciones/eventos, intradia, microestructura, order flow y lifecycle de estrategias.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Mismo programa conceptual para backtest/live | `DecisionCore`, `ReplayLiveEquivalence` | Ch. 1 / 17, 22-25 | Critica |
| Datos historicos con survivorship, delistings, BBO y auction prices | `HistoricalDataQualityGate`, `PointInTimeUniverse`, `PrimaryAuctionPricePolicy` | Ch. 1 / 18-21; Ch. 6 / 198-200 | Critica |
| Metricas, Calmar, max drawdown, Kelly y leverage conservador | `MetricsEngine`, `DrawdownProfiler`, `RiskSizingModel` | Ch. 1 / 28-40 | Alta |
| Factor risk vs alpha, time-series/cross-sectional/statistical factors | `FactorResearchPipeline`, `FactorExposureReport` | Ch. 2 / 43-72 | Alta |
| Short interest, liquidity y universo dependiente | `ShortInterestFeature`, `SmallCapLiquiditySegmentation`, `RegimeMonitor` | Ch. 2 / 63-65 | Alta para small caps |
| Time-series AR/ARMA/VAR/VEC/Kalman con control de complejidad | `TimeSeriesResearch`, `LagSelectionPolicy`, `KalmanStateEstimator` | Ch. 3 / 75-96 | Media/Alta |
| ML con train/test, CV, bagging, random forest, SVM, HMM, NN | `MLExperimentRegistry`, `ModelComplexityBudget`, `ValidationSplitter` | Ch. 4 / 99-132 | Alta futura |
| Normalizacion y agregacion cross-sectional | `FeatureNormalizationPolicy`, `PointInTimeFeatureStore` | Ch. 4 / 125-131 | Critica para ML |
| Scheduled events y opciones | `EventCalendar`, `ScheduledEventFeed`, `BidAskExecutionPolicy` | Ch. 5 / 149-153 | Media |
| Path-dependent backtests | `PathDependentBacktest` | Ch. 5 / 153-157 | Media |
| Intraday latency, capacity, spread, adverse selection | `LatencyModel`, `CapacityModel`, `AdverseSelectionAudit` | Ch. 6 / 175-193 | Critica |
| Backtesting intradia con BBO, Level 2, ITCH, timestamps irregulares | `IntradayBacktestEngine`, `OrderBookReconstructor`, `EventClock` | Ch. 6 / 193-198 | Critica |
| Order flow, aggressor tags, BVC y order book imbalance | `OrderFlowBuilder`, `AggressorTagPolicy`, `OrderBookImbalanceFeature` | Ch. 6 / 202-214 | Alta futura |
| Trade price/midprice optimism | `ExecutablePriceGate`, `TradeVsQuoteFillAudit` | Ch. 6 / 198-211; Ch. 7 / 223-226 | Critica |
| Strategy decay, competition and live reality | `StrategyDecayMonitor`, `BacktestVsLiveReconciler`, `StrategyLifecycle` | Ch. 8 / 235-237 | Alta |

## Algorithmic Trading

**book_id:** `algorithmic_trading_chan`  
**Fuente:** Ernest P. Chan  
**Rol:** puente practico entre estrategia, backtesting, automatizacion, mean reversion, momentum intradia y riesgo.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Backtest que pueda convertirse en ejecucion automatizada | `ReplayLiveEquivalence`, `DecisionCore`, `ExecutionAdapterContract` | Ch. 1 / 19-56 | Critica |
| Look-ahead, data-snooping, survivorship y corporate actions | `TemporalIntegrityGate`, `ExperimentRegistry`, `PointInTimeUniverse`, `CorporateActions` | Ch. 1 / 21-31 | Critica |
| Hipotesis estadistica y regimenes | `ValidationReport`, `RegimeMonitor` | Ch. 1 / 34-43 | Alta |
| Plataforma backtest/ejecucion | `BacktestPlatform`, `BrokerAdapter`, `RunManifest` | Ch. 1 / 43-56 | Alta |
| Estacionariedad, ADF, Hurst, variance ratio y half-life | `MeanReversionResearch`, `StationarityTest`, `HalfLifeEstimator` | Ch. 2 / 57-78 | Media/Alta |
| Spreads, ratios, Bollinger, scaling-in y Kalman | `SignalModel`, `PairStrategyTemplate`, `KalmanStateEstimator` | Ch. 3 / 81-104 | Media |
| Data errors en threshold strategies | `BadTickFilter`, `DataQualityGate` | Ch. 3 / 101-104 | Critica |
| Acciones/ETFs, gaps, baskets y short constraints | `SmallCapStrategyLibrary`, `GapStrategyTemplate`, `ShortAvailabilityModel` | Ch. 4 / 105-124 | Alta |
| Intraday momentum, news, PEAD, order-book imbalance | `EventState`, `MarketReplay`, `OrderBookImbalanceFeature` | Ch. 7 / 173-186 | Alta |
| Kelly, half-Kelly, CPPI, stops y risk indicators | `RiskSizingModel`, `StopModel`, `RiskIndicatorRegistry` | Ch. 8 / 187-204 | Alta |

## Trading Systems and Methods

**book_id:** `trading_systems_methods_kaufman`  
**Fuente:** Perry J. Kaufman  
**Rol:** enciclopedia practica de familias de sistemas, parametros, testing, optimizacion, costes, liquidez y riesgo.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Primero idea, despues herramienta | `HypothesisRegistry`, `StrategySpec` | Ch. 1 / 1-8 | Alta |
| Datos, distribucion, probabilidad y supply/demand | `ResearchFoundation`, `FeatureValidation` | Ch. 2 / 9-29 | Media |
| Regresion, correlacion y modelos explicativos | `FeaturePipeline`, `SpreadResearch` | Ch. 3 / 30-60 | Media |
| Trend calculations y trend systems | `TrendStrategyTemplate`, `MovingAverageBenchmark` | Ch. 4-5 / 62-125 | Alta |
| Momentum, oscillators, seasonality y cycles | `MomentumStrategyTemplate`, `RegimeFilter`, `SeasonalityFeature` | Ch. 6-8 / 126-212 | Media/Alta |
| Volume, open interest, breadth y chart systems | `VolumeFeature`, `BreadthFeature`, `PatternTemplate` | Ch. 9-12 / 213-304 | Media |
| Spreads/arbitrage | `SpreadStrategyTemplate`, `RelativeValueResearch` | Ch. 13 / 305-333 | Media |
| Behavioral/event trading, gaps y pattern recognition | `EventState`, `GapStrategyTemplate`, `PatternRecognitionResearch` | Ch. 14-15 / 334-418 | Alta para scanners |
| Day trading, opening range y costes intradia | `IntradayStrategyTemplate`, `ExecutionRealismGate`, `OpeningRangeBenchmark` | Ch. 16 / 419-435 | Critica para small caps |
| Adaptive techniques, volatility y multiple timeframes | `AdaptiveParameterPolicy`, `VolatilityModel`, `MultiTimeframeState` | Ch. 17-20 / 436-502 | Media |
| Testing, optimizacion, out-of-sample y overoptimization | `ExperimentControl`, `OptimizationAudit`, `WalkForwardValidation` | Ch. 21 / 503-554 | Critica |
| Price shocks, runs, system trade-offs y similarity | `StressTesting`, `RobustnessReview`, `StrategyCorrelationReport` | Ch. 22 / 555-586 | Alta |
| Liquidez, leverage, diversificacion, trade risk y ruin | `RiskEngine`, `LiquidityGate`, `PortfolioRisk`, `RuinAnalysis` | Ch. 23 / 587-630 | Critica |
## Empirical Market Microstructure

**book_id:** `empirical_market_microstructure_hasbrouck`  
**Fuente:** Joel Hasbrouck  
**Rol:** referencia academica para microestructura empirica, trades/quotes, spread, order flow, impact y limit orders.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Roll model y bid/ask bounce | `SpreadEstimator`, `BidAskBounceAudit` | Ch. 3 / 12-15 | Critica |
| Efficient price vs transaction price | `EfficientPriceEstimator`, `MicrostructureNoiseModel` | Ch. 7-8 / 44-63 | Critica |
| Trade direction y inventory control | `TradeDirectionClassifier`, `InventoryEffectModel` | Ch. 10 / 72-79 | Alta |
| VAR, impulse response y variance decomposition | `OrderFlowVAR`, `PriceResponseCurve` | Ch. 12-13 / 86-102 | Alta |
| Structural price/trade models y PIN | `InformationAsymmetryFeature`, `AdverseSelectionAudit` | Ch. 14-15 / 103-115 | Alta |
| Cointegration y price discovery | `LinkedVenuePriceDiscovery` | Ch. 17 / 117-122 | Media/Alta |
| Limit order economics | `LimitOrderFillModel`, `QueueAssumptionLedger` | Ch. 18-21 / 124-148 | Critica para limit orders |
| Liquidity measures | `LiquidityGate`, `CapacityModel` | Ch. 22 / 150-164 | Critica small caps |

## Systematic Trading

**book_id:** `systematic_trading_carver`  
**Fuente:** Robert Carver  
**Rol:** framework modular para forecasts, sizing, volatility targeting, portfolio weights y costes.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Overfitting y fitting prudente | `OverfitGuard`, `ModelComplexityBudget` | Ch. 3 | Alta |
| Framework modular | `StrategyFramework`, `DecisionMode` | Ch. 5 | Alta |
| Instrument selection | `InstrumentSelectionPolicy` | Ch. 6 | Media/Alta |
| Forecast generation and scaling | `RawForecast`, `ForecastScaler` | Ch. 7-8 | Critica |
| Forecast weights and cap | `ForecastCombiner`, `ForecastCap` | Ch. 8 | Alta |
| Volatility targeting | `VolatilityTargetPolicy` | Ch. 9 | Critica |
| Forecast to position | `PositionSizer`, `PortfolioTarget` | Ch. 10 | Critica |
| Instrument weights and diversification multiplier | `PortfolioConstruction`, `DiversificationMultiplier` | Ch. 11 | Alta |
| Trading costs and speed | `CostAwareTradeFilter`, `TradeSpeedPolicy` | Ch. 12 | Critica |

## Algorithmic Trading and DMA

**book_id:** `algorithmic_trading_and_dma_johnson`  
**Fuente:** Barry Johnson  
**Rol:** referencia practica para DMA, order types, execution algorithms, TCA, routing e infraestructura.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| DMA vs algorithmic trading | `ExecutionMode`, `BrokerAccessModel` | Ch. 1 / 3-25 | Alta |
| Market structure and protocols | `VenueModel`, `MarketModel` | Ch. 2-3 / 27-78 | Alta |
| Order types and instructions | `OrderModel`, `OrderInstruction` | Ch. 4 / 83-112 | Critica |
| TWAP/VWAP/POV/IS algorithms | `ExecutionAlgorithmLibrary` | Ch. 5 / 115-160 | Critica |
| Transaction cost analysis | `PreTradeTCA`, `PostTradeTCA` | Ch. 6 / 161-186 | Critica |
| Efficient trading frontier | `ExecutionOptimizer`, `ExecutionDecisionTree` | Ch. 7 / 189-217 | Alta |
| Order placement, aggressiveness and hidden liquidity | `OrderPlacementPolicy`, `HiddenLiquidityModel` | Ch. 8 / 221-254 | Critica |
| Execution tactics | `ExecutionTacticLibrary` | Ch. 9 / 257-275 | Alta |
| Forecasting market conditions and impact | `ShortHorizonMarketForecast`, `ImpactModel` | Ch. 10 / 277-309 | Alta |
| OMS, routing and infrastructure | `OMS`, `Router`, `BrokerAdapter`, `LiveExecutionStack` | Ch. 11 / 311-337 | Critica |

## Building Winning Algorithmic Trading Systems

**book_id:** `building_winning_algorithmic_trading_systems_davey`  
**Fuente:** Kevin J. Davey  
**Rol:** proceso practico de strategy factory desde idea hasta walk-forward, Monte Carlo, incubacion y live monitoring.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Testing/evaluating systems | `StrategyEvaluationChecklist` | Ch. 5-8 / 43-76 | Alta |
| Goals and trading idea | `IdeaRecord`, `HypothesisSpec` | Ch. 9-10 / 79-92 | Alta |
| Data and limited testing | `DatasetContract`, `LimitedTestRun` | Ch. 11-12 / 93-114 | Alta |
| Walk-forward analysis | `WalkForwardRunner` | Ch. 13 / 115-128 | Critica |
| Monte Carlo and incubation | `MonteCarloRobustness`, `ShadowTradingHarness` | Ch. 14 / 129-132 | Critica |
| Diversification | `StrategyDiversificationReport` | Ch. 15 / 133-138 | Alta |
| Position sizing and money management | `PositionSizingPolicy`, `CapitalAllocationPolicy` | Ch. 16 / 139-146 | Alta |
| Documentation and go-live | `ResearchLedger`, `GoLiveChecklist` | Ch. 17, 20-22 / 147-202 | Critica |
| Live monitoring | `LivePerformanceMonitor`, `LiveRunDiary` | Ch. 23-24 / 205-232 | Critica |

## Python for Algorithmic Trading Cookbook

**book_id:** `python_for_algorithmic_trading_cookbook_strimpel`  
**Fuente:** Jason Strimpel  
**Rol:** recetario tecnico Python para data, research, backtesting, analytics, IB API, live deployment y storage.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Free market data and OpenBB | `ExternalDataAdapter` | Ch. 1 | Media/Alta |
| pandas transforms | `FeaturePipeline` | Ch. 2 | Alta |
| CSV/SQLite/PostgreSQL/HDF5 | `LocalDataStoreReference` | Ch. 4 | Media |
| Factor research | `FactorResearch`, `FactorExposureModel` | Ch. 5 | Alta |
| VectorBT and walk-forward | `VectorizedPrototype`, `ParameterSearchPrototype` | Ch. 6 | Alta |
| Zipline Reloaded | `ReferenceEventBacktest` | Ch. 7 | Alta |
| Alphalens and Pyfolio | `FactorAnalytics`, `PerformanceReport` | Ch. 8-9 | Alta |
| Interactive Brokers API | `BrokerAdapterReference`, `OrderModelReference` | Ch. 10-11 | Alta |
| Live deployment | `LiveStrategyRunner` | Ch. 12 | Alta |
| ArcticDB, risk alerts, execution details DB | `TickStore`, `RiskAlertEngine`, `ExecutionLedger` | Ch. 13 | Alta |
## Lectura Recomendada Por Tarea

```text
Si el agente trabaja en flujo Market/Signal/Order/Fill:
  leer Successful Algorithmic Trading Ch. 14.

Si trabaja en entorno/datos/vectorized research:
  leer Hilpisch Ch. 2-4.

Si trabaja en clases Python event-based:
  leer Hilpisch Ch. 6 y comparar con Successful Algorithmic Trading Ch. 14.

Si trabaja en online/live:
  leer Hilpisch Ch. 7/10, Quantitative Trading Ch. 5 y Machine Trading Ch. 1.

Si trabaja en fills/costes:
  leer Successful Algorithmic Trading Ch. 3/14, Hilpisch Ch. 6/10, Pardo Ch. 6, Quantitative Trading Ch. 3/5 y Machine Trading Ch. 6.

Si trabaja en protocolo de evaluacion, optimizacion o go/no-go:
  leer Pardo Ch. 3, Ch. 8, Ch. 10 y Ch. 11.

Si trabaja en control de sobreajuste:
  leer Quantitative Trading Ch. 3, Algorithmic Trading Ch. 1, Kaufman Ch. 21, Machine Trading Ch. 4, Pardo Ch. 9-13 y despues Lopez de Prado/PBO/DSR.

Si trabaja en paper/shadow/live reconciliation:
  leer Quantitative Trading Ch. 5, Machine Trading Ch. 8 y Pardo Ch. 14.

Si trabaja en small-cap capacity:
  leer Quantitative Trading Ch. 2/5/8, Algorithmic Trading Ch. 4/7/8, Kaufman Ch. 16/23, Machine Trading Ch. 6 y complementar con Harris.

Si trabaja en intraday quotes/order flow:
  leer Machine Trading Ch. 6, Hasbrouck Ch. 10-14 y Johnson Ch. 8-11 antes de disenar `QuoteEvent`, `OrderFlowBuilder` o `OrderBookReconstructor`.

Si trabaja en catalogo de estrategias benchmark:
  leer Kaufman Ch. 5/6/12/16 y Algorithmic Trading Ch. 2-7.

Si trabaja en testing, optimizacion o robustez parametrica:
  leer Pardo Ch. 9-13 y Kaufman Ch. 21-23 juntos.
```



