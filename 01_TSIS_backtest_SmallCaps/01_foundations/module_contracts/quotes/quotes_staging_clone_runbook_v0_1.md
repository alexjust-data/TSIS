# Quotes Recovery Clone To Target E-root Runbook v0.1

Filename note: this file keeps the historical `quotes_staging_clone_runbook`
name for link stability. Semantically, `E:/TSIS/data/quotes_` is now the target
official E-root pending post-copy parity audit and promotion, not disposable
staging.

## Purpose

This runbook defines the safe operational clone from:

```text
D:/quotes
```

to:

```text
E:/TSIS/data/quotes_
```

The target is intentionally named `quotes_` and, as of the 2026-06-29
clarification, is the target official E-root for the active `D:/quotes`
recovery clone. It must not be consumed officially until post-copy parity audit
and promotion exist. The pre-existing `E:/TSIS/data/quotes` tree is
legacy/incomplete for this recovery decision.

## Authority Rule

The official TSIS market-data database root is:

```text
E:/TSIS/data
```

For quotes recovery, the target official E-root is:

```text
E:/TSIS/data/quotes_
```

It is blocked from downstream official consumption until post-copy parity audit
and promotion. The pre-existing `E:/TSIS/data/quotes` tree is legacy/incomplete
for this recovery decision.

`D:/quotes` and `C:/TSIS_Data/data/quotes` are not official database roots for
new consumption. They may appear in historical manifests as provenance paths
because earlier inspection evidence was generated from those physical locations.

Those paths can be used only for forensic reconciliation, recovery comparison or
lineage validation. They must not be introduced into downstream table contracts
as primary source-of-truth roots.

## Why This Exists

The visual quotes inspection manifests include audited cases whose `source_file`
points to `D:/quotes`. A spot check found cases that are present in `D:/quotes`
but not under `E:/TSIS/data/quotes`.

The project needs a clean recovery clone into the target E-root before deciding
whether `quotes_` can be promoted, indexed or consumed by downstream tables such
as `microstructure_features_table`.

This does not mean `D:/quotes` becomes authoritative. The clone exists to move
legacy physical evidence into an auditable target E-root under the official
`E:/TSIS/data` storage topology.

## Non-Negotiable Safety Rules

- Do not run a destructive mirror.
- Do not use `/MIR`.
- Do not use `/PURGE`.
- Do not delete anything from `E:/TSIS/data/quotes`.
- Do not treat `quotes_` as consumable by official downstream systems until a
  post-copy audit exists.
- Do not update consumers to read `quotes_` as an official source of truth
  without a separate promotion decision.
- Do not use `C:/TSIS_Data/data/quotes` or `D:/quotes` as official roots in new
  output contracts.

## Script

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/data_ops/clone_quotes_to_staging.ps1
```

Default roots:

```text
SourceRoot = D:/quotes
TargetRoot = E:/TSIS/data/quotes_
LogRoot    = E:/TSIS/data/data_ops_manifests/quotes_clone
```

The script uses `robocopy` because the operation can involve millions of files.
It writes a pre-manifest, PID manifest, heartbeat JSON/JSONL, robocopy log and
final JSON manifest for each new run.

For million-file roots, the preferred operational mode is ticker-chunked
copying with `-ChunkByTicker`. This enumerates only the top-level ticker
directories under `D:/quotes` and launches one observable robocopy unit per
ticker. It avoids a recursive pre-count of the whole tree while still exposing
`current_index/total_count`, the active ticker path, PID state and heartbeat
age in the monitor.

This runbook is governed by:

```text
C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md
```

Every new full clone, scoped clone, dry-run or resume must print a monitor
command at startup. The generic monitor is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" `
  -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_clone" `
  -Compact `
  -Watch
```

If a specific `Run ID` is printed by the runner, add:

```powershell
-RunId "<printed_run_id>"
```

Expected telemetry files:

