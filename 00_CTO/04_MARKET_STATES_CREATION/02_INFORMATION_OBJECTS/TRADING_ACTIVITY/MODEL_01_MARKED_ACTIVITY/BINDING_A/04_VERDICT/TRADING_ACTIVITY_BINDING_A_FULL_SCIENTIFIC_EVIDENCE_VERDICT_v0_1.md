# Trading Activity Binding A full scientific evidence verdict v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `SCIENTIFIC_EVIDENCE_VERDICT` |
| `document_status` | `EXECUTED_PASS_WITH_RESTRICTIONS` |
| `representation_candidate` | `ABSOLUTE_AND_PIT_RELATIVE_MULTISCALE_MARKED_ACTIVITY_PROCESS` |
| `binding_id` | `trading_activity_binding_a_candidate_v0_2` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `verdict` | `PASS_WITH_RESTRICTIONS` |
| `candidate_comparison` | `PERMITTED_TO_BE_PLANNED_NOT_EXECUTED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-14` |

## 1. Decision

Binding A passes the bounded scientific evidence gate for continued candidate
comparison inside its declared legacy-RTH research scope.

```text
technical terminal certification       = PASS
value-level evidence audit              = PASS_WITH_DECLARED_RESTRICTIONS
current_state family                    = PASS
multiscale_contrast family              = PASS
pit_baseline_and_surprise family        = PASS_WITH_PERCENTILE_REPLAY_RESTRICTION
hard failures                           = 0
Binding B long materialization          = NOT_AUTHORIZED
temporal OOS                            = NOT_AUTHORIZED
canonical promotion                     = NOT_AUTHORIZED
```

This is not a claim that Binding A is the preferred representation. It means
that it is sufficiently specified, physically coherent and causally bounded
to remain a valid experimental candidate against a separately preregistered
Binding B.

## 2. Authorities and frozen evidence

The audit is governed by:

- `TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md`;
- `TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md`;
- `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md`;
- `TRADING_ACTIVITY_TEMPORAL_AND_MISSINGNESS_CONTRACT_v0_1.md`;
- `TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1.md`;
- `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_5.md`.

Certified source run:

```text
run_id = ta3_stage8_target_only_full_recovery_v0_3_20260814
final_manifest_sha256 = 421c5728cd9dd54195e7993258636884ffb6c887ab543d36d924579cab424956
verified_reference_manifest_sha256 = 952583f357e2808fb5df563cb75432c3d46b41aced55f8ad340e2abb1f319527
target_contexts_sha256 = 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220
```

Evidence audit:

```text
run_id = trading_activity_binding_a_full_evidence_audit_v0_1_rerun3_20260814
auditor_sha256 = c984a2259e8ccdc21924f4001f2c241393fe57af3389dd22178a632567e21925
binding_a_specification_sha256 = e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19
status = PASS_WITH_DECLARED_RESTRICTIONS
selected sessions = 20
early-close sessions = 4
hard failures = 0
```

Runtime root:

```text
C:/TSIS_Data/runtime/trading_activity_binding_a_full_evidence_audit_v0_1_rerun3_20260814
```

## 3. Audit design

The certified 2,400 TARGET sessions contain exactly 150 sessions in every
combination of four logical shards and four frozen cohorts. The auditor chose
one deterministic sentinel from each of the 16 combinations and added one
early-close sentinel per shard, for 20 complete sessions.

Every row of all three families was read for each selected session. The audit
did not rematerialize features and did not access the network.

| Family | Sampled rows | Check types | Failures |
|---|---:|---:|---:|
| `current_state` | 2,123,900 | 31 | 0 |
| `multiscale_contrast` | 849,560 | 16 | 0 |
| `pit_baseline_and_surprise` | 6,371,700 | 32 | 0 |

The full certified inventory was also checked for 2,400 files per family,
exact row counts, `PASS` status and one schema per family.

## 4. Family 1 — current state

### 4.1 Variables audited

| Variable | Evidence | Verdict |
|---|---|---|
| `eligible_trade_count` | nonnegative domain, zero/missingness states, fixed grain | PASS |
| `eligible_share_volume` | nonnegative domain, observed-zero semantics | PASS |
| `eligible_dollar_volume` | nonnegative domain, observed-zero semantics | PASS |
| `trade_arrival_rate` | exact `eligible_trade_count / window_seconds` replay | PASS |
| `median_intertrade_duration_us` | nonnegative, typed insufficient-sample NULL | PASS |
| `p10_intertrade_duration_us` | nonnegative and never above median | PASS |
| `largest_trade_volume_share` | closed unit interval when calculable | PASS |
| `active_subwindow_fraction` | closed unit interval when calculable | PASS |
| `max_subwindow_trade_share` | closed unit interval when calculable | PASS |
| `max_subwindow_volume_share` | closed unit interval when calculable | PASS |
| `consecutive_active_subwindows` | nonnegative and bounded by `W / w` | PASS |

