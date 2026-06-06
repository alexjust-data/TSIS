# Reference Closeout

## Decision final del bloque

`reference` queda auditado y utilizable como capa de:

- identidad
- existencia temporal
- corporate actions
- explicacion causal parcial de anomalias de mercado

No es un bloque puramente auxiliar. Ya tiene valor explicativo real sobre `quotes`, `trades` y `halts`.

## Qué queda cerrado

- fase estructural cerrada
- `overview`, `all_tickers`, `events`, `splits` y `dividends` ya auditados a nivel de contenido real
- `events -> halts` validado como frente causal fuerte
- `events -> quotes` validado como frente causal fuerte pero todavia mixto
- `splits -> trades` validado como frente causal quirurgico y defendible
- viewer causal implementado
- politica `good / review / bad` preliminar fijada

## Politica final actual

- `good`
  - `good_identity_snapshot`
  - `good_split_event`
  - `split_explains_trade_scale_mismatch`
  - `ticker_change_near_halt` cuando el caso visual es coherente
- `review`
  - `review_transient_symbol`
  - `review_instrument_type_ambiguity`
  - `review_no_split_payload`
  - `split_near_scale_mismatch_review`
  - `ticker_change_near_quotes_anomaly`
  - `reference_event_near_halt_review`
  - `reference_event_near_quotes_review`
  - residuos de identidad enlazados debilmente a mercado
- `bad`
  - `bad_unresolved_identity`
  - no emerge todavia una familia causal agregada `bad` en el overlay de mercado

## Lectura operativa

La lectura mas importante del bloque es esta:

- el valor fuerte de `reference` no sale solo de metadata estatica
- sale sobre todo de `corporate actions`
- `ticker_change` ya explica una parte material de la fragilidad observada en `quotes` y `halts`
- `splits` explican un subconjunto pequeno pero real de `scale_suspect` en `trades`

Tambien queda fijado algo importante:

- `events -> quotes` es fuerte como detector
- pero visualmente sigue siendo una familia mas heterogenea que `splits -> trades`
- por eso hoy cae en `review`, no en `good`

## Limites residuales

- algunos casos de `quotes-only` siguen dominados por iliquidez extrema u outliers
- no toda proximidad temporal entre `ticker_change` y anomalia microestructural debe leerse como causalidad economica cerrada
- `splits` no quedan confirmados limpiamente por `daily` y `1m` en la mayoria de los casos ya enlazados

## Estado

`reference` queda ya al nivel de auditoria profunda y plena dentro del marco actual.

El siguiente bloque natural para continuar la auditoria con este mismo nivel de exigencia es `short` o `additional`, pero `reference` como tal queda cerrado. 
