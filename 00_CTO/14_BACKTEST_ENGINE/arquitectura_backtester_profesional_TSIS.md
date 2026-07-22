# Arquitectura completa para aterrizar un backtester profesional en TSIS

Sí. Y después de revisar lo que existe, mi conclusión es bastante clara:

> **No hay un único libro que documente de principio a fin cómo construir un backtester profesional, realista, reproducible y reutilizable posteriormente en tiempo real.**

La fuente más cercana a ese “esqueleto completo” no es un libro: es estudiar la arquitectura y el código de **NautilusTrader** y **LEAN**, y utilizar libros y papers para endurecer cada subsistema.

Para TSIS no te recomendaría copiar íntegramente ninguno. Los usaría como **arquitecturas de referencia** para redactar primero el contrato del backtester y construir después una versión propia, limitada y verificable.

# Mi recomendación principal

## Referencia arquitectónica número 1: NautilusTrader

Actualmente es probablemente la referencia pública más alineada con lo que buscas:

- arquitectura orientada a eventos;
- simulación histórica determinista;
- estrategia compartida entre backtest y directo;
- datos, comandos y eventos;
- message bus;
- órdenes y ejecución;
- portfolio;
- contabilidad;
- risk engine;
- informes;
- market replay;
- timestamps de alta resolución;
- Python para estrategia y control, con núcleo de alto rendimiento en Rust.

Su arquitectura separa expresamente los entornos:

```text
Backtest
Sandbox
Live
```

y ejecuta los mismos actores, estrategias y algoritmos de ejecución en backtest y live.

Su backtest se construye alrededor de:

```text
historical data stream
        ↓
BacktestEngine
        ↓
MessageBus
        ↓
Data Engine
Strategy
Risk Engine
Execution Engine
Portfolio
Cache
Accounting
Reports
```

La documentación describe que el `BacktestEngine` procesa un flujo histórico utilizando los mismos componentes conceptuales del sistema: cache, message bus, portfolio, estrategias, algoritmos de ejecución y módulos definidos por el usuario.

### Por qué es especialmente relevante para TSIS

Porque TSIS necesita precisamente esto:

```text
mismo núcleo decisional
        +
distinto adaptador de datos y ejecución
```

Es decir:

```text
HistoricalDataAdapter ─┐
ReplayDataAdapter ─────┼→ mismo Strategy/Decision Core
LiveDASAdapter ────────┘
```

NautilusTrader demuestra que esta arquitectura no es una fantasía: es una manera real de diseñar motores de trading. Además, su documentación cubre por separado ejecución, órdenes, posiciones, accounting, portfolio y reporting.

**No significa que debas utilizar NautilusTrader como producto definitivo.** Significa que deberías estudiar su modelo de dominio antes de inventar el tuyo.

---

# Referencia arquitectónica número 2: LEAN

LEAN es el motor open source de QuantConnect. Está diseñado para:

```text
research
backtest
optimization
live trading
```

Su núcleo está escrito en C#, pero permite escribir algoritmos en Python.

LEAN es útil para estudiar cómo separar:

```text
Universe Selection
Alpha / Signal Generation
Portfolio Construction
Risk Management
Execution
```

Su `Algorithm Framework` formaliza precisamente esas responsabilidades para facilitar diseños reutilizables.

El flujo conceptual es:

```text
Universo
    ↓
Alpha Model
    ↓
Insights
    ↓
Portfolio Construction
    ↓
Risk Management
    ↓
Execution Model
    ↓
Orders
```

El `Alpha Model`, por ejemplo, genera objetos de predicción con dirección, magnitud, confianza y peso sugerido, en lugar de mezclar directamente predicción, portfolio y ejecución.

### Qué copiaría conceptualmente de LEAN

- separación entre universo y estrategia;
- separación señal/portfolio;
- risk model independiente;
- execution model independiente;
- brokerage adapters;
- order tickets y order events;
- posibilidad de usar el mismo algoritmo en backtest y live;
- gestión de diferencias entre simulación y directo.

