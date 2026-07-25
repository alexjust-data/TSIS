# Runtime Capabilities Architecture v0.1

Status: `RECORDED_ARCHITECTURE_NO_EXECUTION`
Date: `2026-07-24`

This document defines the TSIS runtime capability layer.

Until this point, TSIS has primarily governed what market representations mean.
From this point, TSIS must also govern how a representation is generated when a
human, experiment or future system asks for it.

## 1. Core Shift

```text
Before:
    build a dataset

Now:
    resolve a governed request
    into a reproducible dataset if authorized
```

A dataset is an output. A runtime capability is the governed ability to produce
or retrieve that output under a contract.

## 2. Canonical Runtime Flow

```text
Request
-> Request Contract
-> Profile Resolver
-> Source Resolver
-> Universe / Calendar Resolver
-> Execution Plan
-> Authorization Check
-> Deterministic Build
-> Validation
-> Dataset Registry / Candidate Registry
-> Manifest + Lineage + Hashes
-> Delivery or Blocked Result
```

## 3. Component Definitions

```text
request_contract
    = what is being asked: kind, profile, dates, universe, output mode.

profile_resolver
    = checks semantic profile identity, status, version and restrictions.

source_resolver
    = resolves physical source authority, coverage and policies.

execution_planner
    = computes partitions, estimated rows, validators, limits and output target.

materializer
    = builds data only after explicit execution authorization.

validator
    = checks schema, lineage, temporal legality, determinism and scope.

dataset_registry
    = records outputs by request fingerprint, coverage, hashes and status.

cache_or_idempotency_index
    = prevents duplicate outputs for identical governed requests.
```

## 4. Layer Boundary

This layer is not:

```text
Data Foundation
Market State semantics
Event State semantics
Execution State
Strategy
Outcome
```

It is runtime infrastructure. It can serve Market State, Event State and later
other governed dataset-generation requests.

## 5. Current State

```text
market_state_core_four_intraday_profile_v0_1
    = official semantic profile
    = no official physical dataset yet

event_state_core_four_intraday_profile_v0_1
    = official semantic profile
    = no official physical dataset yet

request_resolver
    = not implemented

materializer
    = not authorized

dataset registry write
    = not authorized
```

## 6. First Capability To Design

The first specific runtime capability should be:

```text
market_state_on_demand_capability_design_authorization_v0_1
```

Reason:

```text
Event State on-demand depends on Market State on-demand.
```

## 7. Closure

```text
runtime_capabilities_architecture
    = RECORDED_ARCHITECTURE_NO_EXECUTION

requests_executed = 0
materializers_executed = 0
datasets_written = 0
registry_entries_written = 0
source_rows_read = 0
production = false
downstream_consumption = false
```
