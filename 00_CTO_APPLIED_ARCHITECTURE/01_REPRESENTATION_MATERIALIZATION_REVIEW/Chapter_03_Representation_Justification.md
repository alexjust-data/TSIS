# Chapter 3 --- Representation Justification

## Objective

Not every concept deserves to become a Canonical Market Representation.

The purpose of this chapter is to define the institutional criteria by
which TSIS justifies the existence of a representation before any
implementation, contract or physical artifact is created.

A representation is never created because it is technically convenient.

It is created because it is architecturally necessary.

------------------------------------------------------------------------

## The Principle of Justification

Every Canonical Market Representation shall have an explicit and
documented justification.

Without an approved justification, no representation may enter the
institutional architecture of TSIS.

Justification precedes:

-   schemas;
-   dataset contracts;
-   builders;
-   validators;
-   registries;
-   physical implementations.

------------------------------------------------------------------------

## Representation Is a Scientific Decision

Creating a new representation is an architectural decision.

It changes the conceptual model of the market maintained by TSIS.

Therefore, the burden of proof belongs to the proposed representation.

The question is never:

``` text
Can we build it?
```

The first question is:

``` text
Should it exist?
```

------------------------------------------------------------------------

## Categories of Justification

A Canonical Market Representation may be justified through one or more
of the following categories.

### Ontological Justification

The representation is required because the market cannot be described
consistently without it.

Examples:

``` text
Market State
Event
Outcome
Decision
```

------------------------------------------------------------------------

### Scientific Justification

The representation is required to answer research questions or to
express scientific knowledge that cannot be represented adequately by
existing canonical representations.

------------------------------------------------------------------------

### Representation Justification

The representation is required because existing canonical
representations cannot preserve the required semantic, temporal or
causal boundaries.

Creating additional columns inside another representation is
insufficient.

A separate representation is required.

------------------------------------------------------------------------

### Governance Justification

The representation is required to preserve institutional governance,
traceability or semantic stability across the architecture.

------------------------------------------------------------------------

### Operational Justification

The representation is required to enable institutional operation without
altering canonical semantics.

Operational convenience alone is never sufficient.

------------------------------------------------------------------------

## Multiple Justifications

A representation may have more than one justification.

Example:

``` text
Event State

representation_justification:

- ontological
- scientific
- governance
```

The institutional record shall explicitly declare every accepted
justification.

------------------------------------------------------------------------

## What Is Not a Valid Justification

The following reasons are not sufficient on their own:

``` text
The table became too large.

The query is slow.

The implementation is easier.

The ML model expects another layout.

Another project uses a similar structure.

The engineering team prefers it.
```

These may motivate a different implementation.

They do not justify creating a new Canonical Market Representation.

------------------------------------------------------------------------

## Relationship with Enabling Institutional Artifacts

Not every institutional artifact is a Canonical Market Representation.

Artifacts such as:

``` text
instrument_master
market_calendar
expected_data_calendar
dataset_certification_matrix
```

exist primarily to support identity, governance, certification or
operation.

They remain institutional assets, but they should not be artificially
classified as market representations.

This distinction preserves the separation between market knowledge and
infrastructure.

------------------------------------------------------------------------

## Institutional Record

Every Canonical Market Representation should have an institutional
justification record describing:

-   representation name;
-   architectural purpose;
-   justification categories;
-   relationship to existing representations;
-   semantic boundaries;
-   approving authority.

This record becomes part of the architectural traceability of TSIS.

------------------------------------------------------------------------

## Fundamental Rule

A Canonical Market Representation exists because the architecture
requires it.

It never exists because the implementation happens to benefit from it.

Implementation follows justification.

Justification never follows implementation.
