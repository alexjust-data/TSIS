# Halts | Current State

`halts` llega a certificacion como una de las capas mas solidas del proyecto.

Base:

- [04_halts_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\04_halts_closeout.md)
- [build_log.json](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\build_log.json)
- [canonical_event_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\canonical_event_summary.parquet)

## Estado estructural

- eventos canonicos: `132,257`
- `good_full_intraday_event`: `129,638`
- `good_date_level_event`: `1,272`
- `review_partial_identity`: `1,096`
- `regulatory_context_only`: `250`
- `bad_unusable_event`: `1`

Lectura:

- la capa de evento queda ampliamente sana
- el residuo duro agregado es practicamente nulo

## Estado `<1B>`

Base:

- [halts_lt1b_event_index.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\halts_lt1b_event_index.parquet)

En el universo `<1B>`:

- eventos indexados: `53,909`
- `good_full_intraday_event`: `53,720`
- `good_date_level_event`: `186`
- `regulatory_context_only`: `3`

La lectura sigue siendo muy fuerte a favor de `halts`.

## Nota sobre el warning del builder

Base:

- [multisource_builder_reconciliation.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\multisource_builder_reconciliation.parquet)

El warning de `build_log.json`:

- `multisource_row_mismatch:source_sum=134154 multisource_rows=133116`

no debe leerse como perdida bruta de `1,038` filas sin explicacion.

El propio artefacto de reconciliacion muestra:

- `nasdaq`: `119,630 -> 118,594` tras deduplicacion (`1,036` de delta)
- `nyse`: `13,178 -> 13,178`
- `sec`: `1,346 -> 1,346`
- `all_sources_concat`: `134,154 -> 133,118`
- `persisted_multisource_parquet`: `133,116`

Lectura:

- casi todo el gap del warning se explica por deduplicacion del builder
- queda un residuo menor de `2` filas entre `133,118` y `133,116`
- ese residuo es marginal y no cambia la certificacion del bloque, pero conviene dejarlo documentado como ajuste fino pendiente
