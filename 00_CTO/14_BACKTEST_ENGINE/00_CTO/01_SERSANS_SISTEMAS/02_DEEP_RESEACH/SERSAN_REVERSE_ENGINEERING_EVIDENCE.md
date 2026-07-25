# Sersans sistemas

La estructura probable de Sersan no es, como mínimo, un sistema compuesto por estos grandes bloques:

```text
DAS Trading Framework

├── 1. Data Foundation / Historical Research
├── 2. Market Data Runtime
├── 3. Premarket Universe Scanner
├── 4. Runtime Orchestrator
├── 5. Strategy Runtime
├── 6. Locate Management
├── 7. Risk and Operational Controls
├── 8. Order Management and DAS Execution
├── 9. Position and Account Accounting
├── 10. Execution Quality / Slippage
├── 11. Analytics and Reporting
├── 12. Observability and Recovery
├── 13. Configuration System
├── 14. Desktop Control Panel
└── 15. Persistent Operational Storage
```

Esto no significa que esas sean sus carpetas exactas. Significa que son **responsabilidades funcionales demostradas o fuertemente exigidas por la evidencia**.

---

# 1. Data Foundation / Historical Research

Este bloque no aparece directamente en la GUI live, pero aparece con claridad en sus artículos y en su discurso técnico.

Incluye:

```text
historical downloader
symbol history
point-in-time universe
delisted companies
ticker changes
market-cap history
raw/unadjusted prices
premarket history
halts
data-quality validation
backtest datasets
```

Sersan afirma que la descarga no es un trámite, sino una parte estructural; habla de procesos repetibles, miles de compañías, décadas de histórico y datasets preparados para plataformas de backtesting. También insiste en universo point-in-time, supervivencia, precios no ajustados y resolución adecuada. 

Por tanto, su arquitectura global probablemente comienza antes del runtime:

```text
Historical providers
        ↓
Download / normalization pipeline
        ↓
Validated research dataset
        ↓
Backtesting platform
        ↓
Strategy selected for deployment
```

Esto no demuestra que forme parte del mismo repositorio `Das_API`, pero sí que forma parte de su infraestructura algorítmica total.

---

# 2. Market Data Runtime

Evidencias directas:

```text
Data Provider
MASSIVE
LIVE
```

y el logger:

```text
premarket.scanner_massive
```

La función probable del bloque es:

```text
Massive REST / WebSocket
        ↓
market-data adapter
        ↓
normalized market data
        ↓
scanner / buffer / strategies
```

Debe manejar al menos:

```text
snapshots
bars
possibly trades
possibly quotes
timestamps
feed health
subscription state
```

No podemos confirmar qué canales concretos emplean.

---

# 3. Premarket Universe Scanner

Este bloque está confirmado funcionalmente.

La consola muestra ciclos sucesivos:

```text
ciclo 343: 1.5s
operables=6
pendientes=2072
próximo ciclo en 29s
```

y la promoción:

```text
Operable (tipo1): TDIC volumen=920123 (shares)
```

seguida de:

```text
operables=7
```

Eso demuestra un proceso periódico que evalúa un universo y mantiene, como mínimo, dos conjuntos o contadores:

```text
pending / monitored symbols
operable symbols
```

La arquitectura interna mínima es:

```text
Base universe
    ↓
Periodic market snapshot/read
    ↓
Scanner rules
    ↓
Eligibility classification
    ↓
Operable registry
```

El significado exacto de `tipo1` continúa siendo desconocido. Solo sabemos que es una etiqueta emitida por el scanner, no por la estrategia. 

---

# 4. Runtime Orchestrator

Este es uno de los bloques mejor sustentados.

Evidencias:

```text
orquestador.json5
INICIAR TRADING
PAUSAR
REINICIAR
DETENER
Inicio automático al abrir la GUI
Estado: Escaneando PreMarket
Cierres orquestador
```

Y parámetros visibles:

```text
intervalo_heartbeat_segundos
timeout_lectura_segundos
reintento_inicial_segundos
reintento_maximo_segundos
max_reintentos
max_reintentos_conexion
max_duracion_conexion_segundos
timeout_conexion_segundos
espera_reintento_conexion_segundos
```

Su responsabilidad probable es:

```text
session lifecycle
component startup/shutdown
connections
heartbeat supervision
retry policies
recovery
strategy activation
scanner activation
session transitions
forced closing
```

Además, `Origen cierre = orquestador` y `Cierres orquestador: 5/48` demuestran que el orquestador puede intervenir en la operativa, no solo controlar procesos.

