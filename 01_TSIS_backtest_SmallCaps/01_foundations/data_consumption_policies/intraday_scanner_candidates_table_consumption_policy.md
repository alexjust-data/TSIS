# Intraday Scanner Candidates Table Consumption Policy v0.1

Dataset:

```text
intraday_scanner_candidates_table_v0_1
```

## Allowed Uses

Allowed:

```text
candidate denominator for intraday research
DAS/frontside overlay input
event-window seeding
market_state/event_state candidate builder input
forensic inspection of first-push timing
```

## Blocked Uses

Blocked:

```text
direct ML feature table
direct RL state table
entry/exit signal
label/reward/outcome table
execution simulator truth
official live scanner
official full-universe claim without promoted 20y run
```

## Required Consumer Behavior

Consumers must declare:

```text
scanner_run_id
scanner_definition_id
source replay root
date range
materialization_scope
full_universe_claim
strategy overlay contract if any
```

If `selected_intraday_in_play_candidate=false`, consumers may still inspect
the row for diagnostics, but must not treat it as an in-play candidate.

If `float_shares` is null, consumers must not infer float from
`shares_outstanding_context`.
