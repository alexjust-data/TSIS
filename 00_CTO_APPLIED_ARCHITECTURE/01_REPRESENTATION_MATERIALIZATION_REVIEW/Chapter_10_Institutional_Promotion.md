# Chapter 10 --- Institutional Promotion

## Objective

Certification demonstrates that a Physical Representation satisfies the
institutional requirements defined by TSIS.

Promotion is a different decision.

The purpose of this chapter is to define how TSIS formally recognizes a
certified Physical Representation as an institutional asset that may be
consumed according to its declared scope.

Promotion is therefore an architectural governance decision.

It is not an engineering operation.

------------------------------------------------------------------------

## Promotion Philosophy

A Physical Representation does not become institutional because it
exists.

It does not become institutional because it performs well.

It does not become institutional because it has been successfully built.

Institutional status is granted only after an explicit promotion
decision supported by certification evidence.

Promotion establishes trust.

It does not create correctness.

Correctness must already have been demonstrated during certification.

------------------------------------------------------------------------

## Promotion Authority

Promotion shall be performed under the governance rules of TSIS.

The promotion decision shall be explicit, documented and reproducible.

Institutional status shall never be inferred from:

-   the existence of a dataset;
-   a successful build;
-   a passing unit test;
-   downstream adoption;
-   historical usage.

Institutional status exists only when explicitly declared.

------------------------------------------------------------------------

## Promotion Inputs

Promotion evaluates evidence produced by previous stages.

Typical inputs include:

-   Canonical Market Representation;
-   Physical Representation;
-   Institutional Contracts;
-   Certification Report;
-   Validation Results;
-   Lineage Information;
-   Registry Entries;
-   Consumer Policies.

Promotion does not recreate this evidence.

It evaluates it.

------------------------------------------------------------------------

## Institutional Status

Every Physical Representation shall declare one institutional status.

Typical statuses include:

``` text
Conceptual

Approved for Materialization

Candidate

Controlled Candidate

Institutional

Deprecated

Superseded

Retired
```

Only institutional implementations may be treated as official
architectural assets within their declared consumer scope.

------------------------------------------------------------------------

## Scope of Promotion

Promotion is always scoped.

Institutional approval does not automatically authorize every possible
use.

A representation may be promoted for:

``` text
Research

Pattern Discovery

Backtesting

Machine Learning

Offline Reinforcement Learning

Execution

Governance

Audit
```

Different consumer domains may require different promotion decisions.

------------------------------------------------------------------------

## Promotion Record

Every promotion decision should produce an institutional record
containing:

-   implementation identity;
-   canonical representation;
-   promoted scope;
-   promotion status;
-   approving authority;
-   decision timestamp;
-   supporting certification reference;
-   applicable restrictions.

This record becomes part of the permanent institutional history of the
implementation.

------------------------------------------------------------------------

## Relationship with Future Changes

Promotion is not permanent.

Subsequent events may require:

-   restriction;
-   suspension;
-   deprecation;
-   replacement;
-   retirement.

Changing institutional status never changes the meaning of the Canonical
Market Representation.

It only changes the institutional trust granted to one implementation.

------------------------------------------------------------------------

## Fundamental Rule

Certification answers:

``` text
Is this implementation correct?
```

Promotion answers:

``` text
May TSIS trust this implementation as an institutional asset?
```

These questions are related.

They are never equivalent.
