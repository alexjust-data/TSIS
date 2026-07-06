# TSIS Lab Architecture v3

Fecha de creacion: 2026-07-05
Estado: arquitectura_v3_cto_vigente
Origen: revision conceptual de `_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE_v2.md` despues de introducir `Scientific Discovery Engine` y `00_TSIS_Lab`
Owner layer: `00_CTO`

## Proposito

Este documento fija la lectura CTO v3 de TSIS.

No borra ni reemplaza fisicamente a:

```text
_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE.md      # v1 historica
_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE_v2.md   # arquitectura state/event-first
```

La v3 cambia el centro de gravedad:

```text
v1 = arquitectura inicial promovida desde 00_private
v2 = arquitectura state/event-first
v3 = Scientific Discovery Engine
```

## Tesis v3

TSIS no es un backtester.
TSIS no es una coleccion de estrategias.
TSIS no es AlphaEvolve.
TSIS no es una tabla de estado.

TSIS es un:

```text
Scientific Discovery Engine
```

Su objetivo es convertir preguntas sobre el mercado en conocimiento validado y, solo despues, en componentes operativos.

## Principio Central

```text
proponer no es validar
optimizar no es descubrir
buen backtest no es conocimiento
sampling probe no es evento validado
```

La unidad central de trabajo ya no es:

```text
event
strategy
model
alphaevolve_candidate
```

La unidad central es:

```text
research_experiment
```

## Cadena Logica v3

```text
Data Foundation
-> Canonical State / Event State / Outcomes
-> Research Experiment
-> Execution
-> Evidence
-> Scientific Validation Pipeline
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
-> ML / RL / AlphaEvolve / Live, segun corresponda
```

## Separacion Sagrada

```text
X = market_state / event_state legal as-of
probe = forma de mirar o muestrear
window = frontera temporal declarada
Y = outcomes separados
experiment = diseno cientifico para mirar X e Y
knowledge = conclusion promovida por evidencia
policy = decision posterior
execution = factibilidad bajo friccion real
```

Ninguna capa posterior puede reescribir silenciosamente:

```text
raw data
lineage
cutoff/as-of
quality gates
leakage gates
outcomes
sealed holdout
```

## Objeto Por Objeto

| Objeto | Responde | No responde |
| --- | --- | --- |
| `data` | que fuente existe y con que calidad | que operar |
| `scanner_candidate` | donde mirar | que estado completo habia |
| `market_state` | que sabia TSIS legalmente en `t` | que outcome ocurrio |
| `event_state` | que estado aplica a un evento/probe/ventana | que accion tomar |
| `sampling_probe` | como muestrear fenomenos posibles | que evento esta validado |
| `event_family_candidate` | que familia empirica parece existir | si hay edge operativo |
| `outcome` | que paso despues | que decision era optima |
| `research_experiment` | que pregunta se ejecuta y como | que conocimiento queda validado |
| `evidence` | que se observo bajo ese experimento | que se debe operar |
| `knowledge_object` | que conclusion candidata existe | produccion automatica |
| `validated_knowledge` | que sobrevivio validacion | ejecucion directa sin componente |
| `strategy` | que respuesta operativa se propone | si el fenomeno es real |
| `decision_model` | que accion tomar bajo constraints | cambiar la verdad historica |
| `execution_model` | si una decision era ejecutable | inventar edge |
| `alphaevolve` | proponer candidate experiments/variantes | validar conocimiento |

## Autoridad Por Area

```text
Filosofia / constitucion epistemologica
-> C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY

Laboratorio operativo transversal
-> C:/TSIS_Data/00_TSIS_Lab

Data Foundation / outputs gobernados SmallCaps
-> C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations

Investigacion y backtest clasico SmallCaps
-> C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research
-> C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs

Outputs pesados / datasets / materializaciones
-> E:/TSIS/data

Autonomous Research / AlphaEvolve
-> C:/TSIS_Data/00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS

Trading systems / event library / strategy research
-> C:/TSIS_Data/00_CTO/13_TRADING_SYSTEMS
```

`01_TSIS_backtest_SmallCaps` no queda reducido a proveedor ni a adapter. Es el modulo operativo SmallCaps: foundations, investigacion, event discovery, feature engine, backtests clasicos, strategy research, builders, validators y datos gobernados.

`00_TSIS_Lab` define la estructura transversal de experimento que puede usar SmallCaps, otros modulos, humanos o AlphaEvolve.

---

# CAPA 0 - RESEARCH PHILOSOPHY

## Objetivo

Definir como piensa TSIS.

Ruta:

```text
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY
```

Documentos base:

```text
00_MANIFESTO/TSIS_RESEARCH_MANIFESTO.md
01_KNOWLEDGE_MODEL/scientific_discovery_engine.md
01_KNOWLEDGE_MODEL/research_question_to_operational_component_lifecycle.md
02_EXPERIMENTAL_METHOD/research_experiment_principles.md
03_HUMAN_AND_AI_RESEARCHERS/human_and_alphaevolve_common_protocol.md
04_MARKET_SCIENCE_PHILOSOPHY/events_are_discovered_not_assumed.md
05_RESEARCH_GOVERNANCE/anti_overfitting_and_validation_principles.md
```

## Regla

La filosofia no ejecuta experimentos. Gobierna su sentido.

---

# CAPA 1 - DATA FOUNDATION

## Objetivo

Construir datos confiables, auditados, reproducibles y versionados.

Data Foundation responde:

```text
que datos existen?
que calidad tienen?
que significan?
que uso permiten?
que lineage gobierna cada output?
```

No busca edge y no decide trades.

## Autoridad

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations
```

Matriz viva:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
```

## Regla

Data Foundation provee infraestructura. No descubre conocimiento por si sola.

---

# CAPA 2 - CANONICAL STATE / EVENT STATE / OUTCOMES

## Objetivo

Construir `X` legal as-of y `Y` separado.

```text
market_state / event_state = X
outcomes = Y
```

## Autoridad CTO

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
```

## Autoridad operativa

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
```

## Estado alcanzado a 2026-07-05

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded scoped E-root = DONE not official
market_state intradia quote-guarded controlled = DONE
intraday event candidates quote-guarded controlled = DONE
event_windows intradia controlled = DONE
event_state intradia controlled = DONE
outcomes intradia separados controlled = DONE
event_research_design_contract_v0_1 = DONE
00_TSIS_Lab research experiment skeleton = DONE
```

## Regla

Las tablas de estado no son el laboratorio completo.

Son la base observable sobre la que los experimentos trabajan.

---

# CAPA 3 - RESEARCH EXPERIMENT PIPELINE

## Objetivo

Convertir preguntas cientificas en ejecuciones reproducibles.

Ruta:

```text
C:/TSIS_Data/00_TSIS_Lab
```

Contratos iniciales:

```text
01_contracts/research_experiment_contract_v0_1.md
01_contracts/research_experiment_execution_protocol_v0_1.md
01_contracts/parameter_sweep_protocol_v0_1.md
01_contracts/scientific_validation_pipeline_contract_v0_1.md
01_contracts/knowledge_object_promotion_contract_v0_1.md
```

## Flujo

```text
Research Question
-> experiment.yaml
-> preflight
-> execution
-> evidence report
-> promotion recommendation
```

## Primer experimento semilla

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Lectura correcta:

```text
+50% = sampling_probe_human_seed
30m = sampling_window_controlled_seed
```

No son evento ni ventana validados.

---

# CAPA 4 - EVENT DISCOVERY / EVENT RESEARCH

## Objetivo

Descubrir fenomenos repetibles antes de convertirlos en eventos validados.

Flujo correcto:

```text
sampling_probe
-> parameter_sweep
-> exploratory_statistics
-> event_family_candidate
-> validation_protocol
-> validated_event_definition
```

## Regla

La Event Library no debe asumir que todo evento ya esta definido.

Antes de una `validated_event_definition` puede haber:

```text
sampling_probe
sampling_window
parameter_grid
exploratory_event_statistics
event_family_candidate
```

---

# CAPA 5 - OUTCOME RESEARCH

## Objetivo

Medir que paso despues sin contaminar `X`.

Outcome Research responde:

```text
que hizo el mercado despues?
```

No responde:

```text
que debia hacer el trader?
```

## Regla

Outcomes son `Y`, nunca features pre-evento.

Labels ML y rewards RL requieren contratos propios.

---

# CAPA 6 - EVIDENCE / KNOWLEDGE OBJECTS

## Objetivo

Convertir resultados de experimentos en evidencia y, si procede, conocimiento candidato.

Flujo:

```text
exploratory_result
-> candidate_phenomenon
-> event_family_candidate
-> representation_candidate
-> transition_candidate
-> policy_candidate
-> validated_knowledge
```

## Regla

Ningun resultado se promueve solo por buen score.

Debe pasar por:

```text
coverage
quality
leakage gates
baseline comparison
parameter sensitivity
out-of-sample / walk-forward si aplica
selection bias accounting
complexity penalty
lineage reproducible
```

---

# CAPA 7 - EVALUATION SYSTEMS

## Objetivo

Separar evaluacion exploratoria de evaluacion bloqueada.

```text
exploratory evaluator = ayuda a descubrir estructura
locked evaluator = valida candidatos promovidos sin cambiar reglas
sealed holdout = evidencia final no reutilizable durante busqueda
```

## Regla

El generador no puede modificar al juez.

Pero no se bloquea un juez sobre un fenomeno que aun no esta definido.

Primero:

```text
experimentos exploratorios
-> evidence
-> event_family_candidate / knowledge_object
```

Despues:

```text
evaluator_contract
-> locked evaluators
```

---

# CAPA 8 - STRATEGY / BACKTEST / DECISION / EXECUTION

## Objetivo

Convertir conocimiento validado en componentes operativos.

`01_TSIS_backtest_SmallCaps` sigue siendo el lugar natural para backtest clasico SmallCaps, investigacion operativa y estrategia SmallCaps.

```text
validated event / state representation / policy hypothesis
-> strategy candidate
-> backtest clasico
-> robustness
-> execution realism
-> promotion review
```

## Regla

Una estrategia no puede redefinir datos, estado, evento validado ni outcome.

---

# CAPA 9 - ML / OFFLINE RL

## Objetivo

Consumir estados, outcomes, knowledge objects y splits gobernados.

ML responde:

```text
que es probable que ocurra?
```

RL responde:

```text
que accion tomar bajo constraints?
```

## Regla

ML/RL no inventan source of truth.

---

# CAPA 10 - EVOLUTION SYSTEMS / ALPHAEVOLVE

## Objetivo

Proponer candidate experiments, variantes, representaciones, detectores o politicas.

AlphaEvolve no es el destino final de la cadena.

Es un generador posible dentro del laboratorio.

## Puede proponer

```text
sampling probes
parameter grids
reference functions
window definitions
representation builders
event detectors
transition candidates
policy candidates
```

## No puede decidir

```text
validated knowledge
production readiness
truth of state
truth of outcome
lineage rewrite
leakage gate disable
quality gate disable
sealed holdout reuse
```

## Regla

```text
same experiment object
same execution protocol
same validation pipeline
```

Un experimento generado por AlphaEvolve y uno propuesto por un humano compiten bajo el mismo contrato.

---

# CAPA 11 - SHADOW LIVE / LIVE OPERATION

## Objetivo

Llevar componentes validados a operacion o shadow sin romper semantica historica.

Live puede producir telemetria y feedback.

No puede redefinir silenciosamente upstream.

---

# Ruta De Implementacion Vigente

## Paso 1 - Mantener Data Foundation viva

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

## Paso 2 - Mantener State/Event/Outcome como base observable

```text
market_state/event_state = X
outcomes = Y
```

## Paso 3 - Usar 00_TSIS_Lab para experimentos

```text
research_experiment_contract
experiment.yaml
parameter_sweep_protocol
scientific_validation_pipeline
```

## Paso 4 - Ejecutar primer experimento semilla

```text
EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Objetivo:

```text
estudiar historicamente movimientos intradia fuertes sin asumir que +50% es evento validado
```

## Paso 5 - Producir evidencia exploratoria

```text
parameter_sweep_results
exploratory_event_statistics_report
promotion_recommendation
```

## Paso 6 - Promover solo lo que sobreviva

```text
candidate_knowledge_object
validated_knowledge
operational_component_candidate
```

## Paso 7 - Solo entonces bloquear evaluadores

```text
evaluator_contract
locked_evaluators
sealed_holdout discipline
```

## Paso 8 - ML/RL/AlphaEvolve/Live bajo contratos

AlphaEvolve puede entrar antes como generador de experimentos, pero no como autoridad de validacion.

---

# Lecturas Obligatorias Por Tipo De Trabajo

## Si toca filosofia de investigacion

```text
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY/README.md
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY/01_KNOWLEDGE_MODEL/scientific_discovery_engine.md
```

## Si toca experimentos

```text
C:/TSIS_Data/00_TSIS_Lab/README.md
C:/TSIS_Data/00_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md
C:/TSIS_Data/00_TSIS_Lab/01_contracts/scientific_validation_pipeline_contract_v0_1.md
```

## Si toca market/event state

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
```

## Si toca AlphaEvolve

```text
C:/TSIS_Data/00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/README.md
C:/TSIS_Data/00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY/03_HUMAN_AND_AI_RESEARCHERS/human_and_alphaevolve_common_protocol.md
C:/TSIS_Data/00_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md
```

# Regla Final

TSIS acepta conocimiento solo cuando puede explicar:

```text
de que datos viene
que estado legal observo
que experimento ejecuto
que evidencia produjo
que validacion paso
que conocimiento resulto
que componente operativo habilita
```

Todo lo demas es hipotesis, investigacion o ruido.




