# TRADING_ACTIVITY_PARALLEL_WORKSTREAM_COORDINATION_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_parallel_workstream_coordination` |
| `document_version` | `v0_1` |
| `document_role` | `CROSS_LAYER_WORKSTREAM_COORDINATION` |
| `document_status` | `CURRENT_COORDINATION` |
| `created_at` | `2026-08-07` |

---

## 1. Objective

Keep Trading Activity moving while resolving market-cap and float dependencies
without weakening point-in-time legality.

---

## 2. Parallel lanes

### Lane A: Trading Activity TA-3

Owner intent: `00_CTO/04_MARKET_STATES_CREATION`.

```text
sample design and preregistration
runner generalization
tests and deterministic smoke
capacity planning
```

Blocked only at final sample-manifest freeze and broad materialization until the
PIT selector gate passes.

### Lane B: Population Target PIT

Owner: `01_TSIS_DATA_FOUNDATION`.

```text
recover historical panel
audit shares and prior-close semantics
rebuild session-start panel if necessary
validate and issue selector gate
```

This lane unblocks `<$100M` historical membership and the physical TA-3 sample.

### Lane C: Float Context

Owner: `01_TSIS_DATA_FOUNDATION`.

```text
source inventory
semantic and temporal audit
coverage assessment
event-driven table design
```

This lane does not block Binding A computation. It blocks canonical float
filtering in scanner and operations.

---

## 3. Synchronization gates

```text
P1 POPULATION_TARGET_PIT_SELECTOR_GATE
-> freeze TA-3 sample manifest

P2 TA-3 SAMPLE_MANIFEST_GATE
-> human decision on broad materialization

F1 FLOAT_SOURCE_GATE
-> authorize float_context builder design

F2 FLOAT_CONTEXT_DATASET_GATE
-> authorize scanner/context consumption

TA3 STRATIFIED_DEVELOPMENT_SOURCE_GATE
-> open Binding B implementation
```

---

## 4. Non-blocking work allowed now

```text
TA-3 inventory schema and selector interfaces
instrument-block runner design
sample-manifest validators
lockbox guards
population source recovery
shares semantic audit
float source inventory
tests and synthetic fixtures
```

Prohibited now:

```text
broad TA-3 materialization
float filtering
OOS reads
model admission
canonical promotion
```

---

## 5. Ownership boundary

```text
00_CTO
= meaning, sample design, gate sequence and verdict

01_TSIS_DATA_FOUNDATION
= physical sources, schemas, builders, validators, manifests and datasets

scanner / market-state consumers
= as-of joins under the admitted contracts
```

No lane may silently redefine another lane's dataset or gate.

