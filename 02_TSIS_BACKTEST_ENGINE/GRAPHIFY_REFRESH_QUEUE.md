## 2026-08-22 - TSIS_GRAPHIFY_QUEUE_RESOLUTION_20260822

- resolution_status: ACCEPTED_REFRESH_PUBLISHED
- published_root: `C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE\graphify-out`
- covered_queue_ids: `GFQ-20260805-BT-004`
- preserved_historical_status: `GFQ-20260805-BT-001` remains `published_snapshot`
- remains_pending_out_of_scope: `GFQ-20260805-BT-002`, `GFQ-20260805-BT-003`
- evidence: `C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE\graphify-out\GRAPHIFY_TERMINAL_AUDIT_20260822.json`

# Graphify Refresh Queue for 02_TSIS_BACKTEST_ENGINE

Status: ACTIVE

## Rule

Any task that changes the semantic corpus, contracts, implementation,
architecture, paths, gate semantics or Graphify governance must end with:

1. the affected official leaf updated and diagnosed; or
2. a `pending` entry here with date, severity, scope, files, target leaf and
   reason for deferral.

A chat, README or changelog note alone is insufficient.

## Active Entries

### GFQ-20260805-BT-001 - Initial current-engine leaf

- **Status:** `published_snapshot`
- **Severity:** `HIGH`
- **Target leaf:** `backtest_engine_current`
- **Scope:** current code, tests, contracts, configs, scripts and living docs
- **Exclusions:** runs, evidence, deliverables, archive and changelog
- **Run:** `backtest_engine_current_20260805T110328Z`
- **Result:** published metrics are recorded in the immutable build manifest
- **Integrity:** the published snapshot passed corpus parity, extraction health,
  multigraph diagnosis and explain smoke testing before later source changes.

### GFQ-20260805-BT-004 - Post-publication current-leaf refresh

- **Status:** `pending`
- **Severity:** `HIGH`
- **Target leaf:** `backtest_engine_current`
- **Detected:** 2026-08-05 after stable publication
- **Files:** `AGENTS.md`, `README.md`, `RUN_FULL_REPOSITORY_TESTS.py`,
  deleted superseded root files `REPRODUCE_BT_GATE_015_R2.md`,
  `REPRODUCE_BT_GATE_015_V0_3.md`,
  `RUN_BT_GATE_014_V0_3_PREEXECUTION_TESTS.py`,
  `RUN_BT_GATE_014_V0_4_PREEXECUTION_TESTS.py` and
  `RUN_BT_GATE_014_V0_5_PREEXECUTION_TESTS.py`,
  `docs/00_system/BACKTEST_ENGINE_ROADMAP.md`,
  `docs/00_system/CURRENT_PROJECT_HANDOFF.md`,
  `docs/00_system/26_BT_GATE_015_V0_3_CONSUMED_FAILURE_READOUT.md`,
  `docs/00_system/27_BT_GATE_015_V0_3_POSTEXECUTION_EXTERNAL_REVIEW.md`,
  `docs/00_system/28_BT_GATE_015_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_4.md`,
  `docs/00_system/34_BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE.md`,
  `src/tsis_backtest/event_state/physical_*_v0_4.py`,
  `tests/unit/test_bt_gate_015_single_use_physical_v0_4.py`,
  `tests/unit/test_market_state_external_review_regressions.py`,
  and the BT-GATE-015 decision, policy, traceability, gate and package
  governance surfaces under `00_CTO/14_BACKTEST_ENGINE`
- **Reason deferred:** these files changed again after final parity and while
  other work was active; BT-GATE-015 has now closed, but rebuilding immediately
  would mix the closure registration with unrelated concurrent source changes
- **Close condition:** resynchronize the affected current corpus after concurrent edits stop,
  update semantic/AST extraction, republish and repeat all acceptance checks

### GFQ-20260805-BT-002 - Gate evidence history leaf

- **Status:** `pending`
- **Severity:** `MEDIUM`
- **Target leaf:** `backtest_gate_evidence_history`
- **Scope:** changelog, selected evidence and governed run manifests
- **Reason deferred:** evidence/run semantics require a separate controlled
  inclusion contract and must not contaminate the current authority leaf

### GFQ-20260805-BT-003 - Archive history leaf

- **Status:** `pending`
- **Severity:** `LOW`
- **Target leaf:** `backtest_archive_history`
- **Scope:** `99_archive`
- **Reason deferred:** historical navigation is lower priority and should not
  enter normal agent context by default

## TSIS_GRAPHIFY_QUEUE_CORPUS_EXCLUSION_ACCEPTED_20260822

- corpus_policy: `EXCLUDED_OPERATIONAL_CONTROL`
- rationale: evita el ciclo build -> actualización de queue -> grafo inmediatamente stale.
- existing_entry_statuses: `UNCHANGED`
- terminal_audit: `C:\TSIS_Data\runs\graphify_refresh\GRAPHIFY_TERMINAL_AUDIT_20260822.json`
- source_coverage_audit: `C:\TSIS_Data\runs\graphify_refresh\GRAPHIFY_SOURCE_COVERAGE_AUDIT_20260822.json`
