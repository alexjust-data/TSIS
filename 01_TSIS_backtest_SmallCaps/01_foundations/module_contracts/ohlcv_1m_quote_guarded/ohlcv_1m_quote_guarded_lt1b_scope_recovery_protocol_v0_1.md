# OHLCV 1m Quote-Guarded LT1B Scope Recovery Protocol v0.1

## 1. Role

This protocol governs the recovery of the `ohlcv_1m_quote_guarded_v0_2`
repair work after the live runner was found to be using all ticker directories
under `E:/TSIS/data/ohlcv_1m` instead of the governed SmallCaps universe.

It is the single reading for:

- why the `12,168` planned-ticker scope is invalid for SmallCaps claims;
- which universe is authoritative;
- how already-written LT1B shards are reused without starting from zero;
- how the missing LT1B tail is completed;
- how the final manifest is consolidated without admitting out-of-scope
  tickers.

## 2. Authoritative Scope

The only valid ticker scope for this repair layer inside
`01_TSIS_backtest_SmallCaps` is:

```text
lt1b_universe_v0_1
```

Canonical source:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.parquet
```

Expected ticker count:

```text
4824
```

Equivalent compact identity materialization:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet
```

The raw OHLCV directory count is not a universe contract. A run that enumerates
all `ticker=*` directories under `E:/TSIS/data/ohlcv_1m` is a broad physical
scan, not a governed SmallCaps materialization.

## 3. Invalid Broad Run

Broad run root:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
```

Observed problem:

```text
planned_tickers = 12168
```

That scope includes tickers outside `lt1b_universe_v0_1`. Therefore:

- this run root must not be promoted as a final SmallCaps manifest;
- any unfiltered `repair_manifest.parquet` from this run is invalid for
  SmallCaps claims;
- the run root may still be used as an intermediate shard source, but only
  through a consolidator that filters by `lt1b_universe_v0_1` and validates
  completion.

At intervention time the broad run contained useful LT1B work:

```text
lt1b_tickers = 4824
lt1b_done_inside_broad_run = 4644
lt1b_missing_after_stop = 180
```

Stopping the broad runner prevents an invalid broad final consolidation. It
does not discard the already-written LT1B shards.

## 4. Supplement Run

The missing LT1B tickers are processed in a separate run root instead of
reusing the broad `RunRoot`. This avoids triggering a final manifest over all
existing broad-run shards.

Active supplement:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_lt1b_missing180_20260703_092956
```

Supplement rule:

- source ticker list = `lt1b_universe_v0_1 - broad_run_DONE`;
- runner = `scripts/run_ohlcv_1m_quote_guarded_repair_v0_2.ps1`;
- `-NoPromoteManifest` is mandatory;
- output remains a run artifact until LT1B consolidation passes.

Monitor command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956" -Watch -IntervalSeconds 30
```

## 5. LT1B Consolidator

The scope-safe consolidator is:

```text
scripts/inspection/minute/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.py
scripts/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1
scripts/monitor_ohlcv_1m_quote_guarded_lt1b_consolidation_v0_1.ps1
```

It accepts one or more repair run roots and enforces:

- `universe_tickers == 4824`;
- every LT1B ticker has a `DONE` status across the supplied run roots unless
  `-NoRequireComplete` is explicitly passed for dry/index-only diagnostics;
- selected repair shards must parse as `ticker_year_month`;
- selected repair shards must belong to an LT1B ticker;
- row-level `ticker` values inside each shard must match the shard ticker and
  remain inside `lt1b_universe_v0_1`;
- per-shard tables are normalized to the canonical LT1B repair-manifest schema
  before append;
- out-of-scope shards are counted and skipped, not written;
- no raw OHLCV parquet is modified.

Schema note:

- individual shard parquet files may differ in inferred physical type for
  otherwise identical fields, for example `v: int64` vs `v: double`;
- the consolidated LT1B manifest writes `v` as `double`;
- missing or unexpected manifest columns are a hard failure.

## 6. Dry Scope Check

Use this while the supplement is still running. It writes only completion and
shard-index files, not the large manifest:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1" -SkipManifest -NoRequireComplete
```

Expected behavior during an incomplete supplement:

- status may be `PASS` because `-NoRequireComplete` is a diagnostic bypass;
- `missing_tickers` must be greater than zero until the supplement completes;
- `skipped_out_scope_shards` must be greater than zero when the broad run root
  is included;
- no `manifest_path` is written.

## 7. Final Consolidation

After all 4,824 LT1B tickers are complete, run the final consolidation without
`-NoRequireComplete`. A supplement run may complete durably through
`ticker_status/`, `ticker_summaries/`, `month_summaries/`, and `repair_shards/`
even if its runner fails during final `repair_summary.json` creation. In that
case the consolidator's completion gate is the authoritative check.

Non-promoted final manifest under the consolidation run root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1" -Overwrite
```

Promoted output root command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1" -ManifestOutput "E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet" -Promote -Overwrite
```

Detailed monitor, in a second terminal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_ohlcv_1m_quote_guarded_lt1b_consolidation_v0_1.ps1" -ConsolidationRunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_lt1b_consolidation_manual_YYYYMMDD_HHMMSS" -Watch -IntervalSeconds 30
```

Promoted files:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json
```

## 8. Completion Gates

The final consolidation is not valid unless:

- `status = PASS`;
- `universe_tickers = 4824`;
- `completed_tickers = 4824`;
- `missing_tickers = 0`;
- `malformed_shard_names = 0`;
- `manifest_rows` is non-null when `-SkipManifest` is not used;
- `promoted_manifest` is non-empty only when `-Promote` is explicitly used.

The existence of broad-run repair shards is not enough. Completion is defined
by the LT1B ticker status table and the filtered shard index.

## 9. Power Outage Recovery

If Windows restarts, power fails, or terminals are closed, do not restart the
broad run.

Use this checklist.

### 9.1 Check supplement state

```powershell
python -c "import pandas as pd; p=r'C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956\ticker_summary.parquet'; df=pd.read_parquet(p); print({'rows': len(df), 'status_counts': df['status'].value_counts().to_dict()})"
```

If it reports:

```text
rows = 180
status_counts = {'DONE': 180}
```

the supplement finished. Continue to consolidation.

Do not require `repair_summary.json` for this supplement. The runner can fail
after durable shard/status completion while trying to build its final summary.
In that case the LT1B consolidator completion gate is authoritative.

If `ticker_summary.parquet` is missing or does not report `180` `DONE` rows,
restart only the supplement from its saved command:

```powershell
Get-Content "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956\resume_supplement_command.txt"
```

Paste the printed command into PowerShell.

Safety rules for supplement restart:

- use the same `RunRoot`;
- use the same 180-ticker allowlist;
- keep `-NoPromoteManifest`;
- do not add `-Overwrite`;
- do not use `supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1` for this
  supplement, because the v0_2 supervisor restarts the generic runner without
  the ticker allowlist.

Monitor the restarted supplement:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956" -Watch -IntervalSeconds 30
```

### 9.2 Check consolidation state

Manual consolidation run root:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_lt1b_consolidation_manual_20260703_094500
```

Check whether final consolidation already completed:

```powershell
Test-Path "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_lt1b_consolidation_manual_20260703_094500\consolidation_summary.json"
```

If it returns `True`, inspect the summary and do not rerun unless the summary
does not pass the completion gates.

If it returns `False` and the supplement has completed, open the consolidation
monitor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_ohlcv_1m_quote_guarded_lt1b_consolidation_v0_1.ps1" -ConsolidationRunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_lt1b_consolidation_manual_20260703_094500" -Watch -IntervalSeconds 30
```

Then launch final consolidation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1" -RunRoots "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838","C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956" -ConsolidationRunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_lt1b_consolidation_manual_20260703_094500" -ManifestOutput "E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet" -Promote -Overwrite
```

If consolidation is interrupted before `consolidation_summary.json`, rerun the
same command after confirming the supplement is complete. The `-Overwrite` flag
is intentional for the final promoted manifest path, not for raw OHLCV data.

### 9.3 2026-07-03 manual consolidation outage state

Observed after the power outage:

```json
{
  "observed_at_utc": "2026-07-03T11:10:49.726876+00:00",
  "stage": "writing_manifest",
  "shards_done": 220500,
  "shards_total": 421533,
  "rows_written": 170851670,
  "rows_per_sec": 56669,
  "current_shard": "C:\\TSIS_Data\\01_TSIS_backtest_SmallCaps\\runs\\data_foundation\\ohlcv_1m_quote_guarded\\quote_guarded_v0_2_20260627_091838\\repair_shards\\LGO_2024_04_repair_manifest.parquet",
  "manifest_path": "E:\\TSIS\\data\\data_foundation_outputs\\ohlcv_1m_quote_guarded\\repair_manifest_lt1b_v0_1.parquet"
}
```

Physical output state:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
size_bytes = 15229029775
last_write_time_utc = 2026-07-03T11:11:48Z

consolidation_summary.json = missing
repair_manifest_lt1b_v0_1_summary.json = missing
```

The partial parquet must not be treated as promoted or complete. The v0_1
consolidator writes `consolidation_status.json` during progress, but writes
`consolidation_summary.json` and the promoted output summary only after the
full manifest write completes successfully.

Post-outage checks executed on 2026-07-03:

```text
supplement ticker_summary rows = 180
supplement status_counts = DONE: 180
supplement months_done = 16053
supplement months_planned = 16053
supplement repair_rows = 5759227

preflight run root = C:/tmp/qg_lt1b_preflight_20260703_codex
preflight status = PASS
created_at_utc = 2026-07-03T13:00:19.753423+00:00
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
selected_repair_shards = 421533
skipped_out_scope_shards = 19510
skipped_incomplete_lt1b_shards = 0
malformed_shard_names = 0
```

Operational conclusion:

- the broad run must not be restarted;
- the 180-ticker supplement must not be restarted;
- the repair shards and LT1B shard index are the durable work product;
- the interrupted 52% manifest write is a partial derived artifact only;
- the final consolidation must be relaunched from the durable shards with the
  same command in section 9.2;
- `-Overwrite` is allowed only for the final manifest path and does not rewrite
  raw OHLCV or repair shards.

### 9.4 Resumability limitation

The v0_1 consolidator is not an append-resumable writer. If power fails before
`consolidation_summary.json` is written, the previous partial manifest cannot
be used as the contractual base for appending the remaining shards.

Reason:

- `consolidation_status.json` is a monitor checkpoint, not a transactional
  append checkpoint;
- the output parquet may not have a final footer and summary;
- the script does not map existing row groups back to the first N shard paths;
- appending blindly could duplicate, skip, or reorder shards.

If outage risk makes reprocessing the manifest write unacceptable, create a
separate v0_2 resumable consolidator before running final promotion. The safer
design is chunked output:

```text
repair_manifest_lt1b_v0_1.parts/
  part_000001.parquet
  part_000002.parquet
  ...
chunk_manifest.jsonl
consolidation_checkpoint.json
```

Each chunk must be written atomically, recorded in a durable checkpoint, and
validated against the LT1B shard index before final assembly or promotion. That
is a new implementation and validation task; it is not part of the v0_1
contract.
### 9.5 2026-07-03 LICN corrupt shard diagnosis

The relaunch of the final consolidation stopped after the monitor checkpoint
`220500 / 421533`, but the actual failing shard was later in the same 500-shard
progress interval:

```text
index_position_1based = 220884
failing_shard = LICN_2025_01_repair_manifest.parquet
error = Parquet magic bytes not found in footer
```

Root cause evidence in the broad run:

```text
run_root = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
month_summary = month_summaries/LICN_2025_01.json
status = ERROR
error = OSError(28, 'Error writing bytes to file. Detail: [errno 28] No space left on device')
```

Physical shard diagnosis:

```text
LICN_2025_01_repair_manifest.parquet size_bytes = 616855
LICN_2025_02_repair_manifest.parquet size_bytes = 241
both fail Parquet metadata reads with missing footer magic bytes
LICN shard files checked = 38
LICN readable shards = 36
LICN corrupt shards = 2
```

A targeted metadata scan over LT1B shards in the disk-full time window found:

```text
checked_suspect_lt1b = 1681
bad = 2
bad_shards = LICN_2025_01, LICN_2025_02
```

Operational conclusion:

- the consolidation should not be relaunched again with only the broad run and
  the 180-ticker supplement;
- the corrupt broad-run files must not be hand-edited or deleted as the primary
  fix;
- create a new `LICN`-only supplement run with `-NoPromoteManifest`;
- include that new supplement as the last `RunRoot` in the final LT1B
  consolidation so its `(LICN, 2025, 01/02)` shards override the corrupt broad
  run artifacts;
- after the `LICN` supplement, run a metadata validation over the final selected
  shard index before launching the large manifest write again.

Suggested repair command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_licn_repair_20260703" -Workers 1 -Tickers "LICN" -MinYear 2025 -MaxYear 2025 -NoPromoteManifest
```
### 9.6 2026-07-03 LICN supplement completed and preflight validated

