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

### GFQ-20260704-001 - Mandatory data plane minute-root reading

Status: pending
Severity: HIGH
Slice:

```text
root_agent_bootstrap
data_plane_physical_authority
minute_ohlcv_1m_consumption
```

Reason:

```text
Agents must always read E:/TSIS/data/README.md as part of the TSIS base context.
For minute/OHLCV 1m work, the canonical physical root is now explicitly
E:/TSIS/data/ohlcv_1m. The rule preserves the lesson from the impossible 1m
candle / quote-guarded LT1B incident: future agents must not infer minute
authority from historical paths, treat raw 1m as corrected in place, or bypass
governed repair overlays/manifests.
```

Changed paths:

```text
E:/TSIS/data/README.md
README.md
AGENTS.md
START_HERE.md
CHANGELOG.md
01_TSIS_backtest_SmallCaps/AGENTS.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the CTO/root agent-bootstrap semantic slice so graph queries surface the
mandatory data-plane reading rule and the canonical minute root.
```

Root action:

```text
No immediate root rebuild. Include in the next official CTO/root refresh batch.
```
### GFQ-20260701-001 - Market State Tables status and operating map

Status: pending
Severity: HIGH

Slice:

```text
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Reason:

```text
Added a dated CTO snapshot explaining expected state tables, component vs
candidate vs institutional state semantics, operational usage from Data
Foundation to strategy research, ML, imitation learning and offline RL, and the
current readiness matrix as of 2026-07-01.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01.md
00_CTO/11_MARKET_SCIENCE/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Refresh the Market State Representation leaf so future graph queries can find
the updated state-table readiness map and do not confuse components/scanners
with promoted market_state/event_state datasets.
```

Root action:

```text
No immediate root rebuild. Include in the next CTO/Market State leaf refresh
batch.
```

Owner:

```text
00_CTO / Market State Representation
```

Notes:

```text
No graph rebuild was performed in this change. This entry queues the semantic
update.
```

### 2026-06-30 - Scanner base eligible and in-play momentum v0.3

Estado: pending
Severidad: HIGH

Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
```

Motivo:

- la arquitectura activa de Scanner Candidate Selection cambia de `v0.2`
  base-plus-profiles a `v0.3` con dos denominadores explicitos;
- `base_eligible_smallcap_denominator` significa quien TSIS puede inspeccionar;
- `in_play_momentum_candidate_denominator` significa base eligible mas
  movimiento fuerte y tradability;
