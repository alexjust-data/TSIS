# Graphify Refresh Queue for 00_CTO

Fecha de creacion: 2026-06-18
Estado: cola operativa versionada para refrescos Graphify de `00_CTO`.

## Rol

Este archivo evita tratar Graphify como si fuera Git.

Git registra cambios continuamente. Graphify se refresca por hitos semanticos,
por severidad o por lote.

Regla:

```text
No actualizar Graphify por cada commit.
Actualizar Graphify cuando el cambio altere el mapa semantico que un agente
necesita consultar.
```

El protocolo autoritativo sigue siendo:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

## Severidad de refresco

### LOW

No requiere Graphify.

Ejemplos:

- typo;
- README menor;
- limpieza textual;
- mover duplicados sin cambiar semantica;
- notas privadas no promovidas.

Accion:

```text
No hacer nada en Graphify.
```

### MEDIUM

Se anota en esta cola, pero no se refresca inmediatamente.

Ejemplos:

- nuevo README funcional;
- nueva nota de research;
- nuevo documento conceptual no promovido;
- ampliacion menor de una carpeta ya indexada.

Accion:

```text
Anotar entrada pending.
Refrescar cuando haya lote suficiente o una consulta lo necesite.
```

### HIGH

Requiere rebuild del leaf afectado en una ventana de trabajo dedicada.

Ejemplos:

- nueva Event Library;
- nueva Strategy Library;
- cambio arquitectonico promovido;
- nuevo PDF o documento importante;
- nueva policy local.

Accion:

```text
Construir o actualizar leaf oficial.
No actualizar root si no es necesario para la tarea inmediata.
```

### CRITICAL

Requiere decision explicita antes de tocar el root.

Ejemplos:

- renombrar carpetas ya indexadas;
- eliminar o migrar rutas indexadas;
- cambiar event taxonomy;
- cambiar contratos canonicos;
- cambiar semantica de schemas o datasets.

Accion:

```text
Construir leaf si aporta valor inmediato.
No hacer merge aditivo si el root conserva nodos antiguos.
Integrar root solo mediante rebuild controlado o reemplazo oficial de slice.
```

## Cadencia recomendada

```text
Diario:
  Git normal.
  Documentar cambios relevantes.
  Anotar pending refresh si aplica.

Por hito:
  Rebuild de leaves afectados.

Por ventana dedicada:
  Integracion limpia del root.
```

## Entradas activas

### 2026-06-30 - TSIS Lab Architecture v2

Estado: pending
Severidad: HIGH

Slice:

```text
00_CTO/
```

Motivo:

- se creo `TSIS_LAB_ARCHITECTURE_v2.md` como arquitectura CTO candidata del
  2026-06-30;
- la v2 actualiza la cadena logica de TSIS con Data Foundation madura,
  Scanner Candidate Selection, Market State Representation, Event State,
  Outcome Research, Strategy Library, Decision Models, Execution Models,
  Evaluation Systems, Evolution Systems / AlphaEvolve y Shadow Live;
- separa explicitamente `data`, `scanner_candidate`, `market_state`,
  `event_state`, `event`, `outcome`, `strategy`, `decision_model`,
  `execution_model` y `evolution_system`;
- evita que futuros agentes confundan scanner rows, seeds controlados o
  materializaciones parciales con estado institucional ML/RL-ready;
- enlaza la arquitectura v2 con Graphify governance sin editar manualmente
  `graphify-out/graph.json`, `GRAPH_REPORT.md` ni `graph.html`.

Changed paths:

```text
00_CTO/TSIS_LAB_ARCHITECTURE_v2.md
00_CTO/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Include this architecture update in the next official 00_CTO architecture or
governance leaf rebuild. Do not perform a blind root merge. Do not manually
edit generated Graphify outputs.
```

### 2026-06-30 - Scanner Candidate Selection architecture

Estado: pending
Severidad: HIGH

Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Motivo:

- se creo la subcapa CTO
  `05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/`;
- la nueva documentacion explica scanner candidate selection como capa previa a
  `market_state` y `event_state`;
- se separa la visibilidad operacional `trade_station_like_scanner_v0_1` de
  `broad_in_play_discovery_scanner_v0_1`;
- se enlazan los contratos operativos reales de `01_foundations` sin crear una
  segunda source of truth;
- se actualizan los mapas CTO para que futuros agentes entiendan que scanner
  rows no son estados ML/RL, estrategias, labels, outcomes, rewards ni fills.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/README.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
