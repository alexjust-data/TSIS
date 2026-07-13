# TSIS Market Representation Architecture

## Chapter 17 --- Feature Registry

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 17. Feature Registry

## 17.1 Purpose

The Feature Registry is the constitutional catalogue of every canonical
feature in TSIS.

A feature does not officially exist until it has been registered.

The registry defines semantics, not implementation.

------------------------------------------------------------------------

## 17.2 Fundamental Principle

There is only one authoritative definition for each canonical feature.

Builders, datasets and models may consume a feature.

They may never redefine its meaning.

------------------------------------------------------------------------

## 17.3 Registry responsibilities

The registry guarantees:

-   semantic uniqueness,
-   discoverability,
-   version control,
-   reproducibility,
-   governance,
-   traceability.

It is the single source of truth for feature definitions.

------------------------------------------------------------------------

## 17.4 Registry entry

Each feature shall contain at least:

``` text
feature_name
feature_family
description
mathematical_formula
economic_interpretation
units
primitive_inputs
feature_dependencies
lookback_window
timestamp_semantics
eligibility_policy
alignment_policy
normalization
quality_requirements
materialization_policy
representation_targets
builder_reference
registry_version
feature_version
status
```

------------------------------------------------------------------------

## 17.5 Canonical naming

Feature names shall be:

-   unique,
-   stable,
-   descriptive,
-   implementation independent.

Recommended convention:

``` text
family.feature_name.window.variant
```

Example:

``` text
microstructure.trade_count_rate.5s.raw
```

------------------------------------------------------------------------

## 17.6 Semantic immutability

A canonical feature name owns one semantic meaning.

If the mathematical meaning changes materially:

``` text
new feature version
```

must be created.

Silent semantic drift is forbidden.

------------------------------------------------------------------------

## 17.7 Dependency graph

Every registry entry shall declare dependencies.

Example:

``` text
Trade Primitive
        ↓
Trade Count
        ↓
Trade Count Rate
        ↓
Tape Acceleration
```

The dependency graph must remain acyclic.

------------------------------------------------------------------------

## 17.8 Feature status

Allowed statuses:

``` text
Draft
Experimental
Validated
Canonical
Deprecated
Retired
```

Only Canonical features may enter official production states.

------------------------------------------------------------------------

## 17.9 Registry governance

Every modification requires:

-   rationale,
-   version increment,
-   changelog,
-   compatibility assessment.

Implementations must reference registry versions explicitly.

------------------------------------------------------------------------

## 17.10 Registry independence

The registry is independent of:

-   builders,
-   datasets,
-   machine learning,
-   trading strategies.

It defines scientific meaning only.

------------------------------------------------------------------------

## 17.11 Constitutional rule

No feature may appear inside a Representation or State unless its
semantic definition exists in the Feature Registry.

The Feature Registry is therefore the authoritative language of
quantitative market representation within TSIS.
