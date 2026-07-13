# TSIS Market Representation Architecture

## Chapter 1 --- Purpose

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 1. Purpose

## 1.1 Why TSIS exists

TSIS (Trading System Intelligence System) is not a trading system.

TSIS is a scientific research platform whose purpose is to build the
most faithful, reproducible and temporally valid representation of the
observable market possible.

Its objective is **not** to maximize short-term trading performance
directly.

Its objective is to maximize the quality of market representation from
which better scientific conclusions, better models and eventually better
decisions can emerge.

This distinction is fundamental.

``` text
TSIS does not study strategies.

TSIS studies markets.
```

Strategies are downstream consumers of market knowledge.

------------------------------------------------------------------------

## 1.2 Representation before prediction

Traditional quantitative systems often begin by asking:

``` text
Can I predict the next price movement?
```

TSIS asks a different question:

``` text
What is the best mathematical representation
of the observable market at this instant?
```

Prediction is considered a secondary problem.

A poor representation cannot be rescued by a sophisticated model.

A rich and temporally correct representation can support many different
modelling paradigms.

------------------------------------------------------------------------

## 1.3 Separation of concerns

Every object inside TSIS belongs to exactly one semantic layer.

``` text
Reality
Observation
Observable
Primitive
Feature
Representation
State
Decision
Outcome
```

Objects from different layers must never be mixed.

For example:

-   A feature is not a strategy.
-   A state is not a prediction.
-   An outcome is not an observable.
-   A decision is not part of market representation.

This separation is a constitutional rule of TSIS.

------------------------------------------------------------------------

## 1.4 Scientific principles

Every component of TSIS should satisfy the following principles:

### Observability

Every state must be constructible using only information available at
its decision timestamp.

### Reproducibility

The same raw inputs, contracts and versions must always produce the same
outputs.

### Determinism

Feature builders should be deterministic unless stochastic behaviour is
explicitly declared.

### Temporal legality

No future information may influence any representation intended for
decision making.

### Interpretability

Every feature must possess a documented mathematical definition and an
economic interpretation.

### Versionability

Representations evolve through explicit versioning rather than silent
modification.

------------------------------------------------------------------------

## 1.5 Scope

TSIS is designed to support:

-   market research,
-   statistical analysis,
-   hypothesis testing,
-   feature engineering,
-   event research,
-   pattern discovery,
-   supervised learning,
-   unsupervised learning,
-   imitation learning,
-   offline reinforcement learning,
-   evolutionary optimisation,
-   execution research.

No individual modelling paradigm owns the architecture.

The representation layer is model-independent.

------------------------------------------------------------------------

## 1.6 Independence from trading strategies

The market representation must remain valid even if every current
trading strategy disappears.

Likewise, new strategies should emerge from the representation rather
than forcing the representation to adapt to existing strategies.

Therefore:

``` text
Representation
    ↓
Research
    ↓
Strategies
```

never

``` text
Strategy
    ↓
Representation
```

------------------------------------------------------------------------

## 1.7 Independence from data vendors

No feature should depend semantically on a particular vendor.

Vendor-specific fields must first be converted into canonical primitives
before entering the representation layer.

This guarantees portability across future data providers.

------------------------------------------------------------------------

## 1.8 Independence from machine learning

Features are not created to satisfy a specific algorithm.

They are created to describe observable properties of the market.

Machine learning, statistics and optimisation consume those
representations but do not define them.

------------------------------------------------------------------------

## 1.9 Long-term objective

The long-term objective of TSIS is to become a continuously evolving
laboratory capable of discovering new market knowledge.

This requires:

-   stable ontological foundations,
-   canonical representations,
-   reproducible feature generation,
-   explicit temporal semantics,
-   rigorous separation between observation and evaluation.

Only under these conditions can future automated systems safely search
for new hypotheses without contaminating research through hidden leakage
or semantic ambiguity.

------------------------------------------------------------------------

## 1.10 Constitutional statement

The representation layer is the scientific foundation of TSIS.

Every future table, registry, builder, validator, feature family, state
surface and learning system shall remain compatible with the principles
defined in this architecture.

If a future implementation conflicts with these principles, the
implementation must change.

The ontology and representation architecture take precedence.
