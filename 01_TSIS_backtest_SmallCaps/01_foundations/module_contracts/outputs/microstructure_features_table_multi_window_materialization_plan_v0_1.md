# Microstructure Features Table Multi-Window Materialization Plan `v0_1`

## 1. Purpose

This document defines the next governed work loop for expanding
`microstructure_features_table` beyond the current one-window seed.

It is a plan and promotion contract. It does not create, certify or promote a
new parquet dataset.

Current official table:

```text
dataset_id: microstructure_features_table_v0_1
scope: seed_event_window_smoke
full_universe_claim: false
rows: 1
tickers: 1
windows: 1
seed window: ZYXI 2025-12-01 full UTC day
quotes root: D:/quotes
trades root: E:/TSIS/data/trades_ticks_prod_2005_2026
```

The current v0.1 table remains a governed vertical slice only. It must not be
treated as a trainable microstructure dataset.

## 2. Why This Loop Exists

`market_state_table` and `event_state_table` need a microstructure state
component that can describe event windows with quote/trade texture:

- spread;
- locked/crossed quotes;
- two-sided quote availability;
- quote staleness/missingness;
- top-of-book depth proxy;
- trade intensity;
- odd-lot ratio;
- duplicate/exact tape texture;
- invalid trade rows;
- off-session ratio;
- dollar volume and liquidity context.

The current seed proves that TSIS can compute these features and preserve
source hashes. It does not prove coverage, stability or model usefulness.

## 3. Non-Negotiable Boundary

The following rule is binding:

```text
No se lanza full-universe ciego.
```

For microstructure this is especially important because raw quotes/trades are
large and path-sensitive.

The next step is not:

```text
scan every quote/trade file for every ticker-minute
```

The next step is:

```text
build a governed multi-window/multi-event candidate from explicit event windows
```

## 4. What "Multi-Window" Means Here

The immediate target is not full raw tape coverage.

The immediate target is a declared event-window denominator such as:

```text
source_window_table: event_windows_table_v0_1
source_event_family: halt
eligible_windows: valid_for_microstructure_feature_candidate = true
scope: halts_intraday_lt1b_calendar_covered_microstructure_candidate
quotes_root: governed E-root or provisional D-root with explicit state
trades_root: E:/TSIS/data/trades_ticks_prod_2005_2026
```

This produces a stronger table than the seed because it covers many governed
windows, but it still does not mean all future event families are covered.

## 5. Event Window Dependency

The first preferred denominator is:

```text
E:/TSIS/data/data_foundation_outputs/event_windows_table/event_windows_table_v0_1.parquet
```

Use only rows where:

```text
valid_for_microstructure_feature_candidate = true
```

Current limitation:

```text
event_windows_table_v0_1 covers halt-derived event windows only.
```

Therefore the first multi-window candidate should claim:

```text
event_family_coverage = halt only
full_universe_claim = false
```

It must not claim news, offerings, filings, gaps, short-pressure events or live
alerts until those event-window sources exist.

## 6. Source Root Decision

The current v0.1 seed uses:

```text
quotes_root_used = D:/quotes
quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity
target_official_quotes_root = E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root = E:/TSIS/data/quotes
```

Before stronger promotion, choose one of these states:

### State A - Official E-root

```text
quotes_root_used = E:/TSIS/data/quotes_
quotes_root_state = official_e_raw_root
```

Allowed for stronger candidate work when `D:/quotes -> E:/TSIS/data/quotes_`
clone parity/audit is complete. `E:/TSIS/data/quotes` is not the target official
root for this recovery decision; it is treated as incomplete/legacy E-root.

### State B - Provisional D-root candidate

```text
quotes_root_used = D:/quotes
quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity
```

Allowed only for a candidate/pilot. It cannot be promoted to production,
execution simulation, ML/RL primary training or backtest-core source.

The row-level source fields must stay visible in every version.

## 7. Current Builder Gap

The current builder is:

```text
scripts/materialize_microstructure_features_table.py
```

Current hardcoded semantics:

```text
dataset_id = microstructure_features_table_v0_1
schema_version = microstructure_features_table_v0_1
materialization_scope = seed_event_window_smoke
dataset_dir = microstructure_features_table_v0_1
summary = _microstructure_features_table_summary_v0_1.csv
manifest = _microstructure_features_table_manifest_v0_1.json
```

Required builder changes before a multi-window candidate:

- config-driven dataset id;
- config-driven schema/policy version;
- config-driven materialization scope;
- config-driven output dataset directory;
- input mode for governed `event_windows_table` rows;
- event family/window role filters;
- source root state selected explicitly;
- candidate-only output path;
- no overwrite of v0.1 output;
- denominator manifest with eligible/requested/materialized/missing counts;
- partition-level and source-file reconciliation;
- row-level missingness states;
- strict leakage and window role preservation.

