# 012 regime_context_table Representation Audit

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
table_number: 012
table_name: regime_context_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\regime_context_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\regime_context_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\regime_context_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\regime_context_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\regime_context_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\012_regime_context_table\012_regime_context_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\012_regime_context_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Broad market/regime proxy context aligned as-of to trading dates and sessions.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Broad market/regime proxy context aligned as-of to trading dates and sessions.
```

What does this table explicitly not represent?

```text
It is not the instrument's own price state, an outcome label, or a strategy decision.
```

TSIS object type:

```text
context_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per regime proxy/date/as-of context with symbol/proxy role, source granularity, timing and derived regime indicators.
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
Regime: covered - see matrix below
Events: not_primary - not a primary responsibility of this table
Structure: covered - see matrix below
```

## 6. Current Physical State

What exists today?

```text
documented_current_state: folder-named physical sample file exists in the table folder and documents the observed physical sample.
physical_observed_state: sample documentation parsed; this audit did not re-read the full physical parquet.
sample_columns_count: 68
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
regime_context_id, regime_symbol, source_symbol_dir, regime_proxy_role, source_dataset_id, source_granularity, context_granularity, trading_date, session_open_utc, as_of_utc, as_of_date, as_of_semantics, first_bar_timestamp, last_bar_timestamp, bars_observed, distinct_timestamp_count, duplicate_timestamp_rows, bar_coverage_state, open_price, high_price, low_price, close_price, previous_close_price, intraday_return
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Regime | Broad market environment | Smallcap behavior depends on broader volatility, risk and liquidity regime. | What regime was observable at t? | regime proxy role, symbol, as-of timing, indicators | regime_symbol, regime_proxy_role, source_granularity, context_granularity, trading_date, as_of_utc | 016/017/ml/rl | keep |
| Temporality | Regime as-of/session alignment | Regime features must be legal at state timestamp. | Which regime value was known by t? | trading_date, session_open_utc, as_of_utc, as_of_date | trading_date, session_open_utc, as_of_utc, as_of_date, as_of_semantics | 014-017 | keep |
| Structure | Proxy identity/granularity | Regime value needs proxy and granularity. | Which proxy/frequency is this? | symbol, proxy role, source dir, granularity | regime_symbol, source_symbol_dir, regime_proxy_role, source_granularity, context_granularity | audits/builders | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| regime_context_id | identity | Regime | derived | Identity for regime context row. | Regime snapshots are source/time scoped. | 016/017 | none | keep |
| regime_symbol / proxy_role / source_symbol_dir | context | Regime | context | Defines market proxy. | Different proxies represent different regimes. | state/context builders | low | keep |
| source_granularity / context_granularity | lineage | Structure | context | Controls frequency/interpretation. | Granularities are not interchangeable. | builders/audits | low | keep |
| trading_date / session_open / as_of fields | asof_control | Temporality | context | Defines observable time. | Regime context must not use later-day info. | 016/017/ml/rl | high_if_ignored | keep |
| regime metric groups | derived_observable | Regime | derived/context | Represents broad market risk/trend/volatility context. | Broad regime conditions future smallcap behavior. | 016/017/clustering | medium | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| proxy_hierarchy_and_fallback_policy | Regime | Needed when multiple proxies or missing data exist. | 012/016 | Audit existing policy/registry before state build. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| end_of_day_regime_for_intraday_open_state | Later-day proxy data can leak into earlier intraday states. | Use as_of_utc and legal rolling values. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on as_of_utc/as_of_semantics
future_data_present: possible if full-day values used before available
outcomes_inline: false
lookback_policy_defined: required for intraday consumers
known_leakage_risks: end-of-day regime leakage into intraday states
```

## 12. Consumption Verdict

```text
market_state/event_state/scanners/backtests/ml/rl/alphaevolve=true with as-of/granularity policy; outcomes=true stratification.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: Regime context is essential, but intraday use needs strict as-of and proxy hierarchy.
required_actions: Define proxy hierarchy/fallback and intraday legality before 016/017.
next_table_dependency: 016 market state and 017 event state
```