### Qué no copiaría directamente

- toda su complejidad;
- su dominio generalista multi-activo;
- la dependencia estructural de C#;
- abstracciones que no necesita tu primera estrategia;
- supuestos de resolución o ejecución que no coincidan con small caps.

---

# Referencia pedagógica para implementarlo: QuantStart

La serie **Event-Driven Backtesting with Python** explica de forma progresiva cómo construir un motor orientado a eventos.

Su valor es que aterriza el patrón en clases comprensibles:

```text
Event
DataHandler
Strategy
Portfolio
ExecutionHandler
Event Queue
```

Un motor event-driven permite alimentar los datos históricamente como si llegaran en directo y reutilizar buena parte de los componentes cambiando el data handler y el execution handler.

La secuencia clásica es:

```text
MarketEvent
    ↓
Strategy
    ↓
SignalEvent
    ↓
Portfolio
    ↓
OrderEvent
    ↓
ExecutionHandler
    ↓
FillEvent
    ↓
Portfolio
```

Esto es probablemente lo mejor para **entender y programar tú mismo la primera versión**.

Sin embargo, la serie no debe tomarse como especificación institucional final. Es una arquitectura educativa que deberás endurecer con:

- timestamps explícitos;
- múltiples tipos de datos;
- órdenes con ciclo de vida;
- fills parciales;
- latencia;
- estados reproducibles;
- corporate actions;
- almacenamiento y manifests.

---

# Libros que sí sirven para aterrizar la implementación

## 1. *Python for Algorithmic Trading* — Yves Hilpisch

Es el primer libro técnico que usaría junto al de Isaac Trullas.

Cubre:

- infraestructura Python;
- datos financieros;
- backtesting vectorizado;
- construcción de clases para backtesting event-based;
- datos en tiempo real y sockets;
- interacción con plataformas;
- despliegue.

Su índice incluye expresamente clases para backtesting basado en eventos y trabajo con datos en tiempo real.

### Qué extraería para TSIS

```text
entorno reproducible
datos históricos
prototipos vectorizados
clases de backtesting
conexión a streaming
deployment
```

### Qué no esperaría del libro

- un OMS profesional completo;
- una simulación exhaustiva de small caps;
- delistings y point-in-time universe;
- modelado profundo de fills;
- gobernanza científica completa;
- integración con Market State/Event State.

Por tanto:

> Hilpisch enseña cómo cruzar el puente de Python; Nautilus y LEAN enseñan cómo debe organizarse la ciudad al otro lado.

---

## 2. *Python for Algorithmic Trading Cookbook*

Lo usaría como recetario, no como arquitectura central.

Incluye capítulos diferenciados para:

- backtesting vectorizado;
- optimización walk-forward;
- backtesting event-based;
- herramientas como VectorBT y Zipline Reloaded.

Sirve para comparar implementaciones, pero no debes ensamblar TSIS copiando recetas de frameworks distintos sin un modelo de dominio único.

---

## 3. *Trading and Exchanges* — Larry Harris

Este libro define cómo debe comportarse el mundo que simulas:

```text
órdenes
liquidez
spread
market orders
limit orders
participantes
matching
ejecución
selección adversa
```

No te construye las clases Python, pero evita diseñar un `ExecutionSimulator` económicamente absurdo.

Para small caps debe leerse durante la construcción de:

```text
Order Model
Fill Model
Slippage Model
Liquidity Model
```

---

## 4. *Empirical Market Microstructure* — Joel Hasbrouck

Es más académico y cuantitativo.

Útil cuando quieras modelar correctamente:

- trades y quotes;
- bid-ask spread;
- price impact;
- order flow;
- relación entre transacciones y formación del precio.

No es necesario para la v0.1 basada en barras. Sí lo será para una simulación basada en quotes, trades o L2.

