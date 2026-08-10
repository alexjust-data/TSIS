# TRADING_ACTIVITY_BINDING_A_MULTISESSION_PILOT_EXECUTION_READOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_multisession_pilot_execution_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTION_EVIDENCE_AND_PILOT_VERDICT` |
| `document_status` | `EXECUTED` |
| `executed_at` | `2026-08-07` |
| `run_id` | `trading_activity_binding_a_multisession_pilot_20260807T100000Z` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `run_completion` | `PASS` |
| `independent_validation` | `PASS` |
| `pilot_evidence_verdict` | `PASS_WITH_RESTRICTIONS` |
| `full_legacy_source_gate` | `PASS_WITH_RESTRICTIONS` |
| `stratified_development_execution` | `AUTHORIZED` |
| `oos_comparison` | `NOT_AUTHORIZED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |

---

## 1. Purpose

This readout closes roadmap stages `TA-1` and `TA-2` for the declared legacy
RTH research-only profile. It reconciles execution, coverage, eligibility,
outputs, baseline availability, missingness, hashes, warnings and failures.

It does not admit the Representation Model, promote canonical features or
authorize a Wake-up detector.

---

## 2. Governed evidence

```text
output root
= G:/TSIS/data/data_foundation_outputs/
  trading_activity_binding_a_multisession_pilot/
  run_id=trading_activity_binding_a_multisession_pilot_20260807T100000Z

runtime root
= G:/TSIS/data/data_ops_manifests/
  trading_activity_binding_a_multisession_pilot/
  trading_activity_binding_a_multisession_pilot_20260807T100000Z
```

Authority hashes:

| Artifact | SHA-256 |
|---|---|
| `final_manifest.json` | `235e5f706a6f7bc4b64e54263d756321d47c24b3a34208c85ba1456e2e65dc10` |
| `metadata/run_summary.json` | `ac64eed1457c26302a8d6f4a237a6d3c693063930c5dbd20ff1201b8c6fdea3c` |
| `validation/output_hashes.parquet` | `4b546aa3f3b1ea59646316e38a33f200142fa62f512f99fec098845694c262e4` |
| `validation/post_run_independent_validation.json` | `c398446766d443f8390f18e15d4c7f992f72eb9dcb9dd81916a7b31e9cc9418f` |

---

## 3. Requested and completed exposure

```text
instrument
= AACT
  cik_ticker:0001853138:AACT

sessions requested
= 130

sessions completed
= 130

session interval
= 2024-09-06 through 2025-03-14

decision symbol-seconds requested
= 3,020,270

decision symbol-seconds completed
= 3,020,270

current-state rows
= 15,101,350 expected
  15,101,350 completed

multiscale rows
= 6,040,540 expected
  6,040,540 completed

baseline rows
= 1,754,925 expected
  1,754,925 completed

total representation rows
= 22,896,815 expected
  22,896,815 completed
```

Physical indexed partition bytes:

```text
88,367,010 bytes
```

---

## 4. Source coverage and eligibility

```text
physical source partitions
= 130 / 130

bounded acquisition evidence
= RESOLVED 130 / 130

Foundation 57f evidence
= JOINED 130 / 130

local audits
= 520
  130 sessions x 4 variable families

automatic exclusions
= 0

source trade rows
= 14,492

eligible trade rows
= 14,074

ineligible trade rows
= 418

unknown fail-closed rows
= 0

exact duplicate flags preserved
= 105
```

Foundation labels were retained as metadata:

```text
review                    = 81 sessions
review_microstructure     = 46 sessions
bad_data                  = 2 sessions
reference_scale_mismatch  = 1 session
```

All 520 variable-family audits were `USABLE_WITH_FLAGS`. No label silently
removed a session.

---

## 5. Current-state evidence

```text
CALCULATED
= 15,048,700

INSUFFICIENT_WINDOW_HISTORY
= 52,650

OBSERVED_NONZERO
= 1,406,361

OBSERVED_ZERO
= 13,694,989

