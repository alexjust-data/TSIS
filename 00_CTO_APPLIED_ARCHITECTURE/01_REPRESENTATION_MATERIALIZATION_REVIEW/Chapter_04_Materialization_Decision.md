# Chapter 4 --- Materialization Decision

## Objective

Not every Canonical Market Representation should become a physical
implementation.

The purpose of this chapter is to define the institutional decision
process that determines whether a Canonical Market Representation should
be materialized within TSIS.

Materialization is therefore a deliberate architectural decision rather
than an automatic consequence of defining a representation.

------------------------------------------------------------------------

## Representation Before Materialization

A Canonical Market Representation may exist entirely within the
architectural layer of TSIS.

Its semantic definition remains valid even if no physical implementation
currently exists.

The existence of a canonical representation does not imply the existence
of:

-   a table;
-   a dataset;
-   a feature store;
-   a registry;
-   a service;
-   any other persistent implementation.

The canonical representation remains the source of meaning regardless of
its implementation status.

------------------------------------------------------------------------

## Why Materialize?

Materialization exists to make a Canonical Market Representation
operational.

Typical motivations include:

-   reproducible scientific research;
-   institutional persistence;
-   controlled downstream consumption;
-   versioning;
-   validation;
-   reproducibility;
-   performance;
-   interoperability between TSIS components.

These motivations justify implementation.

They do not redefine the representation itself.

------------------------------------------------------------------------

## Materialization Is Not Mandatory

The following principle governs the architecture:

``` text
Canonical Market Representation
≠
Mandatory Physical Implementation
```

Some representations may remain conceptual until a legitimate
institutional need appears.

Premature implementation increases maintenance costs, governance
complexity and semantic drift.

------------------------------------------------------------------------

## Decision Criteria

Before approving materialization, TSIS should answer the following
questions.

### Scientific Value

Does the implementation enable reproducible scientific work that cannot
reasonably be achieved otherwise?

### Architectural Consistency

Does the implementation preserve the canonical semantics without
introducing ambiguity?

### Governance

Can the implementation be versioned, validated and governed throughout
its lifecycle?

### Traceability

Can every implementation be traced back to exactly one Canonical Market
Representation?

### Consumer Need

Is there a legitimate institutional consumer requiring this
implementation?

------------------------------------------------------------------------

## Possible Decisions

After evaluation, one of the following decisions should be recorded.

``` text
Not Materialized

Candidate for Materialization

Approved for Materialization

Deprecated

Superseded
```

These decisions apply to the implementation process.

They never change the canonical meaning of the representation.

------------------------------------------------------------------------

## Separation of Responsibilities

This chapter decides whether implementation should exist.

Subsequent chapters determine:

-   how it will be represented physically;
-   which contracts are required;
-   how it will be built;
-   how it will be validated;
-   how it will become an institutional asset.

------------------------------------------------------------------------

## Fundamental Rule

Materialization exists to serve Canonical Market Representations.

Canonical Market Representations never exist to justify an
implementation.

Architecture drives implementation.

Implementation never drives architecture.
