# Concept Index - Trading Systems, 2nd Edition - Jaekle/Tomasini

Indice orientado a agentes. Paginas aproximadas segun TOC local.

## Menu

- [Proceso de desarrollo](#proceso-de-desarrollo)
- [Datos y sesgos](#datos-y-sesgos)
- [Optimizacion y robustez](#optimizacion-y-robustez)
- [Exits y diagnosticos de trade](#exits-y-diagnosticos-de-trade)
- [Position sizing y portfolio](#position-sizing-y-portfolio)
- [Uso recomendado en TSIS](#uso-recomendado-en-tsis)

## Proceso de desarrollo

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Sistema como reglas automaticas | 22-28 | `StrategySpec` sin discrecionalidad |
| Entry formula / exit formula / money management | 29-31 | Separacion `EntryRule`, `ExitPolicy`, `SizingModel` |
| Timeframe selection | 30-31 | `TimeframePolicy`, coste operativo y riesgo |
| Step-by-step system development | 55-98 | `StrategyDevelopmentWorkflow` |
| Trust in system after tests | 98 | `ResearchGovernance`, no parar por primer DD |
| Simple robust system example | 153-179 | Benchmark de robustez y parsimonia |

## Datos y sesgos

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Closing/open price vendor differences | 32 | `DataQualityGate` |
| Session differences | 32 | `SessionCalendar`, `MarketClock` |
| Corporate actions and delistings | 32-33 | `CorporateActions`, `DelistingEvents` |
| Futures continuous contracts | 33-34 | `ContinuousContractPolicy` |
| Perpetual contracts are artificial | 34 | No confundir serie ajustada con ejecutable |
| Data length | 34-39 | `SampleSizeGate` |
| Survivorship bias in stocks | 9, 315 | `PointInTimeUniverse` |
| Data supplier selection | 157-158, 315 | `DataVendorAudit` |

## Optimizacion y robustez

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Rule complexity / degrees of freedom | 36-39 | `ModelComplexityBudget` |
| Optimization | 39-41 | `OptimizationRun` |
| Walk-forward analysis | 41-43, 180-187 | `WalkForwardRunner` |
| Robustness | 44-46 | `RobustnessAnalyzer` |
| Stability diagrams | 64-71 | `ParameterStabilityMap` |
| Out-of-sample deterioration | 9 | `OOSDecayReport` |
| Market data bias | 9 | `DataBiasReview` |
| Over-fitting | 9, 186-187, 317-318 | `OverfittingGuard` |
| Rule complexity via polynomial fitting | 9 | `ComplexityExplanation` |
| Timescale analysis | 100-105 | `TimeframeStressTest` |
| Monte Carlo analysis | 105-120 | `MonteCarloTradeSequence` |
| Anchored WFA | 180-182 | `AnchoredWindowPolicy` |
| Rolling WFA | 181-187 | `RollingWindowPolicy` |
| Sample size / market structure | 187+ | `WindowAdequacyGate` |

## Exits y diagnosticos de trade

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| MAE | 79-84 | `MAEReport`, stop calibration |
| MFE | 88-90, 97 | `MFEReport`, trailing/profit target review |
| Risk stop loss | 83-86 | `StopLossPolicy` |
| Trailing stop | 86-88, 97 | `TrailingStopPolicy` |
| Profit target | 88-91 | `ProfitTargetPolicy` |
| Exit impact on trade distribution | 95-98 | `ExitImpactReport` |
| Gap overrun of stop | 96-98 | `GapSlippageRisk`, `StopFillModel` |
| Trade scatter graph | 95-98 | `TradeDistributionVisualization` |

## Position sizing y portfolio

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Risk management vs money management | 9, 95, Ch. 7 | `RiskModel` vs `SizingModel` |
| Maximum drawdown MM | Ch. 7 | `DrawdownBasedSizing` |
| Fixed fractional | Ch. 7 | `FixedFractionalSizing` |
| Fixed ratio | Ch. 7 | `FixedRatioSizing` |
| MC of position-sized system | Ch. 7 | `SizingMonteCarlo` |
| Dynamic portfolio construction | Ch. 8 | `PortfolioConstruction` |
| Equity-line correlation | Ch. 8 | `EquityCorrelationAnalyzer` |
| Equity-line crossover | Ch. 8 | `StrategyActivationPolicy` |
| WFA activator | Ch. 8 | `WalkForwardActivator` |
| Largest losing trade/streak/drawdown | Ch. 8 | `PortfolioStressMetrics` |
| Stock portfolio ranking | Ch. 9 | `SignalRankingPolicy` |
| Max simultaneous positions | 303-315 | `PositionCapacityPolicy` |
| Loss aversion | 312-314 | `OperatorPsychologyNote`, live governance |
| Daily execution modes | 314-316 | `DailySignalExecutionRunbook` |

## Uso recomendado en TSIS

| Tarea de agente | Consultar |
|---|---|
| Disenar workflow de desarrollo de estrategia | Caps. 2-3 |
| Crear diagnostics de exits | Cap. 3 MAE/MFE |
| Disenar WFA anchored/rolling | Cap. 6 |
| Probar robustez de timeframe | Cap. 4 |
| Crear Monte Carlo basico de trades | Cap. 4 y 7 |
| Crear sizing models | Cap. 7 |
| Crear portfolio rotation/ranking | Caps. 8-9 |
| Revisar survivorship/universos | Cap. 9 |
| Crear runbook de ejecucion diaria | Cap. 9.10 |
