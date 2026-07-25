# Concept Index - Algorithmic Trading and DMA - Barry Johnson

## Menu

- [DMA y mercados](#dma-y-mercados)
- [Ordenes y algoritmos](#ordenes-y-algoritmos)
- [TCA y estrategia optima](#tca-y-estrategia-optima)
- [Implementacion](#implementacion)
- [Uso TSIS](#uso-tsis)

## DMA y mercados

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Algorithmic trading vs DMA | 3-25 | `ExecutionMode` |
| Market microstructure | 27-51 | `MarketModel` |
| Market structure / protocols | 30-38 | `VenueModel` |
| World markets / asset classes | 53-78 | `InstrumentContract` |

## Ordenes y algoritmos

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Market orders | 84 | `MarketOrder` |
| Limit orders | 85 | `LimitOrder` |
| Duration/fill/routing instructions | 88-95 | `OrderInstruction` |
| Hidden/conditional/routed/crossing orders | 96-112 | `AdvancedOrderType` |
| TWAP | 120 | `TWAPAlgo` |
| VWAP | 123 | `VWAPAlgo` |
| POV | 127 | `POVAlgo` |
| Implementation Shortfall | 133 | `ISAlgo`, `ArrivalPriceBenchmark` |
| Adaptive Shortfall | 138 | `AdaptiveISAlgo` |
| Liquidity-driven algorithms | 146 | `LiquiditySeekingAlgo` |

## TCA y estrategia optima

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Pre-trade analysis | 165-167 | `PreTradeTCA` |
| Post-trade analysis | 167-172 | `PostTradeTCA` |
| Market impact | 173-184, 293 | `ImpactModel` |
| Timing risk | 173-184, 299 | `TimingRiskModel` |
| Efficient trading frontier | 192-199 | `ExecutionOptimizer` |
| Algorithm choice factors | 199-208 | `ExecutionDecisionTree` |

## Implementacion

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Order placement | 221-254 | `OrderPlacementPolicy` |
| Signalling risk | 234 | `SignalingRiskScore` |
| Venue choice | 235 | `VenueRouter` |
| Order aggressiveness | 237 | `AggressivenessPolicy` |
| Hidden liquidity | 247-250 | `HiddenLiquidityModel` |
| Execution tactics | 257-275 | `ExecutionTacticLibrary` |
| Forecasting market conditions | 278-292 | `ShortHorizonMarketForecast` |
| Infrastructure requirements | 311-337 | `ExecutionInfrastructure` |
| Testing trading rules | 329-332 | `ExecutionAlgoTestHarness` |

## Uso TSIS

| Tarea | Consultar |
|---|---|
| Disenar `Order` y order instructions | Ch. 4 |
| Disenar execution simulator | Ch. 5-10 |
| Separar parent/child orders | Ch. 5, Ch. 11 |
| Crear TCA | Ch. 6-7 |
| Modelar routing/venue choice | Ch. 8, Ch. 11 |
| Disenar infra para live execution | Ch. 11 |