00_CTO/TSIS_LAB_ARCHITECTURE.md
00_CTO/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Rebuild or update the Market State Representation leaf with official Graphify.
Do not manually edit graphify-out/graph.json, GRAPH_REPORT.md or graph.html.
Root graph merge is not required for this documentation step.
```

### 2026-06-28 - Graphify no-API and version-alignment protocol

Estado: leaf_built_root_not_merged
Severidad: HIGH

Slice:

```text
core_cto_graph / graphify_governance_slice
```

Motivo:

- `PROJECT_RULES.md` and `00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md` now
  distinguish upstream Graphify v0.9.1 behavior from the currently observed
  installed package version.
- The protocol now states that no external API keys are required in Codex:
  without Gemini/Google keys, semantic extraction for docs/papers/images must
  use host-agent/subagent extraction, not an invented API backend.
- Future `BUILD_MANIFEST.md` files must record package version, skill/source
  version, upstream reference, no-API mode and semantic coverage.

Changed paths:

```text
PROJECT_RULES.md
CHANGELOG.md
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
00_CTO/CHANGELOG.md
```

Required Graphify action:

```text
Include these governance files in the next official governance/CTO leaf.
Do not treat this queue entry as graph content or as proof of rebuild.
```

Build result:

```text
Built cross-project governance leaf:
00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/

Graphify package: graphifyy 0.9.1
Semantic mode: Codex host inline extraction, no external API required
Nodes: 37
Edges: 60
Communities: 9
Diagnostic: clean
Root graph merge: not performed
```

### 2026-06-28 - Graphify build baseline provenance rule

Estado: leaf_built_root_not_merged
Severidad: HIGH

Cambios:

- `C:\TSIS_Data\PROJECT_RULES.md`
- `00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
- `00_CTO/CHANGELOG.md`

Motivo:

- los proximos builds Graphify deben dejar un baseline Git reconstruible;
- cada `BUILD_MANIFEST.md` nuevo debe registrar commit, dirty state, corpus
  exacto, cobertura de queue, diagnostico y comandos de delta;
- sin estos campos no se puede calcular con rigor que cambio desde el ultimo
  grafo.

Accion recomendada:

```text
Incluir esta regla en el proximo refresh del leaf de gobernanza Graphify de
00_CTO o del slice CTO afectado. No crear ni modificar graph.json a mano.
```

Root action:

```text
No root merge por esta entrada de forma aislada.
```

Build result:

```text
Covered by:
00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/BUILD_MANIFEST.md

The manifest records graphify package version, skill path/hash, upstream
reference, no-API mode, semantic extraction mode, commit, dirty state, exact
corpus, diagnostics and next-delta commands.
```

### 2026-06-28 - Strategy Library trader-source reorganization

Estado: pending
Severidad: CRITICAL

Cambios:

- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/01_Steven_Dux/`
- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/03_Edu_Trades/`
- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/04_Xavineta/`
- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/`
- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/`
- `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/`
- Steven Dux source references to external transcript and Duxinator roots.

Motivo:

- separa enseñanzas fuente por trader de estrategias/factores TSIS propios;
- mueve documentos, assets e indices de Steven Dux fuera de `LONG/stevenDux`,
  `SHORT/stevenDux`, `FACTORS/stevenDux` y `source_assets/steven_dux`;
- mantiene `LONG/`, `SHORT/` y `FACTORS/` como espacios TSIS para estrategias
  y factores consolidados o en investigacion;
- actualiza enlaces fuente a transcripts organizados por video en
  `E:\TSIS_YOUTUBE\00_TRADERS\00_Steven_Dux\TRANSCRIPTS\` y al root activo
  `E:\00_TRADING\04_Steven_Dux\Duxinator\...`;
- altera rutas que Graphify puede conservar como nodos antiguos.

Accion recomendada:

```text
Rebuild del leaf Trading Systems en ventana dedicada.
No integrar root sin limpiar/reemplazar el slice antiguo.
```

### 2026-06-25 - Market State Representation contract

Estado: leaf_built
Severidad: HIGH

Cambios:

- `11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md`
- `11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md`

Motivo:

- nuevo contrato conceptual `candidate_policy`;
- define Market State Representation como eje comun entre Data Foundation,
  Event Engine, ML, Offline RL, live learning y AlphaEvolve;
- incorpora justificacion cientifica directa y una lectura obligatoria de las
  referencias que conectan estados, Offline RL, distribution shift, LOB
  modeling, LOB simulation, evaluadores de program search y causal ML;
- altera el mapa semantico que futuros agentes deben consultar.

Accion requerida:

```text
Rebuild leaf:
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION

Despues decidir si se actualiza el leaf de 11_MARKET_SCIENCE o el root CTO.
No editar graphify-out manualmente.
```

Build result:

```text
Output:
00_CTO/graphify-out/leaf_slices/market_state_representation_20260628/

Stats:
- corpus_files: 2
- detected_words_approx: 4035
- extraction_nodes: 60
- extraction_edges: 84
- nodes: 60
- edges: 83
- communities: 7

Validation:
- graphify diagnose multigraph passed with 0 missing endpoints, 0 dangling
  endpoints, 0 self-loops and 0 exact duplicate edges.
- graphify explain passed on node `Market State Representation`.
- BUILD_MANIFEST.md includes graph_build_git_commit, dirty state, exact corpus,
  queue coverage, diagnostics and next-delta commands.

Root:
- 00_CTO root graph intentionally not updated.
```

### GFQ-20260623-001 - Long strategy definitions for DAS and Breakout

Status: `pending`

Severity: `MEDIUM`

Slice:

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/
```

Reason:

- Added initial `STRATEGY.md` definitions for DAS and Breakout.
- Added the exploratory DAS notebook stack for first-push, first-dip and
  first-push-high rebreak sample discovery.
- Reworked DAS sample discovery to be scanner-first: screener appearance is the
  candidate unit, while push/dip/rebreak are downstream diagnostics.
- Added DAS `green_wick_dip_reactivation` semantics for wick dips inside green
  continuation candles after first-push rebreak, with notebook diagnostics and
  chart markers.
- Added a static DAS premarket-only detail chart for focused event-day
  premarket review.
- Reworked DAS chart sizing toward square canvases so vertical price structure
  is easier to inspect without shrinking the X-axis.
- Adjusted DAS chart layout to reduce volume-panel height, lower chart
  footprint and separate title/legend text.
- Replaced inherited Gap and Go gap-measurement lines in DAS charts with a
  dedicated premarket-open-to-first-push measurement.
- Updated LONG Strategy Library navigation and documented the pilot sequence
  `gap&go -> DAS -> Breakout`.
- The change affects how future agents should locate and interpret long-side
  strategy research, but does not promote event definitions or rebuild Graphify.

Changed paths:

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_widgets.py
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_case_explorer.ipynb
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/Breakout/STRATEGY.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Batch with the next Trading Systems strategy-library Graphify refresh.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- These are exploratory strategy definitions for sample discovery and later
  Event Library v0 decomposition, not promoted strategy contracts.

### GFQ-20260622-001 - CTO and root test topology scaffold

Status: `pending`

Severity: `MEDIUM`

Slice:

```text
00_CTO/tests/
tests/institutional/
```

Reason:

- Added CTO-specific test governance folders for architecture contracts,
  governance contracts and private/public consistency.
- Added root monorepo test documentation to separate global institutional
  gates from module-owned executable tests.
- The change affects how future agents should locate and classify tests, but
  does not add executable validators yet.

Changed paths:

```text
tests/README.md
tests/institutional/README.md
tests/test_runs/README.md
tests/fixtures/README.md
tests/third_party_evidence/README.md
00_CTO/tests/README.md
00_CTO/tests/architecture_contracts/README.md
00_CTO/tests/governance_contracts/README.md
00_CTO/tests/private_consistency/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Batch with the next CTO governance/architecture documentation refresh.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- This is a test topology and navigation scaffold, not a CI implementation.

### GFQ-20260621-003 - EduTrades Long Plays visual event source index

Status: `pending`

Severity: `MEDIUM`

Slice:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY/
```

Reason:

- Added a visual Event Library source note derived from EduTrades long-play
  material.
- The document stores the copied source markdown under `source_assets/`, uses
  existing EduTrades image assets, and translates strategy/discretionary wording
  into 12 event-search candidate definitions plus transverse context filters.
- No promoted event definitions, detectors or strategies were created.

Changed paths:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/EDUTRADES_LONG_PLAYS_SOURCE_EVENT_INDEX_v0_1.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/source_assets/edu_trades/07_Long_plays.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/source_assets/edu_trades/
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Batch with next Event Library source-note/documentation refresh.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- This is source-note evidence for Event Library, not a promoted event, not a
  detector and not a strategy.

### GFQ-20260621-002 - Data Foundation real-time corporate alerts output target

