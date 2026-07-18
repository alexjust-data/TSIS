# TSIS Market Representation Architecture

## Chapter 14 --- Feature Families

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 14. Feature Families

## 14.1 Purpose

Feature families organize the feature universe into coherent semantic
domains.

A family groups features that measure the same aspect of the market,
regardless of implementation details.

The objective is to provide:

-   semantic consistency,
-   governance,
-   discoverability,
-   reuse,
-   controlled evolution.

------------------------------------------------------------------------

## 14.2 Fundamental principle

A feature belongs to **exactly one primary semantic family**.

It may participate in multiple representations, but its semantic
ownership is unique.

------------------------------------------------------------------------

## 14.3 Canonical feature families

``` text
Identity
Calendar
Quality
Daily
Intraday
Microstructure
Fundamentals
News
Short Context
Corporate Actions
Regime
Scanner
Execution
Position
Outcome (evaluation only)
```

------------------------------------------------------------------------

## 14.4 Identity family

Purpose:

Describe the economic identity of the instrument.

Examples:

``` text
instrument_id
ticker
exchange
security_type
listing_age
market_cap
shares_outstanding
```

------------------------------------------------------------------------

## 14.5 Daily family

Purpose:

Describe daily market context.

Examples:

``` text
gap_pct
daily_range_pct
ATR
RVOL
daily_volume
daily_dollar_volume
```

------------------------------------------------------------------------

## 14.6 Intraday family

Purpose:

Describe price evolution within the session.

Examples:

``` text
distance_to_VWAP
distance_to_HOD
distance_to_LOD
session_return
intraday_range
transaction_count_rate
```

------------------------------------------------------------------------

## 14.7 Microstructure family

Purpose:

Describe the observable dynamics of trades and quotes.

Examples:

``` text
spread
microprice
OFI
trade_count_rate
signed_flow
quote_update_rate
top_depth
burstiness
tape_acceleration
```

The Microstructure family is event-level by nature.

------------------------------------------------------------------------

## 14.8 Context families

Contextual families include:

``` text
Fundamentals
News
Short Context
Corporate Actions
Regime
```

They describe the environment surrounding market activity.

------------------------------------------------------------------------

## 14.9 Execution family

Purpose:

Describe whether a theoretical action is realistically executable.

Examples:

``` text
expected_slippage
spread_cost
visible_liquidity
borrow_state
execution_constraints
```

Execution features shall never contaminate market representation.

------------------------------------------------------------------------

## 14.10 Family independence

Each family evolves independently.

Adding or modifying one family must not require semantic changes in
unrelated families.

------------------------------------------------------------------------

## 14.11 Family metadata

Every family shall define:

``` text
family_name
description
owner
canonical_scope
input_primitives
allowed_dependencies
representation_targets
version
```

------------------------------------------------------------------------

## 14.12 Allowed dependencies

Legal dependency examples:

``` text
Daily → Intraday

Intraday → Microstructure

Identity → Any
```

Forbidden examples:

``` text
Outcome → Microstructure

Decision → Daily

Reward → Representation
```

------------------------------------------------------------------------

## 14.13 Family evolution

Families may grow by adding new features.

Existing feature semantics must remain stable.

Semantic breaking changes require a new feature version rather than
silent modification.

------------------------------------------------------------------------

## 14.14 Constitutional rule

Feature families are semantic containers.

They organize market knowledge.

They do not encode trading logic, prediction or evaluation.

Their only responsibility is to classify measurable properties of the
observable market.
