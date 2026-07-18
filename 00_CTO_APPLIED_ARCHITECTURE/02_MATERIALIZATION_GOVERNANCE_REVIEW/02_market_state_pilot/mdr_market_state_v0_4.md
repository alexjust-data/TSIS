# mdr_market_state_v0_4

Status: `candidate_prototype_record_v0_4`

Role:

``` text
Prototype record used to derive materialization_decision_contract_v0_1
```

Authorized within candidate governance by:

``` text
representation_justification_contract_v0_8
rjr_market_state_v0_4
```

------------------------------------------------------------------------

# Purpose

This Materialization Decision Record (MDR) prototype captures a
**candidate governance decision** concerning whether the accepted
Canonical Market Representation **Market State** may enter the candidate
materialization workflow.

This record is not an institutional authority for physical realization.

It exists to:

-   document the candidate materialization decision;
-   expose the fields required by a future Materialization Decision
    Contract;
-   establish planning constraints;
-   define blockers;
-   preserve traceability from canonical representation to proposed
    physical realization.

It does **not** authorize:

-   schema creation;
-   builder execution;
-   validator execution;
-   parquet generation;
-   registry registration;
-   certification;
-   promotion;
-   downstream consumption.

------------------------------------------------------------------------

# MDR Identity

  Field               Value
  ------------------- -----------------------------------
  mdr_id              `mdr_market_state_v0_4`
  created_at          `2026-07-15`
  record_status       `candidate_prototype_record_v0_4`
  supersedes_mdr_id   `mdr_market_state_v0_3`
  governance_scope    `candidate_governance_only`

------------------------------------------------------------------------

# Upstream Authorization

  Field                              Value
  ---------------------------------- ------------------------------------
  canonical_representation           `Market State`
  canonical_representation_version   `v0_1`
  supporting_rjr                     `rjr_market_state_v0_4`
  rjr_validity                       `true`
  effective_acceptance               `true`
  mdr_authorization                  `true_within_candidate_governance`

The upstream RJR authorizes creation of this candidate MDR prototype.

It does not promote the MDR workflow or any physical representation to
institutional status.

------------------------------------------------------------------------

# Candidate Materialization Decision

## Decision

``` text
candidate_materialization_planning_approved
```

## Meaning

The Canonical Market Representation **Market State** may proceed into
candidate materialization planning.

This decision authorizes:

-   planning;
-   crosswalk design;
-   contract-set verification;
-   schema review;
-   builder design review;
-   validator design review;
-   lineage planning;
-   registry planning;
-   blocker analysis.

This decision does not authorize physical realization.

------------------------------------------------------------------------

# Proposed Physical Identity

  Field                                  Value
  -------------------------------------- -------------------------------------
  stable_artifact_identity               `market_state_table`
  table_slot                             `016_market_state_table`
  physical_representation_type           `dataset_table`
  canonical_representation_ref           `market_state`
  official_physical_status               `contract_defined_not_materialized`
  controlled_candidate_evidence_status   `exists_not_promoted`

The term `candidate` is a status.

It is not part of the stable physical artifact identity.

Therefore:

``` text
market_state_table
```

is the stable physical artifact identity.

The current state must be interpreted through two separate dimensions:

``` text
official_physical_status = contract_defined_not_materialized
```

and:

``` text
controlled_candidate_evidence_status = exists_not_promoted
```

This means:

-   the official physical representation is not materialized or
    promoted;
-   controlled candidate implementations and test evidence already
    exist;
-   candidate evidence shall not be mistaken for the official physical
    representation.

------------------------------------------------------------------------

