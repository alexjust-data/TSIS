# TSIS Long-Running Operations Contract

## 1. Role

This document is the transversal contract for every long-running TSIS command.

It applies to humans, agents, scripts, schedulers and future autonomous
systems in every TSIS module and subfolder.

The goal is simple:

```text
No long-running operation may be a black box.
```

If an operation can run for minutes or hours, scan a large tree, copy many
files, materialize datasets, repair data, build graphs, train models, audit
families or write governed outputs, it must expose durable progress evidence
from the beginning of the run.

---

## 2. Scope

This contract applies when any command meets at least one condition:

- expected runtime above 5 minutes;
- expected IO above 1 GB;
- expected file count above 10,000;
- recursive scan over market-data roots;
- copy, clone, repair, normalization or materialization job;
- model training or large evaluation;
- graph build or graph refresh;
- any operation a human may reasonably leave unattended.

Local rules may be stricter. They may not weaken this contract.

---

## 3. Mandatory Artifacts

Every governed long-running operation MUST create these artifacts before the
expensive work starts.

### 3.1. Pre-manifest

The pre-manifest must be written at startup, before enumeration, copy,
materialization, audit, training or graph extraction begins.

Minimum fields:

- `run_id`
- `status = planned|starting|running`
- `created_at_utc`
- `script_path`
- `script_version_or_hash` when cheap
- `command_line`
- `cwd`
- `host`
- `user`
- `parent_pid`
- `wrapper_pid`
- `git_branch` when available
- `git_commit` when available
- `git_dirty_state` when available
- `mode`
- `dry_run` or `run`
- input roots
- output roots
- log roots
- manifest paths
- expected scope
- resume policy
- overwrite policy
- success criteria
- monitor command

The pre-manifest is not replaced by the final manifest. It exists so that a
human or a future agent can understand a run even if the machine loses power.

JSON telemetry files that are rewritten during a run, especially heartbeat and
PID manifests, must use a Windows-safe replacement strategy. A script must not
depend on `Move-Item -Force` as the only replacement mechanism for an existing
JSON file, because it can fail with "cannot create a file that already exists"
and kill the wrapper while the data operation itself is otherwise healthy.

Acceptable patterns include:

- write to a unique temporary file and replace the target with
  `System.IO.File.Replace` plus a temporary backup file;
- use a documented fallback that preserves the run or degrades telemetry
  gracefully;
- never let a heartbeat rewrite race silently corrupt or stop the governed
  operation.

### 3.2. PID Manifest

The PID manifest must record:

- wrapper PID;
- child process PIDs when they exist;
- process names;
- command line or safe command summary;
- start timestamps;
- current stage;
- whether each PID is expected to still be alive.

### 3.3. Heartbeat

Every operation must write:

- a latest heartbeat JSON file;
- an append-only heartbeat JSONL file.

Default cadence:

- every 60 seconds for active foreground operations;
- every 5 minutes maximum for very low-churn background operations;
- additionally at stage boundaries.

Minimum heartbeat fields:

- `run_id`
- `observed_at_utc`
- `status`
- `stage`
- `elapsed_seconds`
- active PID or child PID
- PID alive flag
- current item, ticker, chunk, subpath, window or shard when known
- current index and total count when known
- percentage when total is known
- source root or active input path when safe
- target root or active output path when safe
- log path
- log size
- log last write time
- process CPU when available
- process IO read/write/data rates when available
- disk free space for relevant output drive when available
- completed counts when cheap and reliable
- bytes/files copied or materialized when cheap and reliable
- last error or warning when present

Important:

Recursive file counts over million-file trees are not mandatory during the
main run if they would materially slow the operation. In that case the
heartbeat must say that physical counting is intentionally disabled and must
still expose process IO, stage, PID, log and output-root evidence.

### 3.4. Human Log

A human-readable log must exist for stdout/stderr, vendor tool output or
script messages.

If a command suppresses verbose tool output with flags such as `robocopy /NFL`,
`/NDL` or `/NP`, the heartbeat becomes mandatory compensation. Suppressed
console verbosity is allowed only when machine telemetry remains live.

### 3.5. Monitor

Every long-running command must print a monitor command immediately after the
pre-manifest is written.

The monitor must be a separate command that can be run in another terminal.
It must not depend on private conversation context.

Minimum monitor behavior:

- show latest heartbeat;
- show PID liveness;
- show wrapper PID liveness when available;
- show elapsed time;
- show stage/current item;
- show log size and last write time;
- show output drive free space when available;
- show final manifest/summary when present.

