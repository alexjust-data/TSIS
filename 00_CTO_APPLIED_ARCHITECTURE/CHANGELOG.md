# 00_CTO_APPLIED_ARCHITECTURE Changelog

This changelog records semantic, structural and governance-relevant changes in:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
```

It does not replace:

```text
C:\TSIS_Data\CHANGELOG.md
C:\TSIS_Data\00_CTO\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\CHANGELOG.md
```

Use this changelog for changes to the applied architecture map, local rules,
Graphify map, table reading surface and continuation guides.

Do not use it for ordinary Git noise or minor typos.

---

## 2026-07-17 | 03_TABLES_feature_engineering | information object model alignment

- Refactored the market representation family catalog so it aligns with `00_FEATURE_ADMISION_PROCESS.md`.
- The catalog now maps families to Information Objects, variables, physical tables, consumers and coverage status.


## 2026-07-17 | applied architecture | folder numbering normalized

- Reordered top-level applied architecture folders so `03_TABLES_feature_engineering` sits immediately after `02_MATERIALIZATION_GOVERNANCE_REVIEW`.
- Renamed:

```text
03_DATA_Raw_audit    -> 04_DATA_Raw_audit
04_DATA_Live_Source  -> 05_DATA_Live_Source
05_STRATEGIES_know   -> 06_STRATEGIES_know
```

- Updated internal references from old `06_TABLES` / `06_TABLES_feature_engineering` paths to `03_TABLES_feature_engineering`.
- Preserved the distinct duplicate file found under the transient `06_TABLES_feature_engineering` folder as:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_FEATURE_ADMISION_PROCESS_duplicate_preserved_20260717.md.md
```

- Removed the now-empty duplicate `06_TABLES_feature_engineering` folder.


## 2026-07-16 | 03_TABLES_feature_engineering | consolidated family attribute index

- Added `03_TABLES_feature_engineering/MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md`.
- It maps market representation families to known attributes from `000-012` and pending responsibilities for `013-018`.


## 2026-07-16 | 03_TABLES_feature_engineering | ES block format for table readings

- Reformatted Spanish table representation readings `000` through `012` into block-based answers with explicit line breaks.
- Purpose: make family, hypothesis, variables and consumers readable at a glance.


## 2026-07-16 | 03_TABLES_feature_engineering | concise spanish representation readings

- Rewrote Spanish per-table audits `000` through `012` into short family-based representation readings.
- Purpose: reduce documentation noise and focus variable admission on phenomenon, hypothesis, minimum variables and consumers.


## 2026-07-16 | 03_TABLES_feature_engineering | spanish audit copies

- Added Spanish copies of the feature-engineering guardrail, audit template and per-table audits `000` through `012`.
- Boundary: originals were preserved; no dataset status or promotion changed.


## 2026-07-16 | 03_TABLES_feature_engineering | 000-012 representation audits

- Generated per-table representation audits for `000` through `012` under `03_TABLES_feature_engineering`.
- Purpose: document what each table represents, which variable families it owns, why those variables deserve to exist, and how they contribute to Market State / Event State / downstream research.
- Boundary: these are applied architecture audits, not dataset promotions.


## 2026-07-16 | 03_TABLES_feature_engineering | market representation guardrails

- Added `03_TABLES_feature_engineering/TABLES_REPRESENTATION_OF_MARKET.md`.
- Added `03_TABLES_feature_engineering/TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Updated local README and LOCAL_RULES to make variable selection depend on market representation family, scientific hypothesis, downstream consumer and evidence.
- Boundary: this is an applied architecture audit surface, not an operational source of truth.

## 2026-07-16 | 013 | quote-guarded v0_2 controlled consumption recorded

- Updated `03_TABLES_feature_engineering/013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md` to `operational_reading_v0_9`.
- Recorded that `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` passed validation and supersedes the v0.1 failed physical tree for controlled downstream work.
- Linked the new foundations contract, policy and registry entry.
- Boundary preserved: controlled downstream input only; not unrestricted institutional promotion and not raw mutation.

## 2026-07-16 | local governance | local agent/rules/changelog scaffold

- Added local `AGENTS.md` to define the entry point for agents working in
  `00_CTO_APPLIED_ARCHITECTURE`.
- Added local `LOCAL_RULES.md` to clarify that this folder is applied
  architecture and not operational source of truth.
- Added this `CHANGELOG.md`.
- Added `03_TABLES_feature_engineering/LOCAL_RULES.md` and `03_TABLES_feature_engineering/CHANGELOG.md` for table work
  governance.
- Established the mandatory six-question gate for future table work.

## 2026-07-16 | 013 | quote-guarded operational reading verified

- Created/updated `03_TABLES_feature_engineering/013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md`.
- Correct reading fixed:

```text
013 = raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay
```

- Verified promoted/PASS manifest locally under:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

- Focused quote-guarded tests executed:

```text
7 passed in 2.81s
```

- Important limitation preserved: `013` is not an official full-universe
  physical replacement tree.

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





