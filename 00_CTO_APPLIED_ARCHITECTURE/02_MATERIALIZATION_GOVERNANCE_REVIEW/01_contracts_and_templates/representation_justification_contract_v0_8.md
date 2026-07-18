# representation_justification_contract_v0_8

Status: `candidate_contract_v0_8`

## Purpose

This contract governs the institutional rules that every
**Representation Justification Record (RJR)** shall satisfy before a
proposed **Canonical Market Representation** or **Enabling Institutional
Artifact** may proceed to the next stage of the TSIS materialization
workflow.

The contract is approved once as institutional policy.

A **Representation Justification Record** is the concrete institutional
instance created for one proposed representation or artifact.

This contract distinguishes:

``` text
RJR validity
```

from:

``` text
MDR authorization
```

A valid RJR may preserve a pending, accepted, rejected or deferred
institutional decision.

Only a valid and effectively accepted RJR may authorize creation of a:

``` text
Materialization Decision Record (MDR)
```

This contract does not authorize schema creation, builder
implementation, validator implementation, physical realization,
certification or promotion.

------------------------------------------------------------------------

## Contract Principle

``` text
Representation Justification Contract
        |
        v
Representation Justification Record
        |
        +--> RJR Validity
        |
        v
Formal Review Decision
        |
        +--> Effective Acceptance
        |
        v
MDR Authorization
```

A valid record preserves institutional history.

A positive and effective decision authorizes progression.

These are different conditions.

------------------------------------------------------------------------

## Scope

This contract governs RJRs for proposals involving:

-   Canonical Market Representations;
-   Enabling Institutional Artifacts;
-   Feature Surfaces;
-   State Surfaces;
-   Outcome Surfaces;
-   Research Views;
-   Future Physical Representations.

------------------------------------------------------------------------

## Mandatory RJR Fields

### 1. RJR Identity

Required:

-   `rjr_id`
-   `contract_version`
-   `created_at`
-   `supersedes_rjr_id`
-   `rjr_status`

Allowed values for `rjr_status`:

-   `draft`
-   `under_review`
-   `accepted`
-   `accepted_with_changes`
-   `rejected`
-   `deferred`
-   `superseded`
-   `retired`

Rules:

-   `rjr_id` shall uniquely identify the record.
-   `contract_version` shall identify the exact governing contract.
-   `created_at` shall use an explicit timestamp.
-   `supersedes_rjr_id` shall be null only when no prior RJR exists.
-   `rjr_status` describes the lifecycle state of the RJR.
-   `rjr_status` does not replace the formal review decision.

### 2. Representation Identity

Required:

-   `representation_id`
-   `representation_name`
-   `representation_version`
-   `artifact_role`

Allowed values for `artifact_role`:

-   `canonical_market_representation`
-   `enabling_institutional_artifact`
-   `feature_surface`
-   `state_surface`
-   `outcome_surface`
-   `research_view`
-   `other`

### 3. Problem Statement

The RJR shall answer:

> What architectural, scientific, ontological, governance, operational
> or validation problem does this representation solve?

Technical convenience alone is not a valid justification.

### 4. Existing Alternatives

The RJR shall identify existing representations, artifacts, contracts,
datasets, views or registries serving a similar purpose.

Allowed overlap values:

-   `none`
-   `complementary`
-   `partial_duplicate`
-   `strong_duplicate`
-   `authority_conflict`

An unresolved `authority_conflict` blocks MDR authorization.

It does not prevent the RJR from being preserved as a valid
institutional record when the conflict is documented.

### 5. Authority Source

Every authority reference shall include:

-   `authority_path`
-   `authority_section`
-   `relationship_to_representation`
-   `authority_type`
-   `authority_reference_status`

Allowed `authority_type` values:

-   `primary`
-   `supporting`

Allowed `authority_reference_status` values:

-   `verified_current`
-   `missing`
-   `stale`
-   `moved`
-   `unverified`

Rules:

-   `authority_path` shall exist in the repository at review time or be
    explicitly marked otherwise.
-   General document names are insufficient.
-   Exact sections shall be cited whenever available.
-   The relationship between the authority and the proposed
    representation shall be explicit.
-   Missing or stale authority references may remain in a valid RJR, but
    unresolved primary-authority problems block MDR authorization.

### 6. Representation Justification

At least one category is mandatory:

-   `ontological`
-   `scientific`
-   `representation`
-   `governance`
-   `operational`
-   `validation`

Each selected category shall include a concise explanation.

### 7. Representation Scope

Required:

-   `included_concepts`
-   `excluded_concepts`
-   `temporal_boundary`
-   `observability_boundary`
-   `identity`
-   `granularity`

### 8. Intended Consumers

Required:

-   `allowed_consumers`
-   `excluded_consumers`
-   `consumer_restrictions`

Allowed consumer values:

-   `research`
-   `pattern_discovery`
-   `backtesting`
-   `machine_learning`
-   `offline_reinforcement_learning`
-   `execution`
-   `governance`
-   `audit`
-   `other`

