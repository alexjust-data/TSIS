# rjr_market_state_v0_4

Status: `candidate_record_v0_4`

Governed by:

``` text
representation_justification_contract_v0_8
```

## RJR Identity

  Field               Value
  ------------------- ----------------------------------------------
  rjr_id              `rjr_market_state_v0_4`
  contract_version    `representation_justification_contract_v0_8`
  created_at          `2026-07-15`
  supersedes_rjr_id   `rjr_market_state_v0_3`
  rjr_status          `accepted`

## Representation Identity

  Field                    Value
  ------------------------ -----------------------------------
  representation_id        `market_state`
  representation_name      `Market State`
  representation_version   `v0_1`
  artifact_role            `canonical_market_representation`

## Problem Statement

### Problem

TSIS requires a governed representation of the information legally
observable for one instrument at a declared decision timestamp.

Without this representation, research, event analysis, pattern
discovery, machine learning and later decision systems may construct
incompatible private definitions of state, mix future information with
current observables or collapse state into signal, strategy, outcome,
reward or execution.

### Why TSIS requires this representation

Market State provides a common semantic boundary for what was knowable
at a specific time.

It allows TSIS to:

-   construct auditable decision-context rows;
-   enforce temporal legality and observability;
-   separate input state `X` from later outcomes `y`;
-   maintain consistent identity, grain and cutoff rules;
-   support governed downstream research without allowing each consumer
    to redefine state.

The justification is semantic and institutional.

It is not based on the convenience of creating `market_state_table`.

## Existing Alternatives

  ---------------------------------------------------------------------------------
  Existing artifact                 Overlap classification  Why insufficient or
                                                            complementary?
  --------------------------------- ----------------------- -----------------------
  `master_daily_table`              `complementary`         Provides daily
                                                            observables but does
                                                            not define a complete
                                                            decision-time Market
                                                            State or intraday state
                                                            semantics.

  `master_intraday_bar_table`       `complementary`         Provides intraday
                                                            observable bars but is
                                                            an enabling observable
                                                            surface, not canonical
                                                            state.

  `microstructure_features_table`   `complementary`         Provides governed
                                                            derived features for
                                                            selected windows but
                                                            does not define state
                                                            identity, decision
                                                            timestamp or complete
                                                            component composition.

  `event_state`                     `complementary`         Represents Market State
                                                            anchored to an event,
                                                            window and role; it
                                                            depends on Market State
                                                            rather than replacing
                                                            it.

  private strategy feature matrices `strong_duplicate`      May contain state-like
                                                            inputs, but their
                                                            semantics are
                                                            strategy-specific and
                                                            cannot act as
                                                            institutional state
                                                            authority.

  `outcomes_table`                  `none`                  Represents post-event
                                                            labels and outcomes and
                                                            must remain separate
                                                            from state.
  ---------------------------------------------------------------------------------

No unresolved `authority_conflict` has been identified.

## Authority Sources

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Authority path                                                                                                                            Authority section               Relationship to         Authority type Reference status
                                                                                                                                                                            representation                         
  ----------------------------------------------------------------------------------------------------------------------------------------- ------------------------------- ----------------------- -------------- --------------------
  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\09_Chapter_8_State_Layer_TSIS.md`                    `8.6 Market State`              Defines Market State as `primary`      `verified_current`
                                                                                                                                                                            the governed                           
                                                                                                                                                                            representation of                      
                                                                                                                                                                            decision-time market                   
                                                                                                                                                                            knowledge.                             

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\12_Chapter_11_Temporal_Legality_TSIS.md`             `Temporal Legality`             Requires state          `primary`      `verified_current`
                                                                                                                                                                            components to respect                  
                                                                                                                                                                            legal time boundaries.                 

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\13_Chapter_12_Observability_TSIS.md`                 `Observability`                 Defines what            `primary`      `verified_current`
                                                                                                                                                                            information may                        
                                                                                                                                                                            legitimately enter                     
                                                                                                                                                                            state.                                 

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\14_Chapter_13_Causality_TSIS.md`                     `Causality`                     Prevents future-derived `primary`      `verified_current`
                                                                                                                                                                            or causally illegal                    
                                                                                                                                                                            information from                       
                                                                                                                                                                            entering state.                        

  `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`   `Primary key and composition`   Defines the             `supporting`   `verified_current`
                                                                                                                                                                            relationship between                   
                                                                                                                                                                            Market State and Event                 
                                                                                                                                                                            State and the                          
                                                                                                                                                                            implementation-facing                  
                                                                                                                                                                            identity of a state                    
                                                                                                                                                                            row.                                   

  `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`                          `Flujo Correcto`;               Defines the controlled  `supporting`   `verified_current`
                                                                                                                                            `Acceptance Criteria`           engineering path that                  
                                                                                                                                                                            may realize the                        
                                                                                                                                                                            representation after                   
                                                                                                                                                                            governance approval.                   

  `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md`                 `Decision Timestamp Policy`     Defines the             `supporting`   `verified_current`
                                                                                                                                                                            implementation-facing                  
                                                                                                                                                                            timestamp policy for                   
                                                                                                                                                                            state rows.                            

  `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md`           `Observable Eligibility`        Defines which           `supporting`   `verified_current`
                                                                                                                                                                            components may be                      
                                                                                                                                                                            eligible for state                     
                                                                                                                                                                            construction.                          
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Representation Justification

  -----------------------------------------------------------------------
  Category                            Justification
  ----------------------------------- -----------------------------------
  `ontological`                       TSIS requires an explicit entity
                                      representing what the market and
                                      instrument looked like at a
                                      decision point.

  `scientific`                        Reproducible research requires a
                                      common, auditable definition of
                                      information available before
                                      outcomes occur.

  `representation`                    Primitive, bar and feature tables
                                      cannot independently express the
                                      complete semantic, temporal and
                                      compositional boundary of state.

  `governance`                        A canonical state prevents private
                                      strategy-specific state definitions
                                      and enforces separation from
                                      outcomes, rewards and execution.

  `operational`                       Downstream event-state
                                      construction, pattern discovery and
                                      controlled modeling require a
                                      stable state interface.

  `validation`                        A distinct state representation
                                      makes leakage, observability,
                                      cutoff, identity and component
                                      lineage directly testable.
  -----------------------------------------------------------------------

