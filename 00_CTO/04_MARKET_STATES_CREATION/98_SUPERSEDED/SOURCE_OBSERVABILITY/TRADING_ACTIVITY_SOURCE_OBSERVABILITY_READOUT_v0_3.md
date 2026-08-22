# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_3

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_source_observability_readout` |
| `document_version` | `v0_3` |
| `document_role` | `SOURCE_OBSERVABILITY_EXECUTION_READOUT` |
| `document_status` | `EXECUTED_DETERMINISTIC_PILOT` |
| `review_verdict` | `PASS_WITH_RESTRICTIONS_FOR_DETERMINISTIC_PILOT` |
| `current_legacy_source_gate` | `PASS_WITH_RESTRICTIONS_FOR_DETERMINISTIC_PILOT` |
| `full_legacy_source_gate` | `IN_PROGRESS` |
| `full_wake_up_source_gate` | `PENDING_MASSIVE_BACKFILL_AND_LIVE_CAPTURE` |
| `binding_a_code_scaffolding` | `AUTHORIZED` |
| `binding_a_deterministic_pilot_execution` | `AUTHORIZED` |
| `binding_a_stratified_oos_execution` | `NOT_AUTHORIZED` |
| `freeze_status` | `NOT_READY_FOR_FREEZE` |
| `canonical_feature_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_2.md` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Scope admitido

```text
LEGACY RTH RECONCILED EVENT-TIME RESEARCH-ONLY
```

Semantica permitida:

```text
first observable transition during RTH
```

Semantica prohibida:

```text
first Wake-up of the complete episode
revision-aware historical detection
measured historical available_at
premarket or after-hours episode onset
```

---

## 2. Rectificacion contractual aplicada

La autoridad de alineacion es:

```text
TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md
```

Modelo gobernante:

```text
ABSOLUTE-AND-PIT-RELATIVE
MULTISCALE MARKED ACTIVITY PROCESS
```

Dimension gobernante:

```text
TRANSITION DYNAMICS
AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

La inconsistencia estaba entre artefactos Wake-up, principalmente
`00_WAKE_UP_END_to_END.md` y `REPRESENTATION_MODELS.md`; no en
`00_TABLES_MARKET_STATE_EVENT_STATE.md`.

---

## 3. Evidencia cerrada en este ciclo

### 3.1 Coverage sidecar

```text
100 tareas deterministas
83 DOWNLOADED_OK
17 DOWNLOADED_EMPTY
100 PASS_WITH_RESTRICTIONS
```

Las 83 particiones presentes superaron:

```text
physical path exists
Parquet readable
required schema present
physical row count equals acquisition row count
audited downloader identity matches
```

La evidencia de paginacion procede del flujo terminal del downloader auditado,
no de un `page_count` inexistente en los manifests.

### 3.2 Reference snapshots

```text
Massive trade condition codes = 55
Massive stock exchanges       = 27
```

Los snapshots estan versionados, hasheados y no persisten la API key.

### 3.3 Trade eligibility

```text
candidate-reviewed condition IDs = 14
known but unreviewed IDs          = 41
pilot trades evaluated            = 23,855
activity eligible                 = 23,604
activity ineligible               = 251
unknown fail-closed               = 0
exact duplicate flags             = 98
```

La matriz separa:

```text
provider volume-update rule
from
causal activity eligibility
```

### 3.4 Tests

```text
25 passed
```

---

## 4. Hard-gate readout actual

| Gate | Estado | Alcance |
|---|---|---|
| Required trade facts | `PASS_WITH_RESTRICTIONS` | Precio, tamano, exchange y conditions presentes. |
| Timestamp semantics | `PASS_WITH_RESTRICTIONS` | Timestamp colapsado `SIP OR participant OR TRF`; timezone eliminado. |
| Availability | `SIMULATABLE_NOT_MEASURED` | Registry de latencia simulado, no latencia historica real. |
| Ordering | `PARTIAL` | Orden estable por timestamp; sin sequence number. |
| Revisions | `NOT_OBSERVABLE` | Vista reconciliada final. |
| Coverage | `PASS_WITH_RESTRICTIONS_FOR_PILOT` | 100 tareas, no full universe. |
| Empty-day semantics | `PASS_WITH_RESTRICTIONS_FOR_PILOT` | 17 `DOWNLOADED_EMPTY` gobernados. |
| Condition semantics | `PASS_WITH_RESTRICTIONS_FOR_OBSERVED_PILOT_CODES` | 14/14 observados resueltos; 41 fail-closed. |
| Exchange semantics | `PASS_WITH_RESTRICTIONS` | Todos los IDs piloto cubiertos por snapshot actual. |
| Duplicate policy | `PASS` | Se preservan; solo se emite research flag. |
| Baseline policy | `CANDIDATE_FROZEN` | Cardinalidades y zero-mass fijados por rectificacion. |
| Latency policy | `CANDIDATE_FROZEN` | 100 ms, 1 s y 5 s como escenarios simulados. |
| Reproducibility | `PASS_FOR_PILOT` | Inputs, scripts, outputs y hashes versionados. |

---

## 5. Autorizacion normalizada

```text
DOCUMENT AUTHORING
= COMPLETE_AS_EXECUTED_PILOT_READOUT

BINDING A CODE SCAFFOLDING
= AUTHORIZED

BINDING A EXECUTION ON THIS DETERMINISTIC PILOT
= AUTHORIZED

BINDING A STRATIFIED DEVELOPMENT EXECUTION
= PENDING STRATIFIED SOURCE-GATE EXPANSION

BINDING A OOS COMPARISON
= NOT_AUTHORIZED

CANONICAL IMPLEMENTATION
= NOT_AUTHORIZED
```

---

## 6. Lo que sigue pendiente de Massive

```text
premarket and after-hours historical coverage
provider trade identity
sequence number
participant timestamp
SIP timestamp as separate field
TRF timestamp and identity
correction indicator
revision linkage when provided
tape and enriched metadata
```

El backfill no invalida el trabajo RTH. Activa:

```text
REQUIRES_REVALIDATION
REBUILD_NEW_DATASET_VERSION
FEATURE_VERSION_REVIEW
```

Nunca una sustitucion silenciosa.

---

## 7. Siguiente paso autorizado

El siguiente artefacto ejecutable es el builder piloto de Binding A para:

```text
ABSOLUTE ACTIVITY
EVENT INTENSITY
BASIC MARKS
BASIC TEMPORAL CONCENTRATION
PIT-RELATIVE SURPRISE
TRANSITION AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

Debe consumir exclusivamente:

```text
coverage sidecar rows with PASS_WITH_RESTRICTIONS
trade eligibility policy v0_2
latency policy registry v0_1
baseline policy candidate
```

Sus outputs seguiran siendo:

```text
EXPERIMENTAL PHYSICAL BINDING
NOT CANONICAL FEATURES
NOT WAKE_UP DETECTOR
```
