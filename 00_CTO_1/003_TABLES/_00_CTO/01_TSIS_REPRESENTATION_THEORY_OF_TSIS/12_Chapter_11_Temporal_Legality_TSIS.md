# TSIS Market Representation Architecture

## Chapter 11 --- Temporal Legality

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 11. Temporal Legality

## 11.1 Purpose

Temporal legality is the constitutional principle that guarantees every
object inside TSIS is constructed only from information that was
legitimately observable at the reference timestamp.

Without temporal legality, reproducible market research is impossible.

------------------------------------------------------------------------

## 11.2 Fundamental principle

Every object inside TSIS belongs to one of two categories:

``` text
Observable before t
```

or

``` text
Observable only after t
```

No object may simultaneously belong to both.

------------------------------------------------------------------------

## 11.3 Decision timestamp

Every state shall declare exactly one canonical decision timestamp.

All upstream objects must satisfy:

``` text
observation_timestamp <= decision_timestamp
```

------------------------------------------------------------------------

## 11.4 Allowed information

The following objects may legally contribute to a state:

-   historical observations,
-   historical primitives,
-   historical features,
-   historical representations,
-   completed historical outcomes occurring strictly before the decision
    timestamp.

------------------------------------------------------------------------

## 11.5 Forbidden information

The following objects are illegal inside any state:

``` text
Future prices
Future returns
Future spreads
Future labels
Future rewards
Future executions
Future outcomes
```

------------------------------------------------------------------------

## 11.6 Lookback windows

Lookback windows are legal because they terminate at the decision
timestamp.

Examples:

``` text
Last 5 seconds
Last 5 minutes
Current session up to t
Previous 20 trading days
```

No lookback may extend beyond the decision timestamp.

------------------------------------------------------------------------

## 11.7 Outcome separation

Outcomes begin strictly after the reference timestamp.

Therefore:

``` text
State
    ↓
Decision
    ↓
Outcome
```

The reverse dependency is forbidden.

------------------------------------------------------------------------

## 11.8 Point-in-time data

Every contextual dataset must respect point-in-time availability.

Examples include:

-   fundamentals,
-   news,
-   short interest,
-   corporate actions,
-   scanner outputs.

Availability dates must be explicitly documented.

------------------------------------------------------------------------

## 11.9 Leakage

Leakage exists whenever information unavailable at the decision
timestamp influences a feature, representation or state.

Leakage may be:

-   explicit,
-   implicit,
-   temporal,
-   statistical,
-   implementation-induced.

All forms are prohibited.

------------------------------------------------------------------------

## 11.10 Validation

Every builder shall expose temporal validation proving that all consumed
inputs satisfy the declared timestamp policy.

Temporal legality must be testable.

------------------------------------------------------------------------

## 11.11 Constitutional rule

Temporal legality has precedence over predictive performance.

Any implementation that improves results by violating temporal legality
is architecturally invalid and shall not become part of TSIS.
