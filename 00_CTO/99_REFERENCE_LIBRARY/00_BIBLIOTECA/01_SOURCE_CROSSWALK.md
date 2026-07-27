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
## Trading Systems, 2nd Edition

**book_id:** `trading_systems_urban_jaekle`  
**Fuente:** Urban Jaekle / Emilio Tomasini  
**Rol:** proceso practico de desarrollo de sistemas, robustez, exits, sizing y portfolio.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Flujo idea -> reglas -> costes -> estabilidad -> exits -> WFA | `StrategyDevelopmentWorkflow` | Caps. 2-3 / 29-98 | Alta |
| Problemas de datos, sesiones, continuos y corporate actions | `DataQualityGate`, `ContinuousContractPolicy` | Cap. 2 / 32-34 | Alta |
| Parameter stability diagrams | `ParameterStabilityMap`, `RobustnessAnalyzer` | Cap. 3 / 64-71 | Alta |
| MAE/MFE para stops y profit targets | `MAE_MFE_Report`, `ExitDiagnostics` | Cap. 3 / 79-98 | Alta |
| Timescale analysis | `TimeframeStressTest` | Cap. 4 / 100-105 | Media |
| Monte Carlo sobre trades | `MonteCarloTradeSequence` | Cap. 4 y 7 | Alta |
| Anchored y rolling WFA | `WalkForwardRunner`, `WindowPolicy` | Cap. 6 / 180-187 | Critica |
| Position sizing | `SizingModel`, `CapitalModel` | Cap. 7 | Alta |
| Dynamic portfolio construction | `PortfolioConstruction`, `StrategyActivationPolicy` | Cap. 8 | Alta |
| Survivorship y portfolio de acciones | `PointInTimeUniverse`, `SignalRankingPolicy` | Cap. 9 / 315+ | Critica |

## Algorithmic Trading Systems and Strategies

**book_id:** `algorithmic_trading_systems_strategies_dolzhenko`  
**Fuente:** Viktoria Dolzhenko  
**Rol:** arquitectura de plataforma de trading, modelo de dominio y core compartido entre search/backtest y real trading.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Requirements elicitation | `ArchitectureDiscovery` | Cap. 3 / 70-72 | Alta |
| Indicator, Signal, Condition, Strategy, Theory | `DomainModel`, `StrategySpec` | Cap. 3 / 72-80 | Critica |
| Theory vs parameterized strategy | `StrategyIdea`, `StrategyInstance` | Cap. 3 / 75-77 | Alta |
| Strategy Search / Sandbox / Real Trading subsystems | `BacktestLiveArchitecture` | Cap. 4 | Critica |
| Exchange gateway y message broker | `ExecutionAdapter`, `EventBus` | Cap. 4 / 142-144 | Alta |
| Master Data Service | `MasterData`, `ReferenceData` | Cap. 4 / 154-156 | Alta |
| Optimization module, GA/brute force | `OptimizationEngine` | Caps. 6-7 / 179-235 | Alta |
| Shared core module | `CoreDecisionEngine`, `BacktestLiveSharedCore` | Cap. 8 / 263-267 | Critica |
| Signal/condition tree model | `ConditionTree`, `RuleExpression` | Cap. 8 / 267-270 | Alta |
| Position state machine | `PositionStateMachine`, `OrderLifecycle` | Cap. 8 / 280-285 | Critica |
| Docker/Kubernetes health/scaling ideas | future `DeploymentRunbook` | Cap. 9 / 297-312 | Baja v0.1 |

## High-Frequency Trading

**book_id:** `high_frequency_trading_aldridge`  
**Fuente:** Irene Aldridge  
**Rol:** microestructura, tick data, costes, capacity, market impact, execution algorithms y core online.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---:|---|
| Limit order book, FIFO/pro-rata, passive/aggressive | `OrderBookSnapshot`, `OrderAggressiveness` | Ch. 3 / 69-84 | Alta |
| Level I/Level II quote/trade schema | `QuoteEvent`, `TradeEvent`, `OrderBookEvent` | Ch. 4 / 91-94 | Critica futura |
| Bid-ask bounce, midquote, sampling | `SpreadModel`, `SamplingPolicy` | Ch. 4 / 98-113 | Alta |
| Irregular timestamps and duration | `EventTimeClock`, `DurationFeatures` | Ch. 4 / 109-116 | Media |
| Trade direction classification | `TradeClassifier` | Ch. 4 / 116-121 | Media |
| Transparent/implicit costs and market impact | `CostModel`, `SlippageModel`, `MarketImpactModel` | Ch. 5 / 123-153 | Alta |
| Performance, attribution, capacity, alpha decay | `PerformanceEngine`, `CapacityModel`, `AlphaDecayMonitor` | Ch. 6 / 155-183 | Alta |
| TWAP/VWAP/POV and optimal execution | `ExecutionPolicy`, `ParticipationCap` | Ch. 15 | Alta futura |
| Development lifecycle and core engine | `OnlineCoreEngine`, `AcceptanceTests` | Ch. 16 / 397-401 | Alta |
## Quantum Finance

