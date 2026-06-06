# Short Closeout

## Alcance

El bloque `short` quedó auditado en dos capas:

- estructural
  - cobertura
  - provider comparison
  - integridad aritmética
  - identidad / remap / vida del ticker
- causal
  - `short_volume` contra `daily`, `quotes`, `trades`, `halts`
  - `short_interest` como contexto lento cerca de `halts`

Universo operativo:

- `<1B>` heredado de la auditoría general

Providers:

- `FINRA`: baseline oficial
- `Polygon`: capa comparativa secundaria

## Hallazgos principales

### Provider baseline

`short_volume`:

- Polygon:
  - `2024-02-06 -> 2026-04-02`
  - `3381` tickers con filas
- FINRA:
  - `2018-08-01 -> 2026-04-29`
  - `4623` tickers con filas

Conclusión:

- en `short_volume`, Polygon queda claramente por debajo de FINRA

`short_interest`:

- Polygon y FINRA quedan bastante más cerca
- aun así, FINRA sigue siendo la referencia oficial preferida

### Calidad estructural

- el residuo `only Polygon` no parece valor añadido limpio
- queda dominado por:
  - `review_provider_coverage_gap`
  - `review_transient_or_remap_candidate`
  - `review_crossing_life_window`

- la consistencia por venue en `short_volume` es claramente mejor en FINRA que en Polygon

### Capa causal

`short_volume`:

- `short_flow_near_market_anomaly = 53,229`
- `short_flow_near_halt = 88`
- `short_flow_market_clean = 2,603`

Lectura:

- `short_volume` aporta mucho más como contexto de anomalía de mercado que como explicación cerrada
- el subconjunto más fuerte es `short_flow_near_halt`

`short_interest`:

- `days_to_cover_spike_near_halt = 1,790`
- `high_short_interest_context = 203`

Lectura:

- `short_interest` sí aporta contexto de crowding / squeeze risk
- pero muchos spikes están deformados por `ADV` casi cero

## Política final

### good

- casos de `short_flow_near_halt` visualmente coherentes
- casos de `days_to_cover_spike_near_halt` económicamente plausibles y no dominados por `ADV=0`

### review

- `short_flow_near_market_anomaly`
- `short_flow_market_clean`
- `high_short_interest_context`
- `days_to_cover_spike_near_halt` por defecto
- casos ambiguos de `short_flow_near_halt`

### bad

- no emerge una familia agregada `bad`

## Decisión final

El bloque `short` queda aceptado con esta semántica:

- `FINRA short_volume` como baseline oficial diario
- `FINRA short_interest` como baseline oficial bisemanal/contextual
- `Polygon short` solo como capa comparativa y de cobertura secundaria

Uso recomendado:

- `short_volume`
  - como señal contextual diaria
  - y como señal fuerte en el subconjunto cercano a halts
- `short_interest`
  - como contexto lento de crowding / iliquidez / squeeze risk

No usar:

- `short_interest` como evidencia causal intradía fina
- `Polygon short_volume` como baseline histórico principal
