# 02 TSIS Backtest Engine Concept Index

Indice global concepto -> fuente -> seccion/pagina para agentes que trabajan en `TSIS_BACKTEST_ENGINE`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Event-driven backtesting | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 14 / 138-164; Hilpisch Ch. 6 / 314-345 | `EventLoop`, `EventQueue`, `EventBus` |
| MarketEvent | `successful_algorithmic_trading` | Ch. 14 / 140-141 | `MarketDataEvent` |
| SignalEvent | `successful_algorithmic_trading` | Ch. 14 / 141 | `Signal` |
| OrderEvent | `successful_algorithmic_trading` | Ch. 14 / 142 | `Order`, `OrderEvent` |
| FillEvent | `successful_algorithmic_trading` | Ch. 14 / 142-143 | `Fill`, `Accounting` |
| DataHandler | `successful_algorithmic_trading` | Ch. 14 / 144-149 | `HistoricalDataAdapter`, `ReplayDataAdapter` |
| Live data adapter | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | SAT Ch. 14 / 144,170; Hilpisch Ch. 7 / 348-374; Chan Ch. 5 / 120-128 | `LiveDASAdapter` |
| Strategy interface | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 14-15 / 149-188; Hilpisch Ch. 6 / 325-345 | `Strategy`, `DecisionPolicy` |
| Strategy intake | `quantitative_trading_chan` | Chan Ch. 2 / 28-50 | `StrategyIntakeChecklist` |
| Strategy lifecycle | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 3 / 85-100; Chan Ch. 1/8 / 20-27, 238-243 | `StrategyLifecycle`, `ResearchGovernance` |
| Strategy specification | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 7 / 204-216 | `StrategySpecification`, `ParameterSchema` |
| Preliminary testing | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 8 / 217-242 | `GoldenCaseTests`, `PreliminaryTestReport` |
| Portfolio state | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 14 / 151-158; Hilpisch Ch. 6 / 318-335 | `Portfolio`, `Accounting` |
| OMS basico | `successful_algorithmic_trading` | Ch. 14 / 151-158 | `OMS`, `OrderLifecycle` |
| Execution simulator | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 14 / 159-160; Hilpisch Ch. 6 / 320-322; Pardo Ch. 6 / 143-170; Chan Ch. 5 / 120-137 | `ExecutionSimulator` |
| Broker adapter | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | SAT Ch. 14 / 164-170; Hilpisch Ch. 8-9 / 376-444; Chan Ch. 4-5 / 113-128 | `BrokerAdapter`, `DASBrokerAdapter` |
| Backtest loop | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 14 / 161-164; Hilpisch Ch. 6 / 314-345 | `Clock`, `EventLoop` |
| Historical simulation diagnostics | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 6 / 143-203; Chan Ch. 3 / 51-107 | `TradeList`, `EquityCurve`, `IntervalPerformance` |
| Backtesting biases | `successful_algorithmic_trading`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 3 / 24-27; Pardo Ch. 13 / 369-393; Chan Ch. 3 / 82-98 | `Validation`, `OverfittingGuard`, `PitfallAudit` |
| Look-ahead bias | `quantitative_trading_chan` | Chan Ch. 3 / 82-83 | `TemporalIntegrityGate` |
| Truncated data invariance | `quantitative_trading_chan` | Chan Ch. 3 / 83, 93-94 | `TruncatedDataInvarianceTest` |
| Transaction costs | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 3 / 28-29; Hilpisch Ch. 6 / 318-328; Pardo Ch. 6 / 143-170; Chan Ch. 2-3 / 43-44, 98-103 | `CostModel`, `FillModel`, `TransactionCostModel` |
| Slippage | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 3 / 28-29; Hilpisch Ch. 10 / 464-465; Pardo Ch. 6 / 143-170; Chan Ch. 2/5 / 43-44, 130-132 | `FillModel`, `SlippageModel` |
| Market impact | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 3 / 29; Chan Ch. 2/5 / 43-44, 130-132 | `ImpactModel`, `ParticipationCap` |
| Participation cap | `quantitative_trading_chan` | Chan Ch. 5 / 130-132 | `AverageVolumeGate`, `DollarVolumeGate` |
| Securities master | `successful_algorithmic_trading` | Ch. 7 / 56-69 | `DataFoundation` |
| Symbol identity | `successful_algorithmic_trading` | Ch. 7 / 59 | `SymbolIdentity` |
| Corporate actions | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 7 / 59; Chan Ch. 3 / 62-68 | `CorporateActions` |
| Survivorship bias | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 3/7 / 24-27, 56-69; Chan Ch. 2-3 / 34-35, 44-45, 59-68 | `SurvivorshipBiasGuard`, `PointInTimeUniverse` |
| Data IO/storage | `python_for_algorithmic_trading_hilpisch` | Ch. 3 / 95-143 | `DataCatalog` |
| Data frequency | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | SAT Ch. 8 / 72-73; Hilpisch Ch. 3 / 95-126; Chan Ch. 7 / 230-235 | `MarketDataSchema` |
| Tick/order book data | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | SAT Ch. 8 / 73; Hilpisch Ch. 3 / 121-122; Chan Ch. 7 / 230-235 | future `QuoteEvent`, `TradeEvent`, `OrderBookEvent` |
| Data cleaning | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 8 / 83-84; Chan Ch. 7 / 167-168 | `DataValidation`, `BadTickFilter` |
| Vectorized research | `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | Hilpisch Ch. 4 / 147-207; Chan Ch. 3 / 51-107 | `ResearchPrototype` |
| Data snooping/overfitting | `python_for_algorithmic_trading_hilpisch`; `successful_algorithmic_trading`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Hilpisch Ch. 4 / 207-210; SAT Ch. 16 / 190-197; Pardo Ch. 13 / 369-393; Chan Ch. 3 / 83-88 | `Validation`, future DSR/PBO |
| ML prediction pipeline | `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | Hilpisch Ch. 5 / 223-310; Ch. 10 / 463-491; Chan Ch. 7 / 170-181 | `FeaturePipeline`, `ModelRegistry` |
| Conditional parameter optimization | `quantitative_trading_chan` | Chan Ch. 7 / 170-181 | future `RegimeConditionalParameterPolicy` |
| Online algorithm | `python_for_algorithmic_trading_hilpisch` | Ch. 7 / 358-362; Ch. 10 / 484-491 | `OnlineStateBuilder`, `DecisionPolicy` |
| Streaming sockets | `python_for_algorithmic_trading_hilpisch` | Ch. 7 / 348-374 | `LiveDataAdapter` |
| Paper trading | `quantitative_trading_chan` | Chan Ch. 3/5 / 87-88, 132-133 | `PaperTradingHarness`, `ShadowTradingHarness` |
| Backtest vs paper reconciliation | `quantitative_trading_chan`; `evaluation_optimization_trading_strategies_pardo` | Chan Ch. 5 / 132-137; Pardo Ch. 14 / 394-413 | `BacktestVsPaperReconciler`, `TradeProfile` |
| Equity curve | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 12 / 121; Hilpisch Ch. 4 / 167-173; Pardo Ch. 6/12 / 143-203, 346-368; Chan Ch. 2-3 / 40-43, 68-82 | `Metrics`, `Report` |
| Sharpe ratio | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 12 / 122-125; Chan Ch. 2-3 / 39-42, 68-75 | `Metrics` |
| Drawdown | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 12 / 126-127; Hilpisch Ch. 10 / 478-483; Pardo Ch. 12 / 348-358; Chan Ch. 2-3 / 40-43, 76-82 | `Metrics`, `Risk`, `DrawdownProfiler` |
| MAR ratio | `quantitative_trading_chan` | Chan Ch. 3 / 68-69 | `Metrics` |
| Required capital | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 12 / 354-357 | `CapitalModel` |
| Strategy stop-loss | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 14 / 399-403 | `StrategyStopLossPolicy` |
| Risk sources | `successful_algorithmic_trading`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 13 / 128-130; Pardo Ch. 5/12 / 118-142, 346-368; Chan Ch. 6 / 151-157 | `RiskRegister` |
| Kelly Criterion | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | SAT Ch. 13 / 130-132; Hilpisch Ch. 10 / 446-463; Chan Ch. 6 / 138-151, 163-164 | future `SizingModel`, `RiskSizingModel` |
| VaR | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 13 / 132-133; Hilpisch Ch. 10 / 480-483 | future `PortfolioRisk` |
| Mean reversion | `quantitative_trading_chan` | Chan Ch. 7 / 166-170 | `MeanReversionStrategyFamily`, `RegimeMonitor` |
| Momentum | `quantitative_trading_chan` | Chan Ch. 7 / 166-170 | `MomentumStrategyFamily`, `RegimeMonitor` |
| Regime shift | `quantitative_trading_chan` | Chan Ch. 5/7 / 133-135, 170-181 | `RegimeMonitor`, `MarketState` |
| Cointegration | `quantitative_trading_chan` | Chan Ch. 7 / 182-200 | future `PairResearch`, `CointegrationTest` |
| Factor models | `quantitative_trading_chan` | Chan Ch. 7 / 200-210 | future `FactorExposureModel` |
| Exit policy | `quantitative_trading_chan` | Chan Ch. 7 / 210-215 | `ExitPolicy` |
| HFT realism | `quantitative_trading_chan` | Chan Ch. 7 / 230-235 | future `QuoteEvent`, `OrderBookEvent`, `LatencyModel` |
| Capacity | `quantitative_trading_chan` | Chan Ch. 2/8 / 48-49, 238-243 | `CapacityModel`, `SmallCapLiquidityGate` |
| Short availability | `quantitative_trading_chan` | Chan Ch. 5 / 135 | `ShortAvailabilityModel` |
| Moving average smoke test | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo` | SAT Ch. 15 / 172-176; Hilpisch Ch. 4/6; Pardo Ch. 7-8 / 204-242 | `BACKTEST_VERTICAL_SLICE_V0_1` |
| Forecasting strategy | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch` | SAT Ch. 15 / 177-181; Hilpisch Ch. 5/10 | `FeaturePipeline` |
| Pairs mean reversion | `successful_algorithmic_trading`; `quantitative_trading_chan` | SAT Ch. 15 / 181-188; Chan Ch. 3/7 / 89-98, 182-200 | intraday strategy example |
| Parameter optimisation | `successful_algorithmic_trading`; `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 16 / 190-203; Hilpisch Ch. 4 / 174-178; Pardo Ch. 9-10 / 243-313; Chan Ch. 3/7 / 83-98, 170-181 | `ExperimentRunner`, `RunManifest`, `OptimizationRun` |
| Objective function | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 9 / 271-281 | `ObjectiveFunctionLibrary` |
| Optimization profile | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 10 / 300-312 | `OptimizationProfile`, `RobustnessAnalyzer` |
| Walk-forward analysis | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 11 / 314-345; Chan Ch. 3/7 / 85-88, 170-181 | `WalkForwardRunner`, `WindowPolicy` |
| Walk-forward efficiency | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 11 / 316-317, 343-344 | `WalkForwardEfficiencyMetric` |
| Cross-validation | `successful_algorithmic_trading`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 16 / 192-198; Pardo Ch. 11 / 314-345; Chan Ch. 3 / 85-88 | `Validation`; upgrade with Lopez de Prado |
| Grid search | `successful_algorithmic_trading`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | SAT Ch. 16 / 198-203; Pardo Ch. 9 / 246-250; Chan Ch. 7 / 173-181 | `ParameterGrid` |
| Overparameterization | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 13 / 388-389; Chan Ch. 3 / 83-88 | `ModelComplexityBudget` |
| Overscanning | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 13 / 389-391; Chan Ch. 3 / 83-98 | `SearchSpaceReview` |
| Trade sample size | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 13 / 386-388; Chan Ch. 3 / 84-85 | `SampleSizeGate` |
| Evaluation profile | `evaluation_optimization_trading_strategies_pardo` | Pardo Ch. 14 / 403-408 | `EvaluationProfile` |
| Trade profile | `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Pardo Ch. 14 / 403-408; Chan Ch. 5 / 132-137 | `LivePerformanceProfile` |
| Logging and monitoring | `python_for_algorithmic_trading_hilpisch`; `evaluation_optimization_trading_strategies_pardo`; `quantitative_trading_chan` | Hilpisch Ch. 7 / 362-370; Ch. 10 / 491-509; Pardo Ch. 14 / 394-413; Chan Ch. 5 / 132-137 | `Monitoring`, `Ledger`, `ShadowTradingMonitor` |
| Deployment | `python_for_algorithmic_trading_hilpisch`; `quantitative_trading_chan` | Hilpisch Ch. 2 / 74-92; Ch. 10 / 491-509; Chan Ch. 4 / 116-118 | `Deployment`, `OperationalRunbook` |

