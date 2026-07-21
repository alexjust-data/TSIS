# News / Catalyst Context - Operational Mapping v0.1

Status: `operational_mapping_v0_1`
Date: `2026-07-21`
Scope: `phase_b_information_object_to_physical_state_bridge`

Este documento conecta `News / Catalyst Context` con modelos aprobados,
capacidades derivables, variables candidatas, tablas fuente y perfiles de
State previstos.

No modifica schemas, builders, datasets ni materializaciones.
No autoriza consumo productivo de State.

## 1. Governance Input

```text
information_object = News / Catalyst Context
formal_admission = accepted_with_restrictions
operational_mapping_decision = mapped_with_restrictions
operational_mapping_phase_b_authorized = true
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false_until_phase_b_artifacts
physical_materialization_authorized = false
dataset_promotion_authorized = false
builder_validation_required = true
market_state_integration_required = true
event_state_integration_required = true
operational_promotion_authorized = false_until_phase_b_gates
```

## 2. Approved Semantic Capability

```text
News / Catalyst Context debe ser capaz de representar presencia, frescura,
intensidad y tipo provisional de informacion noticiosa observable legalmente
as-of.
```

## 3. Approved Representation Models

| Representation model | Mapping status | Operational role |
| --- | --- | --- |
| `news_presence_model` | `mapped_as_core_minimum` | As-of news presence context. |
| `news_freshness_model` | `mapped_as_core_minimum` | Recency / lag context. |
| `article_count_model` | `extension_pending_window_policy` | Legal count/intensity context. |
| `keyword_flag_model` | `restricted_extension_pending_dictionary_policy` | Provisional catalyst proxy. |
| `sentiment_model` | `blocked_until_versioned_model` | Research/extension only. |
| `novelty_model` | `blocked_until_versioned_model_and_baseline` | Research/extension only. |
| `catalyst_category_model` | `blocked_until_governed_taxonomy` | No institutional truth without taxonomy. |

## 4. Capability To Physical Mapping

| Capability | Candidate variable | Source table | State profile | Temporal rule |
| --- | --- | --- | --- | --- |
| `news__published_utc` | `published_utc` | `010_news_context_table` | source input | Published timestamp must be known as-of. |
| `news__as_of_utc` | `as_of_utc` | `010_news_context_table` | source input | Availability timestamp must be <= decision_timestamp. |
| `news__article_count_WINDOW` | `article_count_WINDOW` | `010_news_context_table`, future state builder | `market_state_external_context`, `event_state_context` | Window closed; eligible articles published/as-of <= t. |
| `news__freshness_minutes` | `news_freshness_minutes` | `010_news_context_table`, future state builder | `market_state_external_context`, `event_state_context` | Latest eligible article must be <= t. |
| `news__keyword_flag` | `news_keyword_flag` | `010_news_context_table`, future state builder | restricted extension | Requires dictionary version and field scope. |
| `news__sentiment_score` | `news_sentiment_score` | future model output | blocked extension | Requires versioned model, validation and leakage policy. |
| `news__novelty_score` | `news_novelty_score` | future model output | blocked extension | Requires prior-only baseline and model governance. |

## 5. Source Tables And Temporal Legality

```text
010_news_context_table:
    governed news timestamps, attribution and text fields.

future model outputs:
    sentiment, novelty and catalyst category only after versioned policies.
```

## 6. Operational Restrictions

```text
1. No article is eligible unless published/as_of <= decision_timestamp.
2. Article count requires source filter, attribution scope and closed window.
3. Keyword flags require dictionary version.
4. Sentiment requires versioned model and leakage validation.
5. Novelty requires prior-only corpus/baseline.
6. Catalyst category requires governed taxonomy.
7. Future market response to news is outcome only.
```

## 7. Required Builder Validation

```text
1. published_utc and as_of_utc are present and legal.
2. Attribution to ticker/instrument is governed.
3. Article windows are closed.
4. Sentiment/novelty/category do not appear unless governed.
5. No post-event market response appears in X.
```

## 8. Authorized And Non-Authorized Consumers

Authorized:

```text
builder_validation_design
market_state_integration_design_after_builder_validation
event_state_integration_design_after_market_state_integration
research_planning
```

Not authorized:

```text
production_market_state_builder
state_consumption
canonical_schema_change
physical_state_materialization
dataset_promotion
unversioned_sentiment_truth
ungoverned_catalyst_taxonomy
```

## 9. Review Triggers

```text
1. News source/as_of policy changes.
2. Sentiment or novelty model is versioned and validated.
3. Catalyst taxonomy is approved.
4. Builder Validation detects timestamp or attribution ambiguity.
```

## 10. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\news_catalyst_context_formal_admission_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\05_DATA_derivable\01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
```

