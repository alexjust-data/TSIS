# Source Map - Empirical Market Microstructure - Joel Hasbrouck

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `empirical_market_microstructure_hasbrouck` |
| Tipo | notas PhD / microestructura empirica |
| Estado | extraido e indexado |
| Uso principal | microestructura, trades/quotes, order flow, spread, impact |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Part I | Roll model, random walk/noise, asymmetric info | `SpreadModel`, `EfficientPriceEstimator` |
| Part II | trade direction, VAR, price impact, PIN, cointegration | `OrderFlowBuilder`, `PriceImpactModel` |
| Part III | limit order economics and execution uncertainty | `LimitFillModel`, `QueueAssumptionLedger` |
| Part IV | liquidity measures and asset pricing effects | `LiquidityGate`, `CapacityModel` |

## Preguntas que responde

- Como separar efficient price y transaction price.
- Como interpretar bid/ask bounce.
- Como usar signed order flow para medir impacto.
- Como pensar en informacion asimetrica y adverse selection.
- Por que limit orders tienen riesgo de no ejecucion y seleccion adversa.
- Que medidas empiricas de liquidez pueden alimentar TSIS.

## Preguntas que no responde

- Como implementar el motor event-driven.
- Como crear un OMS.
- Como conectar DAS/Polygon.
- Como hacer PBO/DSR.

## Prioridad de lectura

1. Ch. 1, 3 y 7 para `SpreadModel`.
2. Ch. 10-14 para `OrderFlowBuilder` y price impact.
3. Ch. 18-20 para limit orders.
4. Ch. 22 para liquidez y small caps.

