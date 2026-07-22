# Additional | Current State

`additional` no debe certificarse como un unico dataset plano.

Su cierre correcto mantiene seis subcapas:

- `financials_core`
- `financials_ratios`
- `news`
- `ipos`
- `corporate_actions_additional`
- `economic`

Base:

- [04_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\04_additional_closeout.md)
- [additional_effective_coverage_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_effective_coverage_summary.parquet)

## Lectura inicial

La jerarquia correcta del bloque ya viene bastante clara:

1. `financials_core`
2. `news`
3. `ipos`
4. `economic`
5. `corporate_actions_additional`
6. `financials_ratios`

## Matices duros de la segunda pasada

Base:

- [additional_news_link_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_news_link_summary.parquet)
- [additional_news_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_news_market_link_candidates.parquet)
- [additional_corp_actions_reference_overlap_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_corp_actions_reference_overlap_summary.parquet)

`news`:

- `review_multi_ticker_ambiguous_news = 169,154`
- ese bucket es efectivamente multiticker y no un falso positivo de agregacion
- `mono_pct = 0%`
- media `16.26` tickers por noticia
- mediana `4`

Lectura:

- el bucket ambiguo de `news` es real
- no conviene intentar recuperarlo en bloque como se hizo en `trades`

`corporate_actions_additional`:

- `dividends`: `1,253` tickers con `reference_exact_overlap`, `5` sin exact overlap
- `splits`: `1,858` con `reference_exact_overlap`, `18` sin exact overlap
- `ticker_events`: `2,703` rows en `reference_present_no_exact_overlap`

Lectura:

- `splits` y `dividends` en `additional` son claramente secundarios frente a `reference`
- `ticker_events` no aporta solape exacto y no debe tratarse como capa maestra de corporate actions