## Machine Trading Additions

Estas filas amplian el indice global con los conceptos especificos de `machine_trading_chan`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Backtest/live shared decision core | `machine_trading_chan` | Ch. 1 / 17, 22-25 | `DecisionCore`, `ReplayLiveEquivalence` |
| Primary auction prices | `machine_trading_chan` | Ch. 1 / 19; Ch. 6 / 198-200 | `PrimaryAuctionPricePolicy` |
| Executable price gate | `machine_trading_chan` | Ch. 3 / 76-79; Ch. 6 / 198-211; Ch. 7 / 223-226 | `ExecutablePriceGate`, `TradeVsQuoteFillAudit` |
| BBO/NBBO quote policy | `machine_trading_chan` | Ch. 1 / 19-20; Ch. 6 / 193-200 | `BBOQuotePolicy`, `NBBOState` |
| Same-timestamp tick ordering | `machine_trading_chan` | Ch. 5 / 151-153; Ch. 6 / 193-198, 205-211 | `EventClock`, `SameTimestampPolicy` |
| Factor risk vs alpha | `machine_trading_chan` | Ch. 2 / 43-45 | `FactorExposureReport` |
| Predictive factor model | `machine_trading_chan` | Ch. 2 / 45-57, 69-71 | `FactorResearchPipeline`, `CrossSectionalRanker` |
| Liquidity factor by universe | `machine_trading_chan` | Ch. 2 / 64-65 | `SmallCapLiquiditySegmentation` |
| Short interest/DTC factor | `machine_trading_chan` | Ch. 2 / 63-64 | `ShortInterestFeature` |
| Statistical PCA factors | `machine_trading_chan` | Ch. 2 / 65-69 | `StatisticalFactorModel` |
| AR/ARMA/VAR/VEC models | `machine_trading_chan` | Ch. 3 / 75-87 | `TimeSeriesResearch`, `LagSelectionPolicy` |
| Kalman/state-space models | `machine_trading_chan` | Ch. 3 / 87-96 | `KalmanStateEstimator` |
| ML feature normalization | `machine_trading_chan` | Ch. 4 / 125-127 | `FeatureNormalizationPolicy`, `NormalizerFitPolicy` |
| ML model selection ledger | `machine_trading_chan` | Ch. 4 / 99-132 | `MLExperimentRegistry`, `RandomSeedLedger` |
| Scheduled event backtesting | `machine_trading_chan` | Ch. 5 / 149-153 | `EventCalendar`, `ScheduledEventFeed` |
| Path-dependent backtest | `machine_trading_chan` | Ch. 5 / 153-157 | `PathDependentBacktest` |
| Intraday latency model | `machine_trading_chan` | Ch. 6 / 175-179 | `LatencyModel` |
| Order routing / venue model | `machine_trading_chan` | Ch. 6 / 179-190 | `RoutingModel`, `VenueModel` |
| Adverse selection audit | `machine_trading_chan` | Ch. 6 / 190-193 | `AdverseSelectionAudit` |
| Intraday BBO/Level 2 backtesting | `machine_trading_chan` | Ch. 6 / 193-198 | `IntradayBacktestEngine`, `OrderBookReconstructor` |
| Low-frequency data audit | `machine_trading_chan` | Ch. 6 / 198-200 | `DataFrequencyAudit` |
| Order flow builder | `machine_trading_chan` | Ch. 6 / 202-211; Ch. 7 / 223-226 | `OrderFlowBuilder`, `AggressorTagPolicy` |
| Bulk volume classification | `machine_trading_chan` | Ch. 6 / 203-210 | `OrderFlowEstimator` |
| Order book imbalance | `machine_trading_chan` | Ch. 6 / 212-214 | `OrderBookImbalanceFeature` |
| Strategy decay monitor | `machine_trading_chan` | Ch. 8 / 235-237 | `StrategyDecayMonitor`, `StrategyLifecycle` |


