# FLOAT_CONTEXT_SOURCE_AUDIT_PLAN_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `float_context_source_audit_plan` |
| `document_version` | `v0_1` |
| `document_role` | `CONDITIONAL_CONTEXT_SOURCE_AUDIT_PLAN` |
| `document_status` | `ACTIVE_PARALLEL_PLAN` |
| `information_object_id` | `fundamental_context` |
| `target_component` | `float_context_table` |
| `owner_layer` | `01_TSIS_DATA_FOUNDATION` |
| `materialization_status` | `NOT_STARTED` |
| `scanner_filter_status` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

---

## 1. Current truth

TSIS does not currently have a governed point-in-time `float_context_table`.

Current contracts require:

```text
float_shares = null
```

until source, as-of semantics, coverage and quality are proven.

Available fields such as:

```text
overview_weighted_shares_outstanding
share_class_shares_outstanding
basic_shares_outstanding
diluted_shares_outstanding
```

are shares measures. None may populate `float_shares` without evidence that it
represents publicly tradable float under the declared source methodology.

---

## 2. Purpose

Determine whether TSIS can build a historical event-driven float context for
the operational candidate universe and use it legally in:

```text
daily scanner context
intraday scanner context
Wake-up stratification
episode context
later Tradability research
```

Float does not define Trading Activity and is not a substitute for market cap.

---

## 3. Required coverage target

```text
candidate instruments
= the 4,824 operational LT1B tickers

historical horizon
= all recoverable observations across 2005-2026

physical grain
= instrument_id x float observation/revision
```

The table is event-driven. It must not create one row per minute or one row per
day merely by carrying values forward.

---

## 4. Source inventory

Audit at minimum:

```text
G:/TSIS/data/reference
G:/TSIS/data/additional/financials
G:/TSIS/data/financial, evidence-only while policy-blocked
SEC filing or company-facts assets already stored locally
vendor payloads containing explicit float/free-float fields
instrument_master snapshot fields for reconciliation only
```

For each candidate field preserve:

```text
source_dataset_id
source_file
source_row_id
vendor field name
field definition
units
effective date
publication date
available_at evidence
revision linkage
ticker/instrument identity
coverage by year and ticker
null and stale rates
```

Provider documentation may support semantics, but physical payload inspection
is required before declaring a field observable.

---

## 5. Construct boundary

The audit must distinguish:

```text
SHARES OUTSTANDING
= issued shares currently outstanding

WEIGHTED-AVERAGE SHARES
= accounting-period denominator

PUBLIC FLOAT
= shares estimated to be available for public trading

FREE-FLOAT PERCENT
= float_shares / shares_outstanding under a declared methodology
```

No arithmetic from weighted-average shares alone can manufacture float.

If float is vendor-estimated or derived from affiliate holdings, the method,
lag and limitations must travel with every observation.

---

## 6. Candidate schema

```text
float_context_id
instrument_id
ticker_as_of_observation
float_shares
shares_outstanding_reference
free_float_pct
float_measure_type
effective_at
published_at
observed_at
available_at
source_dataset_id
source_observation_id
source_methodology_version
revision_action
original_observation_id
observation_age_days
coverage_state
quality_state
reason_codes
schema_version
build_run_id
lineage_manifest_id
```

Historical `observed_at` and `available_at` must not be fabricated. When only a
date-level publication is known, use an explicit conservative availability
policy and mark the timestamp as simulated or date-bounded.

---

## 7. Consumption model

At a decision timestamp `t`:

```text
float_as_of(t)
= latest accepted float observation
  with available_at <= t
```

Consumers receive:

```text
float value
age
source
quality
coverage
unknown/stale state
```

The as-of resolver carries the latest valid event into a daily or intraday
state. The physical float table itself remains sparse.

---

## 8. Audit gates

```text
SOURCE SEMANTICS
- explicit evidence that the field represents float

TEMPORAL LEGALITY
- effective, published and available time policy

IDENTITY
- point-in-time instrument mapping

UNITS AND SCALE
- shares units and corporate-action behavior

REVISIONS
- correction and supersession behavior

COVERAGE
- ticker/year coverage, missing and stale intervals

REPRODUCIBILITY
- source snapshots, hashes, builder and lineage
```

Possible verdicts:

```text
FLOAT_SOURCE_GATE
= PASS
  PASS_WITH_RESTRICTIONS
  or FAIL
```

---

## 9. Workstream dependency

```text
TRADING ACTIVITY BINDING A COMPUTATION
= NOT BLOCKED BY FLOAT

TA-3 PRIMARY SAMPLE SELECTION
= MUST NOT USE UNGOVERNED FLOAT

TA-3 LATER FLOAT STRATIFICATION
= ALLOWED BY AS-OF JOIN AFTER FLOAT SOURCE GATE

CANONICAL DAILY SCANNER FLOAT FILTER
= BLOCKED UNTIL FLOAT CONTEXT GATE

INTRADAY FLOAT CONTEXT
= BLOCKED UNTIL FLOAT CONTEXT GATE
```

Joining float later to the frozen primary TA-3 sample avoids delaying Trading
Activity and avoids selecting only cases with favorable or available float.

---

## 10. Deliverables

```text
source inventory manifest
field-level observability matrix
coverage report
semantic and temporal fixtures
source-gate readout
float_context schema candidate
builder plan only after source gate
```

No float filter is activated by this plan.

