# TSIS Lab Architecture v2

Fecha de creacion: 2026-06-30
Estado: arquitectura_v2_candidate
Origen: revision de `TSIS_LAB_ARCHITECTURE.md` v1 del 2026-06-18
Owner layer: `00_CTO`

## Proposito

Este documento es la version v2 de la arquitectura de laboratorio TSIS.

No borra ni reemplaza fisicamente a:

```text
TSIS_LAB_ARCHITECTURE.md
```

La v1 conserva valor historico porque promovio la arquitectura inicial desde:

```text
00_private/arquitectura.md
```

La v2 incorpora el estado real alcanzado durante junio de 2026:

- Data Foundation ya no es solo una lista objetivo; tiene contratos, matrices,
  builders, materializaciones y estados de madurez.
- `daily_scanner_candidates_table` existe como capa de candidate selection,
  no como estado ni senal.
- `market_state` y `event_state` se han convertido en el eje cientifico del
  pipeline.
- existen candidatos controlados de `market_state_table` y `event_state_table`,
  pero no promocion institucional completa.
- Graphify tiene protocolo propio y no debe confundirse con source of truth.
- Strategy Library ya esta en modo event-first, con DAS como research
  experimental y no como contrato de estado institucional.

## Estado de autoridad

Esta v2 es una arquitectura CTO.

No sustituye:

- documentos raiz;
- contratos de `01_foundations`;
- schemas canonicos;
- validators;
- registries;
- manifests de datasets;
- policies de consumo;
- changelogs de modulo.

Regla:

```text
00_CTO disena y organiza.
01_foundations gobierna outputs operativos de Data Foundation.
Los documentos raiz gobiernan reglas transversales.
```

## Tesis v2

TSIS no es un backtester ni una coleccion de estrategias.

TSIS es una maquina cientifica para reconstruir, evaluar y aprender estados de
mercado en microcaps y small caps.

La pregunta central no es:

```text
Funciona esta estrategia?
```

La pregunta central es:

```text
Que estaba ocurriendo en el mercado, que sabia TSIS legalmente en ese instante,
que evento o transicion de estado representaba, que decision era defendible y
como se degrada esa decision bajo ejecucion realista?
```

## Cadena logica vigente

La cadena logica v2 es:

```text
Data Foundation
-> Scanner Candidate Selection
-> Market State Representation
-> Event Library
-> Event Engine
-> Event State
-> Outcome Research
-> Strategy Library
-> Strategy Research
-> Edge Hypotheses
-> Pattern Discovery
-> Cluster Research
-> Machine Learning
-> Decision Models / Offline RL
-> Execution Models
-> Evaluation Systems
-> Evolution Systems / AlphaEvolve
-> Shadow Live / Live Operation
```

Esta cadena es logica y funcional. No significa que cada capa deba vivir como
carpeta top-level en `00_CTO`.

## Principio central

```text
dato != candidato != estado != evento != outcome != estrategia != decision != ejecucion != evolucion
```

Definiciones minimas:

| Objeto | Responde | No responde |
| --- | --- | --- |
| `data` | que fuente existe y con que calidad | que operar |
| `scanner_candidate` | donde mirar | que estado completo habia |
| `market_state` | que sabia TSIS legalmente en `t` | que outcome ocurrio |
| `event_state` | que estado aplica a un evento/candidato | que accion tomar |
| `event` | que fenomeno ocurrio | como operarlo |
| `outcome` | que paso despues | que decision era optima |
| `strategy` | que respuesta operativa se propone | si hay edge robusto |
| `decision_model` | que accion tomar bajo constraints | cambiar la verdad historica |
| `execution_model` | si la decision era ejecutable | inventar edge |
| `evolution_system` | como explorar variantes | modificar evaluadores bloqueados |

## Autoridad por area

