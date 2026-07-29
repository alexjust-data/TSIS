# System status and inspector guide

## Proven vertical slice

```text
registered request
→ fail-closed preflight
→ physical fixture inspection
→ deterministic historical replay
→ scheduled mechanical short round trip
→ accounting with minimum deterministic costs
→ reconciled net PnL and ending equity
```

Bounded ABAT evidence:

```text
quantity = 100
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
```

This proves mechanical and arithmetic closure only.

## Not proven

```text
real bid/ask execution
queue position
partial fills
liquidity sizing
broker commissions/fees
borrow availability
locates
borrow fees
short tradability
strategy edge
robustness
production readiness
Market/Event State consumption
```

## Source snapshot

The baseline used:

- 92 archive entries;
- 61 passing engine tests reported by living documents;
- five test modules;
- two preflight runs;
- one replay smoke;
- one mechanical trade smoke;
- one accounting smoke;
- corrected execution-semantics draft dated 2026-07-29.

Inspectors should begin with `GATE_REGISTER.json`, then follow the traceability matrix for the capability under review.

