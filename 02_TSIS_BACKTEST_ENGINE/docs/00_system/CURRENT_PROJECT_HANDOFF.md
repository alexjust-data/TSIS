# Current Project Handoff

Status: LIVE_RESTART_AUTHORITY
Last verified: 2026-07-31
Repository: `C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE`

## Purpose

This file is the mandatory restart point for any agent entering the backtest
engine after an interruption, context loss or agent replacement. It summarizes
the current authority; it does not replace the contracts or governance records
linked below.

## Current State

```text
LAST_CLOSED_GATE =
BT-GATE-014 /
CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_WITH_RESTRICTIONS

IMPLEMENTATION_ACCEPTANCE = ACCEPTED

V0.5 = CONSUMED_FINAL
SECOND_EXECUTION_V0.5 = PROHIBITED

ACTIVE_GATE = NONE

NEXT_CANDIDATE_GATE =
BT-GATE-015 / EVENT_STATE_CONSUMPTION_SLICE

BT-GATE-015 = NOT_OPEN
BT-GATE-015_CONTRACT = NOT_YET_ACCEPTED
BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
BT-GATE-015_PHYSICAL_READ = NOT_AUTHORIZED
```

## Accepted Capability

BT-GATE-014 proved only this bounded capability:

```text
Market State profile = core-four
instrument/session = ACIU / 2021-03-15
authorized physical rows = 2
typed values per event = 17
physical files opened = 1
physical rows read = 2
events emitted = 2
store inserts = 2
probe observations = 2
early deliveries = 0
orders = 0
fills = 0
PnL = false
provider modification = false
```

Scientific identity:

```text
deterministic_output_hash =
6331839dfc6538f7dd6fda9a1fd7efbc7497d541dcb0c0d89cfd679762067cb1
```

This is a bounded integration result. It is not authorization for general
Market State consumption or evidence of strategy profitability.

## Irreversible History

```text
V0.3 = CONSUMED_FAILED_FINAL
V0.4 = CONSUMED_FAILED_FINAL
V0.5 = CONSUMED_FINAL_ACCEPTED
```

None of these authorizations may be reset or reused. Their state files,
receipts, progress records, failure evidence and final evidence are immutable
historical records.

## Boundaries Still Closed

```text
general Market State consumption = NOT_AUTHORIZED
remaining provider Market State rows = NOT_AUTHORIZED
Event State = NOT_AUTHORIZED
StateReplayFeed generalization = NOT_AUTHORIZED
StateBundle general reads = NOT_AUTHORIZED
provider modification = NOT_AUTHORIZED
upstream rebuild = NOT_AUTHORIZED
strategy access to state = NOT_AUTHORIZED
orders/fills/PnL from state = NOT_AUTHORIZED
production/downstream use = NOT_AUTHORIZED
full 2005-2026 backtest = NOT_AUTHORIZED
optimization and edge claims = NOT_AUTHORIZED
```

## Mandatory Reading Order

An agent must read these files before changing anything:

1. `AGENTS.md`
2. `docs/00_system/CURRENT_PROJECT_HANDOFF.md`
3. `docs/00_system/BACKTEST_ENGINE_ROADMAP.md`
4. `docs/00_system/19_BT_GATE_014_FINAL_POSTEXECUTION_ACCEPTANCE_V0_1.md`
5. `C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE\08_GATES_AND_REVIEWS\GATE_REGISTER.json`
6. `C:\TSIS_Data\00_CTO\14_BACKTEST_ENGINE\PACKAGE_MANIFEST.json`

For historical or forensic work, inspect the V0.3-V0.5 authorization documents
and their run directories. Do not execute their physical CLIs.

## Canonical Evidence

External postexecution acceptance packet:

```text
file =
bt_gate_014_single_use_physical_postexecution_packet_v0_5_r2_20260731T010000Z.zip

sha256 =
7def8211c7318b90dd1c4176b4f42c26ff01f325f9c2250931b2073ad7b1a9c4
```


ZIP files are immutable audit snapshots, not the working source of truth. The
canonical working state is the repository plus the governance tree.

## Exact Next Step

The next task is not code and not a physical read.

```text
1. Obtain or identify the provider/shared-boundary evidence handoff for
   bounded Event State consumption.

2. Perform a read-only feasibility review against the accepted replay loop,
   temporal ordering, identity, availability and restriction contracts.

3. Draft the complete BT-GATE-015 contract.

4. Keep:
   BT-GATE-015 = NOT_OPEN
   BT-GATE-015_IMPLEMENTATION = NOT_AUTHORIZED
   BT-GATE-015_PHYSICAL_READ = NOT_AUTHORIZED

5. Request one owner review of the complete contract.

6. Only after explicit approval may non-physical implementation begin.

7. Any physical Event State read requires a separate, newly audited,
   single-use authorization.
```

Do not infer that the Market State authorization applies to Event State.

## Restart Verification

Before continuing, an agent should verify:

```text
AGENTS current authoritative blocks = 1
ROADMAP current authoritative blocks = 1
BT-GATE-014 governance status = CLOSED_PASS
V0.5 status = CONSUMED_BY_RUN_..._v0_5
V0.5 consumed_by_run_id is not null
BT-GATE-015 implementation authorization is absent
governance validation = PASS
```

The physical V0.5 command must never be used as a restart verification.

## Updating This Handoff

Update this file only when an owner-approved gate transition changes:

```text
last closed gate
active gate
authorized scope
consumed authorization
next required action
closed boundary
canonical evidence identity
```

Routine refactors, packaging corrections and test-count changes do not create a
new gate, but any changed evidence identity must be recorded here when it
becomes authoritative.