---

# Un paper reciente especialmente relevante

Un trabajo de 2026 sobre **implementation risk in portfolio backtesting** estudia cómo diferentes motores pueden obtener resultados distintos aun implementando la misma lógica, debido especialmente al tratamiento de costes y detalles de implementación.

Esto refuerza una decisión fundamental para TSIS:

> Nunca debes confiar en un resultado solamente porque una librería lo produjo. Debes crear estrategias benchmark y comparar el motor de TSIS con una o dos implementaciones independientes.

Por ejemplo:

```text
estrategia benchmark
        ↓
TSIS
LEAN
NautilusTrader o motor de referencia
        ↓
comparación de:
señales
órdenes
fills
posición
P&L
costes
```

---

# La arquitectura completa que extraería de estas fuentes

Esta sería mi propuesta inicial para TSIS.

```text
┌────────────────────────────────────────────────────┐
│ 1. RESEARCH AND EXPERIMENT CONTROL                 │
│ Hypothesis / Strategy Spec / Run Config / Manifest │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 2. DATA FOUNDATION                                │
│ Raw → Canonical → Validated → Point-in-time Data  │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 3. SIMULATION INPUT                               │
│ HistoricalFeed / ReplayFeed / LiveFeed            │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 4. CLOCK + EVENT LOOP                             │
│ Ordering / Scheduling / Session / Timers          │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 5. ONLINE STATE                                   │
│ Market State / Event State / Rolling State        │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 6. EVENT DETECTION                                │
│ Market phenomena and setup lifecycle              │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 7. STRATEGY / DECISION POLICY                     │
│ Observe → Decide → Signal                         │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 8. PORTFOLIO CONSTRUCTION                         │
│ Target / Sizing / Exposure                        │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 9. PRE-TRADE RISK                                 │
│ Limits / Buying power / Max loss / Reject         │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 10. ORDER MANAGEMENT                              │
│ Create / Submit / Amend / Cancel / State machine  │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 11. EXECUTION                                     │
│ SimulatedVenue or BrokerAdapter                   │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 12. FILLS + ACCOUNTING                            │
│ Fill / Position / Cash / P&L / Fees               │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 13. POST-TRADE RISK                               │
│ Stops / Exposure / Drawdown / Kill switches       │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 14. LEDGERS AND AUDIT                             │
│ Decisions / Signals / Orders / Fills / States     │
└────────────────────────┬───────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────┐
│ 15. PERFORMANCE + VALIDATION                      │
│ Metrics / Walk-forward / Robustness / Reports     │
└────────────────────────────────────────────────────┘
```

# Qué hace exactamente cada bloque

## 1. Research and Experiment Control

Antes de ejecutar:

```text
strategy_id
strategy_version
hypothesis_id
dataset_id
universe_id
start/end
parameters
cost_model_version
fill_model_version
random_seed
code_commit
```

Salida:

```text
run_manifest.json
```

Esta capa evita que meses después no sepas qué configuración produjo un resultado.

---

## 2. Data Foundation

Responsabilidades:

```text
raw preservation
canonical schemas
data validation
corporate actions
symbol identity
session calendars
point-in-time universe
timestamps
data lineage
```

Para TSIS ya existe una gran parte de esta capa.

---

## 3. Simulation Input

Una interfaz única:

```python
class MarketDataSource:
    def stream(self):
        ...
```

Implementaciones:

```text
HistoricalParquetDataSource
HistoricalReplayDataSource
DASLiveDataSource
```

La estrategia no debe saber cuál está activo.

---

## 4. Clock y Event Loop

Debe garantizar:

- orden temporal;
- desempate determinista entre eventos con el mismo timestamp;
- apertura y cierre de sesión;
- timers;
- no entregar información futura;
- reproducibilidad.

Ejemplo de prioridad:

```text
1. corporate action
2. session event
3. quote
4. trade
5. bar close
6. timer
7. fill notification
```

