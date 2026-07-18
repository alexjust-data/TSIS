# event_state_candidate_build_authorization_v1

Status: `candidate_record_v1`

Governed by:

```text
candidate_governance
```

Derived from:

```text
rjr_event_state_v1_3
mdr_event_state_v1
canonical_to_physical_mapping_event_state_v1
```

------------------------------------------------------------------------

## Purpose

This record prepares authorization for the first **Governance Phase
controlled candidate build/rebuild** of Event State.

It does not authorize an official physical table.

It does not authorize promotion, certification, production deployment,
ML/RL datasets, execution datasets or downstream operational consumption.

------------------------------------------------------------------------

## Authorization Identity

  Field                      Value
  -------------------------- --------------------------------------------------
  authorization_id           `event_state_candidate_build_authorization_v1`
  created_at                 `2026-07-15`
  authorization_status       `accepted`
  authorization_effective    `true`
  reviewer                   `Codex architectural review`
  decision                   `accepted`

------------------------------------------------------------------------

## Authorization Scope

  -------------------------------------------------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -------------------------------------------------------------------------
  build_type                          `controlled_candidate_build_or_rebuild`

  authorized_scope                    `event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled`

  physical_dataset_id                 `event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled`

  materialization_scope               `intraday_1m_quote_guarded_event_state_controlled_candidate`

  official_table_authorized           `false`

  promotion_authorized                `false`

  certification_authorized            `false`

  downstream_consumption_authorized   `false`

  ml_rl_dataset_authorized            `false`

  execution_authorized                `false`

  full_universe_claim                 `false`
  -------------------------------------------------------------------------------------------------------------

------------------------------------------------------------------------

## Precondition Status

  -------------------------------------------------------------------------------------------------------------
  Precondition                                            Status
  -------------------------------------------------------- ----------------------------------------------------
  accepted `rjr_event_state_v1_3`                          `satisfied`

  accepted `mdr_event_state_v1`                            `satisfied`

  reviewed `canonical_to_physical_mapping_event_state_v1`  `satisfied`

  compatible schema contract                               `satisfied`

  compatible dataset contract                              `satisfied`

  builder definition                                       `satisfied_existing_candidate_builder`

  validator definition                                     `satisfied_existing_contract_and_candidate_tests`

  manifest specification                                   `satisfied_existing_candidate_manifest_pattern`

  controlled output location                               `satisfied_existing_controlled_test_run_root`
  -------------------------------------------------------------------------------------------------------------

This authorization cannot become effective until the mapping review is
closed.

------------------------------------------------------------------------

## Executable References

Builder:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
```

Candidate builder test:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_intraday_quote_guarded_candidate_builder.py
```

Contract stack test:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_table_contract.py
```

Existing controlled evidence dataset:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet
```

Existing controlled evidence manifest:

```text
C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json
```

Lineage contract:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
```

------------------------------------------------------------------------

## Existing Evidence Boundary

A controlled candidate already exists for this scope.

Therefore this record does not claim to authorize the first historical
prototype ever produced.

It authorizes only a governed **candidate build/rebuild decision path**
for the Governance Phase, once all review preconditions close.

Existing evidence status:

```text
controlled_candidate_not_promoted
```

Known documented evidence:

```text
joined_event_state_rows = 15
event_count = 5
state_role_counts = at_event: 5, post_event_review: 5, pre_event: 5
validator_status = passed
full_universe_claim_rows = 0
valid_for_ml_feature_candidate_rows = 0
valid_for_rl_state_candidate_rows = 0
execution_truth_rows = 0
```

This evidence remains candidate-only and not official.

------------------------------------------------------------------------

## Required Acceptance Gates

Any authorized candidate build/rebuild must satisfy:

```text
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
full_universe_claim = false
execution_truth = false
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
```

The build must also prove:

-   no `outcome__*`, `label__*`, `reward__*`, `future__*`,
    `strategy__*`, `signal__*`, `fill__*`, `pnl__*` or `policy__*`
    columns are present;
-   `event_state_id` is unique;
-   physical grain is respected;
-   `decision_timestamp_utc` and cutoff fields obey temporal legality;
-   lineage and manifest references are emitted;
-   candidate scope is controlled and explicitly non-official.

------------------------------------------------------------------------

## Builder Responsibilities

The builder may only:

-   build the approved candidate scope;
-   preserve canonical identity;
-   preserve temporal legality;
-   preserve event scope;
-   emit manifest and lineage;
-   populate only governed fields;
-   keep outcomes, labels, rewards, strategy, execution, fills, PnL and
    future-derived fields out of the table.

------------------------------------------------------------------------

## Validator Responsibilities

Validators must check:

-   schema compliance;
-   temporal legality;
-   identity consistency;
-   physical grain uniqueness;
-   forbidden-field absence;
-   label-separation flags;
-   lineage completeness;
-   controlled scope compliance;
-   no full-universe claim;
-   no execution-truth claim;
-   no downstream-consumption authorization.

------------------------------------------------------------------------

## Expected Outputs

If this authorization later becomes effective, the build/rebuild may
produce only controlled candidate evidence:

-   candidate `event_state_table` parquet;
-   validation report;
-   manifest;
-   lineage metadata;
-   controlled registry/status evidence.

No official E-root table is authorized by this record.

------------------------------------------------------------------------

## Explicit Non-Authorizations

This record does not authorize:

-   institutional table creation;
-   official `event_state_table_v0_1` promotion;
-   certification;
-   production deployment;
-   ML/RL training datasets;
-   execution datasets;
-   downstream operational consumption;
-   full-universe claims;
-   event-family-specific observable blocks not governed elsewhere.

------------------------------------------------------------------------

## Review

  Field                     Value
  ------------------------- ----------------------------
  author                    `TSIS Governance`
  reviewer                  `Codex architectural review`
  review_date               `2026-07-15`
  decision                  `accepted`
  required_changes          `none`
  required_changes_status   `not_applicable`

------------------------------------------------------------------------

## Current Governance State

```text
authorization_effective = true
blocking_precondition = none
candidate_build_allowed_now = true
official_table_authorized = false
promotion_authorized = false
```

------------------------------------------------------------------------

## Fundamental Rule

This record may authorize exactly one thing after review preconditions
close:

```text
Build or rebuild a controlled candidate Event State table within the approved scope.
```

Everything else remains blocked until subsequent governance decisions.