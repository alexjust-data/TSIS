# Additional News Attribution Review Cases v0.1

These rows are not bad data by default. They prove why `news` requires attribution flags before consumption.

| ticker | news_date | publisher_name | title | n_tickers | quotes_severity | trades_severity | news_link_bucket |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FIEE | 2022-05-26 00:00:00 | Seeking Alpha | Q2 2022 Global Outlook: Bracing For Volatility | 652 | PASS |  | news_context_only |
| FIEE | 2021-12-13 00:00:00 | Seeking Alpha | Week Ahead: 9 Major Rate Decisions With Developed Markets Moving Slow | 510 | PASS |  | news_context_only |
| FIEE | 2022-05-14 00:00:00 | Seeking Alpha | Week Ahead - Wall Street Whipsawed | 481 |  |  | news_context_only |
| AATC | 2022-12-21 00:00:00 | GlobeNewswire Inc. | Autoscope Technologies Corporation Announces Intention to Voluntarily Delist Its Common Stock From Nasdaq and Deregister | 1 | SOFT_FAIL | HARD_FAIL | news_near_halt_market_event |
| ABEO | 2024-04-22 00:00:00 | GlobeNewswire Inc. | Abeona Therapeutics Provides Regulatory Update on Pz-cel | 1 | HARD_FAIL | SOFT_FAIL | news_near_halt_market_event |
| ABIO | 2024-04-03 00:00:00 | GlobeNewswire Inc. | ARCA biopharma and Oruka Therapeutics Announce Merger Agreement  | 1 | SOFT_FAIL | HARD_FAIL | news_near_halt_market_event |
| AAGR | 2023-12-11 00:00:00 | GlobeNewswire Inc. | African Agriculture Reports Expanded Activities  Expects to Significantly Increase Production in 2024 | 1 | SOFT_FAIL | SOFT_FAIL | news_near_market_anomaly |
| AAGR | 2023-12-18 00:00:00 | GlobeNewswire Inc. | African Agriculture Inc. Holdings Welcomes Mr. Osman Ahmed, Managing Director and Head of Private Equity at 10X Capital, | 1 | SOFT_FAIL | SOFT_FAIL | news_near_market_anomaly |
| AAGR | 2024-01-17 00:00:00 | GlobeNewswire Inc. | African Agriculture Inc. Receives Computer Donation from Sportradar Group to Empower Education in Senegal Schools | 1 | PASS | HARD_FAIL | news_near_market_anomaly |
| NEWTZ | 2022-08-01 00:00:00 | Seeking Alpha | 3 High Yielders To Dump After An Epic Rally | 57 | PASS | PASS | news_near_short_flow_only |
| ATA | 2021-05-20 00:00:00 | Benzinga | Earnings Scheduled For May 20, 2021 | 40 | PASS | PASS | news_near_short_flow_only |
| NEWTI | 2024-12-16 00:00:00 | Benzinga | NewtekOne, Inc. Declares a Quarterly Dividend of $0.19 per Share | 5 | PASS | PASS | news_near_short_flow_only |
| ACRE | 2021-05-10 00:00:00 | Benzinga | Stocks That Hit 52-Week Highs On Monday | 776 | SOFT_FAIL | SOFT_FAIL | review_multi_ticker_ambiguous_news |
| AGRO | 2021-05-10 00:00:00 | Benzinga | Stocks That Hit 52-Week Highs On Monday | 776 | PASS | SOFT_FAIL | review_multi_ticker_ambiguous_news |
| AMTB | 2021-05-10 00:00:00 | Benzinga | Stocks That Hit 52-Week Highs On Monday | 776 | SOFT_FAIL | SOFT_FAIL | review_multi_ticker_ambiguous_news |

Institutional reading:

- `published_utc` and `news_date` make this useful for event context.
- `n_tickers` and multi-name articles prevent naive ticker causality.
- Market evidence can support a context label, but it does not prove the news caused the move.