```text
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.pre_manifest.json
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.heartbeat.json
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.heartbeat.jsonl
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.pids.json
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.robocopy.log
E:/TSIS/data/data_ops_manifests/quotes_clone/<run_id>.manifest.json
```

Operational note:

An old run launched before this telemetry upgrade may only have a robocopy log
and final manifest at completion. That legacy limitation must not be used as a
template for new long-running commands.

If such a legacy blind run is still alive and the operator needs live progress,
stop it from the terminal that launched it, keep the partial target tree, and
resume with the ticker-chunked command below. Do not run the blind root clone
and the ticker-chunked clone against `E:/TSIS/data/quotes_` at the same time.

## Dry Run

Full-tree dry-run is usually not useful for this dataset because it still scans
millions of files. Use it only if the operator explicitly wants a full scan
without copying:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1"
```

Dry-run mode uses robocopy `/L`, so it scans and reports but does not copy.

## Small Scoped Smoke Test

Before launching the full clone, run a small real copy for one known source
subtree. This validates permissions, path preservation, logging and manifest
creation without scanning all `D:/quotes`.

Example:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -SubPath "SGC\year=2013\month=11\day=04"
```

The target written by this command is:

```text
E:/TSIS/data/quotes_/SGC/year=2013/month=11/day=04/
```

For another sample, replace `-SubPath` with a different relative path under
`D:/quotes`.

## Ticker-Chunk Observable Clone

For this dataset, this is the recommended full operational mode. It is more
observable than a single root-level robocopy because the monitor can report the
active ticker chunk and completed ticker count.

Dry-run one ticker chunk:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -ChunkByTicker `
  -MaxTickerChunks 1 `
  -HeartbeatSeconds 10
```

Real resumable ticker-chunk clone:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -AllowNonEmptyTarget `
  -ChunkByTicker `
  -ThreadCount 64 `
  -Retries 2 `
  -WaitSeconds 2 `
  -HeartbeatSeconds 30
```

Resume from a known ticker after a stopped run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -AllowNonEmptyTarget `
  -ChunkByTicker `
  -StartAtTicker APEX `
  -ThreadCount 64 `
  -Retries 2 `
  -WaitSeconds 2 `
  -HeartbeatSeconds 30
```

Use `-StartAtTicker` only when the previous run evidence proves the last
completed ticker. The value must exist as a top-level ticker directory under
`D:/quotes`.

For a real one-ticker smoke copy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -AllowNonEmptyTarget `
  -ChunkByTicker `
  -MaxTickerChunks 1 `
  -HeartbeatSeconds 10
```

## Direct Root Copy

Direct root copy is permitted but no longer preferred for this million-file
quotes root when a human needs live progress. It produces one robocopy unit for
the whole tree, so the monitor cannot show ticker-level completion.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run
```

## Resume Or Update

If the ticker-chunked copy is interrupted or the target already has content:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -AllowNonEmptyTarget `
  -ChunkByTicker `
  -ThreadCount 64 `
  -Retries 2 `
  -WaitSeconds 2 `
  -HeartbeatSeconds 30
```

This resumes or updates the staging tree. It still does not delete target extras.

Known interruption class:

```text
Move-Item : No se puede crear un archivo que ya existe.
```

This was a telemetry-wrapper failure in the heartbeat writer, not a robocopy
data failure. It was fixed by replacing `Move-Item -Force` with a Windows-safe
temporary-file replacement strategy in:

```text
scripts/data_ops/clone_quotes_to_staging.ps1
```

If an older run stops with that error, do not delete the target. Resume with the
same ticker-chunk command above, optionally with `-StartAtTicker` when the next
ticker is known from log evidence. Robocopy will skip unchanged files and
continue copying missing or changed files.

## Performance Controls

Default:

```text
ThreadCount = 32
Retries     = 3
WaitSeconds = 5
```

For ticker-chunked quotes cloning on the current large staging recovery, use:

```text
ThreadCount = 64
Retries     = 2
WaitSeconds = 2
```

`MaxTickerChunks` exists only for smoke tests and bounded diagnostics. It must
not be used for the full recovery run.

For slower disks or unstable IO, reduce thread count:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -ThreadCount 16
```

