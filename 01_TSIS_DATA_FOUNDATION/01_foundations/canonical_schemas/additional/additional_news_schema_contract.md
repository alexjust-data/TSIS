# Additional News Schema Contract

Status: canonical schema contract for `E:\TSIS\data\additional\news`.

## Purpose

`additional\news` stores Polygon news events for the `<1B>` operating universe. It is a contextual and causal-overlay dataset, not a deterministic truth source for market moves.

## Physical Layout

Observed root:

`E:\TSIS\data\additional\news\news`

Observed pattern:

`ticker=<TICKER>\news_<TICKER>.parquet`

Observed representative payload:

`E:\TSIS\data\additional\news\news\ticker=AACT\news_AACT.parquet`

## Valid Physical Forms

Ticker files may contain either:

- news payload rows
- empty sentinel rows with `ticker`, `_empty`, `_dataset`, `_ingested_utc`

## Observed Payload Columns

`id`, `title`, `author`, `published_utc`, `article_url`, `tickers`, `image_url`, `description`, `keywords`, `insights`, `ticker`, `publisher.name`, `publisher.homepage_url`, `publisher.logo_url`, `publisher.favicon_url`, `amp_url`, `_dataset`, `_ingested_utc`.

Nested/list-like fields:

- `tickers`
- `keywords`
- `insights`

## Canonical Event Key

`ticker + published_utc + id`

Important: `ticker` is the requested/download ticker. `tickers` is the article-level symbol list and may contain multiple symbols. Consumers must preserve this distinction.

## Coverage Evidence

Audited against 4824 `<1B>` tickers:

- `files_present = 4824`
- `files_non_empty = 3869`
- `coverage_non_empty_pct = 80.203`
- `rows_total = 288093`

Root-cause closeout normalized event count:

- `287138` news events
- `3869` tickers with non-empty news
- only `36.38%` mono-ticker events

## Causal Buckets

Observed causal overlay buckets:

- `news_near_halt_market_event = 1268`
- `news_near_market_anomaly = 98400`
- `news_context_only = 18296`
- `review_multi_ticker_ambiguous_news = 169154`
- `news_near_short_flow_only = 20`

## Required Consumer Rules

- Treat multi-ticker news as structurally ambiguous unless a downstream model handles attribution.
- The strongest causal class is `news_near_halt_market_event`.
- `published_utc` must be converted to the relevant market timezone before intraday causal claims.
- Do not use same-day news as causal proof if the market was already disordered before publication.
- Preserve `article_url`, `publisher.*`, `tickers` and `insights` for forensic review.

## Verdict

`additional\news` is the strongest causal/contextual subblock in `additional`, but it must remain attribution-aware. Mono-ticker/news-near-halt cases are most defensible; broad multi-ticker events remain review.