# Materialization Parameters

  -----------------------------------------------------------------------------------------------------
  Field                                  Value
  -------------------------------------- --------------------------------------------------------------
  materialization_mode                   `candidate_controlled_materialization`

  materialization_scope                  `controlled_candidate`

  coverage_denominator                   `declared_coverage_only`

  full_universe_claim                    `false`

  lookback_policy                        `governed_by_market_state_coverage_and_lookback_policy_v0_1`

  candidate_planning_status              `approved`

  official_physical_status               `contract_defined_not_materialized`

  controlled_candidate_evidence_status   `exists_not_promoted`

  production_status                      `not_authorized`

  execution_status                       `not_authorized`
  -----------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Authority References

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Authority Path                                                                                                                             Version / Section    Evidence State             Relationship
  ------------------------------------------------------------------------------------------------------------------------------------------ -------------------- -------------------------- -----------------------
  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\09_Chapter_8_State_Layer_TSIS.md`                     `8.6 Market State`   `verified_current_state`   Defines the canonical
                                                                                                                                                                                             representation to be
                                                                                                                                                                                             materialized.

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`         Materialization      `verified_current_state`   Governs the distinction
                                                                                                                                             policy and permitted                            between semantic
                                                                                                                                             modes                                           existence and physical
                                                                                                                                                                                             materialization.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`    `v0_1`; primary key  `documented_target`        Defines the
                                                                                                                                             and composition                                 implementation-facing
                                                                                                                                                                                             composition and
                                                                                                                                                                                             identity of Market
                                                                                                                                                                                             State.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md`        `v0_1`; coverage,    `documented_target`        Governs scope,
                                                                                                                                             lookback and                                    denominator, lookback
                                                                                                                                             promotion gates                                 and promotion
                                                                                                                                                                                             restrictions.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`                           `v0_1`; flow,        `documented_target`        Governs future
                                                                                                                                             manifest and                                    controlled realization
                                                                                                                                             acceptance criteria                             once authorization
                                                                                                                                                                                             exists.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md`            `v0_1`               `documented_target`        Governs component
                                                                                                                                                                                             eligibility for Market
                                                                                                                                                                                             State.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md`                  `v0_1`               `documented_target`        Governs decision-time
                                                                                                                                                                                             legality.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_snapshot_roles_contract_v0_1.md`                    `v0_1`               `documented_target`        Governs permitted state
                                                                                                                                                                                             roles where applicable.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md`        `v0_1`               `documented_target`        Governs lineage from
                                                                                                                                                                                             sources to state
                                                                                                                                                                                             consumption.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md`                   current candidate    `documented_target`        Defines expected
                                                                                                                                             schema contract                                 physical structure
                                                                                                                                                                                             without implying
                                                                                                                                                                                             materialization.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md`   `v0_1`               `documented_target`        Defines dataset
                                                                                                                                                                                             identity, grain,
                                                                                                                                                                                             version and scope.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md`                current policy       `documented_target`        Governs permitted and
                                                                                                                                                                                             blocked consumers.

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`            current status rows  `verified_current_state`   Confirms official
                                                                                                                                             for Market State                                target not materialized
                                                                                                                                                                                             and controlled
                                                                                                                                                                                             candidates existing but
                                                                                                                                                                                             not promoted.
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

No authority is redefined by this MDR.

------------------------------------------------------------------------

# Current Physical Evidence

The current project state includes controlled candidate evidence such
as:

``` text
market_state_table_v0_1_candidate_microstructure_halt_controlled
```

and other controlled candidate runs.

These artifacts demonstrate integration and testing progress.

They do not change:

``` text
official_physical_status = contract_defined_not_materialized
```

They support only:

``` text
controlled_candidate_evidence_status = exists_not_promoted
```

------------------------------------------------------------------------

# Required Canonical-to-Physical Mapping

Before physical realization may be considered, the following record
shall exist:

``` text
canonical_to_physical_mapping_market_state_v0_1
```

It shall map:

``` text
Market State
        |
        v
market_state_table
        |
        v
