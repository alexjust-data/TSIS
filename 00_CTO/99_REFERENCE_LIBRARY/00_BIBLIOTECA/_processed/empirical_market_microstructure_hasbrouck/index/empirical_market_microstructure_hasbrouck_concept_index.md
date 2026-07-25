# Concept Index - Empirical Market Microstructure - Joel Hasbrouck

## Menu

- [Precios y spreads](#precios-y-spreads)
- [Trades y order flow](#trades-y-order-flow)
- [Limit orders](#limit-orders)
- [Liquidez](#liquidez)
- [Uso TSIS](#uso-tsis)

## Precios y spreads

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Martingale / random walk efficient price | 7-12 | `EfficientPriceModel` |
| Roll model | 12-15 | `SpreadEstimator`, `BidAskBounceAudit` |
| MA/AR price changes | 15-20 | `MicrostructureNoiseModel` |
| Sequential trade asymmetric information | 21-32 | `AdverseSelectionFeature` |
| Strategic trade models | 33-43 | `PriceImpactResearch` |
| Generalized Roll model | 44-52 | `EfficientPriceEstimate` |
| Random-walk/noise decomposition | 53-63 | `NoiseVsPermanentImpactReport` |

## Trades y order flow

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Inventory control | 72-78 | `InventoryEffectModel` |
| Trade direction series | 78-79 | `TradeDirectionClassifier` |
| Vector AR/MA models | 86-92 | `OrderFlowVAR` |
| Impulse response | 88-89 | `PriceResponseCurve` |
| Forecast variance decomposition | 90-92 | `InformationShareReport` |
| Prices and trades statistical models | 93-102 | `PriceImpactModel` |
| Structural models | 103-106 | `SpreadComponentModel` |
| PIN | 107-115 | `InformationAsymmetryFeature` |
| Cointegration / price discovery | 117-122 | `LinkedVenuePriceDiscovery` |

## Limit orders

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Limit orders and dealer quotes | 124-134 | `LimitOrderModel` |
| Execution uncertainty | 135-139 | `LimitFillProbability` |
| Limit order submission strategies | 140-145 | `OrderPlacementPolicy` |
| Dynamic equilibrium models | 146-148 | research futura |

## Liquidez

| Concepto | Paginas aprox. | Uso TSIS |
|---|---:|---|
| Depth, breadth, resilience | 4-5 | `LiquidityDefinition` |
| Fixed transaction costs and pricing | 150-158 | `LiquidityPremiumFeature` |
| Liquidity ratio / illiquidity ratio | 161-164 | `LiquidityMetricLibrary` |
| Stochastic liquidity | 164 | `LiquidityRegimeMonitor` |

## Uso TSIS

| Tarea de agente | Consultar |
|---|---|
| Disenar `QuoteEvent`/`TradeEvent` | Ch. 1, Ch. 3, Ch. 13 |
| Evitar fills con `last_price` ingenuo | Ch. 3, Ch. 7 |
| Crear `OrderFlowBuilder` | Ch. 10-13 |
| Estimar price impact | Ch. 12-14 |
| Evaluar limit orders | Ch. 18-21 |
| Crear liquidity gate para small caps | Ch. 1, Ch. 22 |

