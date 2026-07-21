## 2026-07-21 | 03_TABLES_feature_engineering | Experimental State Builder probe scaffolded and smoked

- Added `05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/` with a non-production `contract_check_only` probe, versioned config, run output root and smoke readout.
- Executed smoke run `experimental_state_builder_probe_v0_1_20260721T091253Z`: 12 objects checked, 48 dry-run resolution snapshots, 0 failures, 21 source-binding warnings, 1 expected block and 0 blocked-capability leaks.
- First engineering finding: active source aliases need governed experimental physical bindings before path/schema checks or data-read probes.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Builder Validation v1 designs completed

- Completed Builder Validation design coverage for all 12 `TSIS Market Ontology v1` Information Objects.
- Added designs for `Liquidity`, `Market Microstructure State`, `Order Flow Pressure`, `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context` and `Halt Context`.
- Kept `Order Flow Pressure` blocked pending trade-quote alignment, side classifier and classifier confidence policy.
- Added `experimental_state_builder_boundary_v0_1.md` to define the next step as a non-production experimental builder, not a production builder.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Builder Validation first batch added

- Added Builder Validation designs for `Price Movement`, `Price Location / Structure` and `Volatility / Range State`.
- Added a Phase B ratification artifact for the existing `Trading Activity` builder validation pilot and aligned the pilot boundary with the frozen ontology / open Phase B state.
- Updated the Builder Validation inventory and local handoff so the first batch is `design_ready_pending_execution`.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized by this batch.

## 2026-07-21 | 03_TABLES_feature_engineering | Operational Mapping v1 batch completed

- Completed governed Phase B Operational Mapping coverage for all 12 `TSIS Market Ontology v1` Information Objects.
- Added mappings for `Volatility / Range State`, `Liquidity`, `Market Microstructure State`, `Order Flow Pressure`, `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context`, `Halt Context`, and a Phase B ratification artifact for `Trading Activity`.
- Updated the Operational Mapping inventory and handoff so the next gate is `Builder Validation`; `Order Flow Pressure` remains State-blocked until trade-quote alignment, side classifier and confidence policy are governed.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by these mappings.
## 2026-07-21 | 03_TABLES_feature_engineering | Price Location Structure Operational Mapping added

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_location_structure_operational_mapping_v0_1.md` as the next governed Phase B Operational Mapping.
- Mapped the core `Price Location / Structure` profile to legal session-open and prior-close anchors while keeping VWAP distance, HOD/LOD proximity, range position, anchored VWAP and pullback/retrace behind later gates.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by this mapping.
## 2026-07-21 | 03_TABLES_feature_engineering | Price Movement Operational Mapping added

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_movement_operational_mapping_v0_1.md` as the first governed Phase B Operational Mapping after the ontology freeze.
- Mapped the core `Price Movement` profile to legal prior-close, session-open and closed-bar return references while keeping speed, acceleration, momentum and reversal/fade behind later gates.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by this mapping.
## 2026-07-21 | 03_TABLES_feature_engineering | TSIS Market Ontology v1 frozen

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_FREEZE.md` as the institutional freeze act for `TSIS Market Ontology v1`.
- Decision: `ontology_status = FROZEN`, `ontology_lock_status = LOCKED`, `phase_a_status = CLOSED`, `phase_b_status = OPEN` for governed engineering.
- Authorized Phase B to start with Operational Mapping while keeping production builders, State consumption, physical variables, schema/materialization and dataset promotion unauthorized until Phase B gates.
- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/AGENT.md` so future agents start from the frozen ontology state.
- Aligned the feature-engineering and Phase B boundary READMEs so Operational Mapping is active while Builder Validation and Market State Integration remain gated.
## 2026-07-06 - DAS first push/dip/rebreak semantics v0.2 smoke

## 2026-07-07 - Quotes D-to-E transfer approved

