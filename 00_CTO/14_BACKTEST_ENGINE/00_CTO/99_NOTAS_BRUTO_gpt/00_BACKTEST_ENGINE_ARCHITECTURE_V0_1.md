# TSIS_SMALLCAPS_BACKTEST_ENGINE_ARCHITECTURE_V0_1

Status: DRAFT_OPERATIVE_ARCHITECTURE  
Date: 2026-07-28  
Scope: Camino B - backtester propio en Python para small caps US.  

Este documento no es un libro, no es una guia institucional completa y no es un modelo de dominio total. Es el croquis operativo para empezar a construir el primer backtester serio de TSIS sin perder la arquitectura.

## 0. Decision central

La primera entrega no debe ser una enciclopedia ni una app live. Debe ser:

```text
BACKTEST_VERTICAL_SLICE_V0_1
```

Objetivo de aceptacion:

```text
Una estrategia intradia simple debe poder ejecutarse sobre datos smallcap locales,
con universo y dataset declarados, orden temporal determinista, decisiones,
order intents, fills simulados, posiciones, accounting, costes, equity,
metricas basicas y manifest reproducible.
```

La teoria solo entra cuando sostiene una decision de construccion o un gate de validacion.

## 1. Croquis general

```text
                          TSIS DATA FOUNDATION
              contratos, schemas, universo LT1B, price views, manifests
                                      |
                                      v
+------------------------ RUN PREFLIGHT / DATA RESOLUTION ------------------------+
| dataset_id, price_view, universe_id, date range, sessions, timezone, manifests  |
| FAIL CLOSED si falta contrato, manifest, schema o autorizacion de consumo        |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+--------------------------- HISTORICAL MARKET REPLAY ----------------------------+
| HistoricalParquetDataSource -> Clock -> EventQueue -> MarketDataEvent           |
| orden temporal, sesiones, missing bars, halts, same timestamp policy            |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+----------------------------- ONLINE OBSERVABLE STATE ---------------------------+
| MarketStateSnapshot, EventStateSnapshot, rolling state, HOD/LOD/VWAP/volume     |
| solo informacion disponible en decision_timestamp                               |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+------------------------------- DECISION CORE -----------------------------------+
| StrategySpec -> Strategy -> DecisionPolicy -> DecisionRecord -> OrderIntent      |
| la estrategia no crea fills, no toca portfolio y no consulta datos futuros       |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+-------------------------- PORTFOLIO / SIZING / RISK ----------------------------+
| PositionSizingPolicy -> PortfolioTarget -> PreTradeRiskGate -> accepted/reject  |
| limites de riesgo, cash, exposicion, liquidez, shortability futura              |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+----------------------------- OMS / EXECUTION SIM -------------------------------+
| Order -> OrderEvent -> FillModel -> CostModel -> FillEvent                      |
| bid/ask, spread, slippage, volume cap, partial fills, halts, latency policy     |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+------------------------------ ACCOUNTING / LEDGER ------------------------------+
| fills -> cash -> position -> realized/unrealized pnl -> equity -> trades        |
| event log canonico + proyecciones parquet                                       |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+--------------------------- DIAGNOSTICS / VALIDATION ----------------------------+
| metrics, trade list, drawdown, cost stress, manual cases, no-leakage tests      |
| despues: WFA, sensitivity, robustness, PBO/DSR solo cuando haya muchas pruebas  |
+---------------------------------------------------------------------------------+
```

## 2. Dos carriles, una autoridad

```text
VECTOR RESEARCH RAIL                         EVENT-DRIVEN RAIL
rapido, exploratorio                         lento, autoritativo
Polars/DuckDB                                Python event loop
features y filtros                           decisiones, ordenes, fills
no demuestra ejecutabilidad                  resultado oficial del backtest
produce candidatos                           produce evidencia de simulacion
```

Regla: una equity curve vectorizada puede sugerir una idea; no aprueba una estrategia smallcap. El resultado serio sale del rail event-driven.

## 3. Flujo de eventos v0.1

