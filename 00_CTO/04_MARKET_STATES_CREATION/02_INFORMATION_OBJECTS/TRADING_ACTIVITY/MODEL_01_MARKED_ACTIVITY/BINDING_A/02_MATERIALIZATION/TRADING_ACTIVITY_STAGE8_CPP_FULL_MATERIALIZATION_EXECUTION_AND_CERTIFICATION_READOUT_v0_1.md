# Trading Activity Stage-8 C++ full materialization execution and certification readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_stage8_cpp_full_materialization_execution_and_certification_readout` |
| `document_version` | `v0_1` |
| `document_role` | `FULL_MATERIALIZATION_EXECUTION_EVIDENCE_AND_FAILED_CERTIFICATION_READOUT` |
| `document_status` | `EXECUTED_FAILED_NOT_PROMOTED` |
| `snapshot_at` | `2026-08-14` |
| `run_id` | `trading_activity_ta3_cpp_full_v0_1_20260811` |
| `physical_run_id` | `ta3_cpp_v0_1_20260811` |
| `physical_execution` | `COMPLETE_4_OF_4_SHARDS_240_OF_240_BLOCKS` |
| `aggregate_certification` | `FAILED` |
| `data_loss_verdict` | `NO_LOSS_DETECTED_BY_DOCUMENTED_LIGHTWEIGHT_AUDIT` |
| `full_rematerialization_required` | `false` |
| `target_only_recovery` | `REQUIRED_NOT_EXECUTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |

## 1. Decision

The expensive C++ calculation completed for all four shards and all 240 frozen
TA-3 blocks. The governed wrapper then failed during the first aggregate
certification gate. Therefore:

```text
physical calculation complete  != certified run PASS
240/240 completed blocks        != canonical promotion
aggregate certification FAILED  != loss of every computed block
```

The original run is preserved as `FAILED_NOT_PROMOTED`. It must not be
rewritten, relabelled `PASS`, deleted or launched again merely to repair the
final certification contract.

The next governed action is a separately versioned target-only recovery and
recertification over the already materialized partitions. Recalculation of the
240 Stage-8 blocks is not currently justified.

## 2. Frozen identity and governed roots

```text
logical run id
= trading_activity_ta3_cpp_full_v0_1_20260811

run root
= D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811

outputs
= <run root>/outputs

runtime
= <run root>/runtime

recovery runtime
= <run root>/runtime/recovery

plan
= C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/VARIABLES_FEATURES/
  TRADING_ACTIVITY_STAGE8_CPP_FULL_MATERIALIZATION_PLAN_v0_1.json
```

Frozen execution identity:

```text
plan SHA-256
= 2e7e4be33237cd1836cfe6ecf1c6ad5ca227b284a9152c87ca6dbddbebdaf5a5

original runner SHA-256
= 338fe64807ceb817867ea07504a78b58d1ed333d39c89ac9ccaf8fb11bf92034

engine fingerprint SHA-256
= 7d24178a5b475c36401b4321af95630550185e5ea227dfe3419f08398bb54a0a

C++ source SHA-256
= 0d62f8ae9c63d59e52b0360b0fec514c8f5afdc19fe7e98f1622a80f772d7848

native binary SHA-256
= 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
```

Python remains the semantic oracle. This readout changes no feature formula,
schema, source policy, PIT rule, lineage identity or promotion status.

## 3. Execution closure

The recovery supervisor reached:

```text
finished_at_utc = 2026-08-13T22:48:06.512394+00:00
elapsed_seconds = 60,028.137198599994
wrapper_exit_code = 1
```

Shard result:

| Shard | Parent run | Blocks | Final state |
|---:|---|---:|---|
| 0 | `ta3c1_s0` | 60/60 | `COMPLETE`, reused as `SKIPPED_COMPLETE` |
| 1 | `ta3c1_s1` | 60/60 | `COMPLETE`, reused as `SKIPPED_COMPLETE` |
| 2 | `ta3c1_s2` | 60/60 | `COMPLETE`, reused as `SKIPPED_COMPLETE` |
| 3 | `ta3c1_s3` | 60/60 | `COMPLETE`, resumed and finished |

Aggregate execution evidence:

```text
parent shards COMPLETE             = 4 / 4
declared blocks                    = 240
unique block IDs                   = 240
block final manifests COMPLETE     = 240 / 240
run summaries PASS                 = 240 / 240
C++ engine fingerprint exact       = 240 / 240
completed-block warnings           = 0
missing output roots               = 0
missing required metadata files    = 0
```

## 4. Exact certification failure

The terminal manifest records:

```text
status = FAILED
stage  = CERTIFY_240_BLOCKS

failure_reason
= AssertionError: Row count mismatch:
  .../outputs/run_id=ta3c1_s0__3244b2db5e3f87198bd321417948efea/
  metadata/run_summary.json
```

The failure occurred after the last block finished, before creation of
`full_materialization_certification.json` and before the full schema
conformance auditor ran.

### 4.1 Immediate gate defect

The aggregate certifier compared the complete `row_counts` dictionary against
the complete `expected_row_counts` dictionary.

All 240 summaries have this shape:

```text
row_counts
= current_state_rows
  multiscale_rows
  baseline_rows

expected_row_counts
= decision_seconds_total
  current_state_rows
  multiscale_rows
  baseline_rows
