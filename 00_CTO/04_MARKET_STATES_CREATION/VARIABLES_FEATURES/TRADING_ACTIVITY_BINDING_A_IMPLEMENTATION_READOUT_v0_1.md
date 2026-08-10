# TRADING_ACTIVITY_BINDING_A_IMPLEMENTATION_READOUT_v0_1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_binding_a_implementation_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_BINDING_IMPLEMENTATION_READOUT` |
| `document_status` | `KERNEL_IMPLEMENTED_PHYSICAL_SMOKE_EXECUTED` |
| `binding_id` | `trading_activity_binding_a_minimal_multiscale_rth_v0_2` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `review_verdict` | `PASS_WITH_RESTRICTIONS` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Especificacion gobernante

```text
TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md
```

La v0_2 cierra para el piloto:

```text
decision unit = symbol-second
W = 5s, 15s, 30s, 60s, 300s
full fixed denominators
right-anchored subwindows
typed PIT percentiles
B20 / B60 / B120
primary simulated latency = 1 second
```

---

## 2. Implementacion

Kernel puro:

```text
01_TSIS_DATA_FOUNDATION/scripts/
trading_activity_binding_a_kernel.py
```

Implementa:

```text
absolute activity
event intensity
intertrade durations
largest-trade mark
temporal concentration
minimal consecutive-subwindow corroboration
multiscale activity-rate log ratio
PIT baseline selection
zero-mass-aware baseline summaries
typed empirical percentiles
absolute-to-PIT log ratios
```

Runner fisico de smoke:

```text
01_TSIS_DATA_FOUNDATION/scripts/
run_trading_activity_binding_a_smoke.py
```

El runner consume:

```text
physical legacy trade Parquet
condition policy matrix
market_calendar_v0_1
latency policy id
decision timestamp
```

No consume outcomes, scanner labels ni eventos Wake-up.

---

## 3. Tests

Kernel Binding A:

```text
12 passed
```

Cobertura integrada del tramo:

```text
coverage sidecar                         4
Massive reference snapshots             2
trade eligibility                      17
trade eligibility physical audit        2
Binding A kernel                        12
------------------------------------------
total                                   37 passed
```

Los fixtures cubren:

```text
fixed denominator
left-open and right-closed boundary
simulated-availability tie
no future availability
one-trade insufficient duration
same-timestamp zero duration
observed zero without concentration imputation
unknown-condition degradation
opening insufficient window history
coverage failure
right-anchored subwindows
multiscale contrast
PIT-only prior sessions
zero-dominated baseline
B60 insufficient history
deterministic rebuild
```

---

## 4. Smoke fisico ejecutado

Input:

```text
ticker/session = AAGR / 2023-12-11 RTH
source rows     = 5,130
decision time  = 2023-12-11T18:21:17Z
latency policy = LATENCY_PRIMARY_CONSERVATIVE
latency        = 1,000 ms
calendar       = XNYS market_calendar_v0_1
calendar run   = market_calendar_v0_1_20260630T193931Z
```

Trade eligibility:

```text
ELIGIBLE_WITH_RESTRICTIONS = 5,126
INELIGIBLE                 =     4
UNKNOWN_FAIL_CLOSED        =     0
```

Current-state output:

| W | Trades | Rate trades/s | Median duration us | p10 us | Active subwindows | Max trade share | Max volume share |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `5s` | 33 | 6.6000 | 4 | 0 | 0.2000 | 1.0000 | 1.0000 |
| `15s` | 33 | 2.2000 | 4 | 0 | 0.0667 | 1.0000 | 1.0000 |
| `30s` | 34 | 1.1333 | 4 | 0 | 0.0667 | 0.9706 | 0.9986 |
| `60s` | 34 | 0.5667 | 4 | 0 | 0.1667 | 0.9706 | 0.9986 |
| `300s` | 38 | 0.1267 | 5 | 0 | 0.0833 | 0.8684 | 0.9960 |

La concentracion observada es coherente con un burst muy comprimido: en 5 y
15 segundos, los 33 trades elegibles caen en una sola subventana activa.

---

## 5. Lineage del smoke

```text
tests/test_runs/
trading_activity_binding_a_smoke_20260806T224000Z/
```

Source Parquet SHA256:

```text
b8e8bf6483e68d5b7716b3c77c82ed509132135172e399905fdbdeaa69a9cffc
```

Condition matrix SHA256:

```text
b2f208496809cb970437d04024d93bfb98780b54b5d790091362aa145eb9635f
```

Market calendar SHA256:

```text
cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c
```

Current-state output SHA256:

```text
424e9299c33e343a076c1fa338f0383e86d41c53bddd0eef8fb1c358c3890ae1
```

---

## 6. Estado exacto

```text
BINDING A EXACT SPECIFICATION
= FROZEN_FOR_DETERMINISTIC_PILOT

CURRENT-STATE COMPUTATIONAL KERNEL
= IMPLEMENTED_AND_TESTED

PIT BASELINE COMPUTATIONAL KERNEL
= IMPLEMENTED_AND_TESTED_WITH_SYNTHETIC_FIXTURES

SINGLE-PARTITION PHYSICAL SMOKE
= PASS

FULL DETERMINISTIC SYMBOL-SECOND PILOT
= NOT_STARTED

PHYSICAL MULTISESSION PIT BASELINE
= NOT_EXECUTED

STRATIFIED OR OOS COMPARISON
= NOT_AUTHORIZED

TABLE MAPPING
= NOT_STARTED

WAKE-UP DETECTOR
= NOT_STARTED

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

---

## 7. Siguiente paso

El siguiente paso ya no es definir mas variables. Es preparar una
materializacion piloto multisesion gobernada con:

```text
pre-manifest
run id
bounded symbol/session scope
PID and heartbeat
live log
final manifest
output-size estimate
restart policy
```

Ese run debe producir `CURRENT_STATE` y `PIT_BASELINE_AND_SURPRISE` como
artefactos experimentales separados. Debido a la unidad `symbol-second`, no se
debe lanzar como comando ad hoc sin cumplir `LONG_RUNNING_OPERATIONS_CONTRACT`.
