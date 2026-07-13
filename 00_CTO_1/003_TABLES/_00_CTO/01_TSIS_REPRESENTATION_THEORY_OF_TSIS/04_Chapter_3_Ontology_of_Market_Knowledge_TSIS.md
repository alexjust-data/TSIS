# TSIS Market Representation Architecture

## Chapter 3 --- Ontology of Market Knowledge

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 3. Ontology of Market Knowledge

## 3.1 Purpose

This chapter formally defines every semantic object allowed to exist
inside TSIS.

No implementation may introduce a new object without assigning it to
this ontology.

------------------------------------------------------------------------

# 3.2 Ontological hierarchy

``` text
Reality
    ↓
Observation
    ↓
Observable
    ↓
Primitive
    ↓
Feature
    ↓
Representation
    ↓
State
    ↓
Decision
    ↓
Outcome
```

Each level increases semantic abstraction while reducing dependence on
raw observations.

------------------------------------------------------------------------

# 3.3 Reality

Reality is the market itself.

Reality cannot be stored directly.

Reality is only accessible through observations.

Examples:

-   Orders submitted by participants
-   Executions
-   Quotes
-   Corporate actions
-   News
-   Trading halts

------------------------------------------------------------------------

# 3.4 Observation

An observation is a direct measurement captured from reality by a data
source.

Examples:

``` text
One trade
One quote update
One news item
One SEC filing
One halt notification
```

Properties:

-   immutable
-   timestamped
-   source dependent
-   may contain noise

Observations are never engineered.

------------------------------------------------------------------------

# 3.5 Observable

An observable is an observation whose semantic meaning has been
identified.

Examples:

``` text
Trade Event
Quote Event
Daily Bar
One-minute Bar
News Event
Halt Event
```

Observables remain close to the original measurement but already possess
domain meaning.

------------------------------------------------------------------------

# 3.6 Primitive

A primitive is the canonical representation of an observable.

Its purpose is normalization.

Examples:

``` text
Canonical Trade Primitive
Canonical Quote Primitive
Canonical 1m Bar
Canonical Daily Bar
```

Properties:

-   deterministic
-   normalized
-   reproducible
-   version controlled

Primitives are the lowest mathematical objects of TSIS.

------------------------------------------------------------------------

# 3.7 Feature

A feature is a deterministic mathematical transformation of one or more
primitives.

Examples:

``` text
Trade Count Rate
Spread
Microprice
Order Flow Imbalance
ATR
Gap %
Distance to VWAP
```

A feature represents one property of the observable market.

A feature is never:

-   a prediction
-   a signal
-   a strategy
-   a reward
-   an outcome

------------------------------------------------------------------------

# 3.8 Representation

A representation is a coherent collection of related features.

Examples:

``` text
Microstructure Representation
Intraday Representation
Daily Representation
Fundamental Representation
Regime Representation
```

Representations organize knowledge.

They do not make decisions.

------------------------------------------------------------------------

# 3.9 State

A state is the complete observable description of the market at one
legal decision timestamp.

Properties:

-   point-in-time
-   temporally legal
-   reproducible
-   consumer independent

States contain representations.

States never contain outcomes.

------------------------------------------------------------------------

# 3.10 Decision

A decision is produced by a policy acting on a state.

Examples:

``` text
Buy
Sell
Hold
Do Nothing
```

Decisions belong to the execution layer.

They never modify market representation.

------------------------------------------------------------------------

# 3.11 Outcome

An outcome describes what happened after the decision timestamp.

Examples:

``` text
Future Return
MFE
MAE
Breakout Success
Halt
Execution Cost
```

Outcomes belong exclusively to the evaluation layer.

------------------------------------------------------------------------

# 3.12 Allowed transformations

``` text
Observation
    ↓
Primitive

Primitive
    ↓
Feature

Feature
    ↓
Representation

Representation
    ↓
State

State
    ↓
Decision

Decision
    ↓
Outcome
```

------------------------------------------------------------------------

# 3.13 Forbidden transformations

The following derivations are illegal:

``` text
Outcome → Feature

Outcome → State

Decision → Feature

Decision → Primitive

Future Observation → Current State

Reward → Representation
```

Violating these rules introduces temporal leakage or semantic ambiguity.

------------------------------------------------------------------------

# 3.14 Semantic distance

Each ontological layer increases semantic distance from reality.

Example:

``` text
Trade Observation

↓

Trade Primitive

↓

Trade Count Rate

↓

Tape Acceleration

↓

Liquidity Representation

↓

Market State

↓

Entry Decision
```

Semantic distance is intentional.

Higher abstraction increases expressive power but also increases
dependency on lower layers.

------------------------------------------------------------------------

# 3.15 Constitutional rule

Every future table, feature family, builder, registry, validator, state
surface and machine learning component must map every object to exactly
one ontological level.

Objects belonging to different levels must never be merged into a single
semantic entity.

This ontology is the constitutional foundation of the TSIS knowledge
representation system.
