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
## Jaekle/Tomasini Additions

Estas filas amplian el indice global con conceptos de `trading_systems_urban_jaekle`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Strategy development workflow | `trading_systems_urban_jaekle` | Caps. 2-3 / 29-98 | `StrategyDevelopmentWorkflow` |
| Parameter stability map | `trading_systems_urban_jaekle` | Cap. 3 / 64-71 | `ParameterStabilityMap` |
| MAE/MFE diagnostics | `trading_systems_urban_jaekle` | Cap. 3 / 79-98 | `MAE_MFE_Report` |
| Timeframe stress test | `trading_systems_urban_jaekle` | Cap. 4 / 100-105 | `TimeframeStressTest` |
| Anchored/Rolling WFA | `trading_systems_urban_jaekle` | Cap. 6 / 180-187 | `WalkForwardRunner`, `WindowPolicy` |
| Position sizing suite | `trading_systems_urban_jaekle` | Cap. 7 | `SizingModel` |
| Dynamic portfolio composition | `trading_systems_urban_jaekle` | Cap. 8 | `StrategyActivationPolicy` |
| Stock portfolio survivorship | `trading_systems_urban_jaekle` | Cap. 9 | `PointInTimeUniverse` |

## Dolzhenko Additions

Estas filas amplian el indice global con conceptos de `algorithmic_trading_systems_strategies_dolzhenko`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Theory vs Strategy | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 3 / 75-77 | `StrategyIdea`, `StrategyInstance` |
| Indicator/Signal/Condition domain | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 3 / 72-80 | `DomainModel`, `ConditionTree` |
| Backtest/live shared core | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 263-264 | `BacktestLiveSharedCore` |
| Strategy runtime context | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 264-266 | `StrategyRuntimeContext` |
| Market data and order status events | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 264-267 | `MarketDataEvent`, `OrderStatusEvent` |
| Signal conflict policy | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 267 | `SignalConflictPolicy` |
| Indicator warmup state | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 267-280 | `IndicatorWarmupState` |
| Position state machine | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 8 / 280-285 | `PositionStateMachine` |
| Exchange gateway/message bus | `algorithmic_trading_systems_strategies_dolzhenko` | Cap. 4 / 142-144 | `ExecutionAdapter`, `EventBus` |

## Aldridge Additions

Estas filas amplian el indice global con conceptos de `high_frequency_trading_aldridge`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Limit order book | `high_frequency_trading_aldridge` | Ch. 3 / 69-76 | `OrderBookSnapshot` |
| Passive/aggressive orders | `high_frequency_trading_aldridge` | Ch. 3 / 77-79 | `OrderAggressiveness` |
| Quote/trade schema | `high_frequency_trading_aldridge` | Ch. 4 / 91-94 | `QuoteEvent`, `TradeEvent` |
| Bid-ask bounce | `high_frequency_trading_aldridge` | Ch. 4 / 98-102 | `BidAskBounceFilter` |
| HF sampling policy | `high_frequency_trading_aldridge` | Ch. 4 / 109-113 | `SamplingPolicy` |
| Trade direction classifier | `high_frequency_trading_aldridge` | Ch. 4 / 116-121 | `TradeClassifier` |
| Market impact model | `high_frequency_trading_aldridge` | Ch. 5 / 132-153; Ch. 15 | `MarketImpactModel` |
| Capacity and alpha decay | `high_frequency_trading_aldridge` | Ch. 6 / 178-183 | `CapacityModel`, `AlphaDecayMonitor` |
| Execution algorithms | `high_frequency_trading_aldridge` | Ch. 15 | `ExecutionPolicy`, `ParticipationCap` |
| Online core engine | `high_frequency_trading_aldridge` | Ch. 16 / 397-401 | `OnlineCoreEngine` |
## Quantum Finance Additions

