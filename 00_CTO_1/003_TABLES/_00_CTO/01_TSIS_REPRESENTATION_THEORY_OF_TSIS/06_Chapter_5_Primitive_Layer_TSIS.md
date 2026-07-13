# TSIS Market Representation Architecture

## Chapter 5 --- Primitive Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 5. Primitive Layer

## 5.1 Purpose

The Primitive Layer is the first canonical representation of market
observations.

Its mission is **not** to engineer knowledge.

Its mission is to transform heterogeneous vendor observations into
stable, reproducible and vendor-independent objects.

Primitives are therefore the canonical building blocks from which every
feature inside TSIS is derived.

------------------------------------------------------------------------

## 5.2 Definition

A primitive is a deterministic canonical object created from one or more
observations without introducing statistical inference.

A primitive preserves:

-   semantic meaning,
-   temporal ordering,
-   economic identity,
-   lineage,
-   reproducibility.

A primitive never represents a prediction.

------------------------------------------------------------------------

## 5.3 Primitive design principles

Every primitive shall satisfy:

1.  Canonical identity.
2.  Deterministic construction.
3.  Explicit lineage.
4.  Point-in-time legality.
5.  Vendor independence.
6.  Immutable semantics.
7.  Versioned specification.

------------------------------------------------------------------------

## 5.4 Primitive families

### Trade primitives

Examples:

``` text
Canonical Trade
Trade Timestamp
Trade Price
Trade Size
Trade Exchange
Trade Conditions
```

------------------------------------------------------------------------

### Quote primitives

Examples:

``` text
Canonical Quote
Bid
Ask
Bid Size
Ask Size
Sequence Number
Participant Timestamp
Feed Timestamp
```

------------------------------------------------------------------------

### Bar primitives

Examples:

``` text
Canonical 1m Bar
Canonical Daily Bar
OHLC
Volume
VWAP
Transaction Count
```

------------------------------------------------------------------------

### Context primitives

Examples:

``` text
Corporate Action
News Publication
SEC Filing
Trading Halt
Short Interest Observation
```

------------------------------------------------------------------------

# 5.5 Primitive responsibilities

Primitives are responsible for:

-   canonical timestamps,
-   canonical identifiers,
-   normalization,
-   quality metadata,
-   temporal validity,
-   provenance.

Primitives are **not** responsible for:

-   aggregation,
-   prediction,
-   feature engineering,
-   statistical inference,
-   strategy logic.

------------------------------------------------------------------------

# 5.6 Primitive invariants

Every primitive must preserve:

``` text
Economic identity

Temporal identity

Measurement identity

Source identity
```

Transformations that modify any of these dimensions must create a new
primitive version.

------------------------------------------------------------------------

# 5.7 Primitive lineage

Every primitive must expose lineage.

Minimum lineage metadata:

``` text
source_dataset

source_vendor

source_timestamp

schema_version

builder_version

quality_state
```

No primitive may exist without traceability.

------------------------------------------------------------------------

# 5.8 Primitive legality

Primitives may only use information observable at the observation
timestamp.

Future information is forbidden.

Primitive construction must never depend upon:

-   future prices,
-   future labels,
-   future outcomes,
-   future rewards.

------------------------------------------------------------------------

# 5.9 Primitive versus Feature

Primitive:

``` text
Trade Price
Trade Size
Bid
Ask
VWAP
```

Feature:

``` text
Trade Count Rate

Spread

Microprice

OFI

ATR
```

Features measure properties.

Primitives preserve observations.

------------------------------------------------------------------------

# 5.10 Primitive lifecycle

``` text
Observation
    ↓
Primitive Creation
    ↓
Validation
    ↓
Certification
    ↓
Consumption
    ↓
Archival
```

Each transition must be reproducible.

------------------------------------------------------------------------

# 5.11 Constitutional rule

No feature may consume raw vendor observations directly.

Every engineered quantity inside TSIS must be derived from canonical
primitives.

Primitives constitute the unique interface between observations and
mathematical representation.
