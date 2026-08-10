# TRADING_ACTIVITY_SOURCE_QUALITY_LABEL_CONSUMPTION_POLICY_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_source_quality_label_consumption_policy` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_SOURCE_LABEL_CONSUMPTION_POLICY` |
| `document_status` | `CURRENT_POLICY` |
| `effective_at` | `2026-08-07` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `information_object_id` | `trading_activity` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `owner` | `TBD` |

---

## 1. Decision

Data Foundation quality labels are mandatory evidence metadata. They are not
automatic inclusion or exclusion gates for the Trading Activity pilot.

This rule applies to every prior label or absence of label, including:

```text
GOOD
RECOVERABLE_WITH_FLAG
REVIEW_NOT_REHABILITATED
BAD
UNCLASSIFIED_OR_NO_EVIDENCE
```

Therefore:

```text
FOUNDATION_QUALITY_LABEL
!= AUTOMATIC PILOT CONSUMPTION DECISION
```

No source label by itself may stop completion of the pilot or the wider
Trading Activity workstream.

---

## 2. Rationale

Foundation labels summarize broad data-quality evidence. Some diagnostics may
be immaterial to the variables evaluated by a particular binding. For example,
a historical VWAP discrepancy does not automatically invalidate trade counts,
event timing or share volume.

The pilot must preserve the original label without assuming that every reason
code affects every Trading Activity variable.

This policy does not weaken or overwrite Data Foundation certification. It
defines how that evidence is consumed by this experimental profile.

---

## 3. Selected-window audit

Every temporal window selected for the pilot must undergo a local,
variable-relevance audit before its result is interpreted.

For Trading Activity, the audit must evaluate at least:

- physical readability and required schema;
- intrawindow coverage and unexplained gaps;
- duplicate events;
- nonpositive or invalid trade sizes;
- timestamp validity and deterministic ordering;
- trade-condition treatment;
- price-scale validity when calculating dollar volume;
- evidence needed to distinguish observed zero from unavailable data.

The audit must record which Binding A variables are affected by each finding.
An unrelated diagnostic must not be converted into a blanket rejection.

---

## 4. Local dispositions

The selected-window audit, not the Foundation label, assigns one of these local
dispositions:

```text
LOCALLY_AUDITED_USABLE
LOCALLY_AUDITED_USABLE_WITH_FLAGS
LOCALLY_AUDITED_DEGRADED
LOCALLY_AUDITED_REPLACE_WINDOW
```

Interpretation:

- `USABLE`: no material issue for the evaluated variables;
- `USABLE_WITH_FLAGS`: evidence is usable with explicit restrictions;
- `DEGRADED`: execution may continue, but affected outputs must retain degraded
  state and reason codes;
- `REPLACE_WINDOW`: the specific window is unsuitable and must be corrected or
  replaced without blocking the complete workstream.

No silent repair, silent exclusion or silent replacement is allowed.

---

## 5. Required lineage

The pilot input manifest must preserve at least:

```text
ticker
trading_date
physical_file
foundation_quality_label
foundation_reason_codes
foundation_evidence_version
local_window_audit_status
local_window_disposition
local_reason_codes
affected_variable_ids
replacement_window_reference
```

Missing Foundation evidence must be represented as
`UNCLASSIFIED_OR_NO_EVIDENCE`; it must not be rewritten as `GOOD`.

---

## 6. Execution and promotion boundary

```text
DETERMINISTIC PILOT EXECUTION
= NOT BLOCKED BY A FOUNDATION LABEL

SELECTED-WINDOW LOCAL AUDIT
= REQUIRED

FINAL CROSS-OBJECT DATA REAUDIT
= REQUIRED BEFORE CANONICAL PROMOTION

CANONICAL FEATURE PROMOTION
= NOT AUTHORIZED
```

After the physical implementations of all Wake-up Information Objects have
been evaluated, TSIS must perform a final governed data re-audit across the
actual selected sources, windows and variables. Foundation evidence remains an
input to that audit, not a substitute for it.

---

## 7. Handoff rule

Future agents designing or executing the multisession pilot must apply this
policy before using a Foundation bucket as a source filter. Any stricter local
restriction requires a versioned amendment with variable-specific evidence.
