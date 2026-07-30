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

### GFQ-20260730-001 - State provider-consumer recovery and BT-GATE-014 handoff

Status: pending
Severity: HIGH
Slice:

```text
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering
09_STATE_CONSUMPTION_BOUNDARY
BT-GATE-014 handoff
```

Reason:

```text
The canonical cold-start recovery authority and local governance were added
after the provider v0.1.2, bounded PIT probe and BT-GATE-014 handoff reached
their current state. The existing graph does not recover this route reliably.
```

Changed paths:

```text
START_HERE.md
README.md
00_CTO_APPLIED_ARCHITECTURE/CHANGELOG.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/LOCAL_RULES.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/STATE_PROVIDER_CONSUMER_RECOVERY.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/AGENT.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/99_ruta_de_trabajo.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/09_STATE_CONSUMPTION_BOUNDARY/README.md
```

Recommended action:

```text
Refresh the dedicated applied-architecture State provider-consumer leaf in a
controlled Graphify window. Verify that a BT-GATE-014 query returns
STATE_PROVIDER_CONSUMER_RECOVERY.md as the primary entry point.
```

Root action:

```text
Do not update the stale root graph additively. Integrate only through the
official Graphify protocol after this documentation is committed.
```

### GFQ-20260722-001 - TSIS root path migration

Status: pending
Severity: CRITICAL
Slice:

```text
root_path_migration_20260722
00_CTO_root_architecture_paths
TSIS_root_module_map
```

Reason:

```text
Top-level indexed roots were renamed/reordered: 00_TSIS_Lab -> 03_TSIS_Lab, 01_TSIS_backtest_SmallCaps -> 01_TSIS_DATA_FOUNDATION, 02_TSIS_webSocket_SmallCaps -> 04_TSIS_webSocket_SmallCaps, 03_TSIS_Offline_RL -> 05_TSIS_Offline_RL, 04_TSIS_Trading_voice -> 06_TSIS_Trading_voice, and 02_TSIS_BACKTEST_ENGINE was introduced as the future backtest implementation shell. Existing root graph/source locations may still contain legacy paths until a controlled rebuild.
```

Changed paths:

```text
PATH_MIGRATION_2026_07_22.md
README.md
AGENTS.md
PROJECT_OPERATING_SYSTEM.md
PROJECT_RULES.md
VERSIONING_STANDARDS.md
RESEARCH_PHILOSOPHY.md
LONG_RUNNING_OPERATIONS_CONTRACT.md
01_TSIS_DATA_FOUNDATION/
02_TSIS_BACKTEST_ENGINE/
03_TSIS_Lab/
04_TSIS_webSocket_SmallCaps/
05_TSIS_Offline_RL/
06_TSIS_Trading_voice/
```

Next action:

```text
Do not merge additively into a stale root graph. Rebuild affected leaves/root in a dedicated Graphify refresh window after Git state is clean enough to distinguish rename from content edits.
```

