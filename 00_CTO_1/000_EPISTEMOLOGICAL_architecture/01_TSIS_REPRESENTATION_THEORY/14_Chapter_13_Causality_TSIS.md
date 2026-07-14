# TSIS Market Representation Architecture

## Chapter 13 --- Causality

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 13. Causality

## 13.1 Purpose

The purpose of this chapter is to distinguish **observation**,
**association**, **prediction**, and **causation** inside TSIS.

TSIS does not assume that predictive performance implies causal
understanding.

Representations describe the market.

Research evaluates hypotheses.

Only rigorous experimentation may support causal claims.

------------------------------------------------------------------------

## 13.2 Fundamental principle

Correlation is not causation.

Prediction is not causation.

Feature importance is not causation.

Every causal statement requires evidence beyond statistical association.

------------------------------------------------------------------------

## 13.3 Causal hierarchy

``` text
Observation
    ↓
Association
    ↓
Prediction
    ↓
Causal Hypothesis
    ↓
Empirical Validation
```

Only the first three layers belong naturally to Data Foundation.

------------------------------------------------------------------------

## 13.4 Observable causes

TSIS allows only observable causes.

Examples:

``` text
Trade intensity
Spread
OFI
Microprice
News publication
Trading halt
Corporate action
```

Latent explanations remain hypotheses until supported by evidence.

------------------------------------------------------------------------

## 13.5 Causal hypotheses

A causal hypothesis proposes that changing one observable property
changes another.

Examples:

``` text
Increasing spread precedes lower execution quality.

Large positive OFI precedes short-term upward pressure.

Trading halts modify subsequent liquidity regimes.
```

These are hypotheses, not architectural truths.

------------------------------------------------------------------------

## 13.6 Representation neutrality

Representations must remain neutral.

They shall never encode:

``` text
This feature causes price.
```

Instead they encode:

``` text
This feature measures an observable property.
```

Causal interpretation belongs to research.

------------------------------------------------------------------------

## 13.7 Strategy independence

A strategy may rely on a causal hypothesis.

The representation layer must not.

Therefore:

``` text
Representation
    ↓
Research
    ↓
Causal Evidence
    ↓
Strategy
```

------------------------------------------------------------------------

## 13.8 Validation

Causal claims require:

-   out-of-sample validation,
-   temporal consistency,
-   robustness across market regimes,
-   robustness across instruments,
-   alternative explanations considered.

------------------------------------------------------------------------

## 13.9 Forbidden assumptions

The following statements are architecturally invalid unless supported by
explicit research:

``` text
Feature X causes breakout.

Indicator Y predicts all reversals.

Microprice guarantees future direction.
```

Such claims belong only inside documented research outputs.

------------------------------------------------------------------------

## 13.10 Constitutional rule

TSIS stores measurements.

TSIS represents observations.

TSIS evaluates hypotheses.

TSIS never embeds causal conclusions inside its representation
architecture.

Causality is the responsibility of scientific research, not of the data
model.
