# Graphify Refresh Queue

## Pending

- status: pending
  date: 2026-08-25
  scope: Daily Pattern Discovery Atlas v0.1 governed corpus correction and recertification
  affected_files:
    - README.md
    - DAILY_PATTERN_DISCOVERY_ATLAS_v0_1.md
    - CHANGELOG.md
    - INCIDENT_REGISTER_v0_1.md
    - PRODUCTION_PERFORMANCE_OPTIMIZATION_PLAN_v0_1.md
    - configs/daily_pattern_atlas_v0_1.yaml
    - scripts/build_final_readout.py
    - src/
    - tests/
    - app/
    - ../../03_TSIS_Lab/04_experiments/EXP_DAILY_PATTERN_ATLAS_0001/
  severity: high
  target_leaf: 05_statistics_patterns_daily_atlas_v0_1
  reason: >-
    The module has no official Graphify leaf or BUILD_MANIFEST yet.
    Queue this new leaf for integration into the root governed graph; do not
    treat a private ad-hoc graph build as the institutional refresh.
    This pending scope also includes the app's terminal-PASS-only run resolver
    and its fallback semantics for incomplete or failed full runs.
- status: pending
  date: 2026-08-25
  scope: Daily Pattern Atlas v0.3 interactive catalog and lifetime chart contract
  affected_files:
    - README.md
    - DAILY_PATTERN_DISCOVERY_ATLAS_v0_1.md
    - CHANGELOG.md
    - app/LOCAL_EXPLORER_README.md
    - app/api/README.md
    - app/api/server_v2.py
    - app/api/test_server.py
    - app/app/AtlasV2.tsx
    - app/app/TradingChart.tsx
    - app/app/atlas.css
  severity: medium
  target_leaf: 05_statistics_patterns_daily_atlas_v0_1
  reason: >-
    The module still has no official Graphify leaf or BUILD_MANIFEST. Queue the
    new 5-family/27-label web catalog, explicit 90-case pagination semantics,
    linked D0 activation controls, full-ticker-lifetime chart and selected-label
    occurrence markers for the next official root-graph integration.
- status: pending
  date: 2026-08-25
  scope: Daily Pattern Atlas v0.4 dual price-view comparison contract
  affected_files:
    - README.md
    - DAILY_PATTERN_DISCOVERY_ATLAS_v0_1.md
    - CHANGELOG.md
    - app/LOCAL_EXPLORER_README.md
    - app/api/README.md
    - app/api/server_v2.py
    - app/api/test_server.py
    - app/api/test_ui_contract.py
    - app/app/AdjustedTradingChart.tsx
    - app/app/AtlasV2.tsx
    - app/app/atlas.css
  severity: medium
  target_leaf: 05_statistics_patterns_daily_atlas_v0_1
  reason: >-
    The module still has no official Graphify leaf or BUILD_MANIFEST. Queue the
    additive direct daily_adjusted OHLCV comparison view, its strict
    same-ticker/same-period boundary, and its explicit exclusion of statistical
    overlays and census recomputation for the next root-graph integration.