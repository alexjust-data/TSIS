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

For governed v0.2 scanner definitions, validator must also fail when:

- `scanner_definition_id` is not `base_in_play_universe_scanner_v0_2`;
- the run treats `base_in_play_universe_scanner_v0_2` as proof that all rows
  are already in-play instead of as the `base_eligible_smallcap_denominator`;
- v0.2 rows omit any required profile flag:

```text
selected_trade_station_like_profile
selected_relative_volume_profile
selected_percent_change_profile
selected_dollar_volume_tradability_profile
selected_das_research_profile
selected_any_profile
scanner_semantic_alignment_version
scanner_profile_semantics
profiles_are_sequential_funnel
relative_volume_profile_status
percent_change_min_threshold_applied
percent_change_min_threshold_pct
dollar_volume_profile_semantic_role
das_research_profile_status
```

- `market_cap_max_filter` is not `100000000`;
- a row is marked base eligible while `market_cap_usd >= 100000000`;
- `selected_trade_station_like_profile = true` while
  `volume_today < 500000`;
- `selected_any_profile = true` while all individual profile flags are false;
- any individual profile flag is true while `all_filters_passed = false`;
- any profile count is documented or emitted as a sequential funnel count
  unless a separate funnel contract exists;
- `scanner_profile_semantics` differs from
  `parallel_flags_not_sequential_filters`;
- `profiles_are_sequential_funnel` is true without a separate explicit funnel
  contract;
- `selected_relative_volume_profile = true` is promoted without intraday/as-of
  acceleration semantics or an explicit provisional/unavailable marker;
- `relative_volume_profile_status = unavailable_without_intraday_asof` and
  `selected_relative_volume_profile = true`;
- `selected_percent_change_profile = true` is promoted without a declared
  minimum percent-change threshold before top-N ranking;
- `percent_change_min_threshold_applied` is false or
  `percent_change_min_threshold_pct` is null in a v0.2 contract-aligned replay;
- `selected_dollar_volume_tradability_profile = true` is interpreted as alpha
  or setup quality rather than tradability/economic activity;
- `dollar_volume_profile_semantic_role` differs from
  `tradability_not_alpha`;
- `selected_das_research_profile = true` is interpreted as a mature DAS
  scanner rather than provisional strategy-overlay lineage;
- `das_research_profile_status` differs from
  `provisional_strategy_overlay_seed_not_final_scanner`;
- `float_filter_state` differs from
  `not_used_until_point_in_time_float_source_exists` before a governed float
  source contract exists;
- `selected_broad_discovery` is interpreted as an active v0.2 scanner rather
  than a deprecated compatibility alias;
- profile configs are missing from:

```text
configs/data_foundation_outputs/scanner_definitions/base_in_play_universe_scanner_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/relative_volume_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/percent_change_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/dollar_volume_tradability_profile_v0_2.yaml
configs/data_foundation_outputs/scanner_definitions/das_research_profile_v0_2.yaml
```

For governed v0.3 scanner definitions, validator must also fail when:

- `scanner_definition_id` is not `base_eligible_smallcap_denominator_v0_3`;
- `selected_in_play_momentum_candidate = true` while `all_filters_passed = false`;
- `selected_in_play_momentum_candidate = true` while all of these are below
  threshold:

```text
daily_high_vs_prev_close_pct < 50
pct_chg_1d < 50
gap_pct < 50
```

- `selected_in_play_momentum_candidate = true` while
  `in_play_volume_tradability_passed = false`;
- `percent_change_min_threshold_pct` is not `50.0` for the v0.3 controlled
  replay;
- `selected_das_research_profile = true`;
- `das_research_profile_status` differs from
  `removed_from_global_scanner_strategy_overlay_only`;
- `selected_any_profile` differs from `selected_in_play_momentum_candidate`;
- `in_play_detection_scope = daily_eod_proxy` is interpreted as segment-level
  frontside timing;
- segment fields are populated without an intraday segment builder manifest;
- float is used as a hard filter before point-in-time source validation.

Governed config paths:

```text
configs/data_foundation_outputs/scanner_definitions/base_eligible_smallcap_denominator_v0_3.yaml
configs/data_foundation_outputs/scanner_definitions/in_play_momentum_candidate_denominator_v0_3.yaml
configs/data_foundation_outputs/scanner_definitions/trade_station_like_profile_v0_3.yaml
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