For large sequential files, `-Unbuffered` adds robocopy `/J`. Do not use it
blindly if the workload is dominated by many small files.

## Post-Copy Requirement

After the clone, a separate audit must compare at minimum:

- source file count;
- target file count;
- source total bytes;
- target total bytes;
- representative file hashes;
- manifest case coverage for good/review/bad quotes;
- failures or retries from the robocopy log.

Only after that audit can `quotes_` be used for official downstream
consumption. `E:/TSIS/data/quotes` remains legacy/incomplete unless a separate
documented migration decision changes that status.

This quote-specific audit is one instance of the broader final RAW storage
parity requirement defined in:

```text
01_foundations/module_contracts/transversal/raw_storage_parity_audit_requirement_v0_1.md
```

The final Data Foundation audit must prove that every raw/source-preserved
family still present under `D:/` has an equivalent governed landing under
`E:/TSIS/data` before the migration can be treated as complete.

## Post-Copy Parity Audit Protocol

This section is the operational plan for the post-copy audit of:

```text
source = D:/quotes
target = E:/TSIS/data/quotes_
```

The clone can be considered operationally copied after the robocopy run reports
success, but it cannot be promoted for official downstream consumption until
the parity audit passes. A robocopy success code is not enough by itself for the
Data Foundation promotion gate.

### Auditor

Use:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/data_ops/audit_quotes_clone_parity.py
```

The auditor is read-only against `D:/quotes` and `E:/TSIS/data/quotes_`. It
writes only audit evidence under:

```text
E:/TSIS/data/data_ops_manifests/quotes_parity_audit
```

It skips reparse points/junctions, matching the clone policy that used robocopy
`/XJ`.

### Evidence Written Per Run

Each audit run writes:

```text
<run_id>.pre_manifest.json
<run_id>.heartbeat.json
<run_id>.heartbeat.jsonl
<run_id>.pids.json
<run_id>.manifest.json
<run_id>.summary.csv
<run_id>.mismatches.csv
<run_id>.ticker_results/
<run_id>.mismatches/
```

The heartbeat is compatible with the generic long-running monitor:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/monitor_long_running_operation.ps1
```

### Two-Phase Safety Policy

Use two audit phases.

Phase A is mandatory structural parity:

```text
hash_mode = mismatches-only
```

It proves, per ticker shard:

- source and target top-level ticker roster match;
- every source relative file path exists in target;
- target does not contain unexpected extra relative file paths for the audited
  ticker;
- byte sizes match;
- hashes are computed only for structural mismatch cases to support diagnosis.

Phase B is optional operationally but required for the strongest "0 percent
clone error" claim:

```text
hash_mode = full
```

It computes SHA256 for every paired file. This is much slower and heavier on
disk IO, but it is the strictest proof that target bytes equal source bytes.

Do not run Phase A and Phase B at the same time. Run Phase B only after Phase A
has passed for all shards, or when the operator explicitly accepts the IO cost.

### Parallel Sharding Policy

The quotes root has roughly five thousand ticker directories. For the overnight
audit, split the sorted top-level ticker roster into five deterministic shards:

```text
shard_count = 5
shard_index = 0..4
```

This is safer than one monolithic process because each shard has its own
manifest, heartbeat, PID file and mismatch report. If one shard fails, only that
shard needs diagnosis or rerun.

Do not use high worker counts inside every shard. Five shards with too many
workers can overload the disks and make the audit less reliable. Recommended
starting point:

```text
Phase A structural: workers=3 per shard, total about 15 workers
Phase B full SHA256: workers=2 per shard, total about 10 workers
```

Increase only after observing stable disk IO, heartbeat age and free space.

### Phase A Commands - Structural Parity

