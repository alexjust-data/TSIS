# mdr_event_state_v1

Status: `candidate_record_v1`

Governed by:

``` text
materialization_decision_contract_v0_3
```

Governance Scope:

``` text
candidate_governance
```

Derived from:

``` text
rjr_event_state_v1_3
```

Prototype reference:

``` text
not_applicable_first_event_state_mdr_lineage
```

------------------------------------------------------------------------

# Purpose

This is the first contract-compliant Materialization Decision Record for
the Canonical Core Representation:

``` text
Event State
```

It belongs to the Governance Phase of TSIS.

Its purpose is to decide how Event State may progress toward physical
representation planning after its Representation Justification Record has
been accepted.

This record does not authorize physical realization, certification,
promotion or downstream consumption.

------------------------------------------------------------------------

# MDR Identity

  Field                 Value
  --------------------- ------------------------------------------
  mdr_id                `mdr_event_state_v1`
  contract_version      `materialization_decision_contract_v0_3`
  created_at            `2026-07-15`
  supersedes_mdr_id     `not_applicable_new_governance_lineage`
  prototype_reference   `not_applicable_first_event_state_mdr_lineage`
  mdr_status            `accepted`

------------------------------------------------------------------------

# Upstream Authority

  Field                          Value
  ------------------------------ ------------------------------------
  canonical_representation_ref   `event_state`
  supporting_rjr                 `rjr_event_state_v1_3`
  rjr_validity                   `true`
  effective_acceptance           `true`
  mdr_authorization              `true_within_candidate_governance`

------------------------------------------------------------------------

# Proposed Materialization Decision

  -------------------------------------------------------------------------------
  Field                                  Value
  -------------------------------------- ----------------------------------------
  proposed_materialization_decision      `candidate_materialization_planning`

  materialization_mode                   `view_first_controlled_candidate_materialization`

  materialization_scope                  `controlled_candidate`

  physical_representation_type           `governed_event_scoped_view_then_dataset_table_candidate`

  stable_artifact_identity               `event_state_table`

  official_physical_status               `contract_defined_not_materialized`

  controlled_candidate_evidence_status   `exists_not_promoted`
  -------------------------------------------------------------------------------

------------------------------------------------------------------------

# Materialization Parameters

  Field                       Value
  --------------------------- --------------------------------------------------
  coverage_denominator        `declared_event_window_scope_only`
  lookback_policy             `market_state_event_state_composition_contract_v0_1 + state_decision_timestamp_policy_v0_1`
  full_universe_claim         `false`
  candidate_planning_status   `planning_authorized`

------------------------------------------------------------------------

# Decision Rationale

Event State should begin as a governed event-scoped representation before
any official materialized table is promoted.

The correct materialization posture is:

``` text
view-first
materialize-when-governed
```

Reason:

-   Event State is organized by governed Event Candidates and Event
    Windows, not by timestamp alone.
-   It must preserve separation from Outcome, Decision, Strategy,
    Reward and Execution.
-   Existing controlled candidates prove feasibility, but do not promote
    an official physical table.
-   The next useful artifact is a canonical-to-physical mapping, not a
    production build.

------------------------------------------------------------------------

# Current Evidence Boundary

The repository documents controlled candidate evidence for Event State:

``` text
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
```

Status:

``` text
controlled_candidate_not_promoted
```

This evidence may support planning and design review.

It shall not be treated as:

-   official `event_state_table_v0_1`;
-   full-universe coverage;
-   ML/RL-ready training state;
-   backtest-core truth;
-   execution truth;
-   promoted institutional dataset.

------------------------------------------------------------------------

# Authority References

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  authority_path                                                                                                                             authority_section                          authority_type    authority_reference_status
  ------------------------------------------------------------------------------------------------------------------------------------------ ------------------------------------------ ----------------- ----------------------------
  `C:\TSIS_Data\00_CTO_1\01_REPRESENTATION_MATERIALIZATION_REVIEW\00_REVISION\rjr_event_state_v1_3.md`                                    `MDR Authorization`                        `primary`         `verified_current`

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\08_Chapter_8_Event_States_TSIS_Event_Research_Architecture.md`     `Event State`                              `primary`         `verified_current`

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\07_Chapter_7_Event_Candidates_TSIS_Event_Research_Architecture.md` `Event Candidates`                         `primary`         `verified_current`

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\03_TSIS_EVENTS\05_Chapter_5_Event_Windows_TSIS_Event_Research_Architecture.md`    `Event Windows`                            `primary`         `verified_current`

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`       `Materialization Policy`                   `primary`         `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`  `event_state_table`                        `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\event_state_table_schema_contract.md`                 `event_state_table_v0_1`                   `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\event_state_table_dataset_contract_v0_1.md`  `dataset contract`                         `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\event_state_table_consumption_policy.md`               `consumption policy`                       `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\event_state_table_registry_entry.yaml`                 `registry entry`                           `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\event_state_table_validators.md`                             `validators`                               `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`          `event_state controlled candidate status`  `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`        `event_state controlled candidate evidence` `supporting`     `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`                         `state builder flow`                       `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md`          `observable eligibility`                   `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md`                `decision timestamp policy`                `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_snapshot_roles_contract_v0_1.md`                  `state roles`                              `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_derived_observables_formula_contract_v0_1.md`     `derived observables`                      `supporting`      `verified_current`
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------


