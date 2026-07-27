# Algorithmic Trading Systems and Strategies - Viktoria Dolzhenko

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido de capitulos](#mapa-rapido-de-capitulos)
- [Bloque A - Requisitos y modelo de dominio](#bloque-a---requisitos-y-modelo-de-dominio)
- [Bloque B - Arquitectura de servicios](#bloque-b---arquitectura-de-servicios)
- [Bloque C - Optimizacion](#bloque-c---optimizacion)
- [Bloque D - Core module](#bloque-d---core-module)
- [Bloque E - Infraestructura](#bloque-e---infraestructura)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates para agentes](#quality-gates-para-agentes)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Este libro es la fuente mas cercana, dentro de la biblioteca procesada, a un libro de arquitectura de plataforma de trading. No es perfecto para TSIS porque usa .NET, microservicios, Kafka y Kubernetes, pero su valor esta en el razonamiento de ingenieria:

```text
requirements -> domain entities -> subsystems -> services -> queue/FSM -> core shared by search and live -> infrastructure
```

Para el Camino B de TSIS, este libro es util porque explicita muchas piezas que los libros de validacion no cubren:

- `Indicator`;
- `Signal`;
- `Condition`;
- `Strategy`;
- `Theory`;
- `Strategy Search Subsystem`;
- `Sandbox Exchange`;
- `Real Trading Subsystem`;
- `Exchange Gateway`;
- `Master Data`;
- `Core module`;
- eventos de candle, order status y deals;
- state machine para posiciones.

## Rol dentro de TSIS

Encaja en:

```text
DomainModel
BacktestLiveSharedCore
StrategySearch
OptimizationEngine
SandboxExchange
RealTradingAdapter
ExchangeGateway
MessageBus
CoreDecisionEngine
OrderAndPositionStateMachine
```

Es especialmente relevante para responder:

```text
Como aterrizo una arquitectura de sistema de trading en componentes software?
Como hago que el core se use tanto en busqueda historica como en real trading?
Que entidades minimas necesito para signals, indicators, strategies y orders?
```

## Mapa rapido de capitulos

| Capitulo | Uso TSIS |
|---|---|
| 1. Popular approaches | Decide por que crear plataforma propia |
| 2. Intro to developing trading systems | Order execution, risk, testing, optimization, metrics |
| 3. Architecture Part 1 | Requirements, entities, theory/strategy/search/live |
| 4. Architecture Part 2 | Microservices, queue, FSM, core, sandbox, real trading, gateway |
| 5. Stack and libraries | Clean architecture, DDD, ORM, migrations, background workers |
| 6. Optimization algorithms | Population algorithms, genetic algorithms, multistart |
| 7. Implementation of optimization | Brute force/GA library patterns |
| 8. Implementation of Core module | Shared core, candles, signals, indicators, position process |
| 9. Final implementation | Docker, Kubernetes, deployments, services, probes, HPA, Helm |

## Bloque A - Requisitos y modelo de dominio

El capitulo 3 es clave. La autora arranca con requirements elicitation y va descubriendo entidades:

```text
Indicator
Signal
Condition
ConditionGroup
Strategy
Theory
Position
FinancialInstrument
Order
SystemOrder
```

Una distincion muy util para TSIS:

```text
Theory = idea/logica sin parametros finales
Strategy = theory + parametros concretos + sizing/risk
```

Esto encaja con:

```text
StrategyIdea
StrategySpec
ParameterSet
StrategyInstance
BacktestRun
LiveStrategyInstance
```

## Bloque B - Arquitectura de servicios

El libro separa el sistema en subsistemas:

```text
Strategy Search Subsystem
Sandbox Exchange
Real Trading Subsystem
Exchange Gateway
Strategy Manager
Instrument Service
Master Data Service
API Service
```

La idea mas transferible a TSIS:

```text
El core decisional debe ser compartido entre busqueda historica/backtest y real trading.
```

En TSIS no hace falta copiar la microarquitectura completa. Para v0.1 puede ser un monolito modular Python, pero con contratos que no impidan separar despues:

```text
CoreDecisionEngine
HistoricalAdapter
ReplayAdapter
LiveAdapter
ExecutionPort
MarketDataPort
StateStore
```

## Bloque C - Optimizacion

Capitulos 6 y 7 tratan optimizacion como modulo extensible.

Puntos utiles:

- el problema tiene alta dimension, multiples extremos y coste computacional alto;
- no hay algoritmo universal;
- un resultado suboptimo puede ser suficiente;
- los algoritmos poblacionales equilibran exploracion y explotacion;
- los algoritmos estocasticos requieren multistart;
- la libreria de optimizacion debe exponer tipos, operadores y parametros.

Para TSIS:

```text
OptimizationAlgorithmRegistry
SearchSpace
ObjectiveFunction
OptimizationRun
OptimizationSeed
OptimizationBudget
```

No debe confundirse con validacion cientifica. Optimizar no valida edge.

## Bloque D - Core module

El capitulo 8 es el mas importante para TSIS.

Input/output del core:

```text
incoming market data / order status / deals
    -> Core module
    -> place/close order command
```

Eventos/comandos clave:

```text
InitContextCommand
UpdateCandleEvent
CancelExchangeOrderEvent
CloseExchangeOrderEvent
CreateDealEvent
PlaceOrderCommand
```

El core trabaja con una regla de aislamiento:

```text
one core instance = one strategy-instrument pair
```

Esto es muy valioso para TSIS porque evita estados mezclados entre simbolos y estrategias. En v0.1, TSIS podria empezar con:

```text
StrategyRuntimeContext(strategy_id, symbol, run_id)
```

El modelo de signal incluye:

```text
Signal
Condition tree
AND/OR groups
Indicator1
Comparison
Indicator2
SignalData
IndicatorValues
```

Tambien hay una state machine ligera para posiciones que responde a eventos, con bloqueo para evitar dos transiciones simultaneas de una misma entidad. Esto mapea a:

```text
PositionStateMachine
OrderLifecycle
SystemOrder
ActivePositionQueue
```

## Bloque E - Infraestructura

El capitulo 9 cubre Docker, Kubernetes, pods, deployments, services, probes, HorizontalPodAutoscaler y Helm.

Para TSIS local PC:

```text
No copiar Kubernetes desde v0.1.
```

Pero si extraer principios:

- readiness/liveness checks;
- manifest versionado;
- servicios con replicas futuras;
- metricas operativas para escalar;
- despliegues reproducibles;
- logs y health endpoints.

## Blueprint TSIS derivado

```text
TSIS Core
    |
    +-- Domain
    |       -> Indicator
    |       -> Signal
    |       -> ConditionTree
    |       -> StrategySpec
    |       -> StrategyInstance
    |
    +-- Runtime
    |       -> StrategyRuntimeContext
    |       -> CoreDecisionEngine
    |       -> UpdateMarketDataEvent
    |       -> OrderStatusEvent
    |       -> FillEvent
    |
    +-- Search
    |       -> Theory/StrategyGenerator
    |       -> OptimizationRun
    |       -> SandboxExecution
    |
    +-- Live/Replay
            -> MarketDataAdapter
            -> ExecutionAdapter
            -> BrokerGateway
            -> PositionStateMachine
```

## Quality gates para agentes

- No mezclar busqueda historica y live con cores distintos.
- El core no debe depender directamente de broker concreto.
- Toda estrategia debe tener contexto aislado.
- Eventos de datos y eventos de ejecucion deben entrar por contratos separados.
- Si dos senales contradictorias se activan, debe existir politica explicita.
- Indicadores deben declarar lookback y estado de calentamiento.
- Position/order processing necesita state machine, no ifs dispersos.
- El sistema debe manejar errores de orden, no solo fills felices.

## Limitaciones

- Arquitectura sobre .NET y microservicios; TSIS v0.1 probablemente debe ser Python modular.
- No es una referencia cientifica de overfitting.
- No profundiza en small caps, halts, borrow, partial fills o Polygon/DAS.
- El modelo inicial usa candles; quotes/order book quedan como expansion.
- No sustituye a NautilusTrader/LEAN como arquitectura profesional de trading.
