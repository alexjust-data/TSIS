# Agent Continuation Guide 013-018 v0.1

Status: `working_guide`

Date: `2026-07-15`

Scope:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\00_EPISTEMOLOGICAL_architecture
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\01_REPRESENTATION_MATERIALIZATION_REVIEW
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\02_MATERIALIZATION_GOVERNANCE_REVIEW
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\013_ohlcv_1m_quote_guarded
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\014
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\015
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\016
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\017
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\018
```

---

## 1. Purpose Of This Guide

This document is for a new agent that must continue work on tables `013` to
`018` without already knowing TSIS.

The agent must not jump directly to columns, scripts, or parquet files.

The correct first question is:

```text
What is this table supposed to mean,
what authority governs it,
and what maturity level can it claim?
```

Only after that can the agent build, validate, or update a table.

---

## 2. Why The Three Review Folders Exist

The three folders are not optional reading.

They exist because TSIS discovered that table creation has three different
layers:

```text
Meaning
    -> Materialization logic
        -> Governance authorization
            -> Physical table work
```

That is why a new agent must read:

```text
00_EPISTEMOLOGICAL_architecture
01_REPRESENTATION_MATERIALIZATION_REVIEW
02_MATERIALIZATION_GOVERNANCE_REVIEW
```

before claiming to understand `013-018`.

---

## 3. What Each Folder Does

### 3.1 `00_EPISTEMOLOGICAL_architecture`

Function:

```text
Defines the language of TSIS.
```

It explains what TSIS means by:

```text
representation
feature
event
state
outcome
decision
phenomenon
knowledge
```

Use it to avoid semantic mistakes.

Example:

```text
Event State is not an event.
Event State is the market described relative to an event.
```

Without this folder, an agent may create technically valid columns that are
conceptually wrong.

### 3.2 `01_REPRESENTATION_MATERIALIZATION_REVIEW`

Function:

```text
Explains how a canonical idea can become a physical artifact.
```

It answers:

```text
When does an idea deserve to become a table?
When is a view enough?
When does materialization become justified?
What is the difference between canonical and physical representation?
```

Use it when deciding whether a planned table is:

```text
canonical representation
supporting representation
institutional artifact
engineering artifact
```

Without this folder, an agent may materialize everything as if every table had
the same architectural weight.

### 3.3 `02_MATERIALIZATION_GOVERNANCE_REVIEW`

Function:

```text
Applies the materialization framework to real TSIS cases.
```

It contains the practical governance chain:

```text
Contract
    -> Record
        -> Review
            -> Decision
                -> Authorization
```

Current important result:

```text
Event State candidate build is authorized.
Official Event State promotion is not authorized.
```

Use it to know what TSIS is allowed to build now.

Without this folder, an agent may confuse:

```text
candidate build allowed
```

with:

```text
official table promoted
```

Those are not the same.

---

## 4. Evaluation Of The Other Agent's Answer

The other agent's answer is mostly correct.

Accepted parts:

```text
1. It correctly separates three maturity levels:
   specification, candidate table, official table.

2. It correctly says that 000-012 may not all have the same maturity level.

3. It correctly says that Market State and Event State depend on upstream
   tables.

4. It correctly says that the correct build sequence is not "Event State
   first", but upstream tables first.

5. It correctly warns against starting table design by listing columns.
```

Important refinement:

```text
The new agent must still read the three architecture/review folders before
touching 013-018.
```

Reason:

```text
013-018 are not just independent engineering tasks.
They are the physical chain that feeds Market State and Event State.
```

The other agent is also right that a table can exist at different maturity
levels:

```text
specification_only
candidate_materialized
validated_candidate
official_promoted
```

But the agent must verify this from status matrices, manifests, validators and
contracts. It must not infer status from file existence.

---

## 5. Mandatory Reading Order For A New Agent

Before modifying anything related to `013-018`, the new agent must read:

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\00_EPISTEMOLOGICAL_architecture
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\01_REPRESENTATION_MATERIALIZATION_REVIEW
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\02_MATERIALIZATION_GOVERNANCE_REVIEW\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
```

Then the agent must read the operational authorities:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\data_foundation_outputs
```

Rule:

```text
00_CTO_APPLIED_ARCHITECTURE explains meaning and governance.
01_foundations defines operational authority.
scripts/tests execute the build.
manifests/status matrices prove what happened.
```

---

## 6. Maturity Levels

Every table must be classified before work starts.

```text
Level 1 - Specification
The document says what the table should represent.
No physical table is implied.

