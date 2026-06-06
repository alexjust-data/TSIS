# Halts | Closeout

`halts` queda cerrado como bloque muy fuerte para la certificación final.

## Veredicto del bloque

La lectura correcta es:

- `halts` sí puede aceptarse como capa de verdad del evento
- sí tiene valor causal real al cruzarse con `quotes` y `trades`
- y no presenta una familia `bad` material que bloquee su uso

## Política final

Estados recomendados:

- `good`
- `review`
- `bad`

Mapeo:

- `good`
  - `confirmed_halt_microstructure_coherent`
- `review`
  - `halt_with_quotes_signal_only`
  - `halt_with_trades_signal_only`
  - `halt_present_but_market_clean`
  - `market_signal_without_clear_halt_window`
- `bad`
  - residuo estructural marginal tipo `bad_unusable_event`

## Conclusión fuerte

En `halts`, recuperar lo máximo posible no exige forzar nada.

Los datos ya sostienen por sí solos que:

- la gran mayoría del bloque es usable
- el overlay visual es defendible
- y el residuo duro es prácticamente irrelevante en masa