Máquina de estados probable, no confirmada literalmente:

```text
STOPPED
STARTING
CONNECTING
PREMARKET_SCAN
READY
TRADING
PAUSED
CLOSING
STOPPING
DEGRADED
FAILED
```

---

# 5. Strategy Runtime

Evidencias:

```text
estrategias.json5
Estrategias 0/0
Sin estrategias cargadas
Estrategias activas
ShortMDL1
Portfolio (todas las estrategias)
Análisis por estrategia
```

Esto confirma:

* múltiples estrategias;
* identidad de estrategia en ejecuciones;
* posibilidad de agregarlas como portfolio;
* carga o activación dinámica;
* configuración externa.

Arquitectura mínima:

```text
Strategy configuration
        ↓
Strategy loader / registry
        ↓
Strategy instance
        ↓
Market-data consumption
        ↓
Trading intent
```

No sabemos:

* si son plugins dinámicos;
* si comparten una clase base;
* si se ejecutan en procesos separados;
* si usan eventos, callbacks o polling.

---

# 6. Locate Management

Está confirmado por:

```text
Locates
locates.json5
```

Y por su discurso:

> detectar una señal short no implica que se pueda operar; hay que localizar acciones, asumir costes y controlar disponibilidad. 

Este bloque probablemente cubre:

```text
locate request
availability
quote/cost
approval
consumption
expiration
rejection
locate attribution to operation
```

No sabemos si DAS proporciona todo, si usan otro proveedor o si parte es manual.

---

# 7. Risk and Operational Controls

No vemos un archivo `risk.json5`, pero la función está demostrada por:

```text
Exposición
retorno flotante
drawdown
cierres del orquestador
stops mediante ZSTOP
botones de pausa/detención
watchdog
```

Y su vídeo declara explícitamente que el sistema debe controlar riesgo, ejecución, errores y recuperación. 

Las responsabilidades mínimas necesarias son:

```text
exposure calculation
position limits
daily-risk controls
stop handling
session-close controls
operational kill/stop
data/feed failure response
```

Todavía no podemos afirmar que exista un `RiskEngine` como módulo separado.

---

# 8. Order Management and DAS Execution

Este bloque es mucho más rico de lo que mostraba el diagrama simple.

La GUI distingue:

```text
Órdenes
ActionOrder
Trades
Trazabilidad
```

Esto indica diferentes niveles del flujo de ejecución.

Reconstrucción funcional probable:

```text
Strategy intent
        ↓
Internal order / operation
        ↓
DAS command
        ↓
ActionOrder / broker response
        ↓
Execution / fill
        ↓
Position update
```

Los trades/fills conservan:

```text
strategy
symbol
side
quantity
price
notional
signed/net flow
route
liquidity
fees
PnL
timestamp
```

Esto demuestra normalización y persistencia de ejecuciones, así como atribución de P&L a fills de cierre. 

DAS aparece conectado mediante:

```text
localhost:9910
```

Por tanto, existe como mínimo un canal local entre el framework y la interfaz/API de DAS.

---

# 9. Position and Account Accounting

Está confirmado funcionalmente por:

```text
Cuenta & Performance
Posiciones
PnL realizado
PnL flotante
equity
exposición
PnL bruto
PnL neto
comisiones
```

Flujo mínimo requerido:

```text
fills
   ↓
position reconstruction
   ↓
average/cost basis
   ↓
realized PnL
   ↓
unrealized PnL
   ↓
account/equity state
```

La pantalla de fills muestra P&L cero en aperturas y P&L en compras que probablemente cubren shorts, lo que implica una política de accounting y matching de fills. No podemos determinar si utilizan average cost, FIFO u otra convención. 

---

# 10. Execution Quality / Slippage

La navegación principal incluye:

```text
Deslizamientos
```

Y en la tabla de ejecuciones se registra:

```text
Ruta
Liquidez
Tarifas
Fees Total
Timestamp
```

Además, el discurso público coloca el slippage como uno de los problemas esenciales de small caps: el backtest entra donde quiere y el real donde puede.

Por tanto, existe muy probablemente una capa de análisis de ejecución que relaciona:

```text
expected price
actual fill price
route
liquidity flag
fees
time
strategy
symbol
```

No sabemos si mide latencias ni cuál es su precio benchmark.

---

# 11. Analytics and Reporting

Está confirmado por:

