# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 27 --- Composite Features

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 27. Composite Features

## 27.1 Purpose

Individual features describe isolated observable properties.

Composite features describe higher-level market phenomena by combining
multiple canonical features under a governed mathematical specification.

Composite features are intended to represent market behaviour, not
isolated measurements.

------------------------------------------------------------------------

## 27.2 Fundamental Principle

A composite feature is **not** an arbitrary collection of variables.

It is a deterministic mathematical composition of canonical features
whose combination represents an observable market concept.

``` text
Primitive
    ↓
Feature
    ↓
Composite Feature
```

------------------------------------------------------------------------

## 27.3 Definition

A composite feature is a feature constructed exclusively from canonical
features while preserving:

-   temporal legality,
-   semantic traceability,
-   deterministic computation,
-   reproducibility.

Composite features never consume:

``` text
Decision
Outcome
Reward
Future information
```

------------------------------------------------------------------------

## 27.4 Motivation

Many market concepts cannot be represented by a single observable.

Examples:

``` text
Liquidity Pressure

Market Participation

Breakout Readiness

Auction Imbalance

Execution Difficulty
```

These require multiple measurable properties.

------------------------------------------------------------------------

## 27.5 Canonical examples

### Liquidity Pressure

Possible inputs:

``` text
Spread
Top Depth
Trade Count Rate
Signed Flow
OFI
```

The composite feature represents liquidity conditions rather than any
individual measurement.

------------------------------------------------------------------------

### Breakout Readiness

Possible inputs:

``` text
Distance to HOD
Spread Compression
Trade Acceleration
Relative Volume
Microprice
```

This remains a representation.

It is **not** a buy signal.

------------------------------------------------------------------------

### Execution Difficulty

Possible inputs:

``` text
Spread
Visible Depth
Quote Stability
Expected Slippage
```

The feature describes execution conditions only.

------------------------------------------------------------------------

## 27.6 Composition rules

Every composite feature shall declare:

``` text
Input Features
Combination Rule
Normalization
Window Policy
Timestamp Semantics
Version
```

No hidden combinations are permitted.

------------------------------------------------------------------------

## 27.7 Traceability

Every composite feature must expose a complete dependency graph.

Example:

``` text
Trade Primitive
      ↓
Trade Count
      ↓
Trade Count Rate
      ↓
Trade Acceleration
            \
             \
Spread --------> Breakout Readiness
```

Every upstream dependency shall remain reproducible.

------------------------------------------------------------------------

## 27.8 Semantic ownership

A composite feature belongs to one primary feature family even when
consuming multiple families.

Example:

``` text
Liquidity Pressure
```

may consume:

``` text
Microstructure
Intraday
Execution
```

yet still belong to the **Microstructure** family.

------------------------------------------------------------------------

## 27.9 Complexity

Composite features should increase explanatory power without sacrificing
interpretability.

Increasing mathematical complexity alone does not justify architectural
promotion.

------------------------------------------------------------------------

## 27.10 Constitutional rule

Composite features remain observable representations.

They shall never encode trading decisions, policy outputs or future
evaluation.

A composite feature describes the market.

It never prescribes an action.
