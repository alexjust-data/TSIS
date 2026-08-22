# CURRENT_STATUS_AND_HANDOFF_v0_12

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `HISTORICAL_COMPATIBILITY_POINTER_NOT_CURRENT` |
| `snapshot_at` | `2026-08-11` |
| `original_snapshot_sha256` | `e68cae3fa6dbacf3ffda8e85130b01fda48f518f523ea84bd4c26adc6eccbf31` |
| `active_workstream` | `wake_up_trading_activity_governed_broad_run_decision` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `HUMAN_DECISION_ON_NEW_VERSIONED_240_BLOCK_CPP_RUN` |
| `current_authority` | `CURRENT_STATUS_AND_HANDOFF_v0_28.md` |
| `lineage_authority` | `TRADING_ACTIVITY_HANDOFF_AND_ROADMAP_LINEAGE_CONSOLIDATION_v0_1.md` |

> Historical compatibility notice: this document is retained only because an
> external Applied Architecture pointer still names it. It must not be used as
> current workstream authority. Read `CURRENT_STATUS_AND_HANDOFF_v0_28.md`.

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
new broad C++ materialization            = NOT_AUTHORIZED
SEC PIT lane                             = PARKED_PENDING_TRADING_ACTIVITY_CLOSE
```

No broad Trading Activity worker or probe worker is alive. Stale `RUNNING`
heartbeats are not runtime authority.

## 2. Non-negotiable semantic invariant

Python is the semantic oracle. C++ may change only execution speed and resource
use. It may not change any variable, formula, column, order, dtype, NULL mask,
calculation state, PIT reference metadata, identity metadata, lineage or output
grain. Any difference is `FAIL`.

The explicit candidate identity is:

```text
engine contract = trading_activity_stage8_engine_binding_v0_1
engine id = trading_activity_stage8_cpp_native_candidate_v0_1
semantic oracle = trading_activity_stage8_python_reference_v0_2
engine fingerprint = 7d24178a5b475c36401b4321af95630550185e5ea227dfe3419f08398bb54a0a
C++ source SHA-256 = 0d62f8ae9c63d59e52b0360b0fec514c8f5afdc19fe7e98f1622a80f772d7848
native binary SHA-256 = 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
```

The runner persists this identity in pre-manifest, lineage, run summary,
pointer and final manifest, and fails closed on an expected fingerprint or
resume mismatch.

## 3. Preserved physical state

```text
frozen TA-3 blocks                       = 240
physically complete old Python blocks    = 23
old shard 0 complete block manifests     = 8
old shard 1 complete block manifests     = 15
old broad run                            = PRESERVE_NEVER_MIX_WITH_CPP
four-shard cycle 1                       = FAILED_PRE_STAGE8_MAX_PATH_PRESERVED
four-shard cycle 2                       = PASS_NEW_COMPACT_ROOT
```

The first four-shard cycle failed in Stage 6 before C++ because a Windows
atomic sidecar path exceeded usable path length. Its evidence was preserved and
was not resumed. Cycle 2 used a new preregistered plan, new run IDs and compact
roots.

## 4. Four-shard certification

```text
plan = VARIABLES_FEATURES/TRADING_ACTIVITY_STAGE8_CPP_FOUR_SHARD_PROBE_PLAN_v0_2.json
runtime root = D:/TSIS/IO/ta8c2/r
status = PASS
elapsed = 231.710 seconds
completed shards = 4/4
failed shards = 0
current_state rows = 156,300
multiscale rows = 62,520
PIT baseline rows = 36,900
engine fingerprint variants = 1
schema variants per output family = 1
missing required variables or metadata = 0
future_window_used = false
```

Authority:

```text
VARIABLES_FEATURES/
TRADING_ACTIVITY_STAGE8_CPP_ENGINE_INTEGRATION_AND_FOUR_SHARD_RECERTIFICATION_READOUT_v0_1.md
```

## 5. Next governed sequence

```text
1. Human reviews the engine-integration and four-shard PASS evidence.
2. Human separately authorizes or rejects a new versioned 240-block C++ run.
3. If authorized, preregister a new run/root/IDs and execute from zero.
4. Reconcile and independently certify all 240 blocks before Binding B.
5. Never resume ba2r2 and never mix Python/C++ partitions in one lineage.
```

The completed bounded probe is not implicit authorization for step 2.

## 6. Explicitly unauthorized

```text
resume of ba2r2 with a changed engine
mixing Python and C++ partitions in one run lineage
changing any Python-defined Trading Activity semantics
broad materialization without separate governed human authorization
Binding B execution
OOS access
Representation Model admission
canonical feature promotion
Wake-up detector calibration
```

## 7. SEC PIT pending lane

SEC PIT evidence under `_DESCAGRA_DATOS_NECESARIA_/` remains preserved and
parked. It resumes after the Trading Activity materialization decision and
workstream close; this handoff does not reinterpret or delete that evidence.
