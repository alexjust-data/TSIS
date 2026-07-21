# 02_TABLE_REPRESENTATION_REVIEW Local Rules

Status: `local_rules_v0_3_entity_function_refinement`
Date: `2026-07-20`

These rules govern work inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW
```

They refine the parent feature engineering rules and must be used when reviewing tables `000` through `018`.

---

## 1. Role

`02_TABLE_REPRESENTATION_REVIEW` is the table-level audit surface for TSIS market representation work.

Its purpose is to make every table review comparable across:

```text
000-012 existing Data Foundation outputs
013 quote-guarded intraday base
014-018 target/candidate downstream tables
```

It is not a promotion authority.

Official table status must still be proven through:

```text
schema contract
dataset contract
registry entry
consumption policy
builder
validator
manifest
summary
status matrix
pytest result
physical artifact inspection
```

---

## 2. Table Maturity Levels

Every table review must classify the table before making downstream claims:

```text
specification_only
candidate_materialized
validated_candidate
official_promoted
historical_or_superseded
```

Rules:

```text
file exists != official table
parquet exists != promoted table
manifest exists != downstream permission
Graphify node exists != operational proof
```

---

## 3. Two-Level Table Review Standard

Every table review must answer two levels of questions.

Level 1 decides whether the table has conceptual reason to exist.

Level 2 decides whether the table is physically, temporally and institutionally governed well enough to be consumed or redesigned.

---

## 4. Level 1 - Architectural Questions

Every table review must answer:

```text
1. What entity, representation or institutional function does the table materialize?

1.1. Does it represent market information, infrastructure, context, quality, governance, event, state or outcome?

1.2. If it stores market information, what market phenomena do the stored information help describe?

2. Why does it deserve to exist as its own entity?

3. What scientific questions must it answer?

4. What other representations consume it?

5. What minimum information does it need to contain?

6. Only now: what attributes must it have?
```

Operational rule:

```text
Do not start by listing columns.
Start by defining representation responsibility.
Do not force institutional infrastructure tables into a market-phenomenon frame.
Then derive the minimum required attributes.
```

Examples:

```text
001_market_calendar
= institutional temporal infrastructure
= not buying pressure, liquidity or momentum

003_dataset_certification_matrix
= governance and quality infrastructure
= not a market phenomenon

004_master_daily_table
= daily instrument market representation
= can describe price, range, liquidity/participation context and daily tradability
```

---

## 5. Level 2 - Physical And Boundary Questions

Every table review must also answer:

```text
7. What is its grain?

8. What is its primary key?

9. What does it consume?

10. What does it produce?

11. What information must it not contain?

12. Which columns are identity, observables, derived values, quality, lineage, as-of, governance or outcomes?

13. Which Information Objects does it implement fully or partially?

14. Which variables are not justified yet?

15. What information is missing?

16. Is there overlap with another table?

17. Is temporal legality defined?

18. What is its physical, contractual, validated and promoted status?
```

Boundary rule:

```text
A table can be useful and still not be official.
A table can be materialized and still not be promoted.
A table can contain variables and still not justify all of them.
```

---

## 6. Column Classification Rule

Every non-trivial table review must classify columns into these categories when possible:

```text
identity
observable
derived
quality
lineage
as_of
governance
outcome
```

Outcome columns must not be allowed into observable X / Market State inputs unless an explicit policy states otherwise.

---

## 7. Information Object Rule

Definition of Information Object:

```text
A semantic unit of information that TSIS decides to preserve
about one or more observable phenomena, independent of its
Representation Model and physical implementation.
```

An Information Object is not the representation itself.
It is what must be represented.

Example:

```text
Liquidity
= Information Object

trading cost + depth + availability
= Representation Model

spread_bps + depth + quote_count
= Physical Implementation
```


### Taxonomy Axis Rule

Do not use a single generic `family` field to classify Information Objects, variables or table content.

Use separate axes:

```text
information_object_family
= semantic meaning of the Information Object.

