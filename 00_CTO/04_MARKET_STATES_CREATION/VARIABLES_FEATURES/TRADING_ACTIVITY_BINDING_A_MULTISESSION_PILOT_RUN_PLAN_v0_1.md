# TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_RUN_PLAN_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_multisession_pilot_run_plan` |
| `document_version` | `v0_1` |
| `document_role` | `GOVERNED_LONG_RUN_PLAN` |
| `document_status` | `READY_FOR_RUNNER_IMPLEMENTATION` |
| `execution_status` | `NOT_STARTED` |
| `execution_authorization` | `NOT_EXECUTABLE_UNTIL_RUNNER_AND_MONITOR_PASS_SMOKE` |
| `information_object_id` | `trading_activity` |
| `representation_model_candidate_id` | `absolute_and_pit_relative_multiscale_marked_activity_process` |
| `binding_id` | `trading_activity_binding_a_minimal_multiscale_rth_v0_2` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `pilot_scope_id` | `aact_rth_20240906_20250314_eval_20250310_20250314_v0_1` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `created_at` | `2026-08-07` |
| `owner` | `TBD` |

---

## 1. Purpose

This plan governs the first physical multisession materialization of Trading
Activity Binding A on dense historical RTH data.

It must demonstrate that TSIS can construct, persist and rebuild:

```text
CURRENT_STATE
MULTISCALE_CONTRAST
PIT_BASELINE_AND_SURPRISE
```

at the frozen `symbol-second` grain without future information, silent source
filtering, hidden missingness or ungoverned long-run execution.

This run is a deterministic physical pilot. It is not detector calibration,
OOS validation, canonical feature promotion or table mapping.

---

## 2. Governing authorities

The runner and readout must obey, in precedence order where applicable:

```text
C:/TSIS_Data/LONG_RUNNING_OPERATIONS_CONTRACT.md

TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md
TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md
TRADING_ACTIVITY_RTH_INTERIM_RESEARCH_SCOPE_v0_1.md
TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md
TRADING_ACTIVITY_RTH_COVERAGE_SIDECAR_SPECIFICATION_v0_2.md
TRADING_ACTIVITY_TRADE_ELIGIBILITY_POLICY_v0_2.md
TRADING_ACTIVITY_LATENCY_POLICY_REGISTRY_v0_1.md
TRADING_ACTIVITY_PIT_BASELINE_POLICY_v0_1.md
TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md
```

The existing 100-task coverage sidecar is evidence that the sidecar mechanism
works. It is not the dense source manifest for this pilot.

---

## 3. Frozen physical scope

### 3.1 Instrument identity

```text
ticker
= AACT

instrument_id
= cik_ticker:0001853138:AACT

identity_resolution_level
= cik_ticker

identity_valid_from
= 2023-06-12

identity_valid_to
= 2025-09-24
```

Authority:

```text
G:/TSIS/data/data_foundation_outputs/instrument_master/
instrument_master_v0_1.parquet
```

Build:

```text
instrument_master_v0_1_20260621T145725Z
```

The identity row covers the complete pilot interval. The runner must resolve
this row from the governed artifact; the values above are assertions, not a
hard-coded replacement for the identity lookup.

### 3.2 Session block

```text
calendar
= XNYS

timezone
= America/New_York

first_session
= 2024-09-06

last_session
= 2025-03-14

total_sessions
= 130 consecutive governed XNYS sessions

warmup_sessions
= 125

warmup_range
= 2024-09-06 through 2025-03-07

evaluation_sessions
= 5

evaluation_range
= 2025-03-10 through 2025-03-14
```

The block contains two governed early closes:

```text
2024-11-29
2024-12-24
```

It also crosses the America/New_York DST transition between `2025-03-07` and
`2025-03-10`.

Physical pre-inspection found one `market.parquet` for every one of the 130
sessions. This must be reverified by the runner and is not a substitute for the
dense acquisition and local-quality audit.

### 3.3 Decision grid

For every governed session, emit one decision timestamp for each integer UTC
second satisfying:

```text
session_open_utc < decision_timestamp < session_close_utc
```

The pilot covers the complete governed RTH session. It is not restricted to
the opening 60 or 90 minutes.

### 3.4 Binding parameters

```text
latency_policy_id
= LATENCY_PRIMARY_CONSERVATIVE_1000MS

window_seconds
= 5, 15, 30, 60, 300

multiscale_pairs
= 5/60, 15/300

baseline_candidates
= B20, B60, B120

trade_eligibility_policy
= trading_activity_trade_eligibility_policy_v0_2

price_view_for_dollar_activity
= trades_raw
```

