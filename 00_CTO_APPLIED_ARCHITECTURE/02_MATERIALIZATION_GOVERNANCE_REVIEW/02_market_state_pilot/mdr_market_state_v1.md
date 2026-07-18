# mdr_market_state_v1

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
rjr_market_state_v0_4
```

Prototype reference:

``` text
mdr_market_state_v0_4
```

------------------------------------------------------------------------

# Purpose

This is the first contract-compliant Materialization Decision Record for
the Canonical Market Representation:

``` text
Market State
```

It belongs to the Governance Phase of TSIS.

Its purpose is to apply the existing Materialization Decision Contract,
not to redesign it.

This record does not authorize physical realization, certification,
promotion or downstream consumption.

------------------------------------------------------------------------

# MDR Identity

  Field                 Value
  --------------------- ------------------------------------------
  mdr_id                `mdr_market_state_v1`
  contract_version      `materialization_decision_contract_v0_3`
  created_at            `2026-07-15`
  supersedes_mdr_id     `not_applicable_new_governance_lineage`
  prototype_reference   `mdr_market_state_v0_4`
  mdr_status            `draft`

------------------------------------------------------------------------

# Upstream Authority

  Field                          Value
  ------------------------------ ------------------------------------
  canonical_representation_ref   `market_state`
  supporting_rjr                 `rjr_market_state_v0_4`
  rjr_validity                   `true`
  effective_acceptance           `true`
  mdr_authorization              `true_within_candidate_governance`

------------------------------------------------------------------------

# Proposed Materialization Decision

  -------------------------------------------------------------------------------
  Field                                  Value
  -------------------------------------- ----------------------------------------
  proposed_materialization_decision      `candidate_materialization_planning`

  materialization_mode                   `candidate_controlled_materialization`

  materialization_scope                  `controlled_candidate`

  physical_representation_type           `dataset_table`

  stable_artifact_identity               `market_state_table`

  official_physical_status               `contract_defined_not_materialized`

  controlled_candidate_evidence_status   `exists_not_promoted`
  -------------------------------------------------------------------------------

------------------------------------------------------------------------

# Materialization Parameters

  Field                       Value
  --------------------------- --------------------------------------------------
  coverage_denominator        `declared_coverage_only`
  lookback_policy             `market_state_coverage_and_lookback_policy_v0_1`
  full_universe_claim         `false`
  candidate_planning_status   `draft`

------------------------------------------------------------------------

# Authority References

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  authority_path                                                                                                                             authority_section                          authority_type    authority_reference_status
  ------------------------------------------------------------------------------------------------------------------------------------------ ------------------------------------------ ----------------- ----------------------------
  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\09_Chapter_8_State_Layer_TSIS.md`                     `8.6 Market State`                         `primary`         `verified_current`

  `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`         `Materialization Policy`                   `primary`         `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`    `Primary key and composition`              `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md`        `Coverage, lookback and promotion gates`   `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`                           `Flow and acceptance criteria`             `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_observable_eligibility_contract_v0_1.md`            `Observable eligibility`                   `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_decision_timestamp_policy_v0_1.md`                  `Decision timestamp policy`                `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md`        `Raw-to-consumption lineage`               `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md`                   `Current schema contract`                  `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md`   `v0_1`                                     `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md`                `Current consumption policy`               `supporting`      `verified_current`

  `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`            `Market State status rows`                 `supporting`      `verified_current`
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# Blocking Preconditions

Physical realization remains blocked until:

1.  `canonical_to_physical_mapping_market_state_v1` exists and is
    approved.
2.  Contract-set review is complete.
3.  Schema and dataset contracts are current.
4.  Builder and validators are approved.
5.  Raw-to-consumption lineage is complete.
6.  Manifest and summary requirements are defined.
7.  Registry entry and consumption policy are current.
8.  Coverage denominator and lookback policy are confirmed.
9.  A `physical_realization_authorization_record` is approved.

------------------------------------------------------------------------

# Review

  -----------------------------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -----------------------------------------------------------------------------------
  author                              `TSIS Governance`

  reviewer                            `pending`

  review_date                         `pending`

  decision                            `not_reviewed`

  comments                            `First Governance Phase MDR aligned with materialization_decision_contract_v0_3.`

  required_changes                    `Formal review required.`

  required_changes_status             `open`
  -----------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# MDR Validity

``` text
mdr_validity = true
```

Reason:

-   all mandatory contract fields are present;
-   upstream authority is valid;
-   authority references are explicit;
-   blockers are documented;
-   review state is explicit;
-   `mdr_status = draft` is consistent with `decision = not_reviewed`.

------------------------------------------------------------------------

# Planning Authorization

``` text
planning_authorization = false
```

Because:

``` text
formal_review_decision = not_reviewed
```

------------------------------------------------------------------------

# Physical Realization Authorization

``` text
physical_realization_authorization = false
```

Because:

-   planning authorization is false;
-   canonical-to-physical mapping is not yet approved;
-   blockers remain open;
-   no Physical Realization Authorization Record exists.

------------------------------------------------------------------------

# Authorized Next Artifact

After successful formal review, this MDR may authorize creation of:

``` text
canonical_to_physical_mapping_market_state_v1
```

No physical implementation is authorized by this record.

------------------------------------------------------------------------

# Fundamental Rule

This MDR applies an existing candidate governance contract.

It does not redefine the governance mechanism.

No physical realization, certification, promotion or downstream
consumption may begin until later governance artifacts explicitly
authorize those stages.