```text
Data Foundation outputs
-> autoridad operativa: 01_TSIS_backtest_SmallCaps/01_foundations
-> autoridad CTO: 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS

Scanner Candidate Selection
-> autoridad operativa: 01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
-> autoridad CTO: 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION

Market State Representation
-> autoridad CTO: 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
-> autoridad operativa objetivo: 01_foundations market_state/event_state contracts

Trading knowledge architecture
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS

Event Library
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY

Event Engine Model
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL

Outcome Research
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH

Strategy Library
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY

Machine Learning doctrine
-> autoridad CTO: 00_CTO/08_MACHINE_LEARNING
-> implementacion futura: modulo 01 o modulo 03 segun caso

Decision Models / Offline RL
-> autoridad metodologica: 00_CTO/09_REINFORCEMENT_LEARNING y 00_CTO/13_TRADING_SYSTEMS/09_DECISION_MODELS
-> implementacion futura: 03_TSIS_Offline_RL

Execution Models
-> autoridad CTO: 00_CTO/13_TRADING_SYSTEMS/08_EXECUTION_MODELS

Evolution Systems / AlphaEvolve / OpenEvolve
-> autoridad CTO: 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS y 00_CTO/13_TRADING_SYSTEMS/10_EVOLUTION_SYSTEMS
-> sandbox y gating: 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE

Graphify
-> autoridad de protocolo: 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
-> cola: 00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

---

# CAPA 1 - DATA FOUNDATION

## Objetivo

Construir una representacion fiable, auditada, reproducible y versionada del
mercado.

Data Foundation no busca edge y no decide trades.

Su funcion es responder:

```text
Que datos existen?
Que calidad tienen?
Que significan?
Que usos permiten?
Que usos prohiben?
Que lineage y version gobierna cada output?
```

## Autoridad

La autoridad operativa vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

La matriz viva de estado es:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
```

La v2 no debe duplicar esa matriz como source of truth. Debe apuntar a ella.

## Output families vigentes

| Output family | Rol | Estado general a 2026-06-30 |
| --- | --- | --- |
| `instrument_master_v0_1` | identidad y universo LT1B | validated for declared scope |
| `market_calendar_v0_1` | sesiones XNYS | validated for declared scope |
| `expected_data_calendar_v0_1` | denominador de cobertura esperada | validated for declared scope |
| `corporate_actions_table_v0_1` | splits, dividends, ticker changes | validated for declared scope |
| `dataset_certification_matrix_v0_1` | quality gates por familia | validated for declared scope |
| `master_daily_table_v0_1` | contexto diario multi price-view | validated for declared scope |
| `master_intraday_bar_table_v0_1` | 1m scoped split-normalized cases | scoped pilot, not full universe |
| `microstructure_features_table_v0_1` | prueba seed quote/trade window | seed state sample |
| `microstructure_features_table_v0_2_candidate` | 50 controlled halt windows | controlled candidate, not promoted |
| `market_state_table_v0_1_candidate` | controlled state snapshots | controlled candidate, not promoted |
| `event_state_table_v0_1_candidate` | controlled event-state snapshots | controlled candidate, not promoted |
| `halts_table_v0_1` | halts and suspensions | validated for declared scope |
| `event_windows_table_v0_1` | halt-derived event windows | validated for declared scope |
| `outcomes_table_v0_1` | daily post-event outcomes | validated for declared scope |
| `fundamentals_asof_table_v0_1` | filing-date-aware fundamentals | validated for declared scope |
| `news_context_table_v0_1` | published-time news context | validated for declared scope |
| `short_context_table_v0_1` | short interest/volume context | validated for declared scope, not borrow/SSR |
| `short_sale_constraints_table` | SSR/borrow/locate constraints | target contract, source blocked |
| `regime_context_table_v0_1` | session-level regime proxies | validated for declared scope |
| `daily_scanner_candidates_table_v0_1` | scanner candidates / denominators | builder + controlled replay, not official E-root |

## Regla de interpretacion

`validated_for_declared_scope` no significa:

```text
full universe
ML/RL-ready
execution-ready
institutional market state
```

Significa que el output cumple su scope declarado y debe consumirse bajo su
policy.