## Algorithmic Trading Additions

Estas filas amplian el indice global con los conceptos especificos de `algorithmic_trading_chan`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Automated execution readiness | `algorithmic_trading_chan` | Ch. 1 / 19-56 | `ReplayLiveEquivalence`, `ExecutionAdapterContract` |
| Backtest platform selection | `algorithmic_trading_chan` | Ch. 1 / 43-56 | `BacktestPlatformDecisionRecord` |
| Hypothesis testing for strategies | `algorithmic_trading_chan` | Ch. 1 / 34-40 | `StatisticalValidationReport` |
| Mean reversion half-life | `algorithmic_trading_chan` | Ch. 2 / 64-66 | `HalfLifeEstimator` |
| ADF/Hurst/variance ratio | `algorithmic_trading_chan` | Ch. 2 / 59-68 | `StationarityTestSuite` |
| CADF/Johansen cointegration | `algorithmic_trading_chan` | Ch. 2 / 68-78 | `CointegrationResearch` |
| Bollinger mean-reversion rule | `algorithmic_trading_chan` | Ch. 3 / 88-90 | `MeanReversionStrategyTemplate` |
| Kalman dynamic hedge ratio | `algorithmic_trading_chan` | Ch. 3 / 92-100 | `KalmanStateEstimator` |
| Threshold data-error guard | `algorithmic_trading_chan` | Ch. 3 / 101-104 | `BadTickFilter`, `ThresholdSignalAudit` |
| Buy-on-gap model | `algorithmic_trading_chan` | Ch. 4 / 110-114 | `GapStrategyTemplate` |
| News/intraday momentum | `algorithmic_trading_chan` | Ch. 7 / 173-181 | `EventState`, `NewsEventFeed` |
| HFT/order-book imbalance warning | `algorithmic_trading_chan` | Ch. 7 / 182-186 | `OrderBookImbalanceFeature`, `HFTReadinessGate` |
| CPPI risk control | `algorithmic_trading_chan` | Ch. 8 / 198-200 | `CapitalProtectionPolicy` |
| Risk indicators | `algorithmic_trading_chan` | Ch. 8 / 202-204 | `RiskIndicatorRegistry` |

