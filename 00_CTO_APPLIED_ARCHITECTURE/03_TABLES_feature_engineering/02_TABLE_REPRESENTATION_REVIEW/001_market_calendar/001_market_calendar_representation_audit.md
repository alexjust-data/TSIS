# 001 market_calendar Representation Audit

Status: `technical_audit_v0_1`

Date: `2026-07-16`

Audit scope: table representation, feature-engineering relevance and downstream consumption boundaries.

This document applies the shared guardrail from:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\TABLES_REPRESENTATION_OF_MARKET.md
```

---

## 1. Table Identity

```text
table_number: 001
table_name: market_calendar
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\market_calendar_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\market_calendar_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\market_calendar_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\market_calendar_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\market_calendar_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\001_market_calendar\001_market_calendar.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\001_market_calendar\README.md [not_found_in_local_check]
```

Architecture references:

```text
epistemology: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\00_EPISTEMOLOGICAL_architecture
representation_materialization_review: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\01_REPRESENTATION_MATERIALIZATION_REVIEW
materialization_governance_review: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\02_MATERIALIZATION_GOVERNANCE_REVIEW
```

## 3. Central Guardrail

What do we need to know to correctly describe the state of the market at an instant `t`?

```text
We need only the information this table is responsible for making observable, legal and traceable at t.
For this table, the contribution is: Canonical session calendar and trading-time boundary.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Canonical session calendar and trading-time boundary.
```

What does this table explicitly not represent?

```text
It is not price behavior, a liquidity feature, a signal, or an outcome.
```

TSIS object type:

```text
institutional_infrastructure
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per trading session with open/close timestamps, session length, early-close flag, date partitions and timezone semantics.
```

Which market representation families should it cover?

```text
Price: not_primary - not a primary responsibility of this table
Trend: not_primary - not a primary responsibility of this table
Volatility: not_primary - not a primary responsibility of this table
Liquidity: not_primary - not a primary responsibility of this table
Participation: not_primary - not a primary responsibility of this table
Microstructure: not_primary - not a primary responsibility of this table
Temporality: covered - see matrix below
Daily Context: not_primary - not a primary responsibility of this table
Intraday Context: not_primary - not a primary responsibility of this table
News: not_primary - not a primary responsibility of this table
Fundamentals: not_primary - not a primary responsibility of this table
Regime: not_primary - not a primary responsibility of this table
Events: not_primary - not a primary responsibility of this table
Structure: covered - see matrix below
```

## 6. Current Physical State

What exists today?

```text
documented_current_state: folder-named physical sample file exists in the table folder and documents the observed physical sample.
physical_observed_state: sample documentation parsed; this audit did not re-read the full physical parquet.
sample_columns_count: 16
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
session_date, open_utc, close_utc, open_et, close_et, session_minutes, is_early_close, year, month, dow, calendar, timezone, source_calendar_artifact, build_run_id, schema_version, created_at_utc
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Temporality | Session legality | Market observables depend on session boundaries. | Is t inside a valid session? | session_date, open/close UTC/ET, session_minutes, early_close | session_date, open_utc, close_utc, open_et, close_et, session_minutes, is_early_close | all time-aware builders | keep |
| Structure | Calendar/timezone semantics | Calendar authority prevents cross-market/timezone ambiguity. | Which calendar governs this row? | calendar, timezone, year, month, dow | year, month, dow, calendar, timezone | builders/audits | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| session_date | identity | Temporality | context | Defines session grain. | Market behavior is session-relative. | all session-keyed tables | none | keep |
| open_utc / close_utc / open_et / close_et | asof_control | Temporality | context | Defines legal boundaries. | Temporal legality needs exact boundaries. | 013/014/backtests/states | medium_if_wrong | keep |
| session_minutes / is_early_close | context | Temporality | derived/context | Normalizes by session length. | Early close changes volume/time comparisons. | 014/015/016 | low | keep |
| year / month / dow / calendar / timezone | context | Structure | context | Supports partitions and interpretation. | Calendar context affects expectedness. | builders/audits | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| intraday_session_phase_policy | Intraday Context | Needed later for open/midday/close phase features. | 014/016 | Not required inside 001 but downstream must define it. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| None identified in this short audit | n/a | n/a | keep |

## 11. Temporal Legality And Leakage

```text
as_of_safe: true
future_data_present: false
outcomes_inline: false
lookback_policy_defined: not applicable
known_leakage_risks: timezone or early-close mishandling
```

## 12. Consumption Verdict

```text
market_state=true time boundary; event_state=true event window legality; scanner=true session filters; outcomes=true alignment context; all model uses=calendar context only.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_for_current_role
reason: It provides temporal legality, not predictive noise.
required_actions: Ensure 013/014 use this calendar for session boundaries.
next_table_dependency: 002_expected_data_calendar
```