- Approved `E:/TSIS/data/quotes_` as the official E-root quotes dataset for the `D:/quotes` recovery transfer.
- Evidence basis: Phase A structural parity passed for all `5207` tickers; Phase B full SHA256 original shard hash-read exceptions were resolved by targeted retry `quotes_parity_sha256_hash_error_retry_20260707` with `6/6` parity OK and zero mismatches.
- Documents with pre-approval `D:/quotes` lineage now require rebuild against the approved E-root before any official downstream promotion.

- Updated `das_widgets.py` first push logic to follow the human DAS sequence: first green expansion after awakening, first push high before the first red pullback, first dip low inside the first red/non-green pullback sequence, then rebreak of the first push high.
- Updated rebreak validity to require a green candle with high and close above `first_push_high`, plus volume at least equal to the dip-low candle volume.
- Smoke `CYTO 2024-03-25` passed visual manifest validation with 5 labels and generated review image `C:/Users/AlexJ/TSIS_smoke_review/CYTO_2024-03-25_visual_contract_threshold50_v02_semantics.png`.
- Human review is still required before treating v0.2 semantics as accepted.
## 2026-07-06 - Validador visual y manifest label-level para experimento DAS

- Creado `00_TSIS_Lab/06_validators/validate_visual_inspection_manifest.py` para validar evidencia visual label-level en runs de experimento.
- Anotado `06_validators/` en el README del Lab y actualizado `EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md` con el comando de validacion ejecutable.
- Adaptado `00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py` para exportar `visual_inspection_manifest.parquet`, `visual_inspection_manifest.csv`, imagen contractual de inspeccion y sidecar JSON de labels.
- Smoke `XAGE 2025-04-14`: deteccion DAS passed, PNG export passed, `visual_inspection_manifest` generado, 5 labels, 1 visual case, validador visual `PASS`.
## 2026-07-05 - execution_protocol.md para EXP_DAS_FRONTSIDE_DISCOVERY_0001

- Creado `00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md`.
- Definida la ejecucion reproducible de `SWEEP_001_frontside_operability_boundary`: inputs, preflight, embudo DAS, metricas, baselines, gates anti-basura, memoria de candidatos, output root y relacion futura con AlphaEvolve.
- Aclarado que el notebook queda como inspeccion humana y que la verdad reproducible debe venir de executor + manifest + evidence report.
## 2026-07-05 - SWEEP_001 reformulado como frontera de operabilidad DAS/frontside

- Renombrado `SWEEP_001_momentum_threshold_sensitivity.yaml` a `SWEEP_001_frontside_operability_boundary.yaml`.
- Aclarado que `+50%` fue una criba humana de operabilidad frontside, no una entrada, evento validado ni threshold optimo.
- Declarado que valores bajo `50%` son grupo de control, `50%` es suelo humano a auditar y valores superiores miden intensidad/sobreextension posible.
## 2026-07-05 - EXP_INTRADAY_MOMENTUM_EXTENSION_0001 archivado

- Movido `00_TSIS_Lab/04_experiments/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/` a `00_TSIS_Lab/04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/`.
- Marcado el experimento como `archived_superseded` y `superseded_by: EXP_DAS_FRONTSIDE_DISCOVERY_0001`.
- Actualizadas las referencias activas para que el experimento inicial operativo sea `EXP_DAS_FRONTSIDE_DISCOVERY_0001`.
- `intraday_momentum_extension` queda conservado como concepto/familia futura posible, no como experimento activo.
## 2026-07-05 - EXP_DAS_FRONTSIDE_DISCOVERY_0001 creado en TSIS Lab

- Creado `00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/` como primer experimento `strategy_seeded_event_discovery` para DAS/frontside.
- Anotados `research_design.md`, `parameter_space.yaml` y `SWEEP_001_frontside_operability_boundary.yaml` con corpus en espanol: origen humano del screener, semillas no validadas, gramatica `scanner seed -> awakening -> first push -> first dip -> rebreak -> DAS sequence -> outcome`, y ruta para descubrir importancia de factores por capas.
- Actualizado el registro de experimentos y el README del Lab. AlphaEvolve queda deshabilitado hasta que existan executor, validators, evidence reports y promotion gates.
## 2026-07-05 - Eliminado ARCHITECTURE_OVERVIEW y alineadas lecturas raiz