## Kaufman Additions

Estas filas amplian el indice global con los conceptos especificos de `trading_systems_methods_kaufman`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Strategy family taxonomy | `trading_systems_methods_kaufman` | Ch. 5-13 / 89-333 | `StrategyTemplateRegistry` |
| Parameter type classification | `trading_systems_methods_kaufman` | Ch. 21 / 505-506 | `ParameterSpaceRegistry` |
| Parameter spacing policy | `trading_systems_methods_kaufman` | Ch. 21 / 505-510 | `ParameterGridPolicy` |
| Optimization map/surface review | `trading_systems_methods_kaufman`; `evaluation_optimization_trading_strategies_pardo` | Kaufman Ch. 21 / 510-517; Pardo Ch. 10 / 300-312 | `OptimizationSurfaceReport` |
| Robust plateau vs isolated peak | `trading_systems_methods_kaufman`; `evaluation_optimization_trading_strategies_pardo` | Kaufman Ch. 21 / 510-517; Pardo Ch. 10 / 300-312 | `RobustnessAnalyzer` |
| Step-forward testing | `trading_systems_methods_kaufman`; `evaluation_optimization_trading_strategies_pardo` | Kaufman Ch. 21 / 517-519; Pardo Ch. 11 / 314-345 | `WalkForwardRunner` |
| Rule-change contamination | `trading_systems_methods_kaufman` | Ch. 21 / 519-520 | `ResearchChangeLedger` |
| Price shock audit | `trading_systems_methods_kaufman` | Ch. 21-22 / 546-565 | `PriceShockStressTest` |
| Day-trading cost sensitivity | `trading_systems_methods_kaufman` | Ch. 16 / 419-435 | `IntradayCostGate`, `ExecutionRealismGate` |
| Opening range breakout benchmark | `trading_systems_methods_kaufman` | Ch. 16 / 428-435 | `OpeningRangeBenchmarkStrategy` |
| System trade-off profile | `trading_systems_methods_kaufman` | Ch. 22 / 574-579 | `TradeProfileReport` |
| Similarity of systems | `trading_systems_methods_kaufman` | Ch. 22 / 583-586 | `StrategyCorrelationReport` |
| Liquidity execution cost | `trading_systems_methods_kaufman` | Ch. 23 / 589-591 | `LiquidityGate`, `SlippageModel` |
| Risk of ruin | `trading_systems_methods_kaufman` | Ch. 23 / 614-617 | `RuinAnalysis` |
| Optimal f / compounding | `trading_systems_methods_kaufman` | Ch. 23 / 617-626 | `PositionSizingStressTest` |

