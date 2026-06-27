# Quotes Staging Clone Runbook v0.1

## Purpose

This runbook defines the safe operational clone from:

```text
D:/quotes
```

to:

```text
E:/TSIS/data/quotes_
```

The target is intentionally named `quotes_` and is a staging root. It must not
replace `E:/TSIS/data/quotes` silently.

## Authority Rule

The official TSIS market-data database root is:

```text
E:/TSIS/data
```

Therefore the official live quotes root remains:

```text
E:/TSIS/data/quotes
```

`D:/quotes` and `C:/TSIS_Data/data/quotes` are not official database roots for
new consumption. They may appear in historical manifests as provenance paths
because earlier inspection evidence was generated from those physical locations.

Those paths can be used only for forensic reconciliation, recovery staging or
lineage validation. They must not be introduced into downstream table contracts
as primary source-of-truth roots.

## Why This Exists

The visual quotes inspection manifests include audited cases whose `source_file`
points to `D:/quotes`. A spot check found cases that are present in `D:/quotes`
but not under `E:/TSIS/data/quotes`.

The project needs a clean staging clone before deciding whether any official
quotes root should be promoted, merged, indexed or consumed by downstream
tables such as `microstructure_features_table`.

This does not mean `D:/quotes` becomes authoritative. The clone exists to move
legacy physical evidence into an auditable staging location under the official
`E:/TSIS/data` storage topology.

## Non-Negotiable Safety Rules

- Do not run a destructive mirror.
- Do not use `/MIR`.
- Do not use `/PURGE`.
- Do not delete anything from `E:/TSIS/data/quotes`.
- Do not treat `quotes_` as official until a post-copy audit exists.
- Do not update contracts to point to `quotes_` as source of truth without a
  separate promotion decision.
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
It writes a robocopy log and a JSON manifest for each run.

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

## Real Copy

After the scoped smoke test is satisfactory, launch the full clone directly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run
```

## Resume Or Update

If the copy is interrupted or the target already has content:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_ops\clone_quotes_to_staging.ps1" `
  -Run `
  -AllowNonEmptyTarget
```

This resumes or updates the staging tree. It still does not delete target extras.

## Performance Controls

Default:

```text
ThreadCount = 32
Retries     = 3
WaitSeconds = 5
```

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

Only after that audit can `quotes_` be considered for promotion, rename, merge,
or official downstream consumption.

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
status: staging target only
source_of_truth: no
downstream official consumption: blocked until post-copy audit and promotion
```
