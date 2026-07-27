# High-Frequency Trading - Irene Aldridge

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Microestructura y order book](#bloque-a---microestructura-y-order-book)
- [Bloque B - Datos high-frequency](#bloque-b---datos-high-frequency)
- [Bloque C - Costes, performance y capacity](#bloque-c---costes-performance-y-capacity)
- [Bloque D - Estrategias, riesgo y market impact](#bloque-d---estrategias-riesgo-y-market-impact)
- [Bloque E - Implementacion](#bloque-e---implementacion)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Aldridge es una referencia fuerte para microestructura, tick data, costes, performance/capacity HFT, market impact, optimal execution e implementacion de sistemas automatizados de baja latencia.

Para TSIS small caps, no significa que debamos construir HFT. Significa que debemos entender que:

```text
fills, slippage, spread, bid-ask bounce, irregular timestamps, liquidity depletion, order book replenishment y market impact
```

no son detalles cosmeticos. Determinan si un backtest es ejecutable.

## Rol dentro de TSIS

Encaja en:

```text
MicrostructureModel
QuoteTradeSchema
ExecutionRealism
SlippageModel
SpreadModel
LatencyModel
CapacityModel
MarketImpactModel
OrderRoutingPolicy
HFTDataQualityGate
```

Debe usarse despues de tener el motor event-driven basico, cuando TSIS empiece a endurecer small caps con quotes/trades y ejecucion realista.

## Mapa rapido de capitulos

| Capitulo | Uso TSIS |
|---|---|
| 1. Modern Markets and HFT | Diferencia entre systematic, algo execution y HFT |
| 2. Technology, Systems and HFT | Messaging, software, latency, data tests |
| 3. Microstructure, Orders, LOB | Orders, CLOB, FIFO/pro-rata, passive/aggressive |
| 4. High-Frequency Data | Tick data, Level I/II, bid-ask bounce, sampling, trade direction |
| 5. Trading Costs | Transparent/implicit costs, market impact |
| 6. Performance and Capacity | Metrics, attribution, capacity, alpha decay |
| 7. Business of HFT | Processes, markets, economics |
| 8. Statistical Arbitrage | HFT stat arb context |
| 9. Directional Event Strategies | Event trading and tradable news |
| 10-11. Market Making | Inventory/order-flow information |
| 12. Additional HFT and manipulation | Latency arb, spoofing, quote stuffing, crashes |
| 13. Regulation | Regulatory constraints |
| 14. Risk Management | HFT risk measurement |
| 15. Minimizing Market Impact | TWAP/VWAP/POV, optimal execution, book resiliency |
| 16. Implementation | Development lifecycle, core engine, testing |

## Bloque A - Microestructura y order book

Capitulo 3 cubre:

- limit order books;
- best bid/ask;
- finite liquidity;
- market order sweeping;
- price-time FIFO;
- pro-rata matching;
- passive/aggressive orders;
- rebates;
- normal vs inverted venues;
- fragmentation and NBBO.

La leccion para TSIS:

```text
market order fill at last price = simulacion ingenua
```

Incluso sin L2 completo, el simulador debe declarar:

```text
spread assumption
side-aware fill price
available volume cap
latency assumption
fee/rebate assumption
```

## Bloque B - Datos high-frequency

Capitulo 4 es esencial para futuros `QuoteEvent` y `TradeEvent`.

Datos Level I:

```text
best bid price
best ask price
best bid size
best ask size
last trade price
last trade size
timestamp
symbol/venue
```

Datos Level II:

```text
order book changes away from best bid/ask
new limit orders
cancellations
depth by price level
```

Problemas que TSIS debe representar:

- tick data voluminoso;
- bid-ask bounce;
- retornos no normales;
- timestamps irregulares;
- sampling por last tick o interpolacion;
- duration carries information;
- ausencia de buy/sell identifiers;
- tick rule, quote rule, Lee-Ready, BVC.

## Bloque C - Costes, performance y capacity

Capitulos 5 y 6 conectan coste y capacidad:

```text
transparent costs
implicit costs
bid-ask spread
slippage
market impact
permanent impact
capacity
alpha decay
performance attribution
```

Para small caps:

```text
capacity = no es solo AUM, es volumen disponible, spread, impacto y decay de edge
```

TSIS debe medir resultados antes y despues de costes por separado.

## Bloque D - Estrategias, riesgo y market impact

Capitulo 15 trata execution algorithms:

- TWAP;
- VWAP;
- POV;
- order-routing;
- minimal impact;
- advanced optimal execution;
- order book replenishment/resiliency;
- temporary/permanent impact.

La idea practica:

```text
la ejecucion es un algoritmo propio, no un detalle posterior al signal
```

Para TSIS v0.1 no hace falta optimal execution avanzado, pero si:

```text
ExecutionPolicy
ParticipationCap
OrderSlicePolicy
ImpactScenario
```

## Bloque E - Implementacion

Capitulo 16 describe lifecycle de desarrollo:

```text
planning
analysis
design
implementation
maintenance
```

Y un core engine que:

- recibe, evalua y archiva quotes;
- ejecuta econometria runtime;
- gestiona portfolio runtime;
- inicia y transmite senales;
- recibe confirmaciones de ejecucion;
- calcula P&L runtime;
- gestiona riesgo dinamico.

Esto es una especificacion funcional para el futuro TSIS online.

## Blueprint TSIS derivado

```text
ExecutionRealism
    |
    +-- MarketData
    |       -> QuoteEvent
    |       -> TradeEvent
    |       -> OrderBookSnapshot
    |
    +-- Microstructure
    |       -> SpreadModel
    |       -> BidAskBounceFilter
    |       -> TradeDirectionClassifier
    |
    +-- Execution
    |       -> SideAwareFillModel
    |       -> SlippageModel
    |       -> ParticipationCap
    |       -> MarketImpactScenario
    |
    +-- Runtime
            -> CoreEngine
            -> RuntimePnL
            -> DynamicRisk
            -> ExecutionConfirmations
```

## Quality gates para agentes

- No usar trade price como fill universal sin declarar lado y spread.
- No estimar volatilidad intradia sin controlar bid-ask bounce.
- No convertir ticks a barras sin documentar sampling policy.
- No asumir timestamps regulares en quotes/trades.
- No evaluar small caps sin spread y volumen disponible.
- No estimar capacity sin market impact y alpha decay.
- No mezclar algorithmic execution con alpha generation.
- No llamar HFT a cualquier estrategia intradia.

## Limitaciones

- No es un manual de backtester Python.
- Mucha teoria HFT excede TSIS v0.1.
- Algunos modelos requieren L2/tick data que TSIS puede no tener aun.
- No sustituye a Harris/Hasbrouck/Johnson; los complementa.
- No sustituye validacion estadistica tipo Lopez de Prado/PBO/DSR.
