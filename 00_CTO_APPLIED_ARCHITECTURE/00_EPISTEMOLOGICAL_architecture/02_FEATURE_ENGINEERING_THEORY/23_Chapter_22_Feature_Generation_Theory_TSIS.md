# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 22 --- Feature Generation Theory

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 22. Feature Generation Theory

## 22.1 Purpose

This chapter defines the scientific theory governing how features are
created inside TSIS.

A feature is not an arbitrary variable.

A feature is the result of a deterministic and legally observable
transformation applied to canonical primitives.

The purpose of this chapter is to establish a universal grammar for
feature generation so that every future feature, regardless of domain,
follows the same mathematical and architectural principles.

------------------------------------------------------------------------

## 22.2 Fundamental Principle

Features are **discovered mathematically**, not invented heuristically.

Every feature shall answer one question:

> **Which observable property of the market does this mathematical
> transformation represent?**

If no observable property can be identified, the object is not a
canonical TSIS feature.

------------------------------------------------------------------------

## 22.3 Feature Generation Pipeline

Every feature follows the same pipeline.

``` text
Reality
    ↓
Observation
    ↓
Primitive
    ↓
Transformation
    ↓
Feature
    ↓
Representation
    ↓
State
```

Feature generation begins after canonical primitives exist.

------------------------------------------------------------------------

## 22.4 Primitive → Feature

A primitive contains observations.

Examples:

``` text
Trade
Quote
One-Minute Bar
Daily Bar
News Event
Trading Halt
```

A feature measures one property of those primitives.

Example:

``` text
Trades
        ↓
Trade Count
        ↓
Trade Count Rate
        ↓
Trade Count Acceleration
```

Each transformation increases semantic abstraction while preserving
temporal legality.

------------------------------------------------------------------------

## 22.5 Canonical Feature Equation

Conceptually every feature can be represented as:

``` text
Feature =
Transformation(
    Primitive(s),
    Window,
    Policy,
    Timestamp
)
```

where:

-   Primitive(s) define the input.
-   Window defines the observation horizon.
-   Policy defines legal computation.
-   Timestamp defines observability.

------------------------------------------------------------------------

## 22.6 Feature Components

Every canonical feature contains four inseparable components:

### Observable domain

Example:

``` text
Trades
Quotes
Bars
News
Fundamentals
```

### Mathematical transformation

Examples:

``` text
Sum
Mean
Median
Rate
Difference
Entropy
Percentile
Regression
```

### Temporal definition

Examples:

``` text
1 second
5 seconds
30 seconds
Current Session
Previous 20 Days
```

### Semantic interpretation

Example:

``` text
Trade Count Rate

↓

Observed transaction intensity
```

The semantic interpretation is mandatory.

------------------------------------------------------------------------

## 22.7 Feature Grammar

TSIS generates features through a controlled grammar.

Conceptually:

``` text
Primitive

↓

Operator

↓

Window

↓

Normalization

↓

Canonical Feature
```

Example:

``` text
Trades

↓

Count

↓

5 Seconds

↓

Per Second

↓

Trade Count Rate
```

------------------------------------------------------------------------

## 22.8 Feature Families emerge naturally

Families are not manually invented.

They emerge from the observable domain.

Example:

``` text
Trades

↓

Trade Features

Quotes

↓

Quote Features

Bars

↓

Intraday Features

Daily

↓

Daily Features
```

------------------------------------------------------------------------

## 22.9 Feature Depth

Not every feature possesses the same semantic depth.

Example:

``` text
Trade Count
```

↓

``` text
Trade Count Rate
```

↓

``` text
Trade Count Acceleration
```

↓

``` text
Trade Count Acceleration Z-Score
```

↓

``` text
Acceleration Relative to Historical Baseline
```

Each additional transformation increases semantic depth.

------------------------------------------------------------------------

## 22.10 Feature Legality

Every generated feature must satisfy:

-   deterministic computation,
-   explicit mathematical definition,
-   observable inputs only,
-   documented temporal semantics,
-   documented dependencies.

Failure of any requirement invalidates the feature.

------------------------------------------------------------------------

## 22.11 Canonical Principle

TSIS never creates features by asking:

> "Will this improve prediction?"

Instead it asks:

> "Does this mathematically describe an observable property of the
> market?"

Prediction is evaluated afterwards.

Representation always comes first.

------------------------------------------------------------------------

## 22.12 Constitutional Rule

Every canonical feature inside TSIS shall be derivable through the
Feature Generation Theory defined in this chapter.

Any engineered variable that cannot be expressed through this grammar
shall remain experimental until formally integrated into the
representation architecture.