Open five terminals and launch one shard per terminal. These commands are one
line each for copy/paste use.

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 3 --hash-mode mismatches-only --shard-count 5 --shard-index 0 --run-id "quotes_parity_struct_s0_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 3 --hash-mode mismatches-only --shard-count 5 --shard-index 1 --run-id "quotes_parity_struct_s1_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 3 --hash-mode mismatches-only --shard-count 5 --shard-index 2 --run-id "quotes_parity_struct_s2_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 3 --hash-mode mismatches-only --shard-count 5 --shard-index 3 --run-id "quotes_parity_struct_s3_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 3 --hash-mode mismatches-only --shard-count 5 --shard-index 4 --run-id "quotes_parity_struct_s4_20260703" --heartbeat-seconds 30
```

### Phase A Monitor Commands

Open separate monitor terminals if the runner terminals are not visible.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_s0_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_s1_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_s2_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_s3_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_s4_20260703" -Compact -Watch
```

### Phase A Summary Command

After all five shard terminals finish, run:

```powershell
Get-ChildItem -LiteralPath "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -Filter "quotes_parity_struct_s*_20260703.manifest.json" | Sort-Object Name | ForEach-Object { $j = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json; [PSCustomObject]@{run_id=$j.run_id; status=$j.status; shard=("{0}/{1}" -f $j.shard_index,$j.shard_count); audit_tickers=$j.audit_ticker_count; parity_ok=$j.parity_ok_count; mismatches=$j.mismatch_count; missing_top=$j.missing_top_level_count; extra_top=$j.extra_top_level_count; elapsed_sec=$j.elapsed_seconds} } | Format-Table -AutoSize
```

Phase A passes only if all five rows report:

```text
status = completed_pass
mismatches = 0
missing_top = 0
extra_top = 0
```

If any shard reports `completed_fail`, do not promote `quotes_`. Inspect:

```text
E:/TSIS/data/data_ops_manifests/quotes_parity_audit/<run_id>.mismatches.csv
E:/TSIS/data/data_ops_manifests/quotes_parity_audit/<run_id>.mismatches/
```

### 2026-07-03 Power-Loss Interruption Note

During the first Phase A structural parity audit, five shards were launched
with run ids:

```text
quotes_parity_struct_s0_20260703
quotes_parity_struct_s1_20260703
quotes_parity_struct_s2_20260703
quotes_parity_struct_s3_20260703
quotes_parity_struct_s4_20260703
```

The machine lost power before any shard wrote a final manifest. The heartbeat
files remained at `status = running`, but they are stale evidence only. They
must not be read as live work and they do not satisfy the promotion gate.

Observed state before interruption:

| Shard | Heartbeat progress | Result JSON files | Worker/error JSON files | First missing ticker in original shard |
| --- | ---: | ---: | ---: | --- |
| `s0` | `249/1041` | `249` | `0` | `AMNB` |
| `s1` | `194/1041` | `195` | `0` | `CUTR` |
| `s2` | `188/1042` | `188` | `101` | `HWBK` |
| `s3` | `175/1041` | `175` | `1` | `NPK` |
| `s4` | `219/1042` | `219` | `2` | `SPEX` |

The top-level ticker roster already matched at run start:

```text
source_ticker_dirs = 5207
target_ticker_dirs = 5207
missing_top_level_count = 0
extra_top_level_count = 0
```

The recorded mismatch JSON files from the interrupted run are not accepted as
material source/target mismatches. They were worker errors such as:

```text
PermissionError(13, 'Acceso denegado')
MemoryError()
OSError(22, 'Recursos insuficientes en el sistema para completar el servicio solicitado')
```

Spot checks after restart showed representative affected tickers such as
`GTN.A`, `GTPA`, `GTPB`, `NPTN`, `SPEC` and `SPFI` were accessible in both
`D:/quotes` and `E:/TSIS/data/quotes_`. Therefore this incident should be
treated as an interrupted audit run, not as proof of clone parity failure.