- Eliminado `ARCHITECTURE_OVERVIEW.md` porque la autoridad arquitectonica vigente vive en `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`.
- Actualizados `README.md`, `START_HERE.md`, `AGENTS.md`, `PROJECT_RULES.md`, `00_CTO/README.md`, `00_CTO/LOCAL_RULES.md`, `01_TSIS_backtest_SmallCaps/README.md` y referencias activas relacionadas.
- La lectura raiz queda alineada con TSIS como `Scientific Discovery Engine`, `00_TSIS_Lab` como laboratorio transversal y `research_experiment` como unidad cientifica central.
## 2026-07-05 - Root operating documents aligned with TSIS v3

- Updated `PROJECT_OPERATING_SYSTEM.md` to define TSIS as a Scientific Discovery Engine, add `00_TSIS_Lab`, preserve `01_TSIS_backtest_SmallCaps` as the operational SmallCaps research/backtest module, and replace the old linear flow with the v3 experiment/evidence/knowledge pipeline.
- Updated `RESEARCH_PHILOSOPHY.md` as the root philosophy synthesis while leaving `00_CTO/01_RESEARCH_PHILOSOPHY/` as the deeper CTO library.
- Updated `VERSIONING_STANDARDS.md` with versioning rules for `research_experiment`, sampling probes, parameter sweeps, evidence reports, knowledge objects, representation candidates, and AlphaEvolve/autonomous generator runs.
## 2026-07-05 - AlphaEvolve aligned with Scientific Discovery Engine

- Updated CTO AlphaEvolve docs so AlphaEvolve is defined as a generator of candidate research experiments under the Scientific Validation Pipeline.
- Added `00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md`.
- Updated autonomous research system references and `TSIS_LAB_ARCHITECTURE_v3.md` required reads.
## 2026-07-05 - Superseded CTO architecture archive

- Moved `00_CTO/TSIS_LAB_ARCHITECTURE.md`, `00_CTO/TSIS_LAB_ARCHITECTURE_v2.md`, and `00_CTO/00_CTO_REFACTOR_PLAN.md` to `00_CTO/_archive/superseded_architecture_2026_07_05/`.
- Updated active references to use `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md` as the current CTO architecture.
## 2026-07-05 - TSIS Lab Architecture v3

- Created `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md` as the active CTO architecture reading.
- Reframed TSIS as a Scientific Discovery Engine with `research_experiment` as the central unit of work.
- Updated the Market State v3 map so market_state/event_state/outcomes are the observable X/Y base for experiments, not the whole discovery architecture.
## 2026-07-05 - TSIS Scientific Discovery Engine / 00_TSIS_Lab

- Created `00_TSIS_Lab/` as the central operational lab for reproducible TSIS research experiments.
- Added initial lab contracts, registries, templates, and seed experiment `EXP_INTRADAY_MOMENTUM_EXTENSION_0001`.
- Added Research Philosophy documents under `00_CTO/01_RESEARCH_PHILOSOPHY/` to define TSIS as a Scientific Discovery Engine.
- Clarified that AlphaEvolve is a candidate experiment generator, not the authority; scientific validation remains the acceptance layer.
## 2026-07-04 - Mandatory data plane reading for minute work

- Promoted `E:/TSIS/data/README.md` to mandatory base reading for agents.
- Declared `E:/TSIS/data/ohlcv_1m` as the canonical physical root for minute/OHLCV 1m work.
- Reason: prevent future agents from using historical minute roots, treating raw 1m as corrected in place, or bypassing governed repair overlays after the 1m impossible-candle / quote-guarded LT1B incident.
- Queued the semantic change in `00_CTO/GRAPHIFY_REFRESH_QUEUE.md` and `01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md` for the next official Graphify refresh.

## 2026-06-29 - Master intraday quote-guarded candidate route

- Documented the `master_intraday_bar_table_v0_2_candidate_quote_guarded`
  route without materializing or promoting a new parquet dataset.