## Hasbrouck Additions

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Efficient price vs transaction price | `empirical_market_microstructure_hasbrouck` | Ch. 7-8 / 44-63 | `EfficientPriceEstimator` |
| Bid/ask bounce | `empirical_market_microstructure_hasbrouck` | Ch. 3 / 12-15 | `BidAskBounceAudit` |
| Trade direction classifier | `empirical_market_microstructure_hasbrouck` | Ch. 10, 13 / 78, 93 | `TradeDirectionClassifier` |
| Order flow VAR | `empirical_market_microstructure_hasbrouck` | Ch. 12-13 / 86-102 | `OrderFlowVAR` |
| Price impact decomposition | `empirical_market_microstructure_hasbrouck` | Ch. 13-14 / 93-106 | `PriceImpactModel` |
| Limit order execution uncertainty | `empirical_market_microstructure_hasbrouck` | Ch. 18-20 / 124-145 | `LimitFillProbability` |
| Liquidity measures | `empirical_market_microstructure_hasbrouck` | Ch. 22 / 161-164 | `LiquidityMetricLibrary` |

## Carver Additions

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Forecast scaling | `systematic_trading_carver` | Ch. 7-8, App. D | `ForecastScaler` |
| Forecast combination | `systematic_trading_carver` | Ch. 8 | `ForecastCombiner` |
| Forecast cap | `systematic_trading_carver` | Ch. 8 | `ForecastCap` |
| Volatility targeting | `systematic_trading_carver` | Ch. 9 | `VolatilityTargetPolicy` |
| Forecast to position | `systematic_trading_carver` | Ch. 10 | `ForecastToTargetPosition` |
| Instrument weights | `systematic_trading_carver` | Ch. 11 | `InstrumentWeightPolicy` |
| Diversification multiplier | `systematic_trading_carver` | Ch. 11, App. D | `DiversificationMultiplier` |
| Cost-aware speed policy | `systematic_trading_carver` | Ch. 12 | `TradeSpeedPolicy` |