### GFQ-20260707-001 - Live source adapter interfaces and DasTrades CMD API system map

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/
live_source_adapter_topology
broker_api_safety_boundary
dastrades_cmdapi_system_map_local_ignored
```

Reason:

```text
Se crea la seccion de Systems Engineering para explicar como TSIS separa referencia externa, source adapter, contrato de captura, data root fisico, source parity y consumidores downstream. Incluye el boundary read-only/data-only para broker APIs y el mapa local/ignorado de DasTrades/Sage CMD API bajo `das_api/`. DasTrades/Sage CMD API queda explicitamente separado de cualquier estrategia de trading llamada DAS.
```

Changed paths:

```text
00_CTO/02_SYSTEMS_ENGINEERING/README.md
00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/README.md
00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/live_source_adapter_topology_v0_1.md
00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/broker_api_safety_boundary_v0_1.md
00_CTO/02_SYSTEMS_ENGINEERING/01_INTERFACES_AND_ADAPTERS/das_api/dastrades_cmdapi_system_map_v0_1.md  # local ignored
00_CTO/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Refrescar el leaf de Systems Engineering / Interfaces and Adapters para que Graphify pueda enrutar consultas sobre APIs live, broker safety boundaries, source adapters y DasTrades/Sage CMD API sin mezclarlo con estrategia DAS.
```

Root action:

```text
No requiere rebuild inmediato del root. Incluir en el siguiente lote oficial CTO/Systems Engineering.
```
### GFQ-20260706-001 - Validador visual de TSIS Lab

Status: pending
Severity: HIGH
Slice:

```text
03_TSIS_Lab
EXP_DAS_FRONTSIDE_DISCOVERY_0001
visual_inspection_manifest
```

Reason:

```text
Se agrego el primer validador ejecutable del Lab para evidencia visual label-level y se adapto el exporter DAS para emitir visual_inspection_manifest.parquet, sidecars de labels y un PNG contractual de inspeccion visual. El smoke XAGE ahora valida PASS para label_id, cobertura de senales, hash del renderer, checks de imagen y validacion de no solape. El EXPORT_MANIFEST.csv legacy sigue siendo insuficiente por si solo.
```

Changed paths:

```text
03_TSIS_Lab/README.md
03_TSIS_Lab/06_validators/README.md
03_TSIS_Lab/06_validators/validate_visual_inspection_manifest.py
03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py
CHANGELOG.md
```

Recommended action:

```text
Refrescar el slice de experimentos/validadores de TSIS Lab para que futuras consultas Graphify muestren que la evidencia visual debe ser label-level y ejecutable, no solo PNGs exportados.
```

Root action:

```text
No requiere rebuild inmediato del root. Incluir en el siguiente lote oficial de refresco Lab/CTO.
```
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
01_TSIS_DATA_FOUNDATION/AGENTS.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE_v2.md
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
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE_v2.md
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
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE.md
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
_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE.md
```

Reason:

- CAPA 1 Data Foundation output targets now include
  `real_time_corporate_event_alerts_table`.
- This aligns the promoted architecture with the module-level output contract
  that documents the missing governed low-latency alerts stream for offerings,
  SEC filings, warrants, reverse splits and comparable smallcap catalysts.
- The operational contract remains under
  `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/`.

Changed paths:

```text
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE.md
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
01_TSIS_DATA_FOUNDATION/01_research/README.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_framework_and_definitions_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/intraday_scanner_candidates_table_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
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
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/scripts/validate_event_candidate_tables.py
01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_event_candidate_table_validators.py
01_TSIS_DATA_FOUNDATION/tests/fixtures/data_foundation_outputs/event_candidate_tables_v0_1/
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo validator ejecutable fixture-scope;
- conectarlo con event_candidate_table_validators_contract_v0_1, schemas daily/intradia y event candidate route;
- marcar validation-on-real-table y builders/materializacion como pendientes;
- preservar que no hay tablas daily/1m materializadas ni ML/RL/AlphaEvolve habilitado.
```

### GFQ-20260704-015 - Market State event candidate builders executable fixture scope

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
Market State v3 registra que los builders de event candidate tables pasan a fixture-scope ejecutable. La ruta queda en builder executable DONE, daily controlled materialization DONE_69_rows, daily wider/E-root PENDING, intraday quote-guarded PENDING y validator run sobre tabla real amplia PENDING.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/scripts/materialize_strategy_candidate_events_table.py
01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_strategy_candidate_events_table_builder.py
tests/test_runs/2026-07-04/daily_strategy_candidate_events_from_daily_scanner_v0_3_20250102_20250110_controlled/
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
01_TSIS_DATA_FOUNDATION/CHANGELOG.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo builder ejecutable fixture-scope;
- conectarlo despues del validator ejecutable y antes de real materialization/event_windows expansion;
- preservar que daily controlled materialization existe, pero daily wider/E-root e intraday quote-guarded siguen pendientes;
- mantener ML/RL/AlphaEvolve production deshabilitado.
```

### GFQ-20260705-001 - Market State daily strategy event windows controlled candidate

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
01_foundations/scripts
market_state_event_windows_route
```

