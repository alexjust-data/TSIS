# 007 event_windows_table Representation Audit

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
table_number: 007
table_name: event_windows_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\event_windows_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\event_windows_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\event_windows_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\event_windows_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\event_windows_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\007_event_windows_table\007_event_windows_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\007_event_windows_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Canonical event-window alignment layer.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Canonical event-window alignment layer.
```

What does this table explicitly not represent?

```text
It does not create events, define market state, contain future labels, or decide trades.
```

TSIS object type:

```text
event_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per governed event window with source event identity, taxonomy, instrument/session identity and window timing.
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
Events: covered - see matrix below
Structure: covered - see matrix below
```

## 6. Current Physical State

What exists today?

```text
documented_current_state: folder-named physical sample file exists in the table folder and documents the observed physical sample.
physical_observed_state: sample documentation parsed; this audit did not re-read the full physical parquet.
sample_columns_count: 63
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
event_window_id, source_event_id, event_source_dataset_id, event_family, event_type, event_code, event_source, ticker, instrument_id, issuer_name, listing_exchange, session_date, year, month, event_time_utc, resume_trade_utc, event_session_phase, window_role, window_start_utc, window_end_utc, window_duration_minutes, window_start_source, window_end_source, contains_event_time
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Events | Event identity/window geometry | Events require explicit windows, not arbitrary slices. | Which event and window is this? | event_window_id, event id, taxonomy, window timestamps | event_window_id, source_event_id, event_family, event_type, event_code, event_source | 017/008/015 | keep |
| Temporality | Pre/at/post alignment | Causal analysis separates before/at/after event. | What was knowable before event time? | window start/end/role, event timestamp | session_date and event/window fields | features/outcomes | keep |
| Structure | Source/instrument binding | Event analyses must be traceable. | Which source/instrument produced this window? | source dataset, instrument_id, ticker | event_source_dataset_id, ticker, instrument_id, issuer_name, listing_exchange | 017/008 | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event_window_id | event_descriptor | Events | derived | Unit of event-aligned analysis. | Window identity differs from source event identity. | 017/008/audits | none | keep |
| source_event_id / event_source_dataset_id | lineage | Structure | context | Links back to source event. | States/outcomes must trace to source. | 017/008 | low | keep |
| event_family / type / code / source | event_descriptor | Events | context | Defines taxonomy/source semantics. | Event types have different response distributions. | event research/017/008 | low | keep |
| window timing group | asof_control | Temporality | derived | Separates pre/at/post observations. | Causality depends on window role. | 017/008/ml/rl | high_if_misused | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| explicit_window_role_columns_review | Events | Verify pre/at/post/replay role fields. | 007/017 | Audit full schema beyond sample excerpt. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| post_event_fields_used_as_pre_event_state | Creates leakage. | Keep post-event only for outcomes/review state. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on window role/event timestamp
future_data_present: allowed only for post-event/outcome consumers
outcomes_inline: false
lookback_policy_defined: required per window role
known_leakage_risks: post-window info in pre-event features
```

## 12. Consumption Verdict

```text
market_state=conditional event proximity only; event_state=true primary upstream; scanner=true if event candidates governed; outcomes=true anchor; model uses=true with strict X/y separation.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: Necessary for event-aligned science, but leakage control depends on window-role enforcement.
required_actions: Verify full schema for window role/timing and pre/post boundaries.
next_table_dependency: 008_outcomes_table and 017_event_state_table
```


