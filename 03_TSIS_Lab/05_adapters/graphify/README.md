# TSIS Graphify Refresh Adapter

This adapter governs full and incremental Graphify refreshes for TSIS.

It exists because a TSIS graph refresh is a long-running, multi-stage operation:

```text
curated corpus
-> structural extraction
-> semantic extraction by Codex agents
-> graph build
-> diagnostics
-> community labeling
-> publication
-> governed root composition
```

## Authority

- Graphify runtime: installed `graphifyy` package.
- Semantic extraction prompt: the official `graphify` Codex skill.
- TSIS build policy: `00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`.
- Long operation policy: `LONG_RUNNING_OPERATIONS_CONTRACT.md`.
- Target definitions: `tsis_graphify_refresh_plan_v0_1.json`.

The adapter never treats historical `graph.json` files as semantic authority. A
historical graph may be an explicitly declared incremental baseline only when the
target plan authorizes it.

## Leaf lifecycle

```powershell
python run_tsis_graphify_leaf_v0_1.py prepare `
  --target-id <TARGET_ID> `
  --run-id <RUN_ID>

python monitor_tsis_graphify_refresh_v0_1.py `
  --run-root <RUN_ROOT> --watch

# Codex agents write every semantic chunk declared by chunk_plan.json.

python run_tsis_graphify_leaf_v0_1.py assemble `
  --target-id <TARGET_ID> `
  --run-id <RUN_ID>

# A Codex agent writes community_labels.json from community_label_plan.json.

python run_tsis_graphify_leaf_v0_1.py publish `
  --target-id <TARGET_ID> `
  --run-id <RUN_ID>
```

No publication occurs before diagnostics pass and all forbidden legacy source
paths are absent.

## Root composition lifecycle

```powershell
python merge_tsis_graphify_roots_v0_1.py prepare `
  --group-id <GROUP_ID> `
  --run-id <RUN_ID>

# A Codex agent writes community_labels.json.

python merge_tsis_graphify_roots_v0_1.py publish `
  --group-id <GROUP_ID> `
  --run-id <RUN_ID>
```

Root composition uses the official `graphify merge-graphs` command. It never
performs a hand-written JSON union.

