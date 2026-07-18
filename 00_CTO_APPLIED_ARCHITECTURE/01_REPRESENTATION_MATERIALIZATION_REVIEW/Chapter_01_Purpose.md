# Chapter 1 --- Purpose

## Objective

The purpose of this document is to govern the institutional process
through which a **Canonical Market Representation** becomes an official
implementation within TSIS.

This document exists because defining a representation and implementing
a representation are fundamentally different activities.

A representation belongs to scientific architecture.

An implementation belongs to system architecture.

Between both exists an institutional decision process that must be
explicit, reproducible and governed.

This document defines that process.

------------------------------------------------------------------------

## Position within TSIS

TSIS is organized as a layered scientific architecture.

Each layer answers a different question.

The **Epistemological Architecture** defines what knowledge may
legitimately exist within the system.

Within that architecture, the **Market Representation Architecture**
defines how market knowledge should be represented through canonical
market representations.

Once a canonical representation has been established, a different
problem appears:

``` text
How should this representation be implemented within TSIS?
```

That question is the responsibility of this document.

It begins where the Market Representation Architecture ends.

------------------------------------------------------------------------

## Why this document exists

A canonical representation is not an implementation.

For example,

``` text
Market State
```

is not a table.

Likewise,

``` text
Event State
```

is not a dataset.

Both are canonical representations defined by the Market Representation
Architecture.

Whether they should become datasets, feature stores, event stores,
registries or any other physical implementation is a separate
architectural decision.

Without an explicit governance process, different implementations could
diverge from the canonical representation they intend to realize.

This document exists to prevent that divergence.

------------------------------------------------------------------------

## Scope

This document governs the transition from a **Canonical Market
Representation** to its institutional implementation.

Its responsibilities include:

-   determining when a canonical representation deserves implementation;
-   defining the governance required before implementation;
-   establishing the institutional process leading to implementation;
-   governing promotion from candidate implementations to institutional
    assets;
-   preserving traceability between canonical representations and their
    implementations.

This document does **not** define:

-   scientific discovery;
-   research methodology;
-   market ontology;
-   representation theory;
-   feature engineering;
-   implementation-specific builders or validators.

Those responsibilities belong to other architectural documents.

------------------------------------------------------------------------

## Fundamental Principle

TSIS never implements concepts directly.

It implements **Canonical Market Representations**.

Every institutional implementation must be traceable to exactly one
canonical representation defined by the Market Representation
Architecture.

Scientific architecture defines the meaning of a representation.

Institutional implementation makes that representation operational.

Neither may redefine the other.

------------------------------------------------------------------------

## Constitutional Statement

The Market Representation Architecture is the sole authority responsible
for defining Canonical Market Representations.

This document never creates, modifies or interprets canonical
representations.

Its sole responsibility is to govern the institutional process by which
those representations become official implementations within TSIS.
