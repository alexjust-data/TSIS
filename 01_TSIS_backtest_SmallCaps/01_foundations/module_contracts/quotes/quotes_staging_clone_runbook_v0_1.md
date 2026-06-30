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

## Current Institutional Status

```text
artifact: E:/TSIS/data/quotes_
status: target official E-root pending post-copy parity audit and promotion
source_of_truth: blocked until audit/promotion
downstream official consumption: blocked until post-copy audit and promotion
legacy_incomplete_e_quotes_root: E:/TSIS/data/quotes
```