Reason:

```text
Market State v3 registra que Camino A avanza desde 69 eventos daily controlados hasta 207 event_windows controladas. La ruta queda en event_windows controlled daily expansion DONE controlled, pero wider/E-root daily, intradia quote-guarded, event_state, outcomes, ML/RL y AlphaEvolve siguen pendientes.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_strategy_event_windows_candidate.py
01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_daily_strategy_event_windows_candidate_builder.py
tests/test_runs/2026-07-05/daily_strategy_event_windows_from_69_daily_events_controlled/
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/CHANGELOG.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo Camino A event_windows controlled daily expansion DONE;
- conectarlo despues de daily_strategy_candidate_events_table controlled materialization y antes de controlled market_state/event_state fixture;
- preservar que es candidate controlado, no tabla oficial, no E-root y no full-universe;
- mantener event_state/outcomes/evaluadores/semantic representations/AlphaEvolve como pendientes.
```

### GFQ-20260705-002 - Market State RAW-to-consumption lineage gate

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_lineage_route
```

Reason:

```text
Market State v3 registra state_raw_to_consumption_lineage_contract_v0_1.md como gate DONE. A partir de ahora cada componente de estado debe explicar su trazabilidad RAW/staged -> derivada -> componente gobernado -> state builder -> consumer antes de alimentar fixtures/candidates.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- anadir nodo RAW-to-consumption lineage gate en Market State;
- conectarlo despues de Canonical State vs Representation Layer y antes de validators/builder candidates;
- preservar que no materializa tablas;
- mostrar master_daily_table_v0_1 como ejemplo cerrado y los demas componentes como pendientes de trazabilidad completa.
```

### GFQ-20260705-003 - Market State Camino A daily lineage closed

Status: pending
Severity: HIGH
Slice:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
01_foundations/module_contracts/outputs
market_state_lineage_route
```

Reason:

```text
Market State v3 registra state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md como DONE controlled. El Camino A daily queda trazado desde master_daily hasta event_windows controladas antes del fixture market_state/event_state.
```

Changed paths:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/README.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
00_CTO/CHANGELOG.md
```

Expected graph action:

```text
- marcar Camino A daily lineage DONE controlled;
- mostrar que 69 events y 207 event_windows son daily EOD controlled, no 1m;
- mantener 1m quote-guarded/micro/contexto/E-root official pendientes.
```


## GFQ-20260705-004 - Market State intradia 1m lineage upstream closed

Estado: pending_graph_refresh
Motivo: v3 Market State incorpora el lineage upstream de `ohlcv_1m` quote-guarded antes de permitir consumo como `intraday__*`.
Docs:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```

## GFQ-20260705-005 - Market State intradia 1m preflight passed

Estado: pending_graph_refresh
Motivo: v3 Market State registra que el lineage upstream 1m quote-guarded ya tiene preflight ligero passed; materializacion candidate sigue pendiente.
Docs/codigo:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/scripts/preflight_master_intraday_quote_guarded_candidate.py
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```

## GFQ-20260705-006 - Market State intradia 1m controlled sample passed

Estado: pending_graph_refresh
Motivo: v3 Market State registra muestra controlada quote-guarded passed: 60 filas, dos price views, 20 reparaciones OHLC reales, sin E-root candidate.
Docs/codigo:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/scripts/materialize_master_intraday_quote_guarded_candidate_sample.py
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```

## GFQ-20260705-007 - Market State intradia 1m scoped candidate passed

Estado: pending_graph_refresh
Motivo: v3 Market State registra scoped candidate quote-guarded passed: 21.670 filas, dos price views, 96 reparaciones OHLC efectivas, sin E-root candidate.
Docs/codigo:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
```

## GFQ-20260705-008 - Market State E-root scoped intradia 1m candidate

Estado: pending_graph_refresh
Motivo: v3 Market State registra que `master_intraday_bar_table_v0_2_candidate_quote_guarded` ya fue materializada en E-root como scoped candidate not official.
Docs/data:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet
```

