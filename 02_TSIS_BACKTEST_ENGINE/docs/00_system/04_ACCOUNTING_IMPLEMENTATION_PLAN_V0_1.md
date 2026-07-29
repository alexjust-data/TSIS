# 04 ACCOUNTING IMPLEMENTATION PLAN V0.1

Status: CLOSED_PASS
Date: 2026-07-28

## Goal

Close the minimum gross-to-net accounting increment after the mechanical ABAT round trip.

## Implemented

```text
CostComponent
CostBreakdown
CostModel
CashLedgerEntry
AccountState
AccountingRunSummary
AccountingRunResult
AccountingEngine
```

## Verified

```text
$env:PYTHONPATH='src'; python -m unittest discover -s tests
# Ran 61 tests OK
```

Real smoke:

```text
run_id = accounting_abat_short_open_close_v0_1
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
```

## Explicit Non-Claims

```text
broker_cost_realism = NOT_CLAIMED
fill_realism = NOT_CLAIMED
short_tradability = NOT_EVALUATED
edge = NOT_EVALUATED
```

