# CURRENT_STATUS_AND_HANDOFF_v0_13

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-11` |
| `active_workstream` | `wake_up_trading_activity_cpp_full_materialization` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `240_BLOCK_RECONCILIATION_AND_FINAL_CERTIFICATION` |
| `supersedes` | `CURRENT_STATUS_AND_HANDOFF_v0_12.md` |

## 1. Current position

```text
TA-1 deterministic pilot                 = PASS_WITH_RESTRICTIONS
TA-2 legacy source gate                  = PASS_WITH_RESTRICTIONS
TA-3 stratified sample                   = FROZEN_AND_VALIDATED
TA-3 G-only source gate                  = PASS_WITH_RESTRICTIONS
TA-3 Binding A preflight                 = PASS
TA-3 old broad Python execution          = PAUSED_PRESERVED_NO_RESUME
Stage-8 original C++ prototype           = FAIL_EQUIVALENCE_PRESERVED
Stage-8 corrected representative smoke   = PASS_EXACT
Stage-8 limited stratified equivalence   = PASS_EXACT_25_OF_25
Stage-8 explicit engine integration      = COMPLETE
Stage-8 four-shard recertification       = PASS_4_OF_4
new broad C++ materialization            = AUTHORIZED_AND_RUNNING
full 240-block certification             = PENDING_RUN_COMPLETION
SEC PIT lane                             = PARKED_PENDING_TRADING_ACTIVITY_CLOSE
```

The human explicitly authorized the new versioned broad run. This authorization
does not authorize canonical promotion, Binding B, OOS access or any semantic
change.

## 2. Non-negotiable semantic invariant

Python remains the semantic oracle. C++ changes only execution speed and
resource use. It may not change any variable, formula, column, order, dtype,
NULL mask, calculation state, PIT reference metadata, identity metadata,
lineage or output grain. Any difference is `FAIL`.

Frozen execution identity:

```text
engine contract = trading_activity_stage8_engine_binding_v0_1
engine id = trading_activity_stage8_cpp_native_candidate_v0_1
semantic oracle = trading_activity_stage8_python_reference_v0_2
engine fingerprint = 7d24178a5b475c36401b4321af95630550185e5ea227dfe3419f08398bb54a0a
C++ source SHA-256 = 0d62f8ae9c63d59e52b0360b0fec514c8f5afdc19fe7e98f1622a80f772d7848
native binary SHA-256 = 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
full wrapper SHA-256 = 338fe64807ceb817867ea07504a78b58d1ed333d39c89ac9ccaf8fb11bf92034
plan SHA-256 = 2e7e4be33237cd1836cfe6ecf1c6ad5ca227b284a9152c87ca6dbddbebdaf5a5
```

Resume is legal only for this same plan, wrapper, engine, source and binary
identity. It must fail closed on any mismatch.

## 3. Active governed run

```text
run id = trading_activity_ta3_cpp_full_v0_1_20260811
physical run id = ta3_cpp_v0_1_20260811
status = RUNNING
launch observed = 2026-08-11T00:08:48Z
wrapper PID at launch = 27572
logical shards = 4
blocks per shard = 60
total blocks = 240
initial workers = 1
maximum concurrent workers = 2
second-worker gate = 120 seconds plus RAM/resource admission
projected total rows = 558,684,000
projected parquet footprint = approximately 61.15 GiB
reserved footprint = 80 GiB
estimated wall time = 4 to 8 hours
```

Governed roots:

```text
plan = VARIABLES_FEATURES/TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_PLAN_v0_1.json
run root = D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811
outputs = <run root>/outputs
runtime = <run root>/runtime
pointers = <run root>/pointers
```

The compact aliases are preregistered in the plan to keep Windows paths below
the usable path ceiling. They do not rename the logical Information Object,
Representation Model or binding.

## 4. Initial runtime evidence

The first operational gate after launch was healthy:

```text
status = RUNNING
active workers = 2
failed shards = 0
completed blocks at early snapshot = 0/240
process-tree RSS = approximately 3.5 GiB
available memory = approximately 10.3 GiB
pagefile used = approximately 0.16 GiB
output free space = approximately 901.1 GiB
driver stderr = empty
shard stderr = empty
independent monitor PID = 24528
```

Zero completed blocks in the early snapshot is not a failure: the two first
complete blocks were still calculating. Runtime authority is the current
heartbeat and manifests, not this static snapshot.

## 5. Monitoring and cooperative stop

Live human monitor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/monitor_long_running_operation.ps1 -RunRoot D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811/runtime -IntervalSeconds 30 -Compact -Watch
```

Heartbeat:

```text
D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811/runtime/heartbeat_latest.json
```

Safe cooperative stop is requested by creating:

```text
D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811/runtime/stop_requested.json
```

Do not kill block workers or manually move partial outputs unless the governed
recovery procedure proves the coordinator is unavailable.

## 6. Final gate still open

Run launch is complete, but materialization is not yet certified. The next gate
must verify all 240 block manifests, exact expected counts, stable schema and
column order, the frozen fingerprint, warnings, lineage and aggregate counts.
Only a successful final manifest can change this run from `RUNNING` to `PASS`.

Explicitly unauthorized:

```text
mixing preserved Python partitions with this C++ lineage
changing the frozen engine or wrapper during the run
calling the run PASS before final certification
Binding B execution
OOS access
Representation Model admission
canonical feature promotion
Wake-up detector calibration
```

## 7. SEC PIT pending lane

SEC PIT evidence under `_DESCAGRA_DATOS_NECESARIA_/` remains preserved and
parked. It resumes after this materialization and its certification close; this
handoff does not reinterpret or delete that evidence.