```text
SessionOpen
MarketDataEvent(bar_1m)
StateUpdated
StrategyDecisionRequested
DecisionRecorded
OrderIntentCreated
RiskChecked
OrderCreated
OrderAccepted | OrderRejected
FillCreated | PartialFillCreated | NoFill
PositionUpdated
AccountUpdated
StopOrExitEvaluated
SessionClose
RunClosed
```

Separaciones obligatorias:

```text
Market condition != Decision
Decision != OrderIntent
OrderIntent != Order
Order != Fill
Fill != Trade
Trade != MarketTrade
Position != PnL report
```

## 4. Componentes del motor

| Componente | Responsabilidad | Fuente principal |
|---|---|---|
| `RunPreflight` | Resolver contratos, dataset, universo, manifests y permisos de consumo | TSIS Data Foundation, Sersan KR-001 |
| `UniverseResolver` | Entregar membresia point-in-time, no lista actual retrospectiva | TSIS LT1B certification, Chan, SAT |
| `MarketDataSource` | Stream historico intercambiable con replay/live futuro | QuantStart/SAT, Hilpisch, Nautilus/LEAN |
| `Clock` / `EventQueue` | Orden temporal, sesiones, timers, desempates | SAT, Hilpisch, Machine Trading |
| `OnlineStateStore` | Estado observable legal por timestamp | TSIS system map, Hilpisch online, Sersan data/sessions |
| `Strategy` / `DecisionPolicy` | Convertir estado legal en decision auditable | Pardo, Chan, Sersan process |
| `PositionSizingPolicy` | Convertir decision en target o cantidad | Pardo, Carver, Sersan money management |
| `RiskGate` | Rechazar/reducir antes de enviar orden | SAT risk, Pardo, Sersan operativa |
| `OMS` | Ciclo de vida de ordenes y eventos de orden | SAT, Harris, Johnson, Nautilus/LEAN |
| `ExecutionSimulator` | Simular fills bajo supuestos declarados | Harris, Johnson, Machine Trading, Sersan KR-014 |
| `CostModel` | Comisiones, fees, locate/borrow futuro, slippage separado | Harris, Johnson, Sersan KR-033 |
| `AccountingLedger` | Cash, posiciones, PnL y equity desde fills | SAT, Chan, Strimpel Cookbook |
| `LedgerWriter` | Persistir eventos y proyecciones reproducibles | DDIA/streaming, Architecture Patterns with Python |
| `MetricsEngine` | Equity, drawdown, trades, costes, MAE/MFE basico | SAT, Pardo, Jaekle, Sersan reports |
| `ValidationRunner` | Tests de motor y validacion experimental gradual | Pardo, Masters, Lopez de Prado despues |

## 5. Adaptadores y puertos

El dominio no debe depender de Polygon, DAS, DuckDB, Polars ni una GUI.

```text
Domain Core
  MarketDataEvent, StateSnapshot, Decision, OrderIntent, Order, Fill, Position

Application Services
  RunPreflight, BacktestRunner, ReplayRunner, MetricsRunner, ValidationRunner

Ports
  MarketDataSource, UniverseSource, HaltSource, QuoteSource, LedgerWriter,
  ManifestWriter, ConfigRepository, ClockProvider

Adapters v0.1
  ParquetMarketDataSource, LT1BUniverseSource, LocalHaltSource,
  ParquetLedgerWriter, JsonManifestWriter

Adapters futuros
  ReplayDataAdapter, DASBrokerAdapter, LiveMarketDataAdapter, OperatorGUI
```

Esta separacion sale de `Architecture Patterns with Python`: modelo de dominio, servicios de aplicacion, puertos/adaptadores, repositorios y eventos. En TSIS sirve para que el backtest historico y el replay/live futuro compartan semantica sin compartir procedencia.

## 6. Particularidades small caps que entran desde el primer diseno

No todas entran en v0.1 con modelo completo, pero ninguna puede quedar invisible.

