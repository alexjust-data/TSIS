# Ohlcv 1m Split-Normalized Full-Universe Materialization Runbook `v0_1`

## 1. Decision

For official intraday backtesting and ML, the data scope used by the experiment
must be split-safe.

Rule:

```text
If a backtest/ML run claims to use the full <1B> intraday universe, the 1m
price view consumed by features, cross-session states and labels must be
available as a governed split-normalized view for that same universe/scope.
```

This does not mean that every workflow must immediately duplicate every raw 1m
file into a new physical root.

It means:

```text
the exact scope consumed by the official run must have a declared split-safe
price-view strategy, manifest, tests, output root and registry status.
```

## 2. Raw vs Split-Normalized Roles

`1m_raw`:

- observed market price scale;
- execution truth candidate only when paired with trades/quotes as needed;
- required for local intraday tape/price behavior.

`1m_split_normalized`:

- cross-session comparable price scale;
- required for gaps, multi-day context, ML features and labels that cross split
  boundaries;
- not execution truth.

`daily_adjusted`:

- daily economic continuity;
- not a replacement for minute execution prices.

## 3. What The Existing Pilot Means

`E:/TSIS/data/ohlcv_1m_split_normalized` currently contains a validated
proof/pilot materialization.

It proves:

```text
the split-normalization method and code work on inspected split cases.
```

It does not prove:

```text
all raw 1m ticker-months have already been physically normalized.
```

## 4. Recommended Institutional Path

There are two valid materialization paths.

### Path A1 - Logical Full-Universe Split-Safe View

Materialize only ticker-months where a future split changes price scale.

For ticker-months with no future split effect, raw 1m is already equivalent to
split-normalized price scale because:

```text
future_split_factor = 1
```

This path is usually the right first institutional target because it avoids
duplicating all raw 1m files where nothing changes.

Output status should be:

```text
full_universe_split_safe_logical_view_candidate
```

### Path A2 - Physical Full Copy

Materialize every raw 1m ticker-month into a split-normalized root, including
factor-1 months.

This is simpler for downstream readers but heavier and slower.

Output status should be:

```text
physical_full_universe_1m_split_normalized_candidate
```

Use this only if downstream systems require one physical parquet root with every
minute row.

## 5. Source Roots

Preferred current roots:

```text
minute_root = E:/TSIS/data/ohlcv_1m
splits_root = E:/TSIS/data/additional/corporate_actions/splits
```

Historical/default script roots may mention `D:/ohlcv_1m` or
`C:/TSIS_Data/data/additional/...`; do not use those unless intentionally
replaying an old run.

## 6. Smoke Test Commands

Run this first in PowerShell. It builds a tiny manifest only.

Preferred runner:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -SmokeOnly `
  -SmokeLimit 100 `
  -Mode split-affected
```

The preferred runner is governed by:

```text
C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md
```

At startup it must print:

- run id;
- run root;
- output root;
- pre-manifest path;
- heartbeat path;
- PID manifest path;
- monitor command.

Monitor command shape:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_long_running_operation.ps1" `
  -RunRoot "<printed_run_root>" `
  -RunId "<printed_run_id>" `
  -Compact `
  -Watch
```

Expected telemetry files inside the printed run root:

```text
<run_id>.pre_manifest.json
<run_id>.heartbeat.json
<run_id>.heartbeat.jsonl
<run_id>.pids.json
_run_summary.json
```

Manual equivalents in this document are documentation of the underlying steps,
not the preferred operational path. If a human or agent uses a manual
equivalent for a long run, it must reproduce the same pre-manifest, heartbeat,
PID manifest, timestamps, logs and monitor surface.

Manual equivalent:

```powershell
$PROJECT = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION"
$RUN_ROOT = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\data_foundation\1m_split_normalized_full_universe_candidate\smoke_$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory -Force -Path $RUN_ROOT | Out-Null

python "$PROJECT\scripts\build_1m_split_normalized_materialization_manifest.py" `
  --minute-root "E:\TSIS\data\ohlcv_1m" `
  --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
  --output "$RUN_ROOT\manifest_smoke.csv" `
  --mode split-affected `
  --limit 100
```

Expected result:

```text
manifest_smoke.csv
manifest_smoke.summary.json
```

Do not promote smoke outputs.

Optimization requirement:

```text
split-affected smoke must not scan the entire ohlcv_1m tree with Path.rglob().
```

The manifest builder must use:

```text
splits_root -> ticker with split file -> expected ticker/year/month path in ohlcv_1m
```

Latest successful smoke evidence:

```text
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_153012/
rows: 100
tickers: 1
scan_strategy: split_tickers_then_partition_direct
files_seen: 139
files_without_split_effect: 39
split_tickers_seen: 4
runtime: 7.7s
official_dataset_created: false
```

Non-valid smoke attempt:

```text
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_152403/
state: timed out before manifest/log creation
reason: previous builder path used global ohlcv_1m tree scan
valid_evidence: false
```

## 7. Recommended Overnight Command - Split-Affected Scope

This builds a manifest for ticker-months that actually need split-normalized
materialization because a future split affects their scale.

Preferred runner:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -Mode split-affected
```

With post-run split-event audit:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -Mode split-affected `
  -RunAudit
```

Manual equivalent:

```powershell
$PROJECT = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION"
$RUN_ID = "split_affected_$(Get-Date -Format yyyyMMdd_HHmmss)"
$RUN_ROOT = "$PROJECT\runs\data_foundation\1m_split_normalized_full_universe_candidate\$RUN_ID"
$MANIFEST = "$RUN_ROOT\manifest_split_affected.csv"
$CHUNKS = "$RUN_ROOT\chunks"
$OUT = "E:\TSIS\data\ohlcv_1m_split_normalized_full_universe_candidate"

