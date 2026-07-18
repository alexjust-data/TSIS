# rjr_event_state_v1_3

Status: `candidate_record_v1_3`

Governed by:

``` text
representation_justification_contract_v0_8
```

Governance Scope:

``` text
candidate_governance
```

Derived from:

``` text
01_questions.md
```

## Purpose

This Representation Justification Record (RJR) justifies the Canonical
Core Representation:

``` text
Event State
```

It justifies the representation itself and **does not** justify any
physical implementation.

------------------------------------------------------------------------

## RJR Identity

  Field               Value
  ------------------- ----------------------------------------------
  rjr_id              `rjr_event_state_v1_3`
  contract_version    `representation_justification_contract_v0_8`
  created_at          `2026-07-15`
  supersedes_rjr_id   `rjr_event_state_v1_2`
  rjr_status          `draft`

------------------------------------------------------------------------

## Representation Identity

  Field                    Value
  ------------------------ -----------------------------------
  representation_id        `event_state`
  representation_name      `Event State`
  representation_version   `v1`
  artifact_role            `canonical_market_representation`

------------------------------------------------------------------------

## Problem Statement

Market State describes the market at a timestamp.

Event State describes the observable market **relative to a governed
Event Candidate and Event Window**.

TSIS requires this representation to organize observable market context
around events without mixing strategy, decisions or future outcomes.

------------------------------------------------------------------------

## Existing Alternatives

  -----------------------------------------------------------------------
  Existing Artifact       Overlap                 Why insufficient?
  ----------------------- ----------------------- -----------------------
  `Market State`          complementary           Snapshot only; not
                                                  event-relative.

  `Event Candidate`       complementary           Detects an event but
                                                  does not represent
                                                  observable state.

  `Outcome`               none                    Represents future
                                                  results, not observable
                                                  context.

  Strategy-specific event strong_duplicate        Private semantics; not
  features                                        governed.
  -----------------------------------------------------------------------

No unresolved `authority_conflict` identified.

------------------------------------------------------------------------

## Authority Sources

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  authority_path                                                                                                                             authority_section     relationship_to_representation   authority_type   authority_reference_status
  ------------------------------------------------------------------------------------------------------------------------------------------ --------------------- -------------------------------- ---------------- ----------------------------
  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\08_Chapter_8_Event_States_TSIS_Event_Research_Architecture.md`       `Event State`         Defines canonical Event State    primary          verified_current
                                                                                                                                                                   semantics.                                        

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\07_Chapter_7_Event_Candidates_TSIS_Event_Research_Architecture.md`   `Event Candidates`    Event State consumes governed    primary          verified_current
                                                                                                                                                                   Event Candidates.                                 

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\05_Chapter_5_Event_Windows_TSIS_Event_Research_Architecture.md`      `Event Windows`       Event State is organized around  primary          verified_current
                                                                                                                                                                   governed Event Windows.                           

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\12_Chapter_11_Temporal_Legality_TSIS.md`              `Temporal Legality`   Governs legal observation        primary          verified_current
                                                                                                                                                                   boundaries.                                       

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\13_Chapter_12_Observability_TSIS.md`                  `Observability`       Governs observable information.  primary          verified_current

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\14_Chapter_13_Causality_TSIS.md`                      `Causality`           Separates observable state from  primary          verified_current
                                                                                                                                                                   future outcomes.                                  
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Representation Justification

  -----------------------------------------------------------------------
  Category                            Justification
  ----------------------------------- -----------------------------------
  ontological                         Event-relative state is a distinct
                                      knowledge object.

  scientific                          Enables reproducible comparison of
                                      event families.

  representation                      Cannot be reduced to Market State
                                      without losing semantic identity.

  governance                          Separates Event, Event State,
                                      Decision and Outcome.

  operational                         Provides a reusable input for
                                      research and models.

  validation                          Enables event-specific temporal
                                      legality, observability and leakage
                                      validation.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Representation Scope

### Included Concepts

-   governed Event Candidate
-   governed Event Window
-   observable Market State relative to the event

### Excluded Concepts

-   Strategy
-   Decision
-   Outcome
-   Reward
-   Execution

### Temporal Boundary

Only information legally observable inside the governed Event Window.

### Observability Boundary

Only components eligible under Event State observability rules may enter
the representation.

### Identity

One governed Event State observation for one governed Event occurrence.

### Granularity

``` text
event_window_id
+ decision_timestamp_utc
+ state_role
+ state_schema_version
```

This is aligned with the current Event State composition/schema
contracts.

------------------------------------------------------------------------

## Event Responsibility

Event State **does not create, detect or validate events**.

It consumes already-governed:

-   Event Candidates
-   Event Windows

and organizes observable market information around them.

------------------------------------------------------------------------

## Intended Consumers

### Allowed

-   research
-   pattern_discovery
-   backtesting
-   machine_learning
-   offline_reinforcement_learning
-   governance
-   audit

### Excluded

-   execution

### Consumer Restrictions

This RJR authorizes neither materialization, certification, promotion
nor downstream execution.

------------------------------------------------------------------------

## Non-Goals

Event State is not:

-   Event detection
-   Strategy
-   Trade signal
-   Outcome
-   Reward
-   Execution policy

------------------------------------------------------------------------

## Expected Success Criteria

-   Event State remains distinct from Market State.
-   Outcome remains separated.
-   Event-relative observability is preserved.
-   Event families become comparable.
-   Downstream systems consume one governed representation.

------------------------------------------------------------------------

## Review

  -------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -------------------------------------------------------------
  author                              `TSIS Governance`

  reviewer                            `Codex architectural review`

  review_date                         `2026-07-15`

  decision                            `accepted`

  required_changes                    `none`

  required_changes_status             `not_applicable`

  comments                            `Accepted after minimal architectural review. Event State consumes governed Event Candidates and Event Windows, does not create events, does not contain outcomes, and aligns with state_schema_version granularity.`
  -------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## RJR Validity

``` text
rjr_validity = true
```

Reason:

All mandatory contract fields are present. Formal architectural review is complete and accepted.

------------------------------------------------------------------------

## Effective Acceptance

``` text
effective_acceptance = true
```

Reason:

``` text
decision = accepted
required_changes_status = not_applicable
```

------------------------------------------------------------------------

## MDR Authorization

``` text
mdr_authorization = true
```

------------------------------------------------------------------------

## Fundamental Rule

Event State is justified because it represents the observable market
relative to a governed event.

It consumes governed Event Candidates and Event Windows.

It neither creates events nor represents strategies, decisions or
outcomes.
