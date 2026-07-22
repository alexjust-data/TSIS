# Additional | Closeout

`additional` queda aceptado, pero con pesos internos muy desiguales.

## Política final

- `good`
  - `financials_core`
  - `economic` como dataset macro
  - `news_near_halt_market_event`
  - subconjunto de `ipo_near_halt_market_event`
- `review`
  - `financials_ratios`
  - `news_near_market_anomaly`
  - `review_multi_ticker_ambiguous_news`
  - `news_context_only`
  - `ipo_near_market_anomaly`
  - `ipo_market_clean`
  - `corporate_actions_additional`
  - `economic` como causalidad ticker-level
- `bad`
  - no emerge familia agregada `bad`

## Veredicto del bloque

La lectura correcta es:

- bloque aceptado
- no homogéneo
- con valor fuerte en `financials_core`
- valor causal real pero mixto en `news`
- contexto útil en `ipos` y `economic`
- y papel secundario/redundante en `corporate_actions_additional`

## Pendiente útil real

La única pendiente que merece trabajo visual adicional antes del ensamblado final es:

- calibración manual de `news_near_market_anomaly`
- calibración manual de `ipo_near_halt_market_event`
- calibración manual de `ipo_near_market_anomaly`
