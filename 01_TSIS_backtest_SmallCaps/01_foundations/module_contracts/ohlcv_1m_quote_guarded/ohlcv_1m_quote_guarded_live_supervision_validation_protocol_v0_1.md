# OHLCV 1m Quote-Guarded Live Supervision And Validation Protocol v0.1

## 1. Document Role

This document records the live operational protocol created during the first
full-universe `ohlcv_1m_quote_guarded_v0_1` repair run.

It belongs in:

```text
01_foundations/module_contracts/ohlcv_1m_quote_guarded/
```

Reason:

- the topic is specific to the quote-guarded `ohlcv_1m` workstream;
- it changes how long-running quote-guarded repair jobs must be operated;
- it does not define a new dataset contract yet;
- it is not an inspection dossier result;
- it is not a promoted data-quality verdict;
- it is not raw data.

This is the canonical place for the operational memory until the complete
foundation chain is promoted into schema, dataset contract, consumption policy,
validators and data-quality report.

## 2. Operational Context

The workstream exists because raw one-minute bars under:

```text
E:/TSIS/data/ohlcv_1m
```

can contain minute candles whose OHLC values contradict the quote evidence
available under:

```text
D:/quotes
```

The initial motivating charts were:

```text
TWG   2026-01-20 premarket
TIRX  2026-01-28 premarket
RVYL  2026-01-23 premarket
SHPH  2026-01-20 premarket
```

The local `trades` roots were not usable for these premarket executions at the
time of the decision. The project therefore chose a provisional quote-envelope
repair manifest, not a trade-derived rebuild.

The raw `ohlcv_1m` files remain immutable.

## 3. Long-Run Problem Observed

The first full-universe attempt was launched with the earlier runner shape:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\run_ohlcv_1m_quote_guarded_repair.ps1" -Workers 12 -Overwrite
```

Observed issue:

- the terminal printed the run header;
- it did not expose granular per-ticker progress;
- no durable shards or summaries were being written early enough to understand
  whether hours of work had produced persistent output;
- the expensive first phase was dominated by walking a very large file tree;
- if the process was stopped, there was no clear durable unit-level evidence of
  what had completed.

Institutional conclusion:

```text
Full-universe quote-guarded repair must be ticker-worker streaming,
telemetry-first, resumable by durable month summaries, and supervised by a
separate watchdog.
```

## 4. v0_2 Runner Design Decision

The v0_2 design assigns whole tickers to workers.

Primary executable surfaces:

```text
scripts/inspection/minute/build_ohlcv_1m_quote_guarded_repairs_v0_2.py
scripts/run_ohlcv_1m_quote_guarded_repair_v0_2.ps1
scripts/monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

Durable run structure:

```text
<RunRoot>/
  run_config.json
  runner_config.json
  progress_snapshot.json
  quote_guarded_repair_v0_2.log
  ticker_status/
  ticker_events/
  ticker_summaries/
  month_summaries/
  repair_shards/
```

Resumability rule:

```text
Relaunch the same RunRoot without -Overwrite.
```

Each ticker-month that already has a readable `month_summaries/*.json` is
skipped. This protects completed work and makes restarts cheap relative to a
full restart.

Do not relaunch with `-Overwrite` unless the intent is to discard and rebuild
the existing run artifacts.

## 5. Active Run Recorded Here

The active full-universe run root discussed in this protocol is:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838
```

Run configuration observed:

```text
script_version = v0_2_ticker_worker
minute_root = E:\TSIS\data\ohlcv_1m
quotes_root = D:\quotes
output_root = E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded
workers = 12
min_year = null
max_year = null
tickers = null
max_tickers = null
max_months_per_ticker = null
promote_manifest = true
overwrite = false
tickers_planned = 12168
```

Important status snapshot during live operation:

```text
observed_at = 2026-06-27T14:55 local Europe/Madrid
supervisor one-shot matching processes = 1
latest output age ~= 0.04 minutes
progress months = 18945/19640 inside started tickers
repair rows ~= 6110918
action = no duplicate runner started
```

This snapshot only proves the run was alive at that observation time. It is not
a final completion claim.

## 6. Why A Separate Supervisor Is Required

The repair process is expected to run for days.

Manual monitoring is not sufficient because:

- the terminal can be closed;
- PowerShell can remain open while child Python behavior changes;
- Windows multiprocessing workers can appear with generic command lines;
- a human cannot reliably watch stale output overnight;
- the project needs durable restart evidence, not verbal memory.

The supervisor is intentionally separate from the runner. It does not process
market data itself. It observes the run root and decides whether a restart is
needed.

## 7. Supervisor Script

Script:

```text
scripts/supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

