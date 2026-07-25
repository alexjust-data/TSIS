# Quantitative Trading - Agent Summary

**book_id:** `quantitative_trading_chan`  
**Autor:** Ernest P. Chan  
**Fuente local:** `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\00_BIBLIOTECA\Quantitative_Trading_-_Ernest_P_Chan.pdf`  
**Titulo extraido:** Quantitative Trading, 2nd Edition  
**Rol dentro de TSIS:** guia practica de trading cuantitativo independiente: seleccion de ideas, backtesting realista, sesgos, costes, ejecucion, paper trading, sizing, riesgo, regimenes, stat arb y capacidad.  
**No es:** especificacion formal de arquitectura event-driven ni manual completo de OMS/fill engine profesional.

## Menu Rapido

- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Donde Encaja En TSIS](#donde-encaja-en-tsis)
- [Mapa De Capitulos](#mapa-de-capitulos)
- [Tesis Principal](#tesis-principal)
- [Fishing For Ideas](#fishing-for-ideas)
- [Backtesting](#backtesting)
- [Datos Historicos](#datos-historicos)
- [Performance Measurement](#performance-measurement)
- [Pitfalls De Backtesting](#pitfalls-de-backtesting)
- [Transaction Costs](#transaction-costs)
- [Strategy Refinement](#strategy-refinement)
- [Business And Infrastructure](#business-and-infrastructure)
- [Execution Systems](#execution-systems)
- [Paper Trading](#paper-trading)
- [Divergencia Backtest Vs Live](#divergencia-backtest-vs-live)
- [Money And Risk Management](#money-and-risk-management)
- [Regimes, Mean Reversion And Momentum](#regimes-mean-reversion-and-momentum)
- [Stationarity, Cointegration And Pairs](#stationarity-cointegration-and-pairs)
- [Factor Models](#factor-models)
- [Exit Strategy](#exit-strategy)
- [Seasonal And High Frequency Strategies](#seasonal-and-high-frequency-strategies)
- [Capacity And Independent Trader Edge](#capacity-and-independent-trader-edge)
- [Blueprint TSIS Derivado](#blueprint-tsis-derivado)
- [Quality Gates TSIS](#quality-gates-tsis)
- [Limitaciones](#limitaciones)
- [Lectura Para Agentes](#lectura-para-agentes)

## Resumen Ejecutivo

Chan es util para aterrizar el laboratorio de TSIS en decisiones practicas. Donde Pardo define un proceso disciplinado de evaluacion y walk-forward, Chan baja al nivel de trabajo de un trader cuantitativo independiente:

```text
buscar ideas
filtrarlas por capacidad, capital, datos y estilo
replicar backtests
evitar sesgos comunes
medir Sharpe/drawdown/MAR
meter costes realistas
pasar a ATS/paper trading
comparar backtest teorico contra ejecucion real
gestionar leverage, sizing y riesgo
vigilar regimenes y alpha decay
```

Para small caps, el libro es especialmente relevante porque repite tres advertencias que TSIS debe tratar como requisitos duros:

```text
survivorship bias
illiquidity / market impact
hard-to-borrow / short constraints
```

Su valor no esta en copiar los ejemplos MATLAB/Python, sino en convertir sus advertencias en tests, manifests, quality gates y ledgers.

## Donde Encaja En TSIS

```text
Halls-Moore / QuantStart -> patron pedagogico Market/Signal/Order/Fill
Hilpisch                  -> entorno Python, datos, event-based classes, live/online
Pardo                     -> proceso formal de evaluacion, optimizacion y WFA
Chan                      -> backtesting practico, costes, ejecucion, paper trading, riesgo y capacidad
Harris                    -> microestructura, ordenes, liquidez y mercado real
Lopez de Prado            -> validacion estadistica avanzada, leakage, PBO/DSR
Nautilus / LEAN           -> arquitectura profesional de referencia
```

Chan debe influir sobre estos nodos:

```text
IdeaIntake
StrategySuitabilityChecklist
DataQualityGate
BacktestPitfallAudit
TransactionCostModel
ExecutionReadiness
PaperTradingHarness
BacktestVsPaperReconciler
RiskSizingModel
CapacityModel
RegimeMonitor
ExitPolicy
```

## Mapa De Capitulos

| Seccion | Paginas PDF | Uso principal para TSIS |
|---|---:|---|
| Ch. 1 Whats, Whos, Whys | 20-27 | contexto de trading cuantitativo independiente |
| Ch. 2 Fishing for Ideas | 28-50 | filtros de estrategias, small caps, capacidad, sesgos |
| Ch. 3 Backtesting | 51-107 | plataformas, datos, metricas, pitfalls, costes, refinamiento |
| Ch. 4 Setting Up Your Business | 108-119 | broker, API, liquidez, infraestructura fisica |
| Ch. 5 Execution Systems | 120-137 | ATS, semi/full automation, paper trading, divergencia live |
| Ch. 6 Money and Risk Management | 138-165 | Kelly, leverage, risk management, model/software risk |
| Ch. 7 Special Topics | 166-237 | mean reversion, momentum, regime, cointegration, factors, exits, HFT |
| Ch. 8 Conclusion | 238-243 | capacidad, edge del independiente, alpha decay |
| Appendix MATLAB | 244-249 | no prioritario para TSIS Python |

## Tesis Principal

Chan defiende que el trader independiente puede competir en nichos de baja capacidad que no interesan a grandes fondos. Esto encaja muy bien con TSIS small caps, pero con una condicion: la ventaja teorica desaparece si el backtester ignora liquidez, costes, spreads, borrowing, survivorship o capacidad.

Para TSIS, el mensaje no es "opera small caps porque son ineficientes". El mensaje correcto es:

```text
small-cap edge solo es creible si el backtest prueba ejecutabilidad
```

## Fishing For Ideas

**Paginas PDF:** 28-50.

Chan propone buscar ideas en papers, blogs, foros, fuentes academicas y comunidades de traders, pero filtrarlas antes de gastar tiempo profundo. Los criterios de filtro son:

```text
tiempo disponible para operar
habilidad de programacion
capital
objetivo: income frecuente vs crecimiento largo plazo
Sharpe esperado
drawdown y duracion de drawdown
costes de transaccion
survivorship bias
decaimiento reciente
nicho/capacidad
competencia institucional
```

Para TSIS, esto deberia existir como `StrategyIntakeChecklist`. Antes de programar una idea, el agente debe registrar:

```text
why_this_strategy
target_universe
expected_holding_period
data_required
known_biases
execution_constraints
capacity_hypothesis
smallcap_specific_risks
```

La advertencia sobre small caps es directa: muchas estrategias academicas funcionan en small/micro caps en backtest, pero la liquidez puede hacer que el PnL ejecutable sea muy inferior.

## Backtesting

**Paginas PDF:** 51-107.

Chan define el backtest como replicacion propia y simulacion historica realista. No basta con aceptar resultados publicados. Replicar sirve para:

```text
entender la estrategia
detectar errores del paper/blog
probar variantes
descubrir restricciones de datos y ejecucion
```

Plataformas discutidas:

```text
Excel
MATLAB
Python
R
QuantConnect / LEAN
Blueshift
```

Para TSIS, la parte importante no es escoger esas plataformas, sino preservar esta regla:

```text
la estrategia que se backtestea debe ser la misma que se ejecuta
```

Esto refuerza la decision del Camino B:

```text
HistoricalDataAdapter
ReplayDataAdapter
LiveDASAdapter
        -> mismo DecisionPolicy
```

## Datos Historicos

**Paginas PDF:** 59-68.

Puntos clave:

```text
split adjustment
dividend adjustment
survivorship-bias-free data
point-in-time data
ruido en high/low diario
stocks que aparecen/desaparecen
universo historico correcto
```

Para TSIS small caps:

```text
SymbolIdentity
CorporateActions
DelistingEvents
PointInTimeUniverse
BadTickFilter
DataQualityReport
```

Chan recomienda escepticismo con datos baratos o incompletos. Para TSIS, esto implica que todo dataset debe tener `dataset_manifest.json` con cobertura, ajustes, universo, proveedor y limitaciones.

## Performance Measurement

**Paginas PDF:** 68-82.

Chan prioriza:

```text
Sharpe ratio
maximum drawdown
maximum drawdown duration
MAR ratio
```

Tambien explica sutilezas de annualizacion y uso de risk-free rate. Para TSIS:

```text
MetricsEngine
EquityCurve
DrawdownCurve
DrawdownDuration
MAR
Sharpe
```

En small caps intraday, estas metricas deben complementarse con:

```text
gross vs net PnL
spread paid
slippage paid
liquidity participation
fees
borrow cost
halt exposure
time-in-market
```

## Pitfalls De Backtesting

**Paginas PDF:** 82-98.

Chan identifica dos grandes errores:

```text
look-ahead bias
data-snooping bias
```

### Look-Ahead Bias

La estrategia no puede usar informacion que no estaba disponible en el momento de decision. Para TSIS, esto debe convertirse en pruebas:

```text
observable_state_only
timestamp_cutoff_enforced
feature_lag_policy
decision_time <= data_available_time
```

Test practico derivado de Chan:

```text
1. correr backtest completo y guardar posiciones/senales
2. truncar los ultimos N dias
3. correr otra vez
4. comparar posiciones/senales hasta T-N
5. cualquier diferencia indica posible leakage/look-ahead
```

Esto deberia ser un test automatizado: `TruncatedDataInvarianceTest`.

### Data-Snooping Bias

Chan advierte que muchas decisiones no numericas tambien cuentan como optimizacion: entrar al open o close, mantener overnight, elegir large/mid/small caps, etc.

Para TSIS:

```text
RunManifest debe contar variantes cuantitativas y cualitativas
StrategySpec debe registrar decisiones probadas
ExperimentRegistry debe conservar intentos fallidos
```

Chan menciona Deflated Sharpe Ratio como correccion posterior. Esto conecta con Lopez de Prado/PBO/DSR.

## Transaction Costs

**Paginas PDF:** 43-44, 98-103, 130-132.

Costes tratados:

```text
commission
bid-ask spread
liquidity cost
opportunity cost de limit orders
market impact
slippage
latency
```

Para TSIS, ninguna metrica debe mostrarse solo en bruto. El engine debe producir:

```text
gross_pnl
fees
spread_cost
slippage_cost
borrow_cost
net_pnl
```

La regla practica de Chan sobre tamanos de orden es muy util para small caps: limitar ordenes como porcentaje del volumen medio. Para TSIS:

```text
ParticipationCap
AverageVolumeGate
DollarVolumeGate
LowPriceStockPenalty
SmallCapLiquidityGate
```

## Strategy Refinement

**Paginas PDF:** 103-107.

Chan permite refinar estrategias, pero exige que el cambio mejore tambien fuera de muestra y tenga base economica o de mercado, no solo ajuste retrospectivo.

Para TSIS:

```text
RefinementProposal
EconomicRationale
TrainImpact
ValidationImpact
TestImpact
ComplexityDelta
GoNoGoDecision
```

Regla para agentes: si una mejora solo funciona en train o solo arregla un caso concreto, no debe entrar en la estrategia principal.

## Business And Infrastructure

**Paginas PDF:** 108-119.

Aunque sea menos cientifico, este bloque aporta requisitos operativos:

```text
broker/API
paper trading account
simulator account
execution speed
liquidity access
VPS
UPS
internet redundancy
monitoring screens
real-time data/news
```

Para TSIS/DAS:

```text
DASBrokerAdapter
BrokerCapabilityMatrix
PaperTradingEnvironment
ExecutionLatencyLog
OperationalRunbook
```

## Execution Systems

**Paginas PDF:** 120-137.

Chan separa:

```text
semiautomated trading system
fully automated trading system
```

Flujo ATS:

```text
latest market data
    -> strategy algorithm
    -> orders
    -> broker API
    -> executions
```

Para TSIS, el punto critico es comparar continuamente:

```text
theoretical orders from backtest/replay
vs
orders actually generated by ATS
vs
fills received from broker/paper account
```

Esto exige:

```text
OrderIntentLedger
OrderSubmissionLedger
BrokerOrderEventLedger
FillLedger
BacktestVsPaperReconciler
```

## Paper Trading

**Paginas PDF:** 132-133.

Chan presenta paper trading como el puente entre backtest y real money. Sirve para detectar:

```text
software bugs
look-ahead no visible en backtest
data timing issues
operational delays
unexpected transaction costs
capital usage real
trade frequency real
PnL volatility real
```

Para TSIS:

```text
ShadowTradingHarness
PaperBrokerAdapter
ExpectedVsObservedTradeReport
DailyOperationalChecklist
```

No debe ser opcional. Para small caps, paper/shadow es donde se descubren restricciones de liquidez, velocidad, scanner, halts y short availability.

## Divergencia Backtest Vs Live

**Paginas PDF:** 133-137.

Chan propone diagnostico de divergencia:

```text
bugs en ATS
trades reales no coinciden con backtest
execution costs superiores
illiquidity / market impact
data-snooping bias
regime shift
short-sale rules
hard-to-borrow
```

Esto encaja con Pardo:

```text
EvaluationProfile
TradeProfile
LivePerformanceMonitor
```

Para TSIS, cada estrategia en shadow/live debe tener alertas de divergencia y una decision:

```text
continue
reduce
pause
retire
re-research
```

## Money And Risk Management

**Paginas PDF:** 138-165.

Chan usa Kelly como marco para:

```text
capital allocation
leverage
portfolio of strategies
risk reduction after losses
```

Puntos practicos:

```text
usar half-Kelly o menos por incertidumbre
capar leverage por peor perdida historica de un periodo
recalcular sizing con estadisticas trailing
reducir exposicion cuando el modelo pierde
evitar sobreapalancamiento tras una buena racha
```

Riesgos tratados:

```text
position risk
market risk
specific risk
model risk
software risk
natural disaster / operational risk
```

Para TSIS:

```text
RiskSizingModel
CapitalAllocator
MaxLossPerTrade
MaxDailyLoss
MaxPortfolioExposure
ModelRiskMonitor
SoftwareRiskReconciliation
OperationalRiskChecklist
```

## Regimes, Mean Reversion And Momentum

**Paginas PDF:** 166-181.

Chan distingue dos familias:

```text
mean reversion
momentum / trend following
```

Para small caps:

```text
mean reversion puede inflarse por malos ticks
survivorship afecta fuerte a mean reversion
momentum puede venir de noticias, large orders, herding o squeezes
competencia reduce oportunidades y holding period
```

TSIS debe guardar `MarketState` y `EventState` porque una regla no tiene el mismo sentido en todos los regimenes:

```text
high_volume_gap
news_momentum
halt_reopen
low_float_squeeze
liquidity_event
mean_reversion_after_exhaustion
```

Chan introduce Conditional Parameter Optimization como ML para escoger parametros condicionados al estado de mercado. En TSIS esto es futuro, no v0.1, pero encaja con:

```text
RegimeConditionalParameterPolicy
StateFeatureStore
ModelRegistry
ParameterDecisionLedger
```

## Stationarity, Cointegration And Pairs

**Paginas PDF:** 182-200.

Chan explica que cointegration no es correlation. Para pairs/stat arb:

```text
correlation -> relacion de retornos a corto plazo
cointegration -> spread estacionario a largo plazo
```

Para TSIS small caps, esto es fuente secundaria. Sirve para futuras estrategias long/short o spreads, pero no bloquea el primer motor.

Nodos:

```text
PairCandidateResearch
HedgeRatioEstimator
CointegrationTest
SpreadState
MeanReversionHalfLife
```

## Factor Models

**Paginas PDF:** 200-210.

Chan resume factor models/APT:

```text
market beta
SMB
HML
momentum factors
fundamental factors
technical factors
PCA/statistical factors
specific returns
```

Para TSIS, factor models pueden servir para:

```text
risk decomposition
universe filters
portfolio exposure control
strategy families futuras
```

No son prioridad para `BACKTEST_VERTICAL_SLICE_V0_1`.

## Exit Strategy

**Paginas PDF:** 210-215.

Tipos de salida:

```text
fixed holding period
target price / profit cap
latest entry signal
stop price
```

Regla importante:

```text
stop loss encaja mejor con momentum
stop loss puede ser perjudicial en mean reversion
```

Para TSIS, `ExitPolicy` debe depender del tipo de estrategia y del estado:

```text
MomentumExitPolicy
MeanReversionExitPolicy
NewsInvalidationExit
TimeStop
ProfitTarget
SignalFlipExit
RiskStop
```

Chan tambien usa half-life de Ornstein-Uhlenbeck para mean reversion. Es futuro para pairs/spreads, no para el primer motor.

## Seasonal And High Frequency Strategies

**Paginas PDF:** 215-235.

Seasonal:

```text
las estacionalidades de equity pueden decaer
las de commodities pueden tener base economica mas persistente
requieren out-of-sample real por pocas observaciones anuales
```

High frequency:

```text
alta frecuencia puede tener Sharpe alto por muchas apuestas
requiere bid/ask, a veces order book
sin costes realistas, muchos backtests HFT son ficcion
la ejecucion y latencia son parte central del edge
```

Para TSIS small caps intraday:

```text
QuoteEvent
TradeEvent
SpreadModel
LatencyModel
OrderBookDataFuture
HFTReadinessGate
```

## Capacity And Independent Trader Edge

**Paginas PDF:** 238-243.

Chan concluye que la ventaja del trader independiente esta en baja capacidad:

```text
estrategias demasiado pequenas para fondos grandes
liquidez temporal
menos restricciones institucionales
mayor flexibilidad
```

Para TSIS small caps, esto es una razon para investigar, no una prueba de edge. La capacidad debe medirse:

```text
capacity_estimate
participation_rate
dollar_volume_available
spread/slippage sensitivity
number_of_symbols_needed
decay_monitor
```

## Blueprint TSIS Derivado

```text
IdeaSource
  -> StrategyIntakeChecklist
  -> DataRequirementSpec
  -> DataQualityGate
  -> BacktestImplementation
  -> PitfallAudit
  -> TransactionCostModel
  -> Train/Test or WFA
  -> SensitivityAnalysis
  -> PaperTradingHarness
  -> BacktestVsPaperReconciler
  -> RiskSizingModel
  -> CapacityModel
  -> LiveDivergenceMonitor
```

Artefactos fisicos sugeridos:

```text
strategy_intake.md
data_requirements.json
data_quality_report.md
pitfall_audit.md
lookahead_invariance_test.parquet
transaction_cost_assumptions.json
sensitivity_grid.parquet
paper_orders.parquet
paper_fills.parquet
backtest_vs_paper_reconciliation.md
risk_sizing_report.json
capacity_report.md
live_divergence_report.md
```

## Quality Gates TSIS

| Gate | Pregunta | Sale si falla |
|---|---|---|
| `IDEA_SUITABLE` | Encaja con capital, datos, tiempo, universo y capacidad? | no programar todavia |
| `DATA_USABLE` | Datos ajustados, point-in-time y sin sesgos graves? | corregir data foundation |
| `NO_LOOKAHEAD` | Senales invariables al truncar futuro? | corregir feature/decision timing |
| `NO_OBVIOUS_SNOOPING` | Pocos parametros y variantes registradas? | simplificar o pasar a validacion robusta |
| `COSTS_INCLUDED` | Spread, fees, slippage y market impact basico incluidos? | no aceptar net PnL |
| `LIQUIDITY_OK` | Ordenes dentro de volumen/dollar volume razonable? | reducir size/universo o rechazar |
| `PAPER_MATCHES_BACKTEST` | Paper orders/fills explican diferencias frente a teorico? | depurar ATS/fill model |
| `RISK_SIZE_OK` | Leverage/sizing soporta drawdowns y fat tails? | reducir capital o bloquear |
| `LIVE_DIVERGENCE_OK` | TradeProfile se mantiene cerca de EvaluationProfile? | revisar, pausar o retirar |

## Limitaciones

- No proporciona una arquitectura event-driven completa.
- Los ejemplos de codigo son pedagogicos y no deben copiarse como nucleo de TSIS.
- Muchas recomendaciones son de trader independiente, no de motor institucional.
- La discusion de Python contiene opiniones y advertencias; TSIS ya esta orientado a Python por integracion local.
- No resuelve delistings/corporate actions/halts/short availability con detalle operativo suficiente.
- No sustituye a Harris para microestructura ni a Lopez de Prado/Pardo para validacion rigurosa.

## Lectura Para Agentes

| Si trabajas en... | Leer primero | Salida esperada |
|---|---:|---|
| filtro inicial de estrategias | 28-50 | `StrategyIntakeChecklist` |
| datos historicos small caps | 59-68, 82-88 | `DataQualityGate` |
| metricas basicas | 68-82 | `MetricsEngine` |
| look-ahead/data-snooping | 82-98 | `PitfallAudit`, `TruncatedDataInvarianceTest` |
| costes de transaccion | 43-44, 98-103, 130-132 | `TransactionCostModel` |
| ATS y DAS/live | 120-137 | `ExecutionReadiness`, `BrokerAdapter` |
| paper/shadow trading | 132-137 | `PaperTradingHarness`, `BacktestVsPaperReconciler` |
| sizing/risk | 138-165 | `RiskSizingModel`, `CapitalAllocator` |
| regimes y strategy type | 166-181 | `RegimeMonitor`, `MarketState` |
| pairs/stat arb | 182-200 | `CointegrationResearch` |
| factor models | 200-210 | `FactorExposureModel` |
| exit policies | 210-215 | `ExitPolicy` |
| HFT/intraday realism | 230-235 | `QuoteEvent`, `SpreadModel`, `LatencyModel` |
| capacity | 238-243 | `CapacityModel`, `SmallCapLiquidityGate` |

