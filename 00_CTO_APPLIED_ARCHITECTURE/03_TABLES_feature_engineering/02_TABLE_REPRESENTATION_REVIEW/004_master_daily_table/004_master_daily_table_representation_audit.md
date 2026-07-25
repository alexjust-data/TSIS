# 004 master_daily_table Representation Audit

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
table_number: 004
table_name: master_daily_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\master_daily_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\master_daily_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\master_daily_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\master_daily_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\master_daily_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\004_master_daily_table\004_master_daily_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\004_master_daily_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Canonical daily market context and daily price/volume observation layer.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Canonical daily market context and daily price/volume observation layer.
```

What does this table explicitly not represent?

```text
It is not intraday microstructure, event state, strategy signal, or future outcome label.
```

TSIS object type:

```text
context_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per instrument-session with daily OHLCV/context, expectedness, source lineage, quality gates and daily observables.
```

Which market representation families should it cover?

```text
Price: covered - see matrix below
Trend: not_primary - not a primary responsibility of this table
Volatility: covered - see matrix below
Liquidity: covered - see matrix below
Participation: not_primary - not a primary responsibility of this table
Microstructure: not_primary - not a primary responsibility of this table
Temporality: not_primary - not a primary responsibility of this table
Daily Context: covered - see matrix below
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
sample_columns_count: 71
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
master_daily_id, instrument_id, ticker, session_date, month, quality_gate_family, source_dataset, source_root, expected_session, expected_reason, expected_dataset_id, expected_source_root, data_present, missing_expected_data, source_daily_present, source_adjusted_present, open, high, low, close, volume, vwap, source_raw_vwap, transaction_count
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Price | Daily price level/range | Daily price anchors intraday interpretation. | What was the session price/range? | daily OHLC fields | daily OHLCV fields in 71-column sample | 016/017/backtests | keep |
| Volatility | Daily movement/range | Daily volatility changes event response and risk. | Was the day unusually volatile? | range, returns, true range/volatility | derived daily fields in sample | 016/ml/rl | keep |
| Liquidity | Daily tradability | Liquidity conditions signal reliability. | Was the instrument tradable enough? | volume, dollar volume, quality/liquidity gates | quality_gate_family, daily fields | scanners/016/backtests | keep |
| Daily Context | Session context | Intraday states need daily context. | What is the daily context around t? | session_date, expectedness, quality lineage | session_date, expected_dataset_id, expected_reason, source_root | 014-017 | keep |
| Structure | Lineage/quality | Daily context must be source-qualified. | Can this row be trusted and joined? | source, quality, expectedness ids | source_dataset, source_root, quality_gate_family | validators/status | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| instrument_id / ticker / session_date | identity | Structure | context | Defines daily grain. | Daily context must join to identity/session. | 014-017/outcomes | medium_if_joined_wrong | keep |
| daily OHLCV group | raw_observable | Price | raw/derived | Captures daily baseline. | Daily price/volume condition intraday behavior. | 016/017/backtests | low | keep |
| daily return/range/volatility group | derived_observable | Volatility | derived | Summarizes movement intensity. | State depends on volatility context. | 016/ml/rl | medium_if_future_window | keep |
| quality_gate / expected_* / source_* | quality_gate | Structure | governance/context | Prevents silent low-quality consumption. | Dataset reliability changes feature trust. | builders/validators | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| explicit_asof_for_same_day_fields | Daily Context | Needed to know if same-day fields are legal intraday before close. | 016/intraday builders | Separate prior-day from completed-session context. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| future_completed_day_fields_at_intraday_t | Completed daily high/low/close can leak before close. | Use prior-day or rolling legal-at-t equivalents. | move |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional
future_data_present: possible if completed-session fields feed intraday t before close
outcomes_inline: false
lookback_policy_defined: required for intraday consumers
known_leakage_risks: same-day high/low/close after t
```

## 12. Consumption Verdict

```text
market_state/event_state/scanners/backtests/ml/rl/alphaevolve=true only with as-of policy; outcomes=true for context/stratification, not labels.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: Daily variables are justified, but intraday use must separate completed-day fields from legal-at-t fields.
required_actions: Document legal lookback/as-of use before 016/017 consume same-day daily fields.
next_table_dependency: 014/016 intraday and market state context
```


