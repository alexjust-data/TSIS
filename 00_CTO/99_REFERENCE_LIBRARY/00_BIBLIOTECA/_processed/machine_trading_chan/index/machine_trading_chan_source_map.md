# Source Map - Machine Trading

**book_id:** `machine_trading_chan`  
**Fuente local:** `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\00_BIBLIOTECA\Machine_Trading_-_Ernest_P_Chan.pdf`  
**Uso:** mapa pagina/seccion -> que estudiar -> componente TSIS.  
**Nota:** este archivo es derivado. No contiene texto completo del PDF.

## Menu

- [Como Usar Este Mapa](#como-usar-este-mapa)
- [Mapa Por Seccion](#mapa-por-seccion)
- [Rutas De Lectura TSIS](#rutas-de-lectura-tsis)
- [Prioridad Para TSIS Backtest Engine](#prioridad-para-tsis-backtest-engine)

## Como Usar Este Mapa

1. Abrir primero `machine_trading_chan_concept_index.md`.
2. Si el concepto afecta al trabajo actual, abrir el resumen.
3. Solo si hace falta mas detalle, abrir el PDF original en las paginas indicadas.
4. No copiar texto del PDF a artefactos persistentes; crear solo notas derivadas, tests o contratos.

## Mapa Por Seccion

| Paginas PDF | Seccion | Que estudiar | Encaje TSIS |
|---:|---|---|---|
| 11-16 | Preface | Intencion practica del libro y alcance | `SourceContext` |
| 17 | Algorithmic trading flow | Mismo bloque conceptual para backtest y live | `DecisionCore`, `BacktestLiveEquivalence` |
| 18-21 | Historical market data | Survivorship-free, delisted stocks, CRSP, BBO, auction data, news/fundamentals | `DataFoundation`, `PointInTimeUniverse` |
| 21-22 | Live market data | Diferencia entre datos diarios e intradia, latencia de feeds | `LiveDataAdapter`, `LatencyModel` |
| 22-27 | Backtesting and trading platforms | Riesgo de reescribir logica distinta para live; plataformas y lenguajes | `ArchitectureReference`, `BrokerAdapter` |
| 28-30 | Performance metrics | CAGR, Sharpe, Calmar, max drawdown, leverage unlevered | `MetricsEngine` |
| 30-39 | Portfolio optimization | Kelly, Markowitz, min variance, risk parity y tail risk | `CapitalAllocator`, `RiskSizingModel` |
| 43-45 | Factor models intro | Alpha vs factor risk, capacidad y diversificacion | `FactorExposureReport` |
| 45-49 | Time-series factors | Fama-French, HML/SMB/UMD, prediccion vs explicacion | `FactorResearchPipeline` |
| 49-57 | Cross-sectional factors | Fundamentales point-in-time y regression/ranking | `PointInTimeFeatureStore`, `CrossSectionalRanker` |
| 57-63 | Options-implied factors | Variables derivadas de opciones para predecir stocks | future `OptionsFeatureStore` |
| 63-64 | Short interest | SIR vs DTC y cambio de signo por regimen | `ShortInterestFeature`, `RegimeMonitor` |
| 64-65 | Liquidity | El signo del efecto depende del universo | `SmallCapLiquiditySegmentation` |
| 65-69 | Statistical factors | PCA y factores estadisticos para corto plazo | `StatisticalFactorModel` |
| 69-71 | Putting factors together | Multisort, collinearity, factor-neutral grouping | `FactorCombiner`, `FactorNeutralPortfolio` |
| 75-83 | AR/ARMA | Lag selection, BIC, midprice y caveat de ejecucion | `TimeSeriesResearch`, `ExecutablePriceGate` |
| 83-87 | VAR/VEC | Modelos multiactivo y neutralidad sectorial | `MultiAssetStateModel` |
| 87-96 | State space/Kalman | Estados ocultos, hedge ratio dinamico, overfitting por noise parameters | `KalmanStateEstimator` |
| 99-102 | AI intro | Data mining, no estacionariedad, black-box risk | `MLResearchPolicy` |
| 102-108 | Stepwise/regression trees | Feature selection, train/test, arboles y overfitting | `FeatureSelection`, `ModelComplexityBudget` |
| 108-114 | Cross-validation/ensembles | CV, bagging, random forest, boosting | `ValidationSplitter`, `EnsembleModelPolicy` |
| 114-117 | Classification/SVM | Clasificacion de retornos y kernels | `ClassifierModelRegistry` |
| 117-121 | HMM | Regimenes ocultos, decoding, limitaciones online | `RegimeStateModel` |
| 121-125 | Neural networks | Random seeds, early stopping, arquitectura simple | `RandomSeedLedger`, `ModelSelectionLedger` |
| 125-127 | Data aggregation/normalization | Agregar stocks tras normalizar predictors y response | `FeatureNormalizationPolicy` |
| 127-131 | Stock selection with ML | Seleccion de factores fundamentales y holding period | `StockSelectionResearch` |
| 131-132 | AI summary | Empezar simple; feature richness importa mas que complejidad | `ModelComplexityBudget` |
| 135-149 | Volatility/options | Volatilidad, GARCH, implied vs realized vol | future `VolatilityResearch` |
| 149-153 | Event-driven options | Anuncios programados, entry/exit time, bid/ask | `EventCalendar`, `BidAskExecutionPolicy` |
| 153-157 | Gamma scalping | Path dependence y combinacion underlying/options | `PathDependentBacktest` |
| 158-168 | Dispersion trading | Multi-leg, neutralidad, seleccion diaria, datos grandes | future `MultiLegBacktest` |
| 175-179 | Intraday and latency | Capacidad, quote size, submission/status/data latency | `LatencyModel`, `CapacityModel` |
| 179-190 | Order types/routing/dark pools | NBBO, Reg NMS, ISO/IOC, dark pool risks | `RoutingModel`, `VenueModel` |
| 190-193 | Adverse selection | Filled vs unfilled PnL, toxic flow, order type choice | `AdverseSelectionAudit` |
| 193-198 | Backtesting intraday strategies | BBO, level 2, ITCH, order book reconstruction | `IntradayBacktestEngine`, `OrderBookReconstructor` |
| 198-200 | Low-frequency data warning | Consolidated open/close puede inflar backtest diario | `PrimaryAuctionPricePolicy`, `DataFrequencyAudit` |
| 200-201 | Implied futures quotes | Calendar spread implied quotes | future `FuturesQuotePolicy` |
| 202-211 | Order flow | Aggressor tags, tick rule, Lee-Ready, BVC, execution realism | `OrderFlowBuilder`, `TradeVsQuoteFillAudit` |
| 212-214 | Order book imbalance | Bid/ask size imbalance como predictor | `OrderBookImbalanceFeature` |
| 217-223 | Bitcoin time-series/ML | Mercado nuevo, midprice optimism, 24/7 risk | `NewMarketResearchChecklist` |
| 223-226 | Bitcoin order flow | Aggressor tags y simplificaciones de backtest | `AggressorTagPolicy`, `OrderFlowBuilder` |
| 227-228 | Cross-exchange arbitrage | Costes, transferencias, exchange risk | `VenueRiskModel` |
| 231-237 | Strategy reality | Estrategias mueren, competencia, cambios de mercado | `StrategyDecayMonitor` |
| 237-241 | Trends/business/managed accounts | Investigacion continua, capital allocation, operational reality | `StrategyLifecycle`, `CapitalAllocator` |

## Rutas De Lectura TSIS

| Tarea | Ruta minima |
|---|---|
| Primer backtester Python v0.1 | 17, 22-25, 28-30, 193-200 |
| Politica de datos historicos | 18-21, 47-49, 125-127, 198-200 |
| Research de factores small caps | 43-72, 127-131 |
| ML posterior al motor | 99-132 |
| Intraday/fills/quotes | 175-214 |
| Order flow features | 202-214, 223-226 |
| Eventos y scheduled catalysts | 149-153 |
| Strategy lifecycle/live decay | 235-237 |

## Prioridad Para TSIS Backtest Engine

| Prioridad | Paginas | Motivo |
|---|---:|---|
| Critica | 17, 22-25 | La misma logica debe servir para backtest/live/replay. |
| Critica | 18-21, 198-200 | Datos y precios ejecutables pueden cambiar completamente el resultado. |
| Critica | 175-214 | Small caps intradia requieren microestructura, bid/ask, spread, size y latency. |
| Alta | 28-40 | Metricas, drawdown, leverage y portfolio son outputs obligatorios. |
| Alta | 99-132 | ML debe entrar con logs, splits, normalizacion y control de complejidad. |
| Media | 43-72 | Factores son importantes para stock selection, pero despues del vertical slice. |
| Media | 135-172 | Opciones/eventos aportan modelado, pero no bloquean small-cap engine v0.1. |
| Baja | 217-241 | Bitcoin/business aporta analogias y lifecycle, no arquitectura base. |