Current implementation status:

```text
candidate_window_manifest_builder: implemented
builder_path: scripts/build_microstructure_candidate_window_manifest.py
feature_materializer_v0_2: parameterized candidate path tested
materializer_path: scripts/materialize_microstructure_features_table.py
controlled_candidate_parquet_created: true
controlled_candidate_promoted: false
official_promoted_parquet_created: false
```

The manifest builder creates a governed candidate window CSV/JSON from
`event_windows_table_v0_1`. It does not compute quote/trade features and it
does not write into `E:/TSIS/data/data_foundation_outputs/`.

The existing feature materializer now supports candidate parameters while
preserving v0.1 defaults. The tested candidate writes only under the test-run
artifact directory, not under the official E-root.

## 8. Candidate Dataset

The first wider candidate should be named as a candidate, not as an official
replacement:

```text
dataset_id = microstructure_features_table_v0_2_candidate
materialization_scope = halt_event_windows_microstructure_candidate
source_window_table = event_windows_table_v0_1
full_universe_claim = false
```

Recommended output:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate/
```

It must not write into:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_1/
```

## 9. Minimum Feature Families For The Candidate

The current compact feature families are acceptable as a base:

Quote features:

- quote row count;
- quote window row count;
- first/last quote timestamp;
- bid/ask zero ratios;
- bid/ask size zero ratios;
- two-sided rows;
- crossed rows and crossed ratio;
- locked rows and locked ratio;
- spread median/p90 in bps;
- top-depth mean.

Trade features:

- trade row count;
- trade window row count;
- first/last trade timestamp;
- invalid price/size rows;
- odd-lot ratio;
- duplicate exact ratio;
- off-regular-session ratio;
- total volume;
- dollar volume;
- min/max/last trade price;
- median/p90 size.

Required additions for multi-window robustness:

- quote/trade missingness reason;
- quote/trade source file exists but empty-in-window flag;
- quote/trade staleness or sparse-window state;
- event window role;
- event family;
- leakage-safe feature flag inherited from `event_windows_table`;
- decision-time eligibility state;
- source root parity state.

## 10. Test Requirements

The candidate is not institutional until tests pass.

Required tests:

- event-window denominator reconciliation;
- eligible window count vs materialized row count;
- duplicate key rejection;
- source file hash validation;
- recomputation from raw quotes/trades for sampled rows;
- missing-source handling;
- empty-window handling;
- crossed/locked/spread formula integrity;
- odd-lot/duplicate/off-session formula integrity;
- no `full_universe_claim=true`;
- no `execution_sim_candidate=true` while quotes root is provisional;
- no `backtest_core_microstructure_candidate=true` until quality gates pass;
- no post-event windows used as ML pre-event features;
- manifest output tree hash validation;
- contract path validation.

Evidence must be written under:

```text
C:/TSIS_Data/tests/test_runs/<date>/<run_id>/
```

## 11. Visual/Forensic Evidence Requirement

Before promotion beyond candidate status, human-inspector evidence is required.

At minimum:

- good windows with clean quote/trade alignment;
- review windows with crossed/locked or sparse quotes;
- review windows with high odd-lot/duplicate trade texture;
- missing quote but present trade windows;
- present quote but missing trade windows;
- halt/event windows with event-time overlays.

Each image must be accompanied by specific text explaining what the inspector
sees and why it matters for state modeling, execution realism and ML/RL
eligibility.

## 12. Consumer Semantics

A multi-window candidate can support:

- event-window research;
- market-state component design;
- liquidity-stress feature exploration;
- missingness/staleness diagnostics;
- controlled ML feature experiments only with `ml_flagged` and leakage gates.

It cannot support by default:

- core backtesting;
- execution simulation;
- live trading;
- RL training;
- full-universe microstructure modeling;
- all event families.

## 13. Stop Conditions

Stop and do not promote if any of the following occur:

- event windows are invented inside the microstructure builder;
- source roots are mixed without row-level lineage;
- D-root quotes are treated as official without parity/audit;
- requested windows and materialized rows cannot be reconciled;
- source hashes are missing for present files;
- recomputation from raw fails;
- post-event windows leak into pre-event features;
- visual/forensic evidence is absent for the scope being promoted;
- tests only prove one seed row but documentation claims broad coverage.

## 14. Next Agent Checklist

The next agent should execute in this order:

1. Read this document.
2. Read `event_windows_table` contracts.
3. Review the existing candidate manifest builder:
   `scripts/build_microstructure_candidate_window_manifest.py`.