Estas filas amplian el indice global con conceptos especificos de `quantum_finance_raymond_lee`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Quantum Price Levels | `quantum_finance_raymond_lee` | Ch. 5 / 116-140 | `QuantumPriceLevelFeature` |
| Forecast model vs trading policy | `quantum_finance_raymond_lee` | Ch. 11-13 / 325-417 | `ForecastModelRegistry`, `DecisionPolicy` |
| Genetic search for alpha ideas | `quantum_finance_raymond_lee` | Ch. 7 / 207-213 | future `GeneticSearchRunner` |
| Fuzzy feature layer | `quantum_finance_raymond_lee` | Ch. 7 / 214-229 | future `FuzzyFeatureLayer` |
| Actor-critic RL trading policy | `quantum_finance_raymond_lee` | Ch. 13 / 398-417 | future `OfflineRLPolicyLab`, `RewardFunctionSpec` |

## Masters Additions

Estas filas amplian el indice global con conceptos especificos de `testing_tuning_market_trading_systems_masters`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Stationarity profile | `testing_tuning_market_trading_systems_masters` | Ch. 2 / 21-24 | `StationarityProfile` |
| Feature entropy report | `testing_tuning_market_trading_systems_masters` | Ch. 2 / 25-45 | `FeatureInformationReport` |
| Training bias estimate | `testing_tuning_market_trading_systems_masters` | Ch. 4-5 / 115-161 | `TrainingBiasEstimate` |
| Selection bias audit | `testing_tuning_market_trading_systems_masters` | Ch. 5 / 157-161 | `SelectionBiasAudit` |
| Walkforward leakage buffers | `testing_tuning_market_trading_systems_masters` | Ch. 5 / 168-176 | `TemporalLeakageGate`, `WalkForwardWindowPolicy` |
| Return granularity policy | `testing_tuning_market_trading_systems_masters` | Ch. 6 / 235-240 | `ReturnGranularityPolicy` |
| Bootstrap confidence bounds | `testing_tuning_market_trading_systems_masters` | Ch. 6 / 254-283 | `BootstrapConfidenceBounds` |
| Permutation testing | `testing_tuning_market_trading_systems_masters` | Ch. 7 / 338-360 | `PermutationTestRunner` |

## Kaufman Website 5e Additions

Estas filas amplian el indice global con conceptos especificos de `trading_systems_methods_website_5e_kaufman`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Backtest expectations | `trading_systems_methods_website_5e_kaufman` | Ch. 1/21 / 38-43, 925-928 | `BacktestExpectationSpec` |
| Parameter schema and spacing | `trading_systems_methods_website_5e_kaufman` | Ch. 21 / 928-930 | `ParameterSchema` |
| Testing data integrity | `trading_systems_methods_website_5e_kaufman` | Ch. 21 / 930-936 | `DataFoundationPolicy` |
| Robustness surface | `trading_systems_methods_website_5e_kaufman` | Ch. 21 / 958-1001 | `RobustnessSurface`, `SensitivityNSpaceReport` |
| Price shock audit | `trading_systems_methods_website_5e_kaufman` | Ch. 21-22 / 990-995, 1012-1017 | `PriceShockAudit` |
| Small-cap liquidity gate | `trading_systems_methods_website_5e_kaufman` | Ch. 20/23 / 887, 1053-1054 | `SmallCapLiquidityGate` |
| Risk metric catalog | `trading_systems_methods_website_5e_kaufman` | Ch. 23 / 1054-1062 | `RiskMetricCatalog` |
| Position sizing and stops | `trading_systems_methods_website_5e_kaufman` | Ch. 23 / 1070-1081 | `PositionSizingPolicy`, `StopPolicy` |

## Software Engineering And Data Architecture Additions

