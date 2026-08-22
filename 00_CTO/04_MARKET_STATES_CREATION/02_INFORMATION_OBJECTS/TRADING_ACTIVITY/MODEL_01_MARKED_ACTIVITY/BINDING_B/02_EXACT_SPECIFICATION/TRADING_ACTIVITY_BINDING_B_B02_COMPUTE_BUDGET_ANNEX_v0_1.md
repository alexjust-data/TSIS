# Trading Activity Binding B B-02 compute budget annex v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_b02_compute_budget_annex` |
| `document_version` | `v0_1` |
| `document_role` | `B02_MACHINE_BOUND_COMPUTE_BUDGET` |
| `document_status` | `ACCEPTED_FOR_B02_DRAFT_NOT_RUN_AUTHORIZATION` |
| `host_profile` | `TSIS_HARDWARE_OPTIMIZATION_PROMPT_2026-08-15` |
| `human_acceptance_context` | `sigue_y_haz_el_codigo_2026-08-15` |
| `created_at` | `2026-08-15` |

## 1. Scope

This annex closes the static budget part of `B02-D11`. It does not certify
throughput and does not authorize a probe or long run. Measured B-06/B-08
projection remains mandatory.

## 2. Governed host

```text
CPU = Ryzen 7 5800X, 8 cores / 16 threads
RAM = 32 GiB physical
GPU = RTX 4060 8 GiB, not assumed useful for event-state tabular recursion
active compute/output = C: NVMe and D:/TSIS/IO as governed by run config
raw trades = G:/TSIS/data/trades_ticks_prod_2005_2026
```

## 3. Frozen initial limits

```text
initial_maximum_workers             = 2
maximum_process_tree_rss_gib        = 24
minimum_os_monitor_reserve_gib      = 6
maximum_projected_full_wall_hours   = 72
maximum_projected_final_output_gib  = 64
minimum_free_disk_gib               = max(3 * projected_output_gib, 100)
heartbeat_maximum_age_seconds       = 60
atomic_checkpoint_interval_minutes  = 15
```

The first production-equivalent probe must report per-worker peak RSS, CPU,
read/write throughput, output bytes per symbol-second and projected wall time.

## 4. Decision rule

```text
measured projection exceeds any limit
-> B-10 optimization required
-> B-12 remains blocked

projection stays within every limit
-> Python remains preferred
-> no automatic B-12 authorization
```

Native/C++ optimization is allowed only after profiling and exact/tolerance-
bound equivalence to the Python semantic oracle.

## 5. Runtime controls

Every future long path must comply with
`LONG_RUNNING_OPERATIONS_CONTRACT.md`: pre-manifest, PID, heartbeat, live log,
separate monitor, atomic outputs, strict resume identity and final manifest.
Resume must reject changed spec, schema, config, code or source fingerprints.

## 6. Verdict

```text
B02-D11 static compute budget       = RESOLVED_FOR_DRAFT
performance evidence                = PENDING_B06_B08
probe execution                     = NOT_AUTHORIZED
long materialization                = NOT_AUTHORIZED
```

