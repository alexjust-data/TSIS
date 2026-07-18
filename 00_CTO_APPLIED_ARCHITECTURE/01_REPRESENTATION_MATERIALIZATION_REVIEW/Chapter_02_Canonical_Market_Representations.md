# Chapter 2 --- Canonical Market Representations

## Definition

A **Canonical Market Representation** is the authoritative conceptual
specification used by TSIS to describe a valid aspect of the market, its
context or its evolution.

It defines what a represented entity means independently of:

-   any table;
-   any schema;
-   any storage format;
-   any builder;
-   any programming language;
-   any research model;
-   any downstream consumer.

A Canonical Market Representation therefore exists before its physical
implementation.

Examples include:

``` text
Market Primitive
Feature
Market Representation
Market State
Event
Event State
Decision
Outcome
```

These concepts are not interchangeable.

Each represents a different type of market knowledge and is governed by
different semantic, temporal and causal constraints.

------------------------------------------------------------------------

## Architectural Authority

Canonical Market Representations are defined and governed by:

``` text
TSIS_Data/
└── 00_CTO_1/
    └── 000_EPISTEMOLOGICAL_architecture/
```

More specifically, their primary authority is the **Market
Representation Architecture** contained within the TSIS Epistemological
Architecture.

The wider Epistemological Architecture governs:

-   how scientific questions are formed;
-   how hypotheses are created;
-   how evidence is collected;
-   how phenomena are established;
-   how knowledge is validated;
-   how research evolves;
-   how scientific discovery is governed.

Within that architecture, the Market Representation Architecture
defines:

-   which market entities may be represented;
-   how representation layers are separated;
-   which temporal constraints apply;
-   what information is observable;
-   how causality is protected;
-   how representations are governed.

The relationship is therefore:

``` text
EPISTEMOLOGICAL ARCHITECTURE
            │
            ├── governs scientific knowledge and discovery
            │
            ▼
MARKET REPRESENTATION ARCHITECTURE
            │
            ├── defines valid market representation semantics
            │
            ▼
CANONICAL MARKET REPRESENTATIONS
```

A Canonical Market Representation is not the whole Epistemological
Architecture.

It is a governed representational entity defined within that
architecture.

------------------------------------------------------------------------

## Why the Representation Is Canonical

The term **canonical** means that the representation acts as the
institutional semantic authority for all implementations that claim to
represent the same entity.

The canonical representation determines:

``` text
what the entity is;
what it is not;
which information may belong to it;
which information must remain outside it;
its temporal meaning;
its observational limits;
its causal limits;
its relationship with other representations.
```

The implementation determines how that meaning is physically realized.

------------------------------------------------------------------------

## Representation Before Implementation

A Canonical Market Representation is implementation-independent.

For example:

``` text
Market State
```

may be defined as a legally observable snapshot of an instrument and its
relevant market context at a declared decision timestamp.

That definition exists independently of whether Market State is
implemented as:

``` text
a Parquet dataset;
a relational table;
a feature-store record;
an in-memory object;
a state service;
a research snapshot.
```

The governing direction is:

``` text
Canonical meaning
        ↓
Implementation contract
        ↓
Physical implementation
```

Never:

``` text
Existing columns
        ↓
Retrospective interpretation
        ↓
Canonical meaning
```

------------------------------------------------------------------------

## Semantic Boundaries

Every Canonical Market Representation must define explicit boundaries
answering:

-   What belongs to the representation?
-   What does not belong to the representation?
-   At what time does the representation exist?
-   In relation to what entity does it exist?

Without these boundaries, no implementation can remain scientifically
consistent.

------------------------------------------------------------------------

## Canonical Representation and Physical Artifacts

A Canonical Market Representation and a physical artifact are not
equivalent.

One canonical representation may have:

-   one implementation;
-   many implementations;
-   or no implementation at all.

Likewise, not every institutional artifact is itself a Canonical Market
Representation.

Infrastructure artifacts such as:

``` text
instrument_master
market_calendar
expected_data_calendar
dataset_certification_matrix
registries
manifests
```

exist for ontological, governance or operational reasons rather than to
represent market knowledge directly.

------------------------------------------------------------------------

## Source of Meaning

Semantic authority always flows in the following direction:

``` text
Market Representation Architecture
        ↓
Canonical Market Representation
        ↓
Representation Contracts
        ↓
Schemas
        ↓
Builders
        ↓
Validators
        ↓
Institutional Implementation
```

Engineering never defines semantics.

It implements semantics already defined by the Market Representation
Architecture.

------------------------------------------------------------------------

## Fundamental Rule

A Canonical Market Representation is the semantic contract between the
scientific architecture of TSIS and every physical implementation that
claims to represent the same market entity.

Technologies, schemas and builders may evolve.

Canonical meaning must remain stable.