---
Fecha: 2026-07-05
Area: market_state_intraday_quote_guarded_consumption
Motivo: registrar que `master_intraday_bar_table_v0_2_candidate_quote_guarded` scoped E-root ya alimenta un fixture controlado de `market_state_table_v0_1_candidate` con `intraday__*`, sin promocion oficial ni gates ML/RL.
Archivos:
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
- 01_TSIS_DATA_FOUNDATION/scripts/materialize_market_state_intraday_quote_guarded_candidate.py
- 01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_market_state_intraday_quote_guarded_candidate_builder.py
- 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
- 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
- 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
- 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
No Graphify rebuild ejecutado en esta iteracion.

## 2026-07-05 - market_state_intraday_event_candidate_route

Estado: pendiente de refresh Graphify.
Motivo: se anadio materializacion controlada/no oficial de `intraday_1m_strategy_candidate_events_table_v0_1` desde `master_intraday_bar_table_v0_2_candidate_quote_guarded`.
Archivos principales:
- `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md`
- `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md`
- `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md`
- `01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md`
- `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md`
- `01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py`
- `01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_strategy_candidate_events_from_master_intraday_qg.py`
Nota: no se ha ejecutado rebuild Graphify en este turno.

## 2026-07-05 - market_state_intraday_event_windows_route

Estado: pendiente de refresh Graphify.
Motivo: se anadio materializacion controlada/no oficial de `event_windows_table_v0_1_candidate_intraday_1m_strategy_events` desde los 5 eventos intradia quote-guarded.
Archivos principales:
- `01_TSIS_DATA_FOUNDATION/scripts/materialize_intraday_1m_strategy_event_windows_candidate.py`
- `01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_intraday_1m_strategy_event_windows_candidate_builder.py`
- `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md`
- `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md`
Nota: no se ha ejecutado rebuild Graphify en este turno.

## 2026-07-05 - market_state_intraday_event_state_route

Estado: pendiente de refresh Graphify.
Motivo: se anadio materializacion controlada/no oficial de `event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled`.
Archivos principales:
- `01_TSIS_DATA_FOUNDATION/scripts/materialize_event_state_intraday_quote_guarded_candidate.py`
- `01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_event_state_intraday_quote_guarded_candidate_builder.py`
- `01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md`
- `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md`
Nota: no se ha ejecutado rebuild Graphify en este turno.

## Pending - 2026-07-05 - HIGH - Market State Outcomes Intradia Controlado

Motivo: `market_state_tables_status_and_operating_map_2026_07_01_v3.md` registra `outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled` como `y` separado para la ruta intradia 1m quote-guarded, y cambia el siguiente paso vivo a evaluadores bloqueados.