`quantum_finance_raymond_lee`

| Tarea TSIS | Secciones/Paginas | Uso |
|---|---:|---|
| QPL como feature experimental | 116-140 | Comparar contra S/R, VWAP, pivots y opening range |
| Catalogo basico de estrategias | 146-181 | Trend, breakout, reversal, channel, stops y hedge |
| AI/GA/fuzzy experimental | 186-230 | Futuro `ExperimentalAlphaLab` |
| Forecast batch/MQL | 300-353 | Traducir pipeline MQL a Python si hay tarea concreta |
| Multiagent RL trader | 398-417 | Futuro `OfflineRLPolicyLab` |

Nota: no usar como fuente principal para motor event-driven, OMS o execution realism.

## Testing and Tuning Market Trading Systems

`testing_tuning_market_trading_systems_masters`

| Tarea TSIS | Secciones/Paginas | Uso |
|---|---:|---|
| Feature QA antes de optimizar | 21-45 | Stationarity y entropy |
| Optimizacion controlada | 46-110 | Regularizacion y differential evolution |
| Bias y seleccion | 115-161 | Training bias, selection bias, OOS final |
| Walkforward correcto | 168-176 | Lookahead, omit buffer, extra gap |
| Retornos para estadistica | 235-240 | Bar-by-bar vs completed trades |
| Bootstrap/permutation | 254-360 | Bounds, drawdown y permutation tests |

Nota: fuente prioritaria para endurecer la validacion una vez el backtester ya produce retornos correctos.

## Trading Systems and Methods, 5th Edition + Website

`trading_systems_methods_website_5e_kaufman`

| Tarea TSIS | Secciones/Paginas | Uso |
|---|---:|---|
| Research governance | 38-43 | Omission errors, costes, resultados demasiado buenos |
| StrategyPatternLibrary | 99-922 | Familias completas de sistemas |
| System testing | 925-944 | Expectations, parameters, data, testing integrity |
| Robustness/sensitivity | 958-1001 | Robustness surface y OOS |
| Cost/price shock audit | 962-995, 1012-1017 | Costes y shocks |
| Risk metrics/sizing | 1047-1081 | Risk control, liquidity, stops, sizing |
| Portfolio allocation | 1099+ | Diversificacion y asignacion |

Nota: preferir esta entrada sobre `trading_systems_methods_kaufman` cuando se necesiten paginas exactas del PDF nuevo.

## Software Engineering And Data Architecture Sources

| Fuente | Tarea TSIS | Secciones/Paginas | Uso |
|---|---|---:|---|
| `architecture_patterns_python_gregory` | Arquitectura Python del motor | 29-37, 43-203, 212-347 | Domain model, repository, UoW, aggregates, message bus, commands, CQRS, DI |
| `fundamentals_software_architecture_2e_richards` | Documento de arquitectura y ADRs | 109-181, 305-326, 414-511, 692-754 | Characteristics, fitness functions, modular monolith, event-driven, ADRs, risk storming |
| `grokking_streaming_systems_fischer` | Modelo streaming pedagogico | 27-207, 223-362 | Queues, stream graph, delivery semantics, windows, joins, backpressure, stateful computation |
| `streaming_systems_akidau` | Semantica temporal rigurosa | 22-170, 174-357 | Event time, watermarks, triggers, lateness, exactly-once, streams/tables, joins |
| `fundamentals_data_engineering_reis` | Data foundation TSIS | 60-165, 225-387, 388-521 | Lifecycle, source systems, CDC/logs, storage, ingestion, transformation, serving |
| `database_internals_petrov` | Storage/consistency/recovery | 24-42, 67-84, 106-207, 216-383 | File formats, WAL, MVCC, LSM, consistency, transactions, consensus |
| `continuous_delivery_humble_farley` | Pipeline de entrega | 65-174, 221-282, 359-377, 451-476 | CI, deployment pipeline, acceptance/capacity tests, data scripts, audit |
| `test_driven_development_python_3e_percival` | Tests Python operativos | 45-141, 205-292, 335-409 | Functional/unit tests, double-loop TDD, regression, isolation, runtime env |
| `software_engineering_google_winters` | Gobernanza de ingenieria | 19-51, 82-118, 276-500, 523-823 | Docs, review, test strategy, fakes, large tests, dependencies, CI/CD |

Lectura recomendada para `TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1`:

```text
1. Fundamentals of Software Architecture
2. Architecture Patterns with Python
3. Streaming Systems
4. Fundamentals of Data Engineering
5. Continuous Delivery
```

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




## Trading and Exchanges: Market Microstructure for Practitioners