```text
1. universo point-in-time y activos muertos
2. cambios de ticker, listings, delistings, suspensiones
3. splits/reverse splits y separacion raw vs adjusted vs feature price view
4. premarket como parte de la historia, no decoracion
5. halts y no-trade windows
6. missing minutes: no trade, missing vendor, halt, fuera de sesion o corrupcion
7. spread y precio ejecutable: bid/ask cuando exista, fallback conservador si no
8. volumen disponible y participation cap
9. partial fills y unfilled remainder policy
10. shorts: locates, borrow, HTB, forced buy-in, pero aplazado si v0.1 es long-only
11. costes: commission, ECN/routing, SEC/TAF, slippage, locate/borrow futuro
12. capacidad: resultado valido para un tamano, no para capital infinito
```

La leccion de Sersan-smallcaps es directa: en real la senal es solo una pieza. Hay que simular datos, horarios, ejecucion, ordenes, riesgo, registros y revision.

## 7. Alcance exacto v0.1

V0.1 debe ser deliberadamente estrecho:

```text
- un universo gobernado: lt1b_universe_v0_1 o subuniverso derivado con manifest
- una granularidad base: 1m intradia
- un solo modo de sesion declarado: premarket + regular, o regular-only
- una estrategia smoke no orientada a edge para validar el motor
- una estrategia smallcap simple despues: in-play/opening-range long-only candidata
- ordenes market o stop-market simples; limit orders aplazadas o muy restringidas
- fill model conservador con spread/slippage/participation cap basico
- sin shorts en el primer slice, salvo stub de `ShortAvailabilityPolicy`
- sin portfolio multi-sistema; un portfolio simple de una cuenta
- outputs parquet + manifest + reporte markdown
```

No objetivos v0.1:

```text
PBO, DSR, Reality Check, SPA, ML, RL, L2, routing avanzado, GUI, DAS live,
portfolio optimizer, execution algos TWAP/VWAP/POV, borrow historico completo.
```

## 8. Estrategias iniciales recomendadas

Primero se valida el motor, no el edge.

```text
SMOKE_INTRADAY_ROUNDTRIP_V0_1
  entra en un timestamp fijo si hay barra valida y sale en otro timestamp fijo.
  objetivo: verificar clock, fills, accounting, costes, ledgers y reproducibilidad.

INPLAY_OPENING_RANGE_LONG_V0_1
  usa gap/premarket/volumen/opening range/HOD de forma causal.
  objetivo: primer caso smallcap realista, todavia no estrategia aprobada.
```

El primer resultado bueno no se interpreta como edge. Se interpreta como evidencia de que el circuito tecnico funciona.

## 9. Outputs fisicos minimos

Cada run debe producir una carpeta inmutable:

```text
run_manifest.json
data_manifest.json
universe_manifest.json
strategy_spec.json
cost_model_spec.json
fill_model_spec.json
session_policy.json
limitations.md

universe_membership.parquet
market_events.parquet
state_snapshots.parquet
decisions.parquet
order_intents.parquet
orders.parquet
order_events.parquet
fills.parquet
positions.parquet
account_snapshots.parquet
closed_trades.parquet
equity_curve.parquet
metrics.json
exceptions.parquet
```

Propuesta de raiz de trabajo:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/experiments/EXP_0001_SMOKE_INTRADAY_ROUNDTRIP/
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/outputs/<run_id>/
```

Si el modulo oficial sigue siendo otro path, el `RunPreflight` debe declarar el root real en el manifest. No se debe inferir significado desde la carpeta.

## 10. Gates de aceptacion antes de escalar

```text
G0_DOCS_READ
  el run declara que contratos Data Foundation, Sersan y bibliografia minima aplican.

G1_DATA_PREFLIGHT_PASS
  dataset_id, price_view, schema, manifest, universe_id y date range resueltos.

G2_TEMPORAL_LEGALITY_PASS
  ninguna decision usa una barra antes de su cierre ni informacion posterior.

G3_DETERMINISM_PASS
  misma config + mismos datos + misma seed producen mismos ledgers y hashes.

G4_MANUAL_ACCOUNTING_PASS
  casos pequenos calculados a mano coinciden con cash, position, fees y PnL.

