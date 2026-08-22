# Trading Activity Stage-8 target-only recovery and recertification plan v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_stage8_target_only_recovery_and_recertification_plan` |
| `document_version` | `v0_1` |
| `document_role` | `RECOVERY_AND_RECERTIFICATION_PLAN` |
| `document_status` | `PREREGISTERED_NOT_AUTHORIZED_NOT_EXECUTED` |
| `created_at` | `2026-08-14` |
| `source_run_id` | `trading_activity_ta3_cpp_full_v0_1_20260811` |
| `source_run_state` | `FAILED_NOT_PROMOTED_WITH_240_COMPLETE_BLOCKS` |
| `target_scope` | `FROZEN_TA3_240_BLOCKS_2400_EXPLICIT_TARGET_SESSIONS` |
| `full_rematerialization` | `PROHIBITED_BY_DEFAULT` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `human_launch_required` | `true` |

## 1. Objective

Recover and independently certify the exact 2,400 frozen TA-3 target sessions
from partitions already produced by the completed C++ run, without recomputing
the 240 Stage-8 blocks and without changing the immutable failed lineage.

The recovery product is a new versioned target-only artifact with its own
manifest, validation evidence, final status and consumption boundary.

## 2. Non-goals

This plan does not authorize:

- rerunning the four parent shards;
- overwriting, moving or deleting any source output;
- editing the original preregistered JSON plan;
- changing Binding A formulas, schemas, dtypes, NULL semantics or PIT rules;
- including warm-up or intervening non-target sessions in the TA-3 denominator;
- Binding B, temporal OOS, Wake-up detector work or model admission;
- canonical or institutional promotion;
- treating the source run as `PASS`.

## 3. Immutable source authority

```text
source run root
= D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811

source output root
= <source run root>/outputs

source runtime root
= <source run root>/runtime

source terminal recovery manifest
= <source run root>/runtime/recovery/final_manifest.json

source target table
= G:/TSIS/data/data_foundation_outputs/
  trading_activity_ta3_stratified_sample/
  trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/
  selected_target_contexts_v0_1.parquet

source target-table SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220
```

Before execution, the implementation must also verify the frozen sample
manifest SHA-256:

```text
100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf
```

Any mismatch is a fail-closed stop.

## 4. New artifact identity

The implementation must allocate a new immutable root and final `run_id` before
launch. The following is a logical placeholder, not an executable identity:

```text
logical dataset
= trading_activity_binding_a_ta3_target_only_candidate_v0_1

planned run-id prefix
= ta3_stage8_target_only_recovery_v0_1_

physical root family
= D:/TSIS/IO/wu/ta/pmma/ba02/target_only/
```

The final run ID, plan/config hashes, script hashes, Git commit and dirty-state
snapshot must be persisted in a pre-manifest. No command is authorized until
those artifacts and the implementation tests exist.

## 5. Exact selection rule

The recovery controller must derive the selected source partitions solely from
the frozen target table and the 240 completed block manifests.

Required join identity:

```text
block_id
instrument_id
ticker_as_of_session
session_date
```

For every one of the 2,400 target rows, exactly one source partition must exist
in each family:

```text
current_state
multiscale_contrast
pit_baseline_and_surprise
```

Expected partition cardinality:

```text
2,400 targets x 3 families = 7,200 selected partitions
```

Missing, duplicate, cross-block or identity-mismatched matches must halt the
run. Directory-range inference without joining the frozen target table is
prohibited.

## 6. Correct target-only row-count contract

The target table records source session duration. The actual Binding A grid is
open-exclusive and close-exclusive:

```text
decision_points = source_session_seconds - 1
```

The exact frozen aggregate contract is:

| Family | Required rows |
|---|---:|
| `current_state` | 279,330,000 |
| `multiscale_contrast` | 111,732,000 |
| `pit_baseline_and_surprise` | 837,990,000 |
| **Total** | **1,229,052,000** |

Per-target formulas:

```text
current_state
= decision_points * 5 windows

multiscale_contrast
= decision_points * 2 short/long pairs

pit_baseline_and_surprise
= decision_points * 5 windows * 3 baseline candidates
```

`decision_seconds_total` is validation metadata. It must not be compared as if
it were a fourth materialized output family.