## Johnson DMA Additions

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Parent/child order execution | `algorithmic_trading_and_dma_johnson` | Ch. 5, 11 / 115-160, 311-337 | `ParentOrder`, `ChildOrder` |
| Order instructions | `algorithmic_trading_and_dma_johnson` | Ch. 4 / 83-112 | `OrderInstruction` |
| TWAP/VWAP/POV/IS | `algorithmic_trading_and_dma_johnson` | Ch. 5 / 120-138 | `ExecutionAlgorithmLibrary` |
| Pre/post trade TCA | `algorithmic_trading_and_dma_johnson` | Ch. 6 / 161-186 | `TCAModel` |
| Efficient trading frontier | `algorithmic_trading_and_dma_johnson` | Ch. 7 / 192-199 | `ExecutionOptimizer` |
| Aggressiveness and signalling risk | `algorithmic_trading_and_dma_johnson` | Ch. 8 / 234-238 | `AggressivenessPolicy` |
| Hidden liquidity | `algorithmic_trading_and_dma_johnson` | Ch. 8 / 247-250 | `HiddenLiquidityModel` |
| Routing and OMS infrastructure | `algorithmic_trading_and_dma_johnson` | Ch. 11 / 311-337 | `Router`, `OMS`, `BrokerAdapter` |

