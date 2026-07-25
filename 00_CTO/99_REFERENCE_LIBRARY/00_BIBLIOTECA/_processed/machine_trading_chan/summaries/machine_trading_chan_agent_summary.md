# Machine Trading - Agent Summary

**book_id:** `machine_trading_chan`  
**Autor:** Ernest P. Chan  
**Fuente local:** `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\00_BIBLIOTECA\Machine_Trading_-_Ernest_P_Chan.pdf`  
**Titulo extraido:** Machine Trading  
**Rol dentro de TSIS:** puente practico entre modelos cuantitativos, machine learning, factores, time-series, opciones/eventos e intradia/microestructura. Sirve para endurecer la capa de research, validacion, costes y ejecucion del backtester.  
**No es:** una especificacion completa de motor event-driven/OMS en Python. Para eso sigue siendo mejor cruzar QuantStart/Halls-Moore, Hilpisch, LEAN y NautilusTrader.

## Menu Rapido

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Donde Encaja En TSIS](#donde-encaja-en-tsis)
- [Mapa De Capitulos](#mapa-de-capitulos)
- [Tesis Principal](#tesis-principal)
- [Chapter 1 - Basics Of Algorithmic Trading](#chapter-1---basics-of-algorithmic-trading)
- [Chapter 2 - Factor Models](#chapter-2---factor-models)
- [Chapter 3 - Time-Series Analysis](#chapter-3---time-series-analysis)
- [Chapter 4 - Artificial Intelligence Techniques](#chapter-4---artificial-intelligence-techniques)
- [Chapter 5 - Options Strategies](#chapter-5---options-strategies)
- [Chapter 6 - Intraday Trading And Market Microstructure](#chapter-6---intraday-trading-and-market-microstructure)
- [Chapter 7 - Bitcoins](#chapter-7---bitcoins)
- [Chapter 8 - Strategy Lifecycle And Business Reality](#chapter-8---strategy-lifecycle-and-business-reality)
- [Blueprint TSIS Derivado](#blueprint-tsis-derivado)
- [Quality Gates TSIS](#quality-gates-tsis)
- [Lectura Para Agentes](#lectura-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen Ejecutivo

`Machine Trading` complementa `Quantitative Trading` del mismo autor. El libro no ensena a construir desde cero un motor event-driven profesional, pero aporta requisitos muy valiosos para no construir un backtester mecanicamente correcto y economicamente falso.

Su valor principal para TSIS esta en cinco zonas:

```text
1. El mismo nucleo conceptual debe poder backtestear y operar en live.
2. Los datos historicos deben representar precios ejecutables, no solo precios publicados.
3. Los modelos de factores, series temporales y ML deben separarse de ejecucion, costes y validacion.
4. El intradia exige BBO/NBBO, timestamps, latency, adverse selection y reglas de fill explicitas.
5. Las estrategias mueren; TSIS necesita lifecycle, decay monitor y reconciliacion backtest/live.
```

Para small caps, el capitulo 6 es el mas importante. Chan explica que incluso estrategias diarias pueden quedar infladas si se usan precios open/close consolidados en lugar de precios de subasta de la primary exchange o, como minimo, midprices derivados de BBO. En small caps este problema es mas grave por spreads, baja profundidad, prints pequenos y datos ruidosos.

## Donde Encaja En TSIS

```text
QuantStart / Halls-Moore -> esqueleto pedagogico event-driven
Hilpisch                 -> entorno Python, datos, clases event-based y online
Pardo                    -> evaluacion, optimizacion y walk-forward
Quantitative Trading     -> backtesting practico, costes, paper/live, riesgo y capacidad
Machine Trading          -> factores, ML, time-series, opciones, intradia y microestructura aplicada
Harris                   -> teoria profunda de ordenes, liquidez y mercado
Lopez de Prado           -> validacion estadistica avanzada y leakage
Nautilus / LEAN          -> arquitectura profesional de referencia
```

`Machine Trading` debe influir sobre estos nodos:

```text
HistoricalDataQualityGate
PrimaryAuctionPricePolicy
BBOQuotePolicy
FactorResearchPipeline
FeatureNormalizationPolicy
MLExperimentRegistry
TrainValidationTestPolicy
OrderFlowBuilder
OrderBookReconstructor
IntradayExecutionSimulator
AdverseSelectionAudit
LatencyModel
StrategyDecayMonitor
BacktestVsLiveReconciler
```

## Mapa De Capitulos

| Seccion | Paginas PDF | Uso principal para TSIS |
|---|---:|---|
| Preface | 11-16 | contexto del libro y enfoque practico |
| Ch. 1 The Basics of Algorithmic Trading | 17-40 | datos, plataformas, broker API, metricas, Kelly, portfolio |
| Ch. 2 Factor Models | 43-72 | factores time-series/cross-sectional, PCA, short interest, liquidity |
| Ch. 3 Time-Series Analysis | 75-96 | AR/ARMA/VAR/VEC/state-space/Kalman, overfitting y constraints |
| Ch. 4 Artificial Intelligence Techniques | 99-132 | ML aplicado, cross-validation, bagging, random forest, HMM, NN, normalizacion |
| Ch. 5 Options Strategies | 135-172 | estrategias event-driven, volatilidad, gamma scalping, dispersion, datos complejos |
| Ch. 6 Intraday Trading and Market Microstructure | 175-214 | latency, order routing, dark pools, adverse selection, intraday backtesting, order flow |
| Ch. 7 Bitcoins | 217-228 | time-series/order flow/cross-exchange en mercado nuevo |
| Ch. 8 Algorithmic Trading Is Good for Body and Soul | 231-241 | strategy decay, portfolio de estrategias, negocio y monitoring |
| Bibliography/Index/EULA | 243-267 | referencias y localizacion |

## Tesis Principal

Chan parte de una idea importante para TSIS:

```text
backtest y live deben compartir la misma logica de decision siempre que sea posible
```

Esto no significa que TSIS deba copiar los ejemplos MATLAB del libro. Significa que el contrato del sistema debe impedir una divergencia silenciosa:

```text
Research signal != production signal
backtest fill != live fill
consolidated close != executable close
midprice PnL != tradable PnL
ML in-sample success != edge real
```

El libro insiste en que un resultado de backtest depende tanto de la estrategia como de los supuestos de datos, timestamps, costes, ordenes y ejecucion. Para un motor small-cap, esta es una advertencia central.

## Chapter 1 - Basics Of Algorithmic Trading

Chan presenta el flujo basico:

```text
historical/live market data
        -> computer program
        -> backtest results or live orders
        -> broker API
        -> order status
```

La frase arquitectonica clave es que el mismo programa conceptual debe servir para backtest y live. Para TSIS esto se traduce en:

```text
HistoricalDataAdapter
ReplayDataAdapter
LiveDASAdapter
        -> mismo Strategy / DecisionPolicy
```

Puntos relevantes:

- Datos historicos: usar fuentes survivorship-bias-free cuando proceda; para universos historicos no basta con precios de activos actuales.
- Corporate actions: splits/dividendos deben tratarse de forma explicita.
- Open/close diario: Chan advierte que el consolidated open/close puede no ser el precio ejecutable por ordenes MOO/MOC. Para backtests serios se prefieren auction prices de la primary exchange o midprices BBO si no hay auction.
- Live data: la calidad y latencia importan mucho mas en intradia que en estrategias diarias.
- Plataformas: la investigacion rapida puede hacerse en lenguajes de alto nivel, pero la operativa necesita arquitectura robusta, control de errores, versionado y eficiencia.
- Metricas: Chan prioriza CAGR, Sharpe, Calmar, maximum drawdown y drawdown duration.
- Kelly: util como teoria de leverage, pero peligroso con fat tails. En practica recomienda bajar leverage hasta que el drawdown sea tolerable.
- Portfolio: Markowitz/Kelly/risk parity son utiles, pero el riesgo de cola y contagio no quedan bien capturados solo con volatilidad.

Para TSIS v0.1:

```text
No usar leverage arbitrario en backtest.
Reportar siempre PnL neto, drawdown y duracion.
Separar metricas unlevered vs levered.
Declarar si el precio usado era close consolidado, auction, bid, ask o mid.
```

## Chapter 2 - Factor Models

El capitulo distingue entre alpha idiosincratico y factor risk. Los factores pueden generar retornos persistentes porque compensan riesgos no diversificables, pero no deben confundirse con arbitraje.

Ideas utiles para TSIS:

- Time-series factors: mercado, HML, SMB, momentum/UMD, volatilidad, macro. Son utiles para explicar exposiciones y, a veces, para prediccion.
- Cross-sectional factors: ratios fundamentales, ROE, book-to-market, liquidity, short interest, option-implied variables. Se usan para ordenar activos y construir long/short.
- Descriptivo vs predictivo: un factor contemporaneo no predice por si solo; el modelo debe usar informacion disponible en `t` para predecir `t+1`.
- Point-in-time: fundamentales, short interest, index membership y universos deben estar fechados correctamente.
- Short interest: DTC puede ser mas informativo que short interest ratio, pero el signo y potencia pueden cambiar por regimen.
- Liquidity: el efecto puede invertirse segun universo. Un resultado en top 3500 stocks no necesariamente vale para SPX, y mucho menos para small caps.
- Statistical factors/PCA: utiles para prediccion de corto plazo e intradia cuando los factores fundamentales se mueven poco.
- Ranking/multisort: a veces es mas robusto que usar retornos predichos exactos por regresion, porque reduce sensibilidad a outliers.

Encaje TSIS:

```text
FactorResearchPipeline
PointInTimeFeatureStore
UniverseSnapshot
CrossSectionalRanker
FactorExposureReport
FactorNeutralPortfolioConstruction
SmallCapLiquiditySegmentation
```

Para small caps, la leccion es doble:

```text
puede haber mas ineficiencia
pero el coste/liquidez/capacidad puede destruir el edge
```

## Chapter 3 - Time-Series Analysis

El capitulo cubre AR, ARMA, VAR, VEC y state-space/Kalman. Chan los propone como primera prueba cuando se estudia un instrumento o mercado sin intuicion previa.

Puntos importantes:

- Usar midprices en analisis de series temporales ayuda a evitar mean reversion fantasma por bid-ask bounce.
- AR/ARMA pueden parecer muy rentables si se asume ejecucion a midprice. Esa hipotesis debe marcarse como idealizada.
- VAR/VEC permiten modelar relaciones entre varios instrumentos o sectores.
- Kalman/state-space puede estimar estados ocultos, hedge ratios dinamicos y relaciones cambiantes.
- Los modelos lineales tambien sobreajustan si se permite demasiados lags o demasiados parametros.
- La seleccion de lags por BIC/AIC ayuda, pero no sustituye validacion out-of-sample.
- Los state-space models requieren constraints fuertes; si no, el ruido se convierte en modelo.

Encaje TSIS:

```text
TimeSeriesResearch
LagSelectionPolicy
StateSpaceModelRegistry
KalmanHedgeRatioEstimator
MidPriceResearchPolicy
ModelComplexityBudget
```

Para el motor:

```text
si una estrategia depende de midprice, TSIS debe comprobar si puede ejecutarse con limit orders
si solo funciona a midprice pero no a bid/ask, no es una estrategia ejecutable
```

## Chapter 4 - Artificial Intelligence Techniques

Chan trata ML con cautela. La idea central es que los datos financieros son limitados, no estacionarios y propensos al overfitting. El libro muestra modelos basicos: stepwise regression, regression/classification trees, cross-validation, bagging, random forest, boosting, SVM, HMM y neural networks.

Lecciones para TSIS:

- Separar `trainset` y `testset` es obligatorio.
- En trading, mas complejidad no implica mejor resultado out-of-sample.
- Los arboles completos pueden mejorar in-sample y empeorar fuera de muestra.
- Cross-validation, bagging, random subspace, random forest, retraining y averaging son tecnicas para reducir fragilidad, pero no garantizan edge.
- Boosting puede mejorar el entrenamiento sin mejorar test.
- Las redes neuronales son muy sensibles a inicializacion y arquitectura; en datasets pequenos financieros, las redes simples pueden superar a redes grandes.
- Normalizacion es obligatoria cuando se agregan datos de muchos instrumentos.
- Si se agrega SPX/small caps en una matriz comun, predictors y response deben escalarse de forma comparable.
- Para ML hacen falta muchos rows y muchos predictors; level 2, news y datos no estructurados pueden ser mas adecuados que cuatro indicadores simples.
- La recomendacion operativa es empezar por modelos simples y aumentar complejidad solo si sobrevive out-of-sample.

Encaje TSIS:

```text
MLExperimentRegistry
FeatureSetVersion
NormalizerFitPolicy
TrainValidationTestSplit
RandomSeedLedger
ModelSelectionLedger
OutOfSampleReport
ModelComplexityBudget
```

Regla TSIS derivada:

```text
ningun modelo ML puede escribir senales sin registrar:
features usadas
normalizacion
split temporal
random seed
modelo/version
parametros
numero de variantes probadas
resultado seleccionado
```

## Chapter 5 - Options Strategies

Este capitulo no es prioridad para el primer backtester de small caps, pero aporta buenas lecciones de modelado de eventos, path dependence, costes y datos multidimensionales.

Ideas utiles:

- Las opciones requieren dimensiones adicionales: underlying, strike, expiration, call/put, moneyness, tenor, Greeks, bid/ask.
- Estrategias event-driven sobre anuncios programados dependen de calendario exacto y timestamps.
- El resultado puede cambiar totalmente segun se asuma entrada a bid, ask o mid.
- Los bid-ask spreads en opciones son amplios; muchas estrategias mueren por coste de ejecucion.
- Gamma scalping es path-dependent: no basta con precio inicial/final; importa la trayectoria completa.
- Dispersion trading muestra la complejidad de rebalancing diario, neutralidad delta/vega y seleccion dinamica de instrumentos.

Encaje TSIS:

```text
EventCalendar
ScheduledEventFeed
PathDependentBacktest
InstrumentSelector
BidAskExecutionPolicy
MultiLegOrderModel
```

Uso practico para TSIS small caps:

```text
si una estrategia small-cap depende de earnings/news/eventos,
tratarla como event-driven con calendario, timestamps y estado antes/despues del evento
```

## Chapter 6 - Intraday Trading And Market Microstructure

Este es el capitulo mas importante del libro para TSIS small caps.

Ideas criticas:

- Intradia puede tener Sharpe alto por mas apuestas independientes, pero capacidad menor.
- La profundidad at-the-touch puede ser pequena incluso en activos muy liquidos; en small caps sera mucho peor.
- Costes intradia incluyen spread, slippage, market impact, adverse selection, opportunity cost y comisiones.
- Hay tres latencias: order submission, order status y market data.
- La latencia afecta distinto a mean reversion y momentum:
  - mean reversion/market making usa limit orders y sufre queue priority, opportunity cost y adverse selection;
  - momentum usa market orders y sufre slippage si llega tarde.
- Order routing, NBBO, ISO, hidden orders, dark pools y special order types cambian la ejecutabilidad.
- Adverse selection debe medirse comparando PnL de ordenes filled vs unfilled en ventanas cortas.
- Backtesting intradia con market orders requiere al menos BBO/NBBO a frecuencia suficiente.
- Backtesting limit-order/market-making requiere order book messages tipo ITCH para reconstruir cola y fills.
- Los timestamps irregulares y multiples ticks con mismo timestamp obligan a un event loop determinista.
- Incluso estrategias diarias pueden quedar infladas por usar consolidated open/close en lugar de primary auction prices.
- Order flow y order book imbalance pueden predecir midprice, pero su utilidad depende de datos y ejecucion.

Encaje TSIS:

```text
QuoteEvent
TradeEvent
OrderBookEvent
PrimaryAuctionPrice
NBBOState
OrderFlowBuilder
OrderBookImbalanceFeature
LatencyModel
QueuePriorityApproximation
AdverseSelectionAudit
IntradayDataQualityGate
```

Regla TSIS:

```text
Un backtest intradia de small caps que no distingue bid/ask, spread, size, timestamp y fill assumption
no debe etiquetarse como ejecutable.
```

## Chapter 7 - Bitcoins

El capitulo usa bitcoin como mercado nuevo donde aplicar time-series, ML, order flow y cross-exchange arbitrage.

Para TSIS no importa bitcoin como activo, sino las advertencias:

- En mercados nuevos, los modelos simples pueden encontrar patrones aparentes.
- Retornos enormes basados en midprice suelen no ser ejecutables.
- Order flow puede predecir precios si se dispone de aggressor tags.
- Backtests con trade price como fill son optimistas si en live hay que comprar al ask y vender al bid.
- Cross-exchange arbitrage no es gratis: comisiones, transferencia de capital, withdraw/deposit delays, inventory, credit risk y exchange risk importan.

Encaje TSIS:

```text
NewMarketResearchChecklist
AggressorTagPolicy
TradeVsQuoteFillAudit
VenueRiskModel
CrossVenueArbitrageCostModel
```

## Chapter 8 - Strategy Lifecycle And Business Reality

Chan insiste en que no todas las estrategias backtesteadas funcionan y que las que funcionan pueden dejar de hacerlo.

Motivos:

- cambio macroeconomico;
- cambio de microestructura;
- competencia;
- exceso de capital;
- regime shift;
- flaw de backtest;
- edge decay.

La respuesta no es confiar ciegamente en un backtest, sino mantener un portfolio de estrategias, monitorizar drawdowns, reducir leverage cuando una estrategia se deteriora, crear nuevas estrategias y retirar las que pierden su fundamento.

Encaje TSIS:

```text
StrategyLifecycle
StrategyBirthDeathLog
DecayMonitor
LivePerformanceProfile
BacktestVsLiveReconciler
CapitalAllocator
PortfolioOfStrategies
```

## Blueprint TSIS Derivado

`Machine Trading` sugiere estas extensiones sobre el backtester base:

```text
DATA FOUNDATION
  raw trades/quotes
  BBO/NBBO snapshots
  primary auction open/close
  point-in-time universe
  corporate actions
  timestamp quality
  missing auction/tick flags

RESEARCH LAYER
  factor store
  feature normalization
  cross-sectional ranking
  time-series model registry
  ML experiment registry
  model complexity budget

EVENT ENGINE
  irregular timestamp event loop
  deterministic same-timestamp priority
  scheduled event feed
  rolling state builder
  order flow builder
  order book imbalance feature

EXECUTION
  bid/ask fill policy
  no default mid fills
  market vs limit semantics
  latency assumptions
  volume/size limits
  partial fill future extension
  adverse selection diagnostics

LEDGERS
  market_events.parquet
  quote_snapshots.parquet
  model_predictions.parquet
  feature_snapshots.parquet
  decisions.parquet
  orders.parquet
  fills.parquet
  account_snapshots.parquet
  execution_assumptions.json
```

## Quality Gates TSIS

| Gate | Regla |
|---|---|
| `ExecutablePriceGate` | No aceptar PnL basado en mid/consolidated close sin etiqueta de limitacion. |
| `PrimaryAuctionGate` | Para estrategias MOO/MOC, preferir primary exchange auction prices o declarar proxy. |
| `BBOAvailabilityGate` | Backtest intradia con market orders requiere bid/ask a la frecuencia de decision. |
| `LimitFillGate` | Limit-order fill no puede asumirse sin regla conservadora o modelo de cola. |
| `TimestampOrderGate` | Eventos con timestamps iguales requieren prioridad documentada y determinista. |
| `MLLeakageGate` | Normalizadores, feature selection y parametros se ajustan solo con train/validation. |
| `MLVariantLedgerGate` | Registrar numero de modelos/parametros probados. |
| `SmallCapLiquidityGate` | Ordenes limitadas por spread, dollar volume, quote size, ADV y halts. |
| `AdverseSelectionGate` | Separar PnL de fills vs missed fills cuando se usan limit orders. |
| `DecayMonitorGate` | Comparar live/shadow con perfil historico y degradar size ante deterioro. |

## Lectura Para Agentes

| Si el agente trabaja en... | Leer primero |
|---|---|
| Arquitectura backtest/live comun | Ch. 1, paginas 17-25 |
| Datos historicos fiables | Ch. 1, paginas 18-21; Ch. 6, paginas 198-200 |
| Metricas y leverage | Ch. 1, paginas 28-40 |
| Factores para universe/stock selection | Ch. 2, paginas 43-72 |
| Modelos temporales | Ch. 3, paginas 75-96 |
| ML aplicado a trading | Ch. 4, paginas 99-132 |
| Estrategias basadas en eventos | Ch. 5, paginas 149-153 |
| Fills, latencia y microestructura | Ch. 6, paginas 175-193 |
| Backtesting intradia serio | Ch. 6, paginas 193-214 |
| Order flow / imbalance | Ch. 6, paginas 202-214 |
| Strategy decay y live reality | Ch. 8, paginas 235-237 |

## Limitaciones

- Muchos ejemplos estan en MATLAB y no deben copiarse literalmente a TSIS Python.
- El libro no cubre un OMS profesional completo ni una arquitectura de snapshots/auditoria como la que TSIS necesita.
- No sustituye Harris para microestructura profunda.
- No sustituye Pardo/Lopez de Prado para protocolo de validacion avanzada.
- Los ejemplos de performance del libro son pedagogicos; TSIS debe tratarlos como casos de estudio, no como estrategias listas para operar.