Latency sensitivity runs are not part of this first multisession run. They
require a separate scope and run ID after the primary pilot closes.

---

## 4. Why this scope

AACT provides a dense physical series long enough to exercise the complete
`B120` lookback while retaining five additional warmup sessions before the
first evaluation day.

The block was selected before detector construction and without choosing known
winning charts or scanner outcomes.

The scope tests:

- normal and early-close sessions;
- EST and EDT calendar offsets;
- all Binding A windows;
- all three PIT baseline candidates;
- low-activity and more active sessions;
- multiple pre-existing Foundation quality labels;
- exact-duplicate flags and schema warnings without automatic source removal.

It does not establish universe-wide representativeness. That belongs to the
later stratified development stage.

---

## 5. Source bindings

### 5.1 Raw trades

```text
source_dataset_id
= trades_ticks_prod_2005_2026_legacy_rth_reduced

source_root
= G:/TSIS/data/trades_ticks_prod_2005_2026

partition_pattern
= {ticker}/year={YYYY}/month={MM}/day={YYYY-MM-DD}/market.parquet
```

Pre-inspection over the selected 130 files found:

```text
raw trade rows
= 14,492

raw share volume
= 30,874,913
```

These are planning observations and must be recomputed in the run manifest.

### 5.2 Calendar

```text
G:/TSIS/data/data_foundation_outputs/market_calendar/
market_calendar_v0_1.parquet
```

Expected build:

```text
market_calendar_v0_1_20260630T193931Z
```

Expected SHA-256:

```text
cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c
```

### 5.3 Instrument identity

```text
G:/TSIS/data/data_foundation_outputs/instrument_master/
instrument_master_v0_1.parquet
```

Expected SHA-256 from its manifest:

```text
69104387d2607306c3fa1740573d130db5e7c30b1d1527d3ee8a8d2b4d53c2d2
```

### 5.4 Trade-condition policy matrix

```text
C:/TSIS_Data/tests/third_party_evidence/massive/market_operations/
snapshot_20260806T220504Z/policy_matrix_candidate_v0_1/
trading_activity_trade_condition_policy_matrix_candidate_v0_1.csv
```

Expected SHA-256:

```text
b2f208496809cb970437d04024d93bfb98780b54b5d790091362aa145eb9635f
```

### 5.5 Foundation 57f evidence

Active resolved path:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/
trades_v2_materialized/trades_current_cd_merged/root_cause_exports/
file_acceptance_cache_lt1b_full_clean_fast_same_schema/raw_metrics_shards
```

The 130 selected sessions join one-to-one with 57f evidence. The observed label
distribution is:

```text
review                    81
review_microstructure     46
bad_data                   2
reference_scale_mismatch   1
```

Other planning observations:

```text
missing required columns       = 0
timestamp outside partition    = 0
negative price rows            = 0
negative size rows             = 0
files with dtype warning       = 4
maximum exact-duplicate ratio  = 7.31981981981982 percent
maximum trades at same time    = 7
```

These values orient the local audit. They do not decide inclusion.

### 5.6 Acquisition evidence

The dense input manifest must resolve acquisition evidence from the legacy
download runs under:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/
trades_lt_1b_download
```

The existing sidecar builder has no ticker/date filter and must not be run over
the full 9.4-million-task universe merely to obtain this pilot slice. The
implementation must add a bounded filter or build an equivalent bounded dense
scope resolver with tests.

---

## 6. Quality-label consumption decision

The governing policy is:

```text
TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md
```

For every Foundation label:

```text
FOUNDATION QUALITY LABEL
= preserved evidence metadata

FOUNDATION QUALITY LABEL
!= automatic pilot exclusion
```

No `good`, `review`, `review_microstructure`, `bad_data`,
`reference_scale_mismatch` or missing-evidence label may silently include or
exclude a session.

Every selected source session is retained in the scope manifest. If it cannot
support a variable family, the runner must emit the expected grain with null
values, an explicit degraded or unavailable state and reason codes.

---

## 7. Selected-session local audit

Before a session is interpreted, run a variable-relevance audit over its
complete selected RTH partition.

Required checks:

```text
PHYSICAL
- file exists and is readable
- required schema is present
- row count and source hash are recorded

TEMPORAL
- event timestamps parse
- timestamps belong to the governed session
- deterministic ordering is reproducible
- simulated availability never exceeds decision time when consumed

ACTIVITY
- price and size are positive finite values
- condition IDs are mapped or fail closed
- exact duplicates are flagged and preserved
- no silent deduplication occurs

COVERAGE
- acquisition status is reconstructed
- observed zero is not inferred from a missing or unreadable source
- unexplained source gaps remain unavailable or degraded

VARIABLE-SPECIFIC
- count and duration findings identify affected variables
- share-size findings identify affected share-volume variables
- price-scale findings identify affected dollar-volume variables
- unrelated VWAP/reference diagnostics do not become blanket rejection
```

