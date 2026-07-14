# TSIS Phenomenon Discovery

## Chapter 8 --- Strategy Emergence

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 8. Strategy Emergence

## 8.1 Purpose

The objective of this chapter is to define how trading strategies emerge
from validated scientific knowledge inside TSIS.

Strategies are **not** starting assumptions.

They are downstream consequences of validated knowledge.

------------------------------------------------------------------------

## 8.2 Fundamental Principle

TSIS does not search directly for profitable strategies.

TSIS discovers:

``` text
Observations
    ↓
Representations
    ↓
Phenomena
    ↓
Knowledge
    ↓
Strategies
```

A strategy is therefore an engineering application of scientific
knowledge.

------------------------------------------------------------------------

## 8.3 Definition

A strategy is a governed decision policy derived from one or more
validated knowledge objects.

Strategies are consumers.

Knowledge remains the producer.

------------------------------------------------------------------------

## 8.4 One-to-many relationship

One phenomenon may support many strategies.

Example:

``` text
Phenomenon:
Liquidity Vacuum

Possible Strategies:
- Momentum Breakout
- Pullback Continuation
- Exhaustion Fade
- Execution Timing
```

The phenomenon is stable.

Strategies may evolve independently.

------------------------------------------------------------------------

## 8.5 Many-to-one relationship

One strategy may require several knowledge objects.

Example:

``` text
Liquidity Vacuum
+
Price Discovery
+
Execution Difficulty
+
Spread Compression
```

↓

``` text
Breakout Strategy
```

Knowledge is composable.

------------------------------------------------------------------------

## 8.6 Strategy hypotheses

A strategy remains a hypothesis until validated.

It should explicitly declare:

``` text
knowledge_dependencies
state_requirements
decision_policy
execution_policy
risk_policy
validation_protocol
```

------------------------------------------------------------------------

## 8.7 Independence

Changing a strategy shall never redefine:

-   features,
-   representations,
-   states,
-   phenomena,
-   knowledge.

Scientific layers remain independent from strategy implementation.

------------------------------------------------------------------------

## 8.8 Multiple consumers

Validated knowledge may simultaneously support:

-   discretionary trading,
-   systematic trading,
-   execution optimisation,
-   reinforcement learning,
-   imitation learning,
-   AlphaEvolve,
-   portfolio construction.

Knowledge is model-independent.

------------------------------------------------------------------------

## 8.9 Failure of a strategy

Failure of one strategy does not invalidate the underlying knowledge.

Possible causes include:

-   execution constraints,
-   transaction costs,
-   inappropriate policy,
-   poor risk management,
-   regime mismatch.

Knowledge and strategy must therefore be evaluated separately.

------------------------------------------------------------------------

## 8.10 Constitutional rule

Strategies are applications of validated knowledge.

TSIS shall always prefer discovering better knowledge over tuning
existing strategies.

Scientific understanding remains the primary objective.