## Data Foundation no-goals

Data Foundation no debe:

- decidir trades;
- redefinir estrategias;
- esconder labels;
- esconder outcomes;
- mezclar reward con features;
- declarar full universe cuando el output es scoped;
- usar scanner rows como `market_state`;
- usar short interest como borrow/locate/SSR;
- modificar raw data sin nueva version o overlay gobernado.

---

# CAPA 1A - SCANNER CANDIDATE SELECTION

## Objetivo

Responder:

```text
Que instrumentos merecian ser mirados bajo una definicion de scanner,
en esta fecha/as-of, y por que razones?
```

El scanner decide donde mirar.

No decide que operar.

## Autoridad

CTO:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION
```

Operativa:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

## Definicion activa v0.2

```text
base_in_play_universe_scanner_v0_2
  = base_eligible_smallcap_denominator
trade_station_like_profile_v0_2
relative_volume_profile_v0_2
percent_change_profile_v0_2
dollar_volume_tradability_profile_v0_2
das_research_profile_v0_2
```

`base_in_play_universe_scanner_v0_2` define la poblacion elegible observable:

```text
common_stock = true
market_cap_usd < 100000000
0.5 < last_price <= 20
data_quality in usable/review
```

`trade_station_like_profile_v0_2` reconstruye visibilidad operativa humana
como perfil sobre el universo base, no como universo separado.

Los perfiles de relative volume, percent change, tradability y DAS research
permiten estudiar timing, atencion, contrapartida y frontside sin convertir
esas variables en filtros universales prematuros.

Precision semantica:

- los perfiles son paralelos, no filtros secuenciales;
- `relative_volume_profile_v0_2` debe significar aceleracion de volumen
  intradia/as-of antes de promocion;
- `percent_change_profile_v0_2` debe exigir minimo declarado antes de top-N;
- `dollar_volume_tradability_profile_v0_2` es tradability, no alpha;
- `das_research_profile_v0_2` es seed provisional; DAS real debe vivir como
  overlay de estrategia o tabla experimental propia.

## Regla

```text
daily_scanner_candidates_table
-> candidate set / denominator
-> strategy overlays when needed
-> market_state_table builder
-> event_state_table builder
```

Queda prohibido:

- entrenar ML/RL directamente sobre scanner rows;
- tratar scanner rows como `event_state`;
- llamar estrategia a una aparicion de scanner;
- meter outcome, PnL, fills o rewards en scanner.

---

# CAPA 1B - MARKET STATE REPRESENTATION

## Objetivo

Responder:

```text
Que sabia TSIS legalmente sobre este instrumento, en este instante, con que
fuentes, calidad, cutoff temporal y restricciones de consumo?
```

Market State es el eje que conecta:

```text
Data Foundation
Scanner Candidate Selection
Event Engine
Outcome Research
ML/RL
Decision Models
Execution Models
AlphaEvolve
```

## Autoridad CTO

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
```

## Objetos

```text
market_state_table
event_state_table
```

Estado actual:

```text
contract stack exists
controlled candidate samples exist
institutional full market_state_table does not exist yet
institutional full event_state_table does not exist yet
```

## Componentes de estado

Un estado puede componer, bajo reglas as-of:

- identidad del instrumento;
- calendario/sesion;
- scanner lineage;
- contexto diario;
- contexto intradia;
- microestructura;
- halts;
- fundamentals;
- news/catalyst;
- short context;
- short sale constraints cuando existan fuentes;
- regime context;
- quality flags;
- source lineage;
- prohibited downstream use flags.

## Regla

```text
componentes de estado != estado institucional
```

Una tabla parcial puede ser correcta y aun no ser suficiente para entrenar
ML/RL.

---

# CAPA 2 - EVENT LIBRARY / EVENT RESEARCH

## Objetivo

Definir fenomenos observables del mercado independientes de la decision
operativa.

Un evento responde:

```text
Que esta ocurriendo?
```

No responde:

```text
Que hago?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY
```

## Regla