The LICN-only supplement completed successfully:

```text
run_root = C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_lt1b_licn_repair_20260703
ticker_status = DONE
months_done = 12
months_planned = 12
repair_shards = 12
repair_rows = 19066
ohlc_repair_rows = 17260
vw_invalid_rows = 19012
```

The previously corrupt months now have readable Parquet shards:

```text
LICN_2025_01_repair_manifest.parquet rows = 8432
LICN_2025_02_repair_manifest.parquet rows = 8723
```

A three-root preflight was executed without writing the large manifest:

```text
preflight_run_root = C:/tmp/qg_lt1b_preflight_20260703_licn_patch
status = PASS
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
selected_repair_shards = 421533
skipped_out_scope_shards = 19510
skipped_incomplete_lt1b_shards = 0
malformed_shard_names = 0
```

The selected shard index now resolves all `LICN` 2025 months from the LICN
supplement run with `run_index = 2`; therefore `LICN_2025_01` and
`LICN_2025_02` no longer resolve to the corrupt broad-run artifacts.

Final consolidation must include three run roots, in this order:

```text
1. quote_guarded_v0_2_20260627_091838
2. quote_guarded_v0_2_lt1b_missing180_20260703_092956
3. quote_guarded_v0_2_lt1b_licn_repair_20260703
```
### 9.7 2026-07-03 final LT1B consolidation promoted

The final three-root consolidation completed and promoted the LT1B manifest:

```text
status = PASS
created_at_utc = 2026-07-03T16:13:47.256010+00:00
universe_dataset = lt1b_universe_v0_1
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
selected_repair_shards = 421533
written_shards = 421533
skipped_out_scope_shards = 19510
skipped_incomplete_lt1b_shards = 0
malformed_shard_names = 0
manifest_rows = 301278342
```

Final promoted artifacts:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
size_bytes = 27226860372
last_write_time_utc = 2026-07-03T16:12:09.0293981Z

E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json
size_bytes = 2019
last_write_time_utc = 2026-07-03T16:13:47.2489558Z

E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_sample.csv
size_bytes = 726926
last_write_time_utc = 2026-07-03T16:12:14.7899242Z
```

Run artifacts:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_lt1b_consolidation_manual_20260703_094500/consolidation_summary.json
size_bytes = 2019
last_write_time_utc = 2026-07-03T16:13:47.2489558Z
```

The final accepted run roots were, in order:

```text
1. quote_guarded_v0_2_20260627_091838
2. quote_guarded_v0_2_lt1b_missing180_20260703_092956
3. quote_guarded_v0_2_lt1b_licn_repair_20260703
```

Closeout conclusion: the quote-guarded LT1B manifest is promoted. Consumers may
only consume it through the contracted overlay model:

```text
raw ohlcv_1m + LT1B repair manifest = quote_guarded view
```
### 9.8 Never restart these commands after outage

Do not run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -Workers 12 -Overwrite
```

Do not run the v0_2 supervisor against the supplement run root.

Both can reintroduce the all-directory scope problem.

## 10. Prohibited Actions

Do not:

- promote `quote_guarded_v0_2_20260627_091838` directly;
- treat `12168` as the SmallCaps universe count;
- consolidate all broad-run shards without an LT1B filter;
- delete raw OHLCV bars;
- hand-edit raw parquet;
- declare quote-guarded VWAP reconstruction from quotes.

## 11. Downstream Contract

The resulting layer remains:

```text
raw ohlcv_1m + LT1B repair manifest = quote_guarded view
```

It is an overlay, not a cloned 20-year OHLCV tree. Consumers must load raw bars
and apply the repair manifest through the governed quote-guarded API or a later
contracted loader.