- Preserved `master_intraday_bar_table_v0_1` as a scoped pilot.
- Declared the active bridge lineage:

```text
repair_run_root = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
minute_root = E:/TSIS/data/ohlcv_1m
quotes_root = D:/quotes
future_official_root = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
```

- Blocked final materialization until the official E-root quote-guarded repair
  manifest and final validation report exist.
- Clarified that the candidate table consumes a repair-manifest overlay:
  `raw ohlcv_1m + repair_manifest = quote-guarded view`. It does not require
  or imply a complete corrected OHLCV 1m parquet tree.
- Added a preflight config and pytest contract guard to prevent accidental
  full-universe or v0.1 overwrite claims.

## 2026-06-29 - Controlled market/event state candidate tables

- Added controlled candidate builders for the state-table loop:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_market_state_table.py --materialize-candidate
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_table.py --materialize-candidate
```

- Materialized candidate outputs under the governed E-root output area:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
```

- Results:
  - `market_state_table_v0_1_candidate`: 50 rows, 9 tickers, 50 event windows,
    50 event-context candidate rows, zero ML/RL/full-universe rows.
  - `event_state_table_v0_1_candidate`: 50 rows, 9 tickers, 25 pre-event rows,
    25 post-event-review rows, 50 pattern-discovery rows, zero ML/RL/full-
    universe rows.
- Both candidates inherit provisional `D:/quotes` lineage from the upstream
  microstructure candidate and require rebuild after `E:/TSIS/data/quotes_`
  parity/audit.
- Added executable tests proving candidate materialization, prohibited-prefix
  absence, as-of legality, label/outcome/reward separation and non-promotion:

```text
python -m pytest tests/data_foundation_outputs/test_market_state_table_contract.py tests/data_foundation_outputs/test_event_state_table_contract.py -q
```

## 2026-06-29 - Daily scanner candidates builder and controlled replay

- Added the Module 01 builder for controlled daily scanner replay:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table.py
```

- Added deterministic builder smoke test:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
```

- Ran the first controlled replay, not an official E-root materialization:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

- Replay result: 30,646 evaluated rows across 6 sessions, 150 TradeStation-like
  top-25 rows, 3,196 broad-discovery rows, 2,383 broad-discovery rows below
  500k volume, zero duplicate logical keys and ML/RL/live flags all false.
- Documented the scanner replay output-root policy: small samples/tests/demos
  go under `C:/TSIS_Data/tests/test_runs/`, while long-range candidate replays
  go under
  `E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/`;
  the official promoted root remains reserved.
