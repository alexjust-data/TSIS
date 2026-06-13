# MLOps And Reproducibility

## Objetivo

Garantizar trazabilidad total.

## Preguntas

- ¿Qué datos generaron este resultado?
- ¿Qué versión del código?
- ¿Qué experimento?

## Contenido esperado

- DVC
- MLflow
- Experiment Tracking
- Dataset Versioning
- Model Registry
- CI/CD

## Resultado esperado

Ciencia reproducible.



Ésta es la más fácil de clasificar.

Va directamente aquí:

```text id="0bzxtg"
00_CTO/
└── 06_MLOPS_AND_REPRODUCIBILITY/
```

De hecho, esa carpeta existe precisamente para esto.

---

# Qué es realmente MLOps

Mucha gente cree que MLOps es:

```text id="6w4n5h"
MLflow
DVC
Docker
```

No.

Eso son herramientas.

---

MLOps realmente responde a una pregunta:

```text id="njzqhk"
¿Puedo reproducir exactamente
este resultado dentro de 3 años?
```

---

Por ejemplo:

Imagina que en TSIS encuentras:

```text id="8c7dfm"
Gap & Go
Expectancy = +0.43R
```

dentro de 2 años deberías poder responder:

```text id="g0jgbz"
¿Qué datos se usaron?

¿Qué versión del Universe Builder?

¿Qué versión del Event Engine?

¿Qué configuración?

¿Qué código?

¿Qué dataset?

¿Qué filtros?

¿Qué fecha?
```

---

Si no puedes responder eso:

```text id="yv0vkq"
NO tienes ciencia

Tienes magia negra
```

---

# Cómo lo organizaría

```text id="mtz4tx"
06_MLOPS_AND_REPRODUCIBILITY/
│
├── README.md
│
├── 01_EXPERIMENT_TRACKING/
│
├── 02_DATA_VERSIONING/
│
├── 03_MODEL_VERSIONING/
│
├── 04_STRATEGY_VERSIONING/
│
├── 05_AGENT_OBSERVABILITY/
│
├── 06_PIPELINES/
│
├── 07_REPRODUCIBILITY/
│
├── 08_TSIS_STANDARDS/
│
└── 09_TOOLING/
```

---

# Experiment Tracking

```text id="vr2g3g"
01_EXPERIMENT_TRACKING/
```

Aquí:

```text id="b3e4j7"
MLflow
Experiment IDs
Run IDs
Tracking
Metrics
Artifacts
```

Pregunta:

```text id="j67q4g"
¿Qué experimento produjo esto?
```

---

# Data Versioning

```text id="3g4v7x"
02_DATA_VERSIONING/
```

Aquí:

```text id="q6h7r9"
DVC
Dataset Versioning
Snapshots
Raw Data Lineage
```

Pregunta:

```text id="m9w2c8"
¿Qué datos generaron este resultado?
```

---

# Model Versioning

```text id="r8d4s2"
03_MODEL_VERSIONING/
```

Aquí:

```text id="n1k6z4"
Model Registry
MLflow Registry
Model Lineage
```

Pregunta:

```text id="x7f3p5"
¿Qué modelo produjo esta predicción?
```

---

# Strategy Versioning

Ésta para TSIS será enorme.

```text id="z5j8h2"
04_STRATEGY_VERSIONING/
```

---

Ejemplo:

```text id="q1v9n4"
GapGo_v12

EMA8 filter añadido

Float max cambiado

SSR filter añadido
```

---

Pregunta:

```text id="y6m3t8"
¿Qué versión de estrategia
produjo este edge?
```

---

# Agent Observability

```text id="k4p7w1"
05_AGENT_OBSERVABILITY/
```

Muy frontera 2026.

---

Aquí:

```text id="d2r8c6"
LangSmith
OpenTelemetry
Agent Tracing
Cost Tracking
Tool Usage
```

Pregunta:

```text id="h9s5j3"
¿Qué hizo exactamente el agente?
```

---

# Pipelines

```text id="p7x2k9"
06_PIPELINES/
```

Aquí:

```text id="v3n8f1"
ETL
Feature Pipelines
Training Pipelines
Research Pipelines
```

Pregunta:

```text id="c5m1q7"
¿Cómo fluye el sistema?
```

---

# Reproducibility

```text id="w8k6t4"
07_REPRODUCIBILITY/
```

Probablemente la sección más importante.

---

Aquí:

```text id="f2r7v9"
Determinism
Seeds
Environment
Docker
CI
Validation
```

---

Pregunta:

```text id="n4x8j6"
¿Puede repetirse el resultado?
```

---

# TSIS Standards

```text id="j7q3m5"
08_TSIS_STANDARDS/
```

Aquí definirías cosas como:

```text id="u9v2k4"
experiment_id

dataset_version

strategy_version

model_version

report_version
```

---

Por ejemplo:

```text id="s3w7n8"
EXP-2026-0042

dataset_version = D17

strategy_version = GAPGO_V11

event_engine = EE_V3

report_version = R7
```

---

# Lo importante para TSIS

Yo haría una separación mental muy clara:

```text id="g5p8x2"
05_EVALUATION_SYSTEMS
```

responde:

```text id="h7m4q1"
¿Funciona?
```

---

```text id="z2n6v9"
06_MLOPS_AND_REPRODUCIBILITY
```

responde:

```text id="c8r3t5"
¿Puedo demostrar cómo llegué aquí?
```

---

Y te diría algo que aprendí viendo proyectos cuantitativos grandes:

Cuando llegues a:

```text id="m1x7k3"
1000 backtests
100 estrategias
50 modelos
20 agentes
```

el problema ya no será encontrar edge.

Será:

```text id="q4v8n2"
recordar qué demonios produjo cada resultado.
```

Por eso, para un sistema como TSIS, esta carpeta no es infraestructura.

Es la **cadena de custodia científica** de todo el conocimiento que genere el sistema.
