# Market State Representation Contract v0.1

Fecha: 2026-06-25
Estado: candidate_policy
Owner layer: `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION`
Aplica a: TSIS Lab, SmallCaps, Event Engine, ML, Decision Models, Offline RL,
Execution Models, Evolution Systems

## 1. Tesis

TSIS no debe entenderse solo como un backtester.

TSIS debe entenderse como una maquina cientifica para reconstruir, evaluar y
aprender estados de mercado alrededor de eventos.

La unidad central no es una vela, una tabla ni una estrategia.

La unidad central es:

```text
market_state(t, instrument, event_context, data_availability_cutoff)
```

Un `market_state` es una representacion temporalmente legal, auditada y
defendible de lo que el sistema podia saber en un instante sobre un instrumento,
un evento o un candidato de evento.

El `market_state` debe derivarse de la data de mercado real descargada, pero no
debe copiar toda la raw data sin estructura.

Regla:

```text
downloaded market data
-> audited raw/source truth
-> derived state components
-> market_state / event_state
-> ML/RL/decision/evaluation
```

La raw data conserva la verdad completa.

El estado conserva una representacion compacta, legal en el tiempo y suficiente
para el consumidor declarado.

Fundamento cientifico directo:

- Offline RL aprende politicas desde datasets historicos, pero requiere entender
  sus limitaciones y cobertura:
  `Levine et al. (2020) - https://arxiv.org/abs/2005.01643`.
- Offline RL sufre distribution shift entre dataset y politica aprendida:
  `Kumar et al. (2020) - https://arxiv.org/abs/2006.04779`.
- DeepLOB modela LOB como estructura espacio-temporal, no como OHLCV plano:
  `Zhang, Zohren, Roberts (2018/2020) - https://arxiv.org/abs/1808.03668`.
- LOBFrame muestra que accuracy predictiva en LOB no implica senal accionable:
  `Briola, Bartolucci, Aste (2024) - https://arxiv.org/abs/2403.09267`.
- JAX-LOB muestra que RL/execution sobre LOB requiere simulacion escalable:
  `Frey et al. (2023) - https://arxiv.org/abs/2308.13289`.
- AlphaEvolve/FunSearch muestran que busqueda automatica requiere evaluadores:
  `Novikov et al. (2025) - https://arxiv.org/abs/2506.13131` y
  `Romera-Paredes et al. (2024) - https://www.nature.com/articles/s41586-023-06924-6`.
- Causal ML justifica representar mecanismos, no solo correlaciones:
  `Scholkopf (2019/2022) - https://arxiv.org/abs/1911.10500`.

Lectura obligatoria de estas referencias:

```text
No hay un paper que demuestre TSIS como sistema completo.
Si hay evidencia directa de los bloques cientificos que obligan esta arquitectura:

- RL formaliza decision sobre estados.
- Offline RL exige datasets historicos gobernados.
- Distribution shift exige cobertura y OOD guards.
- LOB modeling exige estructura espacio-temporal.
- LOB forecasting exige separar accuracy de accionabilidad.
- LOB simulation exige raw replay y mecanismos de mercado.
- Program search exige evaluadores bloqueados.
- Causal ML exige mecanismos, no solo correlaciones.
```

Ese estado alimenta:

```text
Event Engine
-> event_table
-> outcome_table
-> ML probability models
-> Decision Models / Offline RL
-> Execution Models
-> Evolution Systems / AlphaEvolve
```

## 2. Por Que Existe Este Contrato

Las tablas de Data Foundation no existen para ser un fin en si mismas.

Existen para responder, de forma reproducible:

```text
Que instrumento es?
Que dia y sesion es?
Que datos estaban disponibles?
Que calidad tiene cada input?
Que contexto diario habia?
Que evolucion intradia habia?
Que microestructura habia?
Que catalyst o alerta existia?
Que regimen rodea el evento?
Que restricciones de ejecucion habia?
Que no se podia saber todavia?
```

Sin una definicion fuerte de estado:

- ML aprende proxies fragiles;
- RL optimiza sobre observaciones incompletas;
- AlphaEvolve optimiza basura contra evaluadores mal definidos;
- backtesting confunde evento, estrategia y resultado;
- live trading reacciona sin saber que parte del mercado esta viendo.

### 2.1 Estados Actuales Vs Estados Objetivo

