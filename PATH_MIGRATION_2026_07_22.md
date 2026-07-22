# TSIS Root Path Migration - 2026-07-22

Status: active path resolution note
Authority: `C:/TSIS_Data/CHANGELOG.md` and this file
Scope: top-level TSIS folder names changed by the human before the path audit.

## Canonical Path Map

| Legacy path | Current canonical path | Current role |
|---|---|---|
| `C:/TSIS_Data/00_TSIS_Lab` | `C:/TSIS_Data/03_TSIS_Lab` | Transversal research experiment lab: contracts, registries, templates, evidence and validation. |
| `C:/TSIS_Data/01_TSIS_backtest_SmallCaps` | `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION` | Data audit, certification, Data Foundation contracts, schemas, policies, validators, dossiers and governed data outputs. |
| new root | `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE` | Future professional backtest engine implementation area. |
| `C:/TSIS_Data/02_TSIS_webSocket_SmallCaps` | `C:/TSIS_Data/04_TSIS_webSocket_SmallCaps` | Live/shadow ingestion, event-driven operation and execution bridge work. |
| `C:/TSIS_Data/03_TSIS_Offline_RL` | `C:/TSIS_Data/05_TSIS_Offline_RL` | Offline learning over governed states/outcomes. |
| `C:/TSIS_Data/04_TSIS_Trading_voice` | `C:/TSIS_Data/06_TSIS_Trading_voice` | Trading Decision Intelligence / voice decision process layer. |

`C:/TSIS_Data/00_CTO` and `C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE` did not move.

## Agent Resolution Rules

1. Treat the current canonical paths above as the physical roots.
2. If a legacy path appears in historical closeouts, preserved audit evidence, old changelog entries, runtime logs, archives or Graphify outputs, resolve it through this map before declaring the reference broken.
3. Do not recreate a legacy root directory only to satisfy an old reference.
4. Do not rewrite preserved audit evidence solely for path aesthetics. Preserve historical evidence first.
5. Active code, configs, tests, READMEs, AGENTS, LOCAL_RULES and manifests must use canonical paths.
6. If a command fails because it points to a legacy root, substitute the canonical root first and then re-check the local contract that owns that path.
7. The existing `graphify-out` graph may contain stale source locations until an official refresh is run.

## Backtest Boundary

The architecture/theory authority for the professional backtester remains:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE
```

The implementation shell is:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

The backtest engine must consume Data Foundation contracts and certified outputs from:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION
```

It must not own raw data audit, dataset certification, price semantics or data immutability.

## Audit Status

This note is intentionally separate from historical changelogs. It exists so future agents can resolve path leaks while the repository transitions from legacy names to canonical names.

After this note was added, active text files were mechanically audited for these legacy roots:

```text
00_TSIS_Lab
01_TSIS_backtest_SmallCaps
02_TSIS_webSocket_SmallCaps
03_TSIS_Offline_RL
04_TSIS_Trading_voice
```

Remaining legacy references should be classified before editing:

- historical / changelog / archive: normally preserve;
- generated Graphify output: refresh graph, do not hand-edit;
- runtime evidence: normally preserve;
- active code/config/test/governance: migrate to canonical path.