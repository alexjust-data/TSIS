# TSIS Market Representation Architecture

## Chapter 9 --- Decision Layer

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 9. Decision Layer

## 9.1 Purpose

The Decision Layer transforms observable market states into executable
actions.

It is the first layer that introduces intentional behaviour into TSIS.

Everything below the Decision Layer is descriptive.

Everything from the Decision Layer onward is prescriptive.

------------------------------------------------------------------------

## 9.2 Fundamental Principle

States describe.

Decisions choose.

Outcomes evaluate.

These three concepts shall never be merged.

------------------------------------------------------------------------

## 9.3 Definition

A decision is the output of a policy applied to one or more valid
states.

A decision is never an observable property of the market.

It is an action selected by an agent.

------------------------------------------------------------------------

## 9.4 Inputs

A Decision Layer may consume:

``` text
Market State
Event State
Strategy State
Execution State
Position State
```

It may also consume:

-   policy parameters,
-   risk limits,
-   capital constraints.

It may never consume:

``` text
Future outcomes
Future returns
Rewards
Labels
```

------------------------------------------------------------------------

## 9.5 Outputs

Typical decisions include:

``` text
Do Nothing
Enter Long
Enter Short
Exit
Scale In
Scale Out
Cancel
Modify Order
```

The action space is policy-dependent but must be explicitly documented.

------------------------------------------------------------------------

## 9.6 Policy independence

The Decision Layer does not prescribe one decision model.

Examples:

-   rule-based systems,
-   statistical models,
-   supervised learning,
-   reinforcement learning,
-   imitation learning,
-   evolutionary search,
-   human discretionary policies.

All consume the same semantic state.

------------------------------------------------------------------------

## 9.7 Decision legality

Every decision shall declare:

``` text
decision_timestamp
policy_version
state_version
execution_constraints
```

No decision may use information unavailable at its timestamp.

------------------------------------------------------------------------

## 9.8 Separation from execution

A decision is not an execution.

Example:

``` text
Decision:
Buy

Execution:
Partial fill
```

Execution belongs to downstream operational layers.

------------------------------------------------------------------------

## 9.9 Reproducibility

Given:

-   identical states,
-   identical policies,
-   identical parameters,

the decision process must be reproducible.

------------------------------------------------------------------------

## 9.10 Constitutional rule

The Decision Layer is the only architectural layer allowed to transform
market knowledge into actions.

Representations and states must remain action-independent.

Outcomes must remain action-evaluation objects only.
