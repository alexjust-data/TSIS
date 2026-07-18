# TSIS Event Research Architecture

## Chapter 6 --- Event Geometry

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 6. Purpose

Events are anchored in time.

Event Geometry describes their observable structure.

Its objective is to characterize **how an Event occupies time, state
space and market context**, independently of any trading strategy.

Geometry transforms isolated events into measurable research objects.

------------------------------------------------------------------------

# 6.1 Fundamental Principle

Two Events may share the same Event Family but possess completely
different geometries.

Example:

``` text
VWAP Reclaim Candidate
```

may occur after:

-   gradual accumulation,
-   violent momentum,
-   post-halt reopening.

The Event identity remains identical.

The geometry changes.

------------------------------------------------------------------------

# 6.2 Definition

Event Geometry is the structured description of the observable
conditions surrounding an Event across one or more Event Windows.

It is built exclusively from:

-   Event Windows,
-   Event States,
-   canonical Representations.

It never contains:

-   decisions,
-   rewards,
-   future labels.

------------------------------------------------------------------------

# 6.3 Geometry Dimensions

Every Event Geometry may include:

``` text
Temporal Geometry
Price Geometry
Volume Geometry
Microstructure Geometry
Context Geometry
Execution Geometry
```

Each dimension remains independently observable.

------------------------------------------------------------------------

# 6.4 Temporal Geometry

Examples:

``` text
Time since open
Time to close
Pre-event duration
Response duration
Event persistence
```

------------------------------------------------------------------------

# 6.5 Price Geometry

Examples:

``` text
Distance to HOD
Distance to VWAP
Position inside range
Compression
Expansion
Break structure
```

------------------------------------------------------------------------

# 6.6 Volume Geometry

Examples:

``` text
Relative Volume
Trade Count
Dollar Volume
Volume Acceleration
Participation Rate
```

------------------------------------------------------------------------

# 6.7 Microstructure Geometry

Examples:

``` text
Spread
Top Depth
Microprice
Signed Flow
OFI
Quote Update Rate
Burstiness
```

This dimension becomes richer as higher-resolution data become
available.

------------------------------------------------------------------------

# 6.8 Context Geometry

Examples:

``` text
News Context
Regime
Short Context
Corporate Actions
Scanner Context
```

Context explains where the Event occurs.

------------------------------------------------------------------------

# 6.9 Geometry Metadata

Every Event Geometry shall declare:

``` text
geometry_id
event_family
window_policy
representation_versions
feature_registry_version
state_version
builder_version
```

------------------------------------------------------------------------

# 6.10 Geometry versus Phenomenon

Geometry describes.

Phenomena explain.

``` text
Geometry
    ↓
Evidence
    ↓
Phenomenon
```

Geometry belongs to Event Research.

Phenomena belong to Scientific Discovery.

------------------------------------------------------------------------

# 6.11 Constitutional Rule

Event Geometry is the canonical observable description of an Event.

It shall remain representation-based, temporally legal and
strategy-independent.

Its responsibility is to organize evidence, never to prescribe actions.
