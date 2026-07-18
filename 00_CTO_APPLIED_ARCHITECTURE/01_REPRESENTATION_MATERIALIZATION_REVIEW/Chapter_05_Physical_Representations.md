# Chapter 5 --- Physical Representations

## Objective

Once a Canonical Market Representation has been approved for
materialization, TSIS must determine how that representation will exist
as an institutional asset.

The purpose of this chapter is to define the concept of a **Physical
Representation** and to establish its relationship with Canonical Market
Representations.

This chapter does not define implementation technology.

It defines architectural meaning.

------------------------------------------------------------------------

## Definition

A **Physical Representation** is the governed institutional
implementation of a Canonical Market Representation.

Its purpose is to make a canonical representation:

-   persistent;
-   reproducible;
-   versionable;
-   governable;
-   consumable;
-   traceable.

A Physical Representation never defines meaning.

It implements meaning that already exists.

------------------------------------------------------------------------

## Canonical Representation vs Physical Representation

A Canonical Market Representation answers:

``` text
What does this market entity mean?
```

A Physical Representation answers:

``` text
How is that meaning made operational inside TSIS?
```

The relationship is therefore:

``` text
Canonical Market Representation
            ↓
Materialization Decision
            ↓
Physical Representation
```

Meaning always flows from the canonical representation toward the
physical implementation.

Never in the opposite direction.

------------------------------------------------------------------------

## Independence from Technology

A Physical Representation is an architectural concept.

It is independent of storage technology.

Examples include:

``` text
Dataset
Table
Feature Store
Event Store
Knowledge Graph
Registry
State Service
Vector Store
```

Future technologies may replace current implementations without changing
the canonical representation they realize.

------------------------------------------------------------------------

## One-to-One and One-to-Many Relationships

A Canonical Market Representation may have:

``` text
one canonical implementation;
multiple governed implementations;
no implementation.
```

For example:

``` text
Market State
        ├── Research Dataset
        ├── Online State Service
        └── Feature Store Projection
```

Each implementation serves different institutional consumers while
preserving the same semantic authority.

------------------------------------------------------------------------

## Identity of a Physical Representation

Every Physical Representation should declare at minimum:

-   implemented canonical representation;
-   implementation identifier;
-   implementation type;
-   governing contracts;
-   implementation status;
-   version;
-   responsible builders;
-   validators;
-   consumer scope.

This identity allows implementations to evolve while remaining traceable
to their canonical origin.

------------------------------------------------------------------------

## Physical Representation Is Not a Table

Within the current TSIS implementation many Physical Representations
will be materialized as datasets and tables.

This reflects today's engineering choices.

It is not an architectural requirement.

A table is one possible implementation.

It is not the definition of a Physical Representation.

------------------------------------------------------------------------

## Relationship with Engineering

Engineering becomes responsible only after the Physical Representation
has been approved.

Engineering then defines:

-   schemas;
-   builders;
-   validators;
-   manifests;
-   registries;
-   storage layouts;
-   deployment.

These activities belong to implementation.

They must preserve---not redefine---the canonical semantics.

------------------------------------------------------------------------

## Fundamental Rule

Every Physical Representation shall implement exactly one Canonical
Market Representation.

A Physical Representation may evolve technologically.

Its canonical meaning shall remain invariant throughout its lifecycle.
