# 03 REPLAY IMPLEMENTATION PLAN V0.1

Status: IMPLEMENTED_MINIMUM_DRAFT
Date: 2026-07-28

Goal: consume only `PREFLIGHT_PASS` data and emit deterministic, legally observable 1m replay events.

Scope:

```text
input: data_preflight_report.json
output: ReplayBarEvent / ReplayGapEvent sequence
order: available_at, event priority, ticker
available_at: ts_utc + 1 minute
gaps: emitted as GAP events, never imputed
vendor derived fields: not consumed, including vw
```

Acceptance tests:

```text
preflight PASS required
physical inspection PASS required
source file hashes verified
source files read with explicit columns only
bar available_at = ts_start + 1 minute
bar invisible before available_at
interior gaps emitted without synthetic bars
sequence deterministic
vw absent from event contract
real fixture smoke replay passes
```

Not in scope:

```text
strategy decisions
orders
fills
positions
execution realism
full 2005-2026 run
```