### 9. Non-Goals

The RJR shall explicitly identify what the representation is not
intended to represent or enable.

### 10. Expected Success Criteria

Success criteria shall be objective and verifiable.

Performance alone is insufficient.

### 11. Review

Required fields:

-   `author`
-   `reviewer`
-   `review_date`
-   `decision`
-   `comments`
-   `required_changes`
-   `required_changes_status`

Allowed values for `decision`:

-   `not_reviewed`
-   `accepted`
-   `accepted_with_changes`
-   `rejected`
-   `deferred`

Allowed values for `required_changes_status`:

-   `not_applicable`
-   `open`
-   `partially_closed`
-   `closed`

------------------------------------------------------------------------

## Conditional Review Field Rules

### When `decision = not_reviewed`

Permitted:

``` text
reviewer = pending
review_date = pending
required_changes_status = open
```

or:

``` text
required_changes_status = not_applicable
```

The RJR may remain institutionally valid as a pending-review record.

MDR authorization remains false.

### When `decision != not_reviewed`

Mandatory:

-   `reviewer` identifies a concrete reviewer or reviewing authority;
-   `review_date` contains a concrete date or timestamp;
-   `comments` records the rationale;
-   `required_changes_status` is consistent with the decision.

------------------------------------------------------------------------

## RJR Status and Decision Consistency

The following combinations are valid:

  rjr_status                allowed decision
  ------------------------- --------------------------
  `draft`                   `not_reviewed`
  `under_review`            `not_reviewed`
  `accepted`                `accepted`
  `accepted_with_changes`   `accepted_with_changes`
  `rejected`                `rejected`
  `deferred`                `deferred`
  `superseded`              prior decision preserved
  `retired`                 prior decision preserved

A deferred formal decision shall always result in:

``` text
rjr_status = deferred
decision = deferred
```

A record shall update `rjr_status` to match the formal decision.

------------------------------------------------------------------------

## RJR Validity Criteria

An RJR is institutionally valid when:

-   every mandatory field is completed or explicitly marked
    `not_applicable` or conditionally permitted as `pending`;
-   the RJR has a unique institutional identity;
-   the governing contract version is recorded;
-   authority references are present and their status is explicit;
-   overlap is classified;
-   scope and non-goals are explicit;
-   intended and excluded consumers are declared;
-   success criteria are objective;
-   the review state is explicitly recorded;
-   `rjr_status` and `decision` are consistent;
-   unresolved conflicts, missing authorities and required changes are
    transparently recorded.

RJR validity means:

``` text
the record is complete enough to preserve institutional evidence
```

RJR validity does not mean:

``` text
the proposal is accepted
```

------------------------------------------------------------------------

## Effective Acceptance Rule

Effective acceptance shall be computed as:

``` text
effective_acceptance =
    decision = accepted
    OR
    (
        decision = accepted_with_changes
        AND required_changes_status = closed
    )
```

------------------------------------------------------------------------

## MDR Authorization Criteria

Creation of a Materialization Decision Record is authorized only when:

``` text
rjr_validity = true
AND
effective_acceptance = true
```

MDR authorization is false if:

-   an unresolved `authority_conflict` exists;
-   a primary authority reference remains unresolved as `missing`,
    `stale`, `moved` or `unverified`;
-   required changes remain `open` or `partially_closed`;
-   any mandatory governance field is absent;
-   `rjr_status` and `decision` are inconsistent;
-   the decision is `not_reviewed`, `rejected` or `deferred`.

------------------------------------------------------------------------

## Invalid Justifications

The following are invalid:

-   "We need another table."
-   "Implementation becomes easier."
-   "The query is faster."
-   "The ML model expects this layout."
-   "Another project uses it."
-   "The code already exists."
-   "The data is available."
-   "The proposed table will justify the representation."

Circular justification is prohibited.

------------------------------------------------------------------------

## Decision Consequences

### not_reviewed

The RJR may be valid as a draft or under-review record.

MDR authorization is false.

### accepted

The RJR may authorize an MDR if all other authorization criteria are
satisfied.

### accepted_with_changes

The RJR may be valid, but MDR authorization remains false until required
changes are closed.

### rejected

The RJR remains a valid institutional record of a negative decision.

MDR authorization is false.

### deferred

The RJR remains a valid institutional record of a deferred decision.

Its lifecycle status shall be `deferred`.

MDR authorization is false until a later governed review creates or
supersedes the deferred decision.

------------------------------------------------------------------------

## Relationship With Other Authorities

Semantic authority remains in the Epistemological Architecture and
Market Representation Architecture.

This contract governs only the Representation Justification workflow.

------------------------------------------------------------------------

## Fundamental Rule

A rejected, deferred, draft or pending-review RJR may still be a valid
institutional record.

Only a valid and effectively accepted RJR may authorize a
Materialization Decision Record.

Representation justification always precedes materialization and
implementation.
