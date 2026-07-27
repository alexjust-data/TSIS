# Source Map - Algorithmic Trading Systems and Strategies - Dolzhenko

Mapa inverso para agentes: que extraer de Dolzhenko y donde encaja en TSIS.

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `algorithmic_trading_systems_strategies_dolzhenko` |
| Titulo | `Algorithmic Trading Systems and Strategies: A New Approach` |
| Autora | Viktoria Dolzhenko |
| Editorial | Apress / Springer Nature |
| Anio local del PDF | 2024 |
| Paginas PDF | 326 |
| Palabras extraidas aprox. | 85895 |
| Tipo de fuente | Arquitectura e implementacion de plataforma de trading |
| Estado | Extraido e indexado |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Caps. 1-2 | Enfoques, teoria general, ordenes, riesgo, testing, metricas | `StrategyIntake`, `OrderModel`, `MetricsCatalog` |
| Cap. 3 | Requirements, Indicator, Signal, Strategy, Theory | `DomainModel`, `StrategySpec` |
| Cap. 4 | Subsystems, queue, FSM, core, sandbox, gateway, master data | `ArchitectureBlueprint`, `RuntimeBoundary` |
| Cap. 5 | Framework, clean architecture, DDD, persistence, workers | `ImplementationGuidelines` |
| Caps. 6-7 | Optimization algorithms and implementation | `OptimizationEngine` |
| Cap. 8 | Core module, events, signals, indicators, position FSM | `CoreDecisionEngine`, `PositionStateMachine` |
| Cap. 9 | Docker/Kubernetes/Helm | `DeploymentRunbook`, future only |

## Mapa arquitectura TSIS

```text
Dolzhenko
    |
    +-- Domain discovery
    |       -> Indicator
    |       -> Signal
    |       -> ConditionTree
    |       -> Strategy
    |       -> Theory
    |
    +-- System architecture
    |       -> StrategySearch
    |       -> SandboxExchange
    |       -> RealTradingRuntime
    |       -> ExchangeGateway
    |       -> MasterData
    |
    +-- Core runtime
    |       -> StrategyRuntimeContext
    |       -> UpdateCandleEvent
    |       -> OrderStatusEvent
    |       -> FillEvent
    |       -> PlaceOrderCommand
    |
    +-- State machine
            -> PositionProcess
            -> SystemOrder
            -> ActivePositionQueue
            -> StopAndAlert
```

## Preguntas que esta fuente responde

- Que entidades software aparecen al construir una plataforma propia.
- Como separar idea de estrategia parametrizada.
- Como crear un core que sirva para backtest/search y live.
- Como organizar eventos de candle, order status y deals.
- Como estructurar condition trees y signals.
- Como manejar posiciones con una state machine ligera.
- Como pensar en services, queues, adapters y master data.
- Como preparar infraestructura reproducible sin que sea el primer bloqueo.

## Preguntas que no responde

- Validacion cientifica fuerte contra overfitting.
- Small caps, halts, borrow, delistings y corporate actions.
- Profundidad en microestructura, L2, slippage real o market impact.
- Implementacion Python especifica.
- Nautilus/LEAN-level order/fill realism.

## Prioridad de lectura TSIS

1. Cap. 8 completo: shared core, events, signals, positions.
2. Cap. 3: domain model y requirements.
3. Cap. 4: subsystem boundaries, gateway, message broker y master data.
4. Caps. 6-7: optimization engine.
5. Cap. 5: clean architecture y persistence.
6. Cap. 9 solo cuando se prepare despliegue/servicios.
