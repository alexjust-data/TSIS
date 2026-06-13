# Distributed Systems

## Objetivo

Escalar TSIS.

## Preguntas

- ¿Cómo distribuir cargas?
- ¿Cómo coordinar procesos?
- ¿Cómo escalar experimentos?

## Contenido esperado

- Ray
- Kafka
- Redis
- Event Streaming
- Compute Clusters
- Parallel Research

## Resultado esperado

Sistema capaz de ejecutar miles de experimentos.




Ésta va aquí sin ninguna duda:

```text id="1af5a9"
00_CTO/
└── 07_DISTRIBUTED_SYSTEMS/
```

Pero aquí hay algo importante.

La mayoría de gente piensa:

```text id="n4dg0v"
Distributed Systems
=
Kubernetes
=
DevOps
```

Y para TSIS eso sería un error.

---

Yo redefiniría la carpeta así:

```text id="83r5h0"
07_DISTRIBUTED_SYSTEMS

Cómo escalar investigación,
datos, agentes y ejecución.
```

---

# Estructura que haría

```text id="c4k7s2"
07_DISTRIBUTED_SYSTEMS/
│
├── README.md
│
├── 01_DISTRIBUTED_COMPUTE/
│
├── 02_DISTRIBUTED_DATA/
│
├── 03_EVENT_DRIVEN_ARCHITECTURE/
│
├── 04_AGENT_ORCHESTRATION/
│
├── 05_REALTIME_SYSTEMS/
│
├── 06_MODEL_SERVING/
│
├── 07_CLUSTER_ARCHITECTURE/
│
└── 08_TSIS_SCALING_ROADMAP/
```

---

# 01_DISTRIBUTED_COMPUTE

Aquí:

```text id="w1v8n7"
Ray
Ray Core
Ray Tasks
Ray Actors
Parallel Execution
```

Pregunta:

```text id="n7q2r1"
¿Cómo ejecutar miles de tareas?
```

---

Ejemplo TSIS:

```text id="d3m9x5"
500 estrategias

x

20 años

x

100 configuraciones
```

---

Sin Ray:

```text id="v6p4t8"
semanas
```

---

Con Ray:

```text id="k2f7h3"
horas
```

---

# 02_DISTRIBUTED_DATA

Aquí:

```text id="q9r4m2"
Ray Data
Parquet
Arrow
Dataset Sharding
Distributed ETL
```

Pregunta:

```text id="z4t8c6"
¿Cómo mover terabytes?
```

---

Cuando TSIS tenga:

```text id="x5n1v7"
Tick Data
L1
L2
News
Catalysts
```

esta carpeta será crítica.

---

# 03_EVENT_DRIVEN_ARCHITECTURE

Aquí entra exactamente lo que has pegado.

```text id="f2k9q4"
Kafka
Pub/Sub
Queues
Streaming
Events
```

---

Ejemplo:

```text id="a7m3x8"
Websocket
↓
Event
↓
Universe Update
↓
Alert
↓
Agent
↓
Execution
```

---

Pregunta:

```text id="j6v2p9"
¿Cómo se comunican los sistemas?
```

---

# 04_AGENT_ORCHESTRATION

Muy frontera actual.

```text id="b8n5r1"
ResearchAgent
EvidenceAgent
ValidationAgent
CodeAgent
```

---

Pregunta:

```text id="m4t7k3"
¿Cómo coordinamos agentes?
```

---

Aquí guardaría:

```text id="c1p8v6"
Multi-Agent Systems
Workflows
Task Routing
Agent Handoffs
```

---

# 05_REALTIME_SYSTEMS

MUY TSIS.

```text id="x9r2m5"
WebSockets
Market Data
Streaming
Realtime Analytics
```

---

Pregunta:

```text id="f3k7n1"
¿Cómo procesamos mercado en vivo?
```

---

Aquí acabarán:

```text id="s8v4q2"
Polygon
Databento
IBKR
Live Scanner
```

---

# 06_MODEL_SERVING

Aquí:

```text id="p7m2k8"
NVIDIA Triton
vLLM
Inference Servers
Batching
GPU Serving
```

---

Pregunta:

```text id="r5n8c3"
¿Cómo servimos modelos?
```

---

Ahora mismo TSIS no necesita esto.

---

Pero si un día tienes:

```text id="h2v9m4"
Decision Transformer
RL Policy
Research Model
```

sí.

---

# 07_CLUSTER_ARCHITECTURE

Aquí:

```text id="w4k8p1"
Docker
Kubernetes
Clusters
Deployment
```

---

Y aquí viene algo importante.

NO tocaría Kubernetes durante bastante tiempo.

Para TSIS:

```text id="y6m3q7"
Ray
>>
Kafka
>>
Kubernetes
```

---

Exactamente como pone tu nota.

---

# 08_TSIS_SCALING_ROADMAP

Esta carpeta es la más importante.

Porque traduce teoría a TSIS.

---

Ejemplo:

```text id="g8p2m6"
FASE 1

Portátil

Backtests locales

-------------
FASE 2

Ray local

Paralelización

-------------
FASE 3

Ray Cluster

Research distribuido

-------------
FASE 4

Kafka

Live Trading

-------------
FASE 5

Multi-Agent TSIS

-------------
FASE 6

Production Infrastructure
```

---

Y aquí hay algo que me parece clave para tu proyecto:

### 06_MLOPS_AND_REPRODUCIBILITY

responde:

```text id="k7r4n2"
¿Cómo sabemos qué pasó?
```

---

### 07_DISTRIBUTED_SYSTEMS

responde:

```text id="z2m8v5"
¿Cómo hacemos que ocurra a gran escala?
```

---

Por ejemplo:

```text id="d5p1x9"
ResearchAgent
genera 100 hipótesis
```

eso es:

```text id="q3n7k4"
03_AGENT_ENGINEERING
```

---

```text id="b6v2m8"
Evaluarlas correctamente
```

eso es:

```text id="c9r4p1"
05_EVALUATION_SYSTEMS
```

---

```text id="t8k3n6"
Guardar resultados
```

eso es:

```text id="h4m7q2"
06_MLOPS_AND_REPRODUCIBILITY
```

---

```text id="p2v9k5"
Ejecutar 10.000 evaluaciones simultáneas
```

eso es:

```text id="x7n4r8"
07_DISTRIBUTED_SYSTEMS
```

Por eso esta carpeta es la que convierte TSIS de un proyecto de investigación en un sistema capaz de operar a escala institucional.
