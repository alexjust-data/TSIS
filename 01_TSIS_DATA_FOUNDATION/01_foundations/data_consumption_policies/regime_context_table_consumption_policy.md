# Regime Context Table Consumption Policy `v0_1`

## 1. Scope

Dataset:

```text
regime_context_table_v0_1
```

## 2. Permitted Meaning

This table is session-level market-regime context derived from
`regime_indicators_v0_1` minute bars.

Permitted meaning:

```text
regime proxy context known after the proxy session aggregate is legally
available to the consumer
```

Forbidden meaning:

```text
same-session intraday causal state
```

## 3. Required As-Of Join

Consumers must select rows with:

```text
as_of_utc <= event/session decision cutoff
```

Because v0.1 rows are session-close aggregates, a consumer must not use the
same session's completed row for an intraday decision before the session close.

Required flags:

```text
requires_asof_filter = true
contains_future_information_without_event_filter = true
same_session_intraday_causal_claim_allowed = false
```

## 4. Required Gates

Primary context candidates require:

```text
valid_for_event_context_candidate = true
regime_quality_state = good_minute_aggregated_regime_context
market_calendar_covered = true
built_from_minute_parquet = true
built_from_blocked_day_parquet = false
intraday_regime_features_source_included = false
```

Rows in these states require review or explicit masks:

- `review_no_market_calendar_session`
- `review_source_bar_integrity`
- `review_sparse_minute_coverage`

## 5. Source-Specific Rules

### `minute.parquet`

Included source:

```text
E:/TSIS/data/regime_indicators/**/minute.parquet
```

Consumers must preserve:

- `source_file_relative_path`
- `source_proxy_family`
- `regime_proxy_role`
- coverage fields;
- source bar-integrity fields;
- `timestamp_timezone_state`.

### `day.parquet`

Blocked source:

```text
E:/TSIS/data/regime_indicators/**/day.parquet
```

No consumer may infer that this output repaired or consumed the blocked daily
files. The flags must remain:

```text
daily_source_files_blocked = true
built_from_blocked_day_parquet = false
```

### `intraday_regime_features`

Excluded source:

```text
E:/TSIS/data/intraday_regime_features
```

No consumer may infer that this output contains those pilot features.

## 6. ML/RL Boundary

`valid_for_ml_feature_candidate = true` means:

```text
this row may enter a feature set only after an external as-of/state builder
selects it legally
```

It does not mean:

- direct `ml_primary` readiness;
- direct RL state/action/reward readiness;
- live regime state;
- intraday cutoff correctness;
- execution truth.

`valid_for_rl_training_direct` is false for every v0.1 row.

## 7. Final Rule

`regime_context_table` is a component of state, not the state itself.

The future event/market-state builder must still compose:

```text
instrument + calendar + daily/intraday + microstructure + fundamentals + news
+ short + short-sale constraints + regime
```

under one declared decision-time cutoff, lag model and leakage policy.