schema contract
dataset contract
registry entry
consumption policy
builder
validators
manifest
status matrix
```

The mapping must exist before any new physical realization is
authorized.

------------------------------------------------------------------------

# Planning Authorization

  Activity                               Authorized
  -------------------------------------- ------------
  materialization planning               `yes`
  authority crosswalk                    `yes`
  canonical-to-physical mapping design   `yes`
  contract-set review                    `yes`
  schema review                          `yes`
  builder design review                  `yes`
  validator design review                `yes`
  lineage planning                       `yes`
  registry planning                      `yes`

------------------------------------------------------------------------

# Physical Authorization

  Activity                       Authorized
  ------------------------------ ------------
  physical_realization           `no`
  builder_execution              `no`
  validator_execution            `no`
  parquet_generation             `no`
  physical_output_registration   `no`
  certification                  `no`
  promotion                      `no`
  downstream_consumption         `no`
  full_universe_claim            `no`
  execution_use                  `no`

------------------------------------------------------------------------

# Blocking Preconditions

Physical realization remains blocked until all applicable conditions are
satisfied:

1.  `canonical_to_physical_mapping_market_state_v0_1` exists and is
    reviewed.
2.  Exact contract-set crosswalk is complete.
3.  Schema contract is current and internally consistent.
4.  Dataset contract is current and internally consistent.
5.  Builder contract and implementation path are available.
6.  Validators and executable tests are available.
7.  Raw-to-consumption lineage is complete for every component.
8.  Manifest and summary requirements are defined.
9.  Registry entry and consumption policy are current.
10. Coverage denominator and lookback policy are explicit.
11. Full-universe claim remains false unless separately proven and
    promoted.
12. Official and controlled-candidate statuses remain explicitly
    separated.
13. Promotion blockers are recorded.
14. A later governed authorization explicitly permits physical
    realization.

Failure of any applicable condition blocks realization.

------------------------------------------------------------------------

# Rejected Materialization Options

This MDR rejects:

-   direct institutional materialization;
-   physical realization before canonical-to-physical mapping;
-   creation of a new artifact identity such as
    `candidate_market_state_table`;
-   candidate status embedded in the stable artifact name;
-   collapsing official status and candidate evidence into one field;
-   full-universe claims without denominator evidence;
-   automatic promotion after successful build;
-   ML/RL consumption by default;
-   execution-ready deployment;
-   bypassing lineage, certification or promotion;
-   treating existing controlled candidates as official Market State.

------------------------------------------------------------------------

# Status Interpretation

The stable physical identity is:

``` text
market_state_table
```

Official physical lifecycle status is tracked independently:

``` text
contract_defined_not_materialized
institutional
deprecated
superseded
retired
```

Controlled evidence status is also tracked independently:

``` text
no_candidate_evidence
exists_not_promoted
validated_for_declared_candidate_scope
candidate_rejected
candidate_superseded
```

A controlled candidate may exist while the official physical
representation remains not materialized.

These statuses shall never be collapsed.

------------------------------------------------------------------------

# Review

  --------------------------------------------------------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- --------------------------------------------------------------------------------------------------------------
  author                              `TSIS Architecture Review`

  reviewer                            `pending`

  review_date                         `pending`

  decision                            `not_reviewed`

  comments                            `Prototype MDR now separates official physical status from controlled candidate evidence status.`

  required_changes                    `Formal review required before this prototype can be used to derive materialization_decision_contract_v0_1.`

  required_changes_status             `open`
  --------------------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Current Governance State

``` text
record_validity = candidate_valid
candidate_planning_authorization = true
physical_realization_authorization = false
official_physical_status = contract_defined_not_materialized
controlled_candidate_evidence_status = exists_not_promoted
```

This MDR is a prototype candidate record.

It is not governed by an approved Materialization Decision Contract
because that contract does not yet exist.

------------------------------------------------------------------------

# Ordered Downstream Workflow

``` text
mdr_market_state_v0_4
        |
        v
canonical_to_physical_mapping_market_state_v0_1
        |
        v
contract-set and blocker review
        |
        v
future explicit physical-realization authorization
        |
        v
controlled physical candidate, if authorized
        |
        v
certification
        |
        v
promotion review
```

Existing candidate evidence does not bypass this ordered workflow for
any future materialization or promotion claim.

------------------------------------------------------------------------

# Fundamental Rule

This MDR prototype authorizes candidate materialization planning for
**Market State**.

It does not authorize creation, execution, registration, certification,
promotion or consumption of `market_state_table`.

The official physical representation remains:

``` text
contract_defined_not_materialized
```

while controlled candidate evidence remains:

``` text
exists_not_promoted
```

These are separate institutional facts and shall never be conflated.