4. Decide whether the first feature-materialization candidate uses official E
   quotes or provisional D
   quotes with explicit candidate-only status.
5. Build or reuse a small deterministic candidate window manifest from
   `event_windows_table_v0_1`.
6. Reuse the parameterized feature materializer for a larger candidate path
   only after deciding the quotes-root state.
7. Review the existing 6-row smoke visual/forensic inspector evidence before
   any promotion discussion.
8. Expand from the 6-row smoke candidate only with declared denominator,
   source-root state and recomputation tests.

## 15. Current Status

```text
status: controlled_50_window_candidate_materialized_and_tested_not_promoted
official_new_dataset_created: false
controlled_candidate_dataset_created: true
heavy_materialization_started: false
test_candidate_feature_materialization_created: true
candidate_visual_evidence_created: true
full_universe_claim_granted: false
next_executable_action: expand visual/forensic evidence and resolve quotes E-root parity before any stronger promotion
```

Latest candidate manifest evidence:

```text
test_run: C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
tests: 5
passed: 5
failed: 0
source_event_windows_rows: 214112
eligible_microstructure_rows: 85658
eligible_role_counts:
  pre_event_30m: 42829
  same_session_regular: 42829
selected_rows_in_test_manifest: 6
candidate_feature_rows_materialized_under_test_artifacts: 6
candidate_quotes_file_present_rows: 6
candidate_trades_file_present_rows: 6
candidate_hard_fail_count: 0
candidate_source_quotes_rows_total: 20626
candidate_source_trades_rows_total: 71141
official_dataset_created: false
```

Latest visual/forensic evidence for the 6-row smoke candidate:

```text
readout: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_visual_readout_v0_1.md
visual_manifest: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/microstructure_candidate_visual_manifest_v0_1.json
image_dir: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_1/images/
notebook: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/notebooks/data_foundation_outputs/microstructure_candidate_visual_evidence_v0_1.ipynb
visual_case_count: 6
official_dataset_created: false
```

Latest controlled candidate materialization evidence:

```text
dataset_id: microstructure_features_table_v0_2_candidate
materialization_scope: halt_event_windows_microstructure_candidate_controlled_25_per_role
build_run_id: microstructure_features_table_v0_2_candidate_20260627T163646Z
output: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/microstructure_features_table_v0_2_candidate_controlled_25_per_role
manifest: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_manifest_v0_2_candidate_controlled_25_per_role.json
summary: E:/TSIS/data/data_foundation_outputs/microstructure_features_table/_microstructure_features_table_summary_v0_2_candidate_controlled_25_per_role.csv
source_windows_csv: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/microstructure_features_table_v0_2_candidate_controlled_25_per_role/microstructure_features_table_v0_2_candidate_window_manifest_v0_1.csv
source_windows_csv_sha256: 969e8af1535b021f1306a8b80457ca18124ece8d0fceb5365d73edf4eb10645d
rows: 50
tickers: 9
windows: 50
quotes_file_present_rows: 50
trades_file_present_rows: 24
review_partial_source_rows: 26
pass_seed_window_rows: 24
hard_fail_count: 0
duplicate_key_groups: 0
full_universe_claim: false
execution_sim_candidate_rows: 0
backtest_core_microstructure_candidate_rows: 0
quotes_root: D:/quotes
quotes_root_state: provisional_d_legacy_recovery_root_pending_e_parity
target_official_quotes_root: E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root: E:/TSIS/data/quotes
trades_root: E:/TSIS/data/trades_ticks_prod_2005_2026
trades_root_state: official_e_raw_root
output_tree_sha256: a3d418b06d8c4bd200d51d8eb9c6d888664c1af86ab3dd37c80d48ff2397d128
test_evidence: C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_v0_2_controlled_candidate/
tests: 5
passed: 5
failed: 0
visual_readout: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/microstructure_candidate_controlled_visual_readout_v0_2.md
visual_manifest: C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/microstructure_features/visual_evidence_v0_2_controlled_25_per_role/microstructure_candidate_controlled_visual_manifest_v0_2.json
visual_case_count: 50
visual_cached_quote_files_read: 9
visual_cached_trade_files_read: 5
```

Interpretation:

```text
This is a controlled candidate dataset, not an official replacement for
microstructure_features_table_v0_1 and not an institutional microstructure
training corpus. It proves candidate materialization, manifest/tree hashing,
source-window lineage, row-level source hash handling, missing-trades state and
sample raw recomputation. It remains blocked from ML/RL primary use, core
backtesting and execution simulation until coverage, quotes E-root authority,
larger visual/forensic evidence and promotion gates pass.
```