TSIS ya esta creando piezas necesarias para estados de mercado, pero eso no
significa que exista todavia un `market_state` institucional completo.

La distincion obligatoria es:

```text
componentes de estado != market_state institucional
```

Los componentes actuales permiten reconstruir partes del estado. El
`market_state` objetivo sera el objeto canonico que componga esos componentes
con reloj causal, calidad, lineage, leakage boundaries y schema estable.

| Tipo | Ejemplos | Estado conceptual | Puede entrenar ML/RL directamente? |
|---|---|---|---|
| Raw data | quotes, trades, daily, 1m, halts, reference, financial, news | Materia prima auditada o en auditoria | No |
| Componentes foundation | `instrument_master`, `market_calendar`, `master_daily_table`, `master_intraday_bar_table`, `dataset_certification_matrix`, `data_quality_report` | Partes gobernadas o en construccion del estado | Solo si el consumidor respeta contrato y leakage |
| Componentes contextuales | corporate actions, news, filings, real-time alerts, regime indicators, short/borrow context | Overlays causales, informacionales o de regimen | No como features sin corte temporal |
| Componentes microestructurales | quotes/trades-derived spread, depth proxy, tape texture, `microstructure_features_table` | Estado de libro/tape por ventana | Solo scoped; v0.1 no es full-universe |
| `event_state` | estado reconstruido para un evento/candidato de evento | Objeto downstream objetivo | Si tiene schema, lineage, quality gates y leakage checks |
| `market_state` institucional | representacion canonica versionada de lo observable en `t` | Objetivo de este contrato | Si esta promovido, validado y materializado |

Regla:

```text
Una tabla puede ser correcta y aun asi no ser suficiente como estado entrenable.
```

Ejemplo:

- `master_daily_table` puede describir contexto diario.
- `master_intraday_bar_table` puede describir evolucion intradia.
- `microstructure_features_table` puede describir textura quote/trade en una
  ventana.
- `data_quality_report` puede explicar si los inputs son confiables.

Pero ninguno de ellos, por separado, responde:

```text
Que sabia TSIS exactamente sobre este ticker, en este instante, para este
evento, con que calidad, que fuentes y que informacion estaba prohibida?
```

Esa pregunta solo la responde un `market_state` o `event_state` construido bajo
este contrato.

### 2.2 Matriz De Madurez Del Estado

Todo agente debe clasificar cualquier artefacto relacionado con estados en una
de estas categorias:

| Estado | Significado | Uso permitido |
|---|---|---|
| `raw_component` | Fuente fisica o dataset raw | Auditoria, reconstruccion, lineage |
| `audited_component` | Fuente auditada con contratos y quality report | Input para builders gobernados |
| `derived_component` | Tabla derivada de Data Foundation | Contexto parcial de estado |
| `scoped_state_sample` | Estado o feature materializado para muestra/caso | Forense, smoke tests, diseno |
| `event_state_candidate` | Reconstruccion de estado por evento aun no promovida | Research, validacion humana |
| `market_state_candidate` | Estado compuesto con schema preliminar | Prototipo ML/RL bajo constraints |
| `institutional_market_state` | Estado versionado, validado y promovido | Event Engine, ML/RL, live y evaluadores |

Mientras un artefacto no llegue a `institutional_market_state`, no debe
presentarse como base final de entrenamiento ni como source of truth de decision.

### 2.3 Caso Especial: Scanner Candidate Selection

`daily_scanner_candidates_table` tampoco es un `market_state`.

Su rol correcto es:

```text
candidate_selection_component
```

porque responde:

```text
Que instrumentos merecian ser mirados bajo una definicion de scanner,
en esta fecha/as-of, y por que razones?
```

No responde:

```text
Que sabia TSIS exactamente sobre ese instrumento?
Que evento ocurrio?
Que estrategia debe operar?
Que outcome/reward debe asignarse?
```

La documentacion CTO activa vive en:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
```

La autoridad operativa vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_1.md
```

Regla:

```text
El scanner decide donde mirar.
El market_state decide que sabia TSIS en ese momento.
La estrategia decide si ese estado encaja con una hipotesis.
ML/RL no entrena directamente sobre scanner rows.
```

### 2.4 Caso Especial: Microstructure Features Table

`microstructure_features_table_v0_1` no esta mal.

Esta incompleto para el objetivo final.

Su rol correcto es:

```text
scoped_state_sample
```

porque demuestra:

- forma de tabla;
- lineage de quotes/trades;
- hashes de fuentes;
- calculo compacto de features de libro/tape;
- tests contractuales;
- uso de ventanas explicitas.

Pero no demuestra todavia:

- cobertura full-universe;
- cobertura de todos los eventos relevantes;
- E-root oficial de quotes cerrado;
- uso ML/RL primario;
- uso en backtest core;
- uso en execution simulation.

Para dejarlo bien, TSIS debe crear una version posterior que consuma ventanas de
evento gobernadas y fuentes raw oficiales, con cobertura declarada, validators,
evidencia visual/forense y gates de consumo por capa.

La accion correcta no es renombrar v0.1 como completo.

La accion correcta es:

```text
mantener v0.1 como semilla trazable
-> construir v0.2+ con alcance real
-> documentar diferencias
-> validar recomputando desde raw
-> promocionar solo con manifest/changelog
```

## 3. Definicion Canonica

Un estado de mercado en TSIS es:

```text
Market State =
representacion compacta, auditada, versionada y causalmente legal
de todos los observables autorizados necesarios para detectar,
clasificar, comparar o decidir sobre un evento de mercado
en un instante dado.
```

No es:

- raw data;
- un dataframe casual;
- una vela OHLCV aislada;
- una estrategia;
- un setup discrecional;
- un label futuro;
- un reward;
- una prediccion de ML;
- una entrada/salida/stop/target;
- una explicacion narrativa sin schema.

## 4. Separacion No Negociable

```text
Raw data != State
State != Event
Event != Outcome
Outcome != Strategy
Strategy != Decision
Decision != Execution
Execution != Reward
Reward != Fitness
Fitness != Scientific Truth
```

La separacion evita contaminacion semantica.

Ejemplo:

```text
Gap 50% + RVOL 20 + float 3M + offering headline + wide spread
```

puede ser parte del estado.

Pero:

```text
Comprar en pullback VWAP con stop bajo low
```

no es estado. Es estrategia o decision.

## 5. La Maquina Que Aprende En Tiempo Real

La vision TSIS es una maquina que aprende con estados, no una maquina que mira
precios.

En live:

```text
raw/live feeds
-> state builder
-> market_state_t
-> event candidate detector
-> event_state_t
-> policy / risk / execution gate
-> action candidate
-> outcome/reward later
-> archive
-> offline retraining / evaluator update under governance
```

La maquina puede actualizar su estado en segundos o milisegundos.

La maquina no debe modificar retroactivamente:

- datos raw;
- evaluadores;
- event definitions;
- quality gates;
- labels;
- reward functions;

sin versionado, manifest y changelog.

## 6. Estructura Minima De Un Market State

Todo `market_state` promovible debe poder declarar:

```yaml
market_state_id: string
state_version: string
instrument_id: string
ticker: string
observation_time_utc: timestamp
data_availability_cutoff_utc: timestamp
session_date: date
event_clock: string
event_candidate_id: nullable string
event_id: nullable string
source_lineage: dictionary
quality_state: dictionary
feature_domains: dictionary
leakage_boundary: dictionary
promotion_state: string
```

Campos criticos:

- `observation_time_utc`: cuando se observa el mercado.
- `data_availability_cutoff_utc`: ultimo instante legal de informacion.
- `event_clock`: posicion relativa al evento o a la sesion.
- `source_lineage`: datasets, manifests, versions y paths.
- `quality_state`: good/review/bad/scoped/blocked por input.
- `leakage_boundary`: que columnas o fuentes no podian usarse todavia.

## 7. Dominios Del Estado

Un estado completo puede estar compuesto por dominios.

No todos los eventos necesitan todos los dominios, pero todo estado debe declarar
que dominios usa y cuales no.

### 7.1 Identidad / Universo

Fuente esperada:

- `instrument_master`
- `reference/all_tickers`
- ticker events
- delistings
- exchange / market type
- LT1B universe source of truth

Uso:

- impedir survivorship bias;
- resolver ticker remaps;
- evitar mezclar requested ticker con identidad real.

### 7.2 Calendario / Sesion

Fuente esperada:

- `market_calendar`
- expected data calendar
- session clocks

Uso:

- distinguir premarket, regular, after-hours;
- calcular minute index;
- evitar comparar ventanas no equivalentes.