- Added the research-only notebook explorer:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/notebooks/data_foundation_outputs/daily_scanner_candidates_replay_view_v0_1.ipynb
```

## 2026-06-29 - Scanner framework and DAS discovery protection

- Added the Module 01 Data Foundation scanner framework contract:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

- Added two governed scanner-definition configs for
  `daily_scanner_candidates_table_v0_1`:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

- The scanner layer now distinguishes operational visibility replay from broad
  research discovery, so `volume_today > 500000` and `% change 1D` ranking are
  not treated as the only general scanner for DAS research.
- Future controlled scanner replay must quantify candidates discovered by the
  broad scanner but missed or detected late by the TradeStation-like scanner.

## 2026-06-29 - Daily scanner candidates target stack

- Added the Module 01 Data Foundation target stack for:

```text
daily_scanner_candidates_table_v0_1
```

- The stack defines the governed candidate-generation/in-play discovery layer
  before broad `market_state_table` construction.
- Scanner rows are explicitly candidate-set lineage, not complete market
  states, full-universe truth, labels, rewards, strategy signals, execution
  truth or direct ML/RL rows.
- The new stack includes schema, dataset contract, registry entry, consumption
  policy, validator contract, target contract and Graphify refresh queue entry.
- The `market_state_table` / `event_state_table` contracts now recognize
  scanner candidate lineage through the `scanner__` namespace while keeping it
  separate from full state composition.

## 2026-06-29 - Market-state coverage and lookback policy

- Added the Module 01 Data Foundation policy:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

- The policy makes explicit that daily in-play/scanner ticker-days are not
  complete market states.
- Future `market_state_table` / `event_state_table` builds must combine
  full-history compact context, daily scanner/event candidates and governed
  event-window microstructure, with explicit lookback policies and lineage.
- Strategies requiring historical memory, such as `Short Into Resistance`, must
  receive as-of lookback features instead of being represented only by the
  current ticker-day.

## 2026-06-29 - State-table provisional D:/quotes lineage accepted

- Accepted `D:/quotes` as provisional candidate-only quote lineage for the next
  controlled `market_state_table` / `event_state_table` loop while
  target official `E:/TSIS/data/quotes_` parity/audit remains incomplete.
- Required any state or microstructure candidate inheriting that source to
  preserve `quotes_root_used`, `quotes_root_state`,
  `target_official_quotes_root`, `legacy_incomplete_e_quotes_root` and
  `requires_rebuild_after_e_quotes_parity`.
- Corrected the target-root semantics: `E:/TSIS/data/quotes_` is the intended
  E-root produced by the active `D:/quotes` clone; `E:/TSIS/data/quotes` is an
  incomplete/legacy E-root for this recovery decision.
- The provisional allowance does not permit institutional promotion, ML/RL
  primary training, backtest-core direct use or execution simulation truth.

## 2026-06-29 - Graphify leaf Git publication policy

- Updated the root Graphify governance policy so `graphify-out/` root payloads
  remain runtime ignored by default while promoted
  `graphify-out/leaf_slices/<leaf_id>/` directories can be versioned in Git.
- Required publishable Graphify leaves to carry `BUILD_MANIFEST.md`, corpus
  manifest or equivalent, `graph.json`, `GRAPH_REPORT.md`, `graph.html` unless
  `--no-viz` is documented, and clean diagnostics or explicit limitations.
- Clarified that deterministic topology/provenance/navigation leaves are
  publishable only when their limited semantic coverage is declared visibly and
  they are not presented as full semantic Graphify extraction.

## 2026-06-29 - Data certification topology Graphify leaf built

- Built the `00_data_certification` topology refresh leaf at:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260629/
```

- Build result: 88 corpus files, 122 nodes, 653 edges, 11 communities, clean
  `graphify diagnose multigraph` result with 0 missing endpoints, 0 dangling
  endpoints, 0 self-loops and 0 duplicate or collapsed edges.
- The leaf uses `graphifyy 0.9.1` and records modern build provenance, but is a
  deterministic topology refresh; it does not replace the full semantic
  `certification_decisions_20260619` leaf.
- No `00_data_certification` root graph was created or merged.

## 2026-06-29 - Cross-project Graphify governance leaf built

- Upgraded the active Graphify package from `graphifyy 0.8.40` to
  `graphifyy 0.9.1` and reinstalled the Codex Graphify skill before building.
- Built the cross-project Graphify governance leaf at:

```text
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/
```

- The leaf covers root governance, `00_CTO`, `01_foundations`,
  `00_data_certification`, refresh queues, no-API semantic extraction rules,
  build-manifest provenance rules and long-running-operation observability.
- Build result: 37 nodes, 60 edges, 9 communities, clean
  `graphify diagnose multigraph` result with 0 missing endpoints, 0 dangling
  endpoints, 0 self-loops and 0 duplicate or collapsed edges.
- No root graph merge was performed. Larger root refreshes remain pending by
  bounded slice.

## 2026-06-28 - Graphify no-API and version-alignment rule

- Added the root Graphify no-API rule: missing API keys must not block a
  Graphify semantic build in Codex; docs/papers/images must use the Graphify
  skill with host-agent/subagent semantic extraction when no Gemini/Google API
  is configured.
- Clarified that CLI `graphify update` is not enough to prove semantic coverage
  for markdown contracts, papers, images or research documents.
