# 002 expected_data_calendar Representation Audit

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
table_number: 002
table_name: expected_data_calendar
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\expected_data_calendar_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\expected_data_calendar_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\expected_data_calendar_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\expected_data_calendar_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\expected_data_calendar_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\002_expected_data_calendar\002_expected_data_calendar.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\002_expected_data_calendar\README.md [not_found_in_local_check]
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
For this table, the contribution is: Expectedness matrix for whether an instrument/session/dataset should have data.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Expectedness matrix for whether an instrument/session/dataset should have data.
```

What does this table explicitly not represent?

```text
It is not a market feature, signal, event, or outcome.
```

TSIS object type:

```text
governance_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per expected instrument-session-dataset observation, with reason/scope to distinguish true absence from missing data.
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
sample_columns_count: 21
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
expected_dataset_id, expected_source_root, instrument_id, ticker, session_date, expected_session, expected_reason, expectation_scope, calendar, timezone, month, valid_from, valid_to, instrument_master_schema_version, instrument_master_build_run_id, market_calendar_schema_version, market_calendar_build_run_id, expectation_policy_version, build_run_id, schema_version, created_at_utc, dataset_family, year
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Structure | Dataset expectation | Missingness only has meaning relative to expectedness. | Should data exist for this instrument/session/source? | expected_dataset_id, expected_source_root, expected_reason, expectation_scope | expected_dataset_id, expected_source_root, expected_session, expected_reason, expectation_scope | certification/builders | keep |
| Temporality | Expected session coverage | Completeness is session-relative. | Which sessions are expected? | instrument_id, ticker, session_date, valid_from | instrument_id, ticker, session_date, month, valid_from | 003/004/013/014 | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| expected_dataset_id / expected_source_root | lineage | Structure | context | Links expectedness to source dataset. | Completeness is dataset-specific. | 003/builders | none | keep |
| instrument_id / ticker / session_date | identity | Temporality | context | Defines expectedness grain. | Missingness must be measured at consumption grain. | 004/013/014 | medium_if_joined_wrong | keep |
| expected_session / expected_reason / expectation_scope | quality_gate | Structure | derived/governance | Explains expected vs unexpected absence. | Absence is not always failure. | validators/status matrices | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| expectedness_exception_manifest_link | Structure | Useful for reviewed exceptions. | 003/manifests | Only needed if exception evidence is not linked elsewhere. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| None identified in this short audit | n/a | n/a | keep |

## 11. Temporal Legality And Leakage

```text
as_of_safe: true when valid_from/session_date are honored
future_data_present: false
outcomes_inline: false
lookback_policy_defined: not applicable
known_leakage_risks: treating expected non-trading as missing data
```

## 12. Consumption Verdict

```text
market_state=true quality context; event_state=true observability context; scanner=true eligibility; outcomes=true label reliability; model uses=missingness context only.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_for_current_role
reason: It prevents false conclusions from missing or unexpected data.
required_actions: Align expectedness with the promoted/candidate 013 quote-guarded universe before 014+ builds.
next_table_dependency: 003_dataset_certification_matrix
```


