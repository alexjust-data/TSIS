# Trading Activity Stage-8 target-only implementation and four-shard probe readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `EXECUTION_AND_GATE_READOUT` |
| `document_status` | `PASS_PROBES_FULL_HUMAN_AUTHORIZED_NOT_LAUNCHED` |
| `executed_at` | `2026-08-14` |
| `scope` | `TA-3 Stage-8 immutable target-only recovery` |
| `source_run_status` | `FAILED_NOT_PROMOTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `none` |

## 1. Outcome

The target-only recovery path is implemented and its mandatory bounded gate has
passed on all four logical shards.

```text
implementation and unit/adversarial tests = PASS 5/5
production-equivalent shard probes        = PASS 4/4
exact probe TARGET rows                   = PASS 8/8
selected probe family partitions          = PASS 24/24
early-close TARGET coverage               = PASS 4/4 shards
cross-shard schema variants               = 1 per family
prepared FULL fail-closed rehearsal       = PASS_REJECTED_NOT_AUTHORIZED
source blocks recomputed                   = 0
FULL target-only recovery                  = HUMAN_AUTHORIZED_NOT_LAUNCHED
canonical promotion                       = NOT_AUTHORIZED
```

This gate does not repair or relabel the historical failed wrapper. It verifies
immutable outputs and creates a separately governed target-only reference
artifact. No feature values are recalculated or copied.

## 2. Implemented executable surface

| Artifact | SHA-256 |
|---|---|
| `trading_activity_stage8_target_only_contract.py` | `69293ee4b95e7873d4c37dd7b84220ecc18df24c6e4f442c52b5fe8fb3f331a4` |
| `run_trading_activity_stage8_target_only_recovery.py` | `d9596b152c30ba8c64ab3b4b957a06d54ab099ff38ccbf139f110002d8f2e20d` |
| `build_trading_activity_stage8_target_only_recovery_plan.py` | `0d929bff6465a9fe791a2306bc2d27210124827012ebb3e1ab61db643eb3955d` |
| `monitor_trading_activity_stage8_target_only_recovery.ps1` | `e1d49ac9cd0e1206dd46a2753aa7e43c994ae46663e61a862c2c4bd7b8f68e8d` |
| probe plan v0.3 | `d0d794a4ff9a036ccdcd8504401a446257f19cd96563292765d8dedf0a92913f` |
| prepared FULL plan v0.3 | `4968b5f3a8ad986e1a7a22aa1ab236a269b8253d189305cecacb9b255df9c99b` |
| authorized FULL plan v0.3 | `13c5fcee1b4367ca9aecabc91503cbbedc4e45f901ed7dbaddc2d8897080592c` |

The runner verifies plan/script/contract/monitor, historical plan, frozen TARGET
table, sample manifest, Stage-8 engine fingerprint, block identity, selected
file SHA-256, sidecar, byte size, Parquet footer rows, required columns, path
identity, schema, sample values, inherited block validators and
`future_window_used=false`.

Resume is allowed only for a unit already marked `PASS` under identical plan,
script, contract, target, source and file hashes. Overwrite is prohibited.

## 3. Authoritative cardinality contract

The contract has exactly three physical count keys. Metadata scalars never
participate in physical-family dictionary equality.

```text
decision_points = source_session_seconds - 1

