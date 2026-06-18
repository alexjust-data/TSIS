# 00_CTO

Fecha de actualizacion: 2026-06-18
Estado: CTO workspace activo para arquitectura de automatizaciones TSIS.

`00_CTO/` es la capa de direccion tecnica, memoria intelectual y diseno
arquitectonico de TSIS.

No es la autoridad operativa activa del proyecto. Es el lugar donde se ordena
el pensamiento estrategico antes de promocionar ideas maduras a documentos
canonicos, contratos locales, policies, validators o sistemas ejecutables.

## Rol actual

`00_CTO/` cumple cinco funciones:

- conservar razonamiento CTO sobre lo que TSIS debe llegar a ser;
- organizar conocimiento externo antes de convertirlo en doctrina TSIS;
- disenar la arquitectura de automatizacion para Harness, evaluadores y busqueda
  tipo AlphaEvolve;
- definir roadmaps estrategicos sin contaminar carpetas operativas con ideas
  inmaduras;
- convertir trabajo ya auditado en operating models que puedan ejecutarse con
  agentes.

La prioridad actual ya no es pensar agentes en abstracto.

La prioridad actual es:

```text
cerrar el Data Quality Harness sobre la auditoria existente de 01_foundations
```

Esto significa que primero se definen el alcance, los estados, los contratos de
artefactos y el replay offline. Solo despues se definen agentes concretos,
permisos, workflows y runtimes productivos.


## Changelog local

`00_CTO/CHANGELOG.md` registra la historia semantica de la capa CTO:

- hitos de arquitectura;
- protocolos Harness;
- contratos de artefactos;
- decisiones sobre AlphaEvolve;
- cambios de estructura con impacto metodologico.

No reemplaza `C:\TSIS_Data\CHANGELOG.md`, que queda reservado para hitos
globales de TSIS.

No debe crearse un changelog por cada Harness mientras sigan en fase de diseno.
Los Harness operativos futuros deben dejar `run_manifest`, `run_summary`,
`trace logs` y, solo si procede, release log propio.



## Regla de trazabilidad Harness

Todo Harness que produzca artefactos aceptables debe tener toolchain residente
en el proyecto.

Esto incluye generadores, validadores, prompts operativos, templates y configs.

No se acepta como fuente final:

```text
C:\Users\...
C:\tmp\...
Downloads\...
solo conversacion
```

La regla vigente esta en:

```text
12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md
```
## Autoridad activa

`00_CTO/` informa al proyecto. No reemplaza la autoridad canonica.

La autoridad activa vive en:

- `PROJECT_OPERATING_SYSTEM.md`
- `PROJECT_RULES.md`
- `AGENTS.md`
- `VERSIONING_STANDARDS.md`
- `RESEARCH_PHILOSOPHY.md`
- `ARCHITECTURE_OVERVIEW.md`
- `01_TSIS_backtest_SmallCaps/README.md`
- `01_TSIS_backtest_SmallCaps/AGENTS.md`
- `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
- contratos, registries, schemas, policies y validators bajo
  `01_TSIS_backtest_SmallCaps/01_foundations/`

Regla:

```text
00_CTO disena y alimenta autoridad.
Los documentos raiz y contratos de modulo gobiernan autoridad.
```

Si una idea de `00_CTO/` se vuelve obligatoria, debe promocionarse al documento
canonico, regla local, contrato, policy, validator o changelog correspondiente.

## Lectura arquitectonica vigente

La lectura CTO vigente de TSIS es:

```text
TSIS = contratos de datos + doctrina de research + evaluadores + harness + ejecucion reproducible + evolucion controlada
```

Esto implica un orden estricto:

1. Definir que debe automatizarse.
2. Definir el estandar institucional para juzgar outputs.
3. Convertir auditorias y doctrina en contratos ejecutables.
4. Definir workflows Harness y agentes.
5. Ejecutar replay offline contra el baseline historico.
6. Pasar a shadow live.
7. Activar gating live.
8. Solo despues permitir generacion de candidatos tipo AlphaEvolve.

AlphaEvolve no es el punto de partida. AlphaEvolve solo tiene sentido cuando
TSIS ya tiene evaluadores bloqueados, datos versionados, fitness robusto,
lineage completo y archivo controlado de candidatos.

Harness es la necesidad inmediata porque TSIS primero necesita coordinar
trabajo largo, auditable y trazable sobre auditoria de datos, extraccion de
doctrina, mantenimiento de contratos, research, evaluacion y reporting.

## Rail operativo actual

El rail vigente para esta fase es:

```text
auditoria historica verificada
-> contratos ejecutables
-> replay offline
-> shadow live
-> gating live
-> consumo por backtest, ML y AlphaEvolve
```

El frente activo es Data Quality Harness sobre:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

El primer documento de trabajo ya fue creado en:

```text
C:\TSIS_Data\00_CTO\12_TSIS_COGNITIVE_ARCHITECTURE\10_DATA_QUALITY_HARNESS\data_audit_harness_agentic_operating_map.md
```

Ese documento es el snapshot auditor y mapa operativo de referencia para
convertir la auditoria de datos en Harness agentic.

## Frentes iniciales de automatizacion

El primer alcance de automatizacion debe construirse sobre dos bases de
conocimiento ya existentes.

### 1. Data Audit / Foundations

Fuente:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations`

