# Graphify Official Build Protocol for 02_TSIS_BACKTEST_ENGINE

Status: ACTIVE
Graphify package baseline: `graphifyy 0.9.33`

## Purpose

Graphify is a semantic navigation layer. It does not replace contracts, tests,
gate reviews, manifests, the current handoff, or physical evidence.

The graph family is split into leaves:

1. `backtest_engine_current`: current implementation, tests, contracts,
   configurations, scripts and living system documentation.
2. `backtest_gate_evidence_history`: changelog, selected evidence and governed
   run manifests. Pending.
3. `backtest_archive_history`: `99_archive` only when historical navigation
   is justified. Pending and not part of normal agent context.
4. `backtest_engine_root`: future fusion of accepted leaves.

Do not build one monolithic graph from the whole directory.

## First Official Leaf

Stable output:

```text
graphify-out/leaf_slices/backtest_engine_current/
```

Included corpus:

```text
AGENTS.md
LOCAL_RULES.md
README.md
pyproject.toml
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
GRAPHIFY_REFRESH_QUEUE.md
REPRODUCE_*.md
RUN_*.py
src/**/*.py
tests/**/*.py
scripts/**/*.py
contracts/**/*.json
configs/**/*.json
docs/00_system/**/*.md
```

Excluded by default:

```text
99_archive/**
runs/**
evidence/**
deliverables/**
CHANGELOG.md
.pytest_cache/**
__pycache__/**
*.pyc
*.zip
graphify-out/**
```

The exclusion of physical evidence and run outputs is an authority boundary,
not a quality judgment. Those artifacts require their own controlled leaf.

## Safety Boundary

The build is read-only with respect to engine inputs and gate evidence. It must
not execute any `RUN_*.py`, open external Market State or Event State data,
consume a single-use authorization, or claim a gate transition.

The graph must preserve the distinction between:

```text
CURRENT / LIVE authority
HISTORICAL / SUPERSEDED material
AUTHORIZED_NOT_CONSUMED
NOT_AUTHORIZED
CLOSED_PASS
PENDING_REVIEW
```

## Required Pipeline

1. Build a controlled corpus in a temporary workspace.
2. Record canonical source path, relative path, SHA-256 and size.
3. Run Graphify structural extraction for code and semantic extraction for docs.
4. Build an undirected graph unless a later protocol explicitly authorizes a
   directed dependency graph.
5. Label communities with functional names.
6. Generate `graph.json`, `graph.html`, `GRAPH_REPORT.md`,
   `manifest.json`, `corpus_manifest.json` and `BUILD_MANIFEST.md`.
7. Run extraction diagnostics, `graphify diagnose multigraph` and at least one
   `graphify explain` smoke query.

## Acceptance

The leaf is accepted only when:

- every controlled source hash matches its canonical source;
- there are no duplicate node IDs, dangling/missing endpoints, self-loops or
  collapsed undirected edges;
- source paths in `graph.json` are relative to the controlled corpus;
- the build manifest records Git state, Graphify/skill provenance, exclusions,
  semantic mode and diagnostic results;
- no physical backtest command was executed.
