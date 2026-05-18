# Halts | Overlay And Recovery

En `halts`, “recuperar” no significa rescatar bars o files. Significa demostrar que el evento oficial sirve de verdad para explicar mercado.

## Overlay visual `<1B>`

Base:

- [halts_quotes_trades_visual_cases.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\halts_quotes_trades_visual_cases.parquet)
- [03_taxonomy.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\img_phase1\03_taxonomy.png)
- [05_yearly_events.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\img_phase1\05_yearly_events.png)

Casos visuales indexados:

- `25,301`

Buckets:

- `confirmed_halt_microstructure_coherent`: `18,591` (`73.48%`)
- `halt_with_trades_signal_only`: `3,914` (`15.47%`)
- `halt_with_quotes_signal_only`: `1,896` (`7.49%`)
- `halt_present_but_market_clean`: `516` (`2.04%`)
- `market_signal_without_clear_halt_window`: `384` (`1.52%`)

## Qué se recupera aquí

La gran recuperación del bloque es:

- aceptar `halts` como verdad operativa del evento
- y no dejarlo en simple fuente decorativa o documental

`confirmed_halt_microstructure_coherent` ya demuestra esa recuperación de forma fuerte.

## Matiz importante

Los campos:

- `quotes_problem_flag`
- `trades_problem_flag`

salen altos en muchas filas del overlay.

Eso no debe leerse como fallo de `halts`.

Debe leerse así:

- el halt se está cruzando precisamente con datasets que ya traen sus propias flags
- `halts` no queda invalidado por ese cruce
- al contrario, ayuda a contextualizar parte de esos residuos

Ejemplo fuerte:

- `confirmed_halt_microstructure_coherent` aparece dominado por `quotes_problem_flag=True` y `trades_problem_flag=True`
- eso refuerza la utilidad causal de `halts` sobre episodios microestructuralmente tensos