# Consumption Legality Boundary

Event State materialization planning must keep two classifications separate:

```text
state_role
= relation of the row to the event timeline.

consumption_legality
= whether the row may be consumed as predictive/input state.
```

Allowed `consumption_legality` values:

```text
decision_safe
research_only
outcome_adjacent
prohibited_as_input
```

`post_event_review` rows may be valid research Event State rows, but they are not legal X for prediction at the event timestamp.

------------------------------------------------------------------------


# Blocking Preconditions

Physical realization remains blocked until:

1.  `canonical_to_physical_mapping_event_state_v1` exists and is
    approved.
2.  The Event Candidate and Event Window source scope is explicitly
    selected and governed.
3.  The Market State dependency and event-scoped projection rules are
    explicit.
4.  Contract-set review is complete for schema, dataset contract,
    consumption policy, registry entry and validators.
5.  Builder design is approved for view-first reconstruction and any
    controlled candidate materialization.
6.  Validators prove no inline outcomes, labels, rewards, strategy
    fields or execution-truth fields enter Event State.
7.  Raw-to-consumption lineage is complete for Event Candidates, Event
    Windows, Market State dependencies and any microstructure inputs.
8.  Coverage denominator, lookback policy, state roles,
    `consumption_legality` and `decision_timestamp_utc` policy are confirmed.
9.  Controlled candidate evidence is reviewed without promoting it to an
    official dataset.
10. A `physical_realization_authorization_record` is approved.

------------------------------------------------------------------------

# Review

  -----------------------------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -----------------------------------------------------------------------------------
  author                              `TSIS Governance`

  reviewer                            `Codex architectural review`

  review_date                         `2026-07-15`

  decision                            `accepted`

  comments                            `Accepted for planning authorization only. This authorizes canonical-to-physical mapping, schema review, builder design, validator design, lineage planning and registry planning. It does not authorize physical realization.`

  required_changes                    `none`

  required_changes_status             `not_applicable`
  -----------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# MDR Validity

``` text
mdr_validity = true
```

Reason:

-   all mandatory contract fields are present;
-   upstream RJR is valid, effectively accepted and MDR-authorized;
-   authority references are explicit and verified current;
-   current candidate evidence is correctly classified as not promoted;
-   blocking preconditions are documented;
-   review state is explicit;
-   `mdr_status = accepted` is consistent with `decision = accepted`.

------------------------------------------------------------------------

# Planning Authorization

``` text
planning_authorization = true
```

Because:

``` text
formal_review_decision = accepted
```

After formal review, an accepted MDR may authorize only planning:

-   canonical-to-physical mapping;
-   schema review;
-   builder design;
-   validator design;
-   lineage planning;
-   registry planning.

It does not authorize physical realization.

------------------------------------------------------------------------

# Physical Realization Authorization

``` text
physical_realization_authorization = false
```

Because:

-   planning authorization permits planning only and is insufficient for physical realization;
-   canonical-to-physical mapping is not yet approved;
-   blockers remain open;
-   no Physical Realization Authorization Record exists.

------------------------------------------------------------------------

# Authorized Next Artifact

After successful formal review, this MDR may authorize creation of:

``` text
canonical_to_physical_mapping_event_state_v1
```

No physical implementation is authorized by this record.

------------------------------------------------------------------------

# Fundamental Rule

This MDR applies an existing candidate governance contract.

It does not redefine the governance mechanism.

Event State shall remain event-scoped, observable, and separate from
Outcome, Decision, Strategy, Reward and Execution.

No physical realization, certification, promotion or downstream
consumption may begin until later governance artifacts explicitly
authorize those stages.