- Required future Graphify build manifests to record installed package version,
  skill/source version, upstream reference, no-API mode and semantic extraction
  coverage before a build can serve as an official baseline.

## 2026-06-28 - Graphify build baseline provenance rule

- Added a root Graphify baseline rule requiring future `BUILD_MANIFEST.md`
  files to record commit, dirty state, exact corpus, queue coverage,
  diagnostics and next-delta commands.
- Required future Graphify rebuilds to preserve enough Git provenance for:

```powershell
git diff --name-status <graph_build_git_commit>...HEAD
git status --short
```

## 2026-06-27 - Long-running operations observability contract

- Added `LONG_RUNNING_OPERATIONS_CONTRACT.md` as a root TSIS contract.
- Root governance now requires pre-manifest, PID manifest, heartbeat, timestamps,
  live logs, compact progress-line monitor command and final manifest/summary
  for long-running operations across all modules.
- The first instrumented Module 01 runners are:
  `scripts/run_1m_split_normalized_materialization.ps1` and
  `scripts/data_ops/clone_quotes_to_staging.ps1`.

`CHANGELOG.md` es:

```text id="cl1"
la memoria histÃ³rica oficial del proyecto
```

Ahora mismo estÃ¡ vacÃ­o (â€œLâ€) 
y eso es normal al empezar.

---

# Lo MÃS importante

NO es:

```text id="cl2"
â€œun log tÃ©cnico giganteâ€
```

NO es:

```text id="cl3"
â€œtodos los commits pegadosâ€
```

NO es:

```text id="cl4"
â€œhistorial Git duplicadoâ€
```

---

# Entonces:

# Â¿quÃ© es realmente?

Es:

```text id="cl5"
historia semÃ¡ntica institucional
```

---

# Git ya guarda:

* lÃ­neas cambiadas
* commits
* archivos

---

# CHANGELOG guarda:

```text id="cl6"
quÃ© cambiÃ³ conceptualmente
```

---

# Ejemplo REAL

Git commit:

```text id="cl7"
feat: add universe active status filters
```

Eso estÃ¡ bien para Git.

---

# Pero CHANGELOG debe decir:

```text id="cl8"
v0.3.0
- Universe Builder formalized
- delisted handling introduced
- historical universe reconstruction stabilized
```

---

# Entonces:

# CHANGELOG responde:

```text id="cl9"
cÃ³mo evolucionÃ³ TSIS
```

NO:

```text id="cl10"
quÃ© lÃ­neas cambiaron exactamente
```

---

# QuÃ© pondrÃ­a yo en tu caso

Ahora mismo probablemente:

```md id="cl11"
# TSIS Changelog

Todos los cambios institucionales relevantes del proyecto se registran aquÃ­.

El objetivo NO es duplicar Git commits.

El objetivo es registrar:

- milestones arquitectÃ³nicos;
- cambios semÃ¡nticos importantes;
- promotion states;
- breaking changes;
- releases institucionales;
- evoluciÃ³n conceptual del sistema.
```

---

# Luego:

---

# Primera release

```md id="cl12"
## v0.1.0 â€” Initial Institutional Foundation

### Added

- monorepo TSIS structure
- governance layer
- AGENTS.md institutional contract
- PROJECT_OPERATING_SYSTEM.md
- VERSIONING_STANDARDS.md
- RESEARCH_PHILOSOPHY.md
- institutional repository architecture

### Notes

This release establishes the foundational governance and research architecture of TSIS.
```

---

# Luego mÃ¡s adelante:

```md id="cl13"
## v0.2.0 â€” Data Governance Layer

### Added

- RAW data audit layer
- dataset quality policies
- dataset manifests
- schema governance
- historical reconstruction policies

### Changed

- canonical naming authority formalized
```

---

# Luego:

```md id="cl14"
## v0.3.0 â€” Universe Builder Institutionalization

### Added

- historical universe reconstruction
- active/inactive security tracking
- delisted support
- float filtering policies
- universe manifests

### Fixed

- timestamp normalization inconsistencies

### Breaking Changes

- universe schema updated
```

