# Trading Activity Binding A v0.2 Early Output Audit

## Control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_v0_2_early_output_audit` |
| `document_version` | `v0_1` |
| `status` | `PASS_AFTER_REQUIRED_CORRECTION` |
| `audit_date` | `2026-08-10` |
| `binding_id` | `trading_activity_binding_a_candidate_v0_2` |

## Initial broad-run finding

The first closed partitions were audited before allowing broad execution to
continue. Current-state schemas and ordinary calculated rows were conformant,
but the first 405 opening-window rows per session exposed a semantic defect:

```text
calculation_state = INSUFFICIENT_WINDOW_HISTORY
observation_state = OBSERVED_NONZERO (in some rows)
eligible features = NULL
input_event_count = 0
```

The zero incorrectly asserted that no input events had been observed. The broad
controller and workers were stopped before model comparison or promotion.

## Correction

The kernel now distinguishes:

```text
coverage failure / degraded window
-> input_event_count = NULL

incomplete opening window
-> calculated features = NULL
-> input_event_count = count of partially observed eligible inputs
-> feature_input_max_available_at preserved when inputs exist

complete observed zero-activity window
-> input_event_count = 0
```

## Validation

```text
focused tests = 26 PASS
production-equivalent probes = 4 shards COMPLETE
```

Per-shard output volumes:

| Shard | Current state | Multiscale | Baseline/surprise |
|---:|---:|---:|---:|
| 0 | 39,000 | 15,600 | 9,000 |
| 1 | 39,300 | 15,720 | 9,900 |
| 2 | 39,000 | 15,600 | 9,000 |
| 3 | 39,000 | 15,600 | 9,000 |

Validated invariants:

```text
one schema variant per dataset across all shards
five current-state windows present
two registered multiscale pairs present
duration-compression column present
no duplicate physical keys
future_window_used = false
opening-window feature NULL semantics = PASS
opening-window input evidence semantics = PASS
calculated input_event_count = eligible_trade_count
feature_input_max_available_at causal and preserved
multiscale formula recomputation = PASS on early broad output
```

## Verdict

```text
EARLY OUTPUT GATE = PASS_AFTER_REQUIRED_CORRECTION
BROAD RUN RESUME FROM INVALID OUTPUTS = PROHIBITED
BROAD RUN RESTART WITH NEW RUN IDs = AUTHORIZED
CANONICAL PROMOTION = NOT_AUTHORIZED
```
