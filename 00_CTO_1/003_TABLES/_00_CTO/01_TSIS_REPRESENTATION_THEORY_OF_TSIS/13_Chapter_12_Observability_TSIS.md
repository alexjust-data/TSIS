# TSIS Market Representation Architecture

## Chapter 12 --- Observability

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 12. Observability

## 12.1 Purpose

Observability determines whether an object may legally exist inside a
State.

An object is observable if, and only if, it can be constructed
exclusively from information available at or before the reference
timestamp.

Observability is independent of predictive power.

------------------------------------------------------------------------

## 12.2 Fundamental principle

TSIS distinguishes between:

``` text
Observable
```

and

``` text
Knowable only in hindsight
```

Only observable information may participate in market representation.

------------------------------------------------------------------------

## 12.3 Classes of observability

### Directly observable

Measured directly from primitives.

Examples:

``` text
Trade Price
Bid
Ask
Volume
VWAP
Spread
```

### Derived observable

Computed from observable inputs only.

Examples:

``` text
Trade Count Rate
OFI
Microprice
ATR
Gap %
Distance to VWAP
```

### Non-observable

Requires future information.

Examples:

``` text
Future Return
MFE
MAE
Reward
Breakout Success
```

------------------------------------------------------------------------

## 12.4 Observable eligibility

Every observable shall satisfy:

-   temporal legality,
-   canonical lineage,
-   deterministic construction,
-   documented dependencies,
-   quality requirements.

Failure of any condition makes the observable ineligible.

------------------------------------------------------------------------

## 12.5 Quality gates

Observability depends not only on timestamps but also on data quality.

Typical gates include:

``` text
Coverage
Timestamp validity
Sequence integrity
Quote alignment confidence
Price validity
Quality certification
```

------------------------------------------------------------------------

## 12.6 Point-in-time context

Contextual datasets remain observable only if their publication time
precedes the decision timestamp.

Examples:

``` text
Fundamentals
News
Short Interest
Corporate Actions
Scanner Outputs
```

The effective availability timestamp must always be respected.

------------------------------------------------------------------------

## 12.7 Observable dependencies

Legal dependency graph:

``` text
Primitive
    ↓
Observable Feature
    ↓
Representation
    ↓
State
```

Illegal dependencies:

``` text
Outcome → Observable

Decision → Observable

Future Feature → Observable
```

------------------------------------------------------------------------

## 12.8 Observable contracts

Every observable shall declare:

``` text
observable_name
observable_family
formula
inputs
timestamp_semantics
eligibility_policy
quality_requirements
version
```

------------------------------------------------------------------------

## 12.9 Observability testing

Every builder shall provide automated tests proving:

-   temporal legality,
-   dependency legality,
-   deterministic output,
-   quality compliance.

Observability is therefore a verifiable property, not an assumption.

------------------------------------------------------------------------

## 12.10 Constitutional rule

Nothing enters a TSIS State merely because it is useful.

An object enters a State only after proving that it is legally
observable at the declared decision timestamp.
