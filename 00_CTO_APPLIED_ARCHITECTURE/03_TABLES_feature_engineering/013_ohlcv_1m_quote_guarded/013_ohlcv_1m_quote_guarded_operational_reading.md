# 013 OHLCV 1m Quote-Guarded Operational Reading

Status: `operational_reading_v0_9`

Date: `2026-07-16`

Scope:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\013_ohlcv_1m_quote_guarded
```

Primary physical artifact verified on this machine:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

Observed physical metadata:

```text
rows = 301,278,342
columns = 36
status = PASS
```

Important distinction:

```text
013_ohlcv_1m_quote_guarded
```

is not a final independent full physical bar table.

It is a governed quote-guarded repair overlay:

```text
raw ohlcv_1m
+
repair_manifest_lt1b_v0_1.parquet
=
ohlcv_1m_quote_guarded view
```

Raw `ohlcv_1m` remains immutable.

---

## Current Physical Candidate State

The historical physical tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1
```

is superseded for controlled downstream work by:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

v0.2 candidate evidence:

```text
merge_run_id = qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z
validation_run_id = qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z
validation_status = PASS
errors = 0
warnings = 0
candidate_files_seen = 1,272,004
candidate_files_from_original = 1,228,331
candidate_files_from_delta = 43,673
expected_delta_pairs_observed = 3,918
schema_checked = 600
schema_mismatches = 0
```

Operational reading:

```text
v0_2_candidate is a validated controlled downstream input.
v0_2_candidate is not unrestricted institutional promotion.
v0_2_candidate does not mutate raw ohlcv_1m.
v0_2_candidate does not replace trade or quote evidence.
```

Governance links:

```text
contract = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\ohlcv_1m_quote_guarded_dataset_contract_v0_1.md
policy = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\ohlcv_1m_quote_guarded_consumption_policy.md
registry = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\ohlcv_1m\ohlcv_1m_quote_guarded_registry_entry.yaml
```

---

## What Phenomenon Or Representation Do We Want To Materialize?

The target representation is an intraday 1-minute price view where impossible
raw OHLC components are guarded against observed quote evidence.

It represents:

```text
raw 1m OHLCV protected by a quote-envelope repair overlay
```

It does not represent:

```text
executed trade truth
exact premarket OHLCV
exact VWAP reconstruction
execution simulator input
clean full physical 1m replacement tree
```

---

## Why Does It Deserve To Exist As Its Own Entity?

Because raw `ohlcv_1m` contains minute bars whose OHLC components can be
incompatible with the observed quote book.

Those defects can contaminate:

```text
first push detection
intraday scanners
event candidates
event windows
market state
event state
intraday backtests
microstructure and intraday features
```

The entity deserves to exist because it preserves both requirements:

```text
1. raw data remains immutable as forensic source;
2. downstream consumers can use a deterministic quote-guarded view.
```

---

## What Scientific Questions Must It Answer?

This layer must let TSIS answer:

```text
Was this raw 1m candle compatible with the observed quote book?

Which ticker-minutes required repair?

Which OHLC components changed?

Did the intraday move still exist after quote guarding?

Was a scanner/event candidate caused by a real quote-confirmed move or a raw
spike artifact?

How much downstream exposure does a table, event population, state table,
backtest or experiment have to repaired minutes?

Was VWAP valid, invalid, preserved raw, or requiring future trade rebuild?
```

---

## What Other Representations Consume It?

Direct downstream consumers:

```text
014 master_intraday_bar_table
018 intraday_scanner_candidates_table
```

Indirect downstream consumers:

```text
015 microstructure_features_table
016 market_state_table
017 event_state_table
event_windows
intraday outcomes
experiments
backtests
future ML/RL datasets only if explicitly authorized later
```

---

## What Minimum Information Does It Need To Contain?

Minimum required information:

```text
ticker
timestamp
session_date
raw OHLCV
quote-guarded OHLC
repair_state
repair_reason
repair_applied flag
quote envelope
quote_count
VWAP status
source lineage
run/config/version provenance
```

The layer must preserve enough information to support:

```text
reproducibility
downstream filtering
repair exposure reporting
future supersession by trade-rebuilt OHLCV
```

---

## What Attributes Must It Have?

The verified manifest currently exposes these 36 columns:

```text
quote_guarded_view
ticker
ts_utc
minute_utc
minute_ny
session_date
year
month
repair_state
repair_reason
quote_guarded_repair_applied
o_raw
h_raw
l_raw
c_raw
o_qg
h_qg
l_qg
c_qg
vw
v
n
vw_quote_guarded_status
quote_bid_floor
quote_bid_p50
quote_ask_p50
quote_ask_cap
quote_mid_p50
quote_spread_p50
quote_spread_pct_p50
quote_count
quote_guard_config
source_ohlcv_path
source_quotes_path
manifest_created_at_utc
run_root
```

Interpretation:

```text
*_raw columns preserve source OHLC evidence.
*_qg columns define the quote-guarded OHLC view.
quote_* columns preserve the quote envelope evidence.
repair_* columns explain whether and why repair was applied.
source_* and run_root preserve lineage.
```

---

## Current Institutional Reading

Correct reading:

```text
repair_manifest_lt1b_v0_1.parquet is promoted/PASS for the LT1B scope.
raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet defines the quote-guarded view.
```

Incorrect reading:

```text
013 is a fully promoted physical replacement for all raw 1m bars.
013 proves exact premarket trade OHLCV.
013 proves exact VWAP.
013 is execution truth.
013 automatically promotes 014, 015, 016, 017 or 018.
```

Known local root difference:

```text
Some historical contracts reference E:\TSIS\data\...
This machine verifies the promoted manifest under G:\TSIS\data\...
```

---

## 2026-07-16 Verification Update

The important correction is:

```text
013 does not need to be created from zero.
```

The quote-guarded layer is already materialized as a promoted/PASS repair
manifest:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

The correct operational state is:

```text
013 overlay manifest = materialized / PASS
013 full corrected physical bar tree = not official full-universe source of truth
014+ consumers = must prove they consume the overlay correctly
```

Therefore, the next work is not to recreate `013`.

The next work is to use `013` correctly in downstream consumers:

```text
014 master_intraday_bar_table
018 intraday_scanner_candidates_table
015 microstructure_features_table
016 market_state_table
017 event_state_table
```

### Focused Tests Executed

Command executed from:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps
```

Test command:

```text
python -m pytest tests\test_ohlcv_1m_quote_guarded.py tests\data_foundation_outputs\test_master_intraday_quote_guarded_candidate_contract.py tests\data_foundation_outputs\test_master_intraday_quote_guarded_candidate_sample_builder.py tests\data_foundation_outputs\test_master_intraday_quote_guarded_candidate_scoped_builder.py
```

Result:

```text
7 passed in 2.81s
```

These tests verify:

```text
quote-guarded repair detection
quote-guarded repair application
raw columns preserved
volume preserved
VWAP blocked when quote-guarded status requires it
master_intraday quote-guarded candidate contract blocks promotion
sample builder materializes controlled candidate output
scoped builder materializes scoped candidate output
validators pass with hard_fail_count = 0
```


### Critical Correction: Physical Full-Universe Materialization Is Not Clean

The previous verification must not be misread as a clean full-universe physical
materialization.

The focused pytest result only proves the quote-guarded logic and scoped
consumer builders/tests. It does not prove that the full physical tree is clean.

Two different artifacts must remain separated:

```text
1. repair_manifest_lt1b_v0_1.parquet
   status = PASS
   role = promoted repair overlay / manifest

2. ohlcv_1m_quote_guarded_full_universe_v0_1
   status = candidate_not_official
   full_universe_claim = false
   role = physical candidate tree
   known issue = 2015..2020 complete_with_failures
```

Physical candidate root with known failures:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1
```

Authoritative local README for this physical tree states:

```text
physical_materialization_present = true
years_present = 2005..2026
global_clean_close_2005_2026 = false
candidate_not_official
full_universe_claim = false
```