Level 2 - Candidate Table
A builder or parquet exists.
It may change.
It is not source of truth.

Level 3 - Official Table
The table has stable schema, builder, validator, manifest, evidence and
promotion status.
It can be treated as governed source of truth only within its declared scope.
```

Critical rule:

```text
File exists != official table.
Candidate exists != promoted table.
Manifest exists != downstream permission.
```

---

## 7. How 013-018 Should Be Understood

### 7.1 `013_ohlcv_1m_quote_guarded`

Role:

```text
Corrected/guarded intraday 1m foundation.
```

It feeds:

```text
014 master_intraday_bar_table
015 microstructure_features_table
016 market_state_table
017 event_state_table
018 intraday_scanner_candidates_table
```

Do not treat it as a generic raw table.

### 7.2 `014`

Target:

```text
master_intraday_bar_table
```

Role:

```text
Engineering/institutional base table for intraday bars.
```

It is upstream of features, scanners, states and intraday outcomes.

It does not need full canonical representation governance, but it must obey
schema, dataset contract, builder, validator, manifest and status matrix rules.

### 7.3 `015`

Target:

```text
microstructure_features_table
```

Role:

```text
Feature table.
```

It converts intraday bars/trades/quotes/episodes into governed observables.

It is not Market State.
It feeds Market State.

### 7.4 `016`

Target:

```text
market_state_table
```

Role:

```text
Canonical Core Representation.
```

It answers:

```text
How is the market at a decision timestamp?
```

It needs the full governance logic:

```text
RJR
MDR
Mapping
Traceability
Build authorization when required
```

### 7.5 `017`

Target:

```text
event_state_table
```

Role:

```text
Canonical Core Representation.
```

It answers:

```text
How is the market relative to an event?
```

Current governance status:

```text
candidate build allowed
official promotion not allowed
downstream production consumption not allowed
```

The active governance chain lives in:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\02_MATERIALIZATION_GOVERNANCE_REVIEW\03_event_state_governance
```

### 7.6 `018`

Target:

```text
intraday_scanner_candidates_table
```

Role:

```text
Candidate/event discovery surface.
```

It helps decide where to look.

It is not:

```text
Event State
Outcome
Decision
Reward
Execution truth
```

---

## 8. Correct Work Sequence

The practical sequence is:

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

The exact order may change for implementation reasons, but the dependency logic
must not be inverted.

Event State is authorized for candidate build, but it still depends on upstream
inputs.

---

## 9. How To Start A Table

For each table, the agent must answer these questions before coding:

```text
1. What problem does this table solve?
2. What does it represent?
3. Is it canonical, supporting, institutional, or engineering?
4. Which upstream tables does it consume?
5. Which downstream tables or experiments consume it?
6. What is the current maturity level?
7. Which schema contract governs it?
8. Which dataset contract governs it?
9. Which builder exists or must be created?
10. Which validator proves it?
11. Which manifest/status matrix will record the result?
```

Only then should the agent define or modify columns.

---

## 10. Definition Of Done For A Candidate Table

A candidate table is not done because a parquet exists.

It is done only when all of the following are explicit:

```text
schema contract read or updated
dataset contract read or updated
builder executed
validator passed or failure documented
candidate parquet generated
manifest generated
summary generated
status matrix updated
sample/explanatory document updated when applicable
full_universe_claim explicit
promotion_status explicit
downstream permission explicit
```

---

## 11. What The New Agent Must Not Do

The new agent must not:

```text
skip the three review folders;
treat 00_CTO_APPLIED_ARCHITECTURE as the operational source of truth;
treat candidate parquet as official output;
treat Event State build authorization as promotion;
start 013-018 by inventing columns;
merge Market State, Event State, Outcome or Decision semantics;
use future outcomes inside state/features;
claim ML/RL/backtest/execution readiness without status matrix evidence;
create more governance documents unless implementation is blocked.
```

---

## 12. Practical Rule

For this stage of TSIS, the working rule is:

```text
Read the three architecture/governance folders.
Use them to understand meaning, scope and authorization.
Then build tables using 01_foundations contracts, scripts, tests and manifests.
```

The goal is not more literature.

The goal is governed implementation.




