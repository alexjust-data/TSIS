# Short Causal Overlay Closeout

## Estado

La capa causal de `short` ya quedó calibrada manualmente con viewer, cruzando:

- `short_volume`
- `short_interest`
- `daily`
- `quotes`
- `trades`
- `halts`

Artefactos base:

- `short_volume_market_link_candidates.parquet`
- `short_volume_halt_link_candidates.parquet`
- `short_interest_market_context_candidates.parquet`
- `short_causal_alignment_summary.parquet`
- `short_interest_context_summary.parquet`

El viewer final ya permite revisar:

- régimen de `short_volume_ratio`
- contexto de volumen
- precio diario
- microestructura intradía de `quotes`
- tape de `trades`
- y overlay de `halts` cuando existe

## Lectura causal final

### short_volume

Detector usado:

- `total_volume >= 1000`
- y además:
  - `short_volume_ratio >= 90`
  - o `short_ratio_z >= 3`

Resultado agregado:

- `short_flow_near_market_anomaly = 53,229`
- `short_flow_near_halt = 88`
- `short_flow_market_clean = 2,603`

Lectura final:

- `short_volume` sí detecta presión short diaria real
- pero la mayor parte de los casos se comporta como contexto de rareza de mercado, no como explicación causal cerrada
- el bucket verdaderamente más fuerte es `short_flow_near_halt`, cuando el short-flow elevado convive con:
  - halt cercano
  - fragilidad visible en `quotes`
  - y/o rarezas claras en `trades`

Casos revisados:

- `PFX | 2022-12-06`
  - `good`
  - short-flow alto, halt cercano y reacción visual de mercado defendible
- `BRQS | 2018-12-27`
  - `good`
  - ratio extremo y episodio de halt/microestructura suficientemente coherente
- `ZT | 2022-09-27`
  - `review`
  - ratio alto, pero mercado relativamente limpio
- `CSTA | 2022-08-25`
  - `review`
  - short-flow extremo con mercado plano/limpio
- `VCKA | 2021-12-03`
  - `review`
  - régimen raro de short-flow, pero no evento causal limpio
- `AGMH | 2019-08-06`
  - `review`
  - señal extrema repetitiva en ticker frágil, sin cierre causal fuerte

### short_interest

Contexto agregado:

- `days_to_cover_spike_near_halt = 1,790`
- `high_short_interest_context = 203`

Lectura final:

- `short_interest` aporta una capa lenta de crowding / squeeze risk
- es útil como contexto de episodios tensos
- pero muchos spikes de `days_to_cover` quedan deformados por `ADV` muy bajo o cero
- por eso `short_interest` no debe tratarse como señal causal fina por defecto

Casos revisados:

- `VIE | 2020-02-28`
  - `good`
  - spike de `days_to_cover` plausible, no dominado por `ADV=0`, cerca de halt
- `KELYB | 2019-04-30`
  - `review`
  - contexto tenso real, pero spike demasiado extremo y poco estable
- `AAMC | 2022-03-15`
  - `review`
  - `days_to_cover=999.99` dominado por `ADV=0`
- `JSYN | 2019-04-30`
  - `review`
  - salto de ratio muy artificial
- `DMN | 2025-05-15`
  - `review`
  - crowding extremo, pero serie dominada por escalas límite

## Política final del overlay causal

### good

- `short_flow_near_halt`
  - solo cuando el caso visual muestra:
    - short-flow elevado real
    - halt cercano
    - y fragilidad/reacción coherente en mercado
- `days_to_cover_spike_near_halt`
  - solo cuando el spike es económicamente defendible y no está dominado por `ADV=0`

### review

- `short_flow_near_market_anomaly`
- `short_flow_market_clean`
- `high_short_interest_context`
- `days_to_cover_spike_near_halt`
  - por defecto
- `short_flow_near_halt`
  - cuando el caso visual es ambiguo o demasiado limpio

### bad

- no emerge una familia agregada `bad`
- sí hay casos individuales malos o poco interpretables
- pero no un bucket estructural de contradicción causal fuerte

## Conclusión

`short` sí aporta valor real, pero no como capa universal de explicación.

La lectura final del bloque es:

- `short_volume` sirve bien como contexto diario y, en un subconjunto pequeño, como señal fuerte cerca de halts
- `short_interest` sirve como contexto lento de crowding / iliquidez / squeeze risk
- el baseline oficial debe ser `FINRA`
- `Polygon` queda como capa comparativa secundaria, no como referencia principal de cobertura ni calidad