```text
Análisis
Cuenta & Performance
Gráficos
PnL acumulado
PnL diario
Drawdown
Comisiones
Win Rate
Profit Factor
Sharpe
Sortino
Avg Win
Avg Loss
Informe HTML
Export CSV
```

También permite:

```text
análisis por estrategia
portfolio agregado
rango
mensual
total
hoy
base de retornos
```

Y conserva trades agregados con:

```text
entrada
salida
símbolo
lado
qty
precio entrada
precio salida
PnL
R
DD
origen cierre
```

Esto requiere al menos:

```text
execution ledger
trade reconstruction
account/equity series
return-series construction
metrics calculation
query/filter layer
HTML renderer
CSV export
```

No necesariamente son servicios separados. Son responsabilidades comprobables.

---

# 12. Observability and Recovery

Evidencias directas:

```text
Watchdog: Activo / Monitoreando
Consola
Logs
Copiar
Limpiar
CPU
Memoria
status
DAS connection indicator
heartbeat/retry configuration
notificaciones.json5
logs.json5
```

Debe existir alguna combinación de:

```text
structured logging
health checks
resource monitoring
connection monitoring
retry/recovery
alerts
operator console
```

Su vídeo también menciona explícitamente:

```text
registros
errores
informes
alertas
recuperación cuando algo falla
```

y afirma que el repositorio principal supera 200 archivos, 107.000 líneas, 2.687 funciones y 253 clases. 

---

# 13. Configuration System

Confirmado directamente.

Árbol visible:

```text
config/
├── estrategias.json5
├── festivos_manual.csv
├── gui_visualizacion.json5
├── locates.json5
├── logs.json5
├── notificaciones.json5
├── orquestador.json5
└── premarket.json5
```

La GUI edita y valida JSON5 antes de guardar. 

Esto demuestra configuración externa por dominios.

No demuestra:

* versionado;
* validación semántica;
* aplicación en caliente;
* rollbacks;
* separación dev/live.

---

# 14. Desktop Control Panel

El código visible apunta con bastante fuerza a:

```text
Python
CustomTkinter
async bridge
widgets propios
```

Se observan o se han leído elementos como:

```text
import customtkinter as ctk
AsyncBridge
ConsoleWidget
StatusCard
StrategyList
DashboardTab
grid_columnconfigure
config/orquestador.json5
```

Por tanto, la GUI parece una aplicación desktop Python modular, no una web app y probablemente no PySide. 

La organización parcial directamente sugerida por imports es:

```text
src/
├── gui/
│   ├── widgets/
│   ├── dialogs/
│   └── utils/
└── utils/
    └── zonas_horarias
```

Esta sí es una pista de estructura física, aunque los nombres exactos de archivos continúan parcialmente ilegibles.

---

# 15. Persistent Operational Storage

Tiene que existir alguna persistencia porque la aplicación puede consultar:

```text
hoy
mensual
rango
total
```

y exportar:

```text
CSV
HTML
```

Además mantiene:

```text
86 ejecuciones
48 trades cerrados
series de equity
métricas
origen de cierre
```

Eso exige almacenar, como mínimo conceptual:

```text
orders
broker/order events
fills
positions
trades
account/equity snapshots
strategy identity
fees
close attribution
logs
```

No sabemos el medio:

```text
SQLite
PostgreSQL
CSV
JSON
Parquet
otro
```

Por tanto, `data_or_runtime_storage/` no puede presentarse como carpeta real, pero **la capa de persistencia sí debe figurar en la arquitectura reconstruida**.

---

# Arquitectura funcional reconstruida más probable

La representación más fiel que puedo hacer ahora es esta:

