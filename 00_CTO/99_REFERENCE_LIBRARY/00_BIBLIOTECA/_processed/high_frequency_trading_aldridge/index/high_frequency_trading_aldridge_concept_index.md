# Concept Index - High-Frequency Trading - Irene Aldridge

Indice orientado a agentes. Paginas aproximadas segun PDF local.

## Menu

- [Microestructura y ordenes](#microestructura-y-ordenes)
- [Datos HF](#datos-hf)
- [Costes, performance y capacity](#costes-performance-y-capacity)
- [Ejecucion e impacto](#ejecucion-e-impacto)
- [Implementacion y riesgo](#implementacion-y-riesgo)
- [Uso recomendado en TSIS](#uso-recomendado-en-tsis)

## Microestructura y ordenes

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| CLOB / limit order book | 69-76 | future `OrderBookSnapshot` |
| Liquidity as finite limit orders | 72-75 | `AvailableLiquidityModel` |
| Market order sweeping | 74-75 | `MarketOrderFillModel` |
| FIFO price-time priority | 75-76 | future queue approximation |
| Pro-rata matching | 76-77 | venue-specific fill model |
| Passive/aggressive order | 77-79 | `OrderAggressiveness` |
| Spread crossing | 78-79 | `SideAwareFillPrice` |
| Nonexecution risk of limit orders | 79 | `LimitFillProbability` |
| Complex order types | 79-80 | future order model |
| Trading hours / extended hours | 80-81 | `SessionCalendar` |
| Fragmentation and NBBO | 82-84 | venue/routing assumptions |
| Rebates and inverted venues | 84+ | `FeeModel` |

## Datos HF

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Level I data | 91-94 | `QuoteEvent` |
| Level II data | 91, 94 | future `OrderBookEvent` |
| Timestamp precision | 93-94 | `TimestampPolicy` |
| Bid/ask/last trade fields | 91-94 | `QuoteTradeSchema` |
| Tick data volume | 95-98 | storage/performance planning |
| Bid-ask bounce | 98-102 | `BidAskBounceFilter` |
| Roll spread model | 101-102 | `SpreadEstimator` |
| Midquote | 102 | `MidPriceFeature` |
| Size-weighted quote | 102 | `WeightedMidPriceFeature` |
| Non-normal tick returns | 102-109 | robust statistics |
| Irregular spacing | 109-116 | `EventTimeClock` |
| Last tick sampling | 109-111 | `SamplingPolicy` |
| Linear interpolation sampling | 111-113 | `InterpolationPolicy` |
| Duration models | 113-116 | future event-time features |
| Volume clock | 116 | future volume bars |
| Trade direction classification | 116-121 | `TradeClassifier` |
| Tick rule | 117-118 | `TickRuleClassifier` |
| Quote rule / Lee-Ready / BVC | 116-121 | future classifiers |

## Costes, performance y capacity

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Transparent execution costs | 123-127 | `CommissionFeeModel` |
| Implicit execution costs | 127-132 | `SlippageModel` |
| Market impact | 132-153 | `MarketImpactModel` |
| Permanent impact | 143-153 | future impact model |
| Performance measures | 155-169 | `PerformanceEngine` |
| Comparative ratios | 169-176 | `MetricsCatalog` |
| Performance attribution | 176-178 | `AttributionReport` |
| Capacity evaluation | 178-183 | `CapacityModel` |
| Alpha decay | 183 | `AlphaDecayMonitor` |

## Ejecucion e impacto

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Algorithmic execution vs alpha | 31-35, 335+ | `ExecutionPolicy` |
| TWAP | Ch. 15 | baseline execution algo |
| VWAP | Ch. 15 | baseline execution algo |
| POV | Ch. 15 | participation policy |
| Order routing algorithms | Ch. 15 | `OrderRoutingPolicy` |
| Detectability of TWAP/VWAP | 381-385 | randomization/anti-signaling |
| Fourier analysis of order flow | 381-385 | order-flow detection |
| Order book replenishment | 386-395 | `BookResiliencyModel` |
| Temporary/permanent impact | 386-395 | `ImpactScenario` |
| Practical optimal execution steps | 395 | future `OptimalExecutionResearch` |

## Implementacion y riesgo

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Development lifecycle | 397-400 | `EngineeringProcess` |
| Planning/analysis/design/implementation/maintenance | 398-400 | governance |
| Test cases defined in design | 399-400 | `AcceptanceTests` |
| Integration testing | 399-400 | `IntegrationTestSuite` |
| Core engine functions | 401 | `CoreEngine` |
| Runtime quote archive | 401 | `MarketDataArchive` |
| Runtime econometric analysis | 401 | online feature computation |
| Runtime portfolio management | 401 | `OnlinePortfolio` |
| Execution confirmations | 401 | `OrderEvent` |
| Runtime P&L | 401 | `RuntimePnL` |
| Dynamic risk | 401 | `DynamicRiskEngine` |
| HFT risk management | Ch. 14 | `RuntimeRiskMonitor` |

## Uso recomendado en TSIS

| Tarea de agente | Consultar |
|---|---|
| Definir QuoteEvent/TradeEvent | Ch. 4 |
| Endurecer fill model por bid/ask | Ch. 3-5 |
| Crear spread/slippage model | Ch. 3-5 |
| Disenar capacity para small caps | Ch. 5-6 |
| Crear future order book abstractions | Ch. 3-4 |
| Separar alpha de execution algo | Ch. 1, 15 |
| Investigar market impact | Ch. 5, 15 |
| Definir core online futuro | Ch. 16 |
| Crear tests de runtime | Ch. 16 |
