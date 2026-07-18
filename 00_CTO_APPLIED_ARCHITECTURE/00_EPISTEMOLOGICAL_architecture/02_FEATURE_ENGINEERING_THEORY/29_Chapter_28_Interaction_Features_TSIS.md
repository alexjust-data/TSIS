# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 28 --- Interaction Features

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 28. Interaction Features

## 28.1 Purpose

Individual features measure isolated observable properties.

Interaction Features measure the relationship between two or more
independent observable properties.

The objective is to represent emergent market behaviour that cannot be
described by either feature independently.

------------------------------------------------------------------------

## 28.2 Fundamental Principle

An interaction feature is not a simple arithmetic combination.

It represents a new observable property arising from the interaction of
canonical features.

Example:

``` text
Spread
```

and

``` text
Trade Count Rate
```

remain meaningful independently.

However:

``` text
Spread × Trade Count Rate
```

may describe market pressure rather than either variable alone.

------------------------------------------------------------------------

## 28.3 Definition

An Interaction Feature is a deterministic mathematical transformation
combining two or more canonical features while preserving:

-   temporal legality,
-   semantic traceability,
-   deterministic computation,
-   reproducibility.

------------------------------------------------------------------------

## 28.4 Why interactions exist

Many market phenomena emerge only when multiple properties are observed
simultaneously.

Examples include:

``` text
High Trade Rate
+
Spread Compression

High OFI
+
Microprice Displacement

Gap
+
Relative Volume

VWAP Distance
+
Signed Flow
```

Each interaction captures a distinct observable phenomenon.

------------------------------------------------------------------------

## 28.5 Canonical interaction classes

### Multiplicative

``` text
Feature A × Feature B
```

### Ratio

``` text
Feature A / Feature B
```

### Difference

``` text
Feature A − Feature B
```

### Relative deviation

``` text
(A − B) / B
```

### Conditional interaction

``` text
Feature A evaluated only when Feature B satisfies a governed condition.
```

------------------------------------------------------------------------

## 28.6 Semantic requirements

Every interaction shall answer:

> Which observable market property becomes measurable only through this
> interaction?

If no semantic interpretation exists, the interaction remains
experimental.

------------------------------------------------------------------------

## 28.7 Traceability

Every interaction feature shall declare:

``` text
input_features
interaction_operator
window_policy
normalization
timestamp_semantics
feature_family
version
```

The complete dependency graph must remain reconstructible.

------------------------------------------------------------------------

## 28.8 Examples

Example:

``` text
Trade Count Rate

×

Spread Compression
```

Possible interpretation:

``` text
Observed Liquidity Expansion
```

Example:

``` text
OFI

×

Microprice
```

Possible interpretation:

``` text
Observed Directional Pressure
```

These remain representations, never trading signals.

------------------------------------------------------------------------

## 28.9 Illegal interactions

The following are prohibited:

``` text
Feature × Future Return

Feature × Reward

Feature × Outcome

Feature × Decision
```

Future-dependent interactions violate temporal legality.

------------------------------------------------------------------------

## 28.10 Interaction complexity

Increasing the number of interacting features should improve semantic
richness rather than mathematical complexity alone.

Large interaction graphs require explicit governance.

------------------------------------------------------------------------

## 28.11 Constitutional rule

Interaction Features remain canonical observable representations.

They describe relationships between observable properties.

They never encode policies, actions, labels or outcomes.
