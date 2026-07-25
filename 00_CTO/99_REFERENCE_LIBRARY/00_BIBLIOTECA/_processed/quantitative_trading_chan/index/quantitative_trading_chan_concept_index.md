# Concept Index - Quantitative Trading

**book_id:** `quantitative_trading_chan`  
**Uso:** indice concepto -> paginas -> aplicacion TSIS.  
**Regla:** abrir primero este indice, despues el resumen, y solo despues el PDF original por pagina.

## Menu

- [Indice Conceptual](#indice-conceptual)
- [Conceptos Mas Importantes Para TSIS](#conceptos-mas-importantes-para-tsis)
- [Preguntas Rapidas Para Agentes](#preguntas-rapidas-para-agentes)

## Indice Conceptual

| Concepto | Paginas PDF | Que aporta | Encaje TSIS |
|---|---:|---|---|
| Alpha decay | 241-243 | Estrategias pierden potencia con competencia | `DecayMonitor`, `StrategyLifecycle` |
| ATS | 120-137 | Sistema que recibe datos, genera ordenes y envia al broker | `AutomatedTradingSystem`, `DASBrokerAdapter` |
| Backtest replication | 51-52 | Replicar resultados para entender y auditar estrategia | `ReproducibilityGate` |
| Backtesting platforms | 51-59 | Excel/MATLAB/Python/R/LEAN/Blueshift | `ReferencePlatforms` |
| Backtest vs live divergence | 133-137 | Diagnostico de errores, costes, regime shift, snooping | `LiveDivergenceMonitor` |
| Bid-ask spread | 43-44, 98-103 | Coste de liquidez basico | `SpreadCostModel` |
| Broker API | 113-115, 120-128 | Requisito para data retrieval y order submission | `BrokerAdapter`, `DASAdapter` |
| Capacity | 48-49, 238-243 | Cuanto capital absorbe la estrategia sin degradar returns | `CapacityModel` |
| Cointegration | 182-200 | Spread estacionario para pairs/stat arb | `CointegrationResearch` |
| Correlation vs cointegration | 191-200 | No confundir retornos correlacionados con spread estacionario | `PairValidation` |
| Data-snooping bias | 46-48, 83-88, 97-98 | Sobreajuste por parametros y decisiones cualitativas repetidas | `OverfittingGuard`, `ExperimentRegistry` |
| Dark pool/liquidity access | 113-115 | Diferencias de ejecucion entre brokers | `BrokerCapabilityMatrix` |
| Drawdown | 40-43, 76-82 | Profundidad y duracion de perdida | `DrawdownProfiler` |
| Execution costs | 43-44, 98-103, 130-132 | Comisiones, spread, market impact, slippage | `TransactionCostModel` |
| Factor models | 200-210 | APT, Fama-French, PCA/statistical factors | `FactorExposureModel` |
| Hard-to-borrow | 135 | Shorts historicos pueden ser imposibles en real | `ShortAvailabilityModel` |
| High-frequency backtesting | 230-235 | Requiere bid/ask, order book y simulacion sofisticada | `HFTReadinessGate` |
| Historical databases | 59-68 | Fuentes, ajustes y sesgos de datos | `DataCatalog`, `DataQualityGate` |
| Kelly formula | 138-151, 163-164 | Sizing/leverage/capital allocation | `RiskSizingModel`, `CapitalAllocator` |
| Leverage cap | 141-154 | Half-Kelly y limite por worst historical loss | `LeveragePolicy` |
| Look-ahead bias | 82-83 | Uso de informacion futura | `TemporalIntegrityGate` |
| Look-ahead truncation test | 83, 93-94 | Comparar posiciones con y sin futuro truncado | `TruncatedDataInvarianceTest` |
| Low-priced stocks | 130 | Evitar costes altos en acciones baratas | `LowPriceLiquidityGate` |
| Market impact | 43-44, 130-132 | Orden grande mueve precio | `ImpactModel`, `ParticipationCap` |
| Market-neutral / dollar-neutral | 33-34, 69-75 | Capital y Sharpe en long/short | `PortfolioConstruction` |
| Mean reversion | 166-170 | Reversion temporal o cross-sectional | `MeanReversionStrategyFamily` |
| Model risk | 156 | Modelo erroneo o edge erosionado | `ModelRiskMonitor` |
| Momentum | 166-170 | Tendencia por informacion, ordenes grandes o herding | `MomentumStrategyFamily` |
| Order size vs ADV | 130-131 | Limitar orden por volumen medio | `AverageVolumeGate`, `ParticipationCap` |
| Out-of-sample testing | 85-88 | Separar train/test y paper trading | `ValidationSplit`, `PaperTradingHarness` |
| Paper trading | 87-88, 132-133 | Prueba honesta con datos unseen y operativa real | `ShadowTradingHarness` |
| Parameterless models | 86-88 | Parametros optimizados dinamicamente/averaging | `DynamicParameterPolicy` |
| Performance metrics | 68-82 | Sharpe, MDD, MDD duration, MAR | `MetricsEngine` |
| Point-in-time data | 34-35, 45, 48, 59-68 | Evitar survivorship/look-ahead en datos | `PointInTimeUniverse` |
| Regime shift | 45-46, 133-135, 170-181 | Cambio de estructura/regulacion/volatilidad | `RegimeMonitor` |
| Risk management | 151-157 | Reducir size con perdidas, model/software/operational risk | `RiskPolicy` |
| Sharpe ratio | 39-42, 68-75 | Medida central de retorno/riesgo | `MetricsEngine` |
| Short-sale constraints | 135 | Plus-tick/uptick rules y borrow | `ShortSaleConstraintModel` |
| Slippage | 43-44, 131-132 | Diferencia entre trigger y ejecucion | `SlippageModel` |
| Software risk | 157 | ATS no refleja backtest por bugs | `BacktestVsPaperReconciler` |
| Split/dividend adjustment | 62-68 | Ajustar precios antes de senales | `CorporateActions` |
| Stationarity | 182-200 | Base estadistica para mean reversion | `StationarityTest` |
| Stop loss | 155-156, 214-215 | Adecuado en momentum, peligroso en mean reversion | `ExitPolicy`, `RiskStop` |
| Strategy refinement | 103-107 | Mejorar sin reintroducir snooping | `RefinementGovernance` |
| Survivorship bias | 34-35, 44-45, 59-68, 167-168 | Inflacion de backtest por excluir muertos/delistados | `SurvivorshipBiasGuard` |
| Transaction cost formula | 98-103 | Coste proporcional a cambios de pesos/turnover | `CostAccounting` |
| VPS / infrastructure | 116-118 | Resiliencia y latencia operativa | `OperationalRunbook` |

## Conceptos Mas Importantes Para TSIS

1. `TruncatedDataInvarianceTest`: prueba automatica contra look-ahead.
2. `TransactionCostModel`: costes netos obligatorios, especialmente en small caps.
3. `PaperTradingHarness`: paper/shadow como fase obligatoria entre backtest y live.
4. `BacktestVsPaperReconciler`: comparar senales, ordenes, fills y PnL teorico vs observado.
5. `CapacityModel`: ventaja small-cap solo si el size cabe en la liquidez real.
6. `ShortAvailabilityModel`: shorts de small caps no son asumibles por defecto.
7. `RiskSizingModel`: sizing y leverage deben reducirse ante perdidas y fat tails.
8. `RegimeMonitor`: detectar si una estrategia dejo de operar bajo el regimen estudiado.

## Preguntas Rapidas Para Agentes

| Pregunta | Buscar |
|---|---|
| Como filtro una idea antes de programar? | paginas 28-50 |
| Que datos historicos necesito y que sesgos vigilar? | paginas 59-68 |
| Como calcular metricas basicas? | paginas 68-82 |
| Como detecto look-ahead? | paginas 82-83 y 93-94 |
| Como reduzco data-snooping? | paginas 83-88 y 97-98 |
| Como meto costes de transaccion? | paginas 43-44 y 98-103 |
| Como debe pasar el backtest a ATS? | paginas 120-137 |
| Para que sirve paper trading? | paginas 132-133 |
| Por que live puede diferir del backtest? | paginas 133-137 |
| Como gestionar leverage y sizing? | paginas 138-157 |
| Cuando usar stop loss? | paginas 155-156 y 214-215 |
| Como distinguir mean reversion y momentum? | paginas 166-170 |
| Como usar cointegration para pairs? | paginas 182-200 |
| Como pensar factor models? | paginas 200-210 |
| Que exige HFT/intraday realista? | paginas 230-235 |
| Por que small-cap niche puede existir? | paginas 238-243 |

