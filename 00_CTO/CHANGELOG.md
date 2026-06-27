# 00_CTO Changelog

Este changelog registra cambios institucionales y semanticamente relevantes de
la capa CTO de TSIS.

No duplica Git.
No lista cambios menores.
No sustituye a `C:\TSIS_Data\CHANGELOG.md`.
No sustituye a changelogs de modulos operativos como
`01_TSIS_backtest_SmallCaps/CHANGELOG.md`.

## Scope

Este changelog cubre:

- arquitectura CTO;
- Harness agentic;
- AlphaEvolve sandbox policy;
- SersanSistemas distillation;
- operating models;
- protocolos;
- contratos de artefactos;
- cambios relevantes de estructura en `00_CTO`;
- decisiones de secuencia arquitectonica.

No cubre:

- commits normales;
- pequenos edits de README;
- typo fixes;
- runtime outputs;
- ejecuciones concretas de Harness;
- logs;
- artefactos de data audit bajo `01_foundations`;
- cambios propios de modulos operativos.

## Changelog Policy

Usar este archivo cuando cambie la arquitectura conceptual o metodologica de
`00_CTO`.

Usar `C:\TSIS_Data\CHANGELOG.md` solo para hitos globales de TSIS.

Usar `01_TSIS_backtest_SmallCaps/CHANGELOG.md` para cambios institucionales del
modulo de backtest y foundations.

No crear changelogs por Harness mientras los Harness sigan en fase de diseno.
Cuando un Harness pase a runtime operativo real, debera tener manifests,
run summaries, trace logs y, si procede, release log propio.

## Unreleased

### Added

- Added
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/STEVEN_DUX_SOURCE_STRATEGY_INDEX_v0_1.md`
  as a `source_note/draft` mapping Steven Dux source material into TSIS
  strategy-research language: visual examples, strategy candidates, measurable
  variables, crowding/dollar-block contexts and the requirement that future
  Dux-style daily strategy notebooks produce both visual review artifacts and
  statistics ledgers before any promotion.
- Added
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/First_Red_Day/STRATEGY.md`
  as the Duxinator-derived `source_note/strategy draft` for First Red Day,
  including pre-red-day semantics, multi-day runner criteria, volume/dollar
  volume requirements, range-damage math, remaining-reward formulas, required
  candidate-table fields and embedded source images from the Duxinator lesson.
- Added
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Layer_Resistance/STRATEGY.md`
  as the Duxinator-derived `source_note/strategy draft` for Double Layer
  Resistance, defining crowded ticker context, historical resistance proximity,
  intraday consolidation failure, double-layer overhead supply semantics,
  candidate states, formulas, table fields and required chart reviews for
  future short-side strategy research.
- Added the remaining Duxinator strategy/factor drafts under source-scoped
  `stevenDux/` subfolders:
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Bounce_Plus_Gap_Up_Short/STRATEGY.md`,
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Gap_Up_Buying/STRATEGY.md`,
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Intraday_Top/STRATEGY.md`,
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Parabolic_Breakout_Failed_Breakout/STRATEGY.md`,
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Dip_Buying_Multi_Day_Runner/STRATEGY.md`,
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Multi_Day_Top_Risk_Reward/STRATEGY.md`
  and
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Float_Rotation/FACTOR.md`;
  each file preserves strategy/factor semantics as draft research, defines
  measurable candidate fields for future notebooks, lists event-decomposition
  candidates and records desired screenshots from its own source video only.
- Added a Strategy Library provenance rule requiring embedded strategy images
  to come from the same primary video/document/source as the strategy being
  documented; missing images must be recorded as `Imagenes deseadas del propio
  video` instead of substituting unrelated visual evidence.
- Added
  `11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md`
  as a `candidate_policy` defining TSIS market state representation as the
  state-first foundation for Event Engine, ML, Offline RL, live learning and
  AlphaEvolve-style evaluator-driven research; the contract explicitly
  separates current state components from future institutional `market_state`
  and `event_state` objects, and clarifies that states derive from downloaded
  market data without copying all raw data into a single training table, with
  direct references to Offline RL, LOB modeling, evaluator-driven discovery and
  causal ML literature, plus an explicit note that no single paper proves TSIS
  end-to-end but the architecture is forced by convergent evidence on states,
  historical datasets, distribution shift, LOB structure, simulation,
  evaluators and causal mechanisms.
- Added
  `11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md`
  to preserve the discovered route map of TSIS files explaining market states,
  event states, Data Foundation outputs, ML/RL consumption and AlphaEvolve
  evaluator dependencies.
