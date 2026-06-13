# Reference Population Summary v0.1

Resumen ligero promovido desde cache historico. Los parquets pesados siguen en `01_research`.

## Buckets principales

| family | bucket | rows | distinct_tickers |
|---|---|---|---|
| identity | good_identity_snapshot | 12093 | 12093 |
| identity | bad_unresolved_identity | 200 | 200 |
| identity | review_transient_symbol | 175 | 175 |
| overview_404 | review_overview_404_w_suffix | 186 | 186 |
| overview_404 | review_overview_404_other | 7 | 7 |
| overview_404 | review_overview_404_punctuation | 7 | 7 |
| events | empty_events_payload:None | 6262 | 6262 |
| events | ok_event:ticker_change | 6953 | 6206 |
| splits | review_no_split_payload | 9007 | 9007 |
| splits | good_split_event | 5902 | 3461 |
| dividends | good_dividend_event | 266586 | 5255 |
| dividends | review_no_dividend_payload | 7213 | 7213 |
| causal:events_vs_halts | ticker_change_near_halt | 775 |  |
| causal:events_vs_halts | reference_event_near_halt_review | 173 |  |
| causal:events_vs_quotes | ticker_change_near_quotes_anomaly | 2330 |  |
| causal:events_vs_quotes | reference_event_near_quotes_review | 247 |  |
| causal:events_vs_quotes | reference_event_near_quotes_clean | 18 |  |
| causal:identity_vs_trades | identity_review_without_trades_link | 746 |  |
| causal:identity_vs_trades | identity_review_linked_to_scale_mismatch | 2 |  |
| causal:identity_vs_trades | identity_review_linked_to_other_trades_case | 2 |  |
| causal:splits_vs_1m | review_no_1m_alignment | 21 |  |
| causal:splits_vs_1m | m1_split_ratio_review | 1 |  |
| causal:splits_vs_daily | review_no_daily_alignment | 21 |  |
| causal:splits_vs_daily | daily_split_ratio_review | 1 |  |
| causal:splits_vs_trades | split_near_scale_mismatch_review | 13 |  |
| causal:splits_vs_trades | split_explains_trade_scale_mismatch | 9 |  |

## Download endpoints

| dataset | audit_rows | ok_rows | error_rows | resume_skip_rows | distinct_tickers | http_404_rows | nonzero_rows_saved | ok_pct | error_pct | http_404_pct |
|---|---|---|---|---|---|---|---|---|---|---|
| all_tickers | 3109 | 3032 | 0 | 77 | 0 | 0 | 3032 | 97.52 | 0.0 | 0.0 |
| dividends | 12468 | 12443 | 0 | 25 | 12467 | 0 | 12443 | 99.8 | 0.0 | 0.0 |
| events | 12468 | 12443 | 0 | 25 | 12467 | 6250 | 12443 | 99.8 | 0.0 | 50.13 |
| exchanges | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| overview | 12468 | 12243 | 200 | 25 | 12467 | 200 | 12443 | 98.2 | 1.6 | 1.6 |
| splits | 12468 | 12443 | 0 | 25 | 12467 | 0 | 12443 | 99.8 | 0.0 | 0.0 |
| ticker_types | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 |

## Listing presence

| metric | value | reading |
|---|---|---|
| listing_snapshot_summary_rows | 13124 | tickers observed in all_tickers summary |
| listing_snapshot_rows_total | 12977501 | total all_tickers snapshot rows represented by the summary |
| listing_tickers_lt1b | 4824 | tickers flagged in lt1b universe |
