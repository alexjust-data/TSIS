# materialization_decision_contract_v0_3

Status: `candidate_contract_v0_3`

## Purpose

This candidate contract governs the rules that every **Materialization
Decision Record (MDR)** shall satisfy before an accepted Canonical
Market Representation may progress through the candidate materialization
workflow.

When formally promoted, this contract becomes institutional policy.
Until then, its decisions apply only within candidate governance.

------------------------------------------------------------------------

## Contract Principle

``` text
Materialization Decision Contract
        |
        v
Materialization Decision Record
        |
        +--> MDR Validity
        |
        v
Formal Review
        |
        +--> Planning Authorization
        |
        +--> Physical Realization Authorization
        |
        v
Next Governance Artifact
```

Planning authorization and Physical Realization Authorization are
independent decisions.

------------------------------------------------------------------------

## Mandatory MDR Fields

### 1. MDR Identity

Required:

-   mdr_id
-   contract_version
-   created_at
-   supersedes_mdr_id
-   mdr_status

### 2. Upstream Authority

Required:

-   canonical_representation_ref
-   supporting_rjr
-   rjr_validity
-   effective_acceptance
-   mdr_authorization

### 3. Proposed Materialization Decision

Required:

-   materialization_mode
-   materialization_scope
-   physical_representation_type
-   stable_artifact_identity
-   official_physical_status
-   controlled_candidate_evidence_status

### 4. Materialization Parameters

Required:

-   coverage_denominator
-   lookback_policy
-   full_universe_claim
-   candidate_planning_status

### 5. Authority References

Each reference shall include:

-   authority_path
-   authority_section
-   authority_type
-   authority_reference_status

### 6. Blocking Preconditions

Every blocker preventing physical realization shall be explicitly
recorded.

### 7. Review

Required:

-   author
-   reviewer
-   review_date
-   decision
-   comments
-   required_changes
-   required_changes_status

Allowed decisions:

-   not_reviewed
-   accepted
-   accepted_with_changes
-   rejected
-   deferred

If decision = not_reviewed:

-   reviewer = pending
-   review_date = pending

are permitted.

If decision != not_reviewed:

-   reviewer and review_date shall be concrete.

------------------------------------------------------------------------

## MDR Status and Decision Consistency

Valid combinations:

  mdr_status              allowed decision
  ----------------------- --------------------------
  draft                   not_reviewed
  under_review            not_reviewed
  accepted                accepted
  accepted_with_changes   accepted_with_changes
  rejected                rejected
  deferred                deferred
  superseded              prior decision preserved
  retired                 prior decision preserved

An MDR shall update `mdr_status` to reflect the formal review decision.

------------------------------------------------------------------------

## MDR Validity

An MDR is valid when:

-   mandatory fields are complete;
-   upstream RJR is valid;
-   authority references are explicit;
-   blockers are documented;
-   review state is explicit;
-   mdr_status and decision are consistent.

Validity preserves institutional evidence.

Validity does not authorize planning or realization.

------------------------------------------------------------------------

## Planning Authorization

Planning Authorization answers:

``` text
May TSIS begin candidate materialization planning?
```

It shall be computed as:

``` text
planning_authorization =
    mdr_validity = true
    AND (
        formal_review_decision = accepted
        OR (
            formal_review_decision = accepted_with_changes
            AND required_changes_status = closed
        )
    )
```

Planning Authorization permits only:

-   contract review;
-   schema review;
-   builder design;
-   validator design;
-   lineage planning;
-   registry planning.

It never permits physical realization.

------------------------------------------------------------------------

## Physical Realization Authorization

Physical Realization Authorization answers:

``` text
May TSIS begin physical realization?
```

It requires:

-   planning_authorization = true
-   canonical_to_physical_mapping approved
-   all blocking preconditions resolved
-   contract-set complete
-   approved `physical_realization_authorization_record`

Planning Authorization alone is insufficient.

------------------------------------------------------------------------

## Relationship With Prototype MDRs

Prototype MDRs may omit contract_version or use prototype-specific
fields while this contract remains in candidate status.

Once adopted, conforming MDRs shall use this contract's field names.

------------------------------------------------------------------------

## Relationship With Other Contracts

This contract follows:

``` text
representation_justification_contract
```

and precedes:

``` text
physical realization
certification
promotion
```

It does not replace schema, dataset, builder or validator contracts.

------------------------------------------------------------------------

## Fundamental Rule

An accepted Canonical Market Representation does not automatically
authorize physical realization.

Every proposed Physical Representation shall first pass through a
Materialization Decision Record compliant with this contract.

Planning Authorization shall never be interpreted as Physical
Realization Authorization.