Documento CTO vigente:

- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/data_audit_harness_agentic_operating_map.md`

Proposito:

- entender que datasets derivados de Polygon estan auditados, certificados,
  restringidos, incompletos o aun en revision;
- convertir estandares historicos de auditoria en checks repetibles;
- preparar el puente entre control historico de calidad de data y control diario
  de data live;
- definir que debe hacer Harness antes de crear agentes concretos.

Estado:

- la auditoria esta muy avanzada, pero no debe tratarse como terminada;
- hay baseline verificado;
- existen deudas de navegabilidad y contrato que deben cerrarse antes de
  productivizar agentes.

Regla:

```text
los agentes deben reproducir la auditoria existente antes de operar live
```

### 2. Sersan Backtest Doctrine

Fuente:

- `C:\TSIS_Data\00_CTO\99_REFERENCE_LIBRARY\SersanSistemas`

Proposito:

- destilar el curso de trading algoritmico en doctrina mecanica TSIS para
  backtesting y validacion de estrategias;
- extraer reglas sobre robustez, BRaC, walk-forward, optimizacion, stops, money
  management, portfolio y regimen;
- traducir metodologia experta en checklists, requisitos de evaluador y futuros
  tests automatizables.

Estado:

- fuente de alto valor;
- aun no es doctrina canonica;
- debe pasar por protocolo formal de destilacion antes de alimentar evaluadores
  o AlphaEvolve.

Regla:

```text
SersanSistemas es fuente experta; solo gobierna TSIS despues de destilacion y promocion
```

## Politica de grafo semantico Graphify

Graphify puede usarse como mapa semantico de navegacion para Codex y futuros
agentes, pero no es autoridad canonica ni sustituye Git, `AGENTS.md`, los
documentos raiz, `01_foundations` ni los changelogs.

El protocolo operativo local obligatorio esta en:

```text
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

Ese protocolo manda sobre cualquier improvisacion local. En particular, ningun
agente debe crear manualmente `00_CTO/graphify-out/graph.json` y presentarlo
como Graphify oficial.

Regla:

```text
Graphify indexa conocimiento para navegar.
Los contratos versionados gobiernan conocimiento.
```

Por tanto, `graphify-out/` debe tratarse por defecto como artefacto runtime
reconstruible. No es source of truth institucional salvo decision explicita,
manifest y promocion posterior.

Regla de procedencia:

```text
Compatible con graphify query no significa oficial Graphify.
Si no lo genero el pipeline oficial, no debe ocupar graphify-out/graph.json.
```

### Actualizaciones incrementales

Las actualizaciones del grafo de `00_CTO` se gobiernan en:

```text
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

El grafo raiz actual es un grafo fusionado. Cuando se anadan o modifiquen
archivos, un agente no debe reescanear todo `00_CTO` como bloque unico por
defecto. Debe identificar el slice afectado, reconstruir o actualizar ese leaf
mediante Graphify oficial, fusionarlo con `graphify merge-graphs`, reclusterizar
con `graphify cluster-only` y validar con `graphify diagnose multigraph`.

Mapping vigente para trading:

```text
13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/
-> core_cto_graph / trading_systems_slice
```

Por tanto, una incorporacion de documentos o PDFs en
`13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/` no queda absorbida por el grafo raiz
hasta que ese slice haya sido extraido, fusionado y diagnosticado oficialmente.

### Scope operativo inicial

No debe construirse un unico grafo monolitico de `00_CTO/`.

La capa CTO contiene material con estados distintos:

- workspace operativo de Harness;
- memoria arquitectonica;
- destilaciones Sersan;
- biblioteca externa consultiva;
- notas privadas o fuente no canonica;
- outputs runtime reconstruibles.

Fusionarlo todo sin distincion haria que el grafo confundiera autoridad,
referencia, borrador, output y fuente externa.

El grafo operativo inicial debe priorizar:

- `00_CTO/README.md`
- `00_CTO/CHANGELOG.md`
- `00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/README.md`
- `00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/`
- `00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/`

Ese scope conecta direccion CTO, Harness y contratos de artefactos dentro de
`00_CTO`.

`C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations` es dependencia
operativa externa referenciada por `00_CTO`, pero no forma parte del grafo
`00_CTO` por defecto. Si se necesita, debe construirse como grafo separado del
modulo `01_TSIS_backtest_SmallCaps` y fusionarse solo mediante una decision de
scope explicita.

### Subgrafos y merges

Para respetar las reglas de Graphify y preservar semantica, el grafo de
`00_CTO` debe construirse por subgrafos leaf y merges gobernados:

Los nombres siguientes son ids logicos de build, no carpetas existentes:

1. `core_cto_graph`
   - README, CHANGELOG, folders ligeros de direccion CTO y memoria.
2. `data_quality_harness_graph`
   - `00_SHARED_HARNESS_KERNEL`
   - `10_DATA_QUALITY_HARNESS`
3. `sersan_distillation_graph`
   - `20_SERSAN_DISTILLATION_HARNESS`, partido por practica o lesson pack.
4. `reference_sersan_graph`
   - `99_REFERENCE_LIBRARY/SersanSistemas`, construido por slices gobernadas.

Regla de merge:

```text
core_cto_graph + data_quality_harness_graph + sersan_distillation_graph
= grafo operativo CTO inicial
```

`reference_sersan_graph` no debe absorberse a ciegas. Puede fusionarse con el
grafo raiz solo mediante una decision explicita de scope, con manifest,
verificacion y separacion clara entre fuente experta, destilacion, contrato y
doctrina TSIS.

### Estado del build Graphify actual

Estado al 2026-06-18:

```text
00_CTO/graphify-out/
├── graph.json
├── GRAPH_REPORT.md
├── graph.html
└── BUILD_MANIFEST.md
```

El grafo raiz actual fue generado y reclusterizado mediante Graphify oficial.
No es un fallback manual.

Cobertura incluida:

- `12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS`
- core CTO Markdown: README, changelog, protocolo Graphify, carpetas ligeras
  `01_*` a `13_*`, `agent_standards`, `architecture_decisions`,
  `research_principles`, `roadmap`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS`, slice
  operativa de protocolos, contratos, runbooks, toolchain, manifests, reports,
  mechanical rules, open questions y quality reports
- `99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised`
- `99_REFERENCE_LIBRARY/SersanSistemas/02_workshops`, slice documental
  detectada por Graphify: `.md`, `.txt`, `.html`
- `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY`, slice incremental de trading:
  `07_Long_plays.md`, `07_Short_Plays.md` y
  `Day Trading en Small Caps - XVNTrading.pdf`

Verificacion raiz final:

```text
nodes: 1732
edges: 2269
communities: 166
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Pendiente o diferido:

- imagenes y videos de `02_workshops`, por coste/tamano operativo;
- JSON de alineacion/transcripcion de `02_workshops`: Graphify 0.8.40 los
  detecto como `code`, pero el extractor AST oficial produjo `0` nodos y `0`
  edges, por lo que no se fusionaron;
- `.ELD`, `.tsw` y formatos TradeStation: no quedaron absorbidos por el scan
  documento/code oficial actual y requieren transformacion o importer
  gobernado antes de integrarse.

### Politica de outputs

Los grafos intermedios deben poder vivir fuera del repositorio, por ejemplo en:

```text
C:\tmp\graphify_00_cto\
```

Esa ruta es un area runtime sugerida, no una carpeta fuente de `00_CTO`.

El grafo operativo final, si se decide materializarlo dentro de `00_CTO`, debe
vivir en:

```text
00_CTO/graphify-out/graph.json
```

Ese path solo puede existir si el archivo fue generado por Graphify. Un fallback
manual, aunque sea JSON compatible, debe guardarse fuera del path canonico con
nombre `non_official_fallback`.

Antes de tratar cualquier grafo como artefacto gobernado, debe existir al menos:

- manifest de build;
- lista de subgrafos fuente;
- fecha;
- comando o procedimiento usado;
- alcance incluido y excluido;
- decision explicita de si es runtime, consultivo o promovido.

Las exclusiones tecnicas globales para builds Graphify se declaran en:

```text
C:\TSIS_Data\.graphifyignore
```

Ese archivo debe excluir datos, caches, outputs runtime y artefactos binarios,
pero no debe usarse para ocultar diferencias semanticas entre fuente, doctrina,
contrato y referencia. Esa separacion debe resolverse por scopes de build y
por manifests.

## Documentos activos y siguientes

### Documento activo creado

1. `12_TSIS_COGNITIVE_ARCHITECTURE/README.md`

   Tesis transversal v0:

   ```text
   Harness antes que AlphaEvolve.
   Evaluadores antes que generadores.
   Alcance de automatizacion antes que roles de agentes.
   ```

2. `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/data_audit_harness_agentic_operating_map.md`

   Snapshot auditor de `01_foundations` y mapa operativo para Data Quality
   Harness.

### Siguientes documentos recomendados

Los proximos documentos deben crearse en `12_TSIS_COGNITIVE_ARCHITECTURE/`, en
este orden:

1. `2026-06-11_harness_data_audit_state_vocabulary.md`
2. `2026-06-11_harness_live_run_artifact_contract.md`
3. `2026-06-11_harness_data_audit_offline_replay_protocol.md`
4. `DATA_QUALITY_HARNESS_OPERATING_MODEL_v0_1.md`
5. `TSIS_AGENT_OPERATING_MODEL_v0_1.md`
6. `SERSAN_BACKTEST_DOCTRINE_SCOPE_v0_1.md`
7. `SERSAN_DISTILLATION_PROTOCOL_v0_1.md`
8. `TSIS_EVALUATOR_CONTRACT_TRADING_v0_1.md`
9. `ALPHAEVOLVE_TSIS_SANDBOX_POLICY_v0_1.md`

Razon:

```text
primero fijar estados y artefactos;
despues validar replay;
despues definir agentes;
despues destilar doctrina;
despues bloquear evaluadores;
despues permitir busqueda evolutiva.
```

## Mapa de carpetas

### `00_private/`

Notas privadas, pensamiento exploratorio, prompts iniciales, capturas y
razonamiento no canonico.

Estado:

- material fuente;
- no canonico;
- no automaticamente correcto;
- util para reconstruir intencion.

Una nota privada puede inspirar trabajo canonico, pero debe destilarse antes de
promocionarse.

### `01_RESEARCH_PHILOSOPHY/`

Notas CTO sobre como TSIS debe producir conocimiento.

Cubre preguntas como:

- que cuenta como evidencia;
- que cuenta como edge;
- como deben probarse hipotesis;
- como evitar sobreoptimizacion;
- como separar correlacion de mecanismo causal.

La autoridad activa sigue viviendo en `RESEARCH_PHILOSOPHY.md` y en las reglas
del proyecto.

### `02_SYSTEMS_ENGINEERING/`

Pensamiento de arquitectura y diseno de sistema.

Debe contener notas sobre:

- limites entre modulos;
- interfaces;
- flujo de datos;
- diseno event-driven;
- decisiones tecnicas;
- mantenibilidad.

No sustituye `PROJECT_OPERATING_SYSTEM.md` ni los contratos de modulo.

### `03_AGENT_ENGINEERING/`

Material fuente sobre como deben trabajar agentes IA dentro de TSIS.

Cubre:

- Harness engineering;
- long-running agents;
- estandares de agentes;
- descomposicion de tareas;
- seguridad de agentes;
- revision y observabilidad;
- colaboracion multiagente.

Esta carpeta no es todavia el modelo operativo final de agentes. Es la capa
fuente que alimentara documentos futuros en `12_TSIS_COGNITIVE_ARCHITECTURE/`
y, mas adelante, `AGENTS.md` si alguna regla pasa a ser obligatoria.

### `04_MEMORY_AND_KNOWLEDGE/`

Memoria, context engineering, RAG, GraphRAG y diseno de conocimiento
institucional.

Idea clave:

```text
TSIS no solo debe computar; TSIS debe recordar.
```

Tipos futuros de memoria relevantes:

- memoria de research;
- memoria de hipotesis;
- memoria de fallos;
- memoria arquitectonica;
- memoria de trading;
- memoria de evidencia.

GraphRAG vive aqui como tecnologia. Un futuro market knowledge graph puede vivir
en `11_MARKET_SCIENCE/` si pasa a formar parte de la representacion del estado
de mercado.

### `05_EVALUATION_SYSTEMS/`

Area de diseno para decidir si algo funciona.

Debe cubrir:

- evals de agentes;
- evals de research;
- evals de backtest;
- evals de calidad de datos;
- diseno de benchmarks;
- fitness functions;
- pruebas de robustez.

Regla central:

```text
el evaluador es mas importante que el generador
```

Esta carpeta es critica antes de AlphaEvolve. Sin evaluadores, la generacion de
candidatos se convierte en p-hacking automatizado.

### `06_MLOPS_AND_REPRODUCIBILITY/`

Cadena de custodia cientifica de resultados.

Debe responder:

- que datos produjeron este resultado;
- que codigo lo produjo;
- que config estaba activa;
- que experiment id y run id aplican;
- que version de modelo, estrategia o report se uso.

Puede apoyarse en MLflow, DVC, manifests, registries, CI y observabilidad de
agentes, pero las herramientas son secundarias frente a la semantica de
reproducibilidad.

### `07_DISTRIBUTED_SYSTEMS/`

Arquitectura de escalado para TSIS.

No significa empezar por Kubernetes.

Para TSIS, el orden probable es:

```text
ejecucion local -> paralelismo local/Ray -> Ray cluster -> event streaming -> infraestructura productiva
```

Debe cubrir:

- compute distribuido;
- data distribuida;
- arquitectura event-driven;
- orquestacion de agentes;
- realtime systems;
- model serving;
- roadmap de escalado.

### `08_MACHINE_LEARNING/`

Representation learning y modelado predictivo de estructura de mercado.

Debe cubrir:

- feature engineering;
- meta-labeling;
- market state representation;
- information bars;
- causal features;
- control de leakage;
- validacion financiera de ML.

ML no debe tratarse como magia de descubrimiento. Debe operar sobre datos
auditados, labels explicitos y evaluacion temporal valida.

### `09_REINFORCEMENT_LEARNING/`

Decision systems, behavior cloning, offline RL y policy learning.

La carpeta conserva el nombre RL, pero conceptualmente puede evolucionar hacia:

```text
reinforcement learning and decision models
```

Principio importante:

```text
RL va despues de representacion de estado, evaluacion, reproducibilidad y realismo de ejecucion
```

Offline RL no debe esperarse como descubridor de edge desde cero. Debe optimizar
decisiones alrededor de estados, acciones, rewards y estructuras de research ya
gobernadas.

### `10_AUTONOMOUS_RESEARCH_SYSTEMS/`

Sistemas autonomos de descubrimiento e investigacion.

Incluye AlphaEvolve, FunSearch, OpenEvolve, generacion de hipotesis,
evolutionary search y autonomous trading research.

Muchos archivos actuales son placeholders o shells tempranos. Es aceptable
mientras el plan TSIS especifico viva en `12_TSIS_COGNITIVE_ARCHITECTURE/`.

Esta carpeta trata discovery systems en general. No debe ser autoridad operativa
directa sobre trading research.

### `11_MARKET_SCIENCE/`

Ciencia de dominio para modelar el mercado.

Organiza la base conceptual de:

- microestructura;
- financial machine learning;
- causalidad;
- invariantes y riesgo.

Conclusion CTO clave:

```text
market state representation es mas importante que elegir familia de modelo
```

TSIS debe modelar microcaps como estados dinamicos que incluyen atencion,
liquidez, order flow, catalysts, spreads, halts, short pressure, regimen y
restricciones de ejecucion, no solo velas OHLCV.

### `12_TSIS_COGNITIVE_ARCHITECTURE/`

Capa de aplicacion especifica a TSIS para arquitectura de automatizaciones.

Es ahora el workspace CTO principal para:

- alcance de automatizacion;
- operating models de Harness;
- workflows de agentes;
- automatizacion de data quality;
- destilacion de doctrina Sersan;
- contratos de evaluador;
- sandbox policy para AlphaEvolve;
- camino de promocion desde research automation hacia ejecucion controlada.

Documentos activos:

- `README.md`
- `10_DATA_QUALITY_HARNESS/data_audit_harness_agentic_operating_map.md`

Regla vigente:

```text
Harness antes que AlphaEvolve.
Evaluadores antes que generadores.
Data Quality Harness antes que agentes genericos.
```

### `99_REFERENCE_LIBRARY/`

Biblioteca de referencia externa.

Contiene:

- papers;
- PDFs;
- libros;
- cursos;
- videos;
- transcripciones;
- imagenes;
- ejemplos de codigo;
- referencias AlphaEvolve;
- el curso SersanSistemas.

Es fuente de alto valor, pero no autoridad directa.

Regla importante:

```text
el material de referencia solo se vuelve doctrina TSIS despues de destilacion y promocion
```

El corpus SersanSistemas es especialmente importante para doctrina de backtest,
robustez, disciplina de optimizacion, money management y construccion de
portfolio. Debe alimentar un protocolo formal de destilacion antes de ser usado
por Harness o AlphaEvolve.

### `roadmap/`

Direccion estrategica y secuenciacion.

Debe contener:

- roadmap maestro;
- roadmaps por modulo;
- milestones;
- prioridades;
- deuda tecnica;
- roadmap de aprendizaje;
- orden de dependencias.

No debe contener notas completas de research, biblioteca externa, datasets,
outputs ni assets pesados.

## Estados de promocion dentro de 00_CTO

Una idea CTO puede estar en cuatro estados:

1. `source_note`: nota cruda, referencia, prompt, extracto de curso o
   pensamiento privado.
2. `draft`: borrador estructurado pero no autoritativo.
3. `candidate_policy`: cerca de convertirse en regla, contrato u operating
   model.
4. `promoted`: incorporada a documento canonico, contrato, policy, validator o
   changelog.

Solo las ideas `promoted` gobiernan ejecucion real.

## Reglas para escribir en 00_CTO

### Si debe ir aqui

- notas de arquitectura estrategica;
- diseno de automatizaciones;
- roadmaps;
- decisiones tipo ADR;
- borradores de doctrina;
- diseno de evaluadores;
- destilacion de fuentes;
- referencias ligeras;
- explicaciones markdown.

### No debe ir aqui

- market data raw;
- parquets de datasets;
- runtime outputs;
- logs;
- caches;
- datasets certificados;
- credenciales live;
- notebooks como autoridad final;
- contratos operativos que pertenecen a `01_foundations/`;
- reglas obligatorias que pertenecen a documentos raiz.

## Regla de duplicados

No debe mantenerse el mismo documento conceptual en varias carpetas de
`00_CTO/`.

Ubicaciones preferidas:

- direccion de proyecto: `roadmap/`
- fuentes de agentes y Harness: `03_AGENT_ENGINEERING/`
- plan especifico de automatizacion TSIS: `12_TSIS_COGNITIVE_ARCHITECTURE/`
- referencias de discovery autonomo: `10_AUTONOMOUS_RESEARCH_SYSTEMS/`
- representacion de mercado y ciencia de dominio: `11_MARKET_SCIENCE/`
- memoria y retrieval: `04_MEMORY_AND_KNOWLEDGE/`
- diseno de evaluadores: `05_EVALUATION_SYSTEMS/`
- cadena de custodia reproducible: `06_MLOPS_AND_REPRODUCIBILITY/`
- biblioteca externa: `99_REFERENCE_LIBRARY/`

Si un documento parece pertenecer a dos lugares, debe vivir en uno solo y ser
referenciado desde el otro.

## Politica Git y artefactos

Debe versionarse:

- markdown institucional;
- roadmaps;
- ADRs;
- resumenes fuente ligeros;
- protocolos;
- especificaciones de evaluador;
- operating models;
- ejemplos textuales pequenos.

No debe versionarse como memoria normal del proyecto salvo justificacion
explicita:

- imagenes pesadas;
- videos;
- PDFs grandes;
- zips;
- runtime outputs;
- `graphify-out/` generado;
- raw datasets;
- caches generadas;
- credenciales privadas;
- secretos de broker o live trading.

## Regla final

`00_CTO/` existe para evitar que TSIS se convierta en una suma de scripts,
prompts, datasets y experimentos.

Su funcion es preservar direccion, disenar automatizaciones con disciplina y
alimentar la autoridad canonica solo cuando las ideas esten maduras.

El siguiente paso correcto ya no es crear mas abstraccion ni inflar roles de
agentes.

El siguiente paso correcto es:

```text
cerrar el vocabulario de estados y el contrato de artefactos live del Data Quality Harness
```

Despues de eso, TSIS podra construir agentes Harness contra trabajo real:
primero replay offline, despues shadow live, despues gating live. Solo mas
adelante AlphaEvolve debe buscar dentro de sandboxes con datos gated y
evaluadores bloqueados.