Do not delete the partial evidence directories. Keep them for incident
traceability, but do not use them as final parity evidence.

Important resume rule:

```text
Do not use --start-at-ticker with --shard-count 5 to resume these exact shards.
```

In the current auditor, `--start-at-ticker` is applied before shard splitting.
Using it with `--shard-count 5` would shift the shard boundaries and would not
continue the same original shard. Until the auditor has an explicit
per-shard resume or ticker-list mode, the clean institutional path is to rerun
Phase A with new run ids and preserve the interrupted run as partial evidence.


#### 2026-07-03 Rerun Monitor Note: s0 Heartbeat Lag

During the post-power-loss rerun, `quotes_parity_struct_rerun_s0_20260703` showed a stale heartbeat counter (`current_index=21/1041`, heartbeat last write `2026-07-03 15:27:07`) while its worker output directory continued to advance normally.

Operational interpretation:

- Do not treat `s0` as stuck solely because the heartbeat `progress` column remains at `21/1041`.
- The authoritative progress signal for this anomaly is the number and last-write timestamp of files under:
  `E:\TSIS\data\data_ops_manifests\quotes_parity_audit\quotes_parity_struct_rerun_s0_20260703.ticker_results\`
- At `2026-07-03 20:52`, `s0` had `409` ticker result JSON files, with the latest result file written at `20:52:06`; PID `14380` was alive.
- Continue monitoring `result_files` and `last_result_write`. Only consider stopping/relaunching `s0` if those two fields stop advancing for a sustained period while the process remains alive.

Preferred monitor for this rerun:

```powershell
while ($true) {
  $root = "E:\TSIS\data\data_ops_manifests\quotes_parity_audit"
  Get-ChildItem -LiteralPath $root -Filter "quotes_parity_struct_rerun_s*.heartbeat.json" | Sort-Object Name | ForEach-Object {
    $j = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
    $runId = $j.run_id
    $tr = Join-Path $root "$runId.ticker_results"
    $files = @()
    if (Test-Path -LiteralPath $tr) { $files = Get-ChildItem -LiteralPath $tr -Filter "*.json" -File }
    $last = $files | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    [PSCustomObject]@{
      run_id = $runId
      heartbeat_progress = ("{0}/{1}" -f $j.current_index,$j.total_count)
      ticker_result_files = ($files | Measure-Object).Count
      last_ticker_file = $last.Name
      last_ticker_write = $last.LastWriteTime
      heartbeat_write = $_.LastWriteTime
      pid = $j.active_pid
      alive = [bool](Get-Process -Id $j.active_pid -ErrorAction SilentlyContinue)
    }
  } | Format-Table -AutoSize
  Start-Sleep 30
  Clear-Host
}
```

#### 2026-07-04 s0 Recovery Closure

On `2026-07-04`, `quotes_parity_struct_rerun_s0_20260703` had completed all ticker-level evidence but did not write its final manifest. The original active PID (`14380`) was no longer alive, while the result directory contained `1041/1041` ticker JSON files.

Recovery action performed:

- Validated `1041/1041` ticker result JSON files under `quotes_parity_struct_rerun_s0_20260703.ticker_results`.
- Confirmed `parity_ok=true` for all `1041` files.
- Confirmed `mismatch_count=0`, `missing_result_count=0`, and `failed_worker_count=0`.
- Wrote recovered final artifacts:
  - `E:\TSIS\data\data_ops_manifests\quotes_parity_audit\quotes_parity_struct_rerun_s0_20260703.manifest.json`
  - `E:\TSIS\data\data_ops_manifests\quotes_parity_audit\quotes_parity_struct_rerun_s0_20260703.summary.csv`
  - `E:\TSIS\data\data_ops_manifests\quotes_parity_audit\quotes_parity_struct_rerun_s0_20260703.mismatches.csv`
- Updated `quotes_parity_struct_rerun_s0_20260703.heartbeat.json` to `completed_pass` / `final_manifest_written`.
- Preserved the stale heartbeat as:
  `E:\TSIS\data\data_ops_manifests\quotes_parity_audit\quotes_parity_struct_rerun_s0_20260703.heartbeat.pre_recovery_20260704T052034Z.json`

The recovered manifest explicitly includes `recovered_manifest=true`; this distinguishes the closure from shards `s1`-`s4`, whose manifests were written by the original auditor process.
### Phase A Rerun After 2026-07-03 Power Loss

Use new run ids so the interrupted evidence remains intact. To reduce pressure
on Windows process and IO resources, start with `--workers 2`. If the machine
shows memory or permission/resource errors again, reduce to `--workers 1`.

Operational recommendation:

```text
Run at most two shards at the same time until the machine proves stable.
```

Copy/paste commands for the clean Phase A rerun:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode mismatches-only --shard-count 5 --shard-index 0 --run-id "quotes_parity_struct_rerun_s0_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode mismatches-only --shard-count 5 --shard-index 1 --run-id "quotes_parity_struct_rerun_s1_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode mismatches-only --shard-count 5 --shard-index 2 --run-id "quotes_parity_struct_rerun_s2_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode mismatches-only --shard-count 5 --shard-index 3 --run-id "quotes_parity_struct_rerun_s3_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode mismatches-only --shard-count 5 --shard-index 4 --run-id "quotes_parity_struct_rerun_s4_20260703" --heartbeat-seconds 30
```

