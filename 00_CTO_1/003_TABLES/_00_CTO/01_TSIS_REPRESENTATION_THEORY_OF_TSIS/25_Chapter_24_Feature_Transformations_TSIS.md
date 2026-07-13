# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 24 --- Feature Transformations

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 24. Feature Transformations

## 24.1 Purpose

Operators define *what* mathematical action is performed.

Transformations define *how* a feature evolves from a primitive through
one or more successive mathematical stages.

This chapter establishes the canonical transformation pipeline used by
TSIS.

------------------------------------------------------------------------

# 24.2 Fundamental Principle

Every canonical feature is the result of one or more ordered
transformations.

``` text
Primitive
    ↓
Transformation 1
    ↓
Transformation 2
    ↓
Transformation N
    ↓
Canonical Feature
```

Transformations are explicit, versioned and reproducible.

------------------------------------------------------------------------

# 24.3 Transformation versus Operator

An operator is one mathematical action.

Examples:

``` text
Mean
Rate
Difference
Entropy
```

A transformation is an ordered sequence of operators.

Example:

``` text
Trades
    ↓ Count
Trade Count
    ↓ Rate
Trade Count Rate
    ↓ Acceleration
Trade Count Acceleration
    ↓ Z-Score
Normalized Trade Count Acceleration
```

------------------------------------------------------------------------

# 24.4 Canonical transformation stages

A feature may pass through the following stages:

``` text
Selection
Aggregation
Temporal
Normalization
Comparison
Interaction
```

Not every feature requires every stage.

------------------------------------------------------------------------

## 24.5 Selection transformations

Purpose:

Choose the legal input population.

Examples:

``` text
Regular Session Only
Eligible Trades Only
Top-of-Book Quotes
Odd Lots Included
Odd Lots Excluded
```

Selection policies shall always be documented.

------------------------------------------------------------------------

## 24.6 Aggregation transformations

Purpose:

Compress multiple primitives into one measurable quantity.

Examples:

``` text
Count
Sum
Mean
Median
Percentile
```

Aggregation changes cardinality but not semantic ownership.

------------------------------------------------------------------------

## 24.7 Temporal transformations

Purpose:

Measure evolution through time.

Examples:

``` text
Rate
Velocity
Acceleration
Jerk
Time Since
Rolling Difference
```

Temporal transformations require an explicit observation window.

------------------------------------------------------------------------

## 24.8 Normalization transformations

Purpose:

Make comparable observations originating from different scales.

Examples:

``` text
Per Second
Per Trade
Per Share
Per Dollar
Log1p
Z-Score
Historical Percentile
```

Normalization changes representation, not meaning.

------------------------------------------------------------------------

## 24.9 Comparative transformations

Purpose:

Measure deviation from a reference.

Examples:

``` text
Distance to VWAP
Distance to HOD
Distance to Historical Mean
Ratio to Baseline
Spread Compression
```

Every reference must be explicitly defined.

------------------------------------------------------------------------

## 24.10 Interaction transformations

Purpose:

Generate new observable properties by combining independent features.

Examples:

``` text
Spread × Signed Flow
OFI / Top Depth
Gap × RVOL
Trade Rate × Spread
```

Interactions shall possess documented economic interpretation.

------------------------------------------------------------------------

## 24.11 Multi-stage transformations

Complex features may contain multiple sequential transformations.

Example:

``` text
Trades
    ↓
Trade Count
    ↓
Trade Count Rate
    ↓
Acceleration
    ↓
Historical Percentile
```

Each intermediate stage should remain reproducible.

------------------------------------------------------------------------

## 24.12 Transformation metadata

Every transformation shall declare:

``` text
transformation_name
operator_sequence
input_types
output_type
window
normalization
timestamp_semantics
version
```

------------------------------------------------------------------------

## 24.13 Forbidden transformations

The following are prohibited inside canonical representations:

``` text
Future-conditioned transforms
Outcome-conditioned transforms
Reward-conditioned transforms
Model-specific transforms
Hidden preprocessing
```

------------------------------------------------------------------------

## 24.14 Constitutional rule

Every canonical feature inside TSIS shall expose its complete
transformation chain.

No feature may exist whose mathematical derivation cannot be
reconstructed from documented transformations.
