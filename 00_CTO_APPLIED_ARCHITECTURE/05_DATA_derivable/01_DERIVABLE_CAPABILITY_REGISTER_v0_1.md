# Derivable Capability Register v0.1

Status: `compact_capability_register_v0_2_atomic_rows`
Date: `2026-07-20`
Knowledge state: `secondary_summary`

## Rol

Este registro resume, de forma compacta, las capacidades de derivacion que TSIS puede calcular o gobernar desde RAW data o fuentes gobernadas.

No es un schema.
No es un feature store.
No admite Information Objects.
No decide Market State ni Event State.

## Regla Atomica

```text
Una fila = una capacidad derivable canonica.
```

Una fila puede ser parametrica, pero no debe mezclar capacidades distintas.

Ejemplo correcto:

```text
intraday__move_speed_W
```

porque `W` es una variante declarable.

Ejemplo incorrecto:

```text
intraday__shape_pace_W
```

porque mezcla speed, acceleration, pullback, retrace y volume pace.

## Registro

| derivable_id | canonical_output | source | required_fields | derivation_definition | variant_required | required_variant_fields | legal_cutoff | quality_governance_gate | status | known_materializations |
|---|---|---|---|---|---|---|---|---|---|---|
| `daily__open_price` | `open` | OHLCV Daily | open | daily open price as source observable | no | n/a | `yes_after_session_open` | daily row integrity, price_view policy | `existing` | `004_master_daily_table` |
| `daily__high_price` | `high` | OHLCV Daily | high | daily high price as source observable | no | n/a | `yes_after_market_close` | no pre-close final high use | `existing` | `004_master_daily_table` |
| `daily__low_price` | `low` | OHLCV Daily | low | daily low price as source observable | no | n/a | `yes_after_market_close` | no pre-close final low use | `existing` | `004_master_daily_table` |
| `daily__close_price` | `close` | OHLCV Daily | close | daily close price as source observable | no | n/a | `yes_after_market_close` | close availability | `existing` | `004_master_daily_table` |
| `daily__volume` | `volume` | OHLCV Daily | volume | final daily volume as source observable | no | n/a | `yes_after_market_close` | non-negative volume | `existing` | `004_master_daily_table` |
| `daily__vwap` | `vwap` | OHLCV Daily | vwap | daily VWAP as source observable when present | no | n/a | `yes_after_market_close` | vwap validity and source policy | `existing` | `004_master_daily_table` |
| `daily__transaction_count` | `transaction_count` | OHLCV Daily | transaction_count | daily transaction count as source observable | no | n/a | `yes_after_market_close` | non-negative count | `existing` | `004_master_daily_table` |
| `daily__prior_close` | `prior_close` | OHLCV Daily | prior close | previous closed session reference | no | n/a | `yes_with_asof_cutoff` | prior valid session, price_view policy | `existing` | `004_master_daily_table` |
| `daily__gap_pct` | `gap_pct` | OHLCV Daily | open, prior_close | `(open / prior_close) - 1` | no | n/a | `yes_after_session_open` | open and prior_close valid | `existing` | `004_master_daily_table` |
| `daily__daily_return_pct` | `daily_return_pct` | OHLCV Daily | close, prior_close | `(close / prior_close) - 1` | no | n/a | `yes_after_market_close` | close and prior_close valid | `existing` | `004_master_daily_table` |
| `daily__intraday_return_pct` | `intraday_return_pct` | OHLCV Daily | close, open | `(close / open) - 1` | no | n/a | `yes_after_market_close` | open and close valid | `existing` | `004_master_daily_table` |
| `daily__daily_range_pct` | `daily_range_pct` | OHLCV Daily | high, low | `(high / low) - 1` | no | n/a | `yes_after_market_close` | high/low valid, low > 0 | `existing` | `004_master_daily_table` |
| `daily__dollar_volume` | `dollar_volume` | OHLCV Daily | close, volume | `close * volume` | no | n/a | `yes_after_market_close` | price and volume valid | `existing` | `004_master_daily_table` |
| `daily__volume_20d_avg` | `volume_20d_avg` | OHLCV Daily | volume | average volume over prior 20 valid closed sessions | no | n/a | `yes_with_asof_cutoff` | prior sessions only | `existing` | `004_master_daily_table` |
| `daily__rvol_20d` | `rvol_20d` | OHLCV Daily | volume, volume_20d_avg | `volume / volume_20d_avg` | no | n/a | `yes_after_market_close` | denominator > 0; current final volume only after close | `existing` | `004_master_daily_table` |
| `daily__volume_Nd_avg` | `volume_Nd_avg` | OHLCV Daily | volume | average volume over prior N valid closed sessions | yes | N, min_periods, valid-row policy, price_view | `yes_with_asof_cutoff` | prior sessions only | `requires_variant` | not fixed here |
| `daily__rvol_Nd` | `rvol_Nd` | OHLCV Daily | volume, volume_Nd_avg | `volume / volume_Nd_avg` | yes | N, min_periods, denominator policy | `yes_after_market_close` | current final volume only after close | `requires_variant` | not fixed here |
| `daily__dollar_volume_Nd_avg` | `dollar_volume_Nd_avg` | OHLCV Daily | dollar_volume | average dollar volume over prior N valid sessions | yes | N, min_periods, dollar_volume formula id | `yes_with_asof_cutoff` | prior sessions only | `requires_variant` | not fixed here |
| `daily__volatility_Nd` | `daily_volatility_Nd` | OHLCV Daily | declared return | dispersion of declared daily return over prior N sessions | yes | N, return input, statistic, min_periods | `yes_with_asof_cutoff` | prior sessions only | `requires_variant` | not fixed here |
| `daily__range_Nd` | `daily_range_Nd` | OHLCV Daily | declared range metric | aggregate declared range over prior N sessions | yes | N, range input, statistic, min_periods | `yes_with_asof_cutoff` | prior sessions only | `requires_variant` | not fixed here |
| `intraday__bar_open_price` | `open` | OHLCV 1m | open | closed 1m bar open | no | n/a | `yes_after_bar_close` | closed bar only | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_high_price` | `high` | OHLCV 1m | high | closed 1m bar high | no | n/a | `yes_after_bar_close` | closed bar only | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_low_price` | `low` | OHLCV 1m | low | closed 1m bar low | no | n/a | `yes_after_bar_close` | closed bar only | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_close_price` | `close` | OHLCV 1m | close | closed 1m bar close | no | n/a | `yes_after_bar_close` | closed bar only | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_volume` | `volume` | OHLCV 1m | volume | closed 1m bar volume | no | n/a | `yes_after_bar_close` | volume quality | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_vwap` | `vwap` | OHLCV 1m | vwap, close | closed 1m bar VWAP or governed fallback | no | n/a | `yes_after_bar_close` | vwap/close fallback policy | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__bar_transaction_count` | `transaction_count` | OHLCV 1m | transaction_count | closed 1m bar transaction count | no | n/a | `yes_after_bar_close` | count policy | `existing` | `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate` |
| `intraday__quote_guarded_repair_state` | `repair_state` | OHLCV 1m + repair manifest | repair_state, repair_reason, run_id | quote-guarded overlay lineage/quality state | no | n/a | `yes_with_asof_cutoff` | repair manifest scope | `existing` | `013_ohlcv_1m_quote_guarded` |
| `intraday__session_volume_to_time` | `session_volume_to_time` | OHLCV 1m | closed bar volume | cumulative volume from session start to t | no | n/a | `yes_after_bar_close` | bars <= t | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__session_dollar_volume_to_time` | `session_dollar_volume_to_time` | OHLCV 1m | volume, vwap, close | cumulative dollar volume proxy from session start to t | no | n/a | `yes_after_bar_close` | vwap/close policy, bars <= t | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__bars_observed_to_time` | `bars_observed_to_time` | OHLCV 1m | closed bars | count observed closed bars through t | no | n/a | `yes_after_bar_close` | closed bars <= t | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__high_so_far` | `high_so_far` | OHLCV 1m | high | max high over closed bars through t | no | n/a | `yes_after_bar_close` | invalid bars filtered | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__low_so_far` | `low_so_far` | OHLCV 1m | low | min low over closed bars through t | no | n/a | `yes_after_bar_close` | invalid bars filtered | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__range_so_far_ratio` | `range_so_far_ratio` | OHLCV 1m | high_so_far, low_so_far | `(high_so_far / low_so_far) - 1` | no | n/a | `yes_after_bar_close` | denominator > 0 | `formula_defined` | `014_master_intraday_bar_table_candidate` |
| `intraday__return_vs_prior_close_ratio` | `return_vs_prior_close_ratio` | OHLCV 1m + Daily | price_ref, prior_close | `(price_ref / prior_close) - 1` | yes | price_ref | `yes_after_bar_close` | prior_close known by t | `formula_defined` | `014_master_intraday_bar_table_candidate`, future state builder |
| `intraday__return_vs_session_open_ratio` | `return_vs_session_open_ratio` | OHLCV 1m | price_ref, session_open | `(price_ref / session_open) - 1` | yes | price_ref | `yes_after_bar_close` | session open known by t | `formula_defined` | `014_master_intraday_bar_table_candidate`, future state builder |
| `intraday__return_vs_segment_open_ratio` | `return_vs_segment_open_ratio` | OHLCV 1m | price_ref, segment_open | `(price_ref / segment_open) - 1` | yes | price_ref, segment policy | `yes_after_bar_close` | segment open known by t | `formula_defined` | future state builder |
| `intraday__vwap_distance_ratio` | `vwap_distance_ratio` | OHLCV 1m | close, vwap_ref | `(close / vwap_ref) - 1` | yes | vwap_ref, window, denominator policy | `yes_after_bar_close` | vwap_ref built from bars <= t | `requires_variant` | candidate |
| `intraday__bars_expected_to_time` | `bars_expected_to_time` | Calendar + OHLCV 1m | market calendar, t, bar_size | expected closed bars through t | yes | session/segment scope, bar_size | `yes_after_bar_close` | market calendar required | `formula_defined` | state builder candidate |
| `intraday__missing_bar_count_to_time` | `missing_bar_count_to_time` | Calendar + OHLCV 1m | expected bars, observed bars | `max(expected - observed, 0)` | yes | session/segment scope | `yes_after_bar_close` | expected denominator declared | `formula_defined` | state builder candidate |
| `intraday__missing_bar_ratio_to_time` | `missing_bar_ratio_to_time` | Calendar + OHLCV 1m | missing bars, expected bars | `missing_bar_count / expected` | yes | session/segment scope | `yes_after_bar_close` | expected > 0 | `formula_defined` | state builder candidate |
| `intraday__move_speed_W` | `move_speed_W` | OHLCV 1m | return_ref(t), return_ref(t-W) | delta return over elapsed minutes | yes | W, return_ref, price_ref, session/segment scope | `yes_after_bar_close` | bars <= t, min_periods | `requires_variant` | candidate |
| `intraday__move_acceleration_W` | `move_acceleration_W` | OHLCV 1m | move_speed_W | change in move speed or declared second difference | yes | W, speed formula id, elapsed policy | `yes_after_bar_close` | bars <= t, min_periods | `requires_variant` | candidate |
| `intraday__pullback_ratio_W` | `pullback_ratio_W` | OHLCV 1m | high_ref, current_price_ref | distance from high/ref to current price | yes | W, high_ref, current_price_ref | `yes_after_bar_close` | bars <= t | `requires_variant` | candidate |
| `intraday__retrace_ratio_W` | `retrace_ratio_W` | OHLCV 1m | move anchor, current_price_ref | retrace from declared move anchor to current price | yes | W, anchor policy, price_ref | `yes_after_bar_close` | bars <= t, anchor legal | `requires_variant` | candidate |
| `intraday__volume_pace_W` | `volume_pace_W` | OHLCV 1m + Daily baseline | volume_to_time, expected baseline | volume_to_time / expected_volume_to_time_baseline | yes | W, baseline universe, historical sessions, min_periods | `yes_after_bar_close` | baseline prior/as-of only | `requires_variant` | candidate |
| `intraday__dollar_volume_pace_W` | `dollar_volume_pace_W` | OHLCV 1m + Daily baseline | dollar_volume_to_time, expected baseline | dollar_volume_to_time / expected_dollar_volume_to_time_baseline | yes | W, baseline formula, historical sessions, min_periods | `yes_after_bar_close` | baseline prior/as-of only | `requires_variant` | candidate |
| `trades__price` | `trade_price` | Trades | price | trade print price | no | n/a | `yes_at_source_timestamp` | trade timestamp/price validity | `existing` | raw trades, `015_microstructure_features_table_candidate` |
| `trades__size` | `trade_size` | Trades | size | trade print size | no | n/a | `yes_at_source_timestamp` | positive size policy | `existing` | raw trades, `015_microstructure_features_table_candidate` |
| `trades__trade_count_WINDOW` | `trade_count_WINDOW` | Trades | trade timestamp | count trades in legal window | yes | window, session filter, min_rows | `yes_with_closed_window` | window_end <= t | `requires_variant` | `015_microstructure_features_table_candidate` |
| `trades__trade_rate_WINDOW` | `trade_rate_WINDOW` | Trades | trade_count, window_seconds | trade_count / window_seconds | yes | window, session filter, min_rows | `yes_with_closed_window` | window_end <= t | `requires_variant` | candidate |
| `trades__total_volume_WINDOW` | `trades_total_volume_WINDOW` | Trades | size | sum valid trade size in window | yes | window, session filter | `yes_with_closed_window` | valid size, window_end <= t | `existing` | `015_microstructure_features_table_candidate` |
| `trades__dollar_volume_WINDOW` | `trades_dollar_volume_WINDOW` | Trades | price, size | sum price * size in window | yes | window, session filter | `yes_with_closed_window` | valid price/size | `existing` | `015_microstructure_features_table_candidate` |
| `trades__size_median_WINDOW` | `trades_size_median_WINDOW` | Trades | size | median valid trade size in window | yes | window, min_rows | `yes_with_closed_window` | valid size | `existing` | `015_microstructure_features_table_candidate` |
| `trades__size_p90_WINDOW` | `trades_size_p90_WINDOW` | Trades | size | p90 valid trade size in window | yes | window, min_rows | `yes_with_closed_window` | valid size | `existing` | `015_microstructure_features_table_candidate` |
| `trades__odd_lot_ratio_pct_WINDOW` | `trades_odd_lot_ratio_pct_WINDOW` | Trades | size | count 0 < size < 100 / rows * 100 | yes | window, min_rows | `yes_with_closed_window` | valid size policy | `existing` | `015_microstructure_features_table_candidate` |
| `trades__duplicate_exact_ratio_pct_WINDOW` | `trades_duplicate_exact_ratio_pct_WINDOW` | Trades | timestamp, price, size, exchange, conditions | duplicated exact key ratio | yes | window, duplicate key policy | `yes_with_closed_window` | tape quality policy | `existing` | `015_microstructure_features_table_candidate` |
| `trades__off_regular_session_ratio_pct_WINDOW` | `trades_off_regular_session_ratio_pct_WINDOW` | Trades | trade timestamp | off regular session trade ratio | yes | window, session calendar | `yes_with_closed_window` | timestamp/timezone policy | `existing` | `015_microstructure_features_table_candidate` |
| `trades__invalid_price_rows_WINDOW` | `trades_invalid_price_rows_WINDOW` | Trades | price | count invalid trade price rows | yes | window, invalid rule | `yes_with_closed_window` | tape quality policy | `existing` | `015_microstructure_features_table_candidate` |
| `trades__invalid_size_rows_WINDOW` | `trades_invalid_size_rows_WINDOW` | Trades | size | count invalid trade size rows | yes | window, invalid rule | `yes_with_closed_window` | tape quality policy | `existing` | `015_microstructure_features_table_candidate` |
| `trades__bid_hit_ask_lift_WINDOW` | `bid_hit_ask_lift_WINDOW` | Trades + Quotes or conditions | trade price, conditions, bid/ask | classify bid-hit / ask-lift | yes | window, classifier, alignment policy | `yes_with_closed_window` | condition decode/alignment confidence | `candidate` | not official |
| `trades__signed_flow_WINDOW` | `signed_flow_WINDOW` | Trades + Quotes or conditions | price, size, side classification | signed traded volume/flow | yes | window, classifier, sign policy | `yes_with_closed_window` | classifier confidence | `candidate` | not official |
| `trades__aggressor_imbalance_WINDOW` | `aggressor_imbalance_WINDOW` | Trades + Quotes or conditions | signed flow | imbalance between buyer/seller initiated flow | yes | window, sign policy | `yes_with_closed_window` | classifier confidence | `candidate` | not official |
| `quotes__bid_price` | `bid_price` | Quotes L1 | bid_price | top-of-book bid price | no | n/a | `yes_at_source_timestamp` | quote timestamp/price validity | `existing` | raw quotes, `015_microstructure_features_table_candidate` |
| `quotes__ask_price` | `ask_price` | Quotes L1 | ask_price | top-of-book ask price | no | n/a | `yes_at_source_timestamp` | quote timestamp/price validity | `existing` | raw quotes, `015_microstructure_features_table_candidate` |
| `quotes__bid_size` | `bid_size` | Quotes L1 | bid_size | displayed bid size | no | n/a | `yes_at_source_timestamp` | depth validity | `existing` | raw quotes, `015_microstructure_features_table_candidate` |
| `quotes__ask_size` | `ask_size` | Quotes L1 | ask_size | displayed ask size | no | n/a | `yes_at_source_timestamp` | depth validity | `existing` | raw quotes, `015_microstructure_features_table_candidate` |
| `quotes__quote_count_WINDOW` | `quote_count_WINDOW` | Quotes L1 | quote timestamp | count quote rows in legal window | yes | window, min_rows | `yes_with_closed_window` | window_end <= t | `requires_variant` | `015_microstructure_features_table_candidate` |
| `quotes__quote_update_rate_WINDOW` | `quote_update_rate_WINDOW` | Quotes L1 | quote_count, window_seconds | quote_count / window_seconds | yes | window, min_rows | `yes_with_closed_window` | timestamp policy | `requires_variant` | candidate |
| `quotes__two_sided_rows_WINDOW` | `two_sided_rows_WINDOW` | Quotes L1 | bid, ask | count ask > 0 and bid > 0 | yes | window | `yes_with_closed_window` | two-sided quote policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__crossed_rows_WINDOW` | `crossed_rows_WINDOW` | Quotes L1 | bid, ask | count ask < bid for two-sided quotes | yes | window | `yes_with_closed_window` | quote quality policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__locked_rows_WINDOW` | `locked_rows_WINDOW` | Quotes L1 | bid, ask | count ask == bid for two-sided quotes | yes | window | `yes_with_closed_window` | quote quality policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__crossed_ratio_pct_all_rows_WINDOW` | `crossed_ratio_pct_all_rows_WINDOW` | Quotes L1 | crossed_rows, rows | crossed_rows / rows * 100 | yes | window | `yes_with_closed_window` | denominator policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__crossed_ratio_pct_two_sided_WINDOW` | `crossed_ratio_pct_two_sided_WINDOW` | Quotes L1 | crossed_rows, two_sided_rows | crossed_rows / two_sided_rows * 100 | yes | window | `yes_with_closed_window` | denominator policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__locked_ratio_pct_two_sided_WINDOW` | `locked_ratio_pct_two_sided_WINDOW` | Quotes L1 | locked_rows, two_sided_rows | locked_rows / two_sided_rows * 100 | yes | window | `yes_with_closed_window` | denominator policy | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__spread_bps_row` | `spread_bps` | Quotes L1 | bid, ask | `((ask - bid) / mid) * 10000` | no | n/a | `yes_at_source_timestamp` | valid ask > bid, mid > 0 | `formula_defined` | row formula / `015_microstructure_features_table_candidate` |
| `quotes__spread_bps_median_WINDOW` | `quotes_spread_bps_median_WINDOW` | Quotes L1 | spread_bps | median spread in window | yes | window, min_rows | `yes_with_closed_window` | valid spread rows | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__spread_bps_p90_WINDOW` | `quotes_spread_bps_p90_WINDOW` | Quotes L1 | spread_bps | p90 spread in window | yes | window, min_rows | `yes_with_closed_window` | valid spread rows | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__top_depth_mean_WINDOW` | `quotes_top_depth_mean_WINDOW` | Quotes L1 | bid_size, ask_size | mean bid_size + ask_size over two-sided rows | yes | window, min_rows | `yes_with_closed_window` | valid depth rows | `existing` | `015_microstructure_features_table_candidate` |
| `quotes__staleness_WINDOW` | `quote_staleness_WINDOW` | Quotes L1 | quote timestamps | time since last quote or max quote gap | yes | window, timezone, gap definition | `yes_with_closed_window` | timestamp units/sequence policy | `requires_variant` | candidate |
| `quotes__lifetime_WINDOW` | `quote_lifetime_WINDOW` | Quotes L1 | quote timestamps, sequence | duration of quote state before replacement | yes | window, sequence/timestamp policy | `yes_with_closed_window` | timestamp/sequence behavior | `requires_variant` | candidate |
| `trade_quote__alignment_lag_ms` | `alignment_lag_ms` | Trades + Quotes | trade timestamp, quote timestamp | lag between trade and matched quote reference | yes | clock, lag direction, matching policy | `yes_with_closed_window` | alignment policy | `candidate` | target 021 / 015 support |
| `trade_quote__alignment_confidence` | `alignment_confidence` | Trades + Quotes | matched trade/quote pair | confidence score for trade-quote alignment | yes | classifier/rule version | `yes_with_closed_window` | validation evidence | `candidate` | target 021 / 015 support |
| `trade_quote__effective_spread_bps_WINDOW` | `effective_spread_bps_WINDOW` | Trades + Quotes | trade price, mid/bid/ask | effective spread around aligned trade | yes | window, side/classifier, mid policy | `yes_with_closed_window` | no future midpoint misuse | `candidate` | not official |
| `trade_quote__realized_spread_bps_WINDOW` | `realized_spread_bps_WINDOW` | Trades + Quotes | trade price, later mid | realized spread at declared horizon | yes | horizon, side/classifier, future label role | `no_future_or_prohibited` for state | horizon uses future; role-separated outcome/research only | `candidate` | not official / outcome-style only |
| `trade_quote__price_impact_proxy_WINDOW` | `price_impact_proxy_WINDOW` | Trades + Quotes | price move, liquidity/volume proxy | declared price move divided by liquidity/volume proxy | yes | window, price_ref, liquidity_ref, sign policy | `yes_with_closed_window` | formula version, no fill/outcome leak | `candidate` | not official |
| `trade_quote__ofi_l1_WINDOW` | `ofi_l1_WINDOW` | Trades + Quotes | bid/ask price/size changes, trades | L1 order-flow imbalance proxy | yes | window, event ordering, formula version | `yes_with_closed_window` | L1 limitation, alignment | `candidate` | not official |
| `news__published_utc` | `published_utc` | News | published_utc | source publish timestamp | no | n/a | `yes_with_asof_cutoff` | news timestamp policy | `existing` | `010_news_context_table` |
| `news__as_of_utc` | `as_of_utc` | News | as_of_utc | governed availability timestamp | no | n/a | `yes_with_asof_cutoff` | as_of policy | `existing` | `010_news_context_table` |
| `news__article_count_WINDOW` | `article_count_WINDOW` | News | published_utc, ticker attribution | count eligible articles in window | yes | W, source filter, attribution scope | `yes_with_asof_cutoff` | published_utc <= t, attribution quality | `requires_variant` | candidate |
| `news__freshness_minutes` | `news_freshness_minutes` | News | latest published_utc, t | t - latest eligible published_utc | yes | source/filter scope | `yes_with_asof_cutoff` | latest article <= t | `requires_variant` | candidate |
| `news__keyword_flag` | `news_keyword_flag` | News | title, description, keywords | dictionary/string match flag | yes | dictionary version, field scope | `yes_with_asof_cutoff` | text known by publish/as_of | `requires_variant` | candidate |
| `news__sentiment_score` | `news_sentiment_score` | News | text fields | model/dictionary sentiment score | yes | model version, source scope | `yes_with_asof_cutoff` | no future revisions; model governance | `requires_variant` | candidate |
| `news__novelty_score` | `news_novelty_score` | News | current and prior articles | novelty/repetition against prior eligible news | yes | lookback, text model, source scope | `yes_with_asof_cutoff` | prior-only corpus | `requires_variant` | candidate |
| `fundamentals__filing_age_days` | `filing_age_days` | Fundamentals / SEC filings | filing_date/as_of_date, t | t - availability_date in days | no | n/a | `yes_with_asof_cutoff` | availability date <= t | `formula_defined` | `009_fundamentals_asof_table`, state builder candidate |
| `fundamentals__statement_recency_days` | `statement_recency_days` | Fundamentals / SEC filings | statement_available_date, t | t - statement_available_date in days | no | n/a | `yes_with_asof_cutoff` | statement availability <= t | `formula_defined` | `009_fundamentals_asof_table`, state builder candidate |
| `fundamentals__statement_value_FIELD` | `statement_value_FIELD` | Fundamentals / SEC filings | declared statement field | as-of value of declared statement field | yes | FIELD, statement_family, source_dataset_id | `yes_with_asof_cutoff` | PIT/as_of policy, source quality | `existing` | `009_fundamentals_asof_table` |
| `fundamentals__ratio_FORMULA` | `fundamental_ratio_FORMULA` | Fundamentals / SEC filings | statement values | declared financial ratio formula | yes | FORMULA, fields, statement scope, availability policy | `yes_with_asof_cutoff` | formula/version, source quality | `requires_variant` | candidate; financial quality may block some sources |
| `short__days_to_cover` | `days_to_cover` | Short | days_to_cover or short_interest, avg_daily_volume | source value or short_interest / avg_daily_volume | no | n/a | `yes_with_asof_cutoff` | source lag/as_of policy | `existing` | `011_short_context_table` |
| `short__short_volume_ratio` | `short_volume_ratio` | Short | short_volume, total_volume | short_volume / total_volume * 100 when recomputed | no | n/a | `yes_with_asof_cutoff` | denominator valid, source lag | `existing` | `011_short_context_table` |
| `short__short_interest_z_WINDOW` | `short_interest_z_WINDOW` | Short | days_to_cover or short_interest history | z-score vs prior history | yes | window, min_periods, input metric | `yes_with_asof_cutoff` | prior-only source lag | `requires_variant` | candidate |
| `short__borrow_availability_state` | `borrow_availability_state` | Borrow/vendor source | borrow availability fields | governed borrow availability state | yes | vendor/broker source, account scope | none | no governed source today | `blocked_no_source` | not materialized |
| `short__locate_state` | `locate_state` | Locate/broker source | locate approval/source | governed locate state | yes | broker/source, account scope | none | no governed source today | `blocked_no_source` | not materialized |
| `short__ssr_state` | `ssr_state` | SSR source | SSR trigger/source | governed short-sale restriction state | yes | source, trigger rule, as_of | none | no governed source today | `blocked_no_source` | not materialized |
| `halts__halt_type` | `halt_type` | Halts / SEC suspensions | halt_type, halt_code, halt_reason | governed halt classification | no | n/a | `yes_with_asof_cutoff` | event taxonomy availability | `existing` | `006_halts_table` |
| `halts__is_halted_at_t` | `is_halted_at_t` | Halts / SEC suspensions | halt_start, resume timestamp, t | halt_start <= t and resume is null or resume > t | no | n/a | `yes_with_asof_cutoff` | halt/resume known by t | `formula_defined` | state builder candidate |
| `halts__minutes_since_halt_start` | `minutes_since_halt_start` | Halts / SEC suspensions | halt_start, t | t - halt_start in minutes | no | n/a | `yes_with_asof_cutoff` | halt_start known by t | `formula_defined` | state builder candidate |
| `halts__minutes_since_resume` | `minutes_since_resume` | Halts / SEC suspensions | resume timestamp, t | t - resume in minutes | no | n/a | `yes_with_asof_cutoff` | resume known by t | `formula_defined` | state builder candidate |
| `reference__instrument_identity_asof` | `instrument_identity_asof` | Reference | ticker, instrument_id, security type, exchange | identity as-of context | yes | identity fields, as_of policy | `yes_with_asof_cutoff` | reference PIT policy | `existing` | `000_instrument_master` |
| `reference__lifecycle_state_asof` | `lifecycle_state_asof` | Reference | listing/delisting/lifecycle dates | instrument lifecycle state as-of t | yes | lifecycle fields, as_of policy | `yes_with_asof_cutoff` | reference PIT policy | `existing` | `000_instrument_master` |
| `reference__corporate_action_count_WINDOW` | `corporate_action_count_WINDOW` | Reference / corporate actions | action dates/types | count actions by type in window | yes | action_type, window, availability policy | `yes_with_asof_cutoff` | corporate action availability | `formula_defined` | `005_corporate_actions_table`, `004_master_daily_table` flags |
| `reference__corporate_action_recency_days` | `corporate_action_recency_days` | Reference / corporate actions | action effective/known dates, t | days since last eligible action | yes | action_type, availability policy | `yes_with_asof_cutoff` | action known by t | `formula_defined` | candidate |
| `reference__float_pit_state` | `float_pit_state` | Reference / filings/vendor | float over time | point-in-time float/share state | yes | source, as_of policy, field | none | no governed PIT float source | `blocked_no_source` | not official |
| `regime__intraday_return` | `regime_intraday_return` | Regime/context bars | open, close | `(close / open) - 1` | no | n/a | `yes_with_asof_cutoff` | regime source quality | `existing` | `012_regime_context_table` / regime pilot |
| `regime__close_to_previous_close_return` | `regime_close_to_previous_close_return` | Regime/context bars | close, previous_close | `(close / previous_close) - 1` | no | n/a | `yes_with_asof_cutoff` | regime source quality | `existing` | `012_regime_context_table` / regime pilot |
| `regime__high_to_open_return` | `regime_high_to_open_return` | Regime/context bars | high, open | `(high / open) - 1` | no | n/a | `yes_with_asof_cutoff` | regime source quality | `existing` | `012_regime_context_table` / regime pilot |
| `regime__low_to_open_return` | `regime_low_to_open_return` | Regime/context bars | low, open | `(low / open) - 1` | no | n/a | `yes_with_asof_cutoff` | regime source quality | `existing` | `012_regime_context_table` / regime pilot |
| `regime__intraday_range_pct` | `regime_intraday_range_pct` | Regime/context bars | high, low, open | `(high - low) / open` | no | n/a | `yes_with_asof_cutoff` | regime source quality | `existing` | `012_regime_context_table` / regime pilot |
| `regime__bar_coverage_state` | `regime_bar_coverage_state` | Regime/context bars | bars_observed | bucketed regime bar coverage state | no | n/a | `yes_with_asof_cutoff` | regime coverage policy | `existing` | `012_regime_context_table` / regime pilot |
| `quality__presence_state` | `presence_state` | Any source + expected inventory | present/missing flags | declared source/component presence state | yes | component, expected inventory | `yes_with_asof_cutoff` | expected denominator declared | `formula_defined` | multiple tables/status matrices |
| `quality__coverage_ratio` | `coverage_ratio` | Any source + expected inventory | observed_count, expected_count | observed_count / expected_count | yes | component, denominator, window | `yes_with_asof_cutoff` | expected denominator > 0 | `requires_variant` | multiple tables/status matrices |
| `quality__missing_count` | `missing_count` | Any source + expected inventory | expected_count, observed_count | max(expected - observed, 0) | yes | component, denominator, window | `yes_with_asof_cutoff` | expected denominator declared | `requires_variant` | multiple tables/status matrices |
| `lineage__source_hash_state` | `source_hash_state` | Manifests/build metadata | source hash | copied source hash/provenance state | yes | source, manifest role | `yes_with_asof_cutoff` | manifest consistency | `existing` | multiple tables |
| `lineage__build_policy_state` | `build_policy_state` | Manifests/build metadata | build id, schema id, policy id | copied build/schema/policy lineage state | yes | source, manifest role | `yes_with_asof_cutoff` | registry/manifest consistency | `existing` | multiple tables |
| `future__future_return_H` | `future_return_H` | Future prices | future close/price | future return over horizon H | yes | H, price_ref | `no_future_or_prohibited` | outcome only; not state X | `prohibited_as_feature` | `008_outcomes_table` only as label/outcome |
| `future__mfe_H` | `mfe_H` | Future prices | future path | maximum favorable excursion | yes | H, path policy | `no_future_or_prohibited` | outcome only; not state X | `prohibited_as_feature` | `008_outcomes_table` only as label/outcome |
| `future__mae_H` | `mae_H` | Future prices | future path | maximum adverse excursion | yes | H, path policy | `no_future_or_prohibited` | outcome only; not state X | `prohibited_as_feature` | `008_outcomes_table` only as label/outcome |
| `execution__pnl_reward` | `pnl_reward` | Execution/outcomes | fills, actions, prices | realized PnL or RL reward | yes | execution policy, reward formula | `no_future_or_prohibited` | outcome/action, not observable state | `prohibited_as_feature` | outcomes/execution only |
| `decision__selected_by_scanner` | `selected_by_scanner` | Scanner/decision | scanner decision | scanner selection flag | yes | scanner version | `no_future_or_prohibited` as causal feature | decision artifact, not neutral observable | `prohibited_as_feature` | scanner/event candidates only |
| `decision__best_threshold_found` | `best_threshold_found` | Optimizer/ML/AlphaEvolve | optimization results | best threshold found by search | yes | optimizer run | `no_future_or_prohibited` | optimizer result/leakage risk | `prohibited_as_feature` | research output only |
| `decision__action_taken` | `action_taken` | Policy/execution | action | enter/exit/hold/scale action | yes | policy version | `no_future_or_prohibited` | action, not observable state | `prohibited_as_feature` | execution/policy only |

## Regla De Lectura

```text
semantic_classification = not_assigned_in_this_layer
```

La familia semantica y el Information Object candidato se asignan despues en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