Role:

- watches one `RunRoot`;
- checks whether `repair_summary.json` exists;
- checks whether a matching v0_2 runner process is visible;
- checks latest output write time across telemetry and artifact folders;
- appends events to `<RunRoot>/supervisor_events.jsonl`;
- restarts the v0_2 runner only when:
  - no final summary exists;
  - no matching runner process is visible;
  - latest output is stale beyond threshold.

It must not:

- modify raw `E:/TSIS/data/ohlcv_1m`;
- delete run artifacts;
- use `-Overwrite`;
- start a duplicate while a matching runner is visible;
- declare data-quality success.

Recommended live command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Workers 12 -PollSeconds 60 -StaleMinutes 20 -OrphanGraceMinutes 3
```

One-shot diagnostic command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Workers 12 -OrphanGraceMinutes 3 -Once
```

The one-shot command is for testing only. It should print process and freshness
state, then exit.

## 8. Supervisor Detection Detail

The first supervisor test looked only for:

```text
build_ohlcv_1m_quote_guarded_repairs_v0_2.py
```

That was too narrow on Windows because the live process can be visible through
the PowerShell wrapper:

```text
run_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

and child multiprocessing workers can appear with generic Python spawn command
lines.

The supervisor was therefore adjusted to count a matching process when the
command line contains the same `RunRoot` and either:

```text
build_ohlcv_1m_quote_guarded_repairs_v0_2.py
run_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

This avoids false duplicate restarts.

### 2026-06-27 stale wrapper incident

At approximately `18:18` Europe/Madrid, the supervisor terminal reported:

```text
processes = 1
latest_age_min ~= 168
months = 18945/19640
repairs = 6110918
```

This did not mean the job was merely slow.

It meant:

- no durable output had been written since approximately `15:31`;
- the visible matching process was only the PowerShell runner wrapper;
- the wrapper had no Python child process;
- therefore no 12-worker repair pool was actually running.

Confirmed stale process:

```text
PID = 10444
process = powershell.exe
role = run_ohlcv_1m_quote_guarded_repair_v0_2.ps1 wrapper
children = conhost.exe only
python repair child = absent
```

The supervisor was corrected so a stale wrapper with no Python descendants is
classified as an orphan runner wrapper. The corrected behavior is:

```text
if output is stale and runner wrapper has no Python descendants:
    stop only that orphan wrapper
    append stale_orphan_wrapper_stopped to supervisor_events.jsonl
    relaunch v0_2 runner on the same RunRoot without -Overwrite
```

Recorded recovery event:

```text
stale_orphan_wrapper_stopped:
  pid = 10444
restart_started:
  pid = 45836
  python child = 51120
  run_root = quote_guarded_v0_2_20260627_091838
  overwrite = false
```

Post-restart evidence:

```text
18:31 local Europe/Madrid
new month summaries written:
  ADX_2023_04.json
  AEG_2012_10.json
  AEHL_2025_11.json
  AEGR_2016_07.json
new repair shards written:
  AEGN_2012_01_repair_manifest.parquet
  ADV_2022_01_repair_manifest.parquet
  AE_2007_03_repair_manifest.parquet
progress_snapshot:
  ticker_status_files = 233
  DONE = 221
  RUNNING = 12
  months_done = 21584
  months_planned_in_started_tickers = 22800
  repair_rows = 7325758
```

Important operational note:

```text
PowerShell scripts already running in a terminal do not reload changed script
files. After this correction, any already-open supervisor terminal must be
stopped and relaunched so it uses the orphan-wrapper logic.
```

### 2026-06-29 orphan wrapper grace correction

During the same live full-universe run, a later orphan-wrapper state was
observed again:

```text
monitor:
  DONE = 4255
  RUNNING = 0
  months_done/planned_in_started_tickers = 457939/457939

supervisor:
  processes = 1
  orphan_wrappers = 1
  latest_age_min ~= 13
  months = 456641/457130
  repairs = 126013538
```

This state is not equivalent to ordinary slow processing. When the only
matching runner process is a PowerShell wrapper and it has no Python descendant,
there is no active repair worker pool. Waiting for the general stale threshold
therefore wastes time without protecting useful work.

The supervisor was corrected to use two independent thresholds:

```text
StaleMinutes:
  default = 20
  purpose = conservative restart when process state is ambiguous

OrphanGraceMinutes:
  default = 3
  purpose = fast restart when wrapper is clearly orphaned
```

Corrected behavior:

```text
if orphan wrapper exists and latest output age >= OrphanGraceMinutes:
    stop only the orphan wrapper
    append orphan_wrapper_grace_exceeded_stopped to supervisor_events.jsonl
    relaunch v0_2 runner on the same RunRoot without -Overwrite
else if no matching process exists and latest output age >= StaleMinutes:
    relaunch v0_2 runner on the same RunRoot without -Overwrite
```

Operational note:

```text
Any supervisor terminal already open before this correction is still running
the old in-memory script. Stop only that supervisor terminal and relaunch it.
Do not stop the runner, monitor, or validator terminals for this correction.
The relaunched header must include:
  orphan grace: 3m
```

## 9. Why A Separate Validator Is Required

The monitor and supervisor answer:

```text
Is the run alive?
```

They do not answer:

```text
Are the artifacts being written correctly?
```

Validation must be independent of the runner. It should read persisted outputs
and test structural and semantic invariants while the run continues.

## 10. Validator Script

Script:

```text
scripts/validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1
```

Report output:

```text
<RunRoot>/validation/latest_validation_report.json
<RunRoot>/validation/validation_report_YYYYMMDD_HHMMSS.json
```

Recommended live command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Watch -IntervalSeconds 300 -MaxShardsPerPass 500 -SampleRowsPerShard 200 -MinShardAgeSeconds 180
```

Bounded diagnostic command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -MaxShardsPerPass 25 -SampleRowsPerShard 50 -MinShardAgeSeconds 180
```

