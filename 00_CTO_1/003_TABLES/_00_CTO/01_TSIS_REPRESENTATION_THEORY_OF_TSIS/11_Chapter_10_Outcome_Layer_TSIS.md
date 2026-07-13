# TSIS Market Representation Architecture

## Chapter 10 --- Outcome Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 10. Outcome Layer

## 10.1 Purpose

The Outcome Layer evaluates what happened after a decision timestamp.

Outcomes never describe the market at decision time.

They exist exclusively to evaluate hypotheses, decisions, policies and
execution.

------------------------------------------------------------------------

## 10.2 Fundamental Principle

``` text
State
    describes

Decision
    chooses

Outcome
    evaluates
```

No outcome may participate in state construction.

------------------------------------------------------------------------

## 10.3 Definition

An outcome is a deterministic measurement computed strictly after a
reference timestamp.

The reference timestamp may be:

-   decision timestamp,
-   event timestamp,
-   execution timestamp,
-   anchor timestamp.

------------------------------------------------------------------------

## 10.4 Outcome families

Typical families include:

``` text
Price Outcomes
Path Outcomes
Execution Outcomes
Event Outcomes
Risk Outcomes
Opportunity Outcomes
```

Examples:

``` text
Future Return
MFE
MAE
Time to Target
Time to Stop
Breakout Success
Second Halt
Execution Cost
Slippage
Realized Spread
```

------------------------------------------------------------------------

## 10.5 Temporal legality

Every outcome shall declare:

``` text
reference_timestamp
evaluation_horizon
evaluation_window
builder_version
```

The evaluation interval must begin strictly after the reference
timestamp.

------------------------------------------------------------------------

## 10.6 Inputs

Outcomes may consume:

-   future observations,
-   future primitives,
-   future features,
-   execution records.

They may never be consumed by:

``` text
Market State
Event State
Feature Layer
Representation Layer
```

------------------------------------------------------------------------

## 10.7 Outcome metadata

Minimum metadata:

``` text
outcome_name
outcome_family
reference_timestamp
evaluation_start
evaluation_end
units
builder_version
quality_state
```

------------------------------------------------------------------------

## 10.8 Outcome reproducibility

Identical:

-   raw inputs,
-   horizons,
-   contracts,
-   builders,

must always generate identical outcomes.

------------------------------------------------------------------------

## 10.9 Outcome independence

Outcome definitions are independent of:

-   strategy,
-   model,
-   optimizer,
-   reinforcement learning algorithm.

The same outcome may evaluate many different policies.

------------------------------------------------------------------------

## 10.10 Constitutional rule

Outcomes belong exclusively to the evaluation layer.

They are never observable at decision time.

Any architecture allowing outcomes to influence states, representations
or features intended for decision making violates the temporal integrity
of TSIS.
