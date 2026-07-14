# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 31 --- Feature Quality

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 31. Feature Quality

## 31.1 Purpose

Feature Quality defines how the intrinsic quality of a feature is
measured independently of any predictive model.

A high-quality feature is one that is mathematically correct,
operationally reliable and scientifically trustworthy.

Quality is evaluated before usefulness.

------------------------------------------------------------------------

## 31.2 Fundamental Principle

Feature quality is independent of predictive performance.

A feature may have:

-   high quality and low predictive value,
-   low quality and apparently high predictive value.

Only the former is eligible for canonical promotion.

------------------------------------------------------------------------

## 31.3 Quality dimensions

Every feature shall be evaluated along the following dimensions:

``` text
Mathematical Correctness
Temporal Legality
Coverage
Completeness
Stability
Robustness
Interpretability
Traceability
Operational Reliability
```

------------------------------------------------------------------------

## 31.4 Coverage

Coverage measures the proportion of the eligible population for which
the feature can be computed.

Typical metrics:

``` text
eligible_rows
materialized_rows
coverage_ratio
missing_ratio
```

Coverage must always be reported.

------------------------------------------------------------------------

## 31.5 Completeness

Completeness evaluates whether all required inputs were available.

Incomplete features must expose explicit missingness rather than
silently imputing values unless a documented policy exists.

------------------------------------------------------------------------

## 31.6 Stability

A feature should remain statistically stable across:

-   market regimes,
-   years,
-   instruments,
-   exchanges,
-   liquidity profiles.

Observed instability shall be documented rather than hidden.

------------------------------------------------------------------------

## 31.7 Robustness

A feature should be resilient to:

-   small input perturbations,
-   vendor differences,
-   implementation changes,
-   partition boundaries.

Robustness is measured through reproducible sensitivity analyses.

------------------------------------------------------------------------

## 31.8 Interpretability

Every canonical feature shall possess:

-   mathematical interpretation,
-   economic interpretation,
-   semantic ownership.

Features whose meaning cannot be explained remain experimental.

------------------------------------------------------------------------

## 31.9 Traceability

Every feature must be traceable to:

``` text
Primitives
Builders
Contracts
Registry
Materialization
Validation
```

Loss of lineage invalidates canonical status.

------------------------------------------------------------------------

## 31.10 Operational reliability

Operational quality includes:

``` text
builder success rate
quality gate pass rate
runtime stability
schema compatibility
version consistency
```

Implementation failures are quality failures.

------------------------------------------------------------------------

## 31.11 Quality score

TSIS may compute composite quality indicators for operational
monitoring.

Such scores are engineering diagnostics only.

They never replace the underlying quality dimensions.

------------------------------------------------------------------------

## 31.12 Constitutional rule

Canonical promotion requires demonstrably high feature quality.

Quality shall always be evaluated independently from predictive
performance, trading profitability or model preference.
