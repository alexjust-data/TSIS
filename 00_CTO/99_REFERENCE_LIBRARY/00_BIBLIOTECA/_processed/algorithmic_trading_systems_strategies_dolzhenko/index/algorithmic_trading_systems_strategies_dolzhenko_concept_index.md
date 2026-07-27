# Concept Index - Algorithmic Trading Systems and Strategies - Dolzhenko

Indice orientado a agentes. Paginas aproximadas segun PDF local.

## Menu

- [Dominio y requisitos](#dominio-y-requisitos)
- [Arquitectura](#arquitectura)
- [Optimizacion](#optimizacion)
- [Core y runtime](#core-y-runtime)
- [Infraestructura](#infraestructura)
- [Uso recomendado en TSIS](#uso-recomendado-en-tsis)

## Dominio y requisitos

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Crear plataforma propia | 23-26 | Justificacion Camino B |
| Order execution | 32-35 | `OrderModel`, `ExecutionPort` |
| Margin/leverage | 35+ | `BuyingPowerModel`, `MarginModel` |
| Performance indicators | 20, Ch. 2 | `MetricsCatalog` |
| Indicator entity | 72-73 | `Indicator` |
| Signal entity | 73-74 | `Signal` |
| Strategy entity | 74-76 | `StrategySpec`, `StrategyInstance` |
| Theory vs Strategy | 75-77 | `StrategyIdea` vs `ParameterizedStrategy` |
| Condition tree | 78-80 | `ConditionTree`, `RuleExpression` |
| Open/close signal separation | 74-76 | `EntrySignal`, `ExitSignal` |
| Capital management method | 74-80 | `SizingModel` |
| Risk control method | 74-80 | `RiskControl` |

## Arquitectura

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Requirements elicitation | 70-72 | `ArchitectureDiscovery` |
| Subsystem identification | 70-71 | `ModuleBoundaryReview` |
| Strategy Search Subsystem | Ch. 4 | `StrategySearch` |
| Sandbox Exchange | Ch. 4 | `SandboxExecutionVenue` |
| Real Trading Subsystem | Ch. 4 | `LiveTradingRuntime` |
| Exchange Gateway | 142-144 | `BrokerGateway`, `ExecutionAdapter` |
| Kafka/message broker | 143-144 | future `EventBus`; v0.1 can be in-process |
| Strategy Manager | 152-154 | `StrategyRegistry`, `RuntimeSupervisor` |
| Instrument Service | 153-154 | `InstrumentRegistry` |
| Master Data Service | 154-156 | `MasterData`, `ReferenceData` |
| API Service | 154-156 | optional UI/API facade |
| Microservice vs search performance tradeoff | 156 | Avoid over-splitting v0.1 |

## Optimizacion

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Optimization module | 179 | `OptimizationEngine` |
| High-dimensional/multiextremal search | 179-181 | `SearchSpace`, `SearchBudget` |
| Objective function as expensive test | 180 | `BacktestObjectiveFunction` |
| Population algorithms | 181-183 | future `PopulationOptimizer` |
| Search breadth vs intensity | 182 | exploration/exploitation policy |
| Multistart | 182-183 | `OptimizationSeedPolicy` |
| Genetic algorithm | 183-190 | future optimizer |
| Mutation operators | 184-186 | optimizer implementation detail |
| Crossover operators | 186-190 | optimizer implementation detail |
| Brute force algorithm | Ch. 7 | `GridSearch` |
| Algorithm registry/form | 221-222 | `OptimizationAlgorithmRegistry` |

## Core y runtime

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Shared core for search and live | 263-264 | `BacktestLiveSharedCore` |
| One strategy-instrument pair per core | 264 | `StrategyRuntimeContext` |
| InitContextCommand | 264-265 | runtime initialization |
| UpdateCandleEvent | 264-266 | `MarketDataEvent` |
| Order status events | 264 | `OrderStatusEvent` |
| Deal/fill event | 264 | `FillEvent` |
| PlaceOrderCommand | 264 | `OrderCommand` |
| Candle record | 265-266 | `Bar` schema |
| Candle intervals enum | 266 | `Timeframe` |
| Warmup/null signal | 267 | `IndicatorWarmupState` |
| Contradictory open/close signals | 267 | `SignalConflictPolicy` |
| Signal model | 268-269 | `Signal`, `ConditionTree` |
| Strategy parameters and candle ranges | 269-270 | `ParameterSet`, `LookbackSpec` |
| Indicator calculators | 278-280 | `IndicatorCalculator` |
| ATR calculator | 279 | `ATRIndicator` |
| Multi-position support | 280 | `PositionCapacityPolicy` |
| ProcessBot Lite | 280-285 | `PositionStateMachine` |
| Semaphore lock for event processing | 283 | `EntityTransitionLock` |
| Stop and alert state | 285 | `ManualInterventionRequired` |
| Active positions queue | 285 | `ActivePositionIndex` |

## Infraestructura

| Concepto | Paginas aprox. | Relevancia TSIS |
|---|---:|---|
| Pragmatic framework choice | 157 | Use Python if it serves TSIS |
| Clean Architecture | Ch. 5 | `PortsAndAdapters` |
| DDD vs anemic model | Ch. 5 | Domain model discussion |
| ORM/Dapper/migrations | Ch. 5 | persistence patterns |
| Hosted service/backworker | Ch. 5 | background processing |
| Docker image | Ch. 9 | reproducible services |
| Kubernetes pod/deployment/service | 306-310 | future deployment, not v0.1 |
| Readiness/liveness probe | 308-309 | `HealthCheck` |
| HorizontalPodAutoscaler | 309 | future scaling |
| Helm | 310-311 | future manifests |

## Uso recomendado en TSIS

| Tarea de agente | Consultar |
|---|---|
| Definir modelo de dominio para estrategias | Ch. 3 |
| Separar strategy idea de strategy instance | Ch. 3 |
| Disenar core historico/live compartido | Ch. 8 |
| Disenar events y commands del runtime | Ch. 8 |
| Crear state machine de posiciones | Ch. 8 |
| Disenar optimization module extensible | Ch. 6-7 |
| Decidir limites de microservicios | Ch. 4 |
| Preparar infraestructura reproducible futura | Ch. 9 |