Estas filas amplian el indice global con conceptos especificos de la tanda de arquitectura/ingenieria.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---:|---|
| Domain model in Python | `architecture_patterns_python_gregory` | Ch. 1 / 43-65 | `TSISDomainModel` |
| Repository and Unit of Work | `architecture_patterns_python_gregory` | Ch. 2/6 / 70-91, 156-172 | `RepositoryPort`, `UnitOfWork` |
| Aggregate consistency boundary | `architecture_patterns_python_gregory` | Ch. 7 / 177-203 | `BacktestRunAggregate` |
| Domain event bus | `architecture_patterns_python_gregory`; `fundamentals_software_architecture_2e_richards` | APP Ch. 8-11 / 212-295; FSA Ch. 15 / 414-511 | `DomainEventBus`, `EventDrivenArchitectureStyle` |
| CQRS read models | `architecture_patterns_python_gregory`; `fundamentals_software_architecture_2e_richards` | APP Ch. 12 / 297-318; FSA Ch. 20 / 683 | `ReadModelProjection` |
| Event time vs processing time | `streaming_systems_akidau`; `grokking_streaming_systems_fischer` | Akidau Ch. 1 / 23-35; Fischer Ch. 1-2 / 27-84 | `EventClockPolicy` |
| Watermarks and late data | `streaming_systems_akidau` | Ch. 2-3 / 59-122 | `WatermarkPolicy`, `LateDataPolicy` |
| Exactly-once/idempotent sinks | `streaming_systems_akidau`; `grokking_streaming_systems_fischer` | Akidau Ch. 5 / 149-170; Fischer Ch. 5 / 162-207 | `IdempotentSinkContract`, `EventDeliveryContract` |
| Backpressure | `grokking_streaming_systems_fischer` | Ch. 10 / 297-328 | `ReplayBackpressurePolicy` |
| Stateful computation | `grokking_streaming_systems_fischer` | Ch. 11 / 329-362 | `OnlineStateStore` |
| Data engineering lifecycle | `fundamentals_data_engineering_reis` | Ch. 2 / 60-108 | `TSISDataLifecycle` |
| Source systems / CDC / logs | `fundamentals_data_engineering_reis` | Ch. 5 / 225-240 | `SourceSystemContract`, `CDCIngestionPolicy` |
| Ingestion reliability | `fundamentals_data_engineering_reis` | Ch. 7 / 338-362 | `IngestionReliabilityPolicy`, `DeadLetterQueuePolicy` |
| Storage format and checksums | `database_internals_petrov` | Ch. 1/3 / 24-42, 67-84 | `CanonicalFileContract` |
| WAL/recovery/isolation | `database_internals_petrov` | Ch. 5 / 106-142 | `LedgerRecoveryPolicy`, `ConcurrentRunIsolation` |
| Consistency model | `database_internals_petrov` | Ch. 11 / 267-299 | `ConsistencyContract` |
| Architecture characteristics | `fundamentals_software_architecture_2e_richards` | Ch. 4-6 / 109-181 | `ArchitectureCharacteristicCatalog`, `ArchitectureFitnessFunction` |
| Modular monolith decision | `fundamentals_software_architecture_2e_richards` | Ch. 11 / 305-326 | `TSISModularMonolithDecision` |
| Architecture decision records | `fundamentals_software_architecture_2e_richards` | Ch. 21 / 692-723 | `ArchitectureDecisionRecord` |
| Architecture risk storming | `fundamentals_software_architecture_2e_richards` | Ch. 22 / 726-754 | `ArchitectureRiskRegister` |
| Deployment pipeline | `continuous_delivery_humble_farley` | Ch. 5 / 139-174 | `BacktesterDeliveryPipeline` |
| Acceptance/capacity gates | `continuous_delivery_humble_farley` | Ch. 8-9 / 221-282 | `AcceptanceTestGate`, `ReplayCapacityTest` |
| Database/data migrations | `continuous_delivery_humble_farley`; `test_driven_development_python_3e_percival` | CD Ch. 12 / 359-377; TDD Ch. 5/9 / 174-194, 374-378 | `DataSchemaMigrationPolicy` |
| Double-loop TDD | `test_driven_development_python_3e_percival` | Ch. 4 / 138-141 | `OutsideInTDDWorkflow` |
| Regression test harness | `test_driven_development_python_3e_percival`; `software_engineering_google_winters` | TDD Ch. 7 / 225-292; Google Ch. 11-14 / 343-500 | `RegressionTestHarness`, `TestSuiteStrategy` |
| Canonical documentation | `software_engineering_google_winters` | Ch. 3/10 / 82-118, 307-342 | `CanonicalDocsPolicy` |
| Code review policy | `software_engineering_google_winters` | Ch. 9 / 276-305 | `CodeReviewPolicy` |
| Fakes vs real implementations | `software_engineering_google_winters`; `architecture_patterns_python_gregory` | Google Ch. 13 / 419-453; APP Ch. 2-3 / 89-111 | `FakeVsRealTestDoublePolicy` |
| Dependency governance | `software_engineering_google_winters` | Ch. 21 / 684-729 | `DependencyGovernance` |
| CI/CD policy | `software_engineering_google_winters`; `continuous_delivery_humble_farley` | Google Ch. 23-24 / 766-823; CD Ch. 3/5 / 89-174 | `CICDPolicy` |

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








