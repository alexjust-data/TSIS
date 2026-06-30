# Daily Scanner Candidates Table Consumption Policy `v0_1`

## 1. Scope

Dataset target:

```text
daily_scanner_candidates_table_v0_1
```

Current status:

```text
contract_defined_not_materialized
```

## 2. Permitted Meaning

Permitted meaning after materialization:

```text
declared scanner candidate set at a declared session/as-of time
```

Forbidden meaning:

```text
complete market state, complete tradable universe, label, reward, strategy
signal, execution truth or live automation authority
```

## 3. Required Cutoff Rule

Consumers must respect:

```text
as_of_utc <= decision_timestamp_utc
```

If a scanner row uses full-session daily values, it may only support decisions
after the session close unless the builder declares an intraday cutoff policy.

## 4. Consumer Rules

### Scanner Definition Semantics

Consumers must distinguish:

```text
trade_station_like_scanner_v0_1
  -> operational visibility replay

broad_in_play_discovery_scanner_v0_1
  -> broad research discovery
```

`trade_station_like_scanner_v0_1` may be used to ask:

```text
What would the operator likely have seen in the operational hot list?
```

`broad_in_play_discovery_scanner_v0_1` may be used to ask:

```text
What was becoming in-play before the narrow operational scanner necessarily saw it?
```

No consumer may collapse these into one meaning.

For `scanner_framework_v0_2`, consumers must instead use:

```text
base_in_play_universe_scanner_v0_2
  -> common smallcap <100M denominator

trade_station_like_profile_v0_2
  -> operational visibility replay

relative_volume_profile_v0_2
percent_change_profile_v0_2
dollar_volume_tradability_profile_v0_2
das_research_profile_v0_2
  -> governed research/tradability profiles inside the same denominator
```

Rules:

- `volume_today >= 500000` may only be interpreted as the
  `trade_station_like_profile_v0_2` hard filter.
- `market_cap_usd < 100000000` is the common base hard filter.
- `float` must not be used as a filter until a point-in-time source is
  governed and validated.
- `selected_broad_discovery` is deprecated for v0.2 consumers; prefer
  `selected_das_research_profile`.
- No profile flag is a strategy signal, state label, reward, fill or PnL.

### Event Discovery

May use validated rows to reconstruct which tickers were in play under a
declared scanner definition.

### Strategy Research / DAS

DAS may consume rows as candidate seeds for an experimental table such as:

```text
das_candidate_state_table_experimental
```

Required interpretation:

```text
scanner row = where to look
DAS state row = what DAS/frontside state appeared inside that candidate
```

DAS must preserve whether the candidate came from operational visibility,
broad discovery or both. A ticker discovered by the broad scanner must not be
reported as something the human operator necessarily saw in the
TradeStation-like scanner.

### Market State Builder

May use rows as candidate seeds only when:

```text
valid_for_market_state_seed_candidate = true
scanner_replayable = true
contains_future_information_without_event_filter = false
```

The state builder must still pull historical context, lookbacks, quality gates
and event-window microstructure from governed components.

### ML

May not consume the table directly as `X` unless a later feature contract
explicitly allows scanner-derived features.

Default:

```text
valid_for_ml_feature_candidate = false
```

### Offline RL

May not consume scanner rows directly as RL states.

Default:

```text
valid_for_rl_state_candidate = false
```

RL must consume composed state/transition/reward datasets after separate
contracts exist.

### Backtest

May use scanner rows as candidate-set reconstruction, not as execution truth.

### Live

May not use this table as live automation authority unless a separate live
latency/source contract exists.

## 5. Required Joins

Consumers that need a real state must join through governed builders to:

- `instrument_master`;
- `market_calendar`;
- `master_daily_table`;
- `master_intraday_bar_table` where scoped/legal;
- `event_windows_table`;
- `microstructure_features_table` where event windows exist;
- `short_context_table`;
- `regime_context_table`;
- `news_context_table`;
- `short_sale_constraints_table` when materialized.

## 6. Final Rule

`daily_scanner_candidates_table` tells TSIS where to look.

It does not tell TSIS what the full market state is.
