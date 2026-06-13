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

### Pending

- Crear vocabulario canonico de estados para Data Quality Harness.
- Crear contrato de artefactos live para Data Quality Harness.

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
