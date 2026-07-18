# TSIS Phenomenon Discovery

## Chapter 6 --- Knowledge Formation

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 6. Knowledge Formation

## 6.1 Purpose

Phenomena are validated explanations of recurring observable behaviour.

Knowledge is produced only after multiple validated phenomena have been
integrated into a coherent scientific understanding.

Knowledge is therefore a higher-order object than a phenomenon.

------------------------------------------------------------------------

## 6.2 Fundamental Principle

A phenomenon answers:

> What recurring behaviour appears to exist?

Knowledge answers:

> Under what conditions does this behaviour occur, why is it relevant,
> how reliable is it, and where does it cease to apply?

Knowledge is evidence organized into reusable scientific understanding.

------------------------------------------------------------------------

## 6.3 Knowledge hierarchy

``` text
Observation
        ↓
Representation
        ↓
Research Question
        ↓
Hypothesis
        ↓
Evidence
        ↓
Phenomenon
        ↓
Knowledge
```

Knowledge is never created directly from observations.

------------------------------------------------------------------------

## 6.4 Definition

A knowledge object is a governed scientific conclusion supported by one
or more validated phenomena together with their documented scope,
limitations and supporting evidence.

Knowledge remains conditional.

It is never treated as absolute truth.

------------------------------------------------------------------------

## 6.5 Knowledge components

Every knowledge object should include:

``` text
Research Question

Supporting Phenomena

Supporting Evidence

Validated Population

Control Population

Known Limitations

Confidence Assessment

Applicable Contexts
```

------------------------------------------------------------------------

## 6.6 Domain specificity

Knowledge is always conditional upon:

-   market,
-   instrument class,
-   liquidity profile,
-   temporal horizon,
-   research population,
-   available observations.

Generalization beyond the validated scope requires additional evidence.

------------------------------------------------------------------------

## 6.7 Confidence

Confidence is not binary.

Knowledge may be:

``` text
Preliminary

Supported

Replicated

Robust

Canonical
```

Confidence reflects evidence quality rather than profitability.

------------------------------------------------------------------------

## 6.8 Knowledge versus strategy

Knowledge describes market behaviour.

Strategies exploit knowledge.

Therefore:

``` text
Knowledge
        ↓
Possible Strategies
```

One knowledge object may support many strategies.

One strategy may depend upon multiple knowledge objects.

------------------------------------------------------------------------

## 6.9 Knowledge repository

Canonical knowledge should be preserved independently from
implementations.

Each knowledge object shall declare:

``` text
knowledge_id
canonical_name
supporting_phenomena
validated_population
evidence_versions
confidence_level
limitations
creation_date
version
status
```

Knowledge becomes a reusable research asset.

------------------------------------------------------------------------

## 6.10 Knowledge evolution

Knowledge is expected to evolve.

Possible transitions include:

``` text
Supported
        ↓
Replicated
        ↓
Canonical
        ↓
Refined
        ↓
Deprecated
```

Evolution is driven by evidence, not by implementation changes.

------------------------------------------------------------------------

## 6.11 Falsifiability

Every knowledge object shall remain falsifiable.

Future evidence may:

-   strengthen,
-   refine,
-   restrict,
-   or invalidate

previous conclusions.

TSIS therefore stores both supporting and contradictory evidence.

------------------------------------------------------------------------

## 6.12 Constitutional rule

Knowledge inside TSIS is never assumed to be permanent.

It is a governed scientific object built from validated phenomena,
continuously re-evaluated as new evidence becomes available.

Scientific knowledge remains subordinate to empirical evidence.
