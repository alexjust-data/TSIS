# 010 news_context_table Representation Audit

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
table_number: 010
table_name: news_context_table
table_status: official_or_candidate_foundation_artifact_to_be_confirmed_by_registry
audit_status: draft_technical_audit_v0_1
date: 2026-07-16
auditor: Codex
```

## 2. Authority Paths

Required evidence paths:

```text
schema_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\news_context_table_schema_contract.md [exists]
dataset_contract: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\news_context_table_dataset_contract_v0_1.md [exists]
dataset_registry: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\news_context_table_registry_entry.yaml [exists]
consumption_policy: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\news_context_table_consumption_policy.md [exists]
validators: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\news_context_table_validators.md [exists]
status_matrix: C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md [exists]
physical_sample: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\010_news_context_table\010_news_context_table.md [exists]
builder_or_manifest: C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\010_news_context_table\README.md [not_found_in_local_check]
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
For this table, the contribution is: As-of news/information-arrival context for instruments and events.
```

What information can help explain or predict the future behavior of the phenomenon represented?

```text
Only variables that preserve this table's role, have clear time legality and can be consumed downstream without turning context or governance into noisy predictive baggage.
```

## 4. Being Of The Table

What phenomenon or institutional object does this table represent?

```text
As-of news/information-arrival context for instruments and events.
```

What does this table explicitly not represent?

```text
It is not a direct price feature, outcome label, or legal input without publication/availability timing.
```

TSIS object type:

```text
context_table
```

## 5. Conceptual Expected State

What should this table contain conceptually?

```text
One row per news article/context observation with article identity, source path, hashes, author/source metadata, instrument identity and timestamps.
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
Daily Context: not_primary - not a primary responsibility of this table
Intraday Context: not_primary - not a primary responsibility of this table
News: covered - see matrix below
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
sample_columns_count: 71
materialization_status: validated_candidate_or_official_depending_on_registry_status
promotion_status: must be confirmed by dataset registry / certification matrix, not inferred from folder presence.
```

First parsed physical columns:

```text
news_context_id, ticker, source_path_ticker, instrument_id, source_dataset_id, source_subblock, article_id, article_url, article_url_hash, title, title_hash, author, publisher_name, publisher_homepage_url, publisher_logo_url, publisher_favicon_url, image_url, amp_url, description, published_utc, published_utc_raw, published_date, as_of_utc, as_of_date
```

## 7. Variable Family Matrix

| Family | Phenomenon represented | Scientific hypothesis | Questions answered | Minimal variables expected | Physical variables observed | Consumer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| News | Information arrival | News can change attention, liquidity, volatility and event response. | What public information was available around t? | article id, title/source, published/as-of timestamps | news_context_id, article_id, article_url, article_url_hash, title, title_hash, author | 016/017/event research | keep |
| Events | News as event/context | Some news anchors or explains event windows. | Is this article an event source/context? | source dataset/subblock, article identity, instrument | source_dataset_id, source_subblock, article_id, ticker, instrument_id | 007/017 | keep |
| Structure | Source/dedup identity | News is noisy and must be deduplicated. | Is this article unique/traceable? | url/title hashes, source path, author/source | article_url_hash, title_hash, source_path_ticker, author | validators/audits | keep |

## 8. Variable Audit

| Variable or group | Class | Family | Raw / derived / contextual | Why it exists | Hypothesis represented | Downstream consumer | Leakage risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| news_context_id / article_id | identity | News | derived/raw | Article/context identity. | Information objects need stable identity. | 017/research | none | keep |
| url/title hashes | lineage | News | raw/derived | Traceability and deduplication. | Duplicates distort attention. | validators/features | low | keep |
| ticker / source_path_ticker / instrument_id | identity | Structure | context | Binds news to instrument. | News-instrument mapping can be uncertain. | 016/017 | medium | keep |
| news timing group | asof_control | Temporality | context | Determines observability at t. | Only published/available news can condition state. | state/event builders | high_if_missing | keep |

## 9. Missing Variables

Variables or families that should exist but are missing:

| Missing variable | Family | Why needed | Target table | Blocking evidence |
| --- | --- | --- | --- | --- |
| publication_and_ingestion_timestamp_policy | News | Defines exact observable time. | 010/016/017 | Audit full schema for timestamp fields. |

## 10. Noise / Overlap / Misplaced Variables

Variables that may create noise, duplicate another table or live in the wrong layer:

| Variable | Problem | Correct location | Action |
| --- | --- | --- | --- |
| raw_text_features_without_hypothesis | Text-derived variables can become noisy/leaky. | Feature registry or dedicated news feature table. | reduce |

## 11. Temporal Legality And Leakage

```text
as_of_safe: conditional on publication/ingestion timestamp
future_data_present: possible if joined by date without time
outcomes_inline: false
lookback_policy_defined: required for news windows
known_leakage_risks: using articles after event/state timestamp
```

## 12. Consumption Verdict

```text
market_state/event_state/scanners/backtests/ml/rl/alphaevolve=true with publication-time policy; outcomes=true stratification.
```

## 13. Final Audit Decision

Decision:

```text
decision: accepted_with_gaps
reason: News context is useful, but timestamp legality and text-feature control must be explicit.
required_actions: Verify timestamp schema and publication/ingestion precedence before 016/017.
next_table_dependency: 017 event state and event candidate research
```


