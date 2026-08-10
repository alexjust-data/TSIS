# TRADING ACTIVITY BINDING A v0.2 FOUR-SHARD PROBE CERTIFICATION READOUT v0.1

## Control

```text
document_status = EXECUTED
certification_status = PASS
scope = FOUR_SHARD_BOUNDED_PRODUCTION_EQUIVALENT_PROBES
broad_materialization = AUTHORIZED_BY_HUMAN_AFTER_GATE_PASS
canonical_promotion = NOT_AUTHORIZED
date = 2026-08-10
```

## Decision

The rejected `20260808` broad run must not be resumed or consumed. Binding A
was refactored as a single v0.2 implementation and must be rebuilt from zero
under new run IDs.

## Corrections implemented

```text
intertrade_duration_compression
typed stable schemas across missingness branches
duplicate_policy_id
coverage_mode
feature_version v0_2
binding_id v0_2
nullable-aware multiscale kernel
```

Duration compression is calculated only when both current and PIT-baseline
median intertrade durations exist. Otherwise it remains typed `NULL` and is
never replaced with zero.

## Gate history

### Cycle 1

```text
FAIL
reason = coverage_mode absent from MULTISCALE_CONTRAST
```

### Cycle 2

```text
FAIL
reason = Arrow inferred null types for all-null columns in some shards
```

### Cycle 3

```text
PASS
current_state schema variants = 1
multiscale_contrast schema variants = 1
pit_baseline_and_surprise schema variants = 1
```

| Shard | Current rows | Multiscale rows | Baseline rows | Non-null duration compression | Result |
|---:|---:|---:|---:|---:|---|
| 0 | 39,000 | 15,600 | 9,000 | 615 | `PASS` |
| 1 | 39,300 | 15,720 | 9,900 | 0 | `PASS` |
| 2 | 39,000 | 15,600 | 9,000 | 0 | `PASS` |
| 3 | 39,000 | 15,600 | 9,000 | 0 | `PASS` |

Zero non-null rows is valid when duration cardinality is insufficient. The gate
verified that the physical column remains present and typed, values remain
`NULL`, and calculation states preserve the reason.

## Validation performed

```text
26 focused unit/integration tests = PASS
four production-equivalent shard probes = COMPLETE
feature and binding identities = v0_2
future_window_used = false
trade_arrival_rate formula = PASS
current-state ranges and missingness = PASS
multiscale formula recomputation = PASS
duration-compression formula recomputation = PASS
duration-compression NULL semantics = PASS
cross-shard names, types and order = PASS
```

Machine-readable evidence:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\test_runs\
trading_activity_binding_a_v0_2_shard_probe_conformance_cycle3_20260810.json

C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\test_runs\
trading_activity_binding_a_v0_2_shard_probe_certification_cycle3_20260810.json
```

Probe runtime authority:

```text
G:\TSIS\data\data_ops_manifests\ta3_ba_v02_probe3
```

## Broad-run authorization

The broad v0.2 run may start from zero with new output/runtime roots and no
resume relationship to the rejected v0.1-compatible run. The established host
capacity limit remains two concurrent workers; four shards may be completed in
two waves unless a new capacity gate authorizes four workers.



