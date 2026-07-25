Creo que ya tenemos suficiente material para dejar de analizar capturas aisladas y empezar a **reconstruir la arquitectura**.

Y aquí quiero hacer una observación importante.

Después de revisar todas las imágenes, los artículos y el código, **no creo que Sersan haya empezado diseñando pantallas**.

Creo que primero diseñaron el **modelo de dominio** y luego construyeron la GUI encima.

Eso cambia completamente el enfoque.

---

# La infraestructura que yo reconstruyo

No la dibujaría desde la GUI.

La dibujaría desde el backend.

```text
                           ┌────────────────────────────┐
                           │     Desktop GUI           │
                           │ Dashboard / Operativa     │
                           │ Config / Logs             │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │     Control Plane          │
                           │                            │
                           │ Configuration Manager      │
                           │ Runtime Commands           │
                           │ Monitoring                │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │      ORCHESTRATOR          │
                           │                            │
                           │ Session State Machine      │
                           │ Scheduler                 │
                           │ Watchdog                  │
                           │ Recovery                  │
                           └──────┬───────────┬────────┘
                                  │           │
                    ┌─────────────┘           └─────────────┐
                    ▼                                       ▼
          Market Data Plane                        Execution Plane
                    │                                       │
                    ▼                                       ▼
             Massive Adapter                        DAS Adapter
                    │                                       │
                    ▼                                       ▼
             Scanner Engine                        Order Events
                    │                                       │
                    └──────────────┬────────────────────────┘
                                   ▼
                           Runtime Core
```

Hasta aquí **no hay estrategia todavía**.

---

# Runtime Core

Aquí es donde creo que está el verdadero sistema.

```text
Runtime Core
│
├── Universe Engine
├── Strategy Registry
├── Strategy Runtime
├── Risk Engine
├── OMS
├── Portfolio Engine
├── Accounting Engine
├── Execution Tracker
└── Event Bus
```

Esta separación está respaldada por varias de las pistas que hemos ido recogiendo:

* estrategias configurables (`estrategias.json5`);
* orquestador separado (`orquestador.json5`);
* vistas distintas para órdenes, ejecuciones, posiciones y análisis;
* consola del scanner independiente;
* configuración por dominios.  

---

# Flujo completo

## 1. Scanner

Massive

↓

```text
Scanner
```

↓

```text
Universe
```

↓

```text
Candidate
```

↓

```text
Eligible
```

↓

```text
Strategy Runtime
```

La consola sugiere exactamente un proceso periódico donde un símbolo pasa a ser "operable" y aumenta el contador de operables. 

---

## 2. Strategy Runtime

La estrategia recibe únicamente:

```text
MarketData
Portfolio
Position
```

y produce:

```text
Signal
```

No debería hablar directamente con DAS.

---

## 3. OMS

El OMS recibe:

```text
Signal
```

↓

crea

```text
Internal Order
```

↓

envía

```text
DAS Order
```

↓

recibe

```text
ActionOrder
```

↓

recibe

```text
Fill
```

↓

actualiza

```text
Position
```

La existencia separada de las pestañas **Órdenes**, **ActionOrder**, **Trades** y **Trazabilidad** apunta precisamente a un pipeline de este estilo, donde la orden interna y los eventos del broker no son el mismo objeto. 

---

# Accounting

Después del fill:

```text
Fill
```

↓

```text
Accounting
```

↓

```text
Position
```

↓

```text
Portfolio
```

↓

```text
Equity
```

↓

```text
Performance
```

Esto explica por qué la pantalla de análisis puede calcular Sharpe, Sortino, drawdown, PnL y generar informes HTML. 

---

# Analytics

Aquí veo otro subsistema independiente.

```text
Accounting
```

↓

```text
Trade Reconstruction
```

↓

```text
Metrics Engine
```

↓

```text
Report Engine
```

↓

```text
Dashboard
```

No creo que la GUI calcule nada.

Creo que consulta.

---

# Lo que falta en Sersan

Aquí es donde aparece TSIS.

Yo añadiría otra rama completamente separada.

```text
Runtime
```

↓

```text
Execution Events
```

↓

```text
Research Events
```

↓

```text
Market State
```

↓

```text
Event State
```

↓

```text
Outcome Engine
```

↓

```text
Knowledge Base
```

Esto no aparece en las capturas ni en los artículos; es la capa que tú ya has diseñado conceptualmente.

---

# La verdadera estructura de carpetas que construiría

No copiaría literalmente la de Sersan.

Haría algo así:

```text
tsis_runtime/

├── adapters/
│   ├── massive/
│   ├── das/
│   └── replay/
│
├── orchestrator/
│
├── scanner/
│
├── universe/
│
├── runtime/
│
├── strategies/
│
├── orders/
│
├── execution/
│
├── portfolio/
│
├── accounting/
│
├── analytics/
│
├── research_bridge/
│
├── config/
│
├── gui/
│
├── reports/
│
├── logs/
│
└── tests/
```

---

# La pieza que más me interesa

No es la GUI.

Es el:

```text
Orchestrator
```

Porque ahora sabemos bastante de él.

Gestiona:

```text
heartbeat
timeouts
reintentos
conexiones
sesión
scanner
estrategias
```

Todo eso está respaldado por los parámetros visibles en `orquestador.json5`. 

Yo lo escribiría así:

```text
Orchestrator

├── Session Manager
├── Scheduler
├── Runtime Lifecycle
├── Recovery Manager
├── Health Monitor
├── Connection Supervisor
├── Strategy Supervisor
└── Event Dispatcher
```

---

# Lo que NO copiaría

Hay algo que deliberadamente no copiaría.

Ellos parecen construir:

```text
Scanner

↓

Operable

↓

Strategy
```

Yo cambiaría eso por:

```text
Scanner

↓

Universe

↓

Candidate

↓

Observed

↓

Eligible

↓

Strategy
```

Porque TSIS necesita distinguir claramente entre:

```text
el scanner detectó algo interesante
```

y

```text
la estrategia está autorizada para operar
```

Esa separación es muy útil para investigación, replay y auditoría.

---

# Mi conclusión técnica

Con todo el material recopilado hasta ahora, creo que la arquitectura de Sersan puede resumirse en **cinco grandes planos**:

```text
1. Configuration Plane
    JSON5
    Runtime parameters
    Strategies
    Calendar
    Logging

2. Control Plane
    GUI
    Orchestrator
    Watchdog
    Scheduler
    Health

3. Data Plane
    Massive
    Scanner
    Universe
    Runtime data

4. Execution Plane
    Strategy
    OMS
    DAS
    Accounting
    Portfolio

5. Analytics Plane
    Metrics
    Reports
    Performance
    Dashboards
```

Y yo añadiría un sexto plano exclusivo de TSIS:

```text
6. Research Plane

Market State
Event State
Outcome Engine
Knowledge Registry
Hypothesis Engine
Research Analytics
```

Ese sexto plano no sustituye al runtime; se alimenta de él.

En mi opinión, **esa es la diferencia arquitectónica más importante** entre un framework profesional de ejecución (como el que parece haber construido Sersan) y el laboratorio cuantitativo que quieres construir con TSIS. 
