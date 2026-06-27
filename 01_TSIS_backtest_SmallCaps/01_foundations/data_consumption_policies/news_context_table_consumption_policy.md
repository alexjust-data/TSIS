# News Context Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
news_context_table_v0_1
```

## 2. Permitted Meaning

This table is a `published_utc`-aware news context component.

Permitted meaning:

```text
historical vendor news context available from published_utc
```

Forbidden meaning:

```text
proof that the news caused a price move
```

## 3. Required As-Of Join

Consumers must select rows using:

```text
published_utc <= event/decision cutoff
```

For intraday joins, consumers must convert timestamps to the relevant market
timezone and preserve ordering against the event window.

No consumer may join by calendar date alone and call the result pre-event
context.

## 4. Required Gates

Primary context candidates require:

```text
valid_for_event_context_candidate = true
requested_ticker_in_payload_tickers = true
instrument_identity_temporal_match = true
```

Rows with:

```text
ticker_attribution_state = review_multi_ticker_attributed
```

may be used only with explicit attribution handling. They are valid context
candidates, but not deterministic ticker-causal proof.

Rows in `review_no_temporal_identity` may be used only for:

- coverage diagnostics;
- identity-resolution review;
- forensic review;
- robustness checks with explicit masks.

## 5. ML/RL Boundary

`valid_for_ml_feature_candidate = true` means:

```text
this row may enter a feature set only after an external as-of builder selects it legally
```

It does not mean:

- direct `ml_primary` readiness;
- direct RL state/action/reward readiness;
- article caused the move;
- low-latency live availability.

`valid_for_rl_training_direct` is false for every v0.1 row.

## 6. Live Alert Boundary

`news_context_table_v0_1` is historical/contextual.

It is separate from:

```text
real_time_corporate_event_alerts_table
```

which must carry live `received_utc`, feed/vendor lineage and latency
measurement before it can support real-time offering/news alerts.

## 7. Final Rule

`news_context_table` is a component of state, not the state itself.

The future event/market-state builder must still compose:

```text
instrument + calendar + daily/intraday + microstructure + fundamentals + news + short + regime
```

under a single decision-time cutoff.