La prioridad exacta deberá documentarse, porque puede cambiar los resultados.

---

## 5. Online State

Mantiene solamente lo conocido en ese instante:

```text
HOD
LOD
VWAP
rolling volume
spread
position relative to VWAP
opening range
current event lifecycle
```

Desde aquí se materializan:

```text
MarketStateSnapshot
EventStateSnapshot
```

No se consultan tablas históricas futuras durante una decisión.

---

## 6. Event Detection

Responsabilidad:

```text
¿Qué fenómeno observable está ocurriendo?
```

No compra ni vende.

Ejemplos:

```text
OpeningDriveStarted
FirstPullbackDetected
VWAPReclaimDetected
HODBreakDetected
TradingHaltStarted
```

---

## 7. Strategy o Decision Policy

Responsabilidad exclusiva:

```text
Dado el estado observable,
¿qué intención operativa existe?
```

Salida:

```text
ENTER_LONG
ENTER_SHORT
EXIT
REDUCE
HOLD
NO_ACTION
```

Debe guardar:

```text
decision_reason
state_snapshot_id
strategy_rule_id
```

---

## 8. Portfolio Construction

Convierte intención en objetivo:

```text
quiero entrar long
```

a:

```text
quiero tener 500 acciones
```

La estrategia no debería decidir directamente la orden final, porque entonces mezclas edge, sizing y ejecución.

---

## 9. Pre-trade Risk

Valida:

```text
max risk per trade
max daily loss
max symbol exposure
buying power
short availability
position limits
price collars
data staleness
```

Puede rechazar la intención antes de crear o enviar la orden.

---

## 10. Order Management System

El objeto `Order` necesita un ciclo de vida:

```text
CREATED
SUBMITTED
ACCEPTED
PARTIALLY_FILLED
FILLED
CANCEL_PENDING
CANCELED
REJECTED
EXPIRED
```

Y eventos separados:

```text
OrderSubmitted
OrderAccepted
OrderPartiallyFilled
OrderFilled
OrderCanceled
OrderRejected
```

Esto se parece mucho más al mercado real que asumir:

```text
signal → posición instantánea
```

---

## 11. Execution

Dos implementaciones:

```text
SimulatedExecutionVenue
DASBrokerAdapter
```

Ambas deben recibir órdenes del mismo OMS y devolver eventos de ejecución con el mismo contrato.

El simulador empieza simple:

```text
market order fills at next ask/bid
configurable slippage
fixed or variable commission
```

Después evoluciona:

```text
latency
partial fills
liquidity consumption
participation caps
halts
queue approximations
borrow restrictions
```

NautilusTrader documenta explícitamente que algunos modelos todavía simplifican la posición en cola y que los modelos de fill pueden evolucionar hacia slippage variable y dinámicas más complejas. Eso es una buena lección: incluso los motores profesionales tienen supuestos y limitaciones que deben declararse.

---

## 12. Accounting

Cada fill modifica:

```text
cash
position quantity
average price
realized P&L
unrealized P&L
fees
margin
```

No se debería calcular el P&L retrospectivamente únicamente desde una tabla final de trades. Debe surgir del ledger de fills y posiciones.

---

## 13. Post-trade Risk

Una vez dentro:

```text
stop rules
daily drawdown
portfolio exposure
position concentration
stale market data
broker disconnect
kill switch
```

---

## 14. Ledgers

Salidas mínimas:

```text
market_events.parquet
event_instances.parquet
state_snapshots.parquet
decisions.parquet
signals.parquet
orders.parquet
order_events.parquet
fills.parquet
positions.parquet
account_snapshots.parquet
trades.parquet
equity_curve.parquet
run_manifest.json
```

Estas tablas son tanto evidencia económica como evidencia de auditoría.

---

## 15. Performance y validación

Primera capa:

```text
net P&L
expectancy
win rate
average win/loss
drawdown
turnover
exposure
MAE
MFE
holding time
costs
slippage
```