Monitor commands for the rerun:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_rerun_s0_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_rerun_s1_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_rerun_s2_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_rerun_s3_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_struct_rerun_s4_20260703" -Compact -Watch
```

Rerun summary command:

```powershell
Get-ChildItem -LiteralPath "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -Filter "quotes_parity_struct_rerun_s*_20260703.manifest.json" | Sort-Object Name | ForEach-Object { $j = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json; [PSCustomObject]@{run_id=$j.run_id; status=$j.status; shard=("{0}/{1}" -f $j.shard_index,$j.shard_count); audit_tickers=$j.audit_ticker_count; parity_ok=$j.parity_ok_count; mismatches=$j.mismatch_count; missing_top=$j.missing_top_level_count; extra_top=$j.extra_top_level_count; elapsed_sec=$j.elapsed_seconds} } | Format-Table -AutoSize
```

The rerun passes only if all five rerun manifests report:

```text
status = completed_pass
mismatches = 0
missing_top = 0
extra_top = 0
```

Do not start Phase B SHA256 until this clean Phase A rerun passes.
### 2026-07-04 Phase B Start - Full SHA256 Parity

Phase A structural parity rerun passed for shards `0..4` before Phase B was started.

Phase B was started conservatively because full SHA256 parity is substantially more IO-intensive than structural path/size parity.

Started shard:

```text
run_id: quotes_parity_sha256_s0_20260704
shard: 0/5
hash_mode: full
workers: 1
pid: 24900
source_root: D:\quotes
target_root: E:\TSIS\data\quotes_
log_root: E:\TSIS\data\data_ops_manifests\quotes_parity_audit
started_local: 2026-07-04 07:37 Europe/Madrid
```

Launch command used:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 1 --hash-mode full --shard-count 5 --shard-index 0 --run-id "quotes_parity_sha256_s0_20260704" --heartbeat-seconds 30
```

Operational hold:

```text
Do not launch shards s1..s4 until s0 shows stable progress under full SHA256 load.
```

Monitor command for the active Phase B shard:

```powershell
while ($true) { $root="E:\TSIS\data\data_ops_manifests\quotes_parity_audit"; Get-ChildItem -LiteralPath $root -Filter "quotes_parity_sha256_s*_20260704.heartbeat.json" | Sort-Object Name | ForEach-Object { $j=Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json; $runId=$j.run_id; $tr=Join-Path $root "$runId.ticker_results"; $files=@(); if (Test-Path -LiteralPath $tr) { $files=Get-ChildItem -LiteralPath $tr -Filter "*.json" -File }; $last=$files | Sort-Object LastWriteTime -Descending | Select-Object -First 1; [PSCustomObject]@{run_id=$runId; status=$j.status; stage=$j.stage; hb_progress=("{0}/{1}" -f $j.current_index,$j.total_count); result_files=($files|Measure-Object).Count; last_result=$last.Name; last_result_write=$last.LastWriteTime; mismatches=$j.mismatch_count; failed=$j.failed_worker_count; pid=$j.active_pid; alive=[bool](Get-Process -Id $j.active_pid -ErrorAction SilentlyContinue); free_gb=$j.output_free_gb; hb_write=$_.LastWriteTime} } | Format-Table -AutoSize; Start-Sleep 30; Clear-Host }
```
### 2026-07-04 Phase B s1 Start

At operator request, the second Phase B shard was started while `s0` remained active.

```text
run_id: quotes_parity_sha256_s1_20260704
shard: 1/5
hash_mode: full
workers: 1
pid: 28524
source_root: D:\quotes
target_root: E:\TSIS\data\quotes_
log_root: E:\TSIS\data\data_ops_manifests\quotes_parity_audit
started_local: 2026-07-04 07:46 Europe/Madrid
```

Launch command used:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 1 --hash-mode full --shard-count 5 --shard-index 1 --run-id "quotes_parity_sha256_s1_20260704" --heartbeat-seconds 30
```

Active Phase B shards after this action:

```text
quotes_parity_sha256_s0_20260704  shard 0/5  workers=1
quotes_parity_sha256_s1_20260704  shard 1/5  workers=1
```
### 2026-07-04 Phase B s2-s4 Start

At operator request, the remaining Phase B full SHA256 shards were started while `s0` and `s1` remained active.

```text
run_id: quotes_parity_sha256_s2_20260704
shard: 2/5
hash_mode: full
workers: 1
pid: 14052
```

```text
run_id: quotes_parity_sha256_s3_20260704
shard: 3/5
hash_mode: full
workers: 1
pid: 4976
```

```text
run_id: quotes_parity_sha256_s4_20260704
shard: 4/5
hash_mode: full
workers: 1
pid: 15868
```

Shared roots:

```text
source_root: D:\quotes
target_root: E:\TSIS\data\quotes_
log_root: E:\TSIS\data\data_ops_manifests\quotes_parity_audit
started_local: 2026-07-04 08:32 Europe/Madrid
```

Active Phase B shards after this action:

```text
quotes_parity_sha256_s0_20260704  shard 0/5  workers=1
quotes_parity_sha256_s1_20260704  shard 1/5  workers=1
quotes_parity_sha256_s2_20260704  shard 2/5  workers=1
quotes_parity_sha256_s3_20260704  shard 3/5  workers=1
quotes_parity_sha256_s4_20260704  shard 4/5  workers=1
```

Operational note: all five Phase B shards are now active. This is the maximum intended Phase B parallelism for the current run because full SHA256 parity is IO-heavy.
### 2026-07-04 Phase B Workers Escalation to 2

At operator request, Phase B full SHA256 was accelerated from `workers=1` to `workers=2` per shard.

Implementation note:

- The auditor was extended with `--resume-existing-results`.
- The option reuses valid per-ticker JSON files already present under the same `run_id.ticker_results` directory.
- For `hash_mode=full`, reused results must have `hash_checked=true` and matching `hash_mode=full`.
- Invalid or mismatched existing JSON files are not reused.

Reason:

```text
Workers cannot be increased inside already-running Python processes. Existing runs must be stopped and relaunched.
```

Action performed:

- Preserved pre-workers2 heartbeat/pre-manifest/pid evidence with suffix `pre_workers2_20260704T140623Z`.
- Stopped the old `workers=1` process generation.
- Relaunched the same run IDs with `--workers 2 --resume-existing-results`.
- Confirmed all five relaunched wrappers are alive and own the current heartbeats.

Resume counts at relaunch:

```text
quotes_parity_sha256_s0_20260704  reused=141  remaining=900  invalid=0  pid=28624
quotes_parity_sha256_s1_20260704  reused=106  remaining=935  invalid=0  pid=12384
quotes_parity_sha256_s2_20260704  reused=86   remaining=956  invalid=0  pid=28676
quotes_parity_sha256_s3_20260704  reused=81   remaining=960  invalid=0  pid=17528
quotes_parity_sha256_s4_20260704  reused=99   remaining=943  invalid=0  pid=1552
```

Active command shape after escalation:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index <0..4> --run-id "quotes_parity_sha256_s<0..4>_20260704" --heartbeat-seconds 30 --resume-existing-results
```

