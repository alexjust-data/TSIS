# Reference | Causal Value

El valor fuerte de `reference` no está en describir compañías. Está en explicar parte del residuo de mercado.

## `events -> halts`

Base:

- [reference_event_halt_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_event_halt_link_candidates.parquet)

Buckets:

- `ticker_change_near_halt`: `775`
- `reference_event_near_halt_review`: `173`

Lectura:

- aquí sí aparece una familia causal fuerte
- `ticker_change` explica una parte real del comportamiento visto cerca de halts

## `events -> quotes`

Base:

- [reference_event_quotes_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_event_quotes_link_candidates.parquet)

Buckets:

- `ticker_change_near_quotes_anomaly`: `2,330`
- `reference_event_near_quotes_review`: `247`
- `reference_event_near_quotes_clean`: `18`

Lectura:

- `reference` funciona bien como detector
- pero esta familia sigue siendo más mixta que `events -> halts`

## `splits -> trades`

Base:

- [reference_split_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet)

Buckets:

- `split_explains_trade_scale_mismatch`: `9`
- `split_near_scale_mismatch_review`: `13`

Lectura:

- no explica el grueso de `trades`
- sí explica un subconjunto pequeño pero real y defendible

## `splits -> daily / 1m`

Base:

- [reference_split_daily_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_daily_link_candidates.parquet)
- [reference_split_1m_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_1m_link_candidates.parquet)

Resultado:

- `review_no_daily_alignment`: `21`
- `daily_split_ratio_review`: `1`
- `review_no_1m_alignment`: `21`
- `m1_split_ratio_review`: `1`

Lectura:

- la fuerza explicativa de splits aparece sobre todo en comparabilidad con `trades`
- no queda replicada con la misma limpieza en `daily` ni `1m`