**book_id:** `trading_and_exchanges_harris`  
**Fuente:** Larry Harris  
**Rol:** Explica el mercado que el backtester debe simular: participantes, ordenes, liquidez, spreads, costes, impacto y ejecucion.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Order types and instructions | `Order`, `OrderType`, `TimeInForce`, `OrderLifecycle` | Partes sobre ordenes y mercados | Critica |
| Bid-ask spread and liquidity | `SpreadModel`, `LiquidityModel`, `ExecutablePriceGate` | Partes sobre liquidez/costes | Critica |
| Explicit/implicit transaction costs | `CostModel`, `TransactionCostAnalysis` | Partes sobre costes de trading | Critica |
| Market impact and large orders | `ImpactModel`, `ParticipationCap` | Partes sobre impacto/ejecucion | Alta |
| Limit vs market order realism | `FillModel`, `QueueApproximation`, `AdverseSelectionAudit` | Partes sobre ordenes limitadas | Alta |

## Building Applications with AI Agents

**book_id:** `building_applications_ai_agents_albada`  
**Fuente:** Michael Albada  
**Rol:** Fuente de diseno para convertir agentes en operadores de conocimiento y no solo generadores de texto.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Agent roles and workflows | `AgentWorkflowProtocol`, `AgentRunManifest` | Arquitectura de agentes | Alta |
| RAG over source library | `ReferenceRetriever`, `GraphifyQueryWorkflow` | RAG/memory | Alta |
| Tool governance | `ToolUsePolicy`, `EvidenceLedger` | Tools/guardrails | Alta |
| Agent evaluation | `AgentEvaluationHarness` | Evaluation/observability | Media |

## Clean Architecture

**book_id:** `clean_architecture_anderson_rogerio`  
**Fuente:** Rogerio Anderson  
**Rol:** Referencia de arquitectura limpia para mantener el core de backtesting independiente de datos, broker, UI y almacenamiento.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Dependency rule | `DomainCore`, `Port`, `Adapter` | Clean architecture layers | Critica |
| Use cases | `BacktestRunUseCase`, `ReplayRunUseCase` | Application layer | Alta |
| Framework independence | `MarketDataPort`, `LedgerRepository` | Interface adapters | Alta |
| Testable core | `CoreGoldenTests`, `FakeExecutionVenue` | Testing | Alta |

## Clean Architecture

**book_id:** `clean_architecture_robert_martin`  
**Fuente:** Robert C. Martin  
**Rol:** Define la disciplina conceptual: separar politica de negocio de detalles tecnicos y mantener dependencias hacia adentro.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Dependency rule | `BacktestEngineCore`, `DomainCore` | Architecture chapters | Critica |
| Policy vs detail | `DuckDBAdapter`, `DASBrokerAdapter`, `ParquetLedgerRepository` | Boundaries | Critica |
| Component principles | `ComponentBoundary`, `PackagePolicy` | Components | Alta |
| Architecture tests | `BoundaryImportTest`, `CoreContractTest` | Testing/architecture | Alta |

## Clean Architectures in Python

**book_id:** `clean_architectures_python_giordani`  
**Fuente:** Leonardo Giordani  
**Rol:** Aterriza arquitectura limpia en Python con entidades, casos de uso, repositorios y tests.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Python clean architecture layout | `domain/`, `application/`, `adapters/`, `infrastructure/` | Project structure chapters | Critica |
| Repository pattern | `LedgerRepository`, `MarketDataRepository` | Repository chapters | Alta |
| Use case DTOs | `BacktestRunRequest`, `BacktestRunResult` | Use case chapters | Alta |
| In-memory tests | `FakeMarketDataSource`, `InMemoryLedger` | Testing chapters | Alta |

## Domain-Driven Design

**book_id:** `domain_driven_design_evans`  
**Fuente:** Eric Evans  
**Rol:** Ayuda a construir un lenguaje ubicuo y boundaries estables para el motor.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Ubiquitous language | `TSIS_BACKTEST_GLOSSARY` | Core DDD chapters | Critica |
| Entities/value objects | `OrderId`, `Money`, `Price`, `Quantity`, `Timestamp` | Building blocks | Critica |
| Aggregates | `OrderAggregate`, `PortfolioAggregate` | Aggregates | Alta |
| Bounded contexts | `ResearchContext`, `BacktestContext`, `ExecutionContext` | Strategic design | Alta |
| Repositories/factories | `LedgerRepository`, `OrderFactory` | Building blocks | Alta |

## Introduction to Algorithms, 4th Edition

