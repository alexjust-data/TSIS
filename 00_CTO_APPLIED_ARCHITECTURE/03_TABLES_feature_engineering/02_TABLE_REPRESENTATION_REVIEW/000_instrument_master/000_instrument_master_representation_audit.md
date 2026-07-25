# 000 instrument_master Representation Audit

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
table_number: 000
table_name: instrument_master
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\instrument_master_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\instrument_master_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\instrument_master_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\instrument_master_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\instrument_master_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\000_instrument_master\000_instrument_master.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\000_instrument_master\README.md [not_found_in_local_check]
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
For this table, the contribution is: Stable instrument identity and lifecycle map for tradable entities.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Stable instrument identity and lifecycle map for tradable entities.
```

What does this table explicitly not represent?

```text
It is not market state, a price signal, an event, or an outcome.
```

TSIS object type:

```text
institutional_infrastructure
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One governed identity interval per instrument/ticker relationship, with validity, listing metadata, source context and join legality.
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
sample_columns_count: 53
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
instrument_id, ticker, identity_resolution_level, ticker_identity_scope, valid_from, valid_to, name, market, locale, primary_exchange, ticker_type_code, ticker_type_description, is_common_stock, active_in_reference, currency_name, cik, composite_figi, share_class_figi, exchange_name, exchange_acronym, exchange_mic, exchange_operating_mic, overview_request_date, overview_market_cap
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Structure | Instrument identity | Market observations are not comparable unless entity identity is stable. | Which entity does this ticker/date observation belong to? | instrument_id, ticker, validity window, listing metadata | instrument_id, ticker, identity_resolution_level, ticker_identity_scope, valid_from, valid_to, market, primary_exchange | all downstream tables | keep |
| Temporality | Identity validity | Ticker meaning can change through time. | Is this identity legal at t? | valid_from, valid_to | valid_from, valid_to | all time-indexed joins | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| instrument_id | identity | Structure | derived/institutional | Stable cross-table entity key. | Ticker strings are insufficient as identity. | all downstream tables | none | keep |
| ticker + ticker_identity_scope | identity | Structure | context | Keeps ticker visible but scoped. | Ticker-only joins are unsafe. | builders/audits | low | keep |
| valid_from / valid_to | asof_control | Temporality | context | Defines legal identity interval. | Identity joins must be time-bound. | all time-indexed tables | medium_if_ignored | keep |
| market / locale / primary_exchange / ticker_type | context | Structure | context | Describes universe/listing context. | Listing context affects eligibility. | scanners/states/backtests | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| downstream_identity_join_policy | Structure | Prevents ticker-only joins after 000. | consumption policies/builders | Audit every downstream table for instrument_id use. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| ticker_as_primary_join_key | Ticker alone can create identity drift. | Downstream builders should use instrument_id plus date. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: true when valid_from/valid_to are enforced
future_data_present: false
outcomes_inline: false
lookback_policy_defined: not applicable
known_leakage_risks: ticker-only joins across identity changes
```

## 12. Consumption Verdict

```text
market_state=true identity context; event_state=true event binding; scanner=true universe/listing context; outcomes=true join key only; backtest/ml/rl/alphaevolve=conditional metadata only.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_for_current_role
reason: It justifies itself as identity and join legality infrastructure.
required_actions: Audit downstream builders for ticker-only exceptions.
next_table_dependency: 001_market_calendar and all table joins
```