Segunda capa:

```text
por año
por régimen
por ticker
por gap
por float
por hora
por tipo de evento
por Market State
por Event State
```

Tercera capa, cuando haya muchas pruebas:

```text
walk-forward
parameter sensitivity
bootstrap
DSR
PBO
multiple-testing controls
```

# Qué debes estudiar exactamente, en orden

## Bloque 1 — Comprender el patrón event-driven

1. Serie QuantStart: *Event-Driven Backtesting with Python*.
2. Arquitectura y conceptos de NautilusTrader.
3. Architecture/Algorithm Framework de LEAN.

Objetivo:

```text
comprender el flujo completo de eventos
```

## Bloque 2 — Programar el primer vertical

4. Isaac Trullas.
5. Hilpisch, especialmente:
   - infraestructura;
   - datos;
   - vectorized backtesting;
   - event-based backtesting;
   - real-time data y sockets.

Objetivo:

```text
primer motor Python ejecutable
```

## Bloque 3 — Órdenes y ejecución

6. Harris.
7. Documentación de órdenes y ejecución de NautilusTrader.
8. Documentación de órdenes y brokerage de LEAN.
9. Documentación real de DAS.

Objetivo:

```text
Order → OrderEvent → Fill → Position
```

## Bloque 4 — Datos y small caps

10. Literatura sobre:
    - delisting bias;
    - survivorship;
    - corporate actions;
    - stale prices;
    - trades y quotes;
    - liquidez.

Objetivo:

```text
no construir beneficios sobre datos imposibles
```

## Bloque 5 — Validación

11. López de Prado.
12. PBO.
13. DSR.
14. Backtesting protocol.
15. Reality Check/SPA cuando realmente compares muchas variantes.

Objetivo:

```text
no confundir selección con edge
```

# Mi selección mínima: solo seis fuentes

Para no volver a perderte, empezaría únicamente con estas:

1. **NautilusTrader Architecture + Backtesting + Execution docs**
   Esqueleto profesional moderno.

2. **LEAN Algorithm Framework + Engine docs**
   Separación universo, señal, portfolio, riesgo y ejecución.

3. **QuantStart Event-Driven Backtesting series**
   Implementación pedagógica en Python.

4. **Python for Algorithmic Trading — Hilpisch**
   Puente práctico desde Python y datos hasta backtest y directo.

5. **Trading and Exchanges — Harris**
   Realismo de órdenes y ejecución.

6. **Advances in Financial Machine Learning — López de Prado**
   Validación posterior, no construcción inicial.

El libro de Isaac Trullas lo mantendría como material introductorio y práctico, pero no como autoridad arquitectónica única.

# Decisión concreta para TSIS

Yo no comenzaría todavía escribiendo código a partir de los libros.

Primero redactaría un documento único:

```text
TSIS_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md
```

que defina:

```text
1. propósito
2. alcance v0.1
3. modelo de eventos
4. componentes
5. responsabilidades
6. contratos de entrada/salida
7. orden temporal
8. modelo de órdenes
9. modelo de fills
10. modelo de posiciones
11. snapshots de Market State/Event State
12. outputs físicos
13. determinismo
14. equivalencia backtest/replay/live
15. supuestos y limitaciones
16. tests de aceptación
```

Solo después construiría:

```text
BACKTEST_VERTICAL_SLICE_V0_1
```

con una estrategia y un tipo de datos.

La fuente principal para diseñar ese documento debería ser:

```text
NautilusTrader
    +
LEAN
    +
modelo event-driven de QuantStart
```

Y la adaptación científica especial de TSIS sería:

```text
StateSnapshotBuilder
DecisionLedger
EventResearch linkage
Representation versioning
```

Esa combinación sí te da un camino serio y defendible: **no un backtester retail improvisado, pero tampoco una infraestructura institucional infinita antes de emitir la primera señal**.