Do not launch a second generation for these same run IDs while the `workers=2` generation is active.
### Phase B Commands - Full SHA256 Parity

Run Phase B only after Phase A passes or when the operator explicitly wants the
strongest byte-level proof despite the IO cost. Use lower worker count than
Phase A.

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index 0 --run-id "quotes_parity_sha256_s0_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index 1 --run-id "quotes_parity_sha256_s1_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index 2 --run-id "quotes_parity_sha256_s2_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index 3 --run-id "quotes_parity_sha256_s3_20260703" --heartbeat-seconds 30
```

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\audit_quotes_clone_parity.py" --source-root "D:\quotes" --target-root "E:\TSIS\data\quotes_" --log-root "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" --workers 2 --hash-mode full --shard-count 5 --shard-index 4 --run-id "quotes_parity_sha256_s4_20260703" --heartbeat-seconds 30
```

### Phase B Monitor Commands

Use the same monitor pattern with the SHA256 run IDs:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_sha256_s0_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_sha256_s1_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_sha256_s2_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_sha256_s3_20260703" -Compact -Watch
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_long_running_operation.ps1" -RunRoot "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -RunId "quotes_parity_sha256_s4_20260703" -Compact -Watch
```

### Phase B Summary Command

```powershell
Get-ChildItem -LiteralPath "E:\TSIS\data\data_ops_manifests\quotes_parity_audit" -Filter "quotes_parity_sha256_s*_20260703.manifest.json" | Sort-Object Name | ForEach-Object { $j = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json; [PSCustomObject]@{run_id=$j.run_id; status=$j.status; shard=("{0}/{1}" -f $j.shard_index,$j.shard_count); audit_tickers=$j.audit_ticker_count; parity_ok=$j.parity_ok_count; mismatches=$j.mismatch_count; missing_top=$j.missing_top_level_count; extra_top=$j.extra_top_level_count; elapsed_sec=$j.elapsed_seconds} } | Format-Table -AutoSize
```

Phase B passes only if all five rows report:

```text
status = completed_pass
mismatches = 0
missing_top = 0
extra_top = 0
```

### Promotion Gate

`E:/TSIS/data/quotes_` remains blocked for official downstream consumption
until the post-copy audit evidence is reviewed. Minimum promotion evidence:

```text
Phase A structural parity passed for shards 0..4.
No mismatches across all shards.
No missing or extra top-level ticker directories.
No missing worker results.
All shard manifests present.
All shard heartbeats reached final_manifest_written.
```

Stronger promotion evidence:

```text
Phase B full SHA256 parity also passed for shards 0..4.
```

If Phase A passes and Phase B is deferred, any downstream use must state:

```text
quotes_ parity level = structural path/size parity, SHA256 full parity deferred
```

If Phase B passes, downstream use may state:

```text
quotes_ parity level = full SHA256 parity against D:/quotes
```

## Current Institutional Status

```text
artifact: E:/TSIS/data/quotes_
status: target official E-root pending post-copy parity audit and promotion
source_of_truth: blocked until audit/promotion
downstream official consumption: blocked until post-copy audit and promotion
legacy_incomplete_e_quotes_root: E:/TSIS/data/quotes
```
