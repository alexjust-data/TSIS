# TSIS Phenomenon Discovery

## Chapter 12 --- Research Lifecycle

Version: 1.0 (Draft)

------------------------------------------------------------------------

# 12. Research Lifecycle

## 12.1 Purpose

This chapter defines the complete lifecycle of scientific research
inside TSIS.

Research is treated as a governed engineering process rather than an
ad-hoc exploratory activity.

Every research project progresses through explicit stages with complete
lineage, reproducibility and version control.

------------------------------------------------------------------------

## 12.2 Fundamental Principle

Research is never a single experiment.

Research is a lifecycle.

``` text
Question
    ↓
Protocol
    ↓
Hypothesis
    ↓
Evidence
    ↓
Validation
    ↓
Knowledge
    ↓
Strategy
    ↓
Monitoring
    ↓
Revision
```

No stage may be skipped.

------------------------------------------------------------------------

## 12.3 Stage 1 --- Research Question

Every project begins with a clearly defined scientific question.

The question determines:

-   scope,
-   population,
-   representations,
-   observable variables,
-   evaluation protocol.

No implementation begins before the question exists.

------------------------------------------------------------------------

## 12.4 Stage 2 --- Research Protocol

Before collecting evidence, TSIS freezes the protocol.

The protocol specifies:

``` text
Population
Control Population
State Version
Feature Registry Version
Validation Procedure
Acceptance Criteria
Stopping Criteria
```

The protocol prevents retrospective optimisation.

------------------------------------------------------------------------

## 12.5 Stage 3 --- Hypothesis

One or more falsifiable hypotheses are defined.

Competing hypotheses are encouraged.

All hypotheses remain provisional until validated.

------------------------------------------------------------------------

## 12.6 Stage 4 --- Evidence Collection

Evidence is gathered using governed populations.

Every evidence set records:

-   eligibility,
-   sampling,
-   quality,
-   coverage,
-   provenance.

Evidence remains immutable.

------------------------------------------------------------------------

## 12.7 Stage 5 --- Validation

Evidence is analysed according to the predefined protocol.

Possible outcomes:

``` text
Supported

Rejected

Inconclusive

Requires More Evidence
```

Validation evaluates hypotheses, not profitability.

------------------------------------------------------------------------

## 12.8 Stage 6 --- Knowledge Formation

Validated phenomena become structured knowledge.

Knowledge records:

-   scope,
-   limitations,
-   supporting evidence,
-   confidence,
-   lineage.

Knowledge remains conditional.

------------------------------------------------------------------------

## 12.9 Stage 7 --- Strategy Translation

Knowledge may generate one or more strategy hypotheses.

This transition belongs to engineering.

Scientific knowledge remains independent.

------------------------------------------------------------------------

## 12.10 Stage 8 --- Operational Monitoring

Once deployed, knowledge continues to be monitored.

Typical monitoring includes:

``` text
Regime Drift
Population Drift
Representation Drift
Knowledge Stability
Contradictory Evidence
```

Monitoring may trigger revalidation.

------------------------------------------------------------------------

## 12.11 Stage 9 --- Revision

Knowledge evolves through new evidence.

Possible revisions:

``` text
Extension
Restriction
Refinement
Deprecation
Replacement
```

Historical versions remain reproducible.

------------------------------------------------------------------------

## 12.12 Lifecycle metadata

Every research project shall expose:

``` text
research_id
protocol_version
question_id
hypothesis_ids
evidence_sets
knowledge_outputs
current_stage
status
owner
creation_date
last_review_date
```

------------------------------------------------------------------------

## 12.13 Constitutional rule

Every canonical knowledge object inside TSIS shall be traceable to a
complete research lifecycle.

Knowledge without a documented lifecycle shall never become
institutional knowledge.