- Added
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/STRATEGY.md` as the initial
  long-side DAS strategy definition, separating awakening push, first dip hold,
  first-push-high rebreak, DAS sequence activation and future Event Library v0
  decomposition.
- Added
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/Breakout/STRATEGY.md` as the
  initial long-side Breakout strategy definition, including level taxonomy,
  breakout acceptance/failure semantics and future Event Library v0
  decomposition.
- Added the first exploratory DAS notebook stack under
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/`, including
  `das_widgets.py`, `das_case_explorer.ipynb` and local `runs/` containment for
  first-push, first-dip and first-push-high rebreak sample discovery.
- Reworked the DAS exploratory notebook stack to use a scanner-first workflow:
  market cap, session volume and price are hard screener filters, while push,
  dip, rebreak, VWAP context and DAS state are measured as diagnostics for
  later visual review.
- Added DAS `green_wick_dip_reactivation` semantics and notebook diagnostics
  for intrabar wick dips inside green continuation candles after first-push
  rebreak.
- Added a static DAS premarket-only detail chart with compact X-axis and tight
  Y-axis scaling for event-day premarket review.
- Reworked DAS chart sizing to use square notebook canvases and square exported
  PNGs, increasing vertical space without reducing the available X-axis width.
- Reduced DAS chart footprint by 15%, lowered the volume panel height, and split
  chart titles into multiple lines to avoid title/legend overlap.
- Replaced inherited Gap and Go percentage lines in DAS charts with a dedicated
  premarket-open-to-first-push measurement.
- Clarified the DAS strategy definition so first-push-high rebreak is an
  operative candidate worth studying, while also activating the downstream DAS
  dip sequence when not traded directly.
- Expanded the DAS strategy definition with PAVM/JFBR scanner-timing examples,
  explicit negative-case states for failed scanner-only candidates, and the
  scanner v2 refactor contract requiring first-push percentage from premarket
  open plus max-momentum percentage for the full live momentum move.
- Refined the DAS scanner v2 implementation so `min_session_volume` is measured
  as cumulative premarket volume before/during first-push construction, the
  first dip must occur after the first-push high candle, and structural rebreaks
  must occur within the initial DAS window instead of recapturing stale lower
  highs later in premarket.
- Updated DAS charts so scanner trigger labels show premarket-open gap percent,
  trigger price and cumulative volume in an offset below-price arrow annotation; `prior
  close` uses the inherited full-chart reference line again; `first push high`
  remains a bounded labeled segment; and the exploratory `push start` marker is
  removed from candidate review charts.
- Added a shared EMA8/Wilder8 momentum overlay to strategy 1m charts: bullish
  `EMA8 > Wilder8` regions use a translucent green band with green EMA/Wilder
  lines, with Wilder thicker; bearish `EMA8 < Wilder8` regions use the same
  visual grammar in red.
- Updated Strategy Library LONG navigation to document the current pilot
  sequence `gap&go -> DAS -> Breakout`.
- Added `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/` as neutral
  exploratory infrastructure for reusable strategy widgets/helpers, preventing
  direct imports from one strategy folder into another.
- Added `00_CTO/tests/` as the CTO test-governance scaffold, with dedicated
  README contracts for architecture contracts, governance contracts and private
  consistency checks.
- Added root monorepo test documentation under `tests/` and
  `tests/institutional/` to separate global institutional gates from module
  executable tests.
- Added root test artifact folders under `tests/test_runs/`, `tests/fixtures/`
  and `tests/third_party_evidence/` so test outputs, small fixtures and cached
  external evidence do not contaminate raw data roots.
- Updated root `.gitignore` and `.graphifyignore` protections so dated test
  execution outputs, junit files, pytest logs and generated artifacts are not
  committed or loaded into Graphify.
- Added
  `13_TRADING_SYSTEMS/00_EVENT_LIBRARY/EVENT_BEHAVIORAL_MECHANICS_GUIDE_v0_1.md`
  as a draft Event Library guide for documenting behavioral mechanics,
  trader psychology, game-theoretic pressure, crowd dynamics and falsifiable
  mechanism hypotheses without contaminating events with strategies.
- Added
  `13_TRADING_SYSTEMS/00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md`
  as the first draft definition for `DAS_Event` / `Dips After Squeeze`, keeping
  the observable event, behavioral mechanism hypothesis and strategy boundary
  separated.
- Built and diagnosed the updated Graphify leaf for `13_TRADING_SYSTEMS/`
  after adding the behavioral mechanics guide and DAS draft event definition.
  The leaf is stored as ignored runtime output under
  `00_CTO/graphify-out/leaf_slices/trading_systems_event_first_20260620/`.
- Added
  `13_TRADING_SYSTEMS/00_EVENT_LIBRARY/MOSQUITO_SMALLCAPS_SOURCE_EVENT_INDEX_v0_1.md`
  as a visual source-note event inventory derived from external discretionary
  small-cap trader material, including the copied source markdown, copied image
  assets, 20 candidate events and TSIS event-first interpretation of each
  candidate phenomenon.
- Added
  `13_TRADING_SYSTEMS/00_EVENT_LIBRARY/EDUTRADES_LONG_PLAYS_SOURCE_EVENT_INDEX_v0_1.md`
  as a visual source-note event inventory derived from EduTrades long-play
  material, including the copied source markdown, existing EduTrades image
  assets, 12 event-search candidate definitions, transverse context filters
  and TSIS event-first interpretation of each candidate phenomenon.
- Added `LOCAL_RULES.md` as the local operating contract for `00_CTO`,
  including authority boundaries, knowledge states, event-first architecture
  rules, Graphify policy and functional folder criteria.
- Added `TSIS_LAB_ARCHITECTURE.md` as the promoted architecture derived from
  `00_private/arquitectura.md`, covering the governed sequence from Data
  Foundation to Evolution Systems.
- Added `real_time_corporate_event_alerts_table` to CAPA 1 Data Foundation
  output targets in `TSIS_LAB_ARCHITECTURE.md`, with detailed operational
  semantics governed by the module output contract.
- Queued the corresponding CTO Graphify refresh in `GRAPHIFY_REFRESH_QUEUE.md`.
- Added `00_CTO_REFACTOR_PLAN.md` with a functional matrix for active
  top-level folders and a governed target structure for
  `13_TRADING_SYSTEMS/`.
- Refactored `13_TRADING_SYSTEMS/` into the governed event-first physical tree:
  `00_EVENT_LIBRARY`, `01_EVENT_ENGINE_MODEL`, `02_OUTCOME_RESEARCH`,
  `03_STRATEGY_LIBRARY`, `04_STRATEGY_RESEARCH`, `05_EDGE_HYPOTHESES`,
  `06_PATTERN_DISCOVERY`, `07_CLUSTER_RESEARCH`, `08_EXECUTION_MODELS`,
  `09_DECISION_MODELS`, `10_EVOLUTION_SYSTEMS`, `11_SQUEEZE_RESEARCH`,
  `90_DISCRETIONARY_FRAMEWORKS` and `99_EXPERIMENTAL`.
- Added functional READMEs for active `13_TRADING_SYSTEMS/` folders and Event
  Library event-family folders.
- Documented the official incremental Graphify update protocol for `00_CTO`
  leaf slices in `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`.
- Added a reusable agent prompt for refreshing the official `00_CTO` Graphify
  graph after recent Git changes.
- Added `GRAPHIFY_REFRESH_QUEUE.md` to stop treating Graphify like continuous
  Git state and to batch refreshes by semantic severity.
- Documented Graphify refresh cadence:
  `LOW` no refresh, `MEDIUM` queue, `HIGH` leaf rebuild, `CRITICAL` leaf rebuild
  plus explicit root decision.
- Added the historical Graphify mapping for
  `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/`:
  `core_cto_graph / trading_systems_slice`.
- Built and diagnosed the official event-first Graphify leaf for
  `13_TRADING_SYSTEMS/` after the physical refactor. The leaf is stored as
  ignored runtime output under
  `00_CTO/graphify-out/leaf_slices/trading_systems_event_first_20260618/`.

### Changed

- Expanded `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/STRATEGY.md`
  with corrected good DAS variants from annotated review images, including
  `ROLR_clean_frontside_DAS_ladder`,
  `TWG_deep_first_dip_VWAP_reclaim_rebreak`, embedded visual examples and
  required scanner v2 metrics for first-push percentage, first-push high,
  max-momentum high and momentum-end reason.
- Added the Strategy Library dependency contract: strategy folders must not
  import code, runs, notebooks, defaults or semantic helpers from other
  strategy folders; shared utilities must live in neutral infrastructure such
  as `03_STRATEGY_LIBRARY/_shared/`, or remain temporarily duplicated while
  exploratory.
- Shortened DAS exported PNG filenames while preserving full candidate metadata
  in `EXPORT_MANIFEST.csv`, preventing Windows path-length failures during
  full-run chart exports.
- Reworked DAS chart exports to generate both `event_day_premarket_detail` and
  `event_day_detail_until_1600_ny` PNG folders, omit only the selected
  diagnostic marker signals from export charts, segment the first-push-high line
  only up to the detected high, and continue exporting when an individual
  candidate is malformed while recording `EXPORT_ERRORS.csv`.
- Reworked DAS detail exports so chart 2, chart 3 and chart 4 are written
  together per candidate under
  `chart_exports/event_day_details_grouped/<candidate>/`, preserving grouped
  review context while keeping `EXPORT_MANIFEST.csv`.
- Fixed DAS and Gap&Go notebook run loading so large candidate sets avoid
  blocking on full reference enrichment, and Gap&Go now selects the first loaded
  candidate explicitly after run load.
- Reworked DAS `maxpush` review semantics so notebook sorting, labels and PNG
  names prefer the move from the first valid 04:00+ NY premarket bar to the
  first-push high, while preserving scanner-to-max-high metrics for lineage.
- Removed the DAS `green wick dip` visual marker from candidate charts while
  preserving the underlying `first_green_wick_dip_*` diagnostic fields.
- Added a DAS chart VWAP source selector: `calculated` keeps the session VWAP
  computed from OHLCV, while `raw` plots the `vw`/`vw_split_normalized` column
  carried by the 1m parquet when available.
- Expanded `TSIS_LAB_ARCHITECTURE.md` from a compact summary into a richer
  promoted architecture derived from `00_private/arquitectura.md`, preserving
  the detailed layer-by-layer rationale while cleaning encoding, current folder
  names and authority boundaries.

### Notes

- Physical folder refactor has been executed for `13_TRADING_SYSTEMS/` and the
  new event-first Graphify leaf has been built and diagnosed, but the root
  graph has not been merged with that leaf. Treat trading-system graph queries
  against `00_CTO/graphify-out/graph.json` as potentially stale until a
  controlled root rebuild or official slice-replacement flow is completed.
- New or modified trading strategy docs and PDFs under
  `13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/` must be absorbed through the
  official Graphify leaf update/rebuild flow.
- Do not use `graphify merge-graphs` as a blind update after folder renames or
  deletions. In Graphify 0.8.40, the command composes graphs and does not
  remove old slice nodes from the root graph.
- The root graph must not be declared current for `13_TRADING_SYSTEMS/` until
  the new event-first leaf has been integrated without retaining stale path
  nodes, then reclustered and diagnosed.
- Do not assume a post-commit hook updates `00_CTO` Graphify correctly. Because
  the root graph is slice-merged and includes semantic docs/PDFs/references,
  agents must follow the governed slice update protocol.
- Do not spend Graphify extraction tokens for every small Git change. Agents
  must classify refresh severity and use `GRAPHIFY_REFRESH_QUEUE.md` unless the
  current task genuinely requires an updated semantic map.
- Absorbed files in the previous trading slice update before the path refactor:
  - `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/07_Long_plays.md`
  - `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/07_Short_Plays.md`
  - `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/Day Trading en Small Caps - XVNTrading.pdf`
- Root graph after the trading slice merge:

```text
nodes: 1732
edges: 2269
communities: 166
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Event-first `13_TRADING_SYSTEMS/` leaf built after the physical refactor:

```text
nodes: 438
links: 614
hyperedges: 18
communities: 19
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

Updated `13_TRADING_SYSTEMS/` leaf after Event Library behavioral/DAS docs:

```text
nodes: 313
links: 408
hyperedges: 10
communities: 20
detected_files: 42
detected_words: 30071
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

### Pending

- Crear vocabulario canonico de estados para Data Quality Harness.
- Crear contrato de artefactos live para Data Quality Harness.

## 2026-06-18 - Official 00_CTO Graphify graph build

### Added

- Built the official root Graphify runtime graph at:
  `00_CTO/graphify-out/graph.json`
- Generated official runtime outputs:
  - `00_CTO/graphify-out/GRAPH_REPORT.md`
  - `00_CTO/graphify-out/graph.html`
  - `00_CTO/graphify-out/BUILD_MANIFEST.md`
- Added governed Graphify runtime corpus ignore pattern:
  `**/graphify-*-corpus/`

### Included

The root graph was built through official Graphify subgraph extraction,
`graphify merge-graphs`, and `graphify cluster-only`.

Included graph slices:

- shared Harness kernel;
- Data Quality Harness;
- core CTO Markdown folders;
- SERSAN distillation operational protocols, contracts, runbooks, toolchain,
  manifests and quality reports;
- `99_REFERENCE_LIBRARY/SersanSistemas/03_only_md_revised`;
- `99_REFERENCE_LIBRARY/SersanSistemas/02_workshops` textual documents detected
  by Graphify: `.md`, `.txt`, `.html`.