If the latest heartbeat says `status=running` but:

- the heartbeat is stale;
- the wrapper PID is not alive;
- no active child PID is alive;
- and no final manifest/summary exists;

then the monitor MUST NOT keep presenting the operation as simply running. It
must surface a derived state such as:

```text
status=stale_no_process raw_status=running
```

This protects human operators from confusing a stale heartbeat with live work.

### 3.5.1. Compact Progress Lines

Every monitor for a governed long-running operation MUST support a compact,
append-only line mode for humans.

This mode must print one new line per interval and must not clear the screen.
It exists because a human operator needs to see trend and velocity, not only a
single refreshed snapshot.

Required line shape:

```text
[timestamp] status=<status> stage=<stage> processes=<n> latest_age_sec=<n> elapsed_sec=<n> progress=<done>/<total> item=<current_item> cpu=<n> io_read_Bps=<n> io_write_Bps=<n> output_free_GB=<n>
```

When wrapper PID liveness is available, compact mode should expose it:

```text
wrapper_alive=<true|false>
```

When the operation exposes domain counters, the compact line must include them.

Examples:

```text
months=31210/31975 repairs=10766119
chunks=12/87 rows=5421000 files=312
files=182391/900000 bytes=9423112201
windows=450/1200 hard_fails=0
epochs=3/40 train_loss=0.421 val_loss=0.488
```

If a total is not known yet, the line must say so explicitly:

```text
progress=unknown reason=manifest_not_finished
```

For setup phases like manifest building, `0/0` without explanation is not
acceptable in human-facing compact mode. The line must explain the phase:

```text
stage=build_manifest progress=unknown reason=total_known_after_manifest
```

This compact line mode is required for all future TSIS long-running monitors,
not only for Module 01 data jobs.

### 3.6. Final Manifest

On completion, interruption or failure, the operation must write a final
manifest or final summary with:

- final status;
- start/end timestamps;
- duration;
- exit code;
- success rule;
- counts produced by the operation;
- output roots;
- important output files;
- hashes when required by the dataset contract;
- warnings;
- failure reason if any;
- resume instructions;
- promotion state.

---

## 4. Runtime Topology

Runtime telemetry belongs near the run output or in an explicit runtime/log
root. It must not be committed to Git unless a local contract explicitly
promotes a small manifest as institutional evidence.

Allowed runtime roots include:

- `runs/`
- `runtime/`
- `E:/TSIS/data/data_ops_manifests/`
- dataset-specific governed output roots outside Git.

Git keeps:

- scripts;
- contracts;
- small institutional manifests when explicitly allowed;
- changelogs;
- tests.

Git does not keep:

- raw data;
- heavy logs;
- large runtime snapshots;
- parquets;
- cloned datasets.

---

## 5. Stop, Resume and Duplicate-Run Policy

Before starting or restarting a long operation, the runner must check whether
an active run with the same target is already alive when that is technically
possible.

If an active PID exists, the default behavior is:

```text
do not start a duplicate writer against the same target
```

If a run is interrupted:

- the interruption must be visible in heartbeat or final summary when possible;
- the resume command must be documented;
- resume must preserve already written data unless the contract explicitly
  declares a destructive overwrite policy;
- destructive resume or purge requires explicit human approval.

---

## 6. Required Console Header

Every runner must print, at minimum:

```text
run_id
mode
input roots
output roots
pre-manifest path
heartbeat path
log path
PID manifest path
monitor command
success rule
resume policy
```

This header is not cosmetic. It is the first operational control surface for
humans.

---

## 7. Failure Rule

A long-running operation that does not produce pre-manifest and heartbeat
telemetry is not acceptable as a future TSIS runner.

If a legacy command lacks this telemetry, it may be allowed to finish if it is
already running, but the script must be upgraded before being recommended for
the next serious run.

---

## 8. Relationship to Other Contracts

This contract is governed by:

- `PROJECT_RULES.md`
- `PROJECT_OPERATING_SYSTEM.md`
- `VERSIONING_STANDARDS.md`
- `AGENTS.md`

It applies to:

- `01_TSIS_backtest_SmallCaps`
- `02_TSIS_webSocket_SmallCaps`
- `03_TSIS_Offline_RL`
- `00_CTO`
- any future TSIS module.

The rule is institutional:

```text
If a human cannot know where a serious command is, the command is not TSIS-grade.
```
