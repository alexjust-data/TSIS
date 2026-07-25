# 005 corporate_actions_table Representation Audit

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
table_number: 005
table_name: corporate_actions_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\corporate_actions_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\corporate_actions_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\corporate_actions_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\corporate_actions_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\corporate_actions_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\005_corporate_actions_table\005_corporate_actions_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\005_corporate_actions_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Corporate action event/context layer explaining structural changes in price scale, shares, listing context and comparability.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Corporate action event/context layer explaining structural changes in price scale, shares, listing context and comparability.
```

What does this table explicitly not represent?

```text
It is not market state by itself, a signal, or an outcome table.
```

TSIS object type:

```text
context_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per corporate action with action type/date, source lineage, priority and reference status.
```

Which market representation families should it cover?

```text
Price: not_primary - not a primary responsibility of this table
Trend: not_primary - not a primary responsibility of this table
Volatility: not_primary - not a primary responsibility of this table
Liquidity: not_primary - not a primary responsibility of this table
Participation: not_primary - not a primary responsibility of this table
Microstructure: not_primary - not a primary responsibility of this table
Temporality: not_primary - not a primary responsibility of this table
Daily Context: covered - see matrix below
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
sample_columns_count: 36
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
corporate_action_id, instrument_id, ticker, action_type, action_date, action_year, source_system, source_dataset, source_root, source_priority, source_event_id, is_reference_primary_source, is_additional_secondary_source, split_from, split_to, split_ratio, cash_amount, currency, declaration_date, ex_dividend_date, pay_date, record_date, dividend_type, dividend_frequency
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Structure | Instrument structural change | Corporate actions can make history non-comparable. | Did a structural action affect this date? | action id/type/date, source, priority | corporate_action_id, action_type, action_date, source_system, source_priority | 004/013/014/016 | keep |
| Daily Context | Action context | Corporate actions alter daily/intraday interpretation. | Is today near a split/dividend/symbol action? | action_date, action_year, instrument/ticker | instrument_id, ticker, action_date, action_year | 016/017 | keep |
| Events | Corporate action occurrence | Some actions can anchor event windows. | Can this action create an event candidate/window? | source_event_id, action_type, effective date | source_event_id, action_type, action_date | 007/017/outcomes | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| corporate_action_id | event_descriptor | Structure | derived/governance | Auditable action identity. | Structural events need identity. | 007/audits | none | keep |
| instrument_id / ticker | identity | Structure | context | Binds action to instrument. | Corporate actions must not be joined by ticker alone. | 004/013/014/states | medium_if_joined_wrong | keep |
| action_type / action_date | event_descriptor | Events | raw/context | Defines what happened and when. | Action type changes interpretation. | 007/016/017 | low | keep |
| source_* / source_priority / primary_source | lineage | Structure | governance/context | Controls provenance/conflicts. | Sources can conflict. | certification/validators | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| effective_asof_timestamp | Temporality | Needed when action knowledge date differs from action date. | 005/016/017 | Check announcement/effective/as-of fields. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| action_date_as_knowledge_date | Can leak if market did not know the action yet. | Use announcement/as-of fields where available. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on action date vs announcement/as-of semantics
future_data_present: possible if future corporate actions are joined before known
outcomes_inline: false
lookback_policy_defined: required for state consumers
known_leakage_risks: future-known action data
```

## 12. Consumption Verdict

```text
market_state/event_state/scanners/backtests/ml/rl/alphaevolve=true with as-of legality; outcomes=true for stratification/context.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: The role is clear, but action knowledge timing must be explicit for state/event use.
required_actions: Verify announcement/effective/as-of semantics before intraday state use.
next_table_dependency: 004, 007, 016, 017
```


