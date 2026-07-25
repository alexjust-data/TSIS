# Algorithmic Trading and DMA - Barry Johnson

Resumen operativo para agentes TSIS.

## Menu

- [Resumen ejecutivo](#resumen-ejecutivo)
- [Rol dentro de TSIS](#rol-dentro-de-tsis)
- [Mapa rapido](#mapa-rapido)
- [Part I - Trading y mercados](#part-i---trading-y-mercados)
- [Part II - Algoritmos y TCA](#part-ii---algoritmos-y-tca)
- [Part III - Implementacion](#part-iii---implementacion)
- [Part IV - Estrategias avanzadas](#part-iv---estrategias-avanzadas)
- [Blueprint TSIS derivado](#blueprint-tsis-derivado)
- [Quality gates](#quality-gates)
- [Limitaciones](#limitaciones)

## Resumen ejecutivo

Johnson es una de las mejores fuentes practicas para ejecucion profesional, DMA, tipos de orden, transaction cost analysis, seleccion de algoritmos, order placement, routing e infraestructura de trading electronico.

Para TSIS small caps es mas importante que muchos libros de backtesting, porque explica que ocurre despues de que una estrategia decide comprar o vender.

Su foco:

```text
order -> venue/routing -> algorithm -> tactics -> fills -> transaction costs -> post-trade analysis
```

El archivo era escaneado; se proceso con OCR completo.

## Rol dentro de TSIS

Encaja en:

```text
OrderModel
OrderInstructions
ExecutionAlgorithm
ExecutionTactics
VenueModel
RoutingModel
TransactionCostAnalysis
PreTradeCostEstimate
PostTradeCostReport
OrderManagementInfrastructure
```

Es referencia primaria para `ExecutionSimulator` y `BrokerAdapter` desde la perspectiva de ejecucion.

## Mapa rapido

| Parte | Contenido | Uso TSIS |
|---|---|---|
| Part I | mercados, microestructura, asset classes, electronic trading | `MarketModel`, `VenueModel` |
| Part II | orders, TWAP, VWAP, POV, IS, AS, TCA, optimal strategy | `ExecutionAlgorithmLibrary`, `TCAModel` |
| Part III | order placement, hidden liquidity, execution tactics, forecasting conditions, infrastructure | `OrderPlacementPolicy`, `RoutingModel`, `ExecutionEngine` |
| Part IV | portfolios, multi-asset, news, data mining, AI | future `PortfolioExecution`, `NewsAwareExecution` |

## Part I - Trading y mercados

Johnson introduce DMA y algorithmic trading como mecanismos de ejecucion, no como estrategias alfa. Esto es clave para TSIS:

```text
alpha strategy != execution algorithm
```

La estrategia decide intencion; el algoritmo decide como ejecutar. El motor debe reflejar esa separacion.

## Part II - Algoritmos y TCA

Capitulos clave:

- orders;
- algorithm overview;
- transaction costs;
- optimal trading strategies.

Familias:

```text
impact-driven: TWAP, VWAP, POV, minimal impact
cost-driven: implementation shortfall, adaptive shortfall, market close
opportunistic: price inline, liquidity-driven, pair trading
```

Para TSIS v0.1, no hace falta implementar todos. Pero si debe existir el contrato:

```text
ExecutionAlgorithm
    inputs: order, market_state, constraints, benchmark
    outputs: child_orders, schedule, routing, fill_events
```

TCA debe existir en dos momentos:

```text
pre_trade_estimate
post_trade_measurement
```

## Part III - Implementacion

Esta parte es la mas arquitectonica:

- order placement;
- price formation;
- order matching;
- signalling risk;
- venue choice;
- order choice;
- aggressiveness;
- hidden liquidity;
- execution probability;
- execution tactics;
- infrastructure requirements;
- order management;
- routing;
- testing.

Para TSIS:

```text
OrderManager
    -> Router
    -> ExecutionAlgorithm
    -> Tactic
    -> Venue/BrokerAdapter
```

La decision de agresividad debe depender de:

- urgencia;
- liquidez;
- spread;
- volatilidad;
- riesgo de no completar;
- riesgo de senalizar intencion;
- coste esperado.

## Part IV - Estrategias avanzadas

Johnson extiende ejecucion a portfolios, multi-asset, noticias, data mining e IA. Para TSIS esto queda como futuro, pero aporta conceptos utiles:

- ejecutar una cartera no equivale a ejecutar ordenes independientes;
- news handling puede cambiar tacticas de ejecucion;
- data mining debe tratarse con cuidado y backtesting especifico;
- AI puede generar reglas o parametros, pero aumenta riesgo operacional y de validacion.

## Blueprint TSIS derivado

```text
ParentOrder
    -> ExecutionObjective
    -> Benchmark
    -> PreTradeTCA
    -> ExecutionAlgorithm
    -> ChildOrderSchedule
    -> OrderPlacementPolicy
    -> Router/VenueModel
    -> FillEvents
    -> PostTradeTCA
```

Campos recomendados:

```text
parent_order_id
child_order_id
execution_algo_id
benchmark_type
arrival_price
decision_price
limit_price
venue
routing_instruction
urgency
participation_rate
expected_cost_bps
realized_cost_bps
implementation_shortfall_bps
```

## Quality gates

- No mezclar alpha signal con execution algorithm.
- Parent orders y child orders deben estar separados.
- Registrar benchmark de ejecucion.
- Registrar arrival price y decision price.
- Separar market impact y timing risk.
- Declarar venue/routing.
- Modelar ordenes market, limit, hidden/conditional si se usan.
- Para small caps, incluir spread, liquidez, halts y partial fills antes de afirmar ejecutabilidad.

## Limitaciones

No es un libro de Python ni de backtesting cientifico. Es fuente de ejecucion y microestructura aplicada. Debe cruzarse con Hasbrouck/Harris para teoria de microestructura y con Nautilus/LEAN para arquitectura de motor.

