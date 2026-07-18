# 006 halts_table Representation Audit

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
table_number: 006
table_name: halts_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\halts_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\halts_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\halts_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\halts_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\halts_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\006_halts_table\006_halts_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\006_halts_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: Governed halt events and halt/resume context.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
Governed halt events and halt/resume context.
```

What does this table explicitly not represent?

```text
It is not general market state, price feature table, or outcome label.
```

TSIS object type:

```text
event_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per halt/resume source event with event identity, issuer/listing context, timing, source lineage and duplicate handling.
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
sample_columns_count: 50
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
halt_event_id, source_event_key, source_row_number, duplicate_source_event_key, source_dataset_id, source, source_priority, ticker, issuer_name, listing_exchange, halt_date, halt_start_et, resume_quote_et, resume_trade_et, halt_code, halt_type, raw_reason, release_no, item_link, url_source, is_sec_suspension, halt_event_state, event_granularity, quality_state
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Events | Trading halt occurrence | Halts reshape liquidity, volatility and event response. | Was trading halted around t/event? | halt id, source key, halt/resume time, reason/type | halt_event_id, source_event_key, halt_date, halt_start_et | 007/017/outcomes | keep |
| Temporality | Session interruption | State legality changes during halt intervals. | Is t inside a halt or near resume? | halt_start, resume time, session date | halt_date, halt_start_et | 016/017/backtests | keep |
| Structure | Source/dedup governance | Event data must be deduplicated and sourced. | Is this halt unique and authoritative? | source ids, duplicate flags, source priority | source_event_key, duplicate_source_event_key, source_dataset_id, source_priority | 007/validators | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| halt_event_id / source_event_key | event_descriptor | Events | raw/derived | Creates event identity/traceability. | Halt windows need stable anchors. | 007/017/outcomes | none | keep |
| ticker / issuer_name / listing_exchange | identity | Structure | context | Binds event to listing context. | Halt interpretation depends on listing identity. | event windows/audits | medium_if_no_instrument_id | keep |
| halt_date / halt_start_et | asof_control | Temporality | raw/context | Defines when halt affects observability. | Market state cannot be normal during halt. | 016/017 | low | keep |
| source / source_priority / duplicate flag | lineage | Structure | governance | Controls conflicts and duplicates. | Halt events need source governance. | validators/007 | low | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| resume_timestamp_and_reason_coverage | Events | Needed to fully describe duration/reason. | 006/007/017 | Check full schema/source completeness. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| None identified in this short audit | n/a | n/a | keep |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on public halt timestamp/source release
future_data_present: false if joined by observed time only
outcomes_inline: false
lookback_policy_defined: required for event windows
known_leakage_risks: using full halt duration before resume is known
```

## 12. Consumption Verdict

```text
market_state=true halt context; event_state=true anchor/context; scanner=true exclusions/triggers; outcomes=true event labels/strata; backtest/ml/rl/alphaevolve=true with event-time policy.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: Halt variables represent a real event family, but duration/reason/as-of handling must be verified.
required_actions: Confirm resume/reason fields and define full-duration legality after resume.
next_table_dependency: 007_event_windows_table and 017_event_state_table
```


