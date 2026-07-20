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

A variable is not admitted because it is common or convenient.

A variable is admitted only if it implements an accepted or candidate Information Object.

Each candidate Information Object belongs in:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_INFORMATION_OBJECTS
```

Do not create a file per variable.
Create a file per relevant Information Object.

---

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

The active dependency logic is:

```text
013 quote-guarded 1m base
    -> 014 master intraday bars
        -> 018 scanner/event candidates
            -> event windows
                -> 015 microstructure features
                    -> 016 market state
                        -> 017 event state
                            -> outcomes / downstream research
```

Implementation order may be adjusted, but dependency meaning must not be inverted.

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
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_INFORMATION_OBJECTS\CANDIDATES\trading_activity.md
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