current_state                = decision_points * 5
multiscale_contrast          = decision_points * 2
pit_baseline_and_surprise    = decision_points * 5 * 3
```

For the frozen 2,400 TARGET sessions:

| Domain | Exact value |
|---|---:|
| TARGET sessions | 2,400 |
| family partitions | 7,200 |
| decision points | 55,866,000 |
| current-state rows | 279,330,000 |
| multiscale rows | 111,732,000 |
| PIT-baseline rows | 837,990,000 |
| total physical rows | 1,229,052,000 |
| early-close TARGET sessions | 27 |

Exact TARGET identity is the four-field key:

```text
(block_id, instrument_id, ticker_as_of_session, session_date)
```

`target_ordinal` is metadata local to upstream grouping and is not an identity.

## 4. Tests and defects caught before authorization

Focused test result:

```text
01_TSIS_DATA_FOUNDATION/tests/test_trading_activity_stage8_target_only_recovery.py
5 passed
```

The gate caught and corrected two additional implementation defects before a
long run was authorized:

1. `target_ordinal` restarts across blocks and is not globally unique. Probe
   membership and inventory uniqueness now use the exact four-field key.
2. `pyarrow.read_table` inferred the `run_id=...` parent directory as a Hive
   partition and collided with the physical `run_id` column in
   `output_hashes.parquet`. Explicit files are now read through
   `ParquetFile.read()`, without dataset partition inference.

These findings are prevention evidence for later Representation Model runners:
never infer global identity from an ordinal without proving its domain, and do
not use dataset/Hive inference when reading an explicitly named manifest file.

## 5. Four-shard production-equivalent evidence

Each probe used the frozen production code, config semantics, source blocks,
schemas and validation policies. Each selected two TARGET sessions, including
one early-close session, and three families per TARGET.

| Shard | TARGET | Partitions | SHA/footer/schema PASS | Early close | Final manifest SHA-256 |
|---:|---:|---:|---:|---:|---|
| 0 | 2 | 6 | 6/6 | 1 | `0013a229f5fd721c1a9247ef0e5451a4ac814b108582c4278e8675762e4fab81` |
| 1 | 2 | 6 | 6/6 | 1 | `fe7afb7f940d1d7d5e2473e2c5ce79af014227b0d073afc17db18c39fb69b775` |
| 2 | 2 | 6 | 6/6 | 1 | `39ef85be01dd10d5e29fa4e715c9185d90536a349938327c5b710551a4bb3c55` |
| 3 | 2 | 6 | 6/6 | 1 | `506066e680c48abf2d695c21fddc8c15cd89acde8386ff417c62b970aa647680` |

Across all four manifests, every family has one schema fingerprint and
`RM-MAT-CTRL-001..005` is `PASS` for the bounded gate. Incident closure remains
pending until the full 2,400/7,200 certification terminates `PASS`.

## 6. FULL authorization state and execution boundary

Prepared plan:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/
trading_activity_stage8_target_only_full_recovery_prepared_v0_3_20260814.json

artifact_status      = PREREGISTERED_NOT_AUTHORIZED
human_authorization  = NOT_AUTHORIZED
```

The prepared plan remains intentionally non-executable. On `2026-08-14`, AlexJ
explicitly authorized a separately frozen executable plan:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/
trading_activity_stage8_target_only_full_recovery_authorized_v0_3_20260814.json

SHA-256             = 13c5fcee1b4367ca9aecabc91503cbbedc4e45f901ed7dbaddc2d8897080592c
artifact_status      = PREREGISTERED_HUMAN_AUTHORIZED
human_authorization  = AUTHORIZED_BY_ALEXJ_20260814
execution_state      = NOT_LAUNCHED
```

Only the human launches the subsequent 7,200-partition
integrity/certification run.
A direct runner rehearsal against the prepared plan exited non-zero with
`Full recovery is not human-authorized`, before creating runtime state.
The earlier v0.2 plans are superseded historical preparation evidence and are
rejected by the current runner because they do not carry controls 004..005.

## 7. Expected FULL artifacts

The authorized run must write before and during work:

```text
runtime/pre_manifest.json
runtime/pid_manifest.json
runtime/heartbeat_latest.json
runtime/heartbeat_history.jsonl
runtime/run.log
artifacts/target_partition_inventory.parquet
artifacts/target_partition_inventory_summary.json
artifacts/partition_verification.jsonl
artifacts/verified_reference_manifest.parquet
runtime/final_manifest.json
```

Terminal `PASS` requires exactly 2,400 TARGET keys, 7,200 selected partitions,
the three exact row totals, one schema per family, all selected hashes and
validators passing, zero recomputation and no canonical promotion.
