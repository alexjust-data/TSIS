# 008 outcomes_table Representation Audit

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
table_number: 008
table_name: outcomes_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\outcomes_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\outcomes_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\outcomes_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\outcomes_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\outcomes_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\008_outcomes_table\008_outcomes_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\008_outcomes_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Future response/label layer tied to event windows.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Future response/label layer tied to event windows.
```

What does this table explicitly not represent?

```text
It is not a feature table, Market State, Event State, or current observable input.
```

TSIS object type:

```text
outcome_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per event window/outcome horizon with future returns, extrema, failure/break, impact/response metrics and label provenance.
```

Which market representation families should it cover?

```text
Price: covered - see matrix below
Trend: not_primary - not a primary responsibility of this table
Volatility: not_primary - not a primary responsibility of this table
Liquidity: covered - see matrix below
Participation: not_primary - not a primary responsibility of this table
Microstructure: not_primary - not a primary responsibility of this table
Temporality: not_primary - not a primary responsibility of this table
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
sample_columns_count: 179
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
outcome_id, event_window_id, source_event_id, event_source_dataset_id, event_family, event_type, event_code, event_source, ticker, instrument_id, issuer_name, listing_exchange, event_session_date, outcome_session_date, outcome_horizon, price_view, event_time_utc, resume_trade_utc, event_session_phase, window_role, window_start_utc, window_end_utc, window_duration_minutes, event_window_quality_state
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Events | Outcome anchored to event window | Event hypotheses need future behavior anchored to the same event/window. | What happened after this event window? | outcome_id, event_window_id, event metadata, horizons | outcome_id, event_window_id, source_event_id, event_family, event_type, event_code | evaluation/ml labels | keep |
| Price | Future price response | Price response evaluates whether an event/state mattered. | What was future return/MFE/MAE? | future return/extrema metrics | future outcome fields in 179-column sample | backtest/ml/rl labels | keep |
| Liquidity | Future tradability/impact | Prediction needs execution-aware outcomes. | How did spread/liquidity behave after event? | future spread/impact/latency fields | outcome fields in sample | execution-aware evaluation | keep |
| Structure | Label provenance | Labels must stay traceable and separate from X. | Which event/source/instrument produced this label? | event source, instrument identity | event_source_dataset_id, ticker, instrument_id | audits/validators | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| outcome_id | outcome_label | Events | derived | Label identity separate from event window. | Outcomes are distinct from state. | evaluation/ml/rl | high_if_used_as_X | keep |
| event_window_id / source_event_id | lineage | Events | context | Anchors labels to event geometry. | Labels must be traceable. | audits/metrics | low | keep |
| future return / MFE / MAE / break group | outcome_label | Price | derived_future | Measures future price behavior. | Forward paths evaluate hypotheses. | backtests/ml labels | high | keep |
| future spread / impact / latency group | outcome_label | Liquidity | derived_future | Measures execution-relevant future conditions. | Tradability matters for usefulness. | execution-aware evaluation | high | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| strict_feature_consumption_denial | Structure | Prevents accidental use as current state/model input. | consumption policy/validators | Must be explicit in downstream loaders. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| outcome_columns_in_state_builders | Future labels inside state create leakage. | Only evaluation/label pipeline may consume them. | delete |

## 11. Temporal Legality And Leakage

```text
as_of_safe: false for state/model input; true only as post-hoc label/evaluation
future_data_present: true by definition
outcomes_inline: true by role but isolated from X
lookback_policy_defined: horizon policy required
known_leakage_risks: any use of outcome columns before prediction/evaluation boundary
```

## 12. Consumption Verdict

```text
market_state=false; event_state=false except post-hoc review; scanner=false; outcomes=true; backtest=true evaluation; ml=true y only; rl=true reward/label only; alphaevolve=true objective/evaluation only.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_for_current_role
reason: It is essential because outcomes are separated from state.
required_actions: Enforce policy so 008 cannot feed observable state builders as X.
next_table_dependency: 017 event state evaluation and label pipelines
```


