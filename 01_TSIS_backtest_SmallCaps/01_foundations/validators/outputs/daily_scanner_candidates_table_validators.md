# Daily Scanner Candidates Table Validators `v0_1`

## 1. Scope

Target dataset:

```text
daily_scanner_candidates_table_v0_1
```

Current status:

```text
validator_contract_defined
implementation_pending
```

## 2. Required Structural Checks

Validator must fail when:

- required columns are missing;
- duplicate grain exists for
  `scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id`;
- `rank <= 0` for selected candidates;
- `top_n <= 0` when `included_in_top_n = true`;
- `population_denominator_count < selected_candidate_count`;
- `selected_candidate_count > evaluated_candidate_count`;
- `full_universe_claim = true` without denominator proof.

## 3. Required Temporal Checks

Validator must fail when:

- `as_of_utc` is after the declared decision timestamp in a state-builder join;
- full-session daily values are used for intraday decisions without explicit
  intraday cutoff policy;
- `market_cap_asof_date` is after `session_date`;
- `source_snapshot_received_at_utc` is after `as_of_utc` without live latency
  annotation.

## 4. Required Scanner Definition Checks

Validator must fail when:

- `scanner_definition_id` is missing;
- filter predicates are not versioned;
- ranking metric is missing;
- `scanner_mode` is not one of:

```text
historical_replay
live_snapshot
manual_research_seed
vendor_scanner_snapshot
```

- manual rows do not declare `scanner_mode = manual_research_seed`;
- top-N rows do not preserve `rank_metric` and `rank_metric_value`.

For governed v0.1 scanner definitions, validator must also fail when:

- `scanner_definition_id = trade_station_like_scanner_v0_1` does not preserve
  the operational hard filters:

```text
market_cap_usd < 100000000
volume_today > 500000
0.5 < last_price <= 20
rank by pct_chg_1d desc
top_n = 25
```

- `scanner_definition_id = broad_in_play_discovery_scanner_v0_1` treats
  `volume_today > 500000` as a universal hard inclusion filter;
- `scanner_definition_id = broad_in_play_discovery_scanner_v0_1` requires
  `% change 1D` as the only way to enter the candidate set;
- selected broad-discovery rows have empty `candidate_reasons`;
- `candidate_reason_count` does not match the persisted reasons;
- a row is marked `selected_broad_discovery = true` without at least one
  broad in-play threshold reason or governed broad selection-set rank reason;
- a row is marked `selected_trade_station_like_top25 = true` without preserving
  `rank_pct_chg_1d` or equivalent rank metadata.

Governed config paths:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

## 5. Required Quality Checks

Validator must mark rows as blocked or review when:

- price is missing or non-positive;
- volume is missing or negative;
- market cap source is stale beyond declared policy;
- instrument identity does not match temporally;
- session date is not a valid trading session;
- source component quality gate is blocked.

## 6. Required Prohibition Checks

Validator must fail if any column namespace or column name contains:

```text
outcome
label
reward
action
policy
fill
pnl
future
strategy_decision
```

unless the column is explicitly a boolean prohibition/quality flag such as
`contains_future_information_without_event_filter`.

## 7. Required Output Evidence

A materialization test must write:

- row count;
- selected/evaluated/denominator counts;
- duplicate-grain count;
- blocked/review/pass counts;
- scanner definitions observed;
- top-N distribution;
- missing source counts;
- `full_universe_claim` distribution;
- sample recomputation evidence for at least one scanner definition.
- comparison evidence between `trade_station_like_scanner_v0_1` and
  `broad_in_play_discovery_scanner_v0_1`, including candidates detected by
  broad discovery but not by the TradeStation-like filter.
- counts of candidates excluded only because `volume_today <= 500000`.
- counts of candidates excluded only because they were not top-N by
  `pct_chg_1d`.

## 8. Promotion Gate

The table may not be promoted until:

- schema contract exists;
- dataset contract exists;
- registry entry exists;
- consumption policy exists;
- validators are implemented;
- materializer writes manifest and summary;
- isolated tests pass;
- at least one controlled historical replay evidence pack exists.

Current builder smoke evidence:

```text
builder: scripts/materialize_daily_scanner_candidates_table.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
controlled_replay: C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

This evidence satisfies builder smoke only. The full validator suite against an
official candidate output is still pending.
