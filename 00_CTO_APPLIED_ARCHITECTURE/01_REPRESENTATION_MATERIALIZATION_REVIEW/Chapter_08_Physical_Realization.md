# Chapter 8 --- Physical Realization

## Objective

Once a Physical Representation has been approved and governed by
institutional contracts, TSIS may proceed with its physical realization.

The purpose of this chapter is to define the architectural
responsibilities associated with transforming a governed Physical
Representation into a concrete institutional implementation.

This chapter does not replace the engineering procedures defined by the
**Table Creation Process**.

Instead, it establishes the architectural boundary between governance
and implementation.

------------------------------------------------------------------------

## From Governance to Engineering

The previous chapters answer:

``` text
What should be implemented?
```

This chapter marks the transition to:

``` text
How is it implemented?
```

At this point the Canonical Market Representation already exists.

The Physical Representation has already been approved.

Its governing contracts already exist.

Engineering now becomes responsible for producing a faithful
implementation.

------------------------------------------------------------------------

## Responsibilities of Physical Realization

Physical realization is responsible for creating governed implementation
artifacts such as:

-   schemas;
-   builders;
-   validators;
-   manifests;
-   summaries;
-   lineage information;
-   reproducible outputs;
-   implementation metadata.

These artifacts operationalize the representation.

They do not redefine it.

------------------------------------------------------------------------

## Engineering as an Execution Layer

Engineering operates under institutional authority.

It receives:

``` text
Canonical Market Representation
        ↓
Materialization Decision
        ↓
Physical Representation
        ↓
Institutional Contracts
```

and produces:

``` text
Implementation Artifacts
```

The direction of authority is never reversed.

------------------------------------------------------------------------

## Required Implementation Artifacts

A complete implementation should include, where applicable:

``` text
Schema

Dataset Contract

Builder

Validator

Manifest

Summary

Build Metadata

Lineage

Registry Entry

Consumption Policy

Promotion Status
```

Different implementations may require additional artifacts.

None may omit the institutional governance defined by previous chapters.

------------------------------------------------------------------------

## Reproducibility

Every realization shall be reproducible.

Institutional implementations should be reconstructable from:

-   source inputs;
-   implementation contracts;
-   builders;
-   configuration;
-   manifests;
-   validator results;
-   version identifiers.

A Physical Representation cannot become an institutional asset unless
its realization is reproducible.

------------------------------------------------------------------------

## Relationship with the Table Creation Process

Within the current TSIS architecture, the engineering procedures
governing implementation already exist.

They include, among others:

-   builder workflows;
-   schema generation;
-   validation;
-   manifests;
-   candidate generation;
-   promotion workflows.

Those procedures are defined by the **Table Creation Process** and its
associated engineering documentation.

This document governs why and when realization occurs.

The Table Creation Process governs how realization is executed.

The two documents are complementary rather than overlapping.

------------------------------------------------------------------------

## Architectural Boundary

This document shall never define:

-   implementation algorithms;
-   software architecture;
-   programming techniques;
-   storage optimization;
-   database tuning.

Those belong to engineering.

Likewise, engineering documentation shall never redefine:

-   canonical semantics;
-   institutional justification;
-   materialization decisions;
-   representation governance.

Those belong to architecture.

------------------------------------------------------------------------

## Fundamental Rule

Physical realization is the execution of an approved architectural
decision.

Engineering creates institutional implementations.

Architecture defines what those implementations are required to
preserve.