### 7.3 Corporate Actions / Price Semantics

Fuente esperada:

- splits;
- dividends;
- ticker events;
- raw / adjusted / normalized price views.

Uso:

- evitar leer split/dividend como alpha;
- decidir que vista de precio alimenta cada capa.

### 7.4 Contexto Diario

Fuente esperada:

- `master_daily_table`
- daily adjusted;
- daily raw;
- returns/gaps/liquidity daily context.

Uso:

- contexto estructural pre-evento;
- gap size;
- ATR/volatility/liquidity context;
- price regime.

### 7.5 Evolucion Intradia

Fuente esperada:

- `master_intraday_bar_table`
- 1m raw;
- 1m split normalized, cuando aplique y este materializado para el universo.

Uso:

- premarket volume;
- opening drive;
- intraday path;
- event window reconstruction.

### 7.6 Microestructura

Fuente esperada:

- quotes;
- trades;
- `microstructure_features_table`;
- spreads;
- NBBO;
- trade tape;
- event-window quote/trade texture.

Uso:

- liquidity stress;
- book/tape health;
- spread expansion;
- price impact;
- aggressive flow;
- execution risk.

### 7.7 Regimen

Fuente esperada:

- regime indicators;
- intraday regime features;
- market-wide context;
- sector/attention/liquidity regimes.

Uso:

- condicionar probabilidades;
- detectar drift;
- segmentar estados similares con semantica diferente.

### 7.8 Catalyst / Informacion Externa

Fuente esperada:

- news;
- SEC filings;
- offerings;
- warrants;
- corporate event alerts;
- real-time vendors.

Uso:

- distinguir evento tecnico de evento informacional;
- construir `corporate_event_risk_state`;
- evitar usar noticia publicada despues como feature pre-evento.

### 7.9 Halts / SSR / Borrow / Short Pressure

Fuente esperada:

- halts;
- short / short_review;
- SSR state;
- borrow availability, cuando exista.

Uso:

- interrumpir event windows;
- medir squeeze/execution constraints;
- distinguir riesgo operacional de alpha.

### 7.10 Fundamentals / Financial

Fuente esperada:

- financial;
- float / market cap;
- filings;
- fundamentals point-in-time.

Uso:

- contexto estructural del instrumento;
- no debe introducir lookahead desde statements publicados despues del evento.

## 8. Estado Por Evento

El objetivo no es una unica tabla universal plana.

El objetivo es poder reconstruir:

```text
event_state(event_id, t)
```

Donde:

```text
event_state =
market_state
+ event definition context
+ event clock
+ event-specific windows
+ quality gates
+ leakage boundaries
```

El `event_state` es el objeto que ML/RL y Decision Models deben consumir.

## 9. Estados Para ML

ML debe responder:

```text
P(outcome | event_state)
```

o:

```text
E[future_path | event_state]
```

ML no decide.

ML produce:

- probabilidades;
- calibracion;
- embeddings;
- clustering;
- anomaly scores;
- state similarity;
- uncertainty.

ML no debe producir:

- entradas;
- stops;
- targets;
- sizing;
- ejecucion;
- reward final.

## 10. Estados Para Offline RL

Offline RL debe operar sobre transiciones:

```text
(state_t, action_t, reward_t, state_t+1, done)
```

En TSIS, `state_t` debe venir de un estado gobernado.

Offline RL no puede inventar una fuente de verdad distinta.

Debe declarar:

- state schema;
- action space;
- reward function;
- behavior policy source;
- dataset coverage;
- out-of-distribution guard;
- temporal split;
- leakage check;
- evaluation policy.

Regla:

```text
Offline RL solo empieza cuando el estado esta bien modelado.
```

## 11. Estados Para AlphaEvolve

AlphaEvolve no debe buscar "la estrategia ganadora" directamente.

Debe empezar por objetos evaluables:

- definiciones de eventos;
- features de estado;
- reglas de limpieza;
- evaluadores;
- execution policies acotadas;
- optimizaciones de rendimiento del backtester.

Contrato:

```text
LLM puede modificar candidato.
LLM no puede modificar juez.
```

AlphaEvolve puede proponer:

- nuevas variables de estado;
- nuevas funciones de agrupacion de eventos;
- nuevos filtros de deteccion de evento;
- nuevos embeddings;
- nuevas policies bajo evaluator bloqueado.