### Verification

Root graph after final merge:

```text
nodes: 1667
edges: 2184
communities: 164
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
exact_duplicate_edges: 0
```

### Deferred

- `02_workshops` images and videos were not absorbed in this phase because they
  are large media slices requiring a separate cost/scope decision.
- `02_workshops` JSON alignment/transcription files were checked with official
  Graphify detect and AST extraction; Graphify 0.8.40 produced `0` nodes and
  `0` edges, so they were not merged.
- `.ELD`, `.tsw` and TradeStation-specific payloads remain outside the current
  official Graphify graph until a governed transformation/import path exists.

### Notes

`graphify-out/` and `graphify-*-corpus/` are runtime reconstructible artifacts
by default. They are not canonical source of truth unless explicitly promoted
later.

## 2026-06-18 - CTO Graphify semantic graph policy

### Added

- Documented the `00_CTO` Graphify policy in `README.md`.
- Added `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md` to define what counts as an
  official Graphify build and what must never be presented as one.
- Added root `.graphifyignore` to exclude generated graph artifacts, runtime
  folders, caches, data outputs and binary model/data blobs from Graphify
  builds.
- Updated root `.gitignore` so Graphify runtime outputs and staging folders
  remain reconstructible local artifacts by default.

### Notes

The policy defines Graphify as a semantic navigation layer for Codex and future
agents, not as canonical authority.

