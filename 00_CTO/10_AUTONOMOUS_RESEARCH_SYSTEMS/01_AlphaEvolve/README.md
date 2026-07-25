# AlphaEvolve En TSIS - Generador De Candidate Research Experiments

Fecha de revision: 2026-07-05
Estado: lectura_operativa_alineada_con_TSIS_LAB_ARCHITECTURE_v3

## Posicion Oficial En TSIS v3

AlphaEvolve no es el centro de TSIS.

El centro de TSIS es:

```text
Scientific Discovery Engine
-> Scientific Validation Pipeline
```

AlphaEvolve es un generador posible de:

```text
candidate research experiments
candidate sampling probes
candidate parameter grids
candidate representation builders
candidate event detectors
candidate transition hypotheses
candidate policy candidates
```

La unidad que AlphaEvolve debe producir para TSIS no es una estrategia final ni una verdad de mercado.

La unidad correcta es:

```text
research_experiment
```

Un experimento propuesto por AlphaEvolve y uno propuesto por un humano deben usar:

```text
same experiment object
same execution protocol
same evidence format
same scientific validation pipeline
```

## Autoridad Y Limites

AlphaEvolve puede proponer candidatos.

AlphaEvolve no puede decidir:

```text
validated knowledge
production readiness
truth of market_state
truth of event_state
truth of outcomes
lineage rewrites
leakage gate disabling
quality gate disabling
sealed holdout reuse
promotion to operational component
```

Si AlphaEvolve modifica el evaluador, eso no es una ejecucion normal de discovery. Debe declararse como experimento separado de diseno de evaluador y validarse con controles adicionales.

## Lecturas Obligatorias Antes De Usarlo

```text
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
C:/TSIS_Data/03_TSIS_Lab/README.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/scientific_validation_pipeline_contract_v0_1.md
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY/03_HUMAN_AND_AI_RESEARCHERS/human_and_alphaevolve_common_protocol.md
C:/TSIS_Data/00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md
```

## Relacion Con El Contenido Tecnico De Este README

Las secciones siguientes conservan la sintesis tecnica de AlphaEvolve: representacion como codigo, mutacion, evaluator, memoria y escalado.

Esa mecanica es util, pero queda subordinada al contrato TSIS:

```text
AlphaEvolve mechanics
-> candidate research experiment
-> TSIS Lab execution
-> Scientific Validation Pipeline
-> evidence/knowledge promotion
```

## Mecanica Tecnica De AlphaEvolve (Referencia)

AlphaEvolve no es "un LLM que inventa y ya". Es un sistema de busqueda evolutiva donde el LLM propone cambios de codigo y un evaluator automatico decide que candidatos sobreviven dentro de ese loop. En TSIS, ese evaluator no es autoridad final: queda subordinado al Scientific Validation Pipeline. La unidad tecnica no es el prompt: es el bucle `programa -> mutacion -> ejecucion -> score -> memoria -> nueva mutacion`.

Segun el paper de DeepMind, el usuario entrega: programa inicial, bloques marcados para evolucionar, evaluator, metricas y configuracion. Luego el sistema samplea programas anteriores desde una base evolutiva, construye prompts ricos, pide diffs al LLM, ejecuta el candidato, lo puntua y guarda los prometedores.

Fuente principal: https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/AlphaEvolve.pdf

## Arquitectura Destilada

```text
Problem Spec
  initial_program.py
  evaluator.py
  fitness config
  guardrails

Evolution Engine
  prompt_sampler
  LLM ensemble
  diff/apply engine
  sandbox executor
  evaluator pool
  program database
  selector/archive
  async controller
```

## 1. Como Representa El Problema

AlphaEvolve representa candidatos como codigo ejecutable, no como texto libre. El paper indica que se pueden marcar bloques con comentarios tipo `EVOLVE-BLOCK-START` / `EVOLVE-BLOCK-END`, dejando el resto como skeleton estable. Eso permite evolucionar desde una funcion pequena hasta partes grandes de un codebase.

La decision clave para clonarlo: no buscar "la solucion" directamente si se puede buscar un programa que genere soluciones. Esto viene de FunSearch: buscar programas suele ser mas interpretable, compacto y escalable que buscar listas crudas de objetos.

Fuente FunSearch: https://www.nature.com/articles/s41586-023-06924-6

## 2. Como Genera Candidatos

Usa un ensemble de LLMs: en el paper, Gemini 2.0 Flash para volumen y Gemini 2.0 Pro para calidad ocasional. El output normalmente son bloques `SEARCH/REPLACE`, no archivos enteros, aunque puede configurarse para reescritura completa en problemas pequenos.

El prompt incluye soluciones anteriores, scores, outputs, contexto humano, literatura, feedback de ejecucion y a veces meta-prompts evolucionados.

Fuente arXiv: https://arxiv.org/abs/2506.13131

## 3. Como Evalua Automaticamente

Cada candidato se ejecuta contra una funcion `evaluate` que devuelve un diccionario de metricas escalares. AlphaEvolve admite cascadas de evaluacion: pruebas pequenas primero, pruebas dificiles solo si pasa las anteriores. Tambien paraleliza evaluaciones costosas y puede anadir feedback LLM para criterios blandos como simplicidad.

Esto es el antidoto contra hallucination: el LLM puede proponer basura, pero solo sobrevive lo que compila, corre, respeta invariantes y mejora metricas.

## 4. Como Selecciona Ganadores