AlphaEvolve no puede:

- usar PnL como unica verdad;
- bajar costes;
- mirar futuro;
- modificar el dataset despues de ver resultados;
- mezclar outcome como feature pre-evento;
- cambiar quality gates para salvar candidatos.

## 12. Real Time State Update

Un sistema live debe actualizar estados bajo estas reglas:

```text
incoming message
-> source timestamp
-> received timestamp
-> normalization
-> quality gate
-> state update
-> event candidate update
-> downstream decision gate
```

Todo estado live debe preservar:

- source timestamp;
- received timestamp;
- processing timestamp;
- feed/vendor;
- latency bucket;
- confidence;
- missingness;
- stale state marker.

Un estado live nunca debe fingir que una alerta existia antes de recibirse.

## 13. Calidad De Estado

Cada estado debe heredar calidad de sus inputs.

Ejemplo:

```yaml
quality_state:
  daily: good
  intraday_1m: good
  quotes: review
  trades: good
  halts: good
  news: scoped
  financial: review
```

El estado resultante no es automaticamente `good`.

La calidad compuesta depende del uso:

- un estado puede ser suficiente para inspeccion forense;
- insuficiente para backtest;
- prohibido para ML/RL full-universe;
- permitido para event discovery scoped.

## 14. Anti-Leakage

Todo estado debe pasar por una barrera de leakage.

Prohibido:

- usar outcomes futuros como estado;
- usar labels como features;
- usar news posterior como catalyst pre-evento;
- usar adjusted data sin declarar semantica;
- usar corporate actions publicados despues como si fueran conocidos antes;
- usar universe membership futura;
- entrenar con data quality flags que dependen de analisis posterior si no se
  separan como audit metadata.

## 15. Outputs Esperados Fututos

Este contrato propone crear, en fases posteriores:

```text
01_foundations/canonical_schemas/outputs/market_state_schema_contract.md
01_foundations/contract_registry/dataset_contracts/market_state_dataset_contract_v0_1.md
01_foundations/data_consumption_policies/market_state_consumption_policy.md
01_foundations/validators/outputs/market_state_validators.md
01_research/event_engine/event_state_builder_contract.md
03_TSIS_Offline_RL/state_action_reward_dataset_contract.md
```

Este documento no crea esos contratos operativos.

Solo define el marco cientifico y semantico.

## 16. Preguntas Que Debe Responder Un Estado

Todo estado promovible debe permitir responder:

1. Que se sabia exactamente en ese instante?
2. De que fuentes salio?
3. Que fuentes estaban ausentes?
4. Que calidad tenia cada familia?
5. Que parte pertenece a identidad, calendario, price semantics, diario,
   intradia, microestructura, catalyst, regimen y ejecucion?
6. Que informacion estaba prohibida por leakage?
7. Que evento o candidato de evento estaba activo?
8. Que outcome se medira despues, separado del estado?
9. Que decision podria tomar un modelo sin mirar futuro?
10. Que evaluator juzgara esa decision?

## 17. Aplicaciones Cientificas Relacionadas

Estas referencias no son autoridad TSIS, pero justifican la direccion cientifica.

