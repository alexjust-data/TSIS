Ambas carpetas siguen superando el umbral de seguridad de Graphify por separado. La forma técnicamente correcta
  existe, pero conviene hacerla por fases: primero grafos por subárea útil, después merge, para no gastar una extracción
  semántica enorme sobre miles de imágenes/docs.

• Sí, se puede. La forma correcta es:

  graphify extract .\00_CTO
  graphify extract .\01_TSIS_backtest_SmallCaps

  Pero no conviene lanzarlo entero todavía. Cada carpeta sigue siendo grande:

  00_CTO: 4676 files · ~50.4M words
    99_REFERENCE_LIBRARY              2556
    12_TSIS_COGNITIVE_ARCHITECTURE    1908
    00_private                          77
    _images                             73
    10_AUTONOMOUS_RESEARCH_SYSTEMS      21

  01_TSIS_backtest_SmallCaps: 1885 files · ~9.3M words
    01_foundations                    1773
    scripts                             77
    01_research                         10
    00_cto                               9
    root                                 7

  Mi recomendación práctica: crear dos grafos, pero acotados primero a lo que realmente vas a consultar.

  Para empezar con valor alto:

  00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE
  01_TSIS_backtest_SmallCaps\01_foundations

  Después fusionamos esos dos. Eso te da un grafo útil para arquitectura/conocimiento institucional sin arrastrar toda
  la librería de referencia ni miles de imágenes.



  ## Inicio
Sí. **Graphify te sirve como “mapa semántico” del repo** para que Codex no tenga que tragarse miles de carpetas y ficheros cada vez.

La idea para TSIS sería:

```text
TSIS repo grande
   ↓
Graphify indexa código + docs + PDFs + SQL + markdown
   ↓
genera graphify-out/
   ├── graph.html
   ├── GRAPH_REPORT.md
   └── graph.json
   ↓
Codex consulta el grafo antes de tocar archivos
```

Graphify dice que funciona con Codex y que para Codex usa `$graphify` en vez de `/graphify`; además recomienda activar `multi_agent = true` en `~/.codex/config.toml` para extracción paralela. ([GitHub][1])

### Instalación básica

En Windows:

```powershell
winget install astral-sh.uv
uv tool install graphifyy
graphify install --platform codex
```

Dentro de tu repo:

```powershell
cd C:\TSIS_DATA
graphify install --project --platform codex
graphify .
```

En PowerShell usa `graphify .`, no `/graphify .`. ([GitHub][1])

### Para carpetas enormes

No indexaría todo TSIS de golpe. Haría esto:

```text
C:\TSIS_DATA\
├── 00_CTO
├── 01_TSIS_backtest_SmallCaps
├── 02_TSIS_webSocket_SmallCaps
├── 03_TSIS_Offline_RL
├── data
├── runs
└── ...
```

Crea `.graphifyignore`:

```gitignore
data/
runs/
run/
.venv/
__pycache__/
node_modules/
dist/
*.parquet
*.csv
*.zip
*.log
*.db
*.sqlite
```

Graphify respeta `.gitignore` y también permite `.graphifyignore`, útil para excluir data pesada y artefactos. ([GitHub][1])

Luego indexa por capas:

```powershell
graphify .\00_CTO
graphify .\01_TSIS_backtest_SmallCaps
graphify .\02_TSIS_webSocket_SmallCaps
```

Y cuando cambies cosas:

```powershell
graphify . --update
```

Graphify permite actualizar solo archivos cambiados con `--update`, consultar el grafo con `graphify query`, explicar nodos con `graphify explain`, y exportar call-flows HTML. ([GitHub][1])

### Cómo trabajaría con Codex

Antes de pedirle a Codex:

```text
“Implementa el executor simulator”
```

le pediría:

```text
$graphify query "qué módulos conectan Event Engine, Strategy Engine y Executor Simulator"
```

Después:

```text
$graphify explain "Executor Simulator"
$graphify path "Event Engine" "Executor Simulator"
```

Así Codex entiende dependencias antes de editar.

### Mi recomendación para ti

Usa Graphify como **capa de memoria estructural del repo**, no como sustituto de Git ni de AGENTS.md.

Para TSIS:

```text
1. AGENTS.md = reglas de trabajo
2. README / module_contracts = contratos humanos
3. Graphify = mapa vivo del sistema
4. Codex = agente que consulta el mapa antes de modificar
```

