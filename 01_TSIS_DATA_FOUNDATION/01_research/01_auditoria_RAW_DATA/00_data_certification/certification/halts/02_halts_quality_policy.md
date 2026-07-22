# Halts | Quality Policy

La política de `halts` es más simple que en mercado.

## `good`

- `confirmed_halt_microstructure_coherent`

Lectura:

- el evento oficial y la reacción observada quedan bien alineados

## `review`

- `halt_with_quotes_signal_only`
- `halt_with_trades_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

Lectura:

- no bloquean el bloque
- necesitan contexto adicional
- o expresan asimetría entre libro, tape y ventana oficial

## `bad`

No aparece familia agregada `bad` en el overlay visual.

Residuo estructural duro observado:

- `1` `bad_unusable_event`

Base:

- [canonical_event_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\canonical_event_summary.parquet)

Ese caso es:

- `event_id_canonical = NA|NA|NA|NA|NA`
- `11` rows
- `nasdaq` only
- sin ticker, sin fecha y sin ventana utilizable

La lectura correcta es:

- existe un residuo basura marginal
- no existe una familia `bad` material del bloque