The local audit grain is:

```text
instrument_id
session_date
variable_family
```

Minimum variable families:

```text
EVENT_COUNT_AND_INTENSITY
SHARE_VOLUME_AND_MARKS
DOLLAR_VOLUME
DURATION_AND_CONCENTRATION
```

Allowed local dispositions:

```text
LOCALLY_AUDITED_USABLE
LOCALLY_AUDITED_USABLE_WITH_FLAGS
LOCALLY_AUDITED_DEGRADED
LOCALLY_AUDITED_REPLACE_WINDOW
```

A material defect does not abort the complete workstream. The current run
retains and labels the affected session. A correction or replacement requires
a new scope revision; no session is silently swapped during the run.

The five-session warmup buffer allows the first target session to retain 120
prior sessions if up to five complete warmup sessions become non-calculable.
If more evidence is lost, the run still completes and reports the affected
baseline as insufficient; a later scope revision may extend warmup backward.

---

## 8. Expected materialization size

The strict decision grid contains:

```text
normal-session decision timestamps
= 23,399

early-close decision timestamps
= 12,599

total symbol-seconds across 130 sessions
= 3,020,270
```

Expected output rows:

| Output family | Formula | Expected rows |
|---|---:|---:|
| `CURRENT_STATE` | `3,020,270 x 5 windows` | `15,101,350` |
| `MULTISCALE_CONTRAST` | `3,020,270 x 2 pairs` | `6,040,540` |
| `PIT_BASELINE_AND_SURPRISE` | `5 target sessions x 23,399 x 5 windows x 3 baselines` | `1,754,925` |
| **Total** |  | **22,896,815** |

Per-session row expectations:

```text
CURRENT_STATE normal session
= 116,995

CURRENT_STATE early close
= 62,995

MULTISCALE normal session
= 46,798

MULTISCALE early close
= 25,198

PIT_BASELINE target session
= 350,985
```

The runner must perform a bounded serialization sizing probe before the full
materialization and record:

- measured compressed bytes per row by output family;
- projected total bytes;
- free space on the output drive;
- the projection method and sample partition.

The run must not start the expensive stage if:

```text
projected output > 25 GiB
OR
free output space < max(3 x projected output, 75 GiB)
```

Changing either limit requires a versioned run-plan amendment.

---

## 9. Required implementation before launch

Create in Data Foundation:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/
run_trading_activity_binding_a_multisession_pilot.py

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/
monitor_trading_activity_binding_a_multisession_pilot.ps1

C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/
trading_activity_binding_a_multisession_pilot_v0_1.json
```

The current single-partition smoke runner is not a multisession runner.

The multisession runner may use an optimized sliding-window/materialization
engine, but the existing pure kernel remains the semantic oracle. Calling the
current kernel by rescanning the complete event list for every second and every
window is not an acceptable production algorithm for this pilot.

Required equivalence evidence:

- exact comparison against the pure kernel at session/window boundaries;
- exact comparison around every event for a deterministic sample;
- deterministic random symbol-second sample with frozen seed;
- exact state and integer-field equality;
- documented numerical tolerance only for floating-point fields;
- duplicate flags and unknown conditions represented identically.

No optimization may change window boundaries, fixed denominators, trade
eligibility, missingness, simulated availability or baseline selection.

---

## 10. Run stages

```text
STAGE 0  validate invocation and write pre-manifest
STAGE 1  resolve calendar, identity and exact dense scope
STAGE 2  join acquisition and 57f evidence
STAGE 3  execute selected-session local audit
STAGE 4  run sizing and kernel-equivalence probes
STAGE 5  materialize CURRENT_STATE by session
STAGE 6  materialize MULTISCALE_CONTRAST from current state
STAGE 7  build cached PIT baseline distributions
STAGE 8  materialize PIT_BASELINE_AND_SURPRISE for five target sessions
STAGE 9  validate grains, row counts, temporal invariants and hashes
STAGE 10 write final manifest and compact test-run pointer
```

Stage transitions must update heartbeat and append one JSONL event.

---

## 11. Output topology

Heavy experimental outputs:

```text
G:/TSIS/data/data_foundation_outputs/
trading_activity_binding_a_multisession_pilot/
run_id=<run_id>/
```

Required layout:

```text
scope/
  dense_input_manifest.parquet
  dense_input_manifest.csv
  selected_session_local_audit.parquet