Si una definicion contiene entrada, stop, target, sizing o gestion parcial, no
es evento. Es estrategia o execution model.

## Relacion con scanner y state

El scanner puede generar candidatos.

El market/event state reconstruye el estado observable.

La Event Library define el fenomeno que puede detectarse sobre ese estado.

---

# CAPA 3 - EVENT ENGINE

## Objetivo

Transformar estados y datos auditados en eventos estructurados.

El Event Engine responde:

```text
Que evento ocurrio o que candidato de evento se activo?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL
```

## Inputs

```text
event_definitions
daily_scanner_candidates_table when used as candidate seed
market_state_table / event_state_table when available
master_daily_table
master_intraday_bar_table
microstructure_features_table
halts_table
event_windows_table
instrument_master
market_calendar
quality policies
```

## Outputs objetivo

```text
event_table
event_candidate_table
event_version_manifest
detection_manifest
```

## Regla

El Event Engine no toma decisiones de trading.

---

# CAPA 4 - OUTCOME RESEARCH

## Objetivo

Medir que paso despues de eventos o candidatos de evento.

Outcome Research responde:

```text
Que hizo el mercado despues?
```

No responde:

```text
Que habria hecho el trader?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH
```

## Inputs

```text
event_table / event_windows_table
master_daily_table
master_intraday_bar_table when legal
halts_table
market_calendar
quality flags
```

## Outputs

```text
outcomes_table
outcome_labels
outcome_horizon_manifest
label_separation_policy
```

## Regla

Outcome labels no son rewards RL hasta que exista contrato de reward.

---

# CAPA 5 - STRATEGY LIBRARY

## Objetivo

Definir respuestas operativas propuestas frente a eventos.

Una estrategia responde:

```text
Que hago frente a este evento/estado?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY
```

## Estado actual relevante

DAS existe como investigacion long-side experimental.

La ruta correcta es:

```text
daily_scanner_candidates_table
-> das_candidate_state_table_experimental
-> future event_state / market_state integration
```

DAS no debe escribir directamente un `market_state` institucional.

## Regla

Las estrategias no pueden redefinir eventos ni datasets upstream.

---

# CAPA 6 - STRATEGY RESEARCH

## Objetivo

Evaluar si una estrategia sobrevive bajo:

- datos gobernados;
- eventos/estados definidos;
- costes;
- slippage;
- capacity;
- halts;
- borrow/SSR cuando aplique;
- walk-forward;
- robustness checks.

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/04_STRATEGY_RESEARCH
```

## Inputs

```text
event_table
event_state_table
outcomes_table
strategy_definition
execution_constraints
cost_model
risk_policy
```

## Outputs

```text
strategy_results
robustness_report
failure_mode_report
promotion_candidate_report
```

---

# CAPA 7 - EDGE HYPOTHESES

## Objetivo

Explicar por que podria existir edge antes de optimizar una estrategia.

Una hipotesis de edge conecta:

```text
fenomeno observable
-> mecanismo de mercado
-> consecuencia esperada
-> restricciones de ejecucion
-> falsificacion
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/05_EDGE_HYPOTHESES
```

## Regla

Una hipotesis de edge no es una equity curve.

---

# CAPA 8 - PATTERN DISCOVERY

## Objetivo

Buscar patrones en eventos, estados y outcomes sin convertirlos todavia en
estrategias.

Pattern Discovery responde:

```text
Que tienen en comun los mejores o peores eventos?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/06_PATTERN_DISCOVERY
```

## Inputs

```text
event_state_table
outcomes_table
cluster_table when available
quality flags
```

## Regla

Pattern Discovery produce conocimiento e hipotesis, no decisiones.

---

# CAPA 9 - CLUSTER RESEARCH

## Objetivo

Agrupar eventos por comportamiento y contexto.

Cluster Research responde:

```text
Existen familias distintas de eventos/estados?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/07_CLUSTER_RESEARCH
```

## Regla

No agrupamos tickers como identidad primaria. Agrupamos comportamiento de
eventos/estados bajo contexto.

---

# CAPA 10 - MACHINE LEARNING

## Objetivo

Estimar probabilidades sobre outcomes futuros dados estados/eventos.

Machine Learning responde:

```text
Que es probable que ocurra?
```

No responde:

```text
Que accion debo tomar?
```

## Autoridad CTO

```text
00_CTO/08_MACHINE_LEARNING
```

## Inputs validos

```text
event_state_table / market_state_table promoted or candidate with explicit limits
outcome labels with temporal separation
quality flags
purged/walk-forward splits
```

## Prohibido

- entrenar directamente sobre scanner rows como estado final;
- mezclar features y labels;
- usar full-session values antes de su cutoff;
- usar candidate tables como institucionales sin promotion review.

---

# CAPA 11 - DECISION MODELS / OFFLINE RL

## Objetivo

Aprender politicas de decision bajo constraints.

Decision Models responden:

```text
Que accion deberia tomar ahora, si alguna?
```

## Autoridad CTO

```text
00_CTO/09_REINFORCEMENT_LEARNING
00_CTO/13_TRADING_SYSTEMS/09_DECISION_MODELS
```

## Inputs

```text
market_state / event_state
model probabilities
execution constraints
risk state
portfolio context
behavioral data when available
```

## Regla

RL no inventa source of truth. RL aprende sobre estados ya gobernados.

---

# CAPA 12 - EXECUTION MODELS

## Objetivo

Convertir decisiones teoricas en acciones realistas bajo friccion de mercado.

Execution Models responden:

```text
Era ejecutable esta decision?
Con que fill, slippage, partial fill, latency, halt risk y borrow constraint?
```

## Autoridad CTO

```text
00_CTO/13_TRADING_SYSTEMS/08_EXECUTION_MODELS
```

## Inputs

```text
quotes
trades
spread
liquidity
halts
borrow / locate / SSR when available
latency assumptions
risk policy
```

## Regla

Una senal correcta puede ser un trade inviable.

---

# CAPA 13 - EVALUATION SYSTEMS

## Objetivo

Definir evaluadores bloqueados, fitness functions, validation gates y promotion
criteria antes de permitir generacion automatica de candidatos.

## Autoridad CTO

```text
00_CTO/05_EVALUATION_SYSTEMS
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE
```

## Regla

El generador no puede modificar al juez.

---

# CAPA 14 - EVOLUTION SYSTEMS / ALPHAEVOLVE

## Objetivo

Evolucionar definiciones, features, filtros, estrategias o politicas solo
cuando existan evaluadores bloqueados y datasets gobernados.

## Autoridad CTO

```text
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS
00_CTO/13_TRADING_SYSTEMS/10_EVOLUTION_SYSTEMS
```

## Inputs minimos

```text
event_table / event_state_table
outcomes_table
locked_evaluators
fitness functions
constraints
candidate archive
lineage
```

## Regla

AlphaEvolve no es punto de partida. Es una capa posterior.

---

# CAPA 15 - SHADOW LIVE / LIVE OPERATION

## Objetivo

Llevar estructuras validadas a operacion en tiempo real sin romper la
semantica historica.

## Relacion modular

```text
01_TSIS_backtest_SmallCaps
-> research, backtest, historical replay, contracts

02_TSIS_webSocket_SmallCaps
-> live ingestion, streaming state, event routing, monitoring

03_TSIS_Offline_RL
-> offline learning sobre estados gobernados
```

## Regla

Live puede producir telemetria y feedback, pero no redefine silenciosamente
semantica upstream.

---

# Graphify y memoria semantica

Graphify es mapa, no autoridad.

Autoridad:

```text
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Regla:

```text
Git conserva cambios.
Graphify se refresca por hitos semanticos.
```

La v2 debe anotarse en la cola Graphify. No debe escribirse manualmente
`graphify-out/graph.json`.

---

# Ruta de implementacion vigente

## Paso 1 - Mantener Data Foundation como autoridad viva

Ruta:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

