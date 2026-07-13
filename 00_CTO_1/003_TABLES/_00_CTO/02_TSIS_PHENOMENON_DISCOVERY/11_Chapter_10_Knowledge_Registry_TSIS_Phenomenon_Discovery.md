# TSIS Phenomenon Discovery

## Chapter 10 --- Knowledge Registry

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 10. Knowledge Registry

## 10.1 Purpose

The Knowledge Registry is the canonical catalogue of every validated
knowledge object inside TSIS.

Representations describe the market.

Phenomena explain recurring behaviour.

The Knowledge Registry preserves those explanations as reusable
scientific assets.

------------------------------------------------------------------------

## 10.2 Fundamental Principle

Knowledge does not officially exist inside TSIS until it has been
registered.

Registration freezes:

-   semantic meaning,
-   validated scope,
-   supporting evidence,
-   confidence level,
-   lineage.

------------------------------------------------------------------------

## 10.3 Registry responsibilities

The registry guarantees:

-   semantic uniqueness,
-   traceability,
-   reproducibility,
-   discoverability,
-   governance,
-   controlled evolution.

------------------------------------------------------------------------

## 10.4 Registry entry

Every knowledge object shall contain at least:

``` text
knowledge_id
canonical_name
summary
research_question_id
supporting_hypotheses
supporting_phenomena
validated_population
control_population
confidence_level
limitations
supporting_evidence
feature_registry_version
state_version
validation_protocol
knowledge_version
status
```

------------------------------------------------------------------------

## 10.5 Canonical naming

Knowledge names shall describe the phenomenon rather than a strategy.

Preferred:

``` text
Liquidity Vacuum
Price Discovery
Volatility Compression
```

Avoid:

``` text
Buy Setup
Opening Long
Best Breakout
```

------------------------------------------------------------------------

## 10.6 Scientific scope

Every knowledge object shall explicitly define:

``` text
Applicable Markets
Applicable Instruments
Applicable Liquidity
Applicable Time Horizons
Known Failure Modes
```

Knowledge without scope is scientifically incomplete.

------------------------------------------------------------------------

## 10.7 Confidence

Confidence reflects evidence quality.

Example levels:

``` text
Exploratory
Supported
Replicated
Robust
Canonical
```

Confidence is independent of profitability.

------------------------------------------------------------------------

## 10.8 Lineage

Every knowledge object shall remain traceable to:

``` text
Research Question
Hypotheses
Evidence Collections
Phenomena
Representations
Feature Registry
State Builder
```

Knowledge without lineage cannot become canonical.

------------------------------------------------------------------------

## 10.9 Versioning

Semantic changes require a new knowledge version.

Historical versions remain reproducible.

No knowledge object shall be silently modified.

------------------------------------------------------------------------

## 10.10 Constitutional rule

The Knowledge Registry is the institutional memory of TSIS.

Strategies may evolve.

Models may evolve.

Representations may improve.

The registry preserves validated scientific knowledge independently of
every implementation.
