# BT-GATE-011 - Single Strategy End-To-End Backtest Contract V0.1

Status: CLOSED_PASS_IMPLEMENTATION_ACCEPTED
Gate: BT-GATE-011
Capability: SINGLE_STRATEGY_END_TO_END_BACKTEST
Owner approval: OWNER_APPROVED_FOR_CONTINUOUS_IMPLEMENTATION
Implementation state: IMPLEMENTED_AND_ACCEPTED
Final acceptance: ACCEPTED

## Purpose

Build the first complete historical backtest path using the already accepted engine capabilities. This gate validates the engine pipeline, not strategy edge or small-caps economic realism.

## Authorized Strategy

```text
strategy_id = open_short_close_cover_v0_1
strategy_spec_version = 0.1
RUN_PURPOSE = ENGINE_VALIDATION_RUN
EDGE_EVIDENCE = NOT_AUTHORIZED
ECONOMIC_REALISM = INCOMPLETE
STRATEGY_OPTIMIZATION = NOT_AUTHORIZED
```

The labels `open` and `close` are strategy labels only. They do not authorize new `MARKET_ON_OPEN` or `MARKET_ON_CLOSE` semantics. Orders are implemented as `MARKET_PROXY` orders using only the accepted `DETERMINISTIC_FILL_SIMULATOR_V0_1` semantics.

## Fixture

```text
fixture_id = TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1
session = 2026-01-05 REGULAR_ONLY
symbols = ABAT, ABEO, ABSI, ABTC, ACB
quantity = 100 shares per symbol
```

The fixture has a passed physical preflight and replay evidence. Gaps are preserved as `ReplayGapEvent`; no prices or bars are imputed.

## Implemented Flow

```text
RunPreflight evidence
-> HistoricalReplayFeed
-> StrategySpec
-> preprogrammed point-in-time decisions
-> BacktestOrderIntent
-> ExecutionOrder
-> DeterministicFillSimulator V0.1
-> FillRecord / CostBreakdownV0
-> positions
-> cash ledger
-> Trade Ledger
-> equity curve
-> metrics
-> Unified Run Manifest
```

## Binding Invariants

1. No decision consumes information after `decision_timestamp`.
2. Entry and exit orders are submitted before the source bar they evaluate.
3. Every fill comes from `DeterministicFillSimulator V0.1`.
4. `MechanicalEventLoop` does not produce fills in this gate.
5. `ReplayGapEvent` is preserved and never imputed.
6. Every symbol ends with position zero or the run fails.
7. Orders, fills, positions, costs, PnL, cash and equity reconcile.
8. Costs are counted exactly once from simulator `CostBreakdownV0`.
9. Same inputs and configuration produce the same semantic output hash.
10. Non-executable symbols must be explicit; no symbol may disappear silently.

## Outputs Required

The accepted run must produce:

- `backtest_run_request.json`
- `strategy_spec.json`
- `decisions.json`
- `order_intents.json`
- `orders.json`
- `order_simulation_results.json`
- `fills.json`
- `cost_breakdowns.json`
- `trade_ledger.json`
- `cash_ledger.json`
- `equity_curve.json`
- `metrics_summary.json`
- `run_summary.json`
- `validation_report.json`
- `determinism_report.json`
- `unified_run_manifest.json`
- `artifact_hashes.json`

## Prohibited Capabilities

```text
StateReplayFeed = NOT_AUTHORIZED
StateBundle physical reads = NOT_AUTHORIZED
Market State consumption = NOT_AUTHORIZED
Event State consumption = NOT_AUTHORIZED
provider modification = NOT_AUTHORIZED
borrow/locates = NOT_IMPLEMENTED
SSR = NOT_IMPLEMENTED
halts = NOT_IMPLEMENTED
liquidity/capacity = NOT_IMPLEMENTED
partial fills = NOT_IMPLEMENTED
bid/ask execution = NOT_IMPLEMENTED
optimization = NOT_AUTHORIZED
edge claims = NOT_AUTHORIZED
```

## Implemented Evidence

```text
run_id = bt_gate_011_open_short_close_qg5_v0_1
validation_status = PASS
order_count = 10
fill_count = 10
trade_count = 5
gross_pnl = -73.00
total_costs = 10.00
net_pnl = -83.00
ending_equity = 9917.00
deterministic_output_hash = f5bccea7d6f5f6eff0647a66d4827a011e5854af9644a8854b10135da883cc2b
engine_suite = 99 tests OK
```

## Current Gate State

```text
BT-GATE-011 = CLOSED_PASS_IMPLEMENTATION_ACCEPTED
IMPLEMENTATION = COMPLETE_AND_ACCEPTED
FINAL_OWNER_REVIEW = ACCEPTED
NEXT_GATE = BT-GATE-012 / MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE
```

This document is the accepted BT-GATE-011 contract and evidence summary. BT-GATE-011 is closed as `CLOSED_PASS_IMPLEMENTATION_ACCEPTED`; the next gate is BT-GATE-012.
