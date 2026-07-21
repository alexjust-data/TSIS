# News / Catalyst Context - State Builder Validation v0.1

Status: `builder_validation_design_v0_1`
Date: `2026-07-21`
Scope: `phase_b_builder_validation_design`

Este documento define la validacion necesaria para comprobar si el builder
puede resolver legalmente el perfil minimo de `News / Catalyst Context`.

No ejecuta un builder.
No cambia codigo.
No modifica schemas.
No materializa `Market State`.
No autoriza consumo operativo.

## 1. Validation Decision

```text
information_object = News / Catalyst Context
builder_validation_decision = design_ready_pending_execution
validation_execution_status = not_executed
operational_mapping = news_catalyst_context_operational_mapping_v0_1.md
production_builder_authorized = false
state_consumption_authorized = false
physical_variables_authorized = false
schema_change_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
market_state_integration_authorized = false_until_builder_validation_execution
```

## 2. Validation Target

```text
builder_validation_profile = news_catalyst_presence_freshness_core_v0_1
mapping_profile = market_state_external_context
profile_role = market_state_context_minimum
validation_scope = non_production_design_validation
```

Modelos incluidos:

```text
news_presence_model
news_freshness_model
article_count_model_as_restricted_extension
keyword_flag_model_as_restricted_extension
```

No incluidos:

```text
sentiment_model
novelty_model
catalyst_category_model
post_news_market_response
```

## 3. Required Resolution Gates

```text
gate_1_object_governance =
  News / Catalyst Context admitted with restrictions and mapped with restrictions.

gate_2_asof_legality =
  published_utc and as_of_utc are present and <= decision_timestamp.

gate_3_attribution_policy =
  ticker/instrument attribution is governed.

gate_4_window_policy =
  article windows are closed and source filters are explicit.

gate_5_dictionary_policy =
  keyword flags require dictionary version and field scope.

gate_6_model_block =
  sentiment, novelty and catalyst category remain excluded unless governed.

gate_7_outcome_separation =
  no post-news price, liquidity or volume response enters X.
```

## 4. Expected Source Resolution

```text
010_news_context_table:
  published_utc
  as_of_utc
  article_count_WINDOW
  news_freshness_minutes
  news_keyword_flag
```

Blocked sources:

```text
future sentiment model output
future novelty model output
ungoverned catalyst taxonomy
future market response tables
```

## 5. Required Checks

```text
1. Every article used is published/as_of <= decision_timestamp.
2. Latest article freshness never references a future article.
3. Article windows are closed and scoped to governed attribution.
4. Keyword flags carry dictionary version.
5. Sentiment, novelty and category are absent from core output.
6. Lineage includes source table, version, article scope, cutoff and quality flag.
```

## 6. Output Authority

Passing this validation may authorize only:

```text
news_catalyst_context_market_state_integration_design
```

It does not authorize:

```text
production_builder
state_consumption
schema_change
physical_materialization
dataset_promotion
unversioned_sentiment_truth
ungoverned_catalyst_taxonomy
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\news_catalyst_context_operational_mapping_v0_1.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\news_catalyst_context_formal_admission_v0_1.md
```
