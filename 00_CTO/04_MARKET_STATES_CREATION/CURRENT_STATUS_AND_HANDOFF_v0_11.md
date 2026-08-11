# CURRENT_STATUS_AND_HANDOFF_v0_11

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-11` |
| `active_workstream` | `wake_up_trading_activity_stage8_cpp_equivalence` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `INTEGRATE_CPP_ENGINE_FINGERPRINT_AND_RUN_FOUR_SHARD_PROBES` |
| `supersedes` | `CURRENT_STATUS_AND_HANDOFF_v0_10.md` |

## 1. Meaning of handoff

A handoff is the versioned current-state document used so another human or
agent can continue without relying on chat or memory. It does not transfer code
ownership, promote an artifact or authorize execution. Previous handoffs remain
historical evidence; this file is the current operational snapshot.

## 2. Current position

```text
TA-1 deterministic pilot                 = PASS_WITH_RESTRICTIONS
TA-2 legacy source gate                  = PASS_WITH_RESTRICTIONS
TA-3 stratified sample                   = FROZEN_AND_VALIDATED
TA-3 G-only source gate                  = PASS_WITH_RESTRICTIONS
TA-3 Binding A preflight                 = PASS
TA-3 broad Binding A execution           = PAUSED_FOR_HARDWARE_OPTIMIZATION
Stage-8 original C++ prototype           = FAIL_EQUIVALENCE
Stage-8 corrected representative smoke   = PASS_EXACT
Stage-8 limited stratified equivalence   = PASS_EXACT
SEC PIT lane                             = PARKED_PENDING_TRADING_ACTIVITY_CLOSE
```

No broad Trading Activity worker is alive. Stale `RUNNING` heartbeats are not
runtime authority.

## 3. Preserved physical state

```text
frozen TA-3 blocks                  = 240
physically complete Python blocks  = 23
shard 0 complete block manifests   = 8
shard 1 complete block manifests   = 15
failed complete blocks             = 0
shards 2 and 3 broad continuation  = NOT_STARTED_IN_CURRENT_D_ROOT
```

The shard-0 pause aggregate says seven complete, but eight granular block final
manifests were completed before the pause. Granular final manifests and hashes
govern. Preserve all outputs; do not rewrite or merge them with C++ results.

## 4. Contract invariant

Python is the semantic oracle. C++ may change only execution speed and resource
use. It may not change any variable, formula, column, order, dtype, NULL mask,
calculation state, PIT reference metadata, identity metadata, lineage or output
grain.

Any difference is `FAIL`; there is no partial acceptance based on performance.

## 5. Incident, correction and evidence

The first C++ prototype was approximately 7.24x faster in the kernel but used a
global historical date list. It changed group-specific PIT metadata and failed
equivalence.

The corrected C++ implementation selects historical sessions separately per
`(clock_minute_et, window_seconds)`. The production-equivalent ACU 2012-04-18
comparison produced:

```text
rows                   = 350,985
contract mismatches    = 0
exact mismatches       = 0
Parquet hash exact     = true
current binary kernel  = 43.105 seconds in final exact smoke
reference kernel       = 210.990 seconds
current speedup        = approximately 4.89x
```

Authority:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_STAGE8_CPP_OPTIMIZATION_AND_EQUIVALENCE_READOUT_v0_1.md
```

## 6. Immediate sequence

```text
1. Integrate C++ behind an explicit engine, source and binary fingerprint without changing the Python-defined contract.
2. Repeat one bounded production-equivalent probe on each of the four shards.
3. Audit every variable, schema, grain, PIT rule, missingness and lineage.
4. Obtain the governed human PASS.
5. Launch a new versioned 240-block run from zero; never mix old Python and new C++ run IDs.
6. Reconcile the new 240-block run before Binding B.
```

Limited stratified comparison plan:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_STAGE8_CPP_BLOCK_EQUIVALENCE_PLAN_v0_1.json
```

Executed evidence:

```text
runtime root             = D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/benchmarks/ta8_eq_limited_v0_1_20260811T010000Z
status                   = PASS
sessions                 = 25/25
rows                     = 8,612,625
contract mismatches      = 0
exact mismatches         = 0
Parquet hashes exact     = 25/25
elapsed                  = 927.500 seconds
native module SHA-256    = 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
```

This limited PASS closes only the comparison gate. It does not authorize C++
production integration, resume or broad materialization.

## 7. Explicitly unauthorized

```text
resume of ba2r2 with a changed engine
mixing Python and C++ partitions in one run lineage
production runner C++ integration without an explicit engine/binary fingerprint
long materialization before four-shard recertification
Binding B execution
OOS access
Representation Model admission
canonical feature promotion
Wake-up detector calibration
```

## 8. SEC PIT pending lane

SEC PIT is preserved as pending work under:

```text
_DESCAGRA_DATOS_NECESARIA_/
```

Do not delete or reinterpret its existing evidence. It is parked while Stage 8
Trading Activity equivalence and the subsequent governed materialization are
the active priority. Resume SEC PIT after this workstream closes.

## 9. Executed operational command

The limited gate was launched once with a new runtime root:

```powershell
python C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/validate_trading_activity_baseline_cpp_block_equivalence.py --plan C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/VARIABLES_FEATURES/TRADING_ACTIVITY_STAGE8_CPP_BLOCK_EQUIVALENCE_PLAN_v0_1.json --runtime-root D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/benchmarks/ta8_eq_limited_v0_1_20260811T010000Z

powershell -File C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/monitor_long_running_operation.ps1 -RunRoot D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/benchmarks/ta8_eq_limited_v0_1_20260811T010000Z -Watch
```

The generic long-operation monitor ran in a separate process and was stopped
after the final `PASS` manifest. Do not rerun this consumed plan unless the
candidate is invalidated and a new governed runtime root is explicitly
authorized.
