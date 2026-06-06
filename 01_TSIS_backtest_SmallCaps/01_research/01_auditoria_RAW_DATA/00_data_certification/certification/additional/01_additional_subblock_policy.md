# Additional | Subblock Policy

## `financials_core`

Queda `good`.

Cobertura efectiva:

- `income_statements`: `99.772%`
- `balance_sheets`: `99.772%`
- `cash_flow_statements`: `99.710%`

Lectura:

- capa fuerte
- útil como base primaria del bloque

## `financials_ratios`

Queda `review`.

- cobertura efectiva: `46.269%`

Lectura:

- no parece corrupción
- sí parece capa escasa o materialización incompleta

## `news`

Queda `good/review` mixto.

Base:

- [additional_news_link_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_news_link_summary.parquet)

Masa:

- `287,138` eventos
- `3,869` tickers con noticias

Buckets:

- `news_near_halt_market_event = 1,268`
- `news_near_market_anomaly = 98,400`
- `news_context_only = 18,296`
- `review_multi_ticker_ambiguous_news = 169,154`
- `news_near_short_flow_only = 20`

Lectura:

- `news_near_halt_market_event` es el subconjunto fuerte
- `news_near_market_anomaly` tiene valor real, pero aún mixto

## `ipos`

Queda `good/review` mixto.

Base:

- [additional_ipo_link_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_ipo_link_summary.parquet)

Buckets:

- `ipo_near_halt_market_event = 156`
- `ipo_near_market_anomaly = 676`
- `ipo_market_clean = 449`

Lectura:

- útil sobre todo como contexto de early-life behavior
- más fuerte cerca de halts

## `corporate_actions_additional`

Queda `review`.

Base:

- [additional_corp_actions_reference_overlap_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_corp_actions_reference_overlap_summary.parquet)

Lectura:

- `splits` y `dividends` son sobre todo redundancia útil frente a `reference`
- `ticker_events` no desplazan a `reference`

## `economic`

Queda `good` como dataset y `review` como causalidad ticker-level.

Lectura:

- series limpias y largas
- overlay macro útil
- no causalidad ticker-by-ticker fuerte
