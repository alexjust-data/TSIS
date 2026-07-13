# TSIS Market Representation Architecture

## Chapter 8 --- State Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 8. State Layer

## 8.1 Purpose

The State Layer is the highest level of observable market representation
inside TSIS.

A state does not predict.

A state does not recommend.

A state does not evaluate.

A state answers one question:

> **What is observable about the market at this exact decision
> timestamp?**

------------------------------------------------------------------------

## 8.2 Definition

A state is a complete, point-in-time, temporally legal composition of
one or more market representations evaluated at a single decision
timestamp.

States are immutable historical snapshots.

------------------------------------------------------------------------

## 8.3 States are not datasets

A state is not:

-   a feature table,
-   a prediction,
-   a signal,
-   a trading rule,
-   an execution instruction,
-   an outcome.

States are semantic objects.

------------------------------------------------------------------------

## 8.4 State composition

A state is built only from legal representations.

``` text
Primitive
    ↓
Feature
    ↓
Representation
    ↓
State
```

States never consume:

``` text
Decision
Outcome
Reward
Future information
```

------------------------------------------------------------------------

## 8.5 Canonical state families

Examples:

``` text
Market State
Event State
Strategy State
Execution State
Position State
```

Each family answers a different scientific question.

------------------------------------------------------------------------

## 8.6 Market State

Purpose:

Describe the complete observable market independently of any strategy.

Typical representations:

``` text
Identity
Calendar
Daily
Intraday
Microstructure
Fundamentals
News
Short Context
Regime
Quality
Scanner Context
```

Question answered:

> What was observable now?

------------------------------------------------------------------------

## 8.7 Event State

Purpose:

Describe the observable market around a governed event window.

An Event State equals:

``` text
Market State
+
Event Window
+
State Role
+
Decision Timestamp
```

It does not imply a trading opportunity.

------------------------------------------------------------------------

## 8.8 Strategy State

Purpose:

Describe the observable geometry required by one strategy family.

Examples:

``` text
Breakout State
VWAP Reclaim State
Pullback State
```

Strategy States remain observable.

They must not contain decisions.

------------------------------------------------------------------------

## 8.9 Execution State

Purpose:

Describe execution conditions.

Typical components:

``` text
Spread
Visible Liquidity
Quote Stability
Expected Slippage
Execution Constraints
Borrow State
```

Execution States answer:

> Can the theoretical decision be executed realistically?

------------------------------------------------------------------------

## 8.10 Position State

Purpose:

Describe an already existing position.

Typical components:

``` text
Entry Price
Current PnL
Time in Trade
Distance to Stop
Distance to Target
Current Market State
```

Position States belong to sequential decision making.

------------------------------------------------------------------------

## 8.11 Decision timestamp

Every state shall declare exactly one decision timestamp.

Every feature inside the state must satisfy:

``` text
feature_timestamp <= decision_timestamp
```

No exception is allowed.

------------------------------------------------------------------------

## 8.12 State metadata

Minimum metadata:

``` text
state_type
state_version
decision_timestamp
coverage_policy
lookback_policy
feature_set_version
representation_versions
builder_version
quality_state
```

------------------------------------------------------------------------

## 8.13 State legality

A state is legal only if:

-   all constituent representations are legal,
-   every feature satisfies observability,
-   no outcome is included,
-   no future information is consumed.

------------------------------------------------------------------------

## 8.14 State reproducibility

Rebuilding the same state using:

-   identical raw inputs,
-   identical contracts,
-   identical builder versions,

must produce identical results.

------------------------------------------------------------------------

## 8.15 Constitutional rule

States constitute the official observable interface between market
representation and decision making.

Every learning algorithm, trading strategy, statistical model and
optimisation process must consume states rather than raw observations
whenever a complete market description is required.