## Representation Scope

### Included concepts

-   instrument identity;
-   declared decision timestamp;
-   state horizon;
-   state schema version;
-   legally observable primitive and derived components;
-   governed market, session, regime, news, fundamental, short and
    microstructure context when eligible;
-   component as-of timestamps;
-   quality, lineage and consumer-gate metadata.

### Excluded concepts

-   future outcomes;
-   labels;
-   rewards;
-   actions;
-   strategy decisions;
-   signals;
-   fills;
-   PnL;
-   policy outputs;
-   future-derived features;
-   event anchoring and event role fields that belong specifically to
    Event State.

### Temporal boundary

Every component shall satisfy:

``` text
component_as_of_utc <= decision_timestamp_utc
```

### Observability boundary

Only components explicitly eligible under state observability and
derived-observable contracts may enter the representation.

Availability in a raw or derived dataset does not automatically make a
component state-eligible.

### Identity

The representation identifies one governed Market State observation.

### Granularity

The implementation-facing canonical grain is:

``` text
instrument_id
+ decision_timestamp_utc
+ state_horizon
+ state_schema_version
```

This grain is aligned with the verified composition contract.

## Intended Consumers

### Allowed consumers

-   `research`
-   `pattern_discovery`
-   `backtesting`
-   `machine_learning`
-   `offline_reinforcement_learning`
-   `governance`
-   `audit`

### Excluded consumers

-   `execution`

### Consumer Restrictions

-   Current controlled candidates are not authorized as institutional
    ML/RL, core-backtest or execution truth.
-   Consumer authorization depends on the physical implementation's
    certification and promotion scope.
-   An accepted RJR does not authorize any physical consumer by itself.
-   Execution use requires a separately promoted low-latency
    implementation and explicit execution policy.

## Non-Goals

Market State is not:

-   a signal;
-   a strategy;
-   a trade recommendation;
-   an action;
-   a reward;
-   an outcome;
-   a label;
-   a fill;
-   an execution policy;
-   a PnL surface;
-   an event definition;
-   a substitute for Event State.

It does not guarantee predictive value.

It does not imply that every eligible component must be physically
materialized.

## Expected Success Criteria

This representation is architecturally successful when:

1.  its semantic meaning remains independent of any physical table or
    storage system;
2.  its identity, grain and decision-time semantics are unambiguous;
3.  state components can be tested for observability, temporal legality
    and lineage;
4.  outcomes, labels, rewards, strategy and execution remain outside the
    representation;
5.  Event State can reference or compose Market State without redefining
    it;
6.  every physical implementation can point back to this canonical
    authority;
7.  controlled candidates cannot be mistaken for promoted institutional
    state;
8.  downstream consumer permissions are explicit and status-dependent.

## Formal Review

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  author                              `TSIS Architecture Review`

  reviewer                            `OpenAI GPT-5.6 Thinking — AI-assisted TSIS architectural review`

  review_date                         `2026-07-15`

  decision                            `accepted`

  comments                            `The representation is independently justified by verified semantic authorities, has clear boundaries, does not depend on the existence of market_state_table, and establishes necessary separation between state, event state, outcomes, strategy, reward and execution. Acceptance applies only to the architectural justification of Market State. It does not promote any physical implementation or candidate dataset.`

  required_changes                    `none`

  required_changes_status             `not_applicable`
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## RJR Validity

``` text
rjr_validity = true
```

## Effective Acceptance

``` text
effective_acceptance = true
```

Because:

``` text
decision = accepted
```

and no blocking authority conflict, unresolved primary authority or
required change remains.

## MDR Authorization

``` text
mdr_authorization = true
```

This authorizes creation of:

``` text
mdr_market_state_v0_1
```

It does not authorize:

-   schema changes;
-   builder execution;
-   physical materialization;
-   candidate promotion;
-   ML/RL consumption;
-   execution use.

## Decision Scope

The accepted decision applies to:

``` text
Canonical Market Representation: Market State
```

It does not apply to:

``` text
market_state_table_v0_1
market_state_table candidates
any particular schema
any particular builder
any physical promotion status
```

Those require subsequent governance and engineering evidence.

## Traceability

Authorized next record:

-   `mdr_market_state_v0_1`

Expected later records:

-   `canonical_to_physical_mapping_market_state_v0_1`
-   `architectural_traceability_market_state_v0_1`

## Fundamental Rule

Market State is accepted as a justified Canonical Market Representation
because TSIS requires a stable, observable and temporally legal
representation of decision-time market knowledge.

No physical implementation is accepted or promoted by this decision.
