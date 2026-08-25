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
