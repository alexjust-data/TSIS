# Trading Activity Binding A independent percentile replay FULL execution readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `INDEPENDENT_PERCENTILE_REPLAY_FULL_EXECUTION_EVIDENCE` |
| `document_status` | `EXECUTED_PASS_EXACT` |
| `run_id` | `trading_activity_binding_a_percentile_replay_full_v0_1_20260814` |
| `mode` | `FULL` |
| `binding` | `trading_activity_binding_a_candidate_v0_2` |
| `scope` | `240_BLOCKS_2400_TARGET_SESSIONS` |
| `created_at` | `2026-08-15` |
| `canonical_promotion` | `NOT_AUTHORIZED` |

## 1. Terminal verdict

```text
status                         = PASS
blocks                         = 240/240
sessions                       = 2,400/2,400
baseline rows checked          = 837,990,000
percentile cells checked       = 3,351,960,000
mismatches                     = 0
exact value match              = true
exact NULL-mask match          = true
checkpoint manifests           = 240
wrapper alive after final      = false
resume required                = false
```

The FULL independent replay closes the remaining percentile-evidence gap for
Binding A. All four materialized PIT percentile variables equal the independent
right-inclusive empirical-rank oracle over the complete frozen TA-3 target
denominator.

## 2. Variables and formula replayed

```text
trade_count_percentile_pit
share_volume_percentile_pit
dollar_volume_percentile_pit
arrival_rate_percentile_pit

replayed = count(reference_value <= current_value) / baseline_total_count
tie policy = RIGHT_INCLUSIVE
interpolation = PROHIBITED
midrank = PROHIBITED
mismatch tolerance = 0
```

The oracle did not import or call the Python, vectorized, adapter or C++
Trading Activity baseline engines.

## 3. Frozen execution identity

```text
started_at_utc   = 2026-08-14T16:51:14.031675+00:00
completed_at_utc = 2026-08-14T21:46:21.778036+00:00
elapsed_seconds  = 17,707.677
elapsed_hours    = 4.918799
rows_per_second  = 47,323.54
cells_per_second = 189,294.17
```

```text
plan SHA-256
= bbb414a44f6eeef80b66bdc4adc7e37ae972ecdb5789bd688094509561e0e515

runner SHA-256
= 024950e7c3fee9007575eb7c3f8d2847c1c478c243c288475c549a351a5fd910

oracle SHA-256
= ccd88a9a9acb25d36fab416388465acd9114a1c096b818e2a003b9af8caab0e7

final manifest SHA-256
= 634e71bccfd10bdc30b82038b9c767e5738b530e94894bc501db579e679fc857
```

Final manifest:

```text
C:/TSIS_Data/runtime/
trading_activity_binding_a_percentile_replay_full_v0_1_20260814/
runtime/final_manifest.json
```

## 4. Scientific interpretation

This result establishes that the four percentile columns in the frozen Binding
A materialization implement the governed empirical-ranking formula exactly for
the entire 240-block / 2,400-session target population. The earlier restriction
was an unclosed evidence gap, not evidence of incorrect percentile values.

The result does not establish that Binding A is the preferred representation.
It does not remove the declared source limitations:

- legacy RTH only;
- simulated rather than historically observed availability;
- first observable RTH transition, not a complete premarket-to-after-hours
  Wake-up episode;
- experimental candidate, not canonical history.

## 5. Gate disposition

```text
Binding A percentile replay restriction = CLOSED_PASS_EXACT
Binding A candidate evidence             = PASS_WITH_SCOPE_RESTRICTIONS
Binding B frozen preregistration         = NEXT_AUTHORIZABLE_GATE
Binding B long materialization           = NOT_AUTHORIZED
temporal OOS                             = NOT_AUTHORIZED
canonical promotion                      = NOT_AUTHORIZED
```

Binding B must import and demonstrate every applicable
`RM-MAT-CTRL-001..006`, pass the variable-by-variable all-shard probe gate and
receive a separate human authorization before any long materialization.