G5_EVENT_CHAIN_PASS
  cada fill traza hasta decision, order_intent, order y estado observable.

G6_EXECUTION_ASSUMPTION_DECLARED
  fill model, spread/slippage, volume cap, halts y same-bar ambiguity declarados.

G7_OUTPUT_COMPLETENESS_PASS
  todos los ledgers minimos existen y son reconstruibles desde manifest.

G8_COST_STRESS_PASS
  el reporte muestra PnL bajo base/moderate/severe costs, aunque sea simple.

G9_LIMITATIONS_EXPLICIT
  el run dice que no cubre todavia: shorts/locates, borrow historico, L2, etc.
```

## 11. Orden de construccion

```text
1. Crear carpeta/microproyecto del backtest engine y contratos v0.1.
2. Implementar `RunPreflight` contra Data Foundation, sin leer datos aun.
3. Crear `SMOKE_INTRADAY_ROUNDTRIP_V0_1` con dataset minusculo fixture.
4. Implementar dominio basico: events, decisions, order intents, orders, fills.
5. Implementar accounting con casos manuales.
6. Implementar ledgers parquet/json.
7. Conectar historical 1m feed para pocos ticker-days.
8. Anadir fill model conservador: next executable bar, slippage, volume cap.
9. Ejecutar reporte minimo: trades, equity, drawdown, costs, limitations.
10. Repetir con `INPLAY_OPENING_RANGE_LONG_V0_1` en muestra pequena.
11. Solo despues escalar a mas fechas/tickers y empezar optimizacion controlada.
```

## 12. Donde encaja cada fuente

```text
Sersan Sistemas
  Proceso practico: datos/sesiones -> reglas -> backtest -> diagnostico ->
  optimizacion -> robustez -> sizing -> portfolio -> incubacion. Tambien aporta
  la advertencia real smallcaps: liquidez, premarket, halts, spread, locates,
  slippage, datos sucios y ejecucion real.

Successful Algorithmic Trading / QuantStart
  Esqueleto pedagogico event-driven: MarketEvent, SignalEvent, OrderEvent,
  FillEvent, DataHandler, Strategy, Portfolio, ExecutionHandler.

Hilpisch
  Python, datos, prototipos vectorizados, clases event-based, streaming y
  monitoring. Util para cruzar de notebook a motor.

Pardo
  Proceso profesional de especificacion, preliminary testing, optimizacion,
  WFA, evaluacion y monitoring. No implementa el motor, gobierna el experimento.

Chan / Machine Trading
  Backtest y live deben compartir nucleo decisional. Small caps exigen costes,
  capacidad, short availability, precios ejecutables y reconciliacion.

Harris / Hasbrouck / Johnson
  Realismo de mercado: ordenes, spread, liquidez, fills, impact, TCA, routing.
  En v0.1 se incorporan como supuestos conservadores y contratos ampliables.

Architecture Patterns with Python / Clean Architecture
  Como construir el motor propio sin mezclar dominio, adapters, GUI, storage y
  servicios de aplicacion.

Masters / Lopez de Prado
  Validacion avanzada, sesgos de seleccion, OOS, overfitting, PBO/DSR. Entran
  despues de que el motor produzca series de retornos fiables.
```

## 13. Regla de gobierno para no desviarnos

Cada nueva idea entra solo si cambia una de estas cosas:

```text
- contrato de dato
- contrato de evento
- decision policy
- order/fill/accounting
- output ledger
- gate de aceptacion
- limitacion declarada
```

Si no cambia nada de eso, se guarda como referencia y no bloquea la construccion.

## 14. Siguiente artefacto concreto

No crear otro blueprint largo. Crear:

```text
BACKTEST_VERTICAL_SLICE_V0_1_IMPLEMENTATION_PLAN.md
```

Debe contener solamente:

```text
- estrategia smoke exacta
- fixture de datos minimo
- contratos de inputs/outputs
- clases Python minimas
- tests de aceptacion
- comandos de ejecucion
- ruta de outputs
```

Ese plan debe ser lo bastante corto para que un agente empiece a programar en el siguiente turno.