It fixes the intended graph construction model:

- build leaf subgraphs instead of one monolithic `00_CTO` graph;
- merge `core_cto_graph`, `data_quality_harness_graph` and
  `sersan_distillation_graph` into the operating CTO graph;
- keep `reference_sersan_graph` separate and consultative by default;
- treat `graphify-out/` as rebuildable runtime output unless explicitly
  promoted with a manifest and scope record.
- use `.graphifyignore` only for technical exclusions; semantic separation
  between operating graph and reference graph remains a build-scope decision.
- keep `01_foundations` as an external operational dependency referenced by
  `00_CTO`, not as part of the default `00_CTO` graph.

### Incident correction

A manual fallback graph was generated during the first attempt and was initially
placed under the canonical Graphify path. That was incorrect: compatibility with
`graphify query`, `graphify explain` or `graphify path` does not prove that the
artifact was produced by the official Graphify pipeline.

The fallback was removed from:

```text
00_CTO/graphify-out/graph.json
00_CTO/graphify-out/GRAPH_REPORT.md
```

and quarantined at:

```text
C:\tmp\graphify_00_cto\non_official_fallback_2026-06-18
```

The temporary mirror under `C:\tmp\graphify_00_cto\phase1_outputs` was also
cleared of canonical `graph.json` / `GRAPH_REPORT.md` names.

Until Graphify itself generates the output, `00_CTO/graphify-out/graph.json`
must not exist.

### Impact

Future Graphify work on `00_CTO` must preserve the authority distinction
between CTO workspace, canonical project contracts, `01_foundations`, Sersan
distillation artifacts and external reference material.

This prevents the reference library or private/source notes from silently
dominating the operational graph used by agents.

