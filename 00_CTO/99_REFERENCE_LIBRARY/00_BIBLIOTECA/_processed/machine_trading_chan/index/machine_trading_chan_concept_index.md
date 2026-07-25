# Concept Index - Machine Trading

**book_id:** `machine_trading_chan`  
**Uso:** indice concepto -> paginas -> aplicacion TSIS.  
**Regla:** abrir primero este indice, despues el resumen, y solo despues el PDF original por pagina.

## Menu

- [Indice Conceptual](#indice-conceptual)
- [Conceptos Mas Importantes Para TSIS](#conceptos-mas-importantes-para-tsis)
- [Preguntas Rapidas Para Agentes](#preguntas-rapidas-para-agentes)

## Indice Conceptual

| Concepto | Paginas PDF | Que aporta | Encaje TSIS |
|---|---:|---|---|
| Same program for backtest/live | 17, 22-25 | Backtest y live deben compartir logica para evitar divergencia | `DecisionCore`, `ReplayLiveEquivalence` |
| Historical data quality | 18-21 | Fuentes, survivorship, delisted data, corporate actions, BBO/auction | `HistoricalDataQualityGate` |
| Survivorship-free data | 18-20, 47-49, 126 | Requiere delistings e index membership historico | `PointInTimeUniverse`, `SurvivorshipBiasGuard` |
| Primary exchange auction price | 19, 198-200 | Mejor precio para MOO/MOC que consolidated open/close | `PrimaryAuctionPricePolicy` |
| Consolidated close problem | 198-200 | Puede inflar estrategias mean-reverting | `ExecutablePriceGate` |
| Live market data latency | 21-22, 176-179 | Latency de data feed cambia la ejecutabilidad | `MarketDataLatencyModel` |
| Broker API / order status | 17, 22-27 | Flujo de ordenes y confirmaciones | `BrokerAdapter`, `OrderStatusEvent` |
| CAGR | 28-29 | Crecimiento compuesto con leverage constante | `MetricsEngine` |
| Sharpe ratio | 28-30 | Medida comun pero limitada por fat tails | `MetricsEngine` |
| Calmar ratio | 29-30 | CAGR dividido por drawdown reciente | `DrawdownProfiler` |
| Maximum drawdown | 28-30, 38 | Mejor proxy de tail risk que volatilidad simple | `RiskReport` |
| Kelly leverage | 29, 35-37, 137-141, 240 | Sizing teorico, peligroso con fat tails | `RiskSizingModel`, `LeveragePolicy` |
| Minimum variance portfolio | 30-38 | Allocation por covarianza cuando retornos esperados son poco fiables | `CapitalAllocator` |
| Risk parity caution | 38-39 | Volatility targeting puede crear contagion y olvidar tail risk | `RiskModelReview` |
| Factor risk vs alpha | 43-45 | Factor risk no se diversifica; alpha si | `FactorExposureReport` |
| Time-series factors | 45-49 | Market, HML, SMB, UMD, volatility como series comunes | `FactorResearchPipeline` |
| Cross-sectional factors | 49-57, 127-130 | Ratios fundamentales y variables por stock | `PointInTimeFeatureStore` |
| Predictive vs descriptive factor model | 45-47 | Factor contemporaneo no equivale a predictor | `TemporalIntegrityGate` |
| Fama-French factors | 47-49 | Ejemplo de uso predictivo y fracaso out-of-sample | `FactorValidationReport` |
| Short interest / DTC | 63-64 | DTC puede ser factor, pero su potencia cambia por regimen | `ShortInterestFeature`, `RegimeMonitor` |
| Liquidity factor | 64-65 | El signo del factor depende del universo | `SmallCapLiquiditySegmentation` |
| Statistical factors / PCA | 65-69 | Factores derivados de covariance matrix, utiles en corto plazo | `StatisticalFactorModel` |
| Cross-sectional ranking | 69-71 | Ranking/multisort puede ser mas robusto que regresion exacta | `CrossSectionalRanker` |
| AR / ARMA | 75-83 | Modelos temporales simples; BIC para lags; peligro de midprice fills | `TimeSeriesResearch`, `LagSelectionPolicy` |
| VAR / VEC | 83-87 | Modelar instrumentos relacionados y neutralidad sectorial | `MultiAssetStateModel` |
| State space / Kalman | 87-96, 140-141 | Estados ocultos, hedge ratio dinamico, riesgo de sobreajuste | `KalmanStateEstimator` |
| Midprice research caveat | 76, 79, 219, 223 | Evita bid-ask bounce pero no garantiza ejecucion | `MidPriceResearchPolicy` |
| Model complexity budget | 96, 123-125, 131 | Menos parametros suele generalizar mejor | `ModelComplexityBudget` |
| ML overfitting | 99-104, 108-114, 123-132 | Finanzas tiene datos limitados y no estacionarios | `OverfittingGuard` |
| Train/test split | 102-104, 123, 129-131 | Separacion obligatoria para modelos ML | `TrainValidationTestPolicy` |
| Cross-validation | 101, 108-109 | Reduce overfitting dentro del training process | `ValidationSplitter` |
| Bagging | 101, 109-111, 124 | Ensemble por bootstrap/resampling | `EnsembleModelPolicy` |
| Random forest | 111-112 | Bagging + random subspace para arboles | `EnsembleModelPolicy` |
| Boosting | 112-114 | Puede subir train sin mejorar test | `ModelSelectionWarning` |
| SVM | 115-117 | Clasificacion lineal/no lineal; kernels aumentan overfitting | `ClassifierModelRegistry` |
| Hidden Markov Model | 117-121 | Regimenes ocultos y estados no observables | `RegimeStateModel` |
| Neural network | 121-125 | Sensibilidad a arquitectura, random seed y overfitting | `RandomSeedLedger`, `ModelRegistry` |
| Data aggregation | 125-127 | Agregar instrumentos solo tras normalizacion | `FeatureNormalizationPolicy` |
| Feature normalization | 125-127 | Escalar predictors/response por volatilidad u otra base apropiada | `NormalizerFitPolicy` |
| ML stock selection | 127-131 | Feature selection fundamental y holding-period logic | `StockSelectionResearch` |
| Scheduled events | 149-153 | Calendario exacto y timestamps de anuncios | `EventCalendar`, `ScheduledEventFeed` |
| Options bid-ask spread | 149-153, 160-168 | Entry/exit a bid/ask/mid cambia el resultado | `BidAskExecutionPolicy` |
| Gamma scalping | 153-157 | Estrategia path-dependent | `PathDependentBacktest` |
| Dispersion trading | 158-168 | Backtest multidimensional, delta/vega neutrality, option selection | `MultiLegOrderModel` |
| Intraday capacity | 175-176 | Intradia tiene capacidad limitada por quote size/depth | `CapacityModel`, `QuoteSizeGate` |
| Latency types | 176-179 | Order submission, order status, market data, computational | `LatencyModel` |
| Limit order adverse selection | 179, 190-193 | Limit fills pueden ser precisamente los malos fills | `AdverseSelectionAudit` |
| Order routing / NBBO | 179-190 | Fragmentacion, protected quotes, routing, IOC/ISO | `RoutingModel`, `NBBOState` |
| Dark pools | 184-190 | Posible mejora de precio, pero informacion/adverse selection | `VenueModel` |
| Intraday backtesting | 193-198 | Market orders requieren BBO; limit orders requieren order book/replay | `IntradayBacktestEngine` |
| Level 2 / ITCH | 193-198, 202 | Mensajes para reconstruir libro y cola | `OrderBookReconstructor` |
| Irregular timestamps | 194-198, 205-211 | Tick data no siempre tiene barras regulares | `EventClock`, `SameTimestampPolicy` |
| BBO construction | 194-198 | Reconstruir best bid/offer desde mensajes | `BBOBuilder` |
| Low-frequency data warning | 198-200 | Datos diarios pueden producir beneficios ficticios | `DataFrequencyAudit` |
| Implied futures quotes | 200-201 | Calendar spreads pueden crear quotes ejecutables | `FuturesQuotePolicy` |
| Order flow | 202-211, 223-226 | Signed transaction volume predictivo | `OrderFlowBuilder` |
| Aggressor tag | 202, 205-208, 223-226 | Identifica si trade fue buyer/seller initiated | `AggressorTagPolicy` |
| Bulk volume classification | 203-210 | Estimar order flow sin tick-level aggressor tags | `OrderFlowEstimator` |
| Order book imbalance | 212-214 | Bid size vs ask size como predictor de midprice | `OrderBookImbalanceFeature` |
| Trade price fill optimism | 223-226 | Fill al trade price puede ser irrealista frente a bid/ask | `TradeVsQuoteFillAudit` |
| Cross-exchange arbitrage costs | 227-228 | Comisiones, transferencias, inventory y exchange risk | `VenueRiskModel` |
| Strategy decay | 235-237 | Estrategias tienen vida finita | `StrategyDecayMonitor` |
| Backtest vs live reality | 235-237 | Algunas estrategias backtesteadas no funcionan out-of-sample | `BacktestVsLiveReconciler` |
| Portfolio of strategies | 235-237, 241 | Diversificar y retirar estrategias deterioradas | `StrategyLifecycle`, `CapitalAllocator` |

## Conceptos Mas Importantes Para TSIS

1. `ExecutablePriceGate`: no usar mid/consolidated close como precio ejecutable por defecto.
2. `PrimaryAuctionPricePolicy`: para MOO/MOC, preferir primary exchange auction prices.
3. `IntradayBacktestEngine`: small caps intradia requieren bid/ask, timestamps, spread, size y fill assumptions.
4. `OrderFlowBuilder`: el order flow es predictor util, pero exige aggressor tags o estimadores documentados.
5. `FeatureNormalizationPolicy`: ML cross-sectional sin normalizacion mezcla volatilidades e instrumentos incompatibles.
6. `ModelComplexityBudget`: la complejidad debe justificarse out-of-sample.
7. `AdverseSelectionAudit`: limit fills no son siempre buenos fills; pueden ser fills toxicos.
8. `StrategyDecayMonitor`: estrategias deben nacer, reducirse, pausarse o morir segun evidencia live.

## Preguntas Rapidas Para Agentes

| Pregunta | Buscar |
|---|---|
| Como conecto backtest y live sin duplicar logica? | paginas 17, 22-25 |
| Que datos historicos necesito para no mentirme? | paginas 18-21, 198-200 |
| Que metricas reporto desde v0.1? | paginas 28-40 |
| Como encajan factores y ranking de acciones? | paginas 43-72 |
| Que cautelas aplicar a time-series models? | paginas 75-96 |
| Que exige ML para no sobreajustar? | paginas 99-132 |
| Que lecciones aportan eventos/opciones? | paginas 149-157 |
| Como modelar backtesting intradia? | paginas 175-214 |
| Como tratar order flow y imbalance? | paginas 202-214 |
| Por que una estrategia puede dejar de funcionar? | paginas 235-237 |
