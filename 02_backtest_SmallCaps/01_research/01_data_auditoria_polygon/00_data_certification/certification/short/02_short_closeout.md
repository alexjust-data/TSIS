# Short | Closeout

`short` queda cerrado, pero con asimetría explícita de fuentes.

## Política final

- `good`
  - casos de `short_flow_near_halt` visualmente coherentes
  - casos de `days_to_cover_spike_near_halt` plausibles y no dominados por `ADV=0`
- `review`
  - `short_flow_near_market_anomaly`
  - `short_flow_market_clean`
  - `high_short_interest_context`
  - `days_to_cover_spike_near_halt` por defecto
- `bad`
  - no emerge una familia agregada `bad`

## Veredicto del bloque

La lectura correcta es:

- `short` sí aporta valor real
- pero no como capa universal de explicación
- y no con Polygon como baseline principal

## Decisión operativa

- usar `FINRA short_volume` como baseline diario
- usar `FINRA short_interest` como baseline contextual
- usar `Polygon short` solo como:
  - comparativo
  - cobertura secundaria
  - o root fresco `<1B>` si se quiere conservarlo