Y muy importante: **no metas datos históricos masivos en Graphify**. Mete arquitectura, código, docs, contratos, schemas, notebooks limpios y papers clave. Data pesada fuera.

[1]: https://github.com/safishamsi/graphify "GitHub - safishamsi/graphify: AI coding assistant skill (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, and more). Turn any folder of code, SQL schemas, R scripts, shell scripts, docs, papers, images, or videos into a queryable knowledge graph. App code + database schema + infrastructure in one graph. · GitHub"



# multiples grafos

Sí, **hasta cierto punto**, pero hay un matiz importante:

**No quieres un único grafo gigante de TSIS.**
**Quieres una federación de grafos.**

La diferencia es enorme.

---

## Opción A — Un mega-grafo

```text
TSIS
├── CTO
├── Backtest
├── WebSocket
├── RL
├── Research
├── Data
├── Papers
├── Harness
└── ...
```

↓

```text
graph.json
```

de millones de relaciones.

Problemas:

* consultas lentas
* ruido enorme
* conceptos repetidos
* pérdida de contexto
* más coste de extracción
* más difícil de mantener

Es parecido a meter toda Wikipedia en una sola tabla SQL.

---

## Opción B — Federación de grafos (lo que yo haría)

```text
TSIS

graph_cto.json
graph_backtest.json
graph_rl.json
graph_harness.json
graph_research.json
```

Cada uno especializado.

---

### graph_cto

```text
Arquitectura
Principios
Harness
Agentes
Memoria
Evaluación
```

Pregunta:

```text
¿Cómo encaja AlphaEvolve dentro de TSIS?
```

↓

consulta graph_cto

---

### graph_backtest

```text
Universe Builder
Event Engine
Outcome Engine
Strategy Evaluator
```

Pregunta:

```text
¿Qué depende del Outcome Engine?
```

↓

consulta graph_backtest

---

### graph_rl

```text
Offline RL
Decision Transformer
CQL
IQL
Policy Learning
```

Pregunta:

```text
¿Cómo conectar Strategy Evaluator con Offline RL?
```

↓

consulta graph_rl

---

### graph_research

```text
papers
DeepMind
Anthropic
OpenAI
AlphaEvolve
```

Pregunta:

```text
¿Qué papers hablan de harnesses evolutivos?
```

↓

consulta graph_research

---

# Entonces, ¿para qué sirven los merges?

Aquí está la clave.

Yo distinguiría dos tipos:

### Merge permanente

No me gusta.

```text
graph_a
+
graph_b
+
graph_c
=
mega_graph
```

Porque vuelves al problema inicial.

---

### Merge temporal

Sí me gusta.

Ejemplo:

El agente pregunta:

```text
¿Cómo se conecta AlphaEvolve con
Strategy Evaluator?
```

Entonces:

```text
graph_cto
+
graph_backtest
+
graph_rl
```

↓

merge temporal

↓

respuesta

↓

se destruye

````

Eso escala muchísimo mejor.

---

# Lo que haría en TSIS

Tu proyecto ya tiene una separación natural:

```text
00_CTO

01_TSIS_backtest_SmallCaps

02_TSIS_webSocket_SmallCaps

03_TSIS_Offline_RL
````

Yo construiría:

```text
graph_cto

graph_backtest

graph_live

graph_rl
```

Y además:

```text
graph_sersan

graph_reference
```

como grafos auxiliares.

---

# Lo más interesante para el futuro

Cuando empieces con:

```text
Harnesses
Agentes
AlphaEvolve
Research loops
```

cada agente podría consultar solo el grafo relevante.

Por ejemplo:

```text
Research Agent
    ↓
graph_reference

Architect Agent
    ↓
graph_cto

Backtest Agent
    ↓
graph_backtest

RL Agent
    ↓
graph_rl
```

Eso se parece mucho más a cómo trabajan sistemas avanzados de investigación que a tener un único grafo monstruoso.

---

Por eso, si me preguntas si "el problema se resuelve con varios grafos mergeados", mi respuesta sería:

```text
Sí, pero no fusionándolos todos para siempre.

La arquitectura correcta es:
muchos grafos especializados
+
fusiones temporales cuando una tarea lo necesite.
```

Eso encaja mucho mejor con la dirección que estás tomando con TSIS, AlphaEvolve, harnesses y agentes especializados.
