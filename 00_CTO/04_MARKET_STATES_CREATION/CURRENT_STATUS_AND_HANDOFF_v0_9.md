# CURRENT_STATUS_AND_HANDOFF_v0_9

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-08` |
| `active_workstream` | `wake_up_trading_activity_ta_3` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `COMPLETE_AND_RECONCILE_BROAD_TA3_BINDING_A` |
| `supersedes` | `CURRENT_STATUS_AND_HANDOFF_v0_8.md` |

## 1. Current position

```text
TA-1 deterministic pilot                 = PASS_WITH_RESTRICTIONS
TA-2 legacy source gate                  = PASS_WITH_RESTRICTIONS
TA-3 stratified sample                   = FROZEN_AND_VALIDATED
TA-3 G-only source gate                  = PASS_WITH_RESTRICTIONS
TA-3 Binding A orchestrator              = IMPLEMENTED_AND_RESUME_CORRECTED
TA-3 Binding A preflight                 = PASS
TA-3 Binding A bounded physical smoke    = PASS
TA-3 broad Binding A execution           = RUNNING_WITH_CONTROLLED_CONCURRENCY
```

The run remains experimental. It does not authorize model admission, canonical
features, OOS access or Wake-up detection.

## 2. Frozen execution scope

```text
sample manifest SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

blocks                 = 240
targets                = 2,400
scope sessions         = 32,013
projected output rows  = 558,684,000
official trade root    = G:/TSIS/data/trades_ticks_prod_2005_2026
D fallback             = PROHIBITED
unavailable G sessions = 3,221 retained in denominator
```

## 3. Runtime incident and correction

Four deterministic shards were launched with 60 blocks each. During execution,
the parent orchestrators for shards 0, 2 and 3 terminated while block workers
had produced or were still producing governed outputs. Shard 1 remained alive.

The first recovery attempt exposed an orchestrator defect: global `--resume`
was forwarded to blocks that had never started. The single-block runner rejects
that state because no output run exists. Shard 2 therefore preserved its first
complete block and failed when the second, new block received `--resume`.

The orchestrator now resolves every block as:

```text
COMPLETE -> skip and register SKIPPED_COMPLETE
PARTIAL  -> invoke the subrunner with --resume
NEW      -> invoke the subrunner without --resume
```

Validation performed after the correction:

```text
Python compilation       = PASS
Ruff                     = PASS
orchestrator pytest      = PASS
PowerShell parser        = PASS
physical resume states   = COMPLETE / COMPLETE / NEW as expected
```

## 4. Concurrency decision

Workers reached approximately 6 GB during `STAGE_8` PIT baseline and surprise
materialization. The host exposes approximately 31.9 GB physical memory. Four
concurrent workers left an unsafe operating margin and may have contributed to
wrapper loss.

```text
MAX_CONCURRENT_TA3_WORKERS = 2
```

This is an operational safety decision, not a scientific change to Binding A
or the frozen sample.

## 5. Shard snapshot

Snapshot observed on 2026-08-08:

```text
SHARD 0 = RUNNING, 6/60 completed, 0 failed
SHARD 1 = RUNNING, 15/60 completed, 0 failed
SHARD 2 = QUEUED_FOR_CONTROLLED_RESUME, 1 complete block preserved
SHARD 3 = QUEUED_FOR_CONTROLLED_RESUME, 5 complete block outputs preserved
```

Shard counters are runtime snapshots and will advance. Governed block manifests
and output hashes, not this snapshot, determine final completion.

## 6. Monitor behavior

The monitor reads the active nested subrunner heartbeat and reports block
completion, internal stage, session, rows, partitions, elapsed time, CPU,
heartbeat age, internal message, and wrapper/worker liveness.

Block progress advances only after a complete block. Progress within a block is
demonstrated by stage, session, rows, partitions, elapsed time, CPU and fresh
heartbeats.

## 7. Immediate sequence

```text
1. Finish the currently active shards 0 and 1.
2. Resume shards 2 and 3 under the two-worker limit.
3. Reconcile all 240 block final manifests and output hashes.
4. Validate requested versus produced rows, coverage and missingness.
5. Emit the TA-3 stratified development source-gate readout.
6. Only after that gate, begin Binding B implementation.
```

Not authorized:

```text
Binding B execution
Binding C implementation without justification
OOS access
Representation Model admission
canonical feature promotion
Wake-up detector calibration
```

## 8. Parallel SEC/fundamental lane

The governed `instrument_master_v0_1` provides the 4,824-instrument acquisition
scope, 4,824 valid CIK mappings and instrument/FIGI context. An external agent
may acquire original SEC filing histories in parallel by unique CIK while
preserving instrument and share-class mappings.

That lane supports future point-in-time shares outstanding, presession market
capitalization and float-context estimates. It does not alter or block the
current Trading Activity Binding A execution.

## 9. Remaining Trading Activity sequence

```text
Binding B implementation
-> A/B comparison at fixed false-alarm budget
-> justified Binding C only if needed
-> temporal OOS validation
-> Representation Model admission or rejection
-> canonical physical binding decision
-> table and lineage mapping
-> full-scope materialization decision
```

Completing Trading Activity does not complete Wake-up. Market Microstructure
State, Price Movement, Liquidity, supporting/conditional context, integrated
representation, detector evaluation and Episode Instance remain downstream.

## 10. Experimental-to-canonical lifecycle clarification

The active TA-3 run is a restricted experimental development materialization.
It evaluates Binding A and its builder; it is not the final 2005-2026 canonical
Trading Activity history.

```text
Binding A / B / justified C
-> frozen development comparison
-> untouched temporal OOS
-> model and binding admission or rejection
-> canonical specification and builder
-> separate full-history production materialization
-> backtest consumption
```

Three time concepts must not be conflated:

```text
feature horizon W       = trailing event window at decision time t
PIT baseline lookback B = causal historical reference before t
coverage period         = calendar history physically materialized
```

Canonical promotion first governs selected dimensions, variables, formulas,
horizons, policies, schema, lineage and the validated builder. A separate run
must then materialize and validate the authorized parent universe and historical
coverage. Backtests normally read this versioned representation dataset; they do
not recompute every raw-event window on each request.

Full contract:

```text
EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md
```