## Trading and Exchanges: Market Microstructure for Practitioners Additions

Estas filas amplian el indice global con conceptos especificos de `trading_and_exchanges_harris`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Market microstructure for practitioners | `trading_and_exchanges_harris` | Orderes, liquidez, costes, ejecucion | `VenueModel`, `ExecutionSimulator` |
| Bid-ask spread | `trading_and_exchanges_harris` | Liquidez y costes | `SpreadModel`, `ExecutablePriceGate` |
| Order type taxonomy | `trading_and_exchanges_harris` | Order instructions | `OrderType`, `TimeInForce` |
| Adverse selection | `trading_and_exchanges_harris` | Liquidity/cost chapters | `AdverseSelectionAudit` |
| Transaction cost analysis | `trading_and_exchanges_harris` | Trading costs | `TransactionCostAnalysis` |

## Building Applications with AI Agents Additions

Estas filas amplian el indice global con conceptos especificos de `building_applications_ai_agents_albada`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Agent workflow governance | `building_applications_ai_agents_albada` | Agent architecture/tool use | `AgentWorkflowProtocol` |
| RAG for TSIS reference library | `building_applications_ai_agents_albada` | RAG/memory | `ReferenceRetriever`, `GraphifyQueryWorkflow` |
| Agent evaluation harness | `building_applications_ai_agents_albada` | Evaluation/guardrails | `AgentEvaluationHarness` |

## Clean Architecture Additions

Estas filas amplian el indice global con conceptos especificos de `clean_architecture_anderson_rogerio`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Clean architecture boundary | `clean_architecture_anderson_rogerio`; `clean_architecture_robert_martin` | Architecture layers | `DomainCore`, `Adapters` |
| Dependency inversion for backtester | `clean_architecture_anderson_rogerio`; `clean_architectures_python_giordani` | Ports/adapters | `Port`, `Adapter` |

## Clean Architecture Additions

Estas filas amplian el indice global con conceptos especificos de `clean_architecture_robert_martin`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Policy/detail separation | `clean_architecture_robert_martin` | Clean architecture boundaries | `DomainCore`, `Adapters` |
| Boundary import tests | `clean_architecture_robert_martin` | Testing architecture | `BoundaryImportTest` |

## Clean Architectures in Python Additions

Estas filas amplian el indice global con conceptos especificos de `clean_architectures_python_giordani`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Python repository pattern | `clean_architectures_python_giordani`; `architecture_patterns_python_gregory` | Repositories/use cases | `LedgerRepository` |
| Python use case service | `clean_architectures_python_giordani` | Use cases | `BacktestRunUseCase` |

## Domain-Driven Design Additions

Estas filas amplian el indice global con conceptos especificos de `domain_driven_design_evans`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Ubiquitous language | `domain_driven_design_evans` | Model-driven design | `TSIS_BACKTEST_GLOSSARY` |
| Aggregate invariants | `domain_driven_design_evans` | Aggregates | `OrderAggregate`, `PortfolioAggregate` |
| Bounded context map | `domain_driven_design_evans` | Strategic design | `TSIS_BOUNDED_CONTEXT_MAP` |

