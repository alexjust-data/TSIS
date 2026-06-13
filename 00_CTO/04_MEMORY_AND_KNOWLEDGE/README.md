# Memory And Knowledge

## Objetivo

Gestionar conocimiento persistente.

## Preguntas

- ¿Qué debe recordar TSIS?
- ¿Cómo recupera contexto?
- ¿Cómo se representa el conocimiento?

## Contenido esperado

- Memory Systems
- Context Engineering
- Agent Memory
- Knowledge Bases
- RAG
- GraphRAG
- Knowledge Graphs

## Resultado esperado

Memoria institucional permanente.



## 3. Memory Systems / Context Engineering

**Frontera actual:** memoria jerárquica, notas persistentes, recuperación contextual y memoria agente. MemGPT planteó los LLMs como sistemas con memoria tipo sistema operativo; Anthropic habla de *agentic memory* y notas persistidas fuera del contexto; A-Mem propone memoria dinámica estilo Zettelkasten. ([arXiv][6])

**RAG moderno:** ya no basta con vector DB simple. La frontera es Agentic RAG, GraphRAG, contextual retrieval, reranking y recuperación híbrida. Anthropic reporta que Contextual Retrieval reduce fallos de recuperación en un 49%, y hasta 67% con reranking. ([arXiv][7])

**Para TSIS:** memoria de hipótesis, trades, patrones, papers, experimentos, decisiones arquitectónicas y errores históricos. Esto puede ser más importante que entrenar un modelo.

**Recursos:** MemGPT, Anthropic Context Engineering, Anthropic Contextual Retrieval, Microsoft GraphRAG, Agentic RAG Survey. ([arXiv][6])

---


De hecho, si AlphaEvolve te enseñó una cosa y Anthropic otra, es esta:

```text id="qt85mf"
Un agente inteligente que olvida
es casi inútil.
```

---


```text id="r61y1r"
04_MEMORY_AND_KNOWLEDGE/
│
├── 01_CONTEXT_ENGINEERING/
│
├── 02_AGENT_MEMORY/
│
├── 03_RAG_SYSTEMS/
│
└── 04_GRAPHRAG/
```

---

# Context Engineering

```text id="trj6gl"
01_CONTEXT_ENGINEERING/
```

Aquí guardaría:

```text id="q7zj5m"
Anthropic Context Engineering
Contextual Retrieval
Context Windows
Context Compression
Long Context Design
```

Pregunta central:

```text id="4s42hl"
¿Cómo damos al agente
la información correcta?
```

---

# Agent Memory

```text id="jsq9yz"
02_AGENT_MEMORY/
```

Aquí:

```text id="2v54w7"
MemGPT
A-Mem
Agent Memory
Persistent Notes
Progress Files
Working Memory
Long-Term Memory
```

Pregunta central:

```text id="jlwm31"
¿Qué debe recordar un agente?
```

---

# RAG Systems

```text id="r3m7fd"
03_RAG_SYSTEMS/
```

Aquí:

```text id="jlwm32"
Classical RAG
Hybrid Search
Reranking
Agentic RAG
Retrieval Pipelines
```

Pregunta:

```text id="jlwm33"
¿Cómo recuperamos conocimiento?
```

---

# GraphRAG

```text id="jlwm34"
04_GRAPHRAG/
```

Aquí:

```text id="jlwm35"
Microsoft GraphRAG
Knowledge Graph Retrieval
Entity Graphs
Relationship Graphs
```

Pregunta:

```text id="jlwm36"
¿Cómo razonamos sobre relaciones?
```

---

# Pero para TSIS hay algo mucho más interesante

Yo crearía esto:

```text id="jlwm37"
06_RESEARCH_MEMORY/
```

porque creo que aquí está la verdadera ventaja competitiva futura.

---

Ejemplo:

```text id="jlwm38"
06_RESEARCH_MEMORY/
│
├── Hypothesis_Memory.md
├── Experiment_Memory.md
├── Failure_Memory.md
├── Edge_Memory.md
├── Paper_Memory.md
└── Research_Graph.md
```

---

Porque TSIS no necesita recordar:

```text id="jlwm39"
qué es Python
```

Eso ya lo sabe GPT.

---

TSIS necesita recordar:

```text id="jlwm40"
Hipótesis H-042 falló

Porque:

Low Float
+
Biotech
+
SSR

no produjo edge
durante régimen de baja liquidez
en 2024-2025
```

---

Eso es memoria científica.

---

# Y luego esta carpeta

```text id="jlwm41"
07_ARCHITECTURAL_MEMORY/
```

Aquí guardarías:

```text id="jlwm42"
Decisiones técnicas
ADR
Arquitectura
Errores históricos
Lecciones aprendidas
```

Ejemplo:

```text id="jlwm43"
ADR-001

No usar barras temporales.

Razón:

Information Bars demostraron
menor ruido.
```

---

# Y ésta

```text id="jlwm44"
08_TRADING_MEMORY/
```

Probablemente será enorme.

Ejemplo:

```text id="jlwm45"
Ticker
Setup
Catalyst
Outcome
Lessons
Market State
```

---

# Lo más importante

La mayoría de gente piensa:

```text id="jlwm46"
RAG = buscar PDFs
```

Eso es la versión 2023.

---

La frontera actual es:

```text id="jlwm47"
Memoria institucional
```

---

Si tuviera que definir TSIS dentro de 5 años, diría:

```text id="jlwm48"
TSIS =
Research System
+
Memory System
```

Porque el verdadero activo no serán los modelos.

Ni los agentes.

Ni AlphaEvolve.

Será algo mucho más difícil de construir:

```text id="jlwm49"
Una memoria acumulada de años de:

hipótesis
experimentos
trades
papers
errores
decisiones
evidencias
```

Y por eso esta sección no es una carpeta técnica.

En realidad es:

```text id="jlwm50"
La memoria a largo plazo de TSIS.
```

Si algún día tienes:

```text id="jlwm51"
ResearchAgent
EvidenceAgent
BacktestAgent
AlphaEvolveAgent
```

todos acabarán leyendo y escribiendo aquí continuamente. De hecho, para un sistema de investigación autónoma, esta carpeta será probablemente más valiosa que cualquier modelo ML que entrenes.