DEGRADED
= 0

future_window_used = true
= 0

feature_input_max_available_at > decision_timestamp
= 0
```

The 52,650 insufficient rows are the exact expected opening-edge rows where a
complete right-anchored window cannot yet exist. They are not imputed from
before session open.

---

## 6. Multiscale evidence

```text
W5_W60
= 3,020,270 rows

W15_W300
= 3,020,270 rows

CALCULATED
= 6,040,540

DEGRADED
= 0

temporal violations
= 0
```

---

## 7. PIT baseline evidence

Every candidate produced the exact target grain:

```text
B20  = 584,975 rows, 20 reference sessions
B60  = 584,975 rows, 60 reference sessions
B120 = 584,975 rows, 120 reference sessions
```

Combined states:

```text
BASELINE_AVAILABLE
= 287,370

BASELINE_ZERO_DOMINATED
= 1,462,185

BASELINE_INSUFFICIENT_HISTORY
= 5,370
```

Per candidate:

| Candidate | Available | Zero dominated | Insufficient |
|---|---:|---:|---:|
| `B20` | 86,510 | 496,675 | 1,790 |
| `B60` | 92,930 | 490,255 | 1,790 |
| `B120` | 107,930 | 475,255 | 1,790 |

The insufficient rows occur at opening edges where the same clock-minute and
window combination lacks calculable source observations. The high
zero-dominated prevalence is an expected empirical property of a dormant AACT
history and must be preserved for later stratification.

Temporal violations:

```text
current available_at after decision
= 0

baseline available_at after decision
= 0

current or future session in baseline
= 0
```

---

## 8. Determinism, hashes and incident recovery

Internal gates:

```text
row counts             = PASS
grain uniqueness       = PASS
temporal legality      = PASS
kernel equivalence     = PASS across 130 sessions
baseline references    = PASS
```

Independent validation:

```text
267 indexed paths
267 unique indexed paths
267 content hashes verified
267 sidecar hashes verified
0 hash failures
```

The first attempt stopped in `STAGE_6` because a Windows temporary sidecar
path exceeded the effective path limit. The remediation and evidence are in:

```text
TRADING_ACTIVITY_BINDING_A_LONG_PATH_INCIDENT_READOUT_v0_1.md
```

The second attempt hash-validated and resumed 133 artifacts, including all 130
current-state partitions. No completed current-state partition was rebuilt or
lost. A separate full rebuild was not executed.

---

## 9. Restrictions

This pass is restricted because:

```text
source scope
= legacy RTH only

historical available_at
= simulated, not measured

observed_at
= unavailable historically

premarket and after-hours
= absent

revision and correction lineage
= not fully observable

instrument representativeness
= one ticker only

market-regime representativeness
= not established

detector false-alarm budget
= not evaluated

OOS validity
= not evaluated
```

Therefore the run describes the first observable transition during RTH, not
the first Wake-up of a complete activation episode.

---

## 10. Verdicts

```text
RUN_COMPLETION
= PASS

INDEPENDENT_POST_RUN_VALIDATION
= PASS

FULL_DETERMINISTIC_SYMBOL_SECOND_PILOT
= PASS_WITH_RESTRICTIONS

PILOT_EVIDENCE_VERDICT
= PASS_WITH_RESTRICTIONS

FULL_LEGACY_SOURCE_GATE
= PASS_WITH_RESTRICTIONS

STRATIFIED_DEVELOPMENT_EXECUTION
= AUTHORIZED

OOS_COMPARISON
= NOT_AUTHORIZED

REPRESENTATION_MODEL_ADMISSION
= NOT_AUTHORIZED

CANONICAL_FEATURE_PROMOTION
= NOT_AUTHORIZED

WAKE_UP_DETECTOR
= NOT_STARTED
```

The next work package is roadmap stage `TA-3`: preregister a development sample
stratified by price, market cap, historical activity, time/regime, coverage
quality and zero-activity prevalence while preserving the complete eligible
symbol-second denominator.
