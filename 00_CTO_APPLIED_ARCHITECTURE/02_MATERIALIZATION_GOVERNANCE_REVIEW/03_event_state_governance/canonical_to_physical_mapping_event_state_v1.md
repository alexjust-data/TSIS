# canonical_to_physical_mapping_event_state_v1

Status: `candidate_record_v1`

Governed by:

```text
candidate_governance
```

Derived from:

```text
rjr_event_state_v1_3
mdr_event_state_v1
```

------------------------------------------------------------------------

## Purpose

Defines how the Canonical Core Representation **Event State** maps to its
proposed physical implementation:

```text
event_state_table
```

This mapping establishes semantic-to-physical translation only.

It does **not** authorize physical realization, certification, promotion
or downstream consumption.

------------------------------------------------------------------------

## Mapping Identity

  Field                  Value
  ---------------------- ------------------------------------------
  mapping_id             `canonical_to_physical_mapping_event_state_v1`
  created_at             `2026-07-15`
  mapping_status         `accepted`
  canonical_reference    `event_state`
  supporting_rjr         `rjr_event_state_v1_3`
  supporting_mdr         `mdr_event_state_v1`

------------------------------------------------------------------------

## Canonical Representation

-   canonical_representation: `event_state`
-   representation_version: `v1`
-   semantic_role: observable market state relative to a governed event
-   event_creation_authority: `not_authorized_here`
-   outcome_authority: `not_authorized_here`

------------------------------------------------------------------------

## Proposed Physical Representation

-   stable_artifact_identity: `event_state_table`
-   physical_representation_type: `dataset_table`
-   current_official_status: `contract_defined_not_materialized`
-   controlled_candidate_evidence_status: `exists_not_promoted`
-   future_root: `E:/TSIS/data/data_foundation_outputs/event_state_table`

------------------------------------------------------------------------

## Canonical To Physical Crosswalk

  Canonical Concept       Physical Mapping
  ----------------------- ------------------------------------------------
  Event State             `event_state_table`
  Event-relative identity `event_state_id`
  Event anchor            `event_id`, `event_window_id`, `event_family`
  Market reference        `market_state_id`
  Temporal legality       `decision_timestamp_utc`, `state_cutoff_utc`
  State role              `state_role`
  Versioning              `state_schema_version`, `state_builder_version`
  Label separation        join keys allowed, inline values prohibited
  Consumer semantics      consumer gate columns
  Lineage                 build/run/source fields and manifest linkage

------------------------------------------------------------------------

## Physical Grain

The base physical grain is:

```text
event_window_id
+ decision_timestamp_utc
+ state_role
+ state_schema_version
```

The physical primary key is:

```text
event_state_id
```

------------------------------------------------------------------------

## Core Physical Columns

These columns are common to every Event State physical candidate,
independent of event family.

### Identity

-   `event_state_id`
-   `event_id`
-   `event_window_id`
-   `market_state_id`
-   `instrument_id`
-   `ticker`
-   `event_family`
-   `event_timestamp_utc`
-   `decision_timestamp_utc`
-   `decision_date`
-   `state_role`
-   `state_schema_version`
-   `state_builder_version`
-   `state_quality_state`

### Event Anchoring

-   `event_window_start_utc`
-   `event_window_end_utc`
-   `pre_event_window_start_utc`
-   `pre_event_window_end_utc`
-   `state_cutoff_utc`
-   `state_cutoff_reason`
-   `event_source_dataset_id`
-   `event_source_quality_state`

### Label Separation

-   `outcome_join_key`
-   `label_join_key`
-   `outcome_values_inline_allowed`
-   `label_columns_inline_allowed`
-   `reward_columns_inline_allowed`

Required values:

```text
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
```

### Consumer Gates

-   `valid_for_pattern_discovery`
-   `valid_for_ml_feature_candidate`
-   `valid_for_backtest_context_candidate`
-   `valid_for_rl_state_candidate`
-   `valid_for_rl_training_direct`
-   `valid_for_execution_context_candidate`
-   `valid_for_execution_simulator_direct`
-   `contains_future_information_without_event_filter`
-   `requires_asof_filter`
-   `full_universe_claim`
-   `execution_truth`

Default values before a real builder:

```text
valid_for_rl_training_direct = false
valid_for_execution_simulator_direct = false
execution_truth = false
requires_asof_filter = true
full_universe_claim = false
```

### Lineage

-   `build_run_id`
-   `created_at_utc`
-   source dataset identifiers
-   source manifest references
-   builder/config/hash references

------------------------------------------------------------------------

## Event Family Specific Blocks

Not defined in this base mapping:

-   `halt_event_state_fields`
-   `first_push_event_state_fields`
-   `rebreak_event_state_fields`
-   `news_event_state_fields`
-   `volume_burst_event_state_fields`

These blocks remain outside the base mapping until an event family is
selected and governed.

No family-specific observable column may be treated as required by this
base mapping.

------------------------------------------------------------------------

## Allowed Inputs

-   governed Event Candidate
-   governed Event Window
-   governed Market State or Market State projection
-   governed observable primitives
-   governed derived observables
-   governed source lineage and quality metadata

------------------------------------------------------------------------

## Forbidden Inputs And Inline Fields

The physical representation must not contain inline values from:

-   Outcome
-   Label
-   Reward
-   Strategy
-   Execution
-   Fill simulation
-   PnL
-   Future-derived information

Allowed exception:

```text
outcome_join_key = allowed
label_join_key = allowed
outcome_values_inline_allowed = false
label_columns_inline_allowed = false
reward_columns_inline_allowed = false
```

The join keys may support later supervised research joins, but the
target values themselves must remain outside `event_state_table`.

------------------------------------------------------------------------

## Builder Responsibilities

A future builder must:

-   preserve canonical identity;
-   enforce the physical grain;
-   enforce temporal legality;
-   preserve event scope;
-   populate only governed fields;
-   emit lineage metadata;
-   set consumer gates conservatively;
-   keep outcomes, labels, rewards, strategy and execution fields out of
    the table.

------------------------------------------------------------------------

## Validator Responsibilities

Validators must check:

-   identity consistency;
-   grain uniqueness;
-   temporal legality;
-   observability;
-   schema compliance;
-   forbidden-field absence;
-   label-separation flags;
-   lineage completeness;
-   no full-universe claim unless separately authorized;
-   no execution-truth claim.

------------------------------------------------------------------------

## Downstream Artifacts

This mapping may inform:

-   schema contract review;
-   dataset contract review;
-   builder design;
-   validators;
-   registry entry review;
-   consumption policy review;
-   manifest requirements;
-   status matrix updates.

It does not replace any of those artifacts.

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
mapping_status = accepted
mapping_review_status = complete
planning_authorization = true
physical_realization_authorization = false
```

Reason:

-   `mdr_event_state_v1` authorizes planning;
-   this mapping review is complete;
-   physical realization is not authorized by this mapping.

------------------------------------------------------------------------

## Fundamental Rule

This mapping defines **how** Event State is translated into a physical
representation.

It does not define event-family-specific observable blocks.

It never authorizes **when** physical realization may occur.