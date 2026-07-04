# Daily Scanner Candidates Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: daily_scanner_candidates_table_v0_1
family: data_foundation_outputs
class: candidate_generation_table
grain: scanner_run_id + scanner_definition_id + session_date + as_of_utc + instrument_id
status: contract_defined_not_materialized
```

## 2. Purpose

`daily_scanner_candidates_table` answers:

```text
Which instruments were in play under this declared scanner definition, at this
session/as-of time, and why?
```

It does not answer:

- what the complete market state was;
- what strategy should trade;
- what outcome happened later;
- whether a fill was possible;
- whether a row is valid for ML/RL training by itself.

## 3. Required Relationship To Market State

This table is an input to future state construction:

```text
daily_scanner_candidates_table
-> governed candidate set
-> market_state_table builder pulls full-history context and event-window data
-> event_state_table binds the state to an event definition/window
```

It must obey:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

The scanner row can seed the state builder, but it is not the state.

## 4. Source Components

Historical replay candidates may derive from:

```text
instrument_master_v0_1
market_calendar_v0_1
master_daily_table_v0_1
master_intraday_bar_table_v0_1 where legal and scoped
fundamentals_asof_table_v0_1 where market-cap/float context is legal
short_context_table_v0_1 where source lag/as-of rules are legal
regime_context_table_v0_1 where regime context is legal
news_context_table_v0_1 for catalyst-aware variants
```

Live candidates require separate source and latency contracts before promotion:

```text
broker_live_scanner
vendor_market_snapshot
broker_api_snapshot
```

## 5. Current Scope

```text
materialized: false
official_materialized: false
builder_implemented: true
controlled_replay_exists: true
full_universe_claim: false
ml_feature_direct: false
rl_state_direct: false
live_downstream_authority: false
```

This contract defines the future official dataset. A controlled candidate replay
exists, but it is not the official E-root materialization:

```text
builder: scripts/materialize_daily_scanner_candidates_table.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
latest_controlled_replay: C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

The replay is evidence of builder shape and scanner comparison only.

`v0.2` controlled candidate implementation exists as historical intermediate
evidence:

```text
builder: scripts/materialize_daily_scanner_candidates_table_v0_2.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_2.py
framework: 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_2.md
target_contract: 01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_2.md
```

`v0.2` changes the scanner model from two independent scanner definitions to:

```text
base_in_play_universe_scanner_v0_2 + governed profile flags
```

The stable identifier remains `base_in_play_universe_scanner_v0_2`, but the
contractual meaning is:

```text
base_eligible_smallcap_denominator
```

It is the denominator of common-stock smallcaps eligible for observation, not
proof that every row is already in-play. Profile flags are parallel markers over
that denominator, not sequential filters.

This is a candidate replay implementation only. It does not promote an
official E-root dataset and does not authorize direct ML/RL/live consumption.

`v0.3` controlled candidate implementation is the active forward path for
in-play momentum semantics:

```text
builder: scripts/materialize_daily_scanner_candidates_table_v0_3.py
test: tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder_v0_3.py
framework: 01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_3.md
target_contract: 01_foundations/module_contracts/outputs/daily_scanner_candidates_table_target_contract_v0_3.md
```

`v0.3` changes the scanner model to:

```text
base_eligible_smallcap_denominator_v0_3
-> in_play_momentum_candidate_denominator_v0_3
-> strategy overlays
```

The key selected field is:

```text
selected_in_play_momentum_candidate
```

It requires base eligibility, a >=50% move under the declared daily proxy, and
minimum volume/tradability. It is still not a market state, label, reward,
strategy signal or execution truth.

## 6. Required Scanner Definition

Every materialization must include a versioned scanner definition containing:

- universe definition;
- filter predicates;
- ranking metric;
- `top_n` behavior;
- data source and price view;
- intraday/as-of timestamp policy;
- market-cap/float source and lag;
- treatment of missing values;
- quality gates;
- replay/live mode.

Scanner definitions must be stored as governed config or documented in the run
manifest. They must not live only inside notebook cells or prompts.

For v0.2 and later:

- generic observation profiles may select or rank denominator rows, but must not
  redefine the denominator;
- strategy overlays may consume scanner rows, but must write separate lineage
  and cannot be hidden inside the Data Foundation scanner;
- `relative_volume` requires intraday/as-of acceleration semantics before
  promotion;
- `percent_change` requires a declared minimum move threshold before top-N
  ranking;
- `dollar_volume` is tradability/economic activity, not alpha;
- DAS-specific filters belong in a DAS strategy overlay or experimental state
  table, not as final Data Foundation scanner doctrine.
- for v0.3 and later, strategy-specific filters must not be hidden in the
  global scanner; use `selected_in_play_momentum_candidate` as the common
  in-play denominator and add strategy overlays downstream.

## 6.1 Governed Scanner Definitions v0.1

The initial governed scanner framework is:

```text
01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

Versioned configs:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

Required interpretation:

```text
trade_station_like_scanner_v0_1
  = operational visibility replay

broad_in_play_discovery_scanner_v0_1
  = broad research discovery / late-arrival-bias protection
```

`volume_today > 500000` is a hard filter only for
`trade_station_like_scanner_v0_1`.

`broad_in_play_discovery_scanner_v0_1` must preserve candidate reasons such as
volume acceleration, RVOL-to-time, after-hours breakout, premarket new high,
prior-day high reclaim, range expansion, news context and halt/reopen context
when source fields are available.

Rows from either scanner are still candidate rows. They are not strategy
signals, market states, labels, outcomes, rewards or execution truth.

## 7. Prohibited Semantics

The table must not:

- claim top-N candidates are the full tradable universe;
- hide manual ticker selection as scanner output;
- contain labels, rewards, PnL, fills or strategy decisions;
- use post-close full-session values for pre-close decisions without explicit
  intraday cutoff policy;
- become the primary ML/RL training table without composition into
  `market_state_table`.

## 8. Allowed Consumers

Allowed after materialization and validation:

- event discovery;
- scanner replay audits;
- candidate-set denominator analysis;
- market-state builder input;
- event-state builder input;
- research sampling lineage.

Not allowed by this contract:

- direct ML feature table;
- direct RL state table;
- backtest execution authority;
- live trading automation authority.

## 9. Change Policy

Version bump required when:

- scanner grain changes;
- scanner predicates or ranking semantics change;
- source classes change;
- live sources become authoritative;
- scanner rows become valid ML/RL features;
- denominator/universe semantics change.
