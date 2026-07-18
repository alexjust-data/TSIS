# TSIS Market Representation Architecture

## PART II --- Feature Engineering Theory

### Chapter 32 --- Feature Selection vs Representation

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 32. Feature Selection vs Representation

## 32.1 Purpose

This chapter separates two concepts that are frequently confused:

-   representing the market;
-   selecting variables for a particular model.

TSIS treats these as independent scientific problems.

------------------------------------------------------------------------

## 32.2 Fundamental Principle

Representation answers:

> What is observable?

Feature Selection answers:

> Which observable properties are useful for this specific consumer?

Selection never defines representation.

------------------------------------------------------------------------

## 32.3 Representation-first philosophy

Canonical features are created because they represent measurable market
properties.

They are **not** created because a model currently benefits from them.

Representation therefore precedes:

-   supervised learning,
-   reinforcement learning,
-   optimization,
-   strategy development.

------------------------------------------------------------------------

## 32.4 Selection is consumer-specific

Different consumers may select different subsets:

``` text
Execution Model

↓

Execution Features

Pattern Discovery

↓

Microstructure Features

Portfolio Model

↓

Daily + Regime Features
```

The canonical feature universe remains unchanged.

------------------------------------------------------------------------

## 32.5 Canonical feature universe

The Feature Registry defines the complete canonical representation.

Selection creates temporary views of that universe.

Selections shall never redefine:

-   semantics,
-   formulas,
-   ownership,
-   versions.

------------------------------------------------------------------------

## 32.6 Selection criteria

Selection may consider:

-   relevance,
-   redundancy,
-   computational cost,
-   latency,
-   stability,
-   interpretability,
-   model requirements.

Selection must never alter feature definitions.

------------------------------------------------------------------------

## 32.7 Research reproducibility

Every feature selection process shall declare:

``` text
selection_method
selection_timestamp
feature_registry_version
selection_population
selection_version
```

This guarantees reproducible experiments.

------------------------------------------------------------------------

## 32.8 Dynamic selection

Selections may change over time.

Representations should remain stable.

A model may choose different features tomorrow without changing the
canonical architecture.

------------------------------------------------------------------------

## 32.9 Forbidden practices

The following are architecturally invalid:

``` text
Removing canonical features because one model ignores them.

Changing feature semantics to improve one experiment.

Renaming features after model training.
```

------------------------------------------------------------------------

## 32.10 Constitutional rule

Representation belongs to TSIS.

Feature selection belongs to the consumer.

The canonical representation shall remain independent of every
downstream modelling choice.
