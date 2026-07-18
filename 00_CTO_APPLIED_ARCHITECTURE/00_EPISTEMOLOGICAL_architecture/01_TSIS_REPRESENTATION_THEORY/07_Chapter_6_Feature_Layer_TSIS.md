# TSIS Market Representation Architecture

## Chapter 6 --- Feature Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 6. Feature Layer

## 6.1 Purpose

The Feature Layer transforms canonical primitives into quantitative
descriptions of observable market properties.

Features do not predict.

Features do not decide.

Features do not evaluate.

Their sole purpose is to measure.

------------------------------------------------------------------------

## 6.2 Definition

A feature is a deterministic mathematical function computed from one or
more primitives using only information available at or before the
feature timestamp.

A feature represents **one measurable property** of the observable
market.

------------------------------------------------------------------------

## 6.3 Core principles

Every feature shall be:

-   mathematically defined;
-   deterministic;
-   temporally legal;
-   reproducible;
-   versioned;
-   economically interpretable;
-   independently testable.

------------------------------------------------------------------------

## 6.4 What a feature is not

A feature is never:

``` text
A trading signal
A prediction
A label
A reward
A decision
An outcome
A strategy
```

These belong to downstream layers.

------------------------------------------------------------------------

## 6.5 Feature families

Features belong to semantic families.

Examples:

``` text
Microstructure
Intraday
Daily
Fundamental
News
Short Context
Regime
Execution
Quality
```

A feature belongs to one primary family.

------------------------------------------------------------------------

## 6.6 Feature composition

A feature may consume:

``` text
Primitive
Primitive + Primitive
Primitive + Feature
Feature + Feature
```

It may never consume:

``` text
Outcome
Decision
Future information
```

------------------------------------------------------------------------

## 6.7 Feature dimensions

Every feature possesses explicit dimensions.

Minimum dimensions:

``` text
Semantic Family
Observation Horizon
Lookback Window
Units
Normalization
Timestamp Semantics
Materialization Policy
Version
```

Example:

``` text
Feature:
microstructure.trade_count_rate

Family:
Microstructure

Window:
5 seconds

Units:
trades/second

Normalization:
None

Timestamp:
Decision timestamp

Version:
1.0
```

------------------------------------------------------------------------

## 6.8 Feature categories

### Atomic features

Computed directly from primitives.

Examples:

``` text
Spread
Trade Count
Trade Size
VWAP Distance
Gap %
```

### Derived features

Computed from existing features.

Examples:

``` text
Spread Compression
Tape Acceleration
OFI Z-score
Spread Percentile
```

### Composite features

Structured combinations of multiple feature families.

Example:

``` text
Liquidity Pressure Representation
```

Composite features should remain interpretable.

------------------------------------------------------------------------

## 6.9 Feature legality

A legal feature satisfies:

``` text
Observable before t

Deterministic

Versioned

Documented

Reproducible
```

Illegal features include:

``` text
Future return

Future spread

Future label

Realized reward

Outcome-dependent values
```

------------------------------------------------------------------------

## 6.10 Feature identity

Every feature requires:

``` text
Canonical Name
Description
Formula
Inputs
Units
Feature Family
Version
```

The canonical name is immutable.

Implementations may change.

Semantics may not.

------------------------------------------------------------------------

## 6.11 Feature registry

Every feature must appear in the Feature Registry.

Minimum registry fields:

``` text
feature_name
feature_family
formula
input_primitives
dependencies
window
units
normalization
builder
version
materialization_policy
quality_requirements
```

No undocumented feature may enter a State.

------------------------------------------------------------------------

## 6.12 Feature lifecycle

``` text
Primitive
    ↓
Feature Definition
    ↓
Validation
    ↓
Registration
    ↓
Materialization
    ↓
Consumption
```

Every transition must preserve reproducibility.

------------------------------------------------------------------------

## 6.13 Constitutional rule

Features are the unique mathematical language used by TSIS to describe
market properties.

Strategies consume features.

States organize features.

Outcomes evaluate decisions.

A feature shall never cross those semantic boundaries.
