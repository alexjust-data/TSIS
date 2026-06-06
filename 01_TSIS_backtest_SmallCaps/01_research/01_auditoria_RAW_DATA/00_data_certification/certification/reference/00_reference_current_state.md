# Reference | Current State

`reference` llega a certificacion como capa de identidad y como capa causal parcial.

Base:

- [04_reference_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\04_reference_closeout.md)
- [reference_identity_quality_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_identity_quality_summary.parquet)
- [reference_causal_alignment_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_causal_alignment_summary.parquet)

## Identidad

- `good_identity_snapshot`: `12,093` rows (`96.99%`)
- `bad_unresolved_identity`: `200` rows (`1.60%`)
- `review_transient_symbol`: `175` rows (`1.40%`)

Lectura:

- la masa principal de identidad queda claramente recuperada
- el residuo duro de identidad es pequeno

## Tesis del bloque

`reference` no se queda en metadata pasiva.

Ya aparece como:

- capa de identidad
- capa de existencia temporal
- capa de corporate actions
- y capa explicativa parcial sobre anomalias de mercado

## Matiz importante de causalidad

Base:

- [reference_split_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_market_link_candidates.parquet)
- [reference_split_daily_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_daily_link_candidates.parquet)
- [reference_split_1m_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_split_1m_link_candidates.parquet)

En `splits -> trades` hay `22` casos candidatos:

- `9` como `split_explains_trade_scale_mismatch`
- `13` como `split_near_scale_mismatch_review`

Pero el contraste contra `daily` y `1m` es mucho mas debil:

- `daily_split_ratio_review`: `1`
- `review_no_daily_alignment`: `21`
- `m1_split_ratio_review`: `1`
- `review_no_1m_alignment`: `21`

Lectura:

- `reference` si aporta explicacion causal real sobre una fraccion pequena de `trades`
- pero esa potencia explicativa no debe sobredimensionarse
- el frente `splits -> market scale` existe, pero es estrecho y no se replica con fuerza en `daily` ni `1m`