## Davey Additions

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Strategy factory | `building_winning_algorithmic_trading_systems_davey` | Ch. 9-17 / 79-152 | `StrategyFactory` |
| Limited feasibility test | `building_winning_algorithmic_trading_systems_davey` | Ch. 12 / 103-114 | `LimitedTestRun` |
| Walk-forward development | `building_winning_algorithmic_trading_systems_davey` | Ch. 13, 18 / 115-128, 155-162 | `WalkForwardRunner` |
| Monte Carlo robustness | `building_winning_algorithmic_trading_systems_davey` | Ch. 14, 19 / 129-132, 163-174 | `MonteCarloRobustness` |
| Incubation / shadow run | `building_winning_algorithmic_trading_systems_davey` | Ch. 14, 19 | `ShadowTradingHarness` |
| Strategy documentation | `building_winning_algorithmic_trading_systems_davey` | Ch. 17 / 147-152 | `ResearchLedger` |
| Live monitoring | `building_winning_algorithmic_trading_systems_davey` | Ch. 23-24 / 205-232 | `LivePerformanceMonitor` |

## Strimpel Cookbook Additions

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| OpenBB/Nasdaq data recipes | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 1 | `ExternalDataAdapterPrototype` |
| pandas feature transforms | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 2 | `FeaturePipelinePrototype` |
| VectorBT prototype | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 6 | `VectorizedPrototype` |
| Zipline reference backtest | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 7 | `ReferenceEventBacktest` |
| Alphalens/Pyfolio analytics | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 8-9 | `AnalyticsReference` |
| IB broker API reference | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 10-11 | `BrokerAdapterReference` |
| Live deployment recipes | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 12 | `LiveStrategyRunnerReference` |
| ArcticDB/tick/execution storage | `python_for_algorithmic_trading_cookbook_strimpel` | Ch. 13 | `TickStoreReference`, `ExecutionLedger` |
## Notas Para Agentes

- `successful_algorithmic_trading` es mejor para entender el flujo `Market/Signal/Order/Fill`.
- `python_for_algorithmic_trading_hilpisch` es mejor para entorno Python, research vectorizado, clases event-based simples, streaming y deployment.
- `evaluation_optimization_trading_strategies_pardo` es mejor para protocolo de desarrollo, optimizacion, walk-forward, overfitting operativo y comparacion backtest/shadow/live.
- `quantitative_trading_chan` es mejor para backtesting practico, costes, paper trading, sizing/risk, capacity y advertencias small caps.
- `machine_trading_chan` es mejor para factores, ML, time-series, microestructura intradia, order flow, executable prices y strategy decay.
- `algorithmic_trading_chan` es mejor para unir estrategia, backtest y ejecucion automatizada con ejemplos de mean reversion, momentum intradia y riesgo.
- 	rading_systems_methods_kaufman es mejor para taxonomia de sistemas, parametros, testing, optimizacion, liquidez y riesgo.
- empirical_market_microstructure_hasbrouck es mejor para trades/quotes, order flow, spread, impact y limit orders.
- lgorithmic_trading_and_dma_johnson es mejor para order types, DMA, execution algorithms, TCA, routing e infraestructura.
- systematic_trading_carver es mejor para forecasts, volatility targeting, position sizing, portfolio construction y costes.
- uilding_winning_algorithmic_trading_systems_davey es mejor para strategy factory, walk-forward, Monte Carlo, incubacion y live monitoring.
- python_for_algorithmic_trading_cookbook_strimpel es mejor como recetario Python para datos, prototipos, analytics, IB API y live recipes.
- Para arquitectura profesional, cruzar con NautilusTrader y LEAN.
- Para small caps, completar fills/costes con Harris, Hasbrouck y Johnson.
- Para validacion avanzada, completar con Lopez de Prado, PBO y DSR.