## 7. Execution phases

### R0. Read-only preflight

Verify:

- source and target-table hashes;
- four parent manifests `COMPLETE` with 60 blocks each;
- 240 unique block manifests `COMPLETE`;
- exact frozen C++ engine fingerprint in every block and summary;
- no live writer owns the source run;
- destination does not exist unless the exact resume identity matches;
- disk and memory gates required by the long-running operations contract.

### R1. Build target partition inventory

Create a machine-readable inventory with one row per target and family,
including:

```text
block_id
block_run_id
instrument_id
ticker
session_date
family
source_path
source_bytes
recorded_source_sha256
recorded_rows
expected_rows
source_engine_fingerprint
source_lineage_manifest
```

The inventory itself must be written atomically and hashed.

### R2. Recompute selected-file integrity

For all 7,200 selected Parquet files:

- recompute SHA-256 from bytes;
- compare against the block `output_hashes.parquet` record;
- compare file rows against the corrected target-only formula;
- validate Parquet readability and footer metadata;
- record zero missing files, zero size mismatches and zero hash mismatches.

This phase may be long and must be human-launched under
`LONG_RUNNING_OPERATIONS_CONTRACT.md`.

### R3. Create the target-only artifact

The default first product is an immutable reference-manifest dataset over the
verified source partitions. This avoids duplicating data before a consumer
requires a standalone physical layout.

Required behavior:

```text
source bytes remain immutable
target-only membership is explicit
every reference carries source SHA-256 and row count
failed source-run status remains visible in lineage
new target-only certification status is independent
```

A standalone byte copy or compaction is a separate, explicitly authorized
materialization. If later required, it must use a new root, preserve the same
row-level semantics and verify copied hashes or deterministic rewritten-file
lineage. Hardlinks must not be used as a substitute for an immutability policy.

### R4. Target-only conformance

The new validator must certify:

- exactly 2,400 unique target identities;
- exactly 7,200 selected family partitions;
- exact aggregate and per-target row counts;
- one schema variant per family;
- required feature and metadata columns present;
- stable column names, types and order;
- exact engine fingerprint and lineage IDs;
- `future_window_used=false`;
- temporal legality and PIT reference dates;
- grain uniqueness within every selected partition;
- zero warnings that violate the frozen contract.

### R5. Final manifest

Only after all previous phases pass may the new artifact write:

```text
status = PASS
scope = FROZEN_TA3_2400_TARGET_SESSIONS_ONLY
source_run_status = FAILED_NOT_PROMOTED
source_blocks_recomputed = 0
canonical_promotion_authorized = false
```

On interruption or failure, write a terminal or resumable manifest without
changing the source run.

## 8. Required implementation artifacts before launch

The Data Foundation owner must create and test:

1. a versioned machine-readable recovery plan/config;
2. a target-partition inventory builder;
3. a target-only validator/certifier;
4. a long-running wrapper with pre-manifest, PID, heartbeat, live log, stop
   request, resume and final manifest;
5. a separate monitor command;
6. unit fixtures for normal, early-close, missing, duplicate, wrong block,
   wrong hash, wrong row count and wrong engine fingerprint cases;
7. one bounded production-equivalent preflight for each logical shard before
   any long integrity scan.

`resume` may reuse only hash-validated completed inventory/hash-check units
from the same plan, code, schema and source identity.

## 9. Acceptance gate

```text
TARGET_ONLY_RECOVERY_PASS
= source identity PASS
  and target join 2400/2400 PASS
  and partitions 7200/7200 PASS
  and selected-file SHA-256 7200/7200 PASS
  and corrected row counts PASS
  and schema/metadata conformance PASS
  and temporal/PIT/grain validation PASS
  and final manifest PASS
```

Until then:

```text
Binding A stratified evidence close = BLOCKED
Binding B                           = BLOCKED
OOS                                = NOT_AUTHORIZED
canonical promotion                = NOT_AUTHORIZED
```

## 10. Authorization boundary

This document prepares the recovery but does not authorize execution. A future
agent must not invent a launch command from this prose. After implementation,
tests and bounded shard-equivalent probes pass, the human must receive the exact
one-line launch and monitor commands and explicitly authorize the long run.

