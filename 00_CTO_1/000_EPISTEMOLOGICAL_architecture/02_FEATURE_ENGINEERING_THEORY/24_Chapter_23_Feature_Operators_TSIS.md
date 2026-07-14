# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 23 --- Feature Operators

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 23. Feature Operators

## 23.1 Purpose

Feature operators are the canonical mathematical transformations allowed
inside TSIS.

A feature is never created directly from a primitive.

It is created by applying one or more governed operators to canonical
primitives.

The objective of this chapter is to define a finite, auditable and
reproducible vocabulary of transformations.

------------------------------------------------------------------------

# 23.2 Fundamental Principle

Every feature can be decomposed into:

``` text
Primitive(s)
      +
Operator(s)
      +
Window
      +
Policy
      ↓
Canonical Feature
```

Therefore the operator is the atomic unit of feature engineering.

------------------------------------------------------------------------

# 23.3 Why operators exist

Without operators, feature engineering becomes an unlimited collection
of ad‑hoc calculations.

TSIS replaces ad‑hoc engineering with a governed mathematical grammar.

Operators are therefore reusable mathematical objects.

------------------------------------------------------------------------

# 23.4 Canonical operator families

## Aggregation

Transform multiple observations into a summary.

Examples:

``` text
count
sum
mean
median
minimum
maximum
variance
standard deviation
quantiles
```

------------------------------------------------------------------------

## Temporal

Describe change over time.

Examples:

``` text
difference
return
rate
velocity
slope
acceleration
jerk
duration
time_since
```

------------------------------------------------------------------------

## Distributional

Describe statistical structure.

Examples:

``` text
entropy
skewness
kurtosis
coefficient of variation
Herfindahl index
Gini coefficient
```

------------------------------------------------------------------------

## Relative

Express one quantity relative to another.

Examples:

``` text
ratio
percentage
basis points
percentile
z-score
rolling rank
distance_to_reference
```

------------------------------------------------------------------------

## Structural

Describe geometry.

Examples:

``` text
path efficiency
drawdown
run length
compression
expansion
overlap
position inside range
```

------------------------------------------------------------------------

## Interaction

Combine independent observables.

Examples:

``` text
spread × signed_flow

OFI / top_depth

trade_rate × spread

gap × RVOL
```

Interaction operators generate new observable properties rather than
arbitrary combinations.

------------------------------------------------------------------------

# 23.5 Operator legality

Every operator must satisfy:

-   deterministic output,
-   explicit mathematical definition,
-   documented units,
-   documented numerical stability,
-   temporal legality.

------------------------------------------------------------------------

# 23.6 Pure operators

A pure operator produces identical output whenever identical inputs are
supplied.

No canonical TSIS operator may depend upon:

-   randomness,
-   hidden state,
-   future observations,
-   implementation side effects.

------------------------------------------------------------------------

# 23.7 Operator composition

Operators may be composed.

Example:

``` text
Trades

↓

Count

↓

Rate

↓

Acceleration

↓

Z-score
```

The resulting feature must preserve the semantic meaning of every
transformation.

------------------------------------------------------------------------

# 23.8 Multi-scale operators

The same operator may be applied over multiple windows.

Example:

``` text
Trade Count Rate

250 ms
1 s
5 s
30 s
```

The operator remains identical.

Only the temporal window changes.

------------------------------------------------------------------------

# 23.9 Normalization operators

Normalization is itself an operator.

Examples:

``` text
raw

per second

per trade

per share

log1p

z-score

historical percentile
```

Normalization changes representation, not semantic ownership.

------------------------------------------------------------------------

# 23.10 Forbidden operators

The following are architecturally illegal:

``` text
Future-dependent transforms

Outcome-conditioned transforms

Reward-based transforms

Model-specific transforms

Vendor-specific hidden transforms
```

Such operations belong outside the canonical representation layer.

------------------------------------------------------------------------

# 23.11 Operator metadata

Every canonical operator shall define:

``` text
operator_name
operator_family
mathematical_definition
input_types
output_type
units
allowed_dependencies
determinism
version
```

------------------------------------------------------------------------

# 23.12 Constitutional rule

Canonical features shall be generated exclusively through governed
operators.

Introducing a new operator modifies the mathematical language of TSIS
and therefore requires architectural governance rather than only
implementation approval.
