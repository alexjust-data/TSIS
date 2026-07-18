# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 29 --- Meta-Features

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 29. Meta-Features

## 29.1 Purpose

Meta-features describe the behaviour of other features rather than
describing primitives directly.

They measure stability, evolution, uncertainty, relationships and
quality of existing canonical features.

Meta-features therefore operate one semantic level above ordinary
features while remaining fully observable.

------------------------------------------------------------------------

## 29.2 Fundamental Principle

A canonical feature measures an observable market property.

A meta-feature measures an observable property of one or more canonical
features.

``` text
Primitive
    ↓
Feature
    ↓
Meta-Feature
```

Meta-features never consume:

``` text
Decision
Outcome
Reward
Future information
```

------------------------------------------------------------------------

## 29.3 Definition

A meta-feature is a deterministic mathematical transformation whose
inputs are canonical features rather than primitives.

Its purpose is to quantify higher-order structure without introducing
future knowledge.

------------------------------------------------------------------------

## 29.4 Why Meta-Features exist

Many relevant properties cannot be described by a single feature value.

Examples include:

``` text
Feature stability
Feature volatility
Feature acceleration
Feature agreement
Feature disagreement
Historical rarity
Cross-feature coherence
```

These properties become observable only after features themselves have
been constructed.

------------------------------------------------------------------------

## 29.5 Canonical Meta-Feature classes

### Stability

Examples:

``` text
Rolling Standard Deviation
Coefficient of Variation
Historical Drift
Persistence
```

------------------------------------------------------------------------

### Dynamics

Examples:

``` text
Feature Velocity
Feature Acceleration
Feature Jerk
```

------------------------------------------------------------------------

### Relative Position

Examples:

``` text
Historical Percentile
Rolling Rank
Distance to Historical Mean
Z-Score
```

------------------------------------------------------------------------

### Agreement

Examples:

``` text
Feature Correlation
Directional Agreement
Consensus Ratio
```

------------------------------------------------------------------------

### Diversity

Examples:

``` text
Entropy of Feature Family
Cross-Feature Dispersion
Feature Concentration
```

------------------------------------------------------------------------

## 29.6 Examples

Example:

``` text
Trade Count Rate
        ↓
Historical Percentile
```

The percentile is a meta-feature.

Example:

``` text
Spread
        ↓
Spread Volatility
```

The volatility of spread is a meta-feature.

Example:

``` text
OFI
        ↓
OFI Stability
```

The stability measurement is a meta-feature.

------------------------------------------------------------------------

## 29.7 Temporal legality

Meta-features obey the same temporal rules as ordinary features.

Every input feature must satisfy:

``` text
feature_timestamp <= decision_timestamp
```

Future observations remain prohibited.

------------------------------------------------------------------------

## 29.8 Registry

Every meta-feature shall declare:

``` text
meta_feature_name
input_features
operator_chain
window_policy
normalization
semantic_interpretation
version
```

Meta-features belong to the same governance process as canonical
features.

------------------------------------------------------------------------

## 29.9 Representation

Meta-features may participate in:

``` text
Market Representation
Event Representation
Execution Representation
```

provided they satisfy observability and semantic clarity.

------------------------------------------------------------------------

## 29.10 Constitutional rule

Meta-features enrich the description of existing observable properties.

They never replace canonical features and never introduce future
information.

They remain descriptive objects within the Representation Layer and
shall not encode decisions, rewards or outcomes.
