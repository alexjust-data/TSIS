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

### 2026-06-25 - Market State Representation contract

Estado: pending
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