Observed year materialization summaries from:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1\_build_runs\qg_1m_full_2015_2024_parallel_v0_1_20260707T092528Z
```

show unresolved failures:

```text
year  completed_tickers  failed_tickers  final_status
2015  4737               548             complete_with_failures
2016  4790               571             complete_with_failures
2017  4851               596             complete_with_failures
2018  4710               758             complete_with_failures
2019  4676               744             complete_with_failures
2020  4892               701             complete_with_failures
2021  6700               0               complete
2022  6707               0               complete
2023  6520               0               complete
2024  6282               0               complete
2025  6405               0               complete
2026  5982               0               complete
```

Sample failure files show:

```text
FileExistsError(17, 'No se puede crear un archivo que ya existe')
```

Current interpretation:

```text
The promoted overlay is valid/PASS.
The physical full-universe candidate tree is incomplete as a clean close.
The failures appear related to materialization/write/resume collisions, not to
an invalid LT1B repair overlay. This is an inference from the failure text and
the overlapping 2015-2024 materialization runs, not a promotion claim.
```

Operational consequence:

```text
Do not recreate the LT1B overlay.
Do rematerialize or reconcile the failed 2015..2020 physical candidate tickers.
Do not promote ohlcv_1m_quote_guarded_full_universe_v0_1 until failed_tickers = 0
and global reconciliation/validation close.
```

The next valid work on `013` is therefore not conceptual design. It is a
controlled repair/rematerialization pass over the failed 2015..2020 ticker-year
set, followed by reconciliation, validation and promotion review.

Operational failure manifest generated for that rerun:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\013_ohlcv_1m_quote_guarded\013_failed_tickers_2015_2020_v0_1.csv
```

Manifest scope:

```text
year  failed_tickers
2015  548
2016  571
2017  596
2018  758
2019  744
2020  701
total 3918
```

### Controlled Rerun Preparation: Ready, Not Full-Launched

A controlled delta rerun has been prepared for the failed 2015..2020 physical
candidate cases.

Important:

```text
The full rerun has not been launched by the agent.
Reason: LONG_RUNNING_OPERATIONS_CONTRACT requires human-visible command,
monitor, output root and scope before a long materialization run starts.
```

Prepared candidate output root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
```

Prepared run root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_build_runs\qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z
```

Prepared artifacts:

```text
pre_manifest_013_failed_rerun_v0_1.json
run_full_rerun_2015_2020.ps1
monitor_full_rerun_2015_2020.ps1
task_plan_failed_year_2015.csv
task_plan_failed_year_2016.csv
task_plan_failed_year_2017.csv
task_plan_failed_year_2018.csv
task_plan_failed_year_2019.csv
task_plan_failed_year_2020.csv
```

Task-plan scope:

```text
2015  548
2016  571
2017  596
2018  758
2019  744
2020  701
total 3918
```

Raw path correction applied in generated task plans:

```text
from E:\TSIS\data\ohlcv_1m
to   G:\TSIS\data\ohlcv_1m
```

Smoke test executed on a separate smoke root:

```text
run_id = qg_1m_failed_2015_delta_smoke_v0_1_20260716T000000Z
year = 2015
tickers = 3
final_status = complete
completed_tickers = 3
failed_tickers = 0
rows_written = 102,678
repairs_applied = 6
```

Smoke output root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_smoke_v0_1_candidate
```

Full rerun launch command for the human operator:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_build_runs\qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z\run_full_rerun_2015_2020.ps1"
```

Monitor command:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_build_runs\qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z\monitor_full_rerun_2015_2020.ps1"
```

Expected success condition:

```text
all six years final_status = complete
failed_tickers = 0 for 2015..2020
launcher_final_manifest.json exists with final_status = complete
```

Non-goal:

```text
This rerun does not promote 013.
It only produces a parallel candidate delta for the failed physical cases.
Promotion still requires reconciliation, validation and review.
```


### Controlled Rerun Execution: Completed

The controlled delta rerun was launched and completed.

Launcher final manifest:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_build_runs\qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z\launcher_final_manifest.json
```

Launcher result:

```text
final_status = complete
exit_code = 0
completed_years = 6/6
finished_at_utc = 2026-07-16T09:02:34.9256467Z
```

Year summary verification:

```text
year  status    completed_tickers  failed_tickers  rows_written  repairs_applied
2015  complete  548                0               21,995,617    627,338
2016  complete  571                0               20,924,494    535,880
2017  complete  596                0               22,619,373    711,769
2018  complete  758                0               28,141,678    1,378,332
2019  complete  744                0               27,102,457    1,021,067
2020  complete  701                0               29,686,897    1,412,098
```