## 2026-06-13 - Data Quality Harness historical preservation contract

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/historical_audit_preservation_and_promotion_contract.md`

### Changed

- Updated `10_DATA_QUALITY_HARNESS/README.md` to make historical audit preservation a mandatory v0.3 operating correction.
- Updated `data_audit_completion_artifact_contract.md` with a historical preflight requirement before any dataset can be promoted to modern dossier status.
- Updated the overnight runbook and prompt pack so future agents work one folder/dataset at a time and stop for human review.

### Notes

The Harness now distinguishes between:

- historical audit already completed under `01_research/01_auditoria_RAW_DATA/00_data_certification`;
- institutional promotion under `01_foundations`;
- and genuinely missing modern evidence.

This is now explicit for `additional`, `halts`, `reference` and `short`.

### Impact

Future data-audit agents must not reaudit those datasets from scratch. They must first read the historical contracts, notebooks, builders, caches, closeouts and certification files, compare them against `01_foundations`, work one folder/dataset at a time, and stop for human review before continuing.

## 2026-06-12 - Data Quality Harness single-agent correction v0.2

### Changed

- Tightened `10_DATA_QUALITY_HARNESS/README.md` around the real mature dossier standard: notebooks as inspector interfaces, resident builders, manifests, visual casepacks and image-by-image interpretation.
- Updated `data_audit_completion_artifact_contract.md` to require notebook/visual/casepack discipline comparable to `daily`, `quotes`, `trades`, `minute` and `1m_split_normalized`.
- Rewrote the overnight runbook as a single-agent execution path for the next run.
- Rewrote the prompt pack around `SINGLE_AGENT_DATA_AUDIT_COMPLETION`.
- Updated `12_TSIS_COGNITIVE_ARCHITECTURE/README.md` so the top-level index points to the corrected single-agent runbook and prompt.

### Corrected

- Removed `images_Flash_Research` from the Data Quality Harness target set for this run and marked it explicitly out of scope.
- Added explicit no-touch protection for `C:/TSIS_Data/data` in addition to `E:/TSIS/data`, module `data/`, `run/`, `runs/` and historical audit roots.
- Replaced immediate multi-agent execution guidance with one autonomous agent plus final integration.

### Impact

The next overnight data-audit agent now has a stricter contract: it must reproduce the actual inspection culture of the mature datasets, not merely create markdown/contracts. This means granular notebooks where useful, stable visuals, manifests, casepacks, and explicit `Que muestra / Responde / No responde / Consecuencia` interpretation before any dataset can be presented as mature.

## 2026-06-12 - Data Quality Harness overnight completion runbook

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/README.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/data_audit_completion_artifact_contract.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_overnight_data_audit_completion_harness_runbook.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_data_audit_agent_prompt_pack.md`

### Changed

- `12_TSIS_COGNITIVE_ARCHITECTURE/README.md`

### Notes

This update turns the Data Quality Harness from a general operating map into an
overnight-executable work plan.

The new runbook and prompt pack define:

- dataset order: `reference`, `Halts`, `financial`, `regime_indicators`,
  final integration;
- artifact contract for modern dataset closeout;
- single-agent execution guidance for the immediate run, with shared-index integration only at the end;
- the initial prompt pack for Codex agents, later tightened by v0.2;
- final integration responsibilities and acceptance criteria.

### Impact

Future agents can now work overnight on the remaining Polygon-derived data
audit without reinterpreting the whole project from chat memory.

The required quality bar is explicit: pending datasets must be closed with the
same kind of contracts, registries, policies, validators, dossiers, assets,
manifests and maturity honesty already present in the mature `daily`, `quotes`,
`trades`, `minute` and `1m_split_normalized` blocks.

## 2026-06-12 - Sersan full-corpus distillation harness run v0.1

### Added

- Project-resident full-corpus Sersan generator:
  `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/run_sersan_corpus_distillation.py`
- Project-resident Sersan artifact validator:
  `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/validate_sersan_distillation.py`
- Full-corpus run config:
  `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/sersan_corpus_distillation_config.json`
- Corpus-level readiness, run, validation and distillation reports under:
  `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/`

### Changed

- Normalized Sersan lesson-pack artifacts across the full inventoried corpus
  using the existing Sersan lesson-pack contract.
- Reprocessed the three pilot lesson packs only as needed to align with the
  corpus-level schema and validator.

### Result

- Lesson packs processed: `17`
- `pass_with_warnings`: `16`
- `blocked`: `1`
- `fail`: `0`
- Mechanical rule candidates extracted: `225`
- TSIS translation candidates created: `225`
- Images indexed: `2108`
- Independent validator result: `pass_with_warnings` with `0` errors.

### Notes

The blocked lesson is `sersan_unmapped_xxx_revised`, which remains unmapped to a
practice/workshop and requires human classification before doctrine work.

This run does not promote Sersan material to canonical TSIS doctrine. Outputs
remain mechanical-rule and TSIS-translation candidates pending human visual
review, code/XLSX semantic parsing and domain-level doctrine consolidation.



## 2026-06-12 - TSIS startup note and autonomous Codex launch

### Added

- Root `START_HERE.md` as the first human-facing TSIS startup note.
- Root `README.md` pointer to `START_HERE.md` and the autonomous Codex launcher.
- `AGENTS.md` note clarifying that `START_HERE.md` is human-facing and does not replace the agent contract.
- Reusable startup prompts for autonomous sessions, sandboxed fallback sessions and Git recovery/publication checks.
- `START_HERE.md` Prompt 4 - Puesta al dia CTO completa, requiring inventory, authority classification and verification of all relevant `00_CTO` material before architecture/Harness work.