---

# Lo MÃS importante

NO registrar ruido.

---

# NO hacer esto:

```md id="cl15"
- fixed typo
- changed comment
- updated import
- changed variable name
```

Eso NO pertenece aquÃ­.

Eso pertenece a Git.

---

# CHANGELOG debe registrar:

```text id="cl16"
cambios con importancia institucional
```

---

# QuÃ© tipos de cosas sÃ­ van aquÃ­

---

# SÃ­:

* nueva arquitectura
* nuevo pipeline
* nuevo schema
* nueva capa
* breaking changes
* promotion institutional
* nuevas policies
* cambios epistemolÃ³gicos
* nuevo simulador
* nueva ontologÃ­a
* nueva metodologÃ­a

---

# NO:

* pequeÃ±os fixes
* imports
* cleanup trivial
* prints
* typo fixes
* experiments temporales

---

# Lo MÃS importante

Tu proyecto tiene:

* governance
* philosophy
* architecture
* reproducibility

Entonces tu changelog debe parecer:

```text id="cl17"
historia evolutiva del sistema
```

---

# NO:

```text id="cl18"
diario tÃ©cnico caÃ³tico
```

---

# CÃ³mo lo usarÃ¡n agentes

MUY importante.

Los agentes leerÃ¡n CHANGELOG para entender:

* quÃ© evolucionÃ³
* quÃ© cambiÃ³ conceptualmente
* quÃ© es estable
* quÃ© se rompiÃ³
* quÃ© fue promocionado
* quÃ© schemas cambiaron
* quÃ© releases existen

---

# Mi recomendaciÃ³n REAL

Tu CHANGELOG deberÃ­a ser:

* corto
* semÃ¡ntico
* institucional
* estable
* limpio
* milestone-oriented

---

# Sinceramente:

# probablemente deberÃ­as pensar en Ã©l como:

```text id="cl19"
historia constitucional de TSIS
```

NO como log tÃ©cnico.

---

## v0.2.1 â€” Project-wide scientific justification standard

### Changed

- Promoted the scientific-justification requirement to root governance in
  `PROJECT_RULES.md`.
- Added the matching research-method principle to `RESEARCH_PHILOSOPHY.md`.

### Impact

- Any institutional decision across TSIS must now connect:

```text
Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta
```

- The requirement applies equally to data, contracts, audits, schemas, events,
  market states, features, ML/RL, simulators, execution, evaluators, fitness
  functions, promotion policies and downstream outputs.
- Components without sufficient direct evidence must remain explicitly marked
  as `engineering convention`, `working hypothesis`, `candidate_policy`,
  `provisional` or `exploratory`.

---

## v0.2.0 â€” Module 01 official Graphify leaf publication

### Added

- Published the first official Graphify leaf for `01_foundations`:
  `01_TSIS_backtest_SmallCaps/01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/`.
- Published the first official Graphify leaf for RAW data certification
  decisions:
  `01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_20260619/`.
- Versioned Graphify governance files for `01_foundations` and
  `00_data_certification`, including build protocols, refresh queues and
  module-local graphify contracts.

### Changed

- `origin/main` now contains the official Graphify leaf artifacts for both
  initial Module 01 graphs.
- `.gitignore` now explicitly opens the governed
  `00_data_certification` Graphify leaf path while keeping heavy runtime and
  evidence artifacts protected by default.

### Notes

The two published leaves are semantic navigation artifacts for agents and
humans. They do not replace manifests, dataset contracts, validators, physical
profiling or certification evidence.

Root Graphify graphs were intentionally not created for these scopes. The
official state is leaf-first:

```text
01_foundations -> foundations_authority_graph
00_data_certification -> certification_decisions_graph
```

### Impact

- Future agents can query the official leaf graph outputs directly from
  `main`.
- Future data-foundation table design must still combine:

```text
contract + certification + evidence + physical profiling + validator
```

- Notebook evidence remains important but is deferred to a separate future
  Graphify leaf instead of being mixed into the first certification decisions
  graph.













