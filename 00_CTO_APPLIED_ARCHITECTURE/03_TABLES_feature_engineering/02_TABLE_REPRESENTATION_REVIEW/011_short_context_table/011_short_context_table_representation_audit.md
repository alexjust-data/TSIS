# 011 short_context_table Representation Audit

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
table_number: 011
table_name: short_context_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\short_context_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\short_context_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\short_context_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\short_context_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\short_context_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\011_short_context_table\011_short_context_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\011_short_context_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Short interest, short volume or borrow-related context with observation/as-of semantics.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Short interest, short volume or borrow-related context with observation/as-of semantics.
```

What does this table explicitly not represent?

```text
It is not price state by itself, not an outcome label, and not necessarily intraday-observable.
```

TSIS object type:

```text
context_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per instrument/source short-context observation, with source family/scope and observation/settlement/trade/as-of semantics.
```

Which market representation families should it cover?

```text
Price: not_primary - not a primary responsibility of this table
Trend: not_primary - not a primary responsibility of this table
Volatility: not_primary - not a primary responsibility of this table
Liquidity: covered - see matrix below
Participation: covered - see matrix below
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
sample_columns_count: 79
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
short_context_id, ticker, instrument_id, source_dataset_id, source_family, source_scope, observation_date_type, observation_date, settlement_date, trade_date, as_of_date, as_of_semantics, short_interest, avg_daily_volume, days_to_cover, total_volume, short_volume, exempt_volume, non_exempt_volume, short_volume_ratio, nyse_short_volume, nyse_short_volume_exempt, nasdaq_carteret_short_volume, nasdaq_carteret_short_volume_exempt
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Participation | Short-side pressure | Short participation can condition squeezes, liquidity and event response. | Was short pressure elevated/changing? | short interest/volume/ratio or borrow metrics | short_context_id, source_family, source_scope plus short metrics in sample | 016/017/backtests | keep |
| Liquidity | Short availability/friction | Borrow/short constraints affect tradability and price response. | Is short-side liquidity constrained? | borrow/short availability metrics | short metric groups in sample | execution-aware research | keep |
| Temporality | Reporting lag/as-of timing | Short data frequency/reporting lag can create point-in-time errors. | Which date makes observation usable? | observation_date, settlement_date, trade_date, as_of_date | observation_date_type, observation_date, settlement_date, trade_date, as_of_date, as_of_semantics | states/ml/rl | keep |
| Structure | Source family/scope | Short datasets vary by source semantics. | Which source/scope governs metric? | source_dataset_id, source_family, source_scope | source_dataset_id, source_family, source_scope | audit/builders | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short_context_id | identity | Participation | derived | Identity for short-context snapshot. | Short context is time/source scoped. | 016/017/audits | none | keep |
| source_family / source_scope / source_dataset_id | lineage | Structure | context | Identifies source semantics. | Short metrics are source-dependent. | builders/validators | low | keep |
| observation/settlement/trade/as_of dates | asof_control | Temporality | context | Defines usable time. | Reporting lag changes observability. | 016/017/backtests | high_if_ignored | keep |
| short metric groups | context | Participation | raw/derived | Represents pressure/constraint context. | Short pressure can affect squeezes/reversion. | states/ml | medium | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| metric_frequency_and_lag_policy | Participation | Short-interest and short-volume families differ. | 011/016/017 | Audit source family definitions and windows. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| mixing_short_interest_and_short_volume_without_scope | Different phenomena/frequencies. | Keep source_family/source_scope or split derived families. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on as_of_semantics
future_data_present: possible if release lag ignored
outcomes_inline: false
lookback_policy_defined: required by source family
known_leakage_risks: using short data before publication
```

## 12. Consumption Verdict

```text
market_state/event_state/scanners/backtests/ml/rl/alphaevolve=true with reporting-lag policy; outcomes=true stratification.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: Short context has a real hypothesis role, but source-specific as-of/lag handling is high-risk.
required_actions: Define frequency/lag policy per short source family before state feature use.
next_table_dependency: 016 market state and 017 event state
```