## Introduction to Algorithms, 4th Edition Additions

Estas filas amplian el indice global con conceptos especificos de `introduction_to_algorithms_cormen_4e`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Priority event queue | `introduction_to_algorithms_cormen_4e` | Heaps/priority queues | `PriorityEventQueue` |
| Complexity budget | `introduction_to_algorithms_cormen_4e` | Algorithm analysis | `ComplexityBudget` |
| Pipeline dependency graph | `introduction_to_algorithms_cormen_4e` | Graph algorithms | `PipelineDependencyGraph` |

## Mastering AI System Design Additions

Estas filas amplian el indice global con conceptos especificos de `mastering_ai_system_design_sreepada`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| AI model registry | `mastering_ai_system_design_sreepada` | AI lifecycle/MLOps | `ModelRegistry` |
| Feature store governance | `mastering_ai_system_design_sreepada`; `machine_trading_chan` | Feature/data design | `PointInTimeFeatureStore` |
| Model drift monitoring | `mastering_ai_system_design_sreepada` | Monitoring | `DriftMonitor` |

## The Clean Coder Additions

Estas filas amplian el indice global con conceptos especificos de `the_clean_coder_martin`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Definition of Done | `the_clean_coder_martin`; `continuous_delivery_humble_farley` | Professionalism/testing | `ModuleAcceptanceChecklist` |
| Agent commitment ledger | `the_clean_coder_martin` | Commitments | `TaskCommitmentLedger` |

## Advanced Algorithmic Trading Additions

Estas filas amplian el indice global con conceptos especificos de `advanced_algorithmic_trading_tawcer`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Advanced benchmark strategy | `advanced_algorithmic_trading_tawcer`; `successful_algorithmic_trading` | Strategy/model examples | `StrategyBenchmarkSuite` |
| Time-series research module | `advanced_algorithmic_trading_tawcer`; `machine_trading_chan` | Time-series/statistical models | `TimeSeriesResearch` |

## A Guide to Creating a Successful Algorithmic Trading Strategy Additions

Estas filas amplian el indice global con conceptos especificos de `guide_successful_algorithmic_trading_strategy_kaufman`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Strategy creation checklist | `guide_successful_algorithmic_trading_strategy_kaufman`; `quantitative_trading_chan` | Strategy design | `StrategyIntakeChecklist` |
| Rule-to-spec conversion | `guide_successful_algorithmic_trading_strategy_kaufman` | Rules/testing | `StrategySpecification` |

## Machine Learning for Algorithmic Trading, 2nd Edition Additions

Estas filas amplian el indice global con conceptos especificos de `machine_learning_algorithmic_trading_jansen_2e`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Alpha factor library | `machine_learning_algorithmic_trading_jansen_2e`; `machine_trading_chan` | Data/features | `AlphaFactorLibrary` |
| ML experiment registry | `machine_learning_algorithmic_trading_jansen_2e` | Model selection | `MLExperimentRegistry` |
| Leakage-aware ML validation | `machine_learning_algorithmic_trading_jansen_2e`; `testing_tuning_market_trading_systems_masters` | Validation/backtesting | `PurgedValidationSplitter` |

## Designing Data-Intensive Applications Additions

Estas filas amplian el indice global con conceptos especificos de `designing_data_intensive_applications_kleppmann`.

| Concepto TSIS | Fuente primaria actual | Seccion/Paginas | Artefacto recomendado |
|---|---|---|---|
| Event log as source of truth | `designing_data_intensive_applications_kleppmann`; `streaming_systems_akidau` | Logs/batch/stream | `EventLog`, `StateRebuilder` |
| Schema evolution | `designing_data_intensive_applications_kleppmann`; `fundamentals_data_engineering_reis` | Encoding/evolution | `SchemaVersioning` |
| Idempotent ledger writes | `designing_data_intensive_applications_kleppmann`; `database_internals_petrov` | Consistency/transactions | `IdempotencyKey`, `LedgerRepository` |
