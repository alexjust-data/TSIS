# Market State On-Demand Capability Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Parent Runtime Architecture: `runtime_capabilities_architecture_v0_1`

This document defines the first Market State on-demand capability. It translates
the official semantic profile into a future request-resolved generation flow.

It is design-only. It does not execute requests, read data, build parquet, write
registry entries or authorize downstream consumption.

## 1. Capability Definition

```text
Market State on-demand capability
    = the governed ability to accept a Market State request
      and later, only when authorized, resolve sources, profiles,
      universe, dates, execution plan, validation and registry output.
```

The capability is not the same as an official dataset.

```text
official semantic profile exists = true
official physical dataset exists = false
runtime capability design exists = true
runtime capability execution exists = false
```

## 2. Request-Centered Flow

```text
Market State Request
-> request contract validation
-> profile resolver
-> source resolver
-> universe/calendar resolver
-> execution planner
-> authorization check
-> deterministic build, only in a later gate
-> validation
-> registry entry, only in a later gate
-> manifest + lineage + hashes
```

## 3. Profile Authority

The first supported semantic target is:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
artifact_validation_run = official_market_state_profile_artifact_validation_v0_1_20260723T193711Z
```

The profile is official semantically, but not a consumable physical dataset.

```text
official_market_state_authorized = false
official_dataset_registry_write_authorized = false
official_parquet_files_written = 0
```

## 4. Required Future Components

```text
market_state_request_contract_design_v0_1
market_state_profile_resolver_design_v0_1
market_state_source_resolver_design_v0_1
market_state_universe_calendar_resolver_design_v0_1
market_state_execution_planner_design_v0_1
market_state_materializer_design_v0_1
market_state_validator_design_v0_1
market_state_dataset_registry_design_v0_1
market_state_idempotency_design_v0_1
```

The route may group some of these if a future authorization freezes a controlled
scope, but no implementation should happen before the contracts are explicit.

## 5. Request Fingerprint Principle

A future request must produce a deterministic fingerprint from at least:

```text
request_type
profile_id
profile_version
source authority versions
universe definition
date/session range
resolution
calendar authority
builder/materializer version
validator policy
output mode
```

Same request plus same authorities must either reuse an accepted output or prove
a deterministic rebuild.

## 6. Blocking Rules

A future request must block before execution if any of these are unresolved:

```text
profile not official as semantic profile
profile artifact validation missing
source physical authority missing
universe definition missing
calendar authority missing
temporal as-of policy missing
estimated scope exceeds authorization
output registry policy missing
```

## 7. Closure

```text
market_state_on_demand_capability_design
    = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

requests_executed = 0
source_rows_read = 0
market_state_records_emitted = 0
market_state_parquet_files_written = 0
dataset_registry_entries_written = 0
production = false
downstream_consumption = false
```
