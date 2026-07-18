# TSIS Phenomenon Discovery

## Chapter 2 --- Research Questions

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 2. Research Questions

## 2.1 Purpose

Scientific discovery begins with questions rather than answers.

The objective of this chapter is to define how research questions are
formulated inside TSIS.

A research question defines the scope of observation, the population to
study and the evidence required before proposing a phenomenon.

------------------------------------------------------------------------

## 2.2 Fundamental Principle

TSIS does not ask:

> Which strategy makes money?

TSIS first asks:

> Which observable behaviour repeatedly appears under controlled
> conditions?

Profitability is evaluated only after knowledge has been established.

------------------------------------------------------------------------

## 2.3 Characteristics of a valid research question

A research question shall be:

-   observable,
-   measurable,
-   falsifiable,
-   reproducible,
-   population-specific,
-   temporally legal.

Example:

``` text
Does trade intensity systematically increase
before liquidity vacuums?
```

Not:

``` text
Can I make money buying here?
```

------------------------------------------------------------------------

## 2.4 Scope

Every question shall explicitly define:

``` text
Population

Observation Horizon

Representations Consumed

States Used

Control Population

Outcome Horizons
```

------------------------------------------------------------------------

## 2.5 Population before hypothesis

Research always begins by defining the population.

Examples:

``` text
All Halt Events

All Scanner Candidates

All Breakout Candidates

Matched Controls

Random Eligible Samples
```

The same question applied to different populations may produce different
conclusions.

------------------------------------------------------------------------

## 2.6 Hypothesis generation

Only after defining the population may TSIS propose hypotheses.

Example:

``` text
H0:
Trade acceleration is unrelated to subsequent liquidity vacuum.

H1:
Trade acceleration systematically precedes liquidity vacuum.
```

The architecture stores hypotheses separately from observations.

------------------------------------------------------------------------

## 2.7 Evidence requirements

A hypothesis cannot become a phenomenon without evidence.

Evidence should include:

-   repeated observations,
-   statistical consistency,
-   robustness across regimes,
-   comparison against controls,
-   reproducibility.

------------------------------------------------------------------------

## 2.8 Negative results

Negative evidence is part of scientific knowledge.

Rejected hypotheses remain valuable because they reduce future search
space.

TSIS preserves failed hypotheses as research artefacts.

------------------------------------------------------------------------

## 2.9 Documentation

Every research question shall declare:

``` text
question_id
question_text
population_id
state_version
representation_versions
control_population
validation_protocol
status
```

------------------------------------------------------------------------

## 2.10 Constitutional rule

Research questions define the beginning of scientific discovery.

Phenomena are never assumed.

They emerge only after disciplined investigation of explicitly declared
questions.
