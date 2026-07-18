# 03_TABLES_feature_engineering Changelog

This changelog records table-specific semantic and operational changes inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

It does not replace the operational changelogs in:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

Use it to record table reading changes, maturity changes, validation evidence,
and important dependency decisions.

---

## 2026-07-17 | information model | family catalog refactored to information objects

- Refactored `01_MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md` from an attribute-by-family inventory into a Market Representation Information Model.
- New structure:

```text
Family
  -> Information Object
    -> phenomenon
    -> hypothesis
    -> physical variables
    -> table location
    -> consumers
    -> coverage status
```

- Preserved the historical filename for continuity while declaring logical name `MARKET_REPRESENTATION_INFORMATION_MODEL_ES` inside the document.
- Clarified the relationship with `00_FEATURE_ADMISION_PROCESS.md`: admission process decides what may enter; information model catalogs what currently exists and what remains pending.


## 2026-07-16 | families | consolidated attribute index added

- Added `MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md`.
- Purpose: consolidate market representation families with the attributes/variables identified across tables `000` through `012`.
- Boundary: marks explicitly which families remain pending for `013-018` instead of treating them as already covered.


## 2026-07-16 | 000-012 | ES audits reformatted with readable blocks

- Reformatted Spanish concise representation readings `000` through `012`.
- Each family field now uses its own fenced `text` block with line breaks for readability:
  - phenomenon;
  - hypothesis;
  - questions;
  - minimum variables;
  - target table;
  - consumers.
- Updated `TABLE_REPRESENTATION_AUDIT_TEMPLATE_ES.md` to enforce the block format.


## 2026-07-16 | 000-012 | ES audits reduced to concise family readings

- Replaced verbose Spanish per-table audits `000` through `012` with concise representation readings.
- New format answers only:
  - market phenomenon represented;
  - scientific hypothesis;
  - questions answered;
  - minimum variables;
  - target table;
  - downstream consumers.
- English originals are left untouched for now; Spanish versions are the preferred human-facing working documents.


## 2026-07-16 | 000-012 | versiones castellanas de auditorias

- Added Spanish copies without deleting the English originals:
  - `TABLES_REPRESENTATION_OF_MARKET_ES.md`
  - `TABLE_REPRESENTATION_AUDIT_TEMPLATE_ES.md`
  - one `*_representation_audit_ES.md` document inside each table folder from `000` through `012`.
- Boundary: English originals remain available as historical/source versions; Spanish copies are the human-facing reading versions.


## 2026-07-16 | 000-012 | representation audits generated

- Created one representation/feature-engineering audit document inside each table folder from `000` through `012`.
- Each audit applies `TABLE_REPRESENTATION_OF_MARKET.md` and `TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Each audit records:
  - table being / non-being;
  - market representation families covered;
  - scientific hypothesis behind variable groups;
  - current physical sample column count from the folder-named physical sample file;
  - leakage/as-of risks;
  - downstream consumption verdict;
  - final audit decision.
- Boundary preserved: these audits do not promote a dataset by themselves; official status remains governed by registry, contracts, validators, manifests and certification matrices.


## 2026-07-16 | feature engineering | representation guardrails added

- Added `TABLES_REPRESENTATION_OF_MARKET.md`.
- Added `TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Updated README and LOCAL_RULES to reflect the renamed `03_TABLES_feature_engineering` role.
- Established the central guardrail:

```text
What do we need to know
to correctly describe
the state of the market
at an instant t?
```

- Established the variable admission rule: every variable must justify why it deserves to exist, which scientific hypothesis it represents, which market representation family it belongs to and which downstream consumer can use it.

## 2026-07-16 | 013 | contract policy registry linked

- Linked the validated `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` to foundations governance artifacts:

```text
contract = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\ohlcv_1m_quote_guarded_dataset_contract_v0_1.md
policy = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\ohlcv_1m_quote_guarded_consumption_policy.md
registry = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\ohlcv_1m\ohlcv_1m_quote_guarded_registry_entry.yaml
```

- Operational decision: 013 can now be used as a controlled downstream input for candidate 014/018 work when the consumer records `price_view = quote_guarded_1m` and the validation manifest.
- Boundary preserved: this is not unrestricted institutional promotion.

## 2026-07-16 | local governance | table rules added

- Added `03_TABLES_feature_engineering/LOCAL_RULES.md`.
- Established mandatory six-question gate before defining table attributes.
- Fixed the rule that table status must be proven from contracts, manifests,
  validators, tests, status matrices or physical inspection.

## 2026-07-16 | 013 | quote-guarded overlay verified

- Updated `013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md`
  to `operational_reading_v0_2`.
- Verified the promoted/PASS repair manifest under:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

- Recorded focused tests:

```text
7 passed in 2.81s
```

- Final reading:

```text
013 is already materialized as a governed quote-guarded overlay.
013 is not an official full-universe physical replacement tree.
014 and downstream consumers must prove correct overlay consumption.
```

## 2026-07-16 | 013 | physical full-universe failure correction

- Corrected the operational reading of `013_ohlcv_1m_quote_guarded` to separate
  the promoted/PASS LT1B repair overlay from the physical full-universe
  candidate tree.
- Confirmed that `ohlcv_1m_quote_guarded_full_universe_v0_1` remains
  `candidate_not_official` with `full_universe_claim=false`.
- Recorded unresolved `complete_with_failures` summaries for 2015..2020:

```text
2015 failed_tickers = 548
2016 failed_tickers = 571
2017 failed_tickers = 596
2018 failed_tickers = 758
2019 failed_tickers = 744
2020 failed_tickers = 701
```

- Current next action: controlled rematerialization/reconciliation of failed
  2015..2020 ticker-year cases before any clean full-universe claim.


- Generated operational failure manifest: `013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv` with 3,918 failed ticker-year rows for controlled rematerialization.

## 2026-07-16 | 013 | failed-rerun launcher prepared and smoke passed

- Prepared non-destructive delta rerun root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
```

- Generated year task plans for 3,918 failed ticker-year cases across 2015..2020.
- Rewrote task-plan raw input paths from `E:\TSIS\data\ohlcv_1m` to `G:\TSIS\data\ohlcv_1m` for this machine.
- Created governed launcher and monitor:

```text
run_full_rerun_2015_2020.ps1
monitor_full_rerun_2015_2020.ps1
```

- Executed short smoke test on separate smoke root:

```text
completed_tickers = 3
failed_tickers = 0
rows_written = 102,678
repairs_applied = 6
```

- Full rerun not launched by agent because `LONG_RUNNING_OPERATIONS_CONTRACT.md` requires human-visible launch command and monitor before long materialization runs.

## 2026-07-16 | 013 | failed 2015-2020 delta rerun completed

- Completed the controlled delta rerun for previously failed 2015..2020 physical candidate cases.
- Launcher final status:

```text
final_status = complete
exit_code = 0
completed_years = 6/6
```

- Year summaries verified:

```text
2015 complete failed_tickers=0 rows=21,995,617 repairs=627,338
2016 complete failed_tickers=0 rows=20,924,494 repairs=535,880
2017 complete failed_tickers=0 rows=22,619,373 repairs=711,769
2018 complete failed_tickers=0 rows=28,141,678 repairs=1,378,332
2019 complete failed_tickers=0 rows=27,102,457 repairs=1,021,067
2020 complete failed_tickers=0 rows=29,686,897 repairs=1,412,098
```

- Aggregate delta output:

```text
rows_written = 150,470,516
repairs_applied = 5,686,484
failed_tickers = 0
```

- Boundary preserved: this creates a parallel candidate delta root and does not by itself promote `013` or mutate the original `v0_1` tree.
- Next gate: reconcile original `v0_1` plus delta candidate, validate partitions/rows/schema/repair counts, then decide merge/promote path.

## 2026-07-16 | 013 | reconciliation PASS before technical merge

- Added reusable reconciliation script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\reconcile_ohlcv_1m_qg_failed_delta_v0_1.py
```

- Accepted reconciliation run:

```text
run_id = qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
status = PASS
errors = 0
warnings = 0
expected_unique_pairs = 3,918
committed_pairs = 3,918
output_file_missing = 0
schema_checked_files = 600
schema_mismatches = 0
```

- Evidence root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_reconciliation_runs\qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
```

- Decision boundary: reconciliation PASS authorizes preparing a technical `v0_2_candidate` merge; it does not authorize institutional promotion.

## 2026-07-16 | 013 | technical merge candidate v0_2 completed

- Created physical technical merge candidate:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Merge run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z
status = complete
mode = hardlink
errors = 0
original_files_seen = 1,272,004
original_files_linked = 1,228,331
original_files_skipped_expected_delta_pair = 43,673
delta_files_seen = 43,673
delta_files_linked = 43,673
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_build_runs\qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z\final_manifest_merge.json
```

- Boundary: this completes a technical candidate merge only. It does not promote the dataset. Next gate is validation of `v0_2_candidate`.

## 2026-07-16 | 013 | v0_2 candidate validation PASS

- Validated merged candidate tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Validation run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z
status = PASS
errors = 0
warnings = 0
candidate_files_seen = 1,272,004
candidate_files_from_original = 1,228,331
candidate_files_from_delta = 43,673
candidate_files_bad_source = 0
source_missing = 0
expected_delta_pairs_observed = 3,918
schema_checked = 600
schema_mismatches = 0
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\final_manifest_validation.json
```

- Boundary: `v0_2_candidate` is now a validated technical candidate tree and is eligible for promotion review. It is not yet promoted.





