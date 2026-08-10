# TRADING_ACTIVITY_BINDING_A_FULL_SCOPE_PREFLIGHT_READOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_a_full_scope_preflight_readout` |
| `document_version` | `v0_1` |
| `document_role` | `FULL_SCOPE_PRE_MATERIALIZATION_EVIDENCE` |
| `document_status` | `EXECUTED` |
| `executed_at` | `2026-08-07` |
| `run_id` | `trading_activity_binding_a_multisession_preflight_20260807_v01` |
| `terminal_stage` | `STAGE_4` |
| `terminal_status` | `INTERRUPTED_COOPERATIVE_AS_PLANNED` |
| `preflight_verdict` | `PASS` |
| `full_materialization_status` | `NOT_STARTED` |
| `promotion_status` | `NOT_AUTHORIZED` |

---

## 1. Purpose

The preflight executed the complete 130-session scope through the last bounded
stage before expensive symbol-second materialization.

Command boundary:

```text
STAGE 0 through STAGE 4
then controlled test stop
```

Therefore:

```text
process exit was non-zero by controlled-stop design
final manifest status = INTERRUPTED_COOPERATIVE
preflight verdict = PASS
```

No `CURRENT_STATE`, `MULTISCALE_CONTRAST` or
`PIT_BASELINE_AND_SURPRISE` full-scope partitions were generated.

---

## 2. Governed paths

Output:

```text
G:/TSIS/data/data_foundation_outputs/
trading_activity_binding_a_multisession_pilot/
run_id=trading_activity_binding_a_multisession_preflight_20260807_v01
```

Runtime:

```text
G:/TSIS/data/data_ops_manifests/
trading_activity_binding_a_multisession_pilot/
trading_activity_binding_a_multisession_preflight_20260807_v01
```

---

## 3. Scope evidence

```text
governed session rows
= 130

physical source partitions present
= 130 / 130

bounded acquisition evidence resolved
= 130 / 130

Foundation 57f evidence rows joined
= 130 / 130

local audit rows
= 520
  130 sessions x 4 variable families

automatic source exclusions
= 0
```

Foundation labels retained:

```text
review                    = 81
review_microstructure     = 46
bad_data                  = 2
reference_scale_mismatch  = 1
```

Local variable-family dispositions:

```text
USABLE_WITH_FLAGS = 520
```

The labels and flags remain evidence metadata. They did not remove a session
or stop the workstream.

---

## 4. Kernel and size evidence

```text
kernel equivalence status
= PASS

sessions probed
= 130

expected decision symbol-seconds
= 3,020,270

expected CURRENT_STATE rows
= 15,101,350

expected MULTISCALE_CONTRAST rows
= 6,040,540

expected PIT_BASELINE_AND_SURPRISE rows
= 1,754,925

expected total rows
= 22,896,815
```

Serialization probe:

```text
bounded compressed projection
= 1.3616 GiB

free output space at preflight
= 183.3452 GiB

configured minimum free-space gate
= 75 GiB or 3x projection, whichever is greater

configured preventive output ceiling
= 25 GiB

disk gate
= PASS
```

The 1.3616 GiB value is a bounded compression probe over highly repetitive
symbol-second metadata. It does not replace the conservative planning range:

```text
working estimate = approximately 3-8 GiB
broad safety range = up to 12-15 GiB
preventive ceiling = 25 GiB
```

---

## 5. Verdict

```text
SOURCE PATH AND HASH PREFLIGHT
= PASS

CALENDAR AND IDENTITY PREFLIGHT
= PASS

DENSE 130-SESSION SCOPE
= PASS

ACQUISITION AND 57F JOIN
= PASS

LOCAL VARIABLE-FAMILY AUDIT
= PASS_WITH_FLAGS

KERNEL EQUIVALENCE
= PASS

OUTPUT SIZE AND FREE-SPACE GATE
= PASS

READY_FOR_HUMAN FULL-RUN DECISION
= YES

FULL MATERIALIZATION
= NOT_STARTED

MODEL ADMISSION
= NOT_AUTHORIZED
```

This readout strengthens the prelaunch evidence. It does not change the next
gate or authorize an agent to start the long run autonomously.
