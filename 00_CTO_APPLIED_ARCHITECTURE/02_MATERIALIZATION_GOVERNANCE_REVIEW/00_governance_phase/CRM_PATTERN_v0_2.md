# CRM_PATTERN_v0_2

Status: `candidate_governance_pattern_v0_2`

## Purpose

This document describes a **candidate governance pattern** being
evaluated within TSIS for introducing, reviewing and authorizing
architectural artifacts.

It is technology-independent and intended for reuse where appropriate.

While this pattern remains in candidate status, it shall not be
interpreted as global institutional law for all TSIS workflows.

Its purpose is to test whether explicit governance evidence improves
architectural decisions.

------------------------------------------------------------------------

```
If a governance artifact does not directly unlock
the next operational artifact,
it should not be created.
```

## Candidate Governance Pattern

The proposed lifecycle is:

``` text
Contract
    |
    v
Record
    |
    v
Formal Review
    |
    v
Decision
    |
    v
Authorization
    |
    v
Next Governance Artifact
```

Each stage has a distinct responsibility.

No stage should replace another.

------------------------------------------------------------------------

## Stage 1 --- Contract

The Contract defines:

-   mandatory fields;
-   rules;
-   validity criteria;
-   consistency rules;
-   consequences;
-   authority boundaries.

The Contract governs Records of the same type once adopted.

While the Contract remains a candidate, its decisions apply only within
candidate governance scope.

------------------------------------------------------------------------

## Stage 2 --- Record

The Record is the concrete instance created under a governing Contract
or prototype workflow.

It captures evidence for one specific proposal.

Examples include:

``` text
representation_justification_record
materialization_decision_record
canonical_to_physical_mapping_record
architectural_traceability_record
```

A Record documents evidence.

It does not create authority by itself.

------------------------------------------------------------------------

## Stage 3 --- Formal Review

The Record is reviewed against its governing Contract or, for
prototypes, against the candidate rules being evaluated.

The review may verify:

-   completeness;
-   consistency;
-   authority references;
-   overlap;
-   traceability;
-   governance compliance.

Possible decisions may include:

``` text
not_reviewed
accepted
accepted_with_changes
rejected
deferred
```

------------------------------------------------------------------------

## Stage 4 --- Decision

The formal decision records the outcome of the review.

A decision applies to the specific Record.

It does not automatically authorize downstream action.

------------------------------------------------------------------------

## Stage 5 --- Authorization

Authorization is computed from:

-   Record validity;
-   review decision;
-   blocking conditions;
-   authority scope.

Authorization determines whether the workflow may proceed.

A valid Record may still have:

``` text
authorization = false
```

Decisions made under candidate contracts authorize progression only
within candidate governance.

------------------------------------------------------------------------

## Stage 6 --- Next Governance Artifact

Successful authorization may permit creation of the next governed
artifact.

For example:

``` text
Representation Justification Contract
        |
        v
Representation Justification Record
        |
        v
Materialization Decision Record
```

The next artifact begins a new governance cycle.

------------------------------------------------------------------------

## Candidate Governance Rule

``` text
Decisions produced under a candidate contract
are candidate governance decisions.
```

They may authorize progression within the candidate workflow.

They shall not be interpreted as:

-   institutional adoption of the governance pattern;
-   promotion of the governing contract;
-   authorization of physical implementation;
-   global applicability across TSIS.

------------------------------------------------------------------------

## Prototype-Derived Contract Rule

A candidate contract should preferably be derived from at least one
reviewed prototype Record.

The intended sequence is:

``` text
Prototype Record
        |
        v
Architectural Review
        |
        v
Stable Prototype
        |
        v
Candidate Contract
```

This rule is itself still under evaluation as part of this candidate
governance pattern.

------------------------------------------------------------------------

## General Candidate Principles

1.  Contracts govern Records.
2.  Records provide evidence.
3.  Reviews evaluate Records.
4.  Decisions record outcomes.
5.  Authorization controls progression.
6.  Every authorization is scoped.
7.  Every stage preserves traceability.
8.  Candidate decisions remain candidate governance decisions.
9.  Engineering should not bypass adopted governance gates.

------------------------------------------------------------------------

## Candidate Reusability

This pattern is currently being tested for:

-   Representation Justification;
-   Materialization Decision;
-   Canonical-to-Physical Mapping;
-   Architectural Traceability.

Future reuse requires separate review.

------------------------------------------------------------------------

## Current Interpretation

The pattern has been validated conceptually through:

``` text
representation_justification_contract_v0_8
rjr_market_state_v0_4
mdr_market_state_v0_4
```

This evidence supports freezing the pattern as a stable candidate.

It does not promote the pattern to institutional status.

------------------------------------------------------------------------

## Fundamental Candidate Rule

Within the current candidate workflow, governance follows:

``` text
Contract
    |
    v
Record
    |
    v
Formal Review
    |
    v
Decision
    |
    v
Authorization
```

This sequence remains subject to future architectural review before any
global TSIS adoption.