Status: `pending`

Severity: `HIGH`

Slice:

```text
TSIS_LAB_ARCHITECTURE.md
```

Reason:

- CAPA 1 Data Foundation output targets now include
  `real_time_corporate_event_alerts_table`.
- This aligns the promoted architecture with the module-level output contract
  that documents the missing governed low-latency alerts stream for offerings,
  SEC filings, warrants, reverse splits and comparable smallcap catalysts.
- The operational contract remains under
  `01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/`.

Changed paths:

```text
00_CTO/TSIS_LAB_ARCHITECTURE.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include in the next CTO architecture leaf refresh. Do not force root rebuild
only for this change unless a root architecture query requires it.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
AlexJ / TSIS CTO
```

### GFQ-20260621-001 - Mosquito Small Caps visual event source index

Status: `pending`

Severity: `MEDIUM`

Slice:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY/
```

Reason:

- Added a visual Event Library source note derived from external discretionary
  small-cap trader material.
- The document embeds copied source images, stores the source markdown under
  `source_assets/`, and translates strategy/discretionary wording into 20
  event-first candidate phenomena.
- No promoted event definitions, detectors or strategies were created.

Changed paths:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/MOSQUITO_SMALLCAPS_SOURCE_EVENT_INDEX_v0_1.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/source_assets/mosquito_smallcaps/La-Formula-Exacta-para-Entrar-en-Trades_Media_4Xh34AFFGJc_001_1080p_pdf.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/source_assets/mosquito_smallcaps/img/
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Batch with next Event Library source-note/documentation refresh.
```

Root action:

```text
No immediate root update.
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- This is source-note evidence, not a promoted event and not a detector.

### GFQ-20260620-002 - DAS event draft definition

Status: `leaf_refreshed`

Severity: `MEDIUM`

Slice:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/
```

Reason:

- Added the first draft event definition for `DAS_Event` / `Dips After
  Squeeze`, including variants, behavioral mechanism hypothesis, recurrent
  sequence indexing and explicit event/strategy boundary.

Changed paths:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Absorbed by Trading Systems leaf refresh.
```

Root action:

```text
No immediate root update.
```

Leaf refresh:

```text
00_CTO/graphify-out/leaf_slices/trading_systems_event_first_20260620/
nodes: 313
edges: 408
communities: 20
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- This is a draft definition, not a promoted event and not a detector.

### GFQ-20260620-001 - Event Library behavioral mechanics guide

Status: `leaf_refreshed`

Severity: `MEDIUM`

Slice:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY/
```

Reason:

- Added a draft Event Library guide for documenting behavioral mechanics,
  trader psychology, game-theoretic pressure and crowd dynamics inside event
  definitions while preserving the event/strategy boundary.

Changed paths:

```text
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/EVENT_BEHAVIORAL_MECHANICS_GUIDE_v0_1.md
00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Absorbed by Trading Systems leaf refresh.
```

Root action:

```text
No immediate root update.
```

Leaf refresh:

```text
00_CTO/graphify-out/leaf_slices/trading_systems_event_first_20260620/
nodes: 313
edges: 408
communities: 20
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Owner:

```text
AlexJ / TSIS CTO
```

Notes:

- Do not rebuild Graphify immediately for this isolated draft guide.

### GFQ-20260618-001 - Trading Systems event-first root integration

Status: `pending_root_integration`

Severity: `CRITICAL`

Slice:

```text
13_TRADING_SYSTEMS/
```

Reason:

- `13_TRADING_SYSTEMS/` fue refactorizado fisicamente a estructura event-first.
- El leaf Graphify event-first ya fue construido y diagnosticado.
- El root actual todavia conserva nodos de rutas historicas como
  `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/`.

Current leaf:

```text
00_CTO/graphify-out/leaf_slices/trading_systems_event_first_20260620/
```

Leaf verification:

```text
nodes: 313
links: 408
hyperedges: 10
communities: 20
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Blocked root action:

```text
Do not run blind graphify merge-graphs into root.
```

Next valid root actions:

- rebuild root from current official leaves;
- or use an official Graphify slice-replacement flow if available in a future
  Graphify version.

## Entry template

```text
### GFQ-YYYYMMDD-NNN - <title>

Status: pending | leaf_built | pending_root_integration | closed | cancelled
Severity: LOW | MEDIUM | HIGH | CRITICAL
Slice:
Reason:
Changed paths:
Recommended action:
Root action:
Owner:
Notes:
```
