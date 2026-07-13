# TSIS Market Representation Architecture

## Chapter 2 --- Representation Philosophy

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 2. Representation Philosophy

## 2.1 The central idea

TSIS does not attempt to model trading strategies.

TSIS attempts to model the observable market.

Everything else is a consequence.

The architecture therefore follows:

``` text
Market
    ↓
Representation
    ↓
Research
    ↓
Knowledge
    ↓
Strategies
```

and never the opposite direction.

------------------------------------------------------------------------

## 2.2 Representation precedes intelligence

No machine learning model, optimizer or reinforcement learning algorithm
can discover knowledge that is absent from its representation.

Therefore the primary engineering objective is not model selection.

It is representation quality.

A richer, temporally valid representation increases the ceiling of every
downstream algorithm.

------------------------------------------------------------------------

## 2.3 Features represent properties

A feature is not:

-   a signal,
-   an opinion,
-   a recommendation,
-   a strategy,
-   a prediction.

A feature represents one observable property of the market.

Examples:

``` text
Spread
Trade Count Rate
Microprice
OFI
Gap %
ATR
Distance to VWAP
```

These properties become meaningful only when interpreted collectively.

------------------------------------------------------------------------

## 2.4 States represent situations

Individual features describe isolated properties.

States describe complete market situations.

A state is therefore an organized composition of multiple
representations evaluated at a legal decision timestamp.

------------------------------------------------------------------------

## 2.5 Knowledge is cumulative

Knowledge is accumulated through successive abstraction.

``` text
Observation
    ↓
Primitive
    ↓
Feature
    ↓
Representation
    ↓
State
```

Each level increases semantic content while reducing dependence on raw
observations.

------------------------------------------------------------------------

## 2.6 Model independence

The representation layer must remain valid independently of:

-   machine learning,
-   statistics,
-   reinforcement learning,
-   evolutionary search,
-   discretionary trading.

No consumer owns the representation.

------------------------------------------------------------------------

## 2.7 Strategy independence

Strategies consume representations.

Representations must never be redesigned merely because a particular
strategy changes.

Otherwise research becomes unstable and historical comparisons lose
meaning.

------------------------------------------------------------------------

## 2.8 Temporal correctness

Every representation must satisfy temporal legality.

Only information available at or before the decision timestamp may
contribute to a state.

Future information belongs exclusively to outcomes.

------------------------------------------------------------------------

## 2.9 Semantic stability

Feature names must represent stable concepts.

Implementations may evolve.

Definitions may become more accurate.

The semantic meaning of a feature should remain stable across versions
whenever possible.

If semantics change materially, a new version must be created.

------------------------------------------------------------------------

## 2.10 Representation as scientific infrastructure

The representation layer is not an implementation detail.

It is the scientific infrastructure of TSIS.

Every future feature family, dataset, builder, registry, validator and
learning algorithm inherits its validity from this representation
architecture.

Any optimization that compromises semantic clarity or temporal legality
must be rejected, even if it improves short-term predictive performance.