### Notes

The startup path now distinguishes between:

1. correct autonomous TSIS sessions launched from `C:\TSIS_Data` in YOLO mode;
2. non-autonomous or sandboxed sessions that must use escalated reads for `C:\TSIS_Data`;
3. Git recovery sessions that must inspect processes, branch state, upstream and remote before pushing.

### Impact

This converts the repeated startup and Git recovery knowledge from chat-only prompts into project-resident operational guidance.
Future Harness agents should start from `START_HERE.md` before task-specific runbooks when the human opens TSIS manually.

## 2026-06-12 - Sersan practice_15 pilot distillation v0.3

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/generate_sersan_p15_pilot.py`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/lesson_sections.jsonl`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/image_evidence_index.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/image_evidence_notes/`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/mechanical_rules.yaml`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/lesson_distillation.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/tsis_translation_map.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/open_questions.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/quality_report.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_15_revised/run_manifest.json`

### Changed

- Removed `practica_15_revised.md` from the pending Sersan pilot list.

### Notes

Third Sersan lesson-pack pilot executed against the artifact contract.

Acceptance decision:

- `pass_with_warnings`

The pilot extracts 20 section records, indexes 206 image references, promotes
66 medium/high/critical image-evidence notes, extracts 23 mechanical rule
candidates and creates 23 TSIS translation candidates.

### Impact

The initial three-pilot Sersan validation set is now complete:

1. `sersan_practice_02_donchain`
2. `sersan_practice_09_revision_apolo`
3. `sersan_practice_15_revised`

This adds the Money Management, risk sizing and portfolio-evaluation layer
needed before scaling distillation to the full Sersan corpus or wiring Sersan
doctrine into AlphaEvolve evaluators.


## 2026-06-12 - Sersan practice_09 pilot distillation v0.2

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/generate_sersan_p09_pilot.py`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/lesson_sections.jsonl`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/image_evidence_index.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/image_evidence_notes/`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/mechanical_rules.yaml`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/lesson_distillation.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/tsis_translation_map.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/open_questions.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/quality_report.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_09_revision_apolo/run_manifest.json`

### Changed

- Updated the Sersan lesson-pack contract to require image-reference extraction
  from both Markdown image syntax and HTML `<img src=...>` tags.
- Removed `practica_09_revision_apolo.md` from the pending Sersan pilot list.

### Notes

Second Sersan lesson-pack pilot executed against the artifact contract.

Acceptance decision:

- `pass_with_warnings`

The pilot extracts 16 section records, indexes 171 image references, promotes
26 medium/high/critical image-evidence notes, extracts 18 mechanical rule
candidates and creates 18 TSIS translation candidates.

### Impact

The Harness now has a concrete optimization-review pilot that covers execution
realism, map reading, overoptimization control, candidate reduction, increment
granularity, Performance Report review, Walk-Forward route rationale and
portfolio contribution.


## 2026-06-12 - Cognitive Architecture Harness folder split

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/shared_run_manifest_contract.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/shared_validation_principles.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/future_live_data_quality_contract.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/runbooks/`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/artifacts/`

### Changed

- Split `12_TSIS_COGNITIVE_ARCHITECTURE` into:
  - `00_SHARED_HARNESS_KERNEL/`
  - `10_DATA_QUALITY_HARNESS/`
  - `20_SERSAN_DISTILLATION_HARNESS/`
- Moved Sersan toolchain and artifacts under `20_SERSAN_DISTILLATION_HARNESS/`.
- Updated the toolchain traceability contract to make this folder model mandatory for future Harness work.
- Regenerated the `sersan_practice_02_donchain` pilot from the new Sersan toolchain path.

### Notes

The first Sersan pilot remains `pass_with_warnings`, but now its
`run_manifest.json` points to the canonical Sersan Harness folder and hashes
the shared/kernel contracts, Sersan contracts, selected evidence images and
outputs.


## 2026-06-11 - Harness toolchain traceability contract

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/harness_toolchain/sersan_distillation/generate_sersan_p02_pilot.py`

### Changed

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/README.md`
- `README.md`

### Notes

Toolchain traceability is now a contract-level requirement.

Accepted Harness outputs must declare project-resident generators, validators,
prompts or configs in `run_manifest.json` with hashes. Outputs produced only
from `C:\Users`, `C:\tmp`, Downloads or chat-only scripts are drafts until the
toolchain is promoted to the project and re-executed or formally blocked.

### Impact

The Sersan practice_02 pilot must be regenerated from the project-resident
generator before it can be treated as accepted pilot evidence.


