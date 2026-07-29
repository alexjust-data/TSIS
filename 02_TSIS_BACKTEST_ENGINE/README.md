# TSIS Backtest Engine

Status: ACTIVE_IMPLEMENTATION_ROOT
Reset: 2026-07-28

This folder is the physical implementation root for the TSIS Python backtest engine.

The operating boundary is:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE
= decisions, guide, architecture notes and construction log

C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
= source code, tests, configs, executable runs and engine outputs
```

The current objective is not a complete institutional platform. The current objective is the first working vertical slice:

```text
BACKTEST_VERTICAL_SLICE_V0_1
```

## Current Priority

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
SINGLE_STRATEGY_END_TO_END_BACKTEST = IMPLEMENTED_AND_ACCEPTED

BT-GATE-012 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
BT-GATE-012_IMPLEMENTATION = IMPLEMENTED_AND_ACCEPTED
IMPLEMENTATION_ACCEPTANCE = ACCEPTED

CURRENT_GATE = BT-GATE-013 / PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PHYSICAL_RUN = NOT_AUTHORIZED
CODE_IMPLEMENTATION = NOT_AUTHORIZED
```

BT-GATE-012 is closed and accepted. BT-GATE-013 has a corrected contract pending final owner review; implementation and physical execution remain not authorized. StateReplayFeed, Market State, Event State and provider integration remain closed.

## 2026-07-29 | BT-GATE-013 corrected contract status

```text
BT-GATE-013 = PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1
BT-GATE-013_CONTRACT = CONTRACT_CORRECTED_PENDING_FINAL_OWNER_REVIEW
BT-GATE-013_IMPLEMENTATION = NOT_AUTHORIZED
PHYSICAL_RUN = NOT_AUTHORIZED
```

