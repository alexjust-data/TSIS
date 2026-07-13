# TSIS Phenomenon Discovery

## Chapter 3 --- Hypothesis Formation

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 3. Hypothesis Formation

## 3.1 Purpose

Research questions identify what deserves investigation.

Hypotheses propose one possible explanation for the observed evidence.

TSIS treats every hypothesis as a scientific object subject to
validation rather than as an assumption to be accepted.

------------------------------------------------------------------------

## 3.2 Fundamental Principle

A hypothesis is **not knowledge**.

A hypothesis is a falsifiable explanation of recurring observable market
behaviour.

Knowledge begins only after repeated empirical validation.

------------------------------------------------------------------------

## 3.3 Scientific sequence

``` text
Market States
        ↓
Research Question
        ↓
Hypothesis
        ↓
Evidence Collection
        ↓
Validation
        ↓
Phenomenon
        ↓
Knowledge
```

------------------------------------------------------------------------

## 3.4 Characteristics of a valid hypothesis

Every hypothesis shall be:

-   observable,
-   falsifiable,
-   measurable,
-   temporally legal,
-   population-specific,
-   reproducible.

Example:

``` text
Increasing signed buying pressure
preceded by spread compression
is associated with a higher probability
of sustained price discovery.
```

------------------------------------------------------------------------

## 3.5 Hypothesis components

Each hypothesis shall define:

``` text
Research Population

Observable Variables

Representations Used

Control Population

Expected Behaviour

Validation Criteria

Acceptance Criteria

Rejection Criteria
```

------------------------------------------------------------------------

## 3.6 Null hypothesis

Every research hypothesis shall explicitly define its null hypothesis.

Example:

``` text
H0

Trade acceleration and liquidity vacuum
are statistically independent.
```

Alternative:

``` text
H1

Trade acceleration systematically
precedes liquidity vacuum.
```

------------------------------------------------------------------------

## 3.7 Competing hypotheses

TSIS encourages multiple competing explanations.

Example:

``` text
H1
Liquidity vacuum.

H2
Spread compression only.

H3
Microprice displacement.

H4
Combined interaction.
```

Evidence decides.

Architecture remains neutral.

------------------------------------------------------------------------

## 3.8 Population dependency

A hypothesis is always conditional upon its declared research
population.

A validated hypothesis for:

``` text
Halt Events
```

does not automatically generalize to:

``` text
Scanner Candidates
```

Population transfer requires separate validation.

------------------------------------------------------------------------

## 3.9 Hypothesis metadata

Every hypothesis shall declare:

``` text
hypothesis_id
question_id
population_id
state_version
representation_versions
feature_registry_version
creation_date
author
status
```

Status examples:

``` text
Draft
Under Investigation
Rejected
Supported
Validated
Deprecated
```

------------------------------------------------------------------------

## 3.10 Rejected hypotheses

Rejected hypotheses remain part of institutional knowledge.

Negative evidence reduces future search space and improves scientific
efficiency.

TSIS therefore preserves rejected hypotheses with complete provenance.

------------------------------------------------------------------------

## 3.11 Constitutional rule

Hypotheses are scientific proposals rather than architectural truths.

No hypothesis may become a canonical market phenomenon until supported
by reproducible empirical evidence across its declared research
population.
