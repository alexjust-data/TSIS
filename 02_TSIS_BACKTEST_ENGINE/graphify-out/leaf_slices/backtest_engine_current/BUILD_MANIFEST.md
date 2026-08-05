# Build Manifest - backtest_engine_current

## Identity

- **Status:** `complete`
- **Acceptance:** `accepted`
- **Run ID:** `backtest_engine_current_20260805T110328Z`
- **Built:** 2026-08-05 (Europe/Madrid)
- **Source root:** `C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE`
- **Controlled corpus:** `C:\tmp\TSIS_graphify_workspaces\backtest_engine_current\corpus`
- **Official leaf:** `graphify-out/leaf_slices/backtest_engine_current`
- **Git branch:** `integrate/main-data-quality-dossiers-20260613`
- **Git commit:** `988292ee07f9440fbb8322048ca2807d45f6e557`
- **Dirty paths at start:** 25
- **Dirty paths after Graphify governance files:** 26

## Toolchain

- **Graphify package:** `0.9.33`
- **Upstream:** `https://github.com/Graphify-Labs/graphify`
- **Skill:** `C:\Users\AlexJ\.codex\skills\graphify\SKILL.md`
- **Skill SHA-256:** `9024289348CCEB6140AF33E9875742DC55F55E5D574E44E5A21BB36239B1BCF4`
- **Semantic backend:** Codex subagents; no external API key
- **Graph type:** undirected simple graph

## Corpus Contract

- **Files:** 162
- **Detected words:** 97,837
- **Code/structured files:** 120
- **Semantic documents:** 42
- **Included:** root governance/handoff files, `RUN_*.py`, `REPRODUCE_*.md`,
  `src/**/*.py`, `tests/**/*.py`, `scripts/**/*.py`, `contracts/**/*.json`,
  `configs/**/*.json`, and living `docs/00_system/**/*.md`
- **Excluded:** `runs`, `evidence`, `deliverables`, `99_archive`, caches,
  generated `graphify-out`, archives and `CHANGELOG.md`
- **Canonical/workspace hash parity:** 162/162 files

## Extraction

- **AST:** 2,369 nodes; 6,935 raw edges
- **Semantic:** 156 nodes; 202 edges; 13 hyperedges
- **Raw merged extraction:** 2,525 nodes; 7,137 edges
- **Normalized extraction:** 2,575 nodes; 6,785 edges
- **Official graph:** 2,568 nodes; 6,774 links; 150 communities
- **Community labels:** 150/150 technical labels
- **Visualization:** full interactive HTML; below the 5,000-node warning threshold
- **Token accounting:** Codex subagent transport did not expose complete token
  counts; values in `cost.json` are not a complete cost estimate

## Normalization And Integrity

The unmodified producer output is retained as `.graphify_extract_raw.json` and
`GRAPH_HEALTH_RAW.json`. It contained 551 dangling endpoint edges, 119 exact
duplicate edges and 348 undirected same-endpoint collapses.

The official extraction applies a deterministic, auditable normalization:

1. materialize 50 endpoints already asserted by AST or semantic edges;
2. deduplicate exact edge records;
3. consolidate undirected parallel edges while preserving every original
   relation, direction and source location in `relations` and `evidence`;
4. retain conflicting node records as node audit metadata.

Final extraction diagnostic and final `graphify diagnose multigraph` result:

- duplicate node IDs: 0
- dangling or missing endpoint edges: 0
- self-loop edges: 0
- exact duplicate edges: 0
- collapsed directed or undirected edges: 0
- absolute source paths in `graph.json`: 0

Sixteen authorization/config JSON files produced zero AST nodes. They remain in
the controlled corpus and hash manifest; this producer warning does not alter
the clean final graph diagnostic.

## Operational Boundary

- No `RUN_*.py`, test suite, backtester, physical-data reader or single-use
  authorization was executed.
- No physical Event State or Market State data was read.
- Canonical files that changed during construction were resynchronized and
  reprocessed before the final 162/162 hash-parity check.
- The explain smoke test resolved `TSIS Backtest Engine Current Project Handoff`
  to `docs/00_system/CURRENT_PROJECT_HANDOFF.md` with nine connections.

## Pending Leaves

- `backtest_gate_evidence_history`: pending under `GFQ-20260805-BT-002`
- `backtest_archive_history`: pending under `GFQ-20260805-BT-003`
