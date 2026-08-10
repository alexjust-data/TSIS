# TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_4

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_source_observability_readout` |
| `document_version` | `v0_4` |
| `document_role` | `SOURCE_GATE_EXECUTION_READOUT` |
| `document_status` | `EXECUTED` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `full_legacy_source_gate` | `PASS_WITH_RESTRICTIONS` |
| `full_wake_up_source_gate` | `PENDING_MASSIVE_BACKFILL_AND_LIVE_CAPTURE` |
| `binding_a_deterministic_pilot_execution` | `COMPLETE` |
| `binding_a_stratified_development_execution` | `AUTHORIZED` |
| `binding_a_oos_comparison` | `NOT_AUTHORIZED` |
| `freeze_status` | `NOT_READY_FOR_FREEZE` |
| `canonical_feature_promotion` | `NOT_AUTHORIZED` |
| `supersedes` | `TRADING_ACTIVITY_SOURCE_OBSERVABILITY_READOUT_v0_3.md` |
| `created_at` | `2026-08-07` |

---

## 1. Supersession

`v0_4` is the current source-observability readout. It incorporates `v0_3` and
closes the legacy deterministic pilot gate with the evidence from:

```text
TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1.md
```

`v0_3` remains historical evidence for the pre-pilot authorization state.

---

## 2. Executed source evidence

```text
selected RTH sessions
= 130 / 130 observed

acquisition evidence
= 130 / 130 resolved

Foundation evidence
= 130 / 130 joined

local variable-family audits
= 520 / 520 executed

source trade rows
= 14,492

eligible rows
= 14,074

ineligible rows
= 418

unknown fail-closed rows
= 0

exact duplicates preserved and flagged
= 105
```

The source supported all frozen windows, multiscale pairs and PIT baseline
candidates without temporal leakage or silent source exclusion.

---

## 3. Physical-binding evidence

```text
decision symbol-seconds
= 3,020,270

current-state rows
= 15,101,350

multiscale rows
= 6,040,540

baseline rows
= 1,754,925

total rows
= 22,896,815

degraded representation rows
= 0

future-window violations
= 0

available-at violations
= 0

hash failures
= 0
```

The three baselines reached their governed reference-session cardinalities:

```text
B20  = 20
B60  = 60
B120 = 120
```

---

## 4. What this source gate authorizes

```text
LEGACY RTH BINDING A RESEARCH
= AUTHORIZED

PREREGISTERED STRATIFIED DEVELOPMENT SAMPLE
= AUTHORIZED

VARIABLE-FAMILY LOCAL REAUDIT
= REQUIRED

PRESERVATION OF COMPLETE SYMBOL-SECOND DENOMINATOR
= REQUIRED
```

The next sample must include both normal and activation periods. It must not be
selected from scanner winners, known Wake-ups or favorable charts only.

---

## 5. What remains unauthorized

```text
OOS MODEL COMPARISON
= NOT_AUTHORIZED

REPRESENTATION MODEL ADMISSION
= NOT_AUTHORIZED

CANONICAL FEATURE PROMOTION
= NOT_AUTHORIZED

WAKE-UP DETECTOR CALIBRATION
= NOT_AUTHORIZED

PREDICTIVE CONSUMPTION
= NOT_AUTHORIZED

COMPLETE-EPISODE WAKE-UP CLAIM
= NOT_SUPPORTED
```

---

## 6. Restrictions that survive the gate

```text
RTH only
simulated historical latency
no measured historical observed_at or available_at
no complete revision/correction lineage
no premarket or after-hours onset
one-ticker pilot evidence
no universe-wide representativeness
no false-alarm budget
no temporal OOS evidence
```

Massive enriched backfill and prospective live/shadow capture remain mandatory
revalidation triggers. They must produce new dataset and feature versions; they
must not overwrite legacy outputs.

---

## 7. Final source verdict

```text
FULL LEGACY SOURCE GATE
= PASS_WITH_RESTRICTIONS

VALID SEMANTIC INTERPRETATION
= FIRST OBSERVABLE TRANSITION DURING RTH

INVALID SEMANTIC INTERPRETATION
= FIRST WAKE-UP OF THE COMPLETE EPISODE

STRATIFIED DEVELOPMENT EXECUTION
= AUTHORIZED

FULL WAKE-UP SOURCE GATE
= PENDING_MASSIVE_BACKFILL_AND_LIVE_CAPTURE
```