**book_id:** `introduction_to_algorithms_cormen_4e`  
**Fuente:** Thomas H. Cormen / Charles E. Leiserson / Ronald L. Rivest / Clifford Stein  
**Rol:** No es libro de trading: es la fuente de rigor para complejidad, estructuras y algoritmos que soportan el motor.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Priority queues/heaps | `PriorityEventQueue` | Heaps/priority queues | Alta |
| Hash tables | `SymbolIndex`, `OrderIndex` | Hashing | Alta |
| Graph algorithms | `PipelineDependencyGraph`, `GraphifyIntegration` | Graphs | Media |
| Complexity analysis | `ComplexityBudget`, `BenchmarkSuite` | Algorithm analysis | Alta |

## Mastering AI System Design

**book_id:** `mastering_ai_system_design_sreepada`  
**Fuente:** Soudamini Sreepada  
**Rol:** Sirve para disenar sistemas AI/ML alrededor del core, no para reemplazar la semantica del backtester.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| AI system lifecycle | `MLExperimentRegistry`, `ModelRegistry` | AI design lifecycle | Media |
| Feature/data pipelines | `PointInTimeFeatureStore` | Data/feature design | Alta futura |
| Model serving | `InferenceService` | Serving chapters | Media futura |
| Monitoring/drift | `DriftMonitor`, `LiveModelMonitor` | MLOps/monitoring | Alta futura |

## The Clean Coder

**book_id:** `the_clean_coder_martin`  
**Fuente:** Robert C. Martin  
**Rol:** No define arquitectura tecnica, pero ayuda a fijar disciplina de ejecucion, pruebas y responsabilidad profesional.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Definition of Done | `ModuleAcceptanceChecklist` | Professional commitments/testing | Alta |
| TDD discipline | `CoreGoldenTests`, `RegressionTests` | Testing chapters | Alta |
| Commitment hygiene | `TaskCommitmentLedger` | Professionalism chapters | Media |

## Advanced Algorithmic Trading

**book_id:** `advanced_algorithmic_trading_tawcer`  
**Fuente:** QuantStart / Michael Halls-Moore  
**Rol:** Sirve como puente entre el primer backtester event-driven y modelos cuantitativos mas avanzados.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Advanced strategy research | `ResearchStrategyLibrary` | Strategy/model chapters | Media/Alta |
| Time-series/statistical models | `TimeSeriesResearch` | Time series chapters | Media |
| Portfolio analytics | `PortfolioAnalytics` | Portfolio/risk chapters | Media |
| Benchmark strategies | `StrategyBenchmarkSuite` | Research examples | Alta |

## A Guide to Creating a Successful Algorithmic Trading Strategy

**book_id:** `guide_successful_algorithmic_trading_strategy_kaufman`  
**Fuente:** Perry J. Kaufman  
**Rol:** Complementa la enciclopedia de Kaufman con un proceso concentrado para formular estrategias robustas.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Strategy creation checklist | `StrategyIntakeChecklist` | Strategy design sections | Alta |
| Rule specification | `StrategySpecification`, `ParameterSchema` | Rules/testing | Alta |
| Robustness thinking | `RobustnessChecklist` | Testing/validation | Alta |
| Risk sizing basics | `RiskSizingModel` | Risk sections | Media |

## Machine Learning for Algorithmic Trading, 2nd Edition

**book_id:** `machine_learning_algorithmic_trading_jansen_2e`  
**Fuente:** Stefan Jansen  
**Rol:** Libro fuerte para laboratorio ML, pero debe entrar despues del motor reproducible y datos limpios.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Point-in-time alpha factors | `PointInTimeFeatureStore`, `AlphaFactorLibrary` | Data/features chapters | Alta futura |
| ML experiment tracking | `MLExperimentRegistry`, `ModelRegistry` | Model selection chapters | Alta futura |
| Leakage-aware validation | `PurgedValidationSplitter`, `OverfittingGuard` | Validation/backtesting chapters | Alta futura |
| ML backtest integration | `BacktestMLAdapter`, `PortfolioConstructionModel` | Backtesting/portfolio chapters | Media futura |

## Designing Data-Intensive Applications

**book_id:** `designing_data_intensive_applications_kleppmann`  
**Fuente:** Martin Kleppmann  
**Rol:** Fuente clave para pensar TSIS como sistema de datos: logs, estado, streams, storage, consistency y evolucion.

| Extraer | Encaja en TSIS | Secciones/Paginas | Prioridad |
|---|---|---|---|
| Event logs as system of record | `EventLog`, `Ledger`, `StateRebuilder` | Batch/stream/log chapters | Critica |
| Schema evolution | `SchemaVersioning`, `DataContract` | Encoding/schema evolution | Critica |
| Storage/index tradeoffs | `LedgerStorage`, `SymbolDateIndex` | Storage/index chapters | Alta |
| Consistency/idempotency | `IdempotencyKey`, `ConsistencyPolicy` | Distributed data chapters | Alta |
| Batch vs streaming views | `BatchPipeline`, `StreamPipeline`, `ReplaySemantics` | Batch/stream chapters | Critica |