| Sistema / paper | Quien lo uso | Que hizo | Relacion con TSIS |
|---|---|---|---|
| AlphaGo / AlphaGo Zero | Google DeepMind | Aprende policy/value sobre representaciones de posiciones y mejora con busqueda/self-play. | TSIS necesita `market_state` antes de policy; sin estado correcto no hay decision correcta. |
| MuZero | Google DeepMind | Aprende un modelo que predice reward, policy y value sin conocer dinamica completa. | TSIS puede aprender dinamica latente de eventos si separa estado, accion, reward y siguiente estado. |
| Offline RL review | Levine, Kumar, Tucker, Fu | Formaliza aprendizaje de politicas desde datasets historicos sin interaccion online. | TSIS debe convertir historico en transiciones gobernadas, no solo en features planas. |
| DeepLOB | Zhang, Zohren, Roberts | Modela LOB como estructura espacio-temporal para prediccion de mid-price en cash equities. | TSIS microcaps necesita representar libro/tape como estado rico, no solo OHLCV. |
| ABIDES | Byrd, Hybinette, Balch | Simulacion multiagente de mercado para AI research con LOB. | TSIS puede usar replay/simulacion para execution y RL sobre estados microestructurales. |
| JAX-LOB | Frey, Li, Nagy, Sapora, Lu, Zohren, Foerster, Calinescu | Simulador LOB GPU para miles de libros y RL de trading. | TSIS necesitara escalabilidad si entrena estados/eventos en universo amplio. |
| Market Making with Deep RL from LOB | Guo, Lin, Huang | RL agent usa LOB de alta dimension para cotizar bid/ask y reward hibrido. | Muestra que decisiones financieras dependen de representacion microestructural del estado. |
| LOBFrame / Deep Limit Order Book Forecasting | Briola, Bartolucci, Aste | Framework open-source para evaluar modelos LOB y advierte que accuracy no equivale a trading accionable. | TSIS debe separar prediccion, decision, coste y ejecutabilidad. |
| FunSearch | Google DeepMind / Nature | LLM + evaluator + evolucion descubre programas verificables en matematica y bin packing. | TSIS debe bloquear evaluadores antes de permitir busqueda evolutiva de eventos/features/policies. |
| AlphaEvolve | Google DeepMind | LLMs + evaluadores + evolucion optimizan algoritmos y componentes de infraestructura. | TSIS puede llegar a AlphaEvolve financiero solo si `market_state` y evaluadores son estables. |
| Causality for Machine Learning | Bernhard Scholkopf | Conecta problemas duros de ML con causalidad. | TSIS debe preferir estados causales/estructurales sobre proxies fragiles. |

## 18. Referencias

- Silver et al. (2016), "Mastering the game of Go with deep neural networks and
  tree search", Nature:
  https://www.nature.com/articles/nature16961
- Silver et al. (2017), "Mastering the game of Go without human knowledge",
  Nature:
  https://www.nature.com/articles/nature24270
- Schrittwieser et al. (2019/2020), "Mastering Atari, Go, Chess and Shogi by
  Planning with a Learned Model", arXiv:
  https://arxiv.org/abs/1911.08265
- Levine et al. (2020), "Offline Reinforcement Learning: Tutorial, Review, and
  Perspectives on Open Problems", arXiv:
  https://arxiv.org/abs/2005.01643
- Zhang, Zohren, Roberts (2018/2020), "DeepLOB: Deep Convolutional Neural
  Networks for Limit Order Books", arXiv:
  https://arxiv.org/abs/1808.03668
- Byrd, Hybinette, Balch (2019), "ABIDES: Towards High-Fidelity Market
  Simulation for AI Research", arXiv:
  https://arxiv.org/abs/1904.12066
- Frey et al. (2023), "JAX-LOB: A GPU-Accelerated limit order book simulator to
  unlock large scale reinforcement learning for trading", arXiv:
  https://arxiv.org/abs/2308.13289
- Guo, Lin, Huang (2023), "Market Making with Deep Reinforcement Learning from
  Limit Order Books", arXiv:
  https://arxiv.org/abs/2305.15821
- Briola, Bartolucci, Aste (2024), "Deep Limit Order Book Forecasting", arXiv:
  https://arxiv.org/abs/2403.09267
- Romera-Paredes et al. (2024), "Mathematical discoveries from program search
  with large language models", Nature:
  https://www.nature.com/articles/s41586-023-06924-6
- Novikov et al. (2025), "AlphaEvolve: A coding agent for scientific and
  algorithmic discovery", arXiv:
  https://arxiv.org/abs/2506.13131
- Scholkopf (2019/2022), "Causality for Machine Learning", arXiv:
  https://arxiv.org/abs/1911.10500

## 19. Criterio De Promocion

Este contrato podra promocionarse cuando existan:

- schema real de `market_state`;
- schema real de `event_state`, si se separa del `market_state` base;
- builder reproducible de `market_state`;
- builder reproducible de `event_state`;
- validators institucionales;
- tests unitarios, contractuales y de integracion;
- test evidence con `run_id`, metadata, logs y outputs trazables;
- ejemplos visuales/forenses para inspectores humanos;
- example event states con casos buenos, review y bad cuando aplique;
- materializacion inicial versionada;
- leakage checks;
- data quality inheritance;
- consumption policies para Event Engine, ML/RL, live y AlphaEvolve;
- registry entry y manifest;
- changelog de promocion.

Hasta entonces, gobierna como `candidate_policy` dentro de `00_CTO`.