Full final validation after the repair run completes:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -MaxShardsPerPass 0 -SampleRowsPerShard 0 -MinShardAgeSeconds 0
```

The final command is intentionally heavier. It should be run after no writer is
active.

## 11. What The Validator Checks

The validator checks persisted artifacts, not raw market truth.

Current checks:

- all readable `month_summaries/*.json`;
- all readable `ticker_status/*.json`;
- stable `repair_shards/*.parquet`;
- required manifest columns exist;
- parquet files are readable;
- stable shard row total matches stable month-summary repair row total;
- month summaries do not reference missing stable shards;
- shard `run_root` matches the requested `RunRoot`;
- `ticker` and `source_ohlcv_path` are not blank;
- `quote_count >= 3`;
- `quote_bid_floor <= quote_ask_cap`;
- repaired OHLC fields are non-null on repaired rows;
- repaired high is coherent with repaired open/low/close;
- repaired low is coherent with repaired open/high/close;
- repaired OHLC values are inside the quote envelope;
- `repair_state` belongs to the expected vocabulary:
  - `quote_repairable_ohlc_vw_invalid`
  - `quote_repairable_ohlc`
  - `vw_invalid_only`
- `vw_quote_guarded_status` belongs to the expected vocabulary:
  - `invalid_not_repaired_from_quotes`
  - `raw_preserved`

During live operation it intentionally ignores shards newer than
`MinShardAgeSeconds` to avoid false failures on a file being written.

## 12. What The Validator Does Not Prove

The validator does not prove:

- quotes are NBBO;
- quotes are complete for every venue;
- raw trade executions are known;
- VWAP is repaired;
- the future Polygon trades rebuild is unnecessary;
- charts or event engines are already consuming the view correctly;
- the full-universe run is complete.

It proves only that the persisted quote-guarded repair artifacts are internally
consistent under the current contract.

## 13. First Validator Evidence

Bounded validation pass recorded during the live run:

```text
status = PASS
errors = []
month_summary_files = 19876
stable_month_summary_files = 19784
repair_shards = 6734
stable_repair_shards = 6583
validated_shards = 25
month_summary_repair_rows = 6615018
shard_row_total = 6615018
report = <RunRoot>/validation/latest_validation_report.json
```

Interpretation:

- no structural or invariant failure was found in the bounded pass;
- the stable shard row total matched stable month-summary repair rows;
- the result is not a final full validation because only 25 stable shards were
  deeply sampled in that diagnostic command.

### 2026-06-28 live validator snapshot race

At approximately `00:06` Europe/Madrid, the live validator emitted:

```text
status = FAIL
errors = ["repair_row_total_mismatch"]
month_summary_repair_rows = 36172835
shard_row_total = 37183284
orphan_shards_count = 1302
sample_orphans included ATNI_2017_02_repair_manifest.parquet
```

Follow-up inspection showed that sampled `ATNI` shards did have matching
month summaries and internally consistent row counts. Example:

```text
ATNI_2017_02 summary repair_rows = 514
ATNI_2017_02 shard rows = 514
ATNI ticker status = DONE
ATNI months_done = 239/239
```

Root cause:

```text
The live validator was taking an inconsistent snapshot while the runner was
writing thousands of new files. It listed/read month summaries first, then
spent time counting shard metadata. By the time it compared totals, some shards
created after the summary listing had become old enough to pass the shard-age
filter, but their summaries were not present in the validator's earlier
in-memory month-summary snapshot.
```

This is a validator snapshot-race failure, not evidence that the quote-guarded
repair artifacts violated price-envelope invariants.

Correction:

```text
The validator now computes one snapshot_cutoff at pass start.
Month summaries and repair shards must both be older than that same cutoff.
In live sampled mode (-MaxShardsPerPass > 0), row-total comparison is scoped to
the sampled stable shards instead of all stable shards.
Final full validation after the writer stops should use -MaxShardsPerPass 0.
```

Operational consequence:

```text
Any already-running validator terminal must be stopped and relaunched after
this correction. Like the supervisor, the validator embeds a temporary Python
script at startup and does not reload edits while running.
```

## 14. Terminal Layout Recommended For Long Runs

Use separate terminals:

### Terminal 1 - Existing Runner

Leave the active runner alone.

Do not close it unless deliberately stopping the job.

### Terminal 2 - Human Monitor

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\monitor_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Watch -IntervalSeconds 30
```

### Terminal 3 - Supervisor

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Workers 12 -PollSeconds 60 -StaleMinutes 20 -OrphanGraceMinutes 3
```

### Terminal 4 - Validator

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1" -RunRoot "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838" -Watch -IntervalSeconds 300 -MaxShardsPerPass 500 -SampleRowsPerShard 200 -MinShardAgeSeconds 180
```

The monitor is for humans.

The supervisor is for automatic restart.

The validator is for artifact correctness.

They should not be collapsed into one terminal because they answer different
questions.

## 15. Restart Rule

If the run appears stalled, do not manually launch a second runner before
checking:

```text
1. repair_summary.json exists?
2. matching runner process exists?
3. latest output write time is stale?
4. supervisor_events.jsonl already attempted restart?
5. current runner was launched without -Overwrite?
```

Only a same-RunRoot, non-overwrite restart is allowed as the default recovery
path.

If `latest_age_min` exceeds the stale threshold while `processes=1`, inspect
whether that single process is only the wrapper. A wrapper without Python
descendants is not active work and should be treated as restartable by the
supervisor.

## 16. Documentation Rule

Every future operational change to this live run protocol must update:

```text
01_foundations/module_contracts/ohlcv_1m_quote_guarded/README.md
01_foundations/module_contracts/ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

If the change alters validation semantics, also update the future validators
document when it exists:

```text
01_foundations/validators/ohlcv_1m/ohlcv_1m_quote_guarded_validators.md
```

## 17. Final Rule

For full-universe quote-guarded repair:

```text
Do not rely on terminal silence.
Do not rely on one final parquet.
Do not mutate raw data.
Do not restart with -Overwrite.
Use monitor for human status.
Use supervisor for restart safety.
Use validator for persisted artifact correctness.
Run final full validation after completion.
```