- el umbral inicial de movimiento fuerte es `50%`;
- el replay diario usa proxy EOD, no segment timing;
- `trade_station_like_profile` queda como visibilidad operativa humana;
- DAS y futuras estrategias quedan como overlays posteriores, no como parte del
  scanner global.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_base_and_in_play_momentum_contract_v0_3.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/notebook/daily_scanner_candidates_v0_3_run_inspection.ipynb
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
00_CTO/CHANGELOG.md
```

Recommended action:

```text
Refresh the Market State scanner-selection leaf so graph queries route agents
to v0.3 as the active scanner semantics and preserve v0.1/v0.2 as historical
evidence only.
```

Root action:

```text
No immediate root rebuild. Include in next CTO leaf refresh batch.
```

Owner:

```text
00_CTO / Market State Representation
```

Notes:

```text
This entry is semantic architecture. It does not promote any E-root dataset.
```

### 2026-06-30 - Scanner base universe and profiles v0.2

Estado: pending
Severidad: HIGH

Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Motivo:

- la arquitectura activa de Scanner Candidate Selection cambia de dos scanners
  independientes a un denominador base elegible con perfiles reproducibles y
  overlays posteriores por estrategia;
- `base_in_play_universe_scanner_v0_2` queda como identificador estable, pero
  su significado correcto es `base_eligible_smallcap_denominator`;
- los perfiles son flags/ranks paralelos sobre el denominador, no filtros
  secuenciales;
- `volume_today >= 500k` y `% change 1D top 25` pasan a ser
  `trade_station_like_profile_v0_2`, no filtros universales;
- `relative_volume_profile_v0_2` debe significar aceleracion de volumen
  intradia/as-of antes de promocion;
- `percent_change_profile_v0_2` debe exigir minimo declarado antes de top-N;
- `dollar_volume_tradability_profile_v0_2` queda como tradability, no alpha;
- `das_research_profile_v0_2` queda como seed provisional para overlay DAS, no
  scanner DAS final;
- `broad_in_play_discovery_scanner_v0_1` queda descompuesto en perfiles,
  razones y rankings sobre el universo base;
- se bloquea float como hard filter hasta auditar disponibilidad point-in-time;
- se anade justificacion cientifica directa con Offline RL, causal ML,
  Causal Factor Investing, DeepLOB, Kyle y order-flow toxicity;
- futuras consultas Graphify sobre scanner deben saber que v0.1 es evidencia
  historica y v0.2 es la candidate policy activa.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_base_universe_and_profiles_contract_v0_2.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_candidate_selection_architecture_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_definitions_trade_station_vs_broad_discovery_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_table_and_contract_map_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/scanner_to_market_state_promotion_path_v0_1.md
00_CTO/11_MARKET_SCIENCE/README.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md
00_CTO/TSIS_LAB_ARCHITECTURE_v2.md
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

Estado: superseded_by_2026-06-30_scanner_base_universe_and_profiles_v0_2
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
- nota posterior: esta entrada describe la creacion inicial v0.1. La
  semantica activa queda reemplazada por scanner base + perfiles v0.2 en la
  entrada `Scanner base universe and profiles v0.2`;
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

- separa enseÃ±anzas fuente por trader de estrategias/factores TSIS propios;
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

### GFQ-20260630-002 - Strategy scanner overlay policy and DAS runbook

Status: pending
Severity: HIGH
Slice:

```text
13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/
13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Reason:

```text
A transversal strategy scanner overlay policy now governs how every future
strategy consumes daily_scanner_candidates_table as a denominator, declares
which candidate denominator a notebook/run used, avoids positive-only selection
bias, and separates Data Foundation scanner rows from strategy overlays and
future market_state/event_state tables. DAS is the first applied implementation,
not an exception.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/strategy_scanner_overlay_policy_v0_1.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/DAS_SCANNER_USAGE_AND_OVERLAY_RUNBOOK_v0_1.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/DAS_CANDIDATE_STATE_TABLE_EXPERIMENTAL_SPEC_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_research/README.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Trading Systems DAS leaf and the Market State scanner-selection leaf
so graph queries can route agents from DAS notebooks to the governed scanner
denominator and overlay rules.
```

Root action:

```text
No immediate root rebuild. Include in next CTO leaf refresh batch.
```

Owner:

```text
00_CTO / DAS strategy research and scanner candidate selection
```

Notes:

```text
This entry documents architecture/navigation only. It does not promote the
scanner replay to an official E-root dataset and does not make DAS a final
institutional scanner.
```

### GFQ-20260630-003 - Intraday scanner first-push architecture

Status: pending
Severity: HIGH
Slice:

```text
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Reason:

```text
Scanner Candidate Selection now distinguishes daily coarse context from
intraday first-push detection. The architecture contract
intraday_scanner_candidates_contract_v0_1.md declares that DAS/frontside,
event-state and future ML/RL state preparation must use an ohlcv_1m-based
intraday scanner when first_cross_ts, segment, volume-to-time or
dollar-volume-to-time matter.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/intraday_scanner_candidates_contract_v0_1.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/README.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Market State scanner-selection leaf so graph queries route future
agents to intraday scanner v0.1 for first-push timing instead of daily scanner
v0.3.
```

Root action:

```text
No immediate root rebuild. Include in next CTO leaf refresh batch.
```

Owner:

```text
00_CTO / Market State Representation scanner candidate selection
```

Notes:

```text
This entry documents architecture/navigation. It does not promote the intraday
scanner replay to an official E-root dataset and does not make scanner rows
market_state, event_state, labels, rewards or strategy signals.
```

### GFQ-20260630-004 - Intraday scanner quote-guarded successor architecture

Status: pending
Severity: HIGH
Slice:

```text
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Reason:

```text
The CTO scanner architecture now records that intraday scanner v0.1 is raw
ohlcv_1m controlled replay evidence only. The next correct path is a
quote-guarded v0.2 candidate that applies the raw ohlcv_1m +
repair_manifest_lt1b_v0_1.parquet overlay before any canonical scanner
promotion for the LT1B universe.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_SCANNER_CANDIDATE_SELECTION/intraday_scanner_candidates_contract_v0_1.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Market State scanner-selection leaf so graph queries do not route
future agents from v0.1 raw replay directly to canonical/full-universe scanner
promotion.
```

Root action:

```text
No immediate root rebuild. Include in next CTO leaf refresh batch.
```

Owner:

```text
00_CTO / Market State Representation scanner candidate selection
```

Notes:

```text
No graph rebuild was performed here. This entry queues the semantic dependency
for the next official Graphify refresh.
```


### GFQ-20260704-005 - Market State observable eligibility route

Status: pending
Severity: HIGH
Slice:

```text
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/
11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/
```

Reason:

```text
Market State v3 records that observable eligibility is closed for declared scope through state_observable_eligibility_contract_v0_1.md.
Formula governance is also closed through state_derived_observables_formula_contract_v0_1.md.
The next route is state builder contract, leakage/formula/timestamp/role validators and controlled fixtures before any official market_state/event_state materialization.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Recommended action:

```text
Refresh the Market State Representation leaf so graph queries understand that observable eligibility, formula governance, timestamp policy and snapshot roles are no longer pending. State builder contract and validators still block state-table materialization.
```

Root action:

```text
No immediate root rebuild. Include in next CTO leaf refresh batch.
```

Owner:

```text
00_CTO / Market State Representation
```

Notes:

```text
No graph rebuild was performed. No market_state/event_state parquet, ML/RL dataset or AlphaEvolve evaluator was enabled by this documentation update.
```

### GFQ-20260704-006 - Market State derived formula gate

Status: pending
Severity: HIGH
Slice: 00_CTO / Market State Representation

Summary:

Market State v3 now records the derived-observable formula gate as complete for declared scope. Eligibility, formula and timestamp policy contracts are closed; next graph route should point to state builder contract and leakage/formula/timestamp/role validators before materialization.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- add formula contract node as completed gate after eligibility;
- mark formula gate no longer pending;
- route future agents to state builder contract and validators;
- preserve no-materialization/no-ML/no-RL/no-AlphaEvolve-enable boundary.

### GFQ-20260704-007 - Market State decision timestamp policy gate

Status: pending
Severity: HIGH
Slice: 00_CTO / Market State Representation

Summary:

Market State v3 now records the decision timestamp policy gate as complete for declared scope. Eligibility, formula and timestamp gates are closed; next graph route should point to state builder contract and leakage/formula/timestamp/role validators before materialization.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- add timestamp policy contract node as completed gate after formula contract;
- mark timestamp policy no longer pending;
- route future agents to state builder contract and validators;
- preserve no-materialization/no-ML/no-RL/no-AlphaEvolve-enable boundary.
### GFQ-20260704-008 - Market State snapshot roles gate

Status: pending
Severity: HIGH
Slice: 00_CTO / Market State Representation

Summary:

Market State v3 now records the state snapshot roles gate as complete for declared scope. Eligibility, formula, timestamp and role gates are closed; next graph route should point to state builder contract and leakage/formula/timestamp/role validators before materialization.

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
00_CTO/CHANGELOG.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Expected graph update:

- add snapshot roles contract node as completed gate after timestamp policy;
- mark snapshot roles no longer pending;
- route future agents to state builder contract and validators;
- preserve no-materialization/no-ML/no-RL/no-AlphaEvolve-enable boundary.
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

### GFQ-20260704-009 - Market State builder contract gate

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_event_state_builder_route
```

Reason:

```text
Market State v3 now records state_builder_contract_v0_1.md as complete for declared scope after eligibility, formula, timestamp and snapshot role gates. Future graph queries must route agents to validators and controlled fixtures next, not to another conceptual builder contract.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- add state builder contract node as completed gate after snapshot roles;
- link builder contract to eligibility, formulas, timestamp policy, snapshot roles, composition contract and coverage/lookback policy;
- route future agents to leakage/formula/timestamp/role/builder validators and controlled fixtures;
- keep official market_state/event_state materialization, ML/RL and AlphaEvolve disabled.
```
### GFQ-20260704-010 - Market State event candidate tables gate

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_event_candidate_route
```

Reason:

```text
Market State v3 now records event_candidate_tables_contract_v0_1.md as complete for declared scope. Future graph queries must show that daily/1m event tables sit between scanner candidates and event_windows/event_state.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- add event candidate tables contract node as completed gate after state builder contract;
- link daily scanner -> daily strategy candidate events -> event windows -> event_state;
- link intraday scanner -> intraday 1m strategy candidate events -> event windows -> event_state;
- mantener event tables no materializadas y ML/RL/AlphaEvolve deshabilitados.
```
### GFQ-20260704-011 - Market State event candidate table schema contracts

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/canonical_schemas/outputs
market_state_event_candidate_route
```

Reason:

```text
Market State v3 registra daily_strategy_candidate_events_table_schema_contract.md e intraday_1m_strategy_candidate_events_table_schema_contract.md como completos para el scope declarado. Las consultas Graphify deben distinguir schema contracts DONE de builders/materializacion PENDING.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodos de schema contract para tablas de eventos candidatas daily e intradia;
- conectarlos despues de event_candidate_tables_contract_v0_1.md;
- enrutar el siguiente trabajo a validators/builders y expansion de event_windows;
- mantener event tables no materializadas y ML/RL/AlphaEvolve deshabilitados.
```
### GFQ-20260704-012 - Market State event candidate validators contract

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_event_candidate_route
```

Reason:

```text
Market State v3 registra event_candidate_table_validators_contract_v0_1.md como completo para el scope declarado. Las consultas Graphify deben distinguir validators contract DONE de validators ejecutables PENDING.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo de contrato validators para event candidate tables;
- conectarlo despues de los schema contracts daily/intradia;
- enrutar el siguiente trabajo a validators ejecutables y fixtures minimos;
- mantener builders/materializacion, event_windows expansion y ML/RL/AlphaEvolve pendientes.
```
### GFQ-20260704-013 - Market State canonical representation boundary

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_representation_layer_boundary
```

Reason:

```text
Market State v3 registra state_canonical_vs_representation_layer_contract_v0_1.md como completo para el scope declarado. Las consultas Graphify deben distinguir Canonical State estable de Representation Layer mutable para AlphaEvolve/RL/ML.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo del contrato Canonical State vs Representation Layer;
- conectarlo a v3, eligibility, formula, builder y semantic_state_representation_contract futuro;
- preservar que no hay cambio de schema ni materializacion de representation candidates;
- enrutar trabajo futuro a validators, fixtures y semantic representations separadas del estado canonico.
```

### GFQ-20260704-014 - Market State event candidate validators executable fixture scope

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
01_foundations/scripts
market_state_event_candidate_route
```

Reason:

```text
Market State v3 ya puede distinguir contract DONE de validator ejecutable fixture-scope DONE. La validacion sobre tabla real sigue PENDING porque daily_strategy_candidate_events_table_v0_1 e intraday_1m_strategy_candidate_events_table_v0_1 no estan materializadas.
```

Changed paths:

```text
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
01_TSIS_backtest_SmallCaps/scripts/validate_event_candidate_tables.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_candidate_table_validators.py
01_TSIS_backtest_SmallCaps/tests/fixtures/data_foundation_outputs/event_candidate_tables_v0_1/
01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo validator ejecutable fixture-scope;
- conectarlo con event_candidate_table_validators_contract_v0_1, schemas daily/intradia y event candidate route;
- marcar validation-on-real-table y builders/materializacion como pendientes;
- preservar que no hay tablas daily/1m materializadas ni ML/RL/AlphaEvolve habilitado.
```