The exact window contract passed:

```text
W = 5, 15, 30, 60, 300 seconds
W <= 30 seconds -> subwindow = 1 second
W > 30 seconds  -> subwindow = 5 seconds
```

Observed state totals demonstrate that missingness was not collapsed to zero:

```text
CALCULATED                              1,649,440
INSUFFICIENT_WINDOW_HISTORY                6,480
NOT_CALCULATED_COVERAGE_GATE_FAILED      467,980
OBSERVED_ZERO                          1,526,883
OBSERVED_NONZERO                         129,037
DEGRADED                                 467,980
```

All sampled numeric variables had zero non-finite values. Every non-null
`feature_input_max_available_at` was at or before its decision timestamp and
`future_window_used` was false throughout.

## 5. Family 2 — multiscale contrast

The only Binding A variable in this family is:

```text
activity_rate_multiscale_log_ratio
```

For all 849,560 sampled rows, the auditor joined the materialized short and
long current-state rates and replayed:

```text
log((short_rate + 1 / long_window_seconds)
    / (long_rate + 1 / long_window_seconds))
```

The exact pair set `(5,60)` and `(15,300)`, null/state behavior, PIT input
timestamp and lineage identity all passed.

```text
CALCULATED             656,640
INPUT_NOT_CALCULATED   192,920
non-finite values            0
```

## 6. Family 3 — PIT baseline and surprise

| Variable | Evidence | Verdict |
|---|---|---|
| four PIT percentiles | typed domain `[0,1]`, availability and state coherence | PASS_WITH_REPLAY_RESTRICTION |
| `trade_count_log_ratio_to_pit` | exact replay from current value and unconditional median | PASS |
| `share_volume_log_ratio_to_pit` | exact replay from current value and unconditional median | PASS |
| `dollar_volume_log_ratio_to_pit` | exact replay from current value and unconditional median | PASS |
| `intertrade_duration_compression` | exact `log((baseline+1)/(current+1))` replay and NULL symmetry | PASS |

The auditor also verified:

- exact candidate IDs `B20`, `B60`, `B120`;
- minimum available-session thresholds 15, 40 and 80;
- `last_reference_date < session_date` whenever present;
- baseline input availability no later than the decision timestamp;
- `total_count = zero_count + positive_count` for all four distributions;
- exact zero-fraction formula for all four distributions;
- stable identity, missingness and future-window metadata.

Observed baseline states were:

```text
BASELINE_AVAILABLE               779,994
BASELINE_ZERO_DOMINATED        4,870,404
BASELINE_INSUFFICIENT_HISTORY    721,302
```

The four materialized percentile values were audited for domain, typed
missingness and baseline-state coherence. This bounded auditor did not replay
their exact empirical ranks from raw baseline observation vectors because
those vectors are not carried in the finalized target partitions. Their
formula is covered by the governed kernel tests, but independent raw replay is
reserved as an explicit later evidence item.

## 7. Audit-tool incident preserved

Two non-scientific failed attempts are retained rather than hidden:

1. the initial attempt stopped before the first target because dataset-style
   Parquet discovery tried to merge a Hive `ticker=` partition dictionary with
   the physical string column; the reader was corrected to `ParquetFile`;
2. `rerun1` incorrectly required one-second subwindows for all windows and
   reported 849,560 false failures; the exact specification was re-read, the
   rule was corrected to 1/5 seconds, and three regression tests passed.

No materialized data changed. `rerun2` repeated the complete frozen sample and
produced zero hard failures. `rerun3` then imported the explicit-file control,
bound the exact specification SHA-256 into the pre/final manifests, repeated
the same complete frozen sample and is the operative result.

## 8. Restrictions and scientific meaning

The verdict remains restricted because:

- the source is legacy RTH only;
- historical availability is simulated, not measured;
- the valid interpretation is the first observable transition during RTH, not
  a complete premarket-to-after-hours Wake-up episode;
- quality labels remain evidence and not universal exclusion rules;
- empirical percentile ranks were not independently replayed from raw baseline
  vectors in this bounded audit.

Therefore:

```text
Binding A may enter governed candidate comparison.
Binding A is not admitted as canonical.
Binding B may be preregistered but not long-materialized.
OOS remains closed.
```

## 9. Next gate

Create the Binding B preregistration and import every applicable
`RM-MAT-CTRL-001..006`. Freeze meaning, formulas, schema, target population,
periods, comparison metrics and false-alarm budget. Then implement tests and
one bounded production-equivalent probe per variable in every planned shard.
A separate human/governed authorization remains mandatory before any long run.
