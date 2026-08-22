# Trading Activity Stage-8 target-only FULL execution and certification readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `FULL_EXECUTION_AND_TERMINAL_CERTIFICATION_READOUT` |
| `document_status` | `PASS_TERMINAL_CERTIFIED_EXPERIMENTAL_NOT_CANONICAL` |
| `executed_at` | `2026-08-14` |
| `scope` | `TA-3 Binding A immutable target-only recovery` |
| `source_run_status` | `FAILED_NOT_PROMOTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `none` |

## 1. Terminal verdict

```text
run status                              = PASS
inventory status                        = PASS
certification status                    = PASS
exact TARGET identities                 = 2,400/2,400
verified family partitions              = 7,200/7,200 PASS
failed partitions                       = 0
duplicate target-family rows            = 0
early-close TARGET identities           = 27/27
schema variants                         = 1 per family
future_window_used=true                 = 0
source blocks recomputed                = 0
canonical promotion                     = false
```

The recovery certified the immutable outputs already produced by the historical
Stage-8 calculation. It did not recalculate features, overwrite partitions or
relabel the historical failed wrapper.

## 2. Frozen execution identity

| Artifact | SHA-256 |
|---|---|
| authorized FULL plan v0.3 | `13c5fcee1b4367ca9aecabc91503cbbedc4e45f901ed7dbaddc2d8897080592c` |
| runner | `d9596b152c30ba8c64ab3b4b957a06d54ab099ff38ccbf139f110002d8f2e20d` |
| cardinality contract | `69293ee4b95e7873d4c37dd7b84220ecc18df24c6e4f442c52b5fe8fb3f331a4` |
| terminal final manifest | `421c5728cd9dd54195e7993258636884ffb6c887ab543d36d924579cab424956` |

```text
run_id:
ta3_stage8_target_only_full_recovery_v0_3_20260814

run_root:
C:/TSIS_Data/runtime/trading_activity_stage8_target_only_full_recovery_v0_3_20260814

started_at_utc:   2026-08-14T11:23:57.525806+00:00
completed_at_utc: 2026-08-14T11:32:49.804192+00:00
elapsed_seconds:  532.3
```

## 3. Exact certified cardinality

| Domain | Expected | Actual | Verdict |
|---|---:|---:|---|
| TARGET sessions | 2,400 | 2,400 | PASS |
| family partitions | 7,200 | 7,200 | PASS |
| current-state rows | 279,330,000 | 279,330,000 | PASS |
| multiscale-contrast rows | 111,732,000 | 111,732,000 | PASS |
| PIT-baseline-and-surprise rows | 837,990,000 | 837,990,000 | PASS |
| early-close TARGET sessions | 27 | 27 | PASS |

Each family has exactly 2,400 reference-manifest rows. The exact target key is:

```text
(block_id, instrument_id, ticker, session_date)
```

The reference manifest contains 2,400 unique target keys, three families per
key and no duplicate target-family row.

## 4. Hash-bound output artifacts

| Artifact | Rows | SHA-256 | Audit |
|---|---:|---|---|
| `target_partition_inventory.parquet` | 7,200 | `5ebd6aa877e55f6e171c75c64916a618e427e6ddca4f107dec8ab2f27b8026ba` | MATCH |
| `target_partition_inventory_summary.json` | n/a | `8a7081f2f1b4e69b21b9bac37780574ec834120b52ff7f8de8ede0a6a238fe2b` | MATCH |
| `partition_verification.jsonl` | 7,200 | `faa681c97d7263f38e652580874ebe3dd4657e6790b3088fae6f49851a62e73f` | MATCH |
| `verified_reference_manifest.parquet` | 7,200 | `952583f357e2808fb5df563cb75432c3d46b41aced55f8ad340e2abb1f319527` | MATCH |

All 7,200 verification records are `PASS`. The final manifest binds inherited
block validators to each selected source-file SHA-256.

## 5. Schema and leakage audit

| Family | Schema SHA-256 | Variants |
|---|---|---:|
| `current_state` | `ce6f4a13101412ad1aa180df4907a2925728d82505c6ebcae50ff141d7c5e1c5` | 1 |
| `multiscale_contrast` | `dec1714c5f958743e1aab8c784aa3f429f5771bd1ab04676e7472c6b5c06c40c` | 1 |
| `pit_baseline_and_surprise` | `00e546c9b555412f0b7bed28abe66ec59f940ce033900063048ba74ae419ef00` | 1 |

```text
future_window_used=true across verification records = 0
validation inheritance = BLOCK_VALIDATORS_BOUND_BY_SELECTED_FILE_SHA256
```

## 6. Incident-control disposition

`RM-MAT-CTRL-001..005` are `PASS` in the FULL runtime evidence. Therefore
the full-denominator and terminal-certification terms of incidents 001..005 are
satisfied.

The incidents are not yet `CLOSED_VERIFIED`. The governing closure formula
also requires proof that the next applicable model plan imports each applicable
control. Current disposition:

```text
RM-MAT-INC-001..005
= FULL_TERMINAL_VERIFIED_LATER_PLAN_IMPORT_PENDING
```

## 7. Scientific and promotion boundary

This readout certifies physical integrity and exact target-only cardinality. It
does not by itself decide that Binding A is scientifically sufficient, beat a
candidate Binding B, pass temporal OOS or become canonical.

```text
Binding A physical evidence package = READY_FOR_EVIDENCE_VERDICT
Binding B                           = NOT_AUTHORIZED
candidate comparison               = NOT_STARTED
temporal OOS                        = NOT_AUTHORIZED
canonical representation           = NOT_AUTHORIZED
```

The next governed step is a separate Binding A evidence verdict, followed by a
Binding B plan that explicitly imports the applicable incident controls before
implementation, all-shard probes or any long materialization.
