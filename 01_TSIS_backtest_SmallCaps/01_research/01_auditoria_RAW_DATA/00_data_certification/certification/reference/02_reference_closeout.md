# Reference | Closeout

`reference` queda cerrado como bloque útil y en gran parte recuperado.

## Política final

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
- `bad`
  - `bad_unresolved_identity`

## Recuperación máxima defendible

La recuperación fuerte del bloque ya está conseguida en:

- identidad buena masiva
- `events -> halts`
- subconjunto quirúrgico de `splits -> trades`

La parte que no conviene sobrerrecuperar es:

- `events -> quotes`
- y los residuos de split no confirmados por `daily` / `1m`

## Veredicto del bloque

La lectura correcta de `reference` es:

- bloque ampliamente usable
- con valor causal real
- pero con fuerza desigual según frente

Orden de confianza:

1. identidad snapshot
2. `events -> halts`
3. `splits -> trades`
4. `events -> quotes`
