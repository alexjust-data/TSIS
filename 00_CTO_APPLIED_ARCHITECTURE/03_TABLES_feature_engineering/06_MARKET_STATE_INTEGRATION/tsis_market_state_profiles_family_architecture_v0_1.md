# TSIS Market State Profiles Family Architecture v0.1

Status: `profiles_family_architecture_recorded_no_execution_v0_1`
Date: `2026-07-23`
Scope: `market_state_profile_family_after_core_four_official_profile_promotion`

This document records the architecture shift from a single monolithic
`Market State` target toward a governed family of Market State profiles.

It does not modify an official profile registry artifact.
It does not authorize an official dataset.
It does not authorize production, downstream consumption, full-history
execution or full-universe execution.

## 1. Current Institutional Fact

The first promoted TSIS Market State profile is:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
promotion_run = official_market_state_candidate_promotion_v0_1_20260723T193403Z
artifact_validation_run = official_market_state_profile_artifact_validation_v0_1_20260723T193711Z
registry_path = official_profiles/market_state_core_four_intraday_profile_v0_1
```

This is an official profile contract. It is not complete TSIS Market State and
it is not an operational official dataset.

## 2. Required Distinctions

TSIS must keep these identities separate:

```text
official_profile_registry
    = semantic contract and evidence boundary

official_dataset_registry
    = operational physical dataset identity

production_builder
    = authorized build process for operational use

downstream_consumption_policy
    = who may consume what, for which purpose, under which restrictions
```

Current boundary:

```text
official_profile_registry = contains market_state_core_four_intraday_profile_v0_1
official_dataset_registry = not updated
official_market_state_authorized = false
official_parquet_materialization_authorized = false
production_builder_authorized = false
downstream_consumption_authorized = false
```

## 3. Profile Family Model

Market State profiles are versioned semantic slices of the observable market
state, not competing definitions of truth.

Current family seed:

```text
market_state_core_four_intraday_profile_v0_1
    = official_profile_promoted_with_restrictions
```

Potential future profiles:

```text
market_state_core_four_daily_profile_v0_1
market_state_liquidity_profile_v0_1
market_state_news_profile_v0_1
market_state_microstructure_profile_v0_1
market_state_order_flow_profile_v0_1
```

These names are architectural placeholders only. None is authorized, promoted
or executable by this document.

## 4. Extension Rule

Future extensions must not silently mutate
`market_state_core_four_intraday_profile_v0_1`.

Every new profile must have its own lifecycle:

```text
profile_design
profile_authorization
sample_preflight_or_scope_freeze
surface_or_source_binding_when_needed
builder_resolution
integration
candidate_materialization
independent_physical_validation
promotion_review
profile_promotion
profile_artifact_validation
```

If an extension changes the semantics of an already promoted profile, it must
be a new profile version or a separate profile identity. It cannot be an
undocumented in-place change.

## 5. Shared Guarantees

Every official or candidate Market State profile must preserve:

```text
observable_as_of_semantics
no_future_outcomes_in_state
explicit_information_object_lineage
logical_profile_id
profile_version
schema_contract
source_authority_manifest
run_id_lineage
fingerprint_lineage
restriction_manifest
promotion_status
```

Calendar-aware intraday profiles must additionally preserve:

```text
governed_calendar_binding
calendar_version
calendar_row_fingerprint
session_open_utc
session_close_utc
fixed_utc_fallback_uses = 0
```

## 6. Relationship To Event State

`Event State` must consume or reference a valid Market State profile contract.
It must not redefine Market State, duplicate a full market snapshot per event,
or bypass profile restrictions.

Current admissible parent for future Event State design:

```text
parent_profile_id = market_state_core_four_intraday_profile_v0_1
parent_profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
```

This document records the architectural parent. It does not authorize Event
State execution or consumption of physical Market State artifacts.

## 7. Next Gates

The next work must be opened by explicit authorization. Valid next design-only
directions are:

```text
market_state_profile_consumption_policy_design
market_state_profile_operational_registry_design
event_state_architecture_design
```

Still closed:

```text
official_market_state_dataset_promotion
official_market_state_parquet_materialization
production_market_state_builder
downstream_consumption
event_state_builder_execution
event_state_materialization
full_history_execution
full_universe_execution
```