source_domain
= observable source domain.

temporal_resolution
= time scale or event window.

institutional_role
= role inside TSIS.
```

Allowed starting values:

```text
information_object_family:
- Price Dynamics
- Trading Activity
- Liquidity
- Market Microstructure
- Instrument Context
- External Context
- Market Context

source_domain:
- OHLCV
- Trades
- Quotes
- News
- Fundamentals
- SEC
- Short
- Halts
- Reference
- Market / Economic Context

temporal_resolution:
- daily
- intraday_bar
- second
- event_window
- as_of

institutional_role:
- observable
- quality
- lineage
- governance
- outcome
```

`Feature Family`, `source family`, `dataset family`, `event family`, `quality family` and `outcome family` are not interchangeable.
If a legacy document uses `family`, table review must state which axis it means.

A variable is not admitted because it is common or convenient.

Table review may discover candidate Information Objects, but it does not admit them.

Object Discovery Process may start from:

```text
market phenomena
research questions
RAW observables
derivable capabilities
existing tables
existing variables
```

Object Discovery Process may identify, inventory or evaluate:

```text
candidate_information_object
candidate_variable
possible_representation_model
source_table_evidence
```

Object Admission Process must follow the scientific direction:

```text
phenomenon_or_scientific_need
    -> Information Object
        -> Representation Model
            -> implementation candidates
                -> temporal legality
                    -> admission decision
```

A variable may be identified, inventoried or evaluated if it implements a candidate Information Object.

A variable may be admitted for canonical state consumption only if it implements an accepted or accepted-with-restrictions Information Object, under the applicable representation model and temporal policy.

Variable states:

```text
candidate_variable
= detected during table/capability review; not authorized for State.

admitted_variable
= implements an accepted or accepted-with-restrictions Information Object under an approved representation model.

state_eligible_variable
= admitted_variable that also passes temporal legality, quality, coverage and consumption policy gates for a specific State build.
```

Each candidate Information Object belongs in:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS
```

Do not create a file per variable.
Create a file per relevant Information Object.

Do not let existing tables define scientific meaning by themselves.
Tables can reveal candidates; admission defines meaning.

---

---

## 7.1 Market State Profile Rule

A canonical Market State must not be interpreted as a universal wide table containing every attribute any consumer may want.

Canonical Market State means:

```text
one governed state semantics
one stable market_state_id
common temporal legality rules
compatible physical representation profiles
```

Allowed conceptual profile pattern:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Common join identity across profiles:

```text
market_state_id
instrument_id
decision_timestamp
representation_profile_version
```

Table review must distinguish:

```text
core_state_candidate
profile_extension_candidate
consumer_specific_view
not_state_eligible
```

A downstream consumer request is not sufficient justification to add a variable to `market_state_core`.
Heavy or specialized observables require a governed profile or extension.


---

## 7.2 Event State Consumption Legality Rule

`state_role` and `consumption_legality` must be treated as independent classifications.

```text
state_role
= temporal/event-relative role.

consumption_legality
= downstream input legality.
```

Allowed `consumption_legality` values:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

Rules:

```text
pre_event / at_event may be decision_safe only when cutoff, role and consumer gates pass.
post_event / post_event_review may be valid for research but must not be decision_safe for event-time prediction.
ML/backtest feature X requires consumption_legality = decision_safe.
```

Table reviews must not infer input legality from `state_role` alone.


## 8. Required Evidence For Table Status

A table status claim must cite at least one relevant authority:

```text
schema contract
dataset contract
dataset registry entry
data consumption policy
validator
builder
manifest
summary
status matrix
pytest result
physical artifact inspection
```

Do not infer status from folder naming alone.

---

## 9. 013-018 Working Rule

The active 013-018 architecture is not a single linear chain.

Canonical DAG:

```text
raw OHLCV 1m
+ 013 quote-guarded overlay
+ corporate actions / quality
        -> 014 master_intraday_bar_table

raw trades
+ raw quotes
+ eligibility policies
+ quality gates
+ governed timestamps / event windows when required
        -> 015 microstructure_features_table

000-015 governed context and observables
+ 018 intraday_scanner_candidates_table when applicable and temporally legal
        -> 016 market_state_table

016 market_state_table
+ event registry / source events
+ 007 event_windows_table
        -> 017 event_state_table
```

Dependency classes:

```text
semantic_dependency
= one artifact needs the meaning of another artifact to be correctly defined.

physical_source_dependency
= one artifact reads fields or rows from another physical source.

eligibility_dependency
= one artifact depends on filters, quality gates, timestamp rules or observability policies.

materialization_selection_dependency
= one build is restricted to a selected subset of instruments, timestamps, events or windows.
```

Rules:

```text
014 master_intraday_bar_table and 015 microstructure_features_table are sibling representation surfaces.
They are not a mandatory linear dependency chain.

015 full/general microstructure features may be built from trades, quotes, eligibility policies,
quality gates and governed timestamps without a universal semantic dependency on 018.

A selective event-window materialization profile of 015 may use windows or candidates produced
from 018 or 007. That is a materialization_selection_dependency, not a universal semantic_dependency.

018 intraday_scanner_candidates_table is not a universal prerequisite for 016 market_state_table.
It is optional scanner/candidate context when applicable and temporally legal.

016 market_state_table consumes governed context and observables from 000-015, plus 018 only
when the representation contract and temporal policy allow it.

017 event_state_table consumes or references 016 market_state_table plus governed event identity
and 007 event_windows_table. It does not redefine the base market state.
```

Do not infer semantic dependency from implementation order or selective materialization strategy.

---

## 10. 013 Specific Rule

`013_ohlcv_1m_quote_guarded` must be read as:

```text
raw ohlcv_1m
+
repair_manifest_lt1b_v0_1.parquet
=
ohlcv_1m_quote_guarded view
```

It is a governed overlay/view, not an official full-universe physical replacement tree.

---

## 11. Per-Table Folder Organization

Each table review folder should separate three different concerns:

```text
004_master_daily_table/
|
|-- 004_master_daily_table.md
|-- table_representation_audit_ES.md
`-- object_candidates.md
```

The exact table file may keep the table-specific prefix for compatibility, but the roles must remain separated.

### `<table_name>.md`

Describes the current state of the table or dataset.

It should cover:

```text
declared purpose
grain
columns
contracts
schema
materialization
builders
validators
status
physical paths when verified
```

It must not become the conceptual audit and must not promote the table by itself.

### `table_representation_audit_ES.md`

Applies this `LOCAL_RULES.md` to the complete table.

It should cover:

```text
responsibility
boundaries
consumes
produces
minimum information
attributes
redundancies
missing information
temporal legality
institutional status
Market State / Event State consumption decision
```

It is the table-level review, not the scientific record of every Information Object.

### `object_candidates.md`

This file is optional at the start, but recommended when a table exposes candidate Information Objects.

It acts as a bridge between table review and Information Object admission.

Example:

```text
Candidate Object:
Trading Activity

Candidate variables:
daily_volume
transaction_count
dollar_volume
rvol_20d

Status:
pending_admission

Reference:
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\CANDIDATES\trading_activity.md
```

Rule:

```text
Do not mix table audit with the scientific object record.
The table audit identifies candidates.
The Information Object file evaluates and admits or rejects them.
```

---
## 12. Changelog Rule

Update:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\CHANGELOG.md
```

when a table reading, maturity level, operational dependency, template or validation status changes.

Do not log trivial formatting.

---

## 13. Final Rule

The goal of table review is not more literature.

The goal is to decide:

```text
what the table represents
what it is allowed to contain
what it actually contains
what it lacks
what must be fixed before Market State / Event State can consume it
```