## 2026-06-11 - Sersan practice_02 pilot distillation v0.1

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/lesson_sections.jsonl`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/image_evidence_index.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/image_evidence_notes/`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/mechanical_rules.yaml`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/lesson_distillation.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/tsis_translation_map.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/open_questions.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/quality_report.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/sersan_practice_02_donchain/run_manifest.json`

### Notes

First Sersan lesson-pack pilot executed against the artifact contract.

Acceptance decision:

- `pass_with_warnings`

The pilot extracts 13 section records, indexes 60 image references, reads the
medium/high/critical image evidence, extracts 13 mechanical rule candidates and
creates 13 TSIS translation candidates.

### Impact

The next pilot should be `sersan_practice_09_revision_apolo`. Before scaling to
the whole course, compare this pilot with practice 09 and practice 15 to decide
whether the contract needs revision.


## 2026-06-11 - Sersan pilot Harness runbook

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md`

### Notes

The Sersan pilot now has an explicit operating runbook.

It fixes:

- how agents should work;
- how iteration loops are bounded;
- how to know whether the work is good;
- what artifacts must exist;
- when to stop;
- what the human reviews;
- and when images must be embedded in `lesson_distillation.md`.

The runbook explicitly prevents uncontrolled "agent loops until done" and
requires contract validation plus `quality_report.md` as the source of final
status.

### Impact

The next safe action is to execute the first pilot lesson:

- `sersan_practice_02_donchain`

## 2026-06-11 - Sersan corpus inventory v0.1

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest.csv`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest_summary.json`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/<lesson_id>/lesson_pack_manifest.json`

### Notes

The first contract-based inventory of `SersanSistemas` is now materialized.

Current corpus inventory:

- lesson packs: `17`
- image references: `2108`
- local unresolved image references: `0`
- external image references: `1`
- `assets_resolved` lesson packs: `16`
- `inventory_only` lesson packs: `1`
- code artifacts: `183`
- xlsx artifacts: `11`
- pdf files: `101`

The only `inventory_only` lesson pack is:

- `sersan_unmapped_xxx_revised`

Reason:

- `xxx_revised.md` has no detected practice number and remains unmapped until
  human review.

### Impact

Future Sersan Distillation Harness agents can now start from stable
`lesson_pack_manifest.json` files instead of rediscovering corpus structure.

The next operational step remains the three-lesson pilot:

1. `sersan_practice_02_donchain`
2. `sersan_practice_09_revision_apolo`
3. `sersan_practice_15_revised`

## 2026-06-11 - CTO Harness foundation and Sersan distillation contracts

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/agentic_harness_architecture_reference.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/data_audit_harness_agentic_operating_map.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_protocol.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md`

### Changed

- `README.md`
- `12_TSIS_COGNITIVE_ARCHITECTURE/README.md`

### Notes

This milestone separates four CTO layers:

1. General agentic Harness architecture.
2. Data Quality Harness applied to the existing `01_foundations` audit.
3. SersanSistemas distillation protocol.
4. Sersan lesson-pack artifact contract.

The architectural sequence is now explicit:

```text
Agentic Harness Reference
-> Data Quality Harness / Sersan Distillation protocols
-> artifact contracts
-> offline replay / pilots
-> agents
-> shadow live
-> gating live
-> AlphaEvolve sandbox
```

The main institutional decision is:

```text
Harness before AlphaEvolve.
Evaluators before generators.
Contracts before agents.
Replay before live.
```

### Impact

- `00_CTO` now has a dedicated cognitive architecture layer for TSIS-specific
  automation design.
- Data audit automation is anchored to the verified `01_foundations` audit
  instead of invented agent roles.
- SersanSistemas is treated as expert source material that must be distilled,
  traced and reviewed before becoming TSIS doctrine.
- Future Harness agents now have a required artifact contract for Sersan lesson
  packs.

## 2026-06-10 - Initial TSIS Cognitive Architecture thesis

### Added

- `12_TSIS_COGNITIVE_ARCHITECTURE/README.md`

### Notes

This established the first CTO thesis for agentic automation in TSIS:

```text
TSIS = memoria + contratos + agentes + evaluadores + ejecucion reproducible + evolucion controlada
```

The document fixed the initial distinction between:

- Harness as the system of agentic work;
- AlphaEvolve as evolutionary candidate search;
- evaluators as the non-negotiable judge.

### Impact

This moved `00_CTO` away from general research collection and toward a concrete
architecture workspace for automation, agents and controlled evolution.
