# Source Map - High-Frequency Trading - Irene Aldridge

Mapa inverso para agentes: que extraer de Aldridge y donde encaja en TSIS.

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `high_frequency_trading_aldridge` |
| Titulo | `High-Frequency Trading` |
| Autora | Irene Aldridge |
| Editorial | Wiley |
| Paginas PDF | 456 |
| Palabras extraidas aprox. | 105114 |
| Tipo de fuente | Microestructura, datos HF, costes, HFT, market impact, implementacion |
| Estado | Extraido e indexado |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Ch. 1-2 | Modern markets, HFT vs algo/systematic, systems/latency | `ExecutionArchitecture`, `LatencyPolicy` |
| Ch. 3 | Orders, LOB, matching, fragmentation, fees | `OrderModel`, `FillModel`, `FeeModel` |
| Ch. 4 | HF data properties, sampling, trade direction | `QuoteTradeSchema`, `SamplingPolicy`, `TradeClassifier` |
| Ch. 5 | Trading costs and market impact | `CostModel`, `SlippageModel`, `MarketImpactModel` |
| Ch. 6 | Performance, attribution, capacity, alpha decay | `PerformanceEngine`, `CapacityModel` |
| Ch. 8-12 | HFT strategy families and manipulation risks | future research, risk controls |
| Ch. 14 | HFT risk | `RuntimeRiskMonitor` |
| Ch. 15 | Execution algos and optimal execution | `ExecutionPolicy`, `OrderRoutingPolicy` |
| Ch. 16 | Implementation lifecycle and core engine | `OnlineCoreEngine`, `AcceptanceTests` |

## Mapa arquitectura TSIS

```text
Aldridge
    |
    +-- Market data realism
    |       -> QuoteEvent
    |       -> TradeEvent
    |       -> OrderBookSnapshot
    |       -> EventTimeClock
    |
    +-- Microstructure
    |       -> SpreadModel
    |       -> LiquidityModel
    |       -> TradeDirectionClassifier
    |
    +-- Execution
    |       -> SideAwareFillModel
    |       -> FeeModel
    |       -> SlippageModel
    |       -> MarketImpactModel
    |       -> ParticipationCap
    |
    +-- Online runtime
            -> CoreEngine
            -> RuntimePnL
            -> DynamicRisk
            -> ExecutionConfirmations
```

## Preguntas que esta fuente responde

- Que diferencia hay entre HFT, systematic trading y algorithmic execution.
- Que contiene Level I y Level II data.
- Por que tick data no se comporta como daily bars.
- Como afecta el bid-ask bounce a volatilidad y retornos.
- Que implica no tener buy/sell identifiers en trades.
- Como funcionan FIFO, pro-rata, passive/aggressive orders.
- Que costes transparentes e implicitos debe medir TSIS.
- Como pensar capacity, alpha decay y market impact.
- Que debe hacer un core engine online.

## Preguntas que no responde

- Como construir el primer backtester Python.
- Como estructurar los artefactos Parquet de TSIS.
- Como validar estadisticamente multiples estrategias.
- Como adaptar todo especificamente a Polygon/DAS.
- Como implementar una simulacion retail simple de v0.1.

## Prioridad de lectura TSIS

1. Ch. 3: microestructura, orders, order book.
2. Ch. 4: HF data, sampling, bid-ask bounce, trade direction.
3. Ch. 5: trading costs y market impact.
4. Ch. 6: performance/capacity/alpha decay.
5. Ch. 15: execution algorithms.
6. Ch. 16: online core implementation.
7. Ch. 8-14 solo cuando se investiguen HFT strategies/risk/regulation.
