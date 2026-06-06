# Daily | Closeout

`daily` queda cerrado como bloque muy recuperable.

## Veredicto del bloque

La lectura rigurosa no es:

- `daily` perfecto

Tampoco es:

- `daily` lleno de agujeros y corrupción

La lectura correcta es:

- calidad de bar ampliamente sana
- residuo `vw` mayoritariamente recuperable
- tail duro muy pequeño y bien aislado
- frontera de cobertura relevante, pero en gran parte recuperable

## Política final

Estados finales recomendados:

- `good`
- `recoverable_without_penalty`
- `recoverable_with_flag`
- `review_not_rehabilitated`
- `bad`

Mapeo operativo:

- calidad `good`
  - `schema_only_or_other`
  - `vw_edge_absmax_only`
- calidad `recoverable_with_flag`
  - `vw_low_ratio_limited_days`
  - `vw_mid_ratio_illiquid_regime`
  - `vw_high_ratio_illiquid_regime`
- calidad `bad`
  - `hard_invalid_parse_or_price`

- cobertura `recoverable_without_penalty`
  - `LIKELY_VALID_GAP_ONLY`
- cobertura `recoverable_with_flag`
  - `AMBIGUOUS_REVIEW`
- cobertura `review_not_rehabilitated`
  - `REALLY_PROBLEMATIC_UNEXPECTED`

## Números clave

- calidad:
  - `44,423` ticker-year files
  - `102` excluidos como `bad`
  - `0.23%` de tail duro
- cobertura:
  - `653` tickers sin `complete_daily`
  - `374` recuperables sin penalización
  - `222` recuperables con flag
  - `57` abiertos como frontera de cobertura

## Conclusión fuerte

En `daily`, la estrategia correcta sí es recuperar lo máximo posible.

Y los datos apoyan esa estrategia:

- casi todo el problema de calidad se recupera salvo `102` ticker-year
- y más del `91%` del faltante de cobertura no debe leerse como fallo duro:
  - `374 + 222 = 596`
  - `596 / 653 = 91.27%`