Aggregate delta output:

```text
failed_tickers = 0
rows_written = 150,470,516
repairs_applied = 5,686,484
```

Important boundary:

```text
This closes the controlled delta rerun for the previously failed 2015..2020
physical candidate cases.

It does not by itself promote 013.
It does not mutate the original v0_1 physical tree.
It creates a parallel candidate delta root that must be reconciled/merged or
compared under an explicit validation step before any clean full-universe claim.
```

Parallel delta root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
```

Next required gate:

```text
reconcile original v0_1 + failed_2015_2020_delta candidate
validate row/schema/partition/repair counts
then decide merge/promote path
```

### Final 013 Reading

Use this reading going forward:

```text
013 is done as a governed quote-guarded overlay.
013 is not done as an official full-universe physical replacement tree.
013 should now be consumed by 014 and downstream tables under explicit tests,
validators and manifests.
```
---

## What This Enables Next

`013` enables the next operational step:

```text
014 master_intraday_bar_table
```

Specifically:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

The correct dependency is:

```text
013 quote-guarded repair manifest
    ->
014 master intraday bar candidate
    ->
018 intraday scanner candidates
    ->
event windows
    ->
015 microstructure features
    ->
016 market state
    ->
017 event state
```

---

## Required Questions For Every Future Table

From this point forward, every table analysis in this folder should answer
these questions before attributes are finalized:

```text
What phenomenon or representation do I want to materialize?

Why does it deserve to exist as its own entity?

What scientific questions must it answer?

What other representations consume it?

What minimum information does it need to contain?

Now, and only now:
What attributes must it have?
```

Operational rule:

```text
Do not start by listing columns.
Start by defining representation responsibility.
Then derive the minimum required attributes.
```







---

## 2026-07-16 Reconciliation Test Before Merge

A non-destructive reconciliation test was executed after the failed 2015..2020 delta rerun.

Test script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\reconcile_ohlcv_1m_qg_failed_delta_v0_1.py
```

Validated inputs:

```text
original_root = C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1
delta_root    = C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
expected_csv  = C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\013_ohlcv_1m_quote_guarded\013_failed_tickers_2015_2020_v0_1.csv
```

Accepted reconciliation result:

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

Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_reconciliation_runs\qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z\reconciliation_result.json
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_reconciliation_runs\qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z\reconciliation_issues.csv
```

Operational conclusion:

```text
The delta is reconciled against the expected 3,918 failed ticker-years.
This PASS authorizes preparing a technical merge candidate.
It does not promote the dataset.
```

Merge rule:

```text
For the 3,918 expected failed ticker-years, delta supersedes original v0_1.
For all other partitions, original v0_1 remains the source for the merge candidate.
```

Boundary:

```text
schema-mode all was tested and found too long for an unmonitored interactive command.
The accepted run used an equidistant schema sample of 600 parquet files.
A full schema scan can be launched separately before promotion if required.
```

---

## 2026-07-16 Technical Merge Candidate Completed

A governed hardlink merge was executed to create the physical candidate tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

Merge script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\merge_ohlcv_1m_qg_full_universe_v0_2_candidate.py
```

Monitor script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\monitor_ohlcv_1m_qg_merge_v0_1.py
```

Accepted merge run:

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

Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_build_runs\qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z\final_manifest_merge.json
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\README.md
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\latest_run_id.txt
```

Operational conclusion:

```text
v0_2_candidate exists as a technical merge candidate.
It combines v0_1 original plus the corrected 3,918 ticker-year delta.
It is not promoted.
```

Next required gate:

```text
Validate v0_2_candidate as a complete candidate tree before any promotion decision.
```

---

## 2026-07-16 v0_2 Candidate Validation PASS

A governed validation run was executed against the merged candidate tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

Validation script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\validate_ohlcv_1m_qg_v0_2_candidate.py
```

Monitor script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\monitor_ohlcv_1m_qg_validation_v0_1.py
```

Accepted validation run:

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

Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\final_manifest_validation.json
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\validation_issues.csv
```

Operational conclusion:

```text
v0_2_candidate is a validated technical candidate tree.
It is eligible for promotion review.
It is not yet promoted.
```

Promotion boundary:

```text
validation PASS != institutional promotion
promotion_authorization = false
```