Condicion:

```text
status matrix + contracts + schemas + registries + policies + validators + manifests + evidence
```

## Paso 2 - Ampliar scanner candidate selection

Ruta CTO:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION
```

Ruta operativa:

```text
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

Siguiente trabajo:

- validator suite completa;
- replay amplio candidato en E-root `candidate_replays`;
- no promocionar como estado.

## Paso 3 - Construir market_state / event_state gobernados

Ruta CTO:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
```

Ruta operativa:

```text
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
```

Siguiente trabajo:

- ampliar candidatos controlados;
- declarar ventanas;
- validar anti-leakage;
- integrar componentes as-of;
- no usar full-universe claims falsos.

## Paso 4 - Gobernar Event Library y Event Engine

Rutas:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY
00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL
```

## Paso 5 - Separar outcomes, estrategias y decisiones

Rutas:

```text
00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY
00_CTO/13_TRADING_SYSTEMS/09_DECISION_MODELS
```

## Paso 6 - Construir evaluadores antes de generadores

Rutas:

```text
00_CTO/05_EVALUATION_SYSTEMS
00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE
```

## Paso 7 - Solo despues, ML/RL y Evolution Systems

Condicion:

```text
states + outcomes + execution realism + validators + locked evaluators
```

---

# Mapeo funcional a carpetas actuales

```text
Data Foundation
-> 01_TSIS_backtest_SmallCaps/01_foundations
-> 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS

Scanner Candidate Selection
-> 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION
-> 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md

Market State Representation
-> 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
-> 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md

Event Library
-> 00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY

Event Engine
-> 00_CTO/13_TRADING_SYSTEMS/01_EVENT_ENGINE_MODEL

Outcome Research
-> 00_CTO/13_TRADING_SYSTEMS/02_OUTCOME_RESEARCH

Strategy Library
-> 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY

Strategy Research
-> 00_CTO/13_TRADING_SYSTEMS/04_STRATEGY_RESEARCH

Edge Hypotheses
-> 00_CTO/13_TRADING_SYSTEMS/05_EDGE_HYPOTHESES

Pattern Discovery
-> 00_CTO/13_TRADING_SYSTEMS/06_PATTERN_DISCOVERY

Cluster Research
-> 00_CTO/13_TRADING_SYSTEMS/07_CLUSTER_RESEARCH

Execution Models
-> 00_CTO/13_TRADING_SYSTEMS/08_EXECUTION_MODELS

Decision Models
-> 00_CTO/13_TRADING_SYSTEMS/09_DECISION_MODELS

Evolution Systems
-> 00_CTO/13_TRADING_SYSTEMS/10_EVOLUTION_SYSTEMS
-> 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS

Squeeze Research
-> 00_CTO/13_TRADING_SYSTEMS/11_SQUEEZE_RESEARCH

Discretionary Frameworks
-> 00_CTO/13_TRADING_SYSTEMS/90_DISCRETIONARY_FRAMEWORKS

Experimental
-> 00_CTO/13_TRADING_SYSTEMS/99_EXPERIMENTAL

Machine Learning doctrine
-> 00_CTO/08_MACHINE_LEARNING

Offline RL doctrine
-> 00_CTO/09_REINFORCEMENT_LEARNING

Graphify governance
-> 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
-> 00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

---

# Lecturas obligatorias por tipo de trabajo

Si el trabajo toca Data Foundation outputs:

```text
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
```

Si el trabajo toca scanner:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

Si el trabajo toca market/event state:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
```

Si el trabajo toca estrategias:

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
```

Si el trabajo toca Graphify:

```text
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

---

# Regla final

La arquitectura TSIS Lab v2 debe hacer imposible confundir:

```text
source data
candidate selection
market state
event state
event definition
outcome
strategy
decision
execution
evaluation
evolution
live operation
```

Si una carpeta, documento, output, notebook, builder o agente mezcla esos
niveles sin contrato explicito, debe corregirse antes de tratarse como
arquitectura activa.