```

The three materialized-family values match their corresponding expected values
in every block, but dictionary equality is false because
`decision_seconds_total` is expected metadata and is not a materialized output
row family.

```text
three materialized family counts exact = 240 / 240
strict full-dictionary equality         = 0 / 240
```

### 4.2 Scope expansion relative to the TA-3 target denominator

The frozen sample contains:

```text
blocks                  = 240
explicit target sessions = 2,400
scope sessions           = 32,013
```

The block configuration stores the first and last target dates as an interval.
The multisession runner consequently materialized current-state and multiscale
families for the complete work scope, including warm-up and intervening
non-target sessions. For PIT baseline it evaluated every governed session
between the first and last target dates, not only rows marked `TARGET`.

This produced useful research evidence, but it is not the exact target-only
denominator preregistered for the TA-3 development comparison.

### 4.3 Preregistered count defects

The preregistered aggregate counts also have two independent defects:

1. target source rows used full session seconds while the runner implements
   `OPEN_EXCLUSIVE_CLOSE_EXCLUSIVE`, so each session produces one fewer decision
   timestamp;
2. `expected_pit_baseline_rows` accounted for the three baseline candidates but
   omitted the five `window_seconds` variants present in the baseline grain.

The original JSON plan is immutable historical evidence. These findings must
not be repaired by editing it in place.

## 5. Observed and target-only counts

### 5.1 Complete physical output currently stored

| Family | Physical rows across 240 blocks |
|---|---:|
| `current_state` | 3,729,376,935 |
| `multiscale_contrast` | 1,491,750,774 |
| `pit_baseline_and_surprise` | 1,121,882,805 |
| **Total feature rows** | **6,343,010,514** |

These are physical scope totals, not a corrected replacement for the frozen
TA-3 target denominator.

### 5.2 Exact recoverable 2,400-target subset

| Family | Original plan | Correct target-only count | Difference/cause |
|---|---:|---:|---|
| `current_state` | 279,342,000 | 279,330,000 | 2,400 sessions x 5 windows x one excluded closing second |
| `multiscale_contrast` | 111,736,800 | 111,732,000 | 2,400 sessions x 2 pairs x one excluded closing second |
| `pit_baseline_and_surprise` | 167,605,200 | 837,990,000 | five windows were omitted; closing second is excluded |
| **Total** | **558,684,000** | **1,229,052,000** | corrected physical grain |

For every target session the corrected formulas are:

```text
decision_points = source_session_seconds - 1

current_state_rows
= decision_points * 5 windows

multiscale_rows
= decision_points * 2 short/long pairs

pit_baseline_rows
= decision_points * 5 windows * 3 baseline candidates
```

## 6. Recoverability audit performed on 2026-08-14

A read-only audit over all parent, block, metadata and validation manifests
reported:

```text
row-count validations PASS              = 240 / 240
grain-uniqueness validations PASS       = 240 / 240
temporal-legality validations PASS      = 240 / 240
baseline-reference validations PASS     = 240 / 240
lineage future_window_used=false         = 240 / 240
schema manifests present                = 240 / 240
schema variants per output family       = 1 / 1 / 1
output-hash index sidecars self-consistent = 240 / 240
```

The 240 hash indices contain:

```text
indexed output files = 67,719
indexed bytes        = 28,218,488,947
indexed GiB          = 26.281
missing files        = 0
size mismatches      = 0
```

The exact frozen target join reported:

```text
target sessions                             = 2,400
current-state target partitions present     = 2,400 / 2,400
multiscale target partitions present        = 2,400 / 2,400
PIT-baseline target partitions present      = 2,400 / 2,400
target partitions matching corrected grain  = 7,200 / 7,200
```

This was a lightweight recovery audit. It verified recorded SHA-index
sidecars, path presence, file sizes, validation manifests and exact target row
counts. It did not recompute the SHA-256 of every indexed Parquet byte. The
target-only recertification must perform that stronger check for its selected
scope.

## 7. Manifest evidence

| Artifact | SHA-256 |
|---|---|
| original pre-manifest | `5b1801753e8ad04a951f7541ed997413ff855fccf11a211ea2948cf5b0099106` |
| recovery pre-manifest | `a87bab953e13a50128b42e39248633a1cf7d69eb7c780af49f8bebc811b910c2` |
| recovery final manifest | `c8e9730f4a2ea936069171cc2a1ef99efe39403c47f5b01e0d9ac56c97901b9d` |
| shard 0 final manifest | `4bcffa4e7c016b16e2d277a00bae490bd7c7d1689ed6f68de8732a87de84be6d` |
| shard 1 final manifest | `c04c8a7e2f33f95bd5caeceef81eadcae6e92d704e7b5d3561bba52b0da2572f` |
| shard 2 final manifest | `a4e4efe62a6cedbdc61895c667653a74c538cc42dfc8537a5b6f3dcb5322830d` |
| shard 3 final manifest | `f7cea3f8a8f2467417f814b6b673670145c31fc24e81582f7a2acf46c442b0db` |

Primary terminal authority:

```text
D:/TSIS/IO/wu/ta/pmma/ba02/runs/run_id=ta3_cpp_v0_1_20260811/
runtime/recovery/final_manifest.json
```

## 8. Governed verdict

```text
expensive C++ computation       = COMPLETE
full physical run certification = FAILED
source outputs                  = PRESERVE_IMMUTABLY
full 240-block relaunch         = PROHIBITED_WITHOUT_NEW_EVIDENCE_AND_AUTHORIZATION
target-only recovery            = PREPARE_SEPARATELY
Binding B                       = BLOCKED
OOS access                      = NOT_AUTHORIZED
Representation Model admission = NOT_AUTHORIZED
canonical promotion             = NOT_AUTHORIZED
```

The governing next plan is:

```text
TRADING_ACTIVITY_STAGE8_TARGET_ONLY_RECOVERY_AND_RECERTIFICATION_PLAN_v0_1.md
```