New-Item -ItemType Directory -Force -Path $RUN_ROOT | Out-Null

python "$PROJECT\scripts\build_1m_split_normalized_materialization_manifest.py" `
  --minute-root "E:\TSIS\data\ohlcv_1m" `
  --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
  --output "$MANIFEST" `
  --mode split-affected `
  --chunk-size 5000 `
  --chunks-dir "$CHUNKS" `
  2>&1 | Tee-Object -FilePath "$RUN_ROOT\build_manifest.log"

Get-ChildItem "$CHUNKS\*.csv" | Sort-Object Name | ForEach-Object {
  $chunkLog = "$RUN_ROOT\materialize_$($_.BaseName).log"
  python "$PROJECT\scripts\materialize_1m_split_normalized.py" `
    --minute-root "E:\TSIS\data\ohlcv_1m" `
    --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
    --output-root "$OUT" `
    --manifest $_.FullName `
    2>&1 | Tee-Object -FilePath $chunkLog
}

$ManifestRows = (Import-Csv $MANIFEST).Count
$OutputFiles = (Get-ChildItem $OUT -Recurse -Filter "*_split_normalized.parquet").Count
[PSCustomObject]@{
  run_root = $RUN_ROOT
  manifest_rows = $ManifestRows
  output_files = $OutputFiles
  output_root = $OUT
} | Format-List
```

Important:

- no `--overwrite` is used;
- rerunning skips existing files where possible;
- this is the preferred first large run.

Latest completed run:

```text
run_id: split_affected_20260627_192314
mode: split-affected
run_root: C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/1m_split_normalized_full_universe_candidate/split_affected_20260627_192314
output_root: E:/TSIS/data/ohlcv_1m_split_normalized_full_universe_candidate
manifest_rows: 115667
chunk_count: 24
output_files_present: 115667
audit_run: true
audit_status: completed
```

Results document:

```text
01_foundations/module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md
```

## 8. Heavier Overnight Command - Physical Full Copy

Use only if the goal is to physically materialize every raw 1m ticker-month,
including factor-1 months.

Preferred runner:

```powershell
& "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_1m_split_normalized_materialization.ps1" `
  -Mode all-existing
```

Manual equivalent:

```powershell
$PROJECT = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION"
$RUN_ID = "physical_all_existing_$(Get-Date -Format yyyyMMdd_HHmmss)"
$RUN_ROOT = "$PROJECT\runs\data_foundation\1m_split_normalized_full_universe_candidate\$RUN_ID"
$MANIFEST = "$RUN_ROOT\manifest_all_existing.csv"
$CHUNKS = "$RUN_ROOT\chunks"
$OUT = "E:\TSIS\data\ohlcv_1m_split_normalized_physical_full_candidate"

New-Item -ItemType Directory -Force -Path $RUN_ROOT | Out-Null

python "$PROJECT\scripts\build_1m_split_normalized_materialization_manifest.py" `
  --minute-root "E:\TSIS\data\ohlcv_1m" `
  --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
  --output "$MANIFEST" `
  --mode all-existing `
  --chunk-size 5000 `
  --chunks-dir "$CHUNKS" `
  2>&1 | Tee-Object -FilePath "$RUN_ROOT\build_manifest.log"

Get-ChildItem "$CHUNKS\*.csv" | Sort-Object Name | ForEach-Object {
  $chunkLog = "$RUN_ROOT\materialize_$($_.BaseName).log"
  python "$PROJECT\scripts\materialize_1m_split_normalized.py" `
    --minute-root "E:\TSIS\data\ohlcv_1m" `
    --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
    --output-root "$OUT" `
    --manifest $_.FullName `
    2>&1 | Tee-Object -FilePath $chunkLog
}

$ManifestRows = (Import-Csv $MANIFEST).Count
$OutputFiles = (Get-ChildItem $OUT -Recurse -Filter "*_split_normalized.parquet").Count
[PSCustomObject]@{
  run_root = $RUN_ROOT
  manifest_rows = $ManifestRows
  output_files = $OutputFiles
  output_root = $OUT
} | Format-List
```

Warning:

```text
This can take much longer and write much more data than Path A1.
```

## 9. Audit Command

After either materialization path, rerun the split-event audit so the new run
can be evaluated against the same institutional logic.

```powershell
$PROJECT = "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION"
$AUDIT_ROOT = "$RUN_ROOT\full_universe_split_event_audit"

python "$PROJECT\scripts\inspection\minute\audit_1m_split_full_universe.py" `
  --minute-root "E:\TSIS\data\ohlcv_1m" `
  --splits-root "E:\TSIS\data\additional\corporate_actions\splits" `
  --output-root "$AUDIT_ROOT" `
  2>&1 | Tee-Object -FilePath "$RUN_ROOT\audit_full_universe_split.log"
```

Expected audit outputs:

```text
full_universe_split_event_cases.csv
full_universe_split_event_cases.parquet
full_universe_split_event_status_summary.csv
full_universe_split_event_audit_meta.csv
```

## 10. Promotion Gate

The resulting output is not institutional just because files were written.

Promotion requires:

- manifest summary reviewed;
- materialized file count reconciled to manifest rows;
- audit outputs reviewed;
- schema/registry/policy updated for the new root;
- tests added or parameterized for the new root;
- Graphify queue updated;
- changelog updated;
- explicit status chosen:
  - `logical_full_universe_split_safe_candidate`;
  - `physical_full_universe_candidate`;
  - or `rejected/quarantine`.

Until then, the output root is a candidate materialization, not a production
backtest/ML source.