current_state/
  ticker=AACT/session_date=YYYY-MM-DD/part-00000.parquet

multiscale_contrast/
  ticker=AACT/session_date=YYYY-MM-DD/part-00000.parquet

pit_baseline_and_surprise/
  ticker=AACT/session_date=YYYY-MM-DD/part-00000.parquet

validation/
  row_count_validation.json
  grain_uniqueness_validation.json
  temporal_legality_validation.json
  kernel_equivalence_validation.json
  baseline_reference_validation.json
  output_hashes.parquet

metadata/
  output_schema_manifest.json
  lineage_manifest.json
  run_summary.json
```

Runtime telemetry:

```text
G:/TSIS/data/data_ops_manifests/
trading_activity_binding_a_multisession_pilot/<run_id>/
```

Compact repository-visible pointer:

```text
C:/TSIS_Data/tests/test_runs/<run_id>/run_pointer_manifest.json
```

The pointer may contain paths, hashes, status and counts. It must not duplicate
the heavy parquet outputs into Git or the C drive.

All parquet partitions must be written atomically with `zstd` compression. A
completed partition must have a recorded hash before it becomes resumable.

---

## 12. Minimum output metadata

Every output row must carry or deterministically reference:

```text
feature_spec_id
feature_version
binding_id
scope_id
pilot_scope_id
instrument_id
ticker
session_date
decision_timestamp
window_seconds or pair_id
subwindow_seconds when applicable
baseline_candidate_id when applicable
trade_eligibility_policy_id
latency_policy_id
source_dataset_id
source_schema_version
market_calendar_build_run_id
instrument_master_build_run_id
foundation_quality_label
local_window_disposition
quality_state
coverage_state
calculation_state
feature_input_max_available_at
lineage_manifest_id
future_window_used = false
```

Foundation and local-quality metadata may be normalized into referenced
sidecars if the row carries stable foreign keys. The lineage must remain
joinable without conversation context.

---

## 13. PIT baseline execution

For each evaluation row, baseline observations must come only from:

```text
prior session_date
same instrument_id
same America/New_York clock-minute bucket
same W
same latency policy
same trade eligibility policy
same schema regime
calculation_state = CALCULATED
```

The current session and future sessions are prohibited.

Cache baseline distributions by:

```text
evaluation_session_date
clock_minute_et
window_seconds
latency_policy_id
baseline_candidate_id
```

The per-second current value may then be compared with the cached sorted
distribution without rebuilding that distribution 60 times.

For every calculated evaluation row with sufficient source history, expected
reference-session counts are:

```text
B20  = 20
B60  = 60
B120 = 120
```

Opening-edge rows may legitimately carry insufficient current-window history.
No value is backfilled from before session open.

---

## 14. Long-running telemetry

The runner must comply with `LONG_RUNNING_OPERATIONS_CONTRACT.md`.

Before expensive work it must create:

```text
pre_manifest.json
pid_manifest.json
heartbeat_latest.json
heartbeat_history.jsonl
run.log
```

Heartbeat cadence:

```text
60 seconds
+ every stage boundary
+ every completed session partition
```

Domain counters must include when known:

```text
sessions_audited / 130
current_state_sessions / 130
multiscale_sessions / 130
baseline_sessions / 5
current_state_rows
multiscale_rows
baseline_rows
source_trade_rows
eligible_trade_rows
unknown_fail_closed_rows
degraded_output_rows
partitions_written
bytes_written
```

Compact monitor line:

```text
[timestamp] status=<status> stage=<stage> wrapper_alive=<bool>
progress=<done>/<total> session=<date> rows=<n> partitions=<n>
cpu=<n> io_read_Bps=<n> io_write_Bps=<n> output_free_GB=<n>
```

The monitor must derive `stale_no_process` when heartbeat is stale, no process
is alive and no final manifest exists.

---

## 15. Resume and overwrite policy

```text
overwrite_policy
= NEVER