La memoria no es solo una lista de "mejores". Es una base evolutiva que balancea explotacion y exploracion. DeepMind dice que esta inspirada en MAP-Elites y modelos de islas.

Practicamente: guardar elites por nicho, no solo el top global. Si guardas solo el mejor score, converges pronto y pierdes diversidad.

Fuente MAP-Elites: https://arxiv.org/abs/1504.04909

## 5. Como Muta / Mejora Variantes

La mutacion es semantica: el LLM modifica codigo con conocimiento de dominio, no con cambios aleatorios de caracteres. En el ejemplo de multiplicacion de matrices, AlphaEvolve llego a tocar optimizer, inicializacion, loss function y sweep de hiperparametros; el paper menciona una solucion que requirio 15 mutaciones.

## 6. Como Evita Basura

Guardrails minimos para clonar bien:

```text
- Ejecutar en sandbox sin red.
- Timeouts y limites de memoria.
- Tests de correccion antes de performance.
- Evaluacion en train y holdout.
- Seeds fijas para reproducibilidad.
- Rechazo si cambia APIs prohibidas.
- Rechazo si usa IO, randomness no controlada o shortcuts.
- Validacion final humana para candidatos ganadores.
```

DeepMind uso verificacion robusta en hardware/Verilog, comparacion contra referencia en inputs aleatorios y revision humana final en casos criticos.

## 7. Como Guarda Memoria

Una base minima deberia guardar:

```text
candidate_id
parent_id
island_id
code_hash
full_code
diff
prompt_used
model_used
metrics_json
artifacts: stdout/stderr/profiling/errors
validity_status
runtime
created_at
```

La clave es que la memoria sirve para construir futuros prompts, no solo para reporting.

## 8. Como Escala Experimentos

AlphaEvolve usa pipeline asincrono: controller, LLM samplers y evaluation nodes. Esta optimizado para throughput, no para que una evaluacion individual sea rapida.

FunSearch ya usaba una idea parecida con samplers y evaluators distribuidos; reportaron configuraciones con muchos evaluadores CPU corriendo en paralelo.

## Blueprint Clonable

```python
while budget_remaining:
    parent, inspirations = database.sample()
    prompt = prompt_sampler.build(parent, inspirations, context, artifacts)
    diff = llm.generate(prompt)
    child = apply_diff(parent.code, diff)

    result = evaluator_cascade(child)

    if result.valid:
        database.add(child, result)
        archive.update(child, result)
```

## Ejemplo Demostrable Minimo

Problema evolutivo: online bin packing. El LLM solo puede cambiar `priority`.

```python
# candidate.py
def priority(item: float, free: float) -> float:
    # EVOLVE-BLOCK-START
    if item > free:
        return -1e9
    return -(free - item)  # baseline: best-fit
    # EVOLVE-BLOCK-END
```

```python
# evaluator.py
from candidate import priority

CASES = [
    [0.4, 0.6, 0.2, 0.8, 0.5, 0.5],
    [0.7, 0.3, 0.3, 0.3, 0.4, 0.6],
]

def pack(items, capacity=1.0):
    bins = []
    for item in items:
        best_i, best_s = None, -1e18
        for i, free in enumerate(bins):
            if item <= free:
                s = priority(item, free)
                if s > best_s:
                    best_i, best_s = i, s
        if best_i is None:
            bins.append(capacity - item)
        else:
            bins[best_i] -= item
    return len(bins), sum(bins)

def evaluate():
    total_bins, total_waste = 0, 0.0
    for case in CASES:
        n_bins, waste = pack(case)
        total_bins += n_bins
        total_waste += waste
    return {
        "score": -total_bins - 0.01 * total_waste,
        "bins": -total_bins,
        "waste": -total_waste,
    }
```

Esto ya contiene la esencia: representacion, evaluator, fitness, guardrail de factibilidad y espacio de mutacion controlado.

## Que Debemos Clonar, No Copiar

AlphaEvolve como sistema cerrado no esta publicado. DeepMind si publico resultados matematicos y verificadores, pero el README del repo aclara que ese repo no contiene el codigo para ejecutar AlphaEvolve.

Resultados publicados: https://github.com/google-deepmind/alphaevolve_results
README raw: https://raw.githubusercontent.com/google-deepmind/alphaevolve_results/main/README.md

Para clonar bien, conviene tomar:

- De AlphaEvolve: full-file/block evolution, evaluator cascades, multi-metric scoring, LLM ensemble, async pipeline.
- De FunSearch: skeleton estable, funcion critica evolutiva, island model, best-shot prompting.
- De MAP-Elites: archivo diverso, no solo leaderboard.
- De OpenEvolve: referencia practica open-source para estructura moderna de clon.

OpenEvolve: https://github.com/algorithmicsuperintelligence/openevolve
README raw: https://raw.githubusercontent.com/algorithmicsuperintelligence/openevolve/main/README.md

## Criterio Principal

Un problema es "evolucionable" si cumple esto:

```text
1. Se puede representar como codigo.
2. Se puede ejecutar muchas veces.
3. Se puede puntuar automaticamente.
4. Los errores se detectan sin juicio humano.
5. Hay espacio real de mejora.
6. La mejora pequena acumulada importa.
```

Si falta el evaluator, no tenemos AlphaEvolve; tenemos brainstorming con LLM. En TSIS, ademas, si falta `research_experiment`, evidencia reproducible y Scientific Validation Pipeline, no tenemos discovery aceptable; tenemos exploracion no gobernada.


