# TRADING_ACTIVITY_TA3_BINDING_A_ORCHESTRATOR_READOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `TA3_BINDING_A_IMPLEMENTATION_AND_PREFLIGHT_READOUT` |
| `document_status` | `EXECUTED` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `sample_gate` | `PASS_WITH_RESTRICTIONS` |
| `preflight_gate` | `PASS` |
| `bounded_smoke_gate` | `PASS` |
| `broad_execution` | `READY_FOR_HUMAN_LAUNCH` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `executed_at` | `2026-08-07` |

## 1. Frozen input

```text
sample manifest
= sample_manifest_v0_2.json

SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

blocks  = 240
targets = 2,400
scope   = 32,013 instrument-sessions
rows    = 558,684,000 projected Binding A rows
```

The only authorized trade root is:

```text
G:/TSIS/data/trades_ticks_prod_2005_2026
```

Legacy `D:` fallback is prohibited. The 3,221 scope sessions absent from the
official root remain `UNAVAILABLE` in the denominator.

## 2. Implementation

The TA-3 orchestrator preserves the validated single-instrument Binding A
kernel. It maps each frozen block to one isolated subrun and adds:

- hash validation of frozen sample bindings;
- exact block scope and target ranges;
- G-only source enforcement;
- deterministic sharding;
- resumable subruns;
- parent PID, heartbeat JSON/JSONL and per-block logs;
- aggregate terminal manifest.

| Artifact | SHA-256 |
|---|---|
| `run_trading_activity_ta3_binding_a.py` | `36405e819a1fd06f0cccbd29a045bc3c2256ff859d7507ece9e37a3d43088435` |
| `preflight_trading_activity_ta3_binding_a.py` | `5303fac8bda9843eccc4018b97ded7db031d8e95ae1b18c4d553fa27277d1296` |
| `monitor_trading_activity_ta3_binding_a.ps1` | `c17df024d2eda4fc051f4c4fc8a7cded63f99e4647ebe9bd5fa4eb3ec0fa2add` |
| orchestrator tests | `1102026db65bbc437e698b69e1211829868e874a54bba99970d933ef29edd881` |

## 3. Preflight evidence

```text
blocks                         = 240
targets                        = 2,400
scope rows                     = 32,013
available G rows               = 28,792
unavailable G rows             = 3,221
filesystem mismatches          = 0
non-contiguous XNYS blocks     = 0
official-G path violations     = 0
preflight gate                 = PASS
```

Evidence:

```text
G:/TSIS/data/data_ops_manifests/trading_activity_ta3_binding_a/
preflight_v0_1_20260807T220000Z.json

SHA-256
= ce189a4f8557650c8b1ae22aa629feb6feb06410ada82c4bca01f81b4ec67a51
```

## 4. Bounded physical smoke

One complete 130-session block was processed with a two-second decision-grid
limit per session.

```text
scope sessions       = 130
evaluation sessions  = 10
current-state rows   = 1,300 / 1,300
multiscale rows      = 520 / 520
baseline rows        = 300 / 300
subrun status        = COMPLETE
orchestrator status  = COMPLETE
failed blocks        = 0
```

The smoke exercised all ten runner stages and did not modify the Binding A
kernel or formulas.

## 5. Regression and capacity

```text
ruff            = PASS
py_compile      = PASS
pytest          = 13 passed
G free capacity = 182.25 GiB at prelaunch review
```

The previous 22.9-million-row Binding A pilot occupies approximately 0.083
GiB. This supports capacity feasibility, but it is not treated as an exact
compression forecast for the 558.7-million-row TA-3 run.

## 6. Authorization boundary

```text
BROAD TA-3 BINDING A EXECUTION
= READY_FOR_HUMAN_LAUNCH

BINDING A ADMISSION
= NOT DECIDED

BINDING B / OOS / CANONICAL PROMOTION
= NOT AUTHORIZED
```

The broad run must use the frozen sample, four disjoint deterministic shards,
the governed long-running-operation controls and no `D:` fallback.