```text
HISTORICAL / RESEARCH SIDE
┌─────────────────────────────────────────────────────────────┐
│ Historical data acquisition and validation                 │
│ Point-in-time universe · unadjusted prices · market cap     │
│ premarket · halts · dirty-data controls                     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKTESTING AND STRATEGY RESEARCH                           │
│ Strategy rules · execution assumptions · costs · locates    │
│ walk-forward · robustness · validation                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                  strategy approved for live
                             │
                             ▼
                        LIVE RUNTIME


┌─────────────────────────────────────────────────────────────┐
│ CONFIGURATION                                               │
│ strategies · premarket · locates · orchestrator · logs      │
│ notifications · GUI · calendar overrides                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR / OPERATIONAL SUPERVISION                      │
│ session lifecycle · start/pause/restart/stop · heartbeat    │
│ connection retry · watchdog · forced exits · market clock   │
└───────────────┬────────────────────────────┬────────────────┘
                │                            │
                ▼                            ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│ MASSIVE MARKET DATA          │  │ DAS EXECUTION CONNECTION  │
│ live feed / snapshots        │  │ localhost:9910            │
│ normalization / buffer       │  │ orders / responses / fills│
└───────────────┬──────────────┘  └──────────────┬────────────┘
                │                                │
                ▼                                │
┌──────────────────────────────┐                 │
│ PREMARKET SCANNER            │                 │
│ recurring cycles             │                 │
│ pending / operable registry  │                 │
│ operability type/reason      │                 │
└───────────────┬──────────────┘                 │
                │                                │
                ▼                                │
┌──────────────────────────────┐                 │
│ STRATEGY RUNTIME             │                 │
│ registry · instances         │                 │
│ signal/decision generation   │                 │
└───────────────┬──────────────┘                 │
                │                                │
                ▼                                │
┌──────────────────────────────┐                 │
│ LOCATE / RISK CONTROLS       │                 │
│ availability · cost · limits │                 │
│ stops · exposure · shutdown  │                 │
└───────────────┬──────────────┘                 │
                │                                │
                ▼                                │
┌─────────────────────────────────────────────────────────────┐
│ ORDER AND EXECUTION WORKFLOW                                │
│ internal orders → DAS action orders → fills → traceability  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ POSITION / ACCOUNTING                                      │
│ positions · cash/equity · realized/unrealized PnL · fees    │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴───────────────┐
              ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│ EXECUTION QUALITY            │  │ ANALYTICS / REPORTING     │
│ slippage · routes · liquidity│  │ trades · returns · PF     │
│ costs · expected vs actual   │  │ Sharpe · DD · HTML · CSV  │
└──────────────────────────────┘  └───────────────────────────┘

Transversal:
GUI · logs · notifications · watchdog · persistence · calendar/time
```

# ¿Y el árbol de carpetas?

No podemos afirmar todavía un árbol completo.

La versión metodológicamente correcta es:

```text
Das_API/

├── config/                              [CONFIRMED]
│   ├── estrategias.json5                [CONFIRMED]
│   ├── festivos_manual.csv              [CONFIRMED]
│   ├── gui_visualizacion.json5          [CONFIRMED]
│   ├── locates.json5                    [CONFIRMED]
│   ├── logs.json5                       [CONFIRMED]
│   ├── notificaciones.json5             [CONFIRMED]
│   ├── orquestador.json5                [CONFIRMED]
│   └── premarket.json5                  [CONFIRMED]
│
├── src/                                 [CONFIRMED]
│   ├── gui/                             [CONFIRMED]
│   │   ├── widgets/                     [CONFIRMED]
│   │   │   ├── console_widget           [CONFIRMED/PARTIAL]
│   │   │   ├── status_card              [CONFIRMED/PARTIAL]
│   │   │   └── strategy_list            [CONFIRMED/PARTIAL]
│   │   ├── dialogs/                     [CONFIRMED]
│   │   ├── utils/                       [CONFIRMED]
│   │   └── dashboard_tab                [CONFIRMED/PARTIAL]
│   │
│   └── utils/
│       └── zonas_horarias               [CONFIRMED]
│
├── premarket/scanner_massive            [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── orchestrator                         [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── strategies                           [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── DAS integration                      [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── Massive integration                  [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── order/execution subsystem            [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── positions/accounting                 [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── locates                              [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── analytics/reporting                  [FUNCTION CONFIRMED;
│                                         PHYSICAL PATH UNKNOWN]
├── logs/                                [PERSISTENCE STRONGLY INFERRED]
├── reports/                             [PERSISTENCE STRONGLY INFERRED]
└── operational data store               [EXISTENCE REQUIRED;
                                          TECHNOLOGY/PATH UNKNOWN]
```

## directa

Después de leer de nuevo todo, creo que su sistema contiene:

1. una infraestructura histórica y de backtesting;
2. una infraestructura live basada en Massive + DAS;
3. un scanner premarket;
4. un orquestador operativo;
5. carga y ejecución de múltiples estrategias;
6. locates;
7. riesgo y stops;
8. OMS y trazabilidad de DAS;
9. accounting de posiciones y cuenta;
10. análisis de slippage;
11. métricas e informes;
12. logs, watchdog, notificaciones y recuperación;
13. configuración externa;
14. GUI desktop;
15. persistencia operativa.

Eso es mucho más cercano a lo que realmente indican los apuntes.


