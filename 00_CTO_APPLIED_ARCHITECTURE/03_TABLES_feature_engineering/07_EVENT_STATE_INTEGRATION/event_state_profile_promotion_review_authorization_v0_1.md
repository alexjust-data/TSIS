# Event State Profile Promotion Review Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-24`

This document authorizes a review-only gate for the first bounded Event State
profile candidate:

```text
event_state_profile_id =
    event_state_core_four_intraday_profile_v0_1

event_type_scope =
    event_type:market_data:session_opened

accepted_subject_scope =
    exchange_session
```

The review may inspect the accepted Event State design chain, the accepted
bounded execution run, the accepted physical validation run and the accepted
candidate dataset review run.

It may decide whether the bounded evidence is sufficient to open a separate
semantic profile promotion authorization.

It may not promote an Event State profile, promote an Event State dataset,
write official parquet, materialize Event State, authorize production,
authorize downstream consumption, create Event Types, detect events, create
unbounded Event Instances, or expand beyond `session_opened`.

## Authorized Gate

```text
gate =
    event_state_profile_promotion_review_v0_1

scope =
    configs/event_state_profile_promotion_review_scope_v0_1.json

authorized_actions =
    evidence_inventory
    restriction_classification
    semantic_profile_sufficiency_review
    profile_promotion_review_decision

authorized_decision_values =
    APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS
    BLOCKED_PENDING_EVIDENCE
    REJECTED_FOR_EVENT_STATE_PROFILE_PROMOTION
```

## Accepted Review Run

```text
accepted_review_run =
    event_state_profile_promotion_review_v0_1_20260724T201046Z

event_state_profile_promotion_review =
    APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS

accepted_as_profile_promotion_review_evidence =
    true

superseded_attempt =
    event_state_profile_promotion_review_v0_1_20260724T200936Z

supersession_reason =
    heartbeat artifact hash order defect;
    not semantic evidence defect
```

## Review Boundary

```text
official_event_state_profile_promotion_executed = false
official_event_state_dataset_promotion = false
official_parquet_write = false
event_state_materialization = false
production = false
downstream_consumption = false
event_detection = false
new_event_types = false
unbounded_event_instance_binding = false
unbounded_event_window_binding = false
```

## Required Accepted Evidence

```text
event_state_profile_contract_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_type:market_data:session_opened =
    accepted_with_restrictions

event_instance_binding_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_window_binding_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_profile_compatibility_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

instrument_session_projection_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_integration_design =
    CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_execution_chain_joint_review =
    CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION

event_state_bounded_execution_chain_execution =
    CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT

event_state_bounded_execution_chain_physical_validation =
    CLOSED_PASS_WITH_RESTRICTIONS

event_state_candidate_dataset_review =
    CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION
```

## Still Closed

```text
complete_tsis_event_state = false
all_event_types = false
halt_resumed = false
official_event_state_dataset = false
official_event_state_parquet = false
production = false
downstream_consumption = false
full_history = false
full_universe = false
```

If the review approves, the next allowed gate is:

```text
event_state_profile_promotion_authorization_v0_1
```