Scope sugerido:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/
```

No refrescado todavia; pendiente de lote Graphify.

## Pending - 2026-07-05 - HIGH - Market State Event Research Design Layer

Motivo: el mapa v3 cambia el siguiente paso semantico desde evaluadores bloqueados hacia diseno experimental de eventos: sampling probes, sampling windows, parameter sweeps, exploratory statistics y event family candidates.

Archivos principales:

```text
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/event_research_design_contract_v0_1.md
```

No refrescado todavia; pendiente de lote Graphify.

## 2026-07-05 - HIGH - Scientific Discovery Engine / 03_TSIS_Lab

Estado: pending.

Motivo:

```text
Se introduce `Scientific Discovery Engine` como arquitectura superior de TSIS,
se crea `03_TSIS_Lab` como laboratorio operativo transversal y se redefine
AlphaEvolve como generador de candidate experiments sometido al mismo
Scientific Validation Pipeline que el investigador humano.
```

Leafs afectados:

```text
00_CTO/01_RESEARCH_PHILOSOPHY
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION
03_TSIS_Lab
```

Accion requerida:

```text
Rebuild/refresh Graphify en ventana dedicada; no ejecutar automaticamente en este cambio.
```

## 2026-07-05 - HIGH - TSIS Lab Architecture v3

Estado: pending.

Motivo:

```text
Se crea `TSIS_LAB_ARCHITECTURE_v3.md` como lectura CTO vigente y se actualiza
el mapa `market_state_tables_status_and_operating_map_2026_07_01_v3.md` para
alinear Market State con `Scientific Discovery Engine` y `03_TSIS_Lab`.
```

Archivos principales:

```text
00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
00_CTO/README.md
00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
03_TSIS_Lab/README.md
```

No refrescado todavia; pendiente de lote Graphify.



### 2026-07-05 - Superseded architecture docs archived after v3 promotion

Estado: pending
Severidad: LOW

Slice:

```text
00_CTO/
```

Motivo:

- se movieron `TSIS_LAB_ARCHITECTURE.md`, `TSIS_LAB_ARCHITECTURE_v2.md` y
  `00_CTO_REFACTOR_PLAN.md` a `_archive/superseded_architecture_2026_07_05/`;
- `TSIS_LAB_ARCHITECTURE_v3.md` queda como unica lectura CTO vigente;
- las referencias operativas se actualizaron para evitar que agentes nuevos
  arranquen desde doctrina superseded.

Changed paths:

```text
00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
00_CTO/_archive/superseded_architecture_2026_07_05/README.md
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE.md
00_CTO/_archive/superseded_architecture_2026_07_05/TSIS_LAB_ARCHITECTURE_v2.md
00_CTO/_archive/superseded_architecture_2026_07_05/00_CTO_REFACTOR_PLAN.md
00_CTO/README.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Include in the next official 00_CTO governance refresh. Do not manually edit generated Graphify outputs.
```

### 2026-07-05 - AlphaEvolve subordinated to TSIS Scientific Validation Pipeline

Estado: pending
Severidad: HIGH

Slice:

```text
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/
00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
00_CTO/README.md
```

Motivo:

- AlphaEvolve queda definido como generador de `candidate research experiments`;
- no es centro de TSIS ni autoridad de validacion;
- cualquier candidato humano o AlphaEvolve debe pasar por el mismo `Scientific Validation Pipeline`;
- se crea contrato explicito para inputs, outputs, superficies de mutacion permitidas y superficies prohibidas.

Changed paths:

```text
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/README.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/README.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/01_ALPHAEVOLVE_TSIS_VISION.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/00_AlphaEvolve_vs_sobreoptimizacion.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/areas_de_trabajo.md
00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/AlphaEnvolve_en_Tsis.md
00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
00_CTO/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Include in next official 00_CTO autonomous research / architecture refresh. Do not manually edit generated Graphify outputs.
```

### 2026-07-05 - Root operating documents aligned with TSIS Lab Architecture v3

Estado: pending
Severidad: HIGH

Slice:

```text
C:/TSIS_Data root documents
00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
03_TSIS_Lab/
```

Motivo:

- `PROJECT_OPERATING_SYSTEM.md`, `RESEARCH_PHILOSOPHY.md` y `VERSIONING_STANDARDS.md` pasan a leer TSIS como `Scientific Discovery Engine`;
- la unidad cientifica central queda declarada como `research_experiment`;
- `RESEARCH_PHILOSOPHY.md` queda como sintesis raiz y `00_CTO/01_RESEARCH_PHILOSOPHY/` como biblioteca extendida;
- `VERSIONING_STANDARDS.md` incorpora versionado de sampling probes, parameter sweeps, evidence reports, knowledge objects, representation candidates y runs AlphaEvolve/autonomous generator.

Changed paths:

```text
PROJECT_OPERATING_SYSTEM.md
RESEARCH_PHILOSOPHY.md
VERSIONING_STANDARDS.md
CHANGELOG.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Required Graphify action:

```text
Include these root documents in the next official architecture/operating-system refresh. Do not manually edit generated Graphify outputs.
```

### 2026-07-05 - Arquitectura raiz v3 como lectura oficial

Severidad: HIGH
Estado: pending official refresh

Cambio semantico:
- Se elimina el overview raiz obsoleto.
- La autoridad de arquitectura pasa a `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`.
- Los documentos raiz y lecturas operativas quedan alineados con TSIS como Scientific Discovery Engine, `03_TSIS_Lab` y `research_experiment`.

Paths afectados:
- `C:/TSIS_Data/README.md`
- `C:/TSIS_Data/START_HERE.md`
- `C:/TSIS_Data/AGENTS.md`
- `C:/TSIS_Data/PROJECT_RULES.md`
- `C:/TSIS_Data/PROJECT_OPERATING_SYSTEM.md`
- `C:/TSIS_Data/RESEARCH_PHILOSOPHY.md`
- `C:/TSIS_Data/VERSIONING_STANDARDS.md`
- `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
- `C:/TSIS_Data/03_TSIS_Lab/README.md`

Accion pendiente:
- Rebuild/refresh Graphify del slice CTO/root en una ventana dedicada.
- No se ejecuto rebuild en este cambio.

### 2026-07-05 - TSIS Lab DAS/frontside research experiment

Severidad: HIGH
Estado: pending official refresh

Cambio semantico:
- Se crea `EXP_DAS_FRONTSIDE_DISCOVERY_0001` como experimento strategy-seeded para convertir DAS/frontside visual en investigacion reproducible.
- El experimento declara `parameter_space.yaml`, `research_design.md`, gramatica de objetos DAS y primer sweep de sensibilidad de `momentum_trigger_pct`.
- Queda explicito que `+50%`, `500k`, `20% push`, `3% dip`, rangos de precio y session scope son semillas humanas investigables, no verdades cientificas.

Paths afectados:
- `C:/TSIS_Data/03_TSIS_Lab/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/02_registries/research_experiment_registry_v0_1.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/experiment.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/research_design.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/parameter_space.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/sweeps/SWEEP_001_frontside_operability_boundary.yaml`

Accion pendiente:
- Rebuild/refresh Graphify del slice Lab/CTO en una ventana dedicada.
- No se ejecuto rebuild en este cambio.

### 2026-07-05 - EXP_INTRADAY_MOMENTUM_EXTENSION_0001 archivado y reemplazado por DAS/frontside activo

Severidad: MEDIUM
Estado: pending official refresh

Cambio semantico:
- `EXP_INTRADAY_MOMENTUM_EXTENSION_0001` deja de ser experimento activo y pasa a archivo superseded.
- `EXP_DAS_FRONTSIDE_DISCOVERY_0001` queda como experimento activo inicial del Lab para investigar DAS/frontside desde una semilla discrecional.
- El concepto `intraday_momentum_extension` se conserva como posible familia/probe futura, pero no como ruta operativa activa.

Paths afectados:
- `C:/TSIS_Data/03_TSIS_Lab/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/02_registries/research_experiment_registry_v0_1.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/experiment.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/`
- `C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
- `C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md`

Accion pendiente:
- Incluir en el siguiente refresh Graphify del slice Lab/CTO.
- No se ejecuto rebuild Graphify en este cambio.

## 2026-07-05 - Graphify refresh batch executed

Status: leaf_built_project_root_merged
Severity: HIGH

Covered slices:

```text
graphify_governance_20260705
market_state_representation_20260705
project_current_20260705 root merge
```

Build outputs:

```text
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260705/
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/market_state_representation_20260705/
C:/TSIS_Data/graphify-out/leaf_slices/graphify_governance_20260705/
C:/TSIS_Data/graphify-out/leaf_slices/market_state_representation_20260705/
C:/TSIS_Data/graphify-out/graph.json
C:/TSIS_Data/graphify-out/project_current_20260705/
```

Build result:

```text
Governance leaf: clean diagnostic, no missing endpoints, no dangling edges, no self-loops.
Market State leaf: clean diagnostic, no missing endpoints, no dangling edges, no self-loops.
Project root merge: 464 nodes, 1507 edges, 49 communities after cluster-only.
```

Coverage notes:

```text
This batch covers the active root/CTO/Market State v3 operating-system refresh,
Scientific Discovery Engine / TSIS Lab architecture references, Canonical State
vs Representation Layer, Market State v3, quote-guarded intraday route,
RAW-to-consumption lineage, event candidate route, event windows, event_state,
outcomes candidate, and the mandatory E:/TSIS minute-data root rule.
```

Root action:

```text
C:/TSIS_Data/graphify-out/graph.json was created with official graphify merge-graphs.
The older C:/TSIS_Data/00_CTO/graphify-out/graph.json was not overwritten because
it contains legacy slice coverage and may retain stale nodes until a dedicated
CTO root replacement window.
```

Limitations:

```text
This is a deterministic curated topology refresh, not a full semantic
re-extraction of every CTO/reference/library document. Legacy pending entries
for Strategy Library, Sersan/reference-library graphs, and full CTO root cleanup
remain open unless covered by the slices above.
```


### 2026-07-05 - SWEEP_001 DAS/frontside reformulado como frontera de operabilidad

Severidad: MEDIUM
Estado: pending official refresh

Cambio semantico:
- `SWEEP_001` deja de leerse como sensibilidad generica de momentum threshold.
- Pasa a leerse como auditoria de frontera de operabilidad frontside para DAS.
- `+50%` queda declarado como criba humana historica; valores inferiores son grupo de control y valores superiores miden intensidad/sobreextension posible.

Paths afectados:
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/experiment.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/research_design.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/parameter_space.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/sweeps/SWEEP_001_frontside_operability_boundary.yaml`

Accion pendiente:
- Incluir en el siguiente refresh Graphify del slice Lab/CTO.
- No se ejecuto rebuild Graphify en este cambio.


### 2026-07-05 - EXP_DAS execution_protocol definido

Severidad: MEDIUM
Estado: pending official refresh

Cambio semantico:
- Se crea `execution_protocol.md` para `EXP_DAS_FRONTSIDE_DISCOVERY_0001`.
- La ejecucion oficial queda definida como executor reproducible + manifests + evidence reports; notebooks quedan como inspeccion humana.
- El protocolo declara inputs, preflight, output root, funnel metrics, outcome metrics, baselines, gates anti-basura, memoria de candidatos y relacion futura con AlphaEvolve.

Paths afectados:
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/README.md`
- `C:/TSIS_Data/03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/experiment.yaml`
- `C:/TSIS_Data/03_TSIS_Lab/00_CTO/01_privado2.md`

Accion pendiente:
- Incluir en el siguiente refresh Graphify del slice Lab/CTO.
- No se ejecuto rebuild Graphify en este cambio.


### GFQ-20260716-001 - SersanSistemas revised Markdown image rehome

Status: pending
Severity: CRITICAL
Slice:

```text
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/
```

Reason:

```text
Se reubican los Markdown revisados de practicas 12 a 27 para que cada practica viva directamente bajo `03_only_md_revised/<practice>/` junto a su carpeta `img/`. El wrapper temporal `03_only_md_revised/02_workshops/` se elimina. Hay un `graphify-out/` local dentro del slice afectado, por lo que las rutas indexadas pueden quedar obsoletas hasta un refresh dedicado.
```

Changed paths:

```text
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/12-practice-02/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/13-practice-03/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/14-practice-04/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/15-practice-05/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/16-practice-06/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/17-practice-07/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/18-practice-08/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/19-practice-09/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/20-practice-10/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/21-practice-11/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/22-practice-12/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/23-practice-13/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/24-practice-14/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/25-practice-15/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/26-practice-16/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/27-practice-17/
00_CTO/99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised/_operation_logs/
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
En una ventana dedicada, refrescar el leaf Graphify de `03_only_md_revised` o reconstruir el slice SersanSistemas afectado para eliminar rutas antiguas indexadas. No hacer merge aditivo al root si conserva nodos de `03_only_md_revised/02_workshops/`.
```

Root action:

```text
No se ejecuto rebuild Graphify durante esta reorganizacion. La validacion local de enlaces de imagen quedo en `_operation_logs/sersan_md_flatten_validation_20260716T105934Z/validation_manifest.json`.
```
