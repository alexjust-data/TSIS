# TSIS Market Representation Architecture

## Chapter 7 --- Representation Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 7. Representation Layer

## 7.1 Purpose

The Representation Layer organizes individual features into coherent
semantic models of the observable market.

A feature measures one property.

A representation explains one domain.

Representations are the bridge between isolated measurements and
complete market states.

------------------------------------------------------------------------

## 7.2 Definition

A representation is a structured, versioned and semantically coherent
collection of related features describing one domain of market
behaviour.

Representations are model-independent.

They exist before any prediction or strategy.

------------------------------------------------------------------------

## 7.3 Why representations exist

Without representations, features become isolated variables.

Representations provide:

-   semantic organization,
-   interpretability,
-   composability,
-   reuse,
-   governance.

A representation answers:

> "Which observable properties jointly describe this aspect of the
> market?"

------------------------------------------------------------------------

## 7.4 Canonical representations

Typical representations include:

``` text
Microstructure Representation
Intraday Representation
Daily Representation
Fundamental Representation
News Representation
Short Context Representation
Regime Representation
Quality Representation
Execution Representation
```

Each representation owns one semantic domain.

------------------------------------------------------------------------

## 7.5 Representation composition

Representations consume only legal features.

``` text
Primitive
    ↓
Feature
    ↓
Representation
```

Representations must never consume:

``` text
Decision
Outcome
Reward
Future information
```

------------------------------------------------------------------------

## 7.6 Representation independence

Representations are independent of:

-   machine learning models,
-   trading strategies,
-   execution policies,
-   optimisation algorithms.

They describe the market itself.

------------------------------------------------------------------------

## 7.7 Internal consistency

All features inside one representation shall satisfy:

-   identical timestamp semantics,
-   compatible lookback policy,
-   identical observability assumptions,
-   compatible materialization policy,
-   documented lineage.

------------------------------------------------------------------------

## 7.8 Representation metadata

Every representation shall declare:

``` text
representation_name
representation_family
representation_version
feature_registry_version
builder_version
coverage_policy
lookback_policy
materialization_policy
quality_requirements
```

------------------------------------------------------------------------

## 7.9 Representation boundaries

A representation may contain multiple feature families.

Example:

``` text
Microstructure Representation

Spread
Top Depth
Microprice
OFI
Trade Count Rate
Signed Flow
Quote Update Rate
Burstiness
```

But it may not include:

``` text
Entry Signal
Expected Return
Reward
Future Label
```

These belong to downstream layers.

------------------------------------------------------------------------

## 7.10 Representation reuse

One representation may be reused by many states.

Example:

``` text
Microstructure Representation
            │
            ├── Market State
            ├── Event State
            ├── Strategy State
            └── Execution State
```

Representations are reusable semantic components.

------------------------------------------------------------------------

## 7.11 Representation versioning

Representations evolve only through explicit version changes.

Changing:

-   feature definitions,
-   feature membership,
-   semantic meaning,

requires a new representation version.

Silent semantic drift is forbidden.

------------------------------------------------------------------------

## 7.12 Representation validation

A representation is valid only if:

-   every feature exists in the Feature Registry,
-   every feature passes eligibility,
-   timestamps are legal,
-   lineage is complete,
-   quality gates succeed.

------------------------------------------------------------------------

## 7.13 Constitutional rule

Representations are the official semantic language of TSIS.

States are constructed from representations.

Representations are never constructed from decisions or outcomes.

They constitute the canonical bridge between engineered features and
observable market states.
