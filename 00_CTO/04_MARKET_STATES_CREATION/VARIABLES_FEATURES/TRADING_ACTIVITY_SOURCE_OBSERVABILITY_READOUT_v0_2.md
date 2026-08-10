# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_2

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_id` | `trading_activity_source_observability_readout` |
| `document_version` | `v0_2` |
| `document_role` | `SOURCE_OBSERVABILITY_AUDIT_READOUT` |
| `document_status` | `EXECUTION_IN_PROGRESS` |
| `supersedes_status_clauses` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md` |
| `inherited_physical_evidence` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_1.md` |
| `governing_amendment` | `TRADING_ACTIVITY_CONTRACT_RECTIFICATION_AND_ALIGNMENT_v0_1.md` |
| `audit_contract` | `TRADING_ACTIVITY_AUDIT_CONTRACT_v0_2.md` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `current_legacy_source_gate` | `IN_PROGRESS` |
| `target_enriched_source_gate` | `DEFERRED_PENDING_MASSIVE_BACKFILL` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-06` |
| `owner` | `TBD` |

---

## 1. Alcance de esta revision

La evidencia fisica, los requisitos `TA-SO-001 ... TA-SO-028` y los tests
`TA-ST-001 ... TA-ST-015` permanecen en `v0_1` y no se reinterpretan aqui.

Esta version corrige:

```text
nombre del Representation Model
frontera Binding A / Binding B
observation_state versus calculation_state
denominador de trade_arrival_rate
semantica exacta de baseline y percentiles
registro de latencia
nombre del contraste multiescala
estados de autorizacion
```

---

## 2. Modelo gobernante

```text
ABSOLUTE-AND-PIT-RELATIVE
MULTISCALE MARKED ACTIVITY PROCESS

with

TRANSITION DYNAMICS
AND MINIMAL ANTI-ARTIFACT CORROBORATION
```

---

## 3. Bindings provisionales corregidos

| Binding | Estado | Frontera |
|---|---|---|
| `A Minimal Multiscale Activity with Basic Anti-Artifact Structure` | `SPECIFIED_WITH_REQUIRED_REVISIONS_APPLIED` | Minimo semantico y antinartefacto; formulas gobernadas por la enmienda. |
| `B Expanded Marks, Duration Distribution and Concentration Geometry` | `IN_PROGRESS_WITH_MATERIAL_RESTRICTIONS` | Solo dimensiones adicionales a A. |
| `C1 Conditional Duration / ACD` | `DEFERRED_PENDING_ENRICHED_SOURCE_AND_SPEC` | Requiere secuencia, resolucion y cardinalidad validadas. |
| `C2 Hawkes` | `DEFERRED_PENDING_ENRICHED_SOURCE_AND_SPEC` | Requiere integridad temporal superior. |

Ningun binding queda admitido ni congelado.

---

## 4. Artefactos de cierre pendientes

```text
condition-code snapshot
exchange snapshot
Trade Eligibility fixtures and reason codes
RTH coverage sidecar implementation and fixtures
latency registry deterministic tests
baseline cardinality and PIT tests
Binding A formula fixtures
remaining legacy TA-ST closures
```

---

## 5. Autorizacion vigente

```text
DOCUMENT AUTHORING
= COMPLETE_AS_DRAFT

CODE SCAFFOLDING AND DETERMINISTIC FIXTURES
= AUTHORIZED

SOURCE AUDIT EXECUTION
= AUTHORIZED

BINDING A EXPERIMENTAL DATA EXECUTION
= PENDING_LEGACY_SOURCE_GATE_CLOSE

EXPERIMENTAL MATERIALIZATION
= PENDING_LEGACY_SOURCE_GATE_CLOSE

CANONICAL VARIABLES AND TABLES
= NOT_AUTHORIZED

PREDICTIVE CONSUMPTION
= NOT_AUTHORIZED
```

---

## 6. Gate de cierre legacy

Solo puede emitirse:

```text
CURRENT_LEGACY_SOURCE_GATE
= PASS_WITH_RESTRICTIONS
```

cuando existan evidencias ejecutadas y versionadas para:

```text
trade eligibility
condition and exchange semantics
ticker-day acquisition completeness
window coverage inference
zero versus unavailable
latency policy application
timestamp ties and deterministic ordering
schema fingerprints
PIT baseline cardinality
```

En caso contrario el gate permanece `IN_PROGRESS` o pasa a `FAIL`.

---

## 7. Dependencia de Massive

```text
PREMARKET_AND_AFTER_HOURS
= DEFERRED_PENDING_MASSIVE_BACKFILL

FULL_EPISODE_FIRST_WAKE_UP
= NOT_OBSERVABLE_FROM_LEGACY_RTH_ONLY

MASSIVE_FULL_HISTORY_BACKFILL_AUDITED
=> REQUIRES_REVALIDATION
```

El backfill no sustituira silenciosamente las features legacy. Exigira nuevos
source IDs, sidecars, baselines, binding versions y readouts.

---

## 8. Estado

```text
READOUT_STATUS                    = EXECUTION_IN_PROGRESS
INHERITED_TA_SO_CLASSIFICATION    = 28_OF_28
INHERITED_TA_ST_CLASSIFICATION    = 15_OF_15
TA_ST_TESTS_FULLY_CLOSED          = NOT_YET
CURRENT_LEGACY_SOURCE_GATE        = IN_PROGRESS
TARGET_ENRICHED_SOURCE_GATE       = DEFERRED_PENDING_MASSIVE_BACKFILL
BINDING_A_SPECIFICATION           = COMPLETE_AS_DRAFT
BINDING_A_CODE_SCAFFOLDING        = AUTHORIZED
BINDING_A_EXPERIMENTAL_EXECUTION  = PENDING_LEGACY_SOURCE_GATE_CLOSE
READY_FOR_FREEZE                  = NO
CANONICAL_PROMOTION               = NOT_AUTHORIZED
```