resume_policy
= RESUME_HASH_VALIDATED_COMPLETE_PARTITIONS
```

At startup:

1. refuse a duplicate active run ID;
2. inspect PID liveness;
3. refuse to overwrite completed partitions;
4. skip only partitions whose expected hash and schema validate;
5. rebuild incomplete temporary partitions;
6. preserve interrupted outputs and telemetry;
7. record every resumed partition in the final manifest.

The runner must support a cooperative stop request checked between session
partitions and major stages. Destructive cleanup is not part of resume.

---

## 16. Technical success rules

Run completion and scientific evidence are separate verdicts.

### 16.1 Governed run completion

`RUN_COMPLETION = PASS` requires:

- pre-manifest, PID manifest, heartbeat, log and final manifest exist;
- exactly 130 governed session rows exist in the dense scope manifest;
- every session has an executed local audit for every required variable family;
- no session was silently removed or replaced;
- all three output families exist;
- output row counts equal the frozen expectations;
- grains are unique;
- partition hashes validate;
- all decision timestamps follow the governed calendar;
- `feature_input_max_available_at <= decision_timestamp` whenever non-null;
- `future_window_used = false` everywhere;
- no current or future session enters a baseline;
- kernel-equivalence probes pass;
- final status, warnings, resume state and promotion state are explicit.

A Foundation label or a locally degraded session cannot by itself make the
governed run incomplete.

### 16.2 Pilot evidence verdict

The post-run readout must separately issue:

```text
PILOT_EVIDENCE_VERDICT
= PASS_WITH_RESTRICTIONS
  or FAIL
```

This verdict evaluates whether physical Binding A behavior, baseline
availability and data adequacy are sufficient to open the next roadmap gate.

Examples that may produce a completed run but a failed evidence verdict:

- B120 remains unavailable for material target rows;
- temporal leakage is found after output reconstruction;
- variable-relevant source degradation is too broad;
- optimized and oracle kernels disagree;
- output is not deterministic across rebuild.

### 16.3 Promotion boundary

```text
RUN_COMPLETION = PASS
!= SOURCE GATE PASS
!= MODEL ADMISSION
!= CANONICAL FEATURE PROMOTION
!= WAKE-UP DETECTOR AUTHORIZATION
```

---

## 17. Failure handling

Infrastructure failures include:

- missing or corrupt telemetry;
- runner crash;
- wrong grain or row count;
- output overwrite;
- schema drift without a governed decision;
- source/calendar/identity hash mismatch;
- temporal leakage;
- unrecoverable partition hash mismatch.

Evidence findings are not infrastructure failures. They must be materialized as
states, warnings and reason codes so the run can finish and be evaluated.

Unknown trade conditions remain `UNKNOWN_FAIL_CLOSED` and degrade the affected
rolling windows according to the frozen kernel. They must not crash the run or
be silently treated as eligible.

---

## 18. Planned human commands

These commands define the intended interface. They are not executable until
the runner, config and monitor exist and pass their short smoke tests.

Launch command shape:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\run_trading_activity_binding_a_multisession_pilot.py" `
  --config "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\trading_activity_binding_a_multisession_pilot_v0_1.json" `
  --run-id "trading_activity_binding_a_multisession_pilot_<UTC_TIMESTAMP>"
```

Monitor command shape:

```powershell
powershell -NoProfile -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_trading_activity_binding_a_multisession_pilot.ps1" `
  -RuntimeRoot "G:\TSIS\data\data_ops_manifests\trading_activity_binding_a_multisession_pilot\<run_id>" `
  -Compact `
  -IntervalSeconds 30
```

Cooperative stop command shape:

```powershell
powershell -NoProfile -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\monitor_trading_activity_binding_a_multisession_pilot.ps1" `
  -RuntimeRoot "G:\TSIS\data\data_ops_manifests\trading_activity_binding_a_multisession_pilot\<run_id>" `
  -RequestStop
```

An agent must present the concrete commands with a real run ID and resolved
paths to the human. The agent must not launch this full run autonomously.

---

## 19. Required pre-launch tests

Before the human receives the concrete command:

```text
UNIT TESTS
- dense calendar block selection
- identity validity lookup
- acquisition-evidence bounded filtering
- Foundation evidence one-to-one join
- local variable-family dispositions
- exact duplicate flag preservation
- no automatic exclusion by Foundation label
- expected row-count calculation
- atomic partition write and resume
- Windows-safe heartbeat replacement
- stale monitor derivation

INTEGRATION SMOKE
- two sessions only
- one normal session and one early-close session
- bounded first minutes permitted only for smoke
- all three output families
- kernel equivalence
- stop and resume
- final manifest on success and controlled interruption
```

The bounded smoke does not change the full pilot scope.

---

## 20. Post-run artifacts

After physical completion, create:

```text
TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_READOUT_v0_1.md
```

Then update the current handoff and decide:

```text
FULL_LEGACY_SOURCE_GATE
= PASS_WITH_RESTRICTIONS or FAIL

STRATIFIED DEVELOPMENT EXECUTION
= AUTHORIZED or NOT_AUTHORIZED
```

No later roadmap stage opens without that versioned readout.
