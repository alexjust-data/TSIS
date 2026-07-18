# Chapter 6 --- Materialization Strategies

## Objective

Once a Physical Representation has been approved, TSIS must decide how
that representation will be materialized.

The purpose of this chapter is to define the architectural principles
governing materialization strategies.

This chapter does not prescribe specific technologies.

Instead, it defines how implementation choices shall preserve the
integrity of the Canonical Market Representation.

------------------------------------------------------------------------

## Strategy Before Technology

A materialization strategy answers:

``` text
How should this Physical Representation exist within TSIS?
```

It does not answer:

``` text
Which database should we use?
```

Technology is an implementation decision.

Materialization strategy is an architectural decision.

------------------------------------------------------------------------

## Guiding Principle

The selected strategy shall be the simplest implementation capable of
satisfying the institutional requirements of the representation.

Those requirements may include:

-   persistence;
-   reproducibility;
-   governance;
-   versioning;
-   consumer access;
-   validation;
-   scalability;
-   latency.

No implementation should introduce semantics that are absent from the
Canonical Market Representation.

------------------------------------------------------------------------

## Possible Strategies

Depending on its institutional purpose, a Physical Representation may be
implemented as:

``` text
Dataset

Table

Feature Store

Event Store

Knowledge Graph

Registry

State Service

Vector Store

Materialized View

Other governed implementations
```

These are implementation strategies.

They are not different representations.

------------------------------------------------------------------------

## Choosing a Strategy

The choice should be based on institutional requirements rather than
engineering preference.

Typical evaluation criteria include:

### Consumer Profile

Who consumes the representation?

Examples:

-   research;
-   backtesting;
-   machine learning;
-   execution;
-   governance;
-   auditing.

### Access Pattern

How will consumers use the representation?

Examples:

-   sequential reads;
-   point lookups;
-   streaming;
-   graph traversal;
-   vector similarity;
-   archival storage.

### Update Behaviour

Does the representation evolve:

-   continuously;
-   periodically;
-   only through governed releases?

### Governance Requirements

Can the chosen strategy preserve:

-   traceability;
-   versioning;
-   validation;
-   reproducibility;
-   institutional status?

------------------------------------------------------------------------

## Strategy Independence

The same Canonical Market Representation may legitimately adopt
different materialization strategies during its lifetime.

For example:

``` text
Research Dataset
        ↓
Feature Store
        ↓
State Service
```

Changing the strategy does not imply changing the canonical meaning.

Only the implementation changes.

------------------------------------------------------------------------

## Relationship with Table Creation

Within the current implementation of TSIS, many strategies will
ultimately result in datasets and tables.

When that occurs, responsibility passes to the engineering process
governed by the Table Creation Process and its associated contracts,
schemas, builders and validators.

This document decides the strategy.

The engineering process decides the implementation.

------------------------------------------------------------------------

## Fundamental Rule

Materialization strategy shall always be selected to preserve the
Canonical Market Representation.

Technology serves the representation.

The representation never adapts its meaning to satisfy technology